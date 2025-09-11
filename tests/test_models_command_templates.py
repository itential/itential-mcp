# Copyright (c) 2025 Itential, Inc
# GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)

import pytest
from pydantic import ValidationError

from itential_mcp.models import command_templates as models


class TestCommandTemplate:
    """Tests for CommandTemplate model."""

    def test_command_template_creation(self):
        """Test creating a CommandTemplate with valid data."""
        template = models.CommandTemplate(
            _id="template_123",
            name="test_template",
            description="Test command template",
            namespace="test_project",
            passRule=True,
        )

        assert template.id == "template_123"
        assert template.name == "test_template"
        assert template.description == "Test command template"
        assert template.namespace == "test_project"
        assert template.passRule is True

    def test_command_template_null_namespace(self):
        """Test CommandTemplate with null namespace (global template)."""
        template = models.CommandTemplate(
            _id="global_123",
            name="global_template",
            description="Global command template",
            namespace=None,
            passRule=False,
        )

        assert template.id == "global_123"
        assert template.namespace is None
        assert template.passRule is False

    def test_command_template_validation_error(self):
        """Test CommandTemplate validation with invalid data."""
        with pytest.raises(ValidationError):
            models.CommandTemplate(
                name="test",
                description="test",
                namespace=None,
                passRule=True,
                # Missing required _id field
            )


class TestGetCommandTemplatesResponse:
    """Tests for GetCommandTemplatesResponse model."""

    def test_get_command_templates_response_creation(self):
        """Test creating GetCommandTemplatesResponse with valid data."""
        template = models.CommandTemplate(
            _id="template_123",
            name="test_template",
            description="Test template",
            namespace=None,
            passRule=True,
        )

        response = models.GetCommandTemplatesResponse(templates=[template])

        assert len(response.templates) == 1
        assert response.templates[0] == template
        assert response.templates[0].id == "template_123"

    def test_get_command_templates_response_empty_list(self):
        """Test GetCommandTemplatesResponse with empty template list."""
        response = models.GetCommandTemplatesResponse(templates=[])

        assert response.templates == []

    def test_get_command_templates_response_multiple_templates(self):
        """Test GetCommandTemplatesResponse with multiple templates."""
        template1 = models.CommandTemplate(
            _id="template_1",
            name="template_one",
            description="First template",
            namespace="project1",
            passRule=True,
        )

        template2 = models.CommandTemplate(
            _id="template_2",
            name="template_two",
            description="Second template",
            namespace=None,
            passRule=False,
        )

        response = models.GetCommandTemplatesResponse(templates=[template1, template2])

        assert len(response.templates) == 2
        assert response.templates[0] == template1
        assert response.templates[1] == template2


class TestCommandTemplateDetail:
    """Tests for CommandTemplateDetail model."""

    def test_command_template_detail_creation(self):
        """Test creating CommandTemplateDetail with valid data."""
        commands = [
            {"command": "show version", "rules": []},
            {
                "command": "show interfaces",
                "rules": [{"eval": "contains", "value": "up"}],
            },
        ]

        detail = models.CommandTemplateDetail(
            _id="detail_123",
            name="detailed_template",
            commands=commands,
            namespace="project1",
            passRule=True,
        )

        assert detail.id == "detail_123"
        assert detail.name == "detailed_template"
        assert detail.commands == commands
        assert detail.namespace == "project1"
        assert detail.passRule is True

    def test_command_template_detail_empty_commands(self):
        """Test CommandTemplateDetail with empty commands list."""
        detail = models.CommandTemplateDetail(
            _id="empty_123",
            name="empty_template",
            commands=[],
            namespace=None,
            passRule=False,
        )

        assert detail.commands == []


class TestDescribeCommandTemplateResponse:
    """Tests for DescribeCommandTemplateResponse model."""

    def test_describe_command_template_response_creation(self):
        """Test creating DescribeCommandTemplateResponse with valid data."""
        template = models.CommandTemplateDetail(
            _id="template_123",
            name="test_template",
            commands=[{"command": "show version"}],
            namespace="project1",
            passRule=True,
        )

        response = models.DescribeCommandTemplateResponse(template=template)

        assert response.template == template


class TestRuleEvaluation:
    """Tests for RuleEvaluation model."""

    def test_rule_evaluation_creation(self):
        """Test creating RuleEvaluation with valid data."""
        rule = models.RuleEvaluation(
            eval="contains", rule="interface up", severity="error", result=True
        )

        assert rule.eval == "contains"
        assert rule.rule == "interface up"
        assert rule.severity == "error"
        assert rule.result is True

    def test_rule_evaluation_complex_rule(self):
        """Test RuleEvaluation with complex rule data."""
        complex_rule_data = {
            "pattern": "interface.*up",
            "type": "regex",
            "flags": ["ignorecase"],
        }

        rule = models.RuleEvaluation(
            eval="regex", rule=complex_rule_data, severity="warning", result=False
        )

        assert rule.rule == complex_rule_data


