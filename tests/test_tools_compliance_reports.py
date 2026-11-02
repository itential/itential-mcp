# Copyright (c) 2025 Itential, Inc
# GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

import pytest
from unittest.mock import AsyncMock, MagicMock

from itential_mcp.tools.compliance_reports import (
    describe_compliance_report,
    get_compliance_reports_by_batch,
)
from itential_mcp.models.compliance_reports import (
    DescribeComplianceReportResponse,
    GetComplianceReportsByBatchResponse,
)
from fastmcp import Context


class TestDescribeComplianceReportTool:
    """Regression tests for Bug 5 — describe_compliance_report must await the service call.

    Previously, client.configuration_manager.describe_compliance_report(report_id)
    was called without await, causing the coroutine object to be passed to the
    Pydantic model, producing:
      ValidationError "Input should be a valid dictionary ... coroutine".
    """

    def setup_method(self):
        """Set up shared mock fixtures."""
        self.mock_context = AsyncMock(spec=Context)
        self.mock_context.debug = AsyncMock()

        self.mock_client = MagicMock()
        self.mock_cm_service = MagicMock()
        self.mock_cm_service.describe_compliance_report = AsyncMock()

        self.mock_client.configuration_manager = self.mock_cm_service
        self.mock_context.request_context.lifespan_context.get.return_value = (
            self.mock_client
        )

    @pytest.mark.asyncio
    async def test_describe_compliance_report_awaits_service_call(self):
        """describe_compliance_report must await the configuration_manager service call.

        The mock is an AsyncMock — if the tool does NOT await it, the coroutine
        propagates to Pydantic and raises ValidationError "Input should be a valid
        dictionary".  If it DOES await, the mock returns the configured dict and the
        response model is valid.
        """
        mock_report = {
            "id": "report-abc123",
            "planName": "Security Baseline",
            "status": "complete",
            "devices": [{"name": "router1", "compliant": True}],
        }
        self.mock_cm_service.describe_compliance_report.return_value = mock_report

        result = await describe_compliance_report(
            self.mock_context, report_id="report-abc123"
        )

        self.mock_cm_service.describe_compliance_report.assert_awaited_once_with(
            "report-abc123"
        )
        assert isinstance(result, DescribeComplianceReportResponse)
        assert result.result["id"] == "report-abc123"
        assert result.result["status"] == "complete"

    @pytest.mark.asyncio
    async def test_describe_compliance_report_passes_report_id(self):
        """describe_compliance_report must pass report_id positionally to the service."""
        self.mock_cm_service.describe_compliance_report.return_value = {"id": "xyz"}

        await describe_compliance_report(self.mock_context, report_id="xyz")

        args, _ = self.mock_cm_service.describe_compliance_report.call_args
        assert args[0] == "xyz"

    @pytest.mark.asyncio
    async def test_describe_compliance_report_returns_full_dict(self):
        """describe_compliance_report must wrap the entire service response dict in result."""
        complex_report = {
            "id": "report-complex",
            "planName": "QoS Compliance",
            "status": "complete",
            "startTime": "2026-03-10T10:00:00Z",
            "endTime": "2026-03-10T10:05:00Z",
            "devices": [
                {"name": "router1", "compliant": True, "violations": []},
                {
                    "name": "switch1",
                    "compliant": False,
                    "violations": ["missing QoS policy"],
                },
            ],
            "summary": {"total": 2, "compliant": 1, "nonCompliant": 1},
        }
        self.mock_cm_service.describe_compliance_report.return_value = complex_report

        result = await describe_compliance_report(
            self.mock_context, report_id="report-complex"
        )

        assert isinstance(result, DescribeComplianceReportResponse)
        assert result.result == complex_report
        assert len(result.result["devices"]) == 2
        assert result.result["summary"]["nonCompliant"] == 1

    @pytest.mark.asyncio
    async def test_describe_compliance_report_logs_entry(self):
        """describe_compliance_report must log entry via ctx.debug."""
        self.mock_cm_service.describe_compliance_report.return_value = {"id": "x"}

        await describe_compliance_report(self.mock_context, report_id="x")

        self.mock_context.debug.assert_called_once_with(
            "inside describe_compliance_report(...)"
        )


