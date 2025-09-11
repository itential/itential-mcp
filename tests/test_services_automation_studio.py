# Copyright (c) 2025 Itential, Inc
# GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)

import pytest
from unittest.mock import AsyncMock, MagicMock

from itential_mcp.services.automation_studio import Service


class TestAutomationStudioService:
    """Tests for Automation Studio service."""

    @pytest.fixture
    def mock_client(self):
        """Create a mock AsyncPlatform client."""
        client = AsyncMock()
        return client

    @pytest.fixture
    def automation_studio_service(self, mock_client):
        """Create an Automation Studio service instance with mock client."""
        return Service(mock_client)

    def test_service_name(self, automation_studio_service):
        """Test service name is correct."""
        assert automation_studio_service.name == "automation_studio"

    @pytest.mark.asyncio
    async def test_describe_workflow_success(self, automation_studio_service, mock_client):
        """Test successful workflow description."""
        workflow_id = "workflow123"
        expected_workflow = {
            "_id": workflow_id,
            "name": "Test Workflow",
            "description": "A test workflow"
        }
        
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "total": 1,
            "items": [expected_workflow]
        }
        mock_client.get.return_value = mock_response
        
        result = await automation_studio_service.describe_workflow(workflow_id)
        
        assert result == expected_workflow
        mock_client.get.assert_called_once_with(
            "/automation-studio/workflows",
            params={"equals[_id]": workflow_id}
        )

    @pytest.mark.asyncio
    async def test_describe_workflow_not_found(self, automation_studio_service, mock_client):
        """Test workflow not found error."""
        workflow_id = "nonexistent"
        
        mock_response = MagicMock()
        mock_response.json.return_value = {"total": 0, "items": []}
        mock_client.get.return_value = mock_response
        
        from itential_mcp import exceptions
        
        with pytest.raises(exceptions.NotFoundError, match="workflow id nonexistent not found"):
            await automation_studio_service.describe_workflow(workflow_id)

    @pytest.mark.asyncio
    async def test_get_templates_default_params(self, automation_studio_service, mock_client):
        """Test getting templates with default parameters."""
        expected_response = {
            "items": [
                {"_id": "template1", "name": "Template 1", "group": "Group 1"},
                {"_id": "template2", "name": "Template 2", "group": "Group 2"}
            ],
            "total": 2,
            "skip": 0,
            "limit": 50,
            "count": 2,
            "next": None,
            "previous": None
        }
        
        mock_response = MagicMock()
        mock_response.json.return_value = expected_response
        mock_client.get.return_value = mock_response
        
        result = await automation_studio_service.get_templates()
        
        assert result == expected_response
        mock_client.get.assert_called_once_with(
            "/automation-studio/templates",
            params={
                "exclude-project-members": "true",
                "limit": 50,
                "sort": "group",
                "include": "_id,name,group"
            }
        )

    @pytest.mark.asyncio
    async def test_get_templates_custom_params(self, automation_studio_service, mock_client):
        """Test getting templates with custom parameters."""
        expected_response = {"items": [], "total": 0}
        
        mock_response = MagicMock()
        mock_response.json.return_value = expected_response
        mock_client.get.return_value = mock_response
        
        result = await automation_studio_service.get_templates(
            include=("_id", "name"),
            exclude_project_members=False,
            limit=25,
            sort="name",
            skip=10
        )
        
        assert result == expected_response
        mock_client.get.assert_called_once_with(
            "/automation-studio/templates",
            params={
                "exclude-project-members": "false",
                "limit": 25,
                "sort": "name",
                "include": "_id,name",
                "skip": 10
            }
        )

    @pytest.mark.asyncio
    async def test_create_template_success(self, automation_studio_service, mock_client):
        """Test successful template creation."""
        expected_response = {
            "created": {
                "_id": "template123",
                "name": "Test Template",
                "group": "Test Group",
                "description": "Test description",
                "template": "conf t\ninterface {{interface}}\n ip address {{ip}}\nend",
                "type": "jinja2",
                "data": '{"interface": "gi0/1", "ip": "192.168.1.1"}',
                "command": "",
                "created": "2025-01-11T10:00:00.000Z",
                "createdBy": "user123",
                "lastUpdated": "2025-01-11T10:00:00.000Z",
                "lastUpdatedBy": "user123"
            },
            "edit": "/automation-studio/#/edit?tab=0&template=template123"
        }
        
        mock_response = MagicMock()
        mock_response.json.return_value = expected_response
        mock_client.post.return_value = mock_response
        
        result = await automation_studio_service.create_template(
            name="Test Template",
            group="Test Group",
            description="Test description",
            template="conf t\ninterface {{interface}}\n ip address {{ip}}\nend",
            data='{"interface": "gi0/1", "ip": "192.168.1.1"}',
            command="",
            type="jinja2"
        )
        
        assert result == expected_response
        mock_client.post.assert_called_once_with(
            "/automation-studio/templates",
            json={
                "template": {
                    "command": "",
                    "template": "conf t\ninterface {{interface}}\n ip address {{ip}}\nend",
                    "data": '{"interface": "gi0/1", "ip": "192.168.1.1"}',
                    "type": "jinja2",
                    "name": "Test Template",
                    "description": "Test description",
                    "group": "Test Group"
                }
            }
        )

    @pytest.mark.asyncio
    async def test_create_template_minimal(self, automation_studio_service, mock_client):
        """Test template creation with minimal parameters."""
        expected_response = {
            "created": {
                "_id": "template456",
                "name": "Minimal Template",
                "group": "Default Group",
                "description": "Minimal description",
                "template": "show version",
                "type": "jinja2",
                "data": "",
                "command": ""
            }
        }
        
        mock_response = MagicMock()
        mock_response.json.return_value = expected_response
        mock_client.post.return_value = mock_response
        
        result = await automation_studio_service.create_template(
            name="Minimal Template",
            group="Default Group",
            description="Minimal description",
            template="show version"
        )
        
        assert result == expected_response
        mock_client.post.assert_called_once_with(
            "/automation-studio/templates",
            json={
                "template": {
                    "command": "",
                    "template": "show version",
                    "data": "",
                    "type": "jinja2",
                    "name": "Minimal Template",
                    "description": "Minimal description",
                    "group": "Default Group"
                }
            }
        )

    @pytest.mark.asyncio
    async def test_update_template_success(self, automation_studio_service, mock_client):
        """Test successful template update."""
        template_id = "template123"
        expected_response = {
            "updated": {
                "_id": template_id,
                "name": "Updated Template",
                "group": "Updated Group",
                "description": "Updated description",
                "template": "conf t\ninterface {{interface}}\n ip address {{ip}}\nend",
                "type": "jinja2",
                "data": '{"interface": "gi0/2", "ip": "192.168.1.2"}',
                "command": "configure terminal",
                "created": "2025-01-11T10:00:00.000Z",
                "createdBy": {
                    "_id": "user123",
                    "username": "test@example.com",
                    "firstname": "Test",
                    "email": "test@example.com"
                },
                "lastUpdated": "2025-01-11T11:00:00.000Z",
                "lastUpdatedBy": {
                    "_id": "user123",
                    "username": "test@example.com",
                    "firstname": "Test",
                    "email": "test@example.com"
                }
            },
            "edit": "/automation-studio/#/edit?tab=0&template=template123"
        }
        
        mock_response = MagicMock()
        mock_response.json.return_value = expected_response
        mock_client.put.return_value = mock_response
        
        result = await automation_studio_service.update_template(
            template_id=template_id,
            name="Updated Template",
            group="Updated Group",
            description="Updated description",
            template="conf t\ninterface {{interface}}\n ip address {{ip}}\nend",
            data='{"interface": "gi0/2", "ip": "192.168.1.2"}',
            command="configure terminal",
            type="jinja2"
        )
        
        assert result == expected_response
        mock_client.put.assert_called_once_with(
            f"/automation-studio/templates/{template_id}",
            json={
                "update": {
                    "name": "Updated Template",
                    "command": "configure terminal",
                    "template": "conf t\ninterface {{interface}}\n ip address {{ip}}\nend",
                    "type": "jinja2",
                    "data": '{"interface": "gi0/2", "ip": "192.168.1.2"}',
                    "group": "Updated Group",
                    "description": "Updated description"
                }
            }
        )

    @pytest.mark.asyncio
    async def test_update_template_minimal(self, automation_studio_service, mock_client):
        """Test template update with minimal parameters."""
        template_id = "template456"
        expected_response = {
            "updated": {
                "_id": template_id,
                "name": "Minimal Update",
                "group": "Minimal Group",
                "description": "Minimal update description",
                "template": "show interfaces",
                "type": "jinja2",
                "data": "",
                "command": ""
            }
        }
        
        mock_response = MagicMock()
        mock_response.json.return_value = expected_response
        mock_client.put.return_value = mock_response
        
        result = await automation_studio_service.update_template(
            template_id=template_id,
            name="Minimal Update",
            group="Minimal Group",
            description="Minimal update description",
            template="show interfaces"
        )
        
        assert result == expected_response
        mock_client.put.assert_called_once_with(
            f"/automation-studio/templates/{template_id}",
            json={
                "update": {
                    "name": "Minimal Update",
                    "command": "",
                    "template": "show interfaces",
                    "type": "jinja2",
                    "data": "",
                    "group": "Minimal Group",
                    "description": "Minimal update description"
                }
            }
        )