class TestCommandResult:
    """Tests for CommandResult model."""

    def test_command_result_creation(self):
        """Test creating CommandResult with valid data."""
        rule = models.RuleEvaluation(
            eval="contains", rule="up", severity="info", result=True
        )

        result = models.CommandResult(
            raw="show interface gi0/0",
            evaluated="show interface GigabitEthernet0/0",
            device="router1",
            response="GigabitEthernet0/0 is up, line protocol is up",
            rules=[rule],
        )

        assert result.raw == "show interface gi0/0"
        assert result.evaluated == "show interface GigabitEthernet0/0"
        assert result.device == "router1"
        assert result.response == "GigabitEthernet0/0 is up, line protocol is up"
        assert len(result.rules) == 1
        assert result.rules[0] == rule

    def test_command_result_no_rules(self):
        """Test CommandResult with no rules."""
        result = models.CommandResult(
            raw="show version",
            evaluated="show version",
            device="switch1",
            response="Cisco IOS Software",
            rules=[],
        )

        assert result.rules == []


class TestRunCommandTemplateResponse:
    """Tests for RunCommandTemplateResponse model."""

    def test_run_command_template_response_creation(self):
        """Test creating RunCommandTemplateResponse with valid data."""
        rule = models.RuleEvaluation(
            eval="contains", rule="up", severity="info", result=True
        )

        cmd_result = models.CommandResult(
            raw="show interfaces",
            evaluated="show interfaces brief",
            device="router1",
            response="Interface status output",
            rules=[rule],
        )

        response = models.RunCommandTemplateResponse(
            name="interface_check_template",
            all_pass_flag=True,
            command_results=[cmd_result],
        )

        assert response.name == "interface_check_template"
        assert response.all_pass_flag is True
        assert len(response.command_results) == 1
        assert response.command_results[0] == cmd_result

    def test_run_command_template_response_multiple_results(self):
        """Test RunCommandTemplateResponse with multiple command results."""
        rule1 = models.RuleEvaluation(
            eval="contains", rule="up", severity="info", result=True
        )
        rule2 = models.RuleEvaluation(
            eval="contains", rule="down", severity="error", result=False
        )

        result1 = models.CommandResult(
            raw="show int gi0/0",
            evaluated="show interface gi0/0",
            device="router1",
            response="gi0/0 is up",
            rules=[rule1],
        )

        result2 = models.CommandResult(
            raw="show int gi0/1",
            evaluated="show interface gi0/1",
            device="router1",
            response="gi0/1 is down",
            rules=[rule2],
        )

        response = models.RunCommandTemplateResponse(
            name="multi_interface_check",
            all_pass_flag=False,
            command_results=[result1, result2],
        )

        assert len(response.command_results) == 2
        assert response.all_pass_flag is False


class TestDeviceCommandResult:
    """Tests for DeviceCommandResult model."""

    def test_device_command_result_creation(self):
        """Test creating DeviceCommandResult with valid data."""
        result = models.DeviceCommandResult(
            device="switch1",
            command="show version",
            response="Cisco IOS Software, Version 15.2",
        )

        assert result.device == "switch1"
        assert result.command == "show version"
        assert result.response == "Cisco IOS Software, Version 15.2"

    def test_device_command_result_empty_response(self):
        """Test DeviceCommandResult with empty response."""
        result = models.DeviceCommandResult(
            device="router1",
            command="show running-config | include hostname",
            response="",
        )

        assert result.response == ""


class TestRunCommandResponse:
    """Tests for RunCommandResponse model."""

    def test_run_command_response_creation(self):
        """Test creating RunCommandResponse with valid data."""
        result1 = models.DeviceCommandResult(
            device="router1", command="show version", response="IOS Version 15.1"
        )

        result2 = models.DeviceCommandResult(
            device="router2", command="show version", response="IOS Version 15.2"
        )

        response = models.RunCommandResponse(results=[result1, result2])

        assert len(response.results) == 2
        assert response.results[0] == result1
        assert response.results[1] == result2

    def test_run_command_response_empty_results(self):
        """Test RunCommandResponse with empty results list."""
        response = models.RunCommandResponse(results=[])

        assert response.results == []

    def test_run_command_response_single_result(self):
        """Test RunCommandResponse with single result."""
        result = models.DeviceCommandResult(
            device="switch1",
            command="show interfaces status",
            response="Port status output",
        )

        response = models.RunCommandResponse(results=[result])

        assert len(response.results) == 1
        assert response.results[0] == result
