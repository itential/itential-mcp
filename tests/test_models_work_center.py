# Copyright (c) 2025 Itential, Inc
# GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

import pytest
from pydantic import ValidationError

from itential_mcp.models.work_center import (
    DescribeManualTaskResponse,
    ManualTaskSummary,
    completion_supported,
)


class TestCompletionSupported:
    """Test the completion_supported helper"""

    @pytest.mark.parametrize("view", ["ViewData", "ViewHTML", "InteractiveHTML"])
    def test_supported_views(self, view):
        assert completion_supported(view) is True

    @pytest.mark.parametrize(
        "view", ["RenderJsonSchema", "viewTemplateResults", "Other", "", None]
    )
    def test_unsupported_and_unknown_views(self, view):
        assert completion_supported(view) is False


class TestManualTaskSummary:
    """Test the ManualTaskSummary model"""

    def test_full_fields(self):
        m = ManualTaskSummary(
            work_item_id="wi-1",
            title="Approve change",
            view_type="ViewData",
            waiting_age_seconds=12,
            completion_supported=True,
        )
        assert m.work_item_id == "wi-1"
        assert m.title == "Approve change"
        assert m.waiting_age_seconds == 12
        assert m.completion_supported is True

    def test_defaults(self):
        m = ManualTaskSummary(work_item_id="wi-1")
        assert m.title is None
        assert m.view_type is None
        assert m.waiting_age_seconds is None
        assert m.completion_supported is False

    def test_work_item_id_required(self):
        with pytest.raises(ValidationError):
            ManualTaskSummary()


class TestDescribeManualTaskResponse:
    """Test the DescribeManualTaskResponse model"""

    def test_full_fields(self):
        r = DescribeManualTaskResponse(
            work_item_id="wi-1",
            title="Approve",
            view_type="InteractiveHTML",
            completion_supported=True,
            status="pending",
            header="h",
            message="m",
            body="b",
            variables={"a": 1},
            btn_success="OK",
            btn_failure="Cancel",
            run_id="job-1",
            run_type="job",
        )
        assert r.btn_failure == "Cancel"
        assert r.variables == {"a": 1}
        assert r.run_type == "job"

    def test_defaults(self):
        r = DescribeManualTaskResponse(work_item_id="wi-1")
        assert r.completion_supported is False
        assert r.header is None
        assert r.run_id is None

    def test_work_item_id_required(self):
        with pytest.raises(ValidationError):
            DescribeManualTaskResponse()
