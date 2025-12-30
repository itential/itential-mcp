# Copyright (c) 2025 Itential, Inc
# GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

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
            namespace={
                "type": "project",
                "_id": "test_project",
                "name": "Test Project",
            },
            passRule=True,
        )

        assert template.id == "template_123"
        assert template.name == "test_template"
        assert template.description == "Test command template"
        assert template.namespace["_id"] == "test_project"
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
            namespace={"type": "project", "_id": "project1", "name": "Project 1"},
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
            namespace={"type": "project", "_id": "project1", "name": "Project 1"},
            passRule=True,
        )

        assert detail.id == "detail_123"
        assert detail.name == "detailed_template"
        assert detail.commands == commands
        assert detail.namespace["_id"] == "project1"
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
            namespace={"type": "project", "_id": "project1", "name": "Project 1"},
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


class TestCreateCommandTemplateRequest:
    """Tests for CreateCommandTemplateRequest model."""

    def test_create_command_template_request_creation(self):
        """Test creating a CreateCommandTemplateRequest with valid data."""
        commands = [
            {
                "command": "show version",
                "passRule": True,
                "rules": [
                    {"rule": "Version 16.12", "eval": "contains", "severity": "error"}
                ],
            }
        ]

        request = models.CreateCommandTemplateRequest(
            name="test_template",
            commands=commands,
            description="Test template",
            project="Test Project",
        )

        assert request.name == "test_template"
        assert request.commands == commands
        assert request.description == "Test template"
        assert request.project == "Test Project"
        assert request.os == ""
        assert request.pass_rule is True
        assert request.ignore_warnings is False

    def test_create_command_template_request_with_regex(self):
        """Test CreateCommandTemplateRequest with regex and variable substitution."""
        commands = [
            {
                "command": "show interfaces <!type!> <!interface!>.<!subInterface!>",
                "passRule": True,
                "rules": [
                    {
                        "rule": "<!type!><!interface!>.<!subInterface!>.*\\s+.*(down|up)",
                        "eval": "RegEx",
                        "severity": "error",
                    }
                ],
            }
        ]

        request = models.CreateCommandTemplateRequest(
            name="interface_check",
            commands=commands,
            description="Interface status check with regex",
        )

        assert request.name == "interface_check"
        assert (
            request.commands[0]["command"]
            == "show interfaces <!type!> <!interface!>.<!subInterface!>"
        )
        assert request.commands[0]["rules"][0]["eval"] == "RegEx"
        assert (
            request.commands[0]["rules"][0]["rule"]
            == "<!type!><!interface!>.<!subInterface!>.*\\s+.*(down|up)"
        )

    def test_create_command_template_request_defaults(self):
        """Test CreateCommandTemplateRequest with default values."""
        commands = [{"command": "show version", "passRule": True, "rules": []}]

        request = models.CreateCommandTemplateRequest(
            name="minimal_template", commands=commands
        )

        assert request.name == "minimal_template"
        assert request.commands == commands
        assert request.description is None
        assert request.project is None
        assert request.os == ""
        assert request.pass_rule is True
        assert request.ignore_warnings is False


class TestCreateCommandTemplateResponse:
    """Tests for CreateCommandTemplateResponse model."""

    def test_create_command_template_response_creation(self):
        """Test creating a CreateCommandTemplateResponse with valid data."""
        response_data = {
            "result": {"ok": 1, "n": 1},
            "ops": [
                {
                    "_id": "testcmd",
                    "name": "testcmd",
                    "os": "",
                    "passRule": True,
                    "ignoreWarnings": False,
                    "commands": [],
                    "created": 1757610875214,
                    "createdBy": "test@example.com",
                    "lastUpdated": 1757610875484,
                    "lastUpdatedBy": "test@example.com",
                }
            ],
            "insertedCount": 1,
            "insertedIds": {"0": "testcmd"},
        }

        response = models.CreateCommandTemplateResponse(**response_data)

        assert response.result == {"ok": 1, "n": 1}
        assert len(response.ops) == 1
        assert response.ops[0]["_id"] == "testcmd"
        assert response.inserted_count == 1
        assert response.inserted_ids == {"0": "testcmd"}


class TestUpdateCommandTemplateRequest:
    """Tests for UpdateCommandTemplateRequest model."""

    def test_update_command_template_request_creation(self):
        """Test creating an UpdateCommandTemplateRequest with valid data."""
        commands = [
            {
                "command": "show ip interface brief",
                "passRule": True,
                "rules": [{"rule": "up", "eval": "contains", "severity": "error"}],
            }
        ]

        request = models.UpdateCommandTemplateRequest(
            name="existing_template", commands=commands, description="Updated template"
        )

        assert request.name == "existing_template"
        assert request.commands == commands
        assert request.description == "Updated template"
        assert request.project is None
        assert request.os == ""
        assert request.pass_rule is True
        assert request.ignore_warnings is False


class TestUpdateCommandTemplateResponse:
    """Tests for UpdateCommandTemplateResponse model."""

    def test_update_command_template_response_creation(self):
        """Test creating an UpdateCommandTemplateResponse with valid data."""
        response_data = {
            "acknowledged": True,
            "modifiedCount": 1,
            "upsertedId": None,
            "upsertedCount": 0,
            "matchedCount": 1,
        }

        response = models.UpdateCommandTemplateResponse(**response_data)

        assert response.acknowledged is True
        assert response.modified_count == 1
        assert response.upserted_id is None
        assert response.upserted_count == 0
        assert response.matched_count == 1
