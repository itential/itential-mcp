# Copyright (c) 2025 Itential, Inc
# GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)

import pytest
from unittest.mock import AsyncMock, MagicMock

from itential_mcp.tools import automation_studio_templates


class TestAutomationStudioTemplatesTools:
    """Tests for Automation Studio templates tools."""

    @pytest.fixture
    def mock_client(self):
        """Create a mock client with automation_studio service."""
        client = AsyncMock()
        client.automation_studio = AsyncMock()
        return client

    @pytest.fixture
    def mock_context(self, mock_client):
        """Create a mock FastMCP context."""
        context = MagicMock()
        context.info = AsyncMock()
        context.request_context.lifespan_context.get.return_value = mock_client
        return context

    @pytest.mark.asyncio
    async def test_get_templates_default_params(self, mock_context, mock_client):
        """Test get_templates with default parameters."""
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
        
        mock_client.automation_studio.get_templates.return_value = expected_response
        
        result = await automation_studio_templates.get_templates(
            ctx=mock_context,
            include=("_id", "name", "group"),
            exclude_project_members=True,
            limit=50,
            sort="group",
            skip=None
        )
        
        assert result == expected_response
        mock_client.automation_studio.get_templates.assert_called_once_with(
            include=("_id", "name", "group"),
            exclude_project_members=True,
            limit=50,
            sort="group",
            skip=None
        )

    @pytest.mark.asyncio
    async def test_get_templates_custom_params(self, mock_context, mock_client):
        """Test get_templates with custom parameters."""
        expected_response = {"items": [], "total": 0}
        
        mock_client.automation_studio.get_templates.return_value = expected_response
        
        result = await automation_studio_templates.get_templates(
            ctx=mock_context,
            include=("_id", "name"),
            exclude_project_members=False,
            limit=25,
            sort="name",
            skip=10
        )
        
        assert result == expected_response
        mock_client.automation_studio.get_templates.assert_called_once_with(
            include=("_id", "name"),
            exclude_project_members=False,
            limit=25,
            sort="name",
            skip=10
        )

    @pytest.mark.asyncio
    async def test_create_template_success(self, mock_context, mock_client):
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
        
        mock_client.automation_studio.create_template.return_value = expected_response
        
        result = await automation_studio_templates.create_template(
            ctx=mock_context,
            name="Test Template",
            group="Test Group",
            description="Test description",
            template="conf t\ninterface {{interface}}\n ip address {{ip}}\nend",
            data='{"interface": "gi0/1", "ip": "192.168.1.1"}',
            command="",
            type="jinja2"
        )
        
        assert result == expected_response
        mock_client.automation_studio.create_template.assert_called_once_with(
            name="Test Template",
            group="Test Group",
            description="Test description",
            template="conf t\ninterface {{interface}}\n ip address {{ip}}\nend",
            data='{"interface": "gi0/1", "ip": "192.168.1.1"}',
            command="",
            type="jinja2"
        )

    @pytest.mark.asyncio
    async def test_create_template_minimal(self, mock_context, mock_client):
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
        
        mock_client.automation_studio.create_template.return_value = expected_response
        
        result = await automation_studio_templates.create_template(
            ctx=mock_context,
            name="Minimal Template",
            group="Default Group",
            description="Minimal description",
            template="show version",
            data="",
            command="",
            type="jinja2"
        )
        
        assert result == expected_response
        mock_client.automation_studio.create_template.assert_called_once_with(
            name="Minimal Template",
            group="Default Group",
            description="Minimal description",
            template="show version",
            data="",
            command="",
            type="jinja2"
        )

    @pytest.mark.asyncio
    async def test_update_template_success(self, mock_context, mock_client):
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
        
        mock_client.automation_studio.update_template.return_value = expected_response
        
        result = await automation_studio_templates.update_template(
            ctx=mock_context,
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
        mock_client.automation_studio.update_template.assert_called_once_with(
            template_id=template_id,
            name="Updated Template",
            group="Updated Group",
            description="Updated description",
            template="conf t\ninterface {{interface}}\n ip address {{ip}}\nend",
            data='{"interface": "gi0/2", "ip": "192.168.1.2"}',
            command="configure terminal",
            type="jinja2"
        )

    @pytest.mark.asyncio
    async def test_update_template_minimal(self, mock_context, mock_client):
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
        
        mock_client.automation_studio.update_template.return_value = expected_response
        
        result = await automation_studio_templates.update_template(
            ctx=mock_context,
            template_id=template_id,
            name="Minimal Update",
            group="Minimal Group",
            description="Minimal update description",
            template="show interfaces",
            data="",
            command="",
            type="jinja2"
        )
        
        assert result == expected_response
        mock_client.automation_studio.update_template.assert_called_once_with(
            template_id=template_id,
            name="Minimal Update",
            group="Minimal Group",
            description="Minimal update description",
            template="show interfaces",
            data="",
            command="",
            type="jinja2"
        )
