# Copyright (c) 2025 Itential, Inc
# GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

import time

import pytest
from unittest.mock import AsyncMock, MagicMock

from itential_mcp.core.exceptions import ItentialMcpException
from itential_mcp.utilities import manual_tasks


def _client(**kw):
    client = MagicMock()
    client.work_center = AsyncMock(**kw)
    return client


def _item(**over):
    base = {
        "id": "wi-1",
        "summary": "Approve change",
        "status": "pending",
        "view": "/workflow_engine/task/ViewData",
        "createdAt": int((time.time() - 30) * 1000),
    }
    base.update(over)
    return base


class TestPendingManualTasks:
    @pytest.mark.asyncio
    async def test_pending_item_returns_list(self):
        client = _client()
        client.work_center.get_work_items.return_value = [_item()]

        result = await manual_tasks.pending_manual_tasks(
            client, "job-1", status="running", live_status="running"
        )

        assert len(result) == 1
        assert result[0].work_item_id == "wi-1"
        assert result[0].title == "Approve change"
        assert result[0].view_type == "ViewData"
        assert result[0].completion_supported is True
        assert 25 <= result[0].waiting_age_seconds <= 60

    @pytest.mark.asyncio
    async def test_only_completed_items_is_empty(self):
        client = _client()
        client.work_center.get_work_items.return_value = [_item(status="completed")]

        result = await manual_tasks.pending_manual_tasks(
            client, "job-1", status="running", live_status="running"
        )

        assert result == []

    @pytest.mark.asyncio
    async def test_404_is_empty(self):
        client = _client()
        client.work_center.get_work_items.side_effect = ItentialMcpException(
            "404 Not Found", http_status=404
        )

        result = await manual_tasks.pending_manual_tasks(
            client, "job-1", status="running", live_status="running"
        )

        assert result == []

    @pytest.mark.asyncio
    @pytest.mark.parametrize("code", [403, 500])
    async def test_other_http_errors_are_unknown(self, code):
        client = _client()
        client.work_center.get_work_items.side_effect = ItentialMcpException(
            "err", http_status=code
        )

        result = await manual_tasks.pending_manual_tasks(
            client, "job-1", status="running", live_status="running"
        )

        assert result is None

    @pytest.mark.asyncio
    async def test_timeout_is_unknown(self):
        client = _client()
        client.work_center.get_work_items.side_effect = TimeoutError()

        result = await manual_tasks.pending_manual_tasks(
            client, "job-1", status="running", live_status="running"
        )

        assert result is None

    @pytest.mark.asyncio
    @pytest.mark.parametrize("status", ["complete", "error", "paused", "canceled"])
    async def test_non_live_run_makes_no_call(self, status):
        client = _client()

        result = await manual_tasks.pending_manual_tasks(
            client, "job-1", status=status, live_status="running"
        )

        assert result == []
        client.work_center.get_work_items.assert_not_called()

    @pytest.mark.asyncio
    async def test_session_status_is_case_sensitive_live(self):
        client = _client()
        client.work_center.get_work_items.return_value = [_item()]

        live = await manual_tasks.pending_manual_tasks(
            client, "s", status="RUNNING", live_status="RUNNING"
        )
        other = await manual_tasks.pending_manual_tasks(
            client, "s", status="COMPLETE", live_status="RUNNING"
        )

        assert len(live) == 1
        assert other == []


class TestSummarize:
    def test_form_view_not_supported(self):
        s = manual_tasks.summarize(_item(view="/x/RenderJsonSchema"))
        assert s.view_type == "RenderJsonSchema"
        assert s.completion_supported is False

    def test_missing_fields(self):
        s = manual_tasks.summarize({"id": "w"})
        assert s.title is None
        assert s.view_type is None
        assert s.waiting_age_seconds is None
        assert s.completion_supported is False

    def test_iso_created_at(self):
        s = manual_tasks.summarize(_item(createdAt="2020-01-01T00:00:00Z"))
        assert s.waiting_age_seconds > 0

    def test_bad_created_at(self):
        assert (
            manual_tasks.summarize(_item(createdAt="garbage")).waiting_age_seconds
            is None
        )
