# Copyright (c) 2025 Itential, Inc
# GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

import inspect

import pytest
from unittest.mock import AsyncMock, MagicMock

from fastmcp import Context

from itential_mcp.models.work_center import DescribeManualTaskResponse
from itential_mcp.tools import work_center


def _ctx(service):
    ctx = AsyncMock(spec=Context)
    client = MagicMock()
    client.work_center = service
    ctx.request_context = MagicMock()
    ctx.request_context.lifespan_context = MagicMock()
    ctx.request_context.lifespan_context.get.return_value = client
    return ctx


class TestModule:
    def test_tags(self):
        assert work_center.__tags__ == ("work_center",)

    def test_tool_is_async(self):
        assert inspect.iscoroutinefunction(work_center.describe_manual_task)

    def test_docstring_has_identity_caveat(self):
        doc = work_center.describe_manual_task.__doc__
        assert "service account" in doc
        assert "per-user authorization" in doc


class TestDescribeManualTask:
    @pytest.mark.asyncio
    async def test_success_only_view(self):
        svc = AsyncMock()
        svc.get_work_item.return_value = {
            "id": "wi-1",
            "summary": "Approve change",
            "status": "pending",
            "view": "/workflow_engine/task/ViewData",
            "execution": {"id": "job-1", "type": "job"},
        }
        svc.get_work_item_incoming.return_value = {
            "header": "H",
            "message": "M",
            "body": "B",
            "variables": {"x": 1},
            "btn_success": "OK",
            "btn_failure": "",
        }

        result = await work_center.describe_manual_task(_ctx(svc), "wi-1")

        assert isinstance(result, DescribeManualTaskResponse)
        assert result.work_item_id == "wi-1"
        assert result.title == "Approve change"
        assert result.view_type == "ViewData"
        assert result.completion_supported is True
        assert result.status == "pending"
        assert result.header == "H"
        assert result.btn_success == "OK"
        assert result.btn_failure == ""
        assert result.run_id == "job-1"
        assert result.run_type == "job"
        svc.get_work_item.assert_awaited_once_with("wi-1")
        svc.get_work_item_incoming.assert_awaited_once_with("wi-1")

    @pytest.mark.asyncio
    async def test_interactive_html_has_both_buttons(self):
        svc = AsyncMock()
        svc.get_work_item.return_value = {
            "id": "wi-2",
            "view": "/workflow_engine/task/InteractiveHTML",
            "execution": {"id": "sess-1", "type": "session"},
        }
        svc.get_work_item_incoming.return_value = {
            "btn_success": "Approve",
            "btn_failure": "Cancel",
        }

        result = await work_center.describe_manual_task(_ctx(svc), "wi-2")

        assert result.completion_supported is True
        assert result.btn_success == "Approve"
        assert result.btn_failure == "Cancel"
        assert result.run_type == "session"

    @pytest.mark.asyncio
    @pytest.mark.parametrize(
        "view", ["/workflow_engine/task/RenderJsonSchema", "viewTemplateResults"]
    )
    async def test_form_views_not_completion_supported(self, view):
        svc = AsyncMock()
        svc.get_work_item.return_value = {"id": "wi-3", "view": view}
        svc.get_work_item_incoming.return_value = {}

        result = await work_center.describe_manual_task(_ctx(svc), "wi-3")

        assert result.completion_supported is False

    @pytest.mark.asyncio
    async def test_falls_back_to_root_execution(self):
        svc = AsyncMock()
        svc.get_work_item.return_value = {
            "id": "wi-4",
            "view": "/x/ViewHTML",
            "rootExecution": {"id": "job-9"},
        }
        svc.get_work_item_incoming.return_value = {}

        result = await work_center.describe_manual_task(_ctx(svc), "wi-4")

        assert result.run_id == "job-9"
        assert result.run_type is None

    @pytest.mark.asyncio
    async def test_service_error_propagates(self):
        svc = AsyncMock()
        svc.get_work_item.side_effect = RuntimeError("nope")
        svc.get_work_item_incoming.return_value = {}

        with pytest.raises(RuntimeError):
            await work_center.describe_manual_task(_ctx(svc), "wi-5")
