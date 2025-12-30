# Copyright (c) 2025 Itential, Inc
# GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later


from itential_mcp.models import compliance_reports as models


class TestDescribeComplianceReportResponse:
    """Test the DescribeComplianceReportResponse model."""

    def test_model_creation_with_basic_data(self):
        """Test creating the model with basic data."""
        data = {"report_id": "123", "status": "complete"}
        response = models.DescribeComplianceReportResponse(result=data)

        assert response.result == data
        assert response.result["report_id"] == "123"
        assert response.result["status"] == "complete"

    def test_model_creation_with_complex_data(self):
        """Test creating the model with complex compliance report data."""
        data = {
            "report_id": "compliance-report-456",
            "status": "complete",
            "devices": [
                {"name": "device1", "compliance_status": "compliant", "violations": []},
                {
                    "name": "device2",
                    "compliance_status": "non-compliant",
                    "violations": [{"rule": "rule1", "severity": "high"}],
                },
            ],
            "summary": {
                "total_devices": 2,
                "compliant_devices": 1,
                "non_compliant_devices": 1,
            },
        }

        response = models.DescribeComplianceReportResponse(result=data)

        assert response.result == data
        assert len(response.result["devices"]) == 2
        assert response.result["summary"]["total_devices"] == 2

    def test_model_serialization(self):
        """Test that the model can be serialized to JSON."""
        data = {"report_id": "789", "status": "running"}
        response = models.DescribeComplianceReportResponse(result=data)

        json_data = response.model_dump()
        assert json_data == {"result": data}

        json_str = response.model_dump_json()
        assert '"report_id":"789"' in json_str
        assert '"status":"running"' in json_str