class TestGetComplianceReportsByBatchTool:
    """Tests for get_compliance_reports_by_batch."""

    def setup_method(self):
        """Set up shared mock fixtures."""
        self.mock_context = AsyncMock(spec=Context)
        self.mock_context.debug = AsyncMock()

        self.mock_client = MagicMock()
        self.mock_cm_service = MagicMock()
        self.mock_cm_service.get_compliance_reports_by_batch = AsyncMock()

        self.mock_client.configuration_manager = self.mock_cm_service
        self.mock_context.request_context.lifespan_context.get.return_value = (
            self.mock_client
        )

    @pytest.mark.asyncio
    async def test_get_compliance_reports_by_batch_awaits_service_call(self):
        """get_compliance_reports_by_batch must await the configuration_manager service call.

        The mock is an AsyncMock — if the tool does NOT await it, the
        coroutine object propagates to Pydantic and raises ValidationError
        "Input should be a valid list". If it DOES await, the mock returns
        the configured list and the response model is valid.
        """
        self.mock_cm_service.get_compliance_reports_by_batch.return_value = []

        result = await get_compliance_reports_by_batch(
            self.mock_context, batch_id="67ead32d5f12757d048a48df"
        )

        self.mock_cm_service.get_compliance_reports_by_batch.assert_awaited_once_with(
            "67ead32d5f12757d048a48df"
        )
        assert isinstance(result, GetComplianceReportsByBatchResponse)
        assert result.reports == []

    @pytest.mark.asyncio
    async def test_get_compliance_reports_by_batch_passes_batch_id(self):
        """get_compliance_reports_by_batch must pass batch_id positionally to the service."""
        self.mock_cm_service.get_compliance_reports_by_batch.return_value = []

        await get_compliance_reports_by_batch(
            self.mock_context, batch_id="67ead32d5f12757d048a48df"
        )

        args, _ = self.mock_cm_service.get_compliance_reports_by_batch.call_args
        assert args[0] == "67ead32d5f12757d048a48df"

    @pytest.mark.asyncio
    async def test_get_compliance_reports_by_batch_maps_response_array(self):
        """get_compliance_reports_by_batch must map the raw report array onto the model."""
        raw_reports = [
            {
                "id": "67ead32d5f12757d048a48d1",
                "batchId": "67ead32d5f12757d048a48df",
                "treeId": "67ead32d5f12757d048a48d2",
                "version": "initial",
                "nodePath": "base/US East/Atlanta",
                "deviceName": "router1",
                "timestamp": "2026-08-18T00:00:00Z",
                "totals": {"errors": 1, "warnings": 2, "infos": 3, "passes": 10},
            },
            {
                "id": "67ead32d5f12757d048a48d9",
                "batchId": "67ead32d5f12757d048a48df",
                "treeId": "67ead32d5f12757d048a48d2",
                "version": "initial",
                "nodePath": "base/US East/Atlanta",
                "deviceName": "router2",
                "timestamp": "2026-08-18T00:01:00Z",
                "totals": {"errors": 0, "warnings": 0, "infos": 1, "passes": 15},
            },
        ]
        self.mock_cm_service.get_compliance_reports_by_batch.return_value = raw_reports

        result = await get_compliance_reports_by_batch(
            self.mock_context, batch_id="67ead32d5f12757d048a48df"
        )

        assert isinstance(result, GetComplianceReportsByBatchResponse)
        assert len(result.reports) == 2
        assert result.reports[0].deviceName == "router1"
        assert result.reports[0].totals.passes == 10
        assert result.reports[1].deviceName == "router2"
        assert result.reports[1].totals.errors == 0
        assert result.reports[1].totals.passes == 15

    @pytest.mark.asyncio
    async def test_get_compliance_reports_by_batch_logs_entry(self):
        """get_compliance_reports_by_batch must log entry via ctx.debug."""
        self.mock_cm_service.get_compliance_reports_by_batch.return_value = []

        await get_compliance_reports_by_batch(self.mock_context, batch_id="batch-1")

        self.mock_context.debug.assert_called_once_with(
            "inside get_compliance_reports_by_batch(...)"
        )

    def test_get_compliance_reports_by_batch_annotation_classification(self):
        """get_compliance_reports_by_batch must be annotated read-only, non-destructive.

        Documents intent: this is a GET-only, safe, non-destructive tool.
        The repo-wide TestToolAnnotationCompleteness and
        TestToolAnnotationSafetyInvariants guards in
        tests/utilities/test_tool.py already enforce this automatically for
        every discovered tool; this is an explicit spot-check.
        """
        annotations = get_compliance_reports_by_batch.annotations

        assert annotations is not None
        assert annotations.read_only_hint is True
        assert annotations.destructive_hint is not True
