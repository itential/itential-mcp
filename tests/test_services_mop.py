# Copyright (c) 2025 Itential, Inc
# GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

import pytest
from unittest.mock import AsyncMock, MagicMock

from itential_mcp.platform.services.mop import Service


class TestMOPService:
    """Test cases for MOP Service class."""

    @pytest.fixture
    def mock_client(self):
        """Create a mock AsyncPlatform client."""
        client = AsyncMock()
        return client

    @pytest.fixture
    def mop_service(self, mock_client):
        """Create a MOP service instance with mock client."""
        return Service(mock_client)

    @pytest.mark.asyncio
    async def test_service_name(self, mop_service):
        """Test that service has correct name."""
        assert mop_service.name == "mop"

    @pytest.mark.asyncio
    async def test_get_project_id_from_name_success(self, mop_service, mock_client):
        """Test successful project ID retrieval."""
        # Mock the API response
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "data": [{"_id": "project_123", "name": "test_project"}]
        }
        mock_client.get.return_value = mock_response

        result = await mop_service._get_project_id_from_name("test_project")

        assert result == "project_123"
        mock_client.get.assert_called_once_with(
            "/automation-studio/projects", params={"equals[name]": "test_project"}
        )

    @pytest.mark.asyncio
    async def test_get_project_id_from_name_not_found(self, mop_service, mock_client):
        """Test project ID retrieval when project not found."""
        # Mock the API response with no results
        mock_response = MagicMock()
        mock_response.json.return_value = {"data": []}
        mock_client.get.return_value = mock_response

        with pytest.raises(ValueError, match="unable to locate project `nonexistent`"):
            await mop_service._get_project_id_from_name("nonexistent")

    @pytest.mark.asyncio
    async def test_get_project_id_from_name_multiple_results(
        self, mop_service, mock_client
    ):
        """Test project ID retrieval when multiple projects match."""
        # Mock the API response with multiple results
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "data": [
                {"_id": "project_1", "name": "test_project"},
                {"_id": "project_2", "name": "test_project"},
            ]
        }
        mock_client.get.return_value = mock_response

        with pytest.raises(ValueError, match="unable to locate project `test_project`"):
            await mop_service._get_project_id_from_name("test_project")

    @pytest.mark.asyncio
    async def test_get_command_templates_success(self, mop_service, mock_client):
        """Test successful retrieval of command templates."""
        expected_templates = [
            {
                "_id": "template_1",
                "name": "Interface Check",
                "description": "Check interface status",
                "namespace": None,
                "passRule": True,
            },
            {
                "_id": "template_2",
                "name": "Version Check",
                "description": "Check device version",
                "namespace": "project_1",
                "passRule": False,
            },
        ]

        mock_response = MagicMock()
        mock_response.json.return_value = expected_templates
        mock_client.get.return_value = mock_response

        result = await mop_service.get_command_templates()

        assert result == expected_templates
        mock_client.get.assert_called_once_with("/mop/listTemplates")

    @pytest.mark.asyncio
    async def test_get_command_templates_empty_list(self, mop_service, mock_client):
        """Test retrieval when no command templates exist."""
        mock_response = MagicMock()
        mock_response.json.return_value = []
        mock_client.get.return_value = mock_response

        result = await mop_service.get_command_templates()

        assert result == []
        mock_client.get.assert_called_once_with("/mop/listTemplates")

    @pytest.mark.asyncio
    async def test_describe_command_template_global(self, mop_service, mock_client):
        """Test describing a global command template."""
        expected_template = {
            "_id": "template_123",
            "name": "Global Template",
            "commands": [{"command": "show version", "rules": []}],
            "namespace": None,
            "passRule": True,
        }

        mock_response = MagicMock()
        mock_response.json.return_value = [expected_template]
        mock_client.get.return_value = mock_response

        result = await mop_service.describe_command_template("Global Template")

        assert result == expected_template
        mock_client.get.assert_called_once_with("/mop/listATemplate/Global Template")

    @pytest.mark.asyncio
    async def test_describe_command_template_with_project(
        self, mop_service, mock_client
    ):
        """Test describing a command template from a specific project."""
        expected_template = {
            "_id": "template_456",
            "name": "Project Template",
            "commands": [{"command": "show interfaces", "rules": []}],
            "namespace": "project_123",
            "passRule": False,
        }

        # Mock project lookup
        mock_project_response = MagicMock()
        mock_project_response.json.return_value = {
            "data": [{"_id": "project_123", "name": "test_project"}]
        }

        # Mock template describe
        mock_template_response = MagicMock()
        mock_template_response.json.return_value = [expected_template]

        mock_client.get.side_effect = [mock_project_response, mock_template_response]

        result = await mop_service.describe_command_template(
            "Project Template", project="test_project"
        )

        assert result == expected_template

        # Verify both API calls were made
        assert mock_client.get.call_count == 2
        mock_client.get.assert_any_call(
            "/automation-studio/projects", params={"equals[name]": "test_project"}
        )
        mock_client.get.assert_any_call(
            "/mop/listATemplate/@project_123: Project Template"
        )

    @pytest.mark.asyncio
    async def test_run_command_template_global(self, mop_service, mock_client):
        """Test running a global command template."""
        expected_result = {
            "name": "Interface Check",
            "all_pass_flag": True,
            "command_results": [
                {
                    "raw": "show int gi0/0",
                    "evaluated": "show interface gi0/0",
                    "device": "router1",
                    "response": "Interface is up",
                    "rules": [],
                }
            ],
        }

        mock_response = MagicMock()
        mock_response.json.return_value = expected_result
        mock_client.post.return_value = mock_response

        result = await mop_service.run_command_template(
            "Interface Check", ["router1", "router2"]
        )

        assert result == expected_result
        mock_client.post.assert_called_once_with(
            "/mop/RunCommandTemplate",
            json={"template": "Interface Check", "devices": ["router1", "router2"]},
        )

    @pytest.mark.asyncio
    async def test_run_command_template_with_project(self, mop_service, mock_client):
        """Test running a command template from a specific project."""
        expected_result = {
            "name": "Project Template",
            "all_pass_flag": False,
            "command_results": [],
        }

        # Mock project lookup
        mock_project_response = MagicMock()
        mock_project_response.json.return_value = {
            "data": [{"_id": "project_456", "name": "my_project"}]
        }

        # Mock template execution
        mock_template_response = MagicMock()
        mock_template_response.json.return_value = expected_result

        mock_client.get.return_value = mock_project_response
        mock_client.post.return_value = mock_template_response

        result = await mop_service.run_command_template(
            "Project Template", ["switch1"], project="my_project"
        )

        assert result == expected_result

        # Verify project lookup call
        mock_client.get.assert_called_once_with(
            "/automation-studio/projects", params={"equals[name]": "my_project"}
        )

        # Verify template execution call
        mock_client.post.assert_called_once_with(
            "/mop/RunCommandTemplate",
            json={"template": "@project_456: Project Template", "devices": ["switch1"]},
        )

    @pytest.mark.asyncio
    async def test_run_command_success(self, mop_service, mock_client):
        """Test successful command execution on multiple devices."""
        expected_result = [
            {
                "device": "router1",
                "raw": "show version",
                "response": "Cisco IOS Version 15.1",
            },
            {
                "device": "router2",
                "raw": "show version",
                "response": "Cisco IOS Version 15.2",
            },
        ]

        mock_response = MagicMock()
        mock_response.json.return_value = expected_result
        mock_client.post.return_value = mock_response

        result = await mop_service.run_command("show version", ["router1", "router2"])

        assert result == expected_result
        mock_client.post.assert_called_once_with(
            "/mop/RunCommandDevices",
            json={"command": "show version", "devices": ["router1", "router2"]},
        )

    @pytest.mark.asyncio
    async def test_run_command_single_device(self, mop_service, mock_client):
        """Test command execution on a single device."""
        expected_result = [
            {
                "device": "switch1",
                "raw": "show interfaces status",
                "response": "Port status information",
            }
        ]

        mock_response = MagicMock()
        mock_response.json.return_value = expected_result
        mock_client.post.return_value = mock_response

        result = await mop_service.run_command("show interfaces status", ["switch1"])

        assert result == expected_result
        mock_client.post.assert_called_once_with(
            "/mop/RunCommandDevices",
            json={"command": "show interfaces status", "devices": ["switch1"]},
        )

    @pytest.mark.asyncio
    async def test_run_command_empty_devices_list(self, mop_service, mock_client):
        """Test command execution with empty devices list."""
        mock_response = MagicMock()
        mock_response.json.return_value = []
        mock_client.post.return_value = mock_response

        result = await mop_service.run_command("show version", [])

        assert result == []
        mock_client.post.assert_called_once_with(
            "/mop/RunCommandDevices", json={"command": "show version", "devices": []}
        )

    @pytest.mark.asyncio
    async def test_get_command_templates_api_error(self, mop_service, mock_client):
        """Test handling of API errors in get_command_templates."""
        mock_client.get.side_effect = Exception("API Error")

        with pytest.raises(Exception, match="API Error"):
            await mop_service.get_command_templates()

    @pytest.mark.asyncio
    async def test_describe_command_template_api_error(self, mop_service, mock_client):
        """Test handling of API errors in describe_command_template."""
        mock_client.get.side_effect = Exception("Template not found")

        with pytest.raises(Exception, match="Template not found"):
            await mop_service.describe_command_template("NonExistent")

    @pytest.mark.asyncio
    async def test_run_command_template_api_error(self, mop_service, mock_client):
        """Test handling of API errors in run_command_template."""
        mock_client.post.side_effect = Exception("Execution failed")

        with pytest.raises(Exception, match="Execution failed"):
            await mop_service.run_command_template("Test Template", ["device1"])

    @pytest.mark.asyncio
    async def test_run_command_api_error(self, mop_service, mock_client):
        """Test handling of API errors in run_command."""
        mock_client.post.side_effect = Exception("Command failed")

        with pytest.raises(Exception, match="Command failed"):
            await mop_service.run_command("show version", ["device1"])

    @pytest.mark.asyncio
    async def test_describe_command_template_project_not_found(
        self, mop_service, mock_client
    ):
        """Test describe_command_template when project lookup fails."""
        # Mock project lookup to return empty results
        mock_project_response = MagicMock()
        mock_project_response.json.return_value = {"data": []}
        mock_client.get.return_value = mock_project_response

        with pytest.raises(ValueError, match="unable to locate project `unknown`"):
            await mop_service.describe_command_template(
                "Template Name", project="unknown"
            )

    @pytest.mark.asyncio
    async def test_run_command_template_project_not_found(
        self, mop_service, mock_client
    ):
        """Test run_command_template when project lookup fails."""
        # Mock project lookup to return empty results
        mock_project_response = MagicMock()
        mock_project_response.json.return_value = {"data": []}
        mock_client.get.return_value = mock_project_response

        with pytest.raises(ValueError, match="unable to locate project `unknown`"):
            await mop_service.run_command_template(
                "Template Name", ["device1"], project="unknown"
            )

    @pytest.mark.asyncio
    async def test_create_command_template_global(self, mop_service, mock_client):
        """Test creating a global command template."""
        commands = [
            {
                "command": "show version",
                "passRule": True,
                "rules": [
                    {"rule": "Version 16.12", "eval": "contains", "severity": "error"}
                ],
            }
        ]

        expected_response = {
            "result": {"ok": 1, "n": 1},
            "ops": [{"_id": "test_template", "name": "test_template"}],
            "insertedCount": 1,
            "insertedIds": {"0": "test_template"},
        }

        mock_response = MagicMock()
        mock_response.json.return_value = expected_response
        mock_client.post.return_value = mock_response

        result = await mop_service.create_command_template(
            name="test_template", commands=commands, description="Test template"
        )

        assert result == expected_response
        mock_client.post.assert_called_once()
        call_args = mock_client.post.call_args
        assert call_args[0][0] == "/mop/createTemplate"
        assert "mop" in call_args[1]["json"]
        assert call_args[1]["json"]["mop"]["name"] == "test_template"
        assert call_args[1]["json"]["mop"]["commands"] == commands
        assert call_args[1]["json"]["mop"]["description"] == "Test template"

    @pytest.mark.asyncio
    async def test_create_command_template_with_project(self, mop_service, mock_client):
        """Test creating a command template in a project."""
        commands = [{"command": "show version", "passRule": True, "rules": []}]

        # Mock project lookup
        mock_project_response = MagicMock()
        mock_project_response.json.return_value = {
            "data": [{"_id": "project123", "name": "Test Project"}]
        }

        expected_response = {
            "result": {"ok": 1, "n": 1},
            "ops": [
                {
                    "_id": "@project123: test_template",
                    "name": "@project123: test_template",
                }
            ],
            "insertedCount": 1,
            "insertedIds": {"0": "@project123: test_template"},
        }

        mock_create_response = MagicMock()
        mock_create_response.json.return_value = expected_response

        # Setup mock to return different responses for different calls
        mock_client.get.return_value = mock_project_response
        mock_client.post.return_value = mock_create_response

        result = await mop_service.create_command_template(
            name="test_template", commands=commands, project="Test Project"
        )

        assert result == expected_response
        mock_client.post.assert_called_once()
        call_args = mock_client.post.call_args
        assert call_args[0][0] == "/mop/createTemplate"
        assert call_args[1]["json"]["mop"]["name"] == "@project123: test_template"

    @pytest.mark.asyncio
    async def test_update_command_template_global(self, mop_service, mock_client):
        """Test updating a global command template."""
        commands = [
            {
                "command": "show ip interface brief",
                "passRule": True,
                "rules": [{"rule": "up", "eval": "contains", "severity": "error"}],
            }
        ]

        # Mock existing template lookup
        existing_template = {
            "_id": "test_template",
            "name": "test_template",
            "created": 1757610875214,
            "createdBy": "test@example.com",
        }
        mock_get_response = MagicMock()
        mock_get_response.json.return_value = [existing_template]

        expected_response = {
            "acknowledged": True,
            "modifiedCount": 1,
            "upsertedId": None,
            "upsertedCount": 0,
            "matchedCount": 1,
        }

        mock_put_response = MagicMock()
        mock_put_response.json.return_value = expected_response

        mock_client.get.return_value = mock_get_response
        mock_client.put.return_value = mock_put_response

        result = await mop_service.update_command_template(
            name="test_template", commands=commands, description="Updated template"
        )

        assert result == expected_response
        mock_client.put.assert_called_once()
        call_args = mock_client.put.call_args
        assert call_args[0][0] == "/mop/updateTemplate/test_template"
        assert call_args[1]["json"]["mop"]["_id"] == "test_template"
        assert call_args[1]["json"]["mop"]["commands"] == commands
        assert call_args[1]["json"]["mop"]["description"] == "Updated template"

    @pytest.mark.asyncio
    async def test_update_command_template_not_found(self, mop_service, mock_client):
        """Test updating a non-existent command template."""
        commands = [{"command": "show version", "passRule": True, "rules": []}]

        # Mock empty template lookup
        mock_get_response = MagicMock()
        mock_get_response.json.return_value = []
        mock_client.get.return_value = mock_get_response

        with pytest.raises(
            ValueError, match="Command template 'nonexistent' not found"
        ):
            await mop_service.update_command_template(
                name="nonexistent", commands=commands
            )
