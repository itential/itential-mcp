# Copyright (c) 2025 Itential, Inc
# GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

import pytest
from unittest.mock import AsyncMock, MagicMock

from itential_mcp.tools.compliance_reports import describe_compliance_report
from itential_mcp.models.compliance_reports import DescribeComplianceReportResponse
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
        self.mock_context.info = AsyncMock()

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
        """describe_compliance_report must log entry via ctx.info."""
        self.mock_cm_service.describe_compliance_report.return_value = {"id": "x"}

        await describe_compliance_report(self.mock_context, report_id="x")

        self.mock_context.info.assert_called_once_with(
            "inside describe_compliance_report(...)"
        )
