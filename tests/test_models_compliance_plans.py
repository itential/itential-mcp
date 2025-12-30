# Copyright (c) 2025 Itential, Inc
# GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

import pytest
from pydantic import ValidationError

from itential_mcp.models.compliance_plans import (
    CompliancePlan,
    GetCompliancePlansResponse,
    CompliancePlanInstance,
    RunCompliancePlanResponse,
)


class TestCompliancePlan:
    """Test cases for CompliancePlan model."""

    def test_create_valid_compliance_plan(self):
        """Test creating a valid CompliancePlan instance."""
        plan_data = {
            "id": "plan-123",
            "name": "Security Compliance Check",
            "description": "Validates security configurations",
            "throttle": 5,
        }

        plan = CompliancePlan(**plan_data)

        assert plan.id == "plan-123"
        assert plan.name == "Security Compliance Check"
        assert plan.description == "Validates security configurations"
        assert plan.throttle == 5

    def test_compliance_plan_missing_required_fields(self):
        """Test that CompliancePlan raises ValidationError for missing required fields."""
        with pytest.raises(ValidationError) as exc_info:
            CompliancePlan()

        errors = exc_info.value.errors()
        required_fields = {"id", "name", "description", "throttle"}
        missing_fields = {
            error["loc"][0] for error in errors if error["type"] == "missing"
        }

        assert required_fields.issubset(missing_fields)

    def test_compliance_plan_invalid_throttle_type(self):
        """Test that CompliancePlan raises ValidationError for invalid throttle type."""
        plan_data = {
            "id": "plan-123",
            "name": "Test Plan",
            "description": "Test description",
            "throttle": "invalid",
        }

        with pytest.raises(ValidationError) as exc_info:
            CompliancePlan(**plan_data)

        errors = exc_info.value.errors()
        throttle_errors = [error for error in errors if error["loc"][0] == "throttle"]
        assert len(throttle_errors) > 0
        assert "int_parsing" in throttle_errors[0]["type"]


class TestGetCompliancePlansResponse:
    """Test cases for GetCompliancePlansResponse model."""

    def test_create_valid_response(self):
        """Test creating a valid GetCompliancePlansResponse instance."""
        plan1 = CompliancePlan(
            id="plan-1", name="Plan 1", description="First plan", throttle=3
        )
        plan2 = CompliancePlan(
            id="plan-2", name="Plan 2", description="Second plan", throttle=5
        )

        response = GetCompliancePlansResponse(plans=[plan1, plan2])

        assert len(response.plans) == 2
        assert response.plans[0].id == "plan-1"
        assert response.plans[1].id == "plan-2"

    def test_empty_plans_list(self):
        """Test creating response with empty plans list."""
        response = GetCompliancePlansResponse(plans=[])
        assert response.plans == []

    def test_response_missing_plans_field(self):
        """Test that GetCompliancePlansResponse raises ValidationError for missing plans field."""
        with pytest.raises(ValidationError) as exc_info:
            GetCompliancePlansResponse()

        errors = exc_info.value.errors()
        plans_errors = [error for error in errors if error["loc"][0] == "plans"]
        assert len(plans_errors) > 0


class TestCompliancePlanInstance:
    """Test cases for CompliancePlanInstance model."""

    def test_create_valid_compliance_plan_instance(self):
        """Test creating a valid CompliancePlanInstance instance."""
        instance_data = {
            "id": "instance-456",
            "name": "Running Security Check",
            "description": "Currently executing security compliance",
            "jobStatus": "running",
        }

        instance = CompliancePlanInstance(**instance_data)

        assert instance.id == "instance-456"
        assert instance.name == "Running Security Check"
        assert instance.description == "Currently executing security compliance"
        assert instance.jobStatus == "running"

    def test_compliance_plan_instance_missing_required_fields(self):
        """Test that CompliancePlanInstance raises ValidationError for missing required fields."""
        with pytest.raises(ValidationError) as exc_info:
            CompliancePlanInstance()

        errors = exc_info.value.errors()
        required_fields = {"id", "name", "description", "jobStatus"}
        missing_fields = {
            error["loc"][0] for error in errors if error["type"] == "missing"
        }

        assert required_fields.issubset(missing_fields)


class TestRunCompliancePlanResponse:
    """Test cases for RunCompliancePlanResponse model."""

    def test_create_valid_run_response(self):
        """Test creating a valid RunCompliancePlanResponse instance."""
        instance = CompliancePlanInstance(
            id="instance-789",
            name="Test Instance",
            description="Test instance description",
            jobStatus="completed",
        )

        response = RunCompliancePlanResponse(instance=instance)

        assert response.instance.id == "instance-789"
        assert response.instance.name == "Test Instance"
        assert response.instance.jobStatus == "completed"

    def test_run_response_missing_instance_field(self):
        """Test that RunCompliancePlanResponse raises ValidationError for missing instance field."""
        with pytest.raises(ValidationError) as exc_info:
            RunCompliancePlanResponse()

        errors = exc_info.value.errors()
        instance_errors = [error for error in errors if error["loc"][0] == "instance"]
        assert len(instance_errors) > 0
