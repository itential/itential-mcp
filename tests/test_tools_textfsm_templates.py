# Copyright (c) 2025 Itential, Inc
# GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)

import pytest
from unittest.mock import AsyncMock, MagicMock

from itential_mcp.tools import textfsm_templates


class TestTextFSMTemplatesTools:
    """Tests for TextFSM templates tools."""

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
    async def test_get_textfsm_templates_default_params(self, mock_context, mock_client):
        """Test get_textfsm_templates with default parameters."""
        expected_response = {
            "items": [
                {"_id": "template1", "name": "ACL Parser", "group": "Network Parsers"},
                {"_id": "template2", "name": "Interface Parser", "group": "Network Parsers"}
            ],
            "total": 2,
            "skip": 0,
            "limit": 50,
            "count": 2,
            "next": None,
            "previous": None
        }
        
        mock_client.automation_studio.get_templates.return_value = expected_response
        
        result = await textfsm_templates.get_textfsm_templates(
            ctx=mock_context,
            include="_id,name,group",
            exclude_project_members=True,
            limit=50,
            sort="group",
            skip=None
        )
        
        assert result == expected_response
        mock_client.automation_studio.get_templates.assert_called_once_with(
            include=["_id", "name", "group"],
            exclude_project_members=True,
            limit=50,
            sort="group",
            skip=None
        )

    @pytest.mark.asyncio
    async def test_get_textfsm_templates_custom_params(self, mock_context, mock_client):
        """Test get_textfsm_templates with custom parameters."""
        expected_response = {"items": [], "total": 0}
        
        mock_client.automation_studio.get_templates.return_value = expected_response
        
        result = await textfsm_templates.get_textfsm_templates(
            ctx=mock_context,
            include="_id,name",
            exclude_project_members=False,
            limit=25,
            sort="name",
            skip=10
        )
        
        assert result == expected_response
        mock_client.automation_studio.get_templates.assert_called_once_with(
            include=["_id", "name"],
            exclude_project_members=False,
            limit=25,
            sort="name",
            skip=10
        )

    @pytest.mark.asyncio
    async def test_create_textfsm_template_success(self, mock_context, mock_client):
        """Test successful TextFSM template creation."""
        expected_response = {
            "created": {
                "_id": "template123",
                "name": "ACL Parser",
                "group": "Network Parsers",
                "description": "Parse Cisco ACL configurations",
                "template": "Value Required,Filldown ACL_NAME (\\S+)\nValue ACL_TYPE (standard|extended)\nValue ACTION (permit|deny)\nValue PROTOCOL ([a-z]+)\n\nStart\n  ^ip\\s+access-list\\s+${ACL_TYPE}\\s+${ACL_NAME}\\s* -> Record\n  ^\\s+${ACTION}\\s+${PROTOCOL}\\s+.* -> Record\n\nEOF",
                "type": "textfsm",
                "data": "ip access-list extended sample\n permit tcp host 10.1.1.1 any\n deny ip any any",
                "command": "show access-list",
                "created": "2025-01-11T10:00:00.000Z",
                "createdBy": "user123",
                "lastUpdated": "2025-01-11T10:00:00.000Z",
                "lastUpdatedBy": "user123"
            },
            "edit": "/automation-studio/#/edit?tab=0&template=template123"
        }
        
        mock_client.automation_studio.create_textfsm_template.return_value = expected_response
        
        result = await textfsm_templates.create_textfsm_template(
            ctx=mock_context,
            name="ACL Parser",
            group="Network Parsers",
            description="Parse Cisco ACL configurations",
            template="Value Required,Filldown ACL_NAME (\\S+)\nValue ACL_TYPE (standard|extended)\nValue ACTION (permit|deny)\nValue PROTOCOL ([a-z]+)\n\nStart\n  ^ip\\s+access-list\\s+${ACL_TYPE}\\s+${ACL_NAME}\\s* -> Record\n  ^\\s+${ACTION}\\s+${PROTOCOL}\\s+.* -> Record\n\nEOF",
            data="ip access-list extended sample\n permit tcp host 10.1.1.1 any\n deny ip any any",
            command="show access-list"
        )
        
        assert result.created.id == "template123"
        assert result.created.name == "ACL Parser"
        assert result.created.type == "textfsm"
        assert result.edit == "/automation-studio/#/edit?tab=0&template=template123"
        mock_client.automation_studio.create_textfsm_template.assert_called_once_with(
            name="ACL Parser",
            group="Network Parsers",
            description="Parse Cisco ACL configurations",
            template="Value Required,Filldown ACL_NAME (\\S+)\nValue ACL_TYPE (standard|extended)\nValue ACTION (permit|deny)\nValue PROTOCOL ([a-z]+)\n\nStart\n  ^ip\\s+access-list\\s+${ACL_TYPE}\\s+${ACL_NAME}\\s* -> Record\n  ^\\s+${ACTION}\\s+${PROTOCOL}\\s+.* -> Record\n\nEOF",
            data="ip access-list extended sample\n permit tcp host 10.1.1.1 any\n deny ip any any",
            command="show access-list"
        )

    @pytest.mark.asyncio
    async def test_create_textfsm_template_minimal(self, mock_context, mock_client):
        """Test TextFSM template creation with minimal parameters."""
        expected_response = {
            "created": {
                "_id": "template456",
                "name": "Simple Parser",
                "group": "Basic Parsers",
                "description": "Simple parsing template",
                "template": "Value NAME (\\S+)\n\nStart\n  ^${NAME} -> Record\n\nEOF",
                "type": "textfsm",
                "data": "",
                "command": "",
                "created": "2025-01-11T10:00:00.000Z",
                "lastUpdated": "2025-01-11T10:00:00.000Z",
                "createdBy": "user123",
                "lastUpdatedBy": "user123",
                "tags": []
            },
            "edit": "/automation-studio/#/edit?tab=0&template=template456"
        }
        
        mock_client.automation_studio.create_textfsm_template.return_value = expected_response
        
        result = await textfsm_templates.create_textfsm_template(
            ctx=mock_context,
            name="Simple Parser",
            group="Basic Parsers",
            description="Simple parsing template",
            template="Value NAME (\\S+)\n\nStart\n  ^${NAME} -> Record\n\nEOF",
            data="",
            command=""
        )
        
        assert result.created.id == "template456"
        assert result.created.name == "Simple Parser"
        assert result.created.type == "textfsm"
        mock_client.automation_studio.create_textfsm_template.assert_called_once_with(
            name="Simple Parser",
            group="Basic Parsers",
            description="Simple parsing template",
            template="Value NAME (\\S+)\n\nStart\n  ^${NAME} -> Record\n\nEOF",
            data="",
            command=""
        )

    @pytest.mark.asyncio
    async def test_update_textfsm_template_success(self, mock_context, mock_client):
        """Test successful TextFSM template update."""
        template_id = "template123"
        expected_response = {
            "updated": {
                "_id": template_id,
                "name": "Updated ACL Parser",
                "group": "Updated Network Parsers",
                "description": "Updated parse Cisco ACL configurations",
                "template": "Value Required,Filldown ACL_NAME (\\S+)\nValue ACL_TYPE (standard|extended)\nValue ACTION (permit|deny)\nValue PROTOCOL ([a-z]+)\n\nStart\n  ^ip\\s+access-list\\s+${ACL_TYPE}\\s+${ACL_NAME}\\s* -> Record\n  ^\\s+${ACTION}\\s+${PROTOCOL}\\s+.* -> Record\n\nEOF",
                "type": "textfsm",
                "data": "ip access-list extended updated\n permit tcp host 10.1.1.1 any\n deny ip any any",
                "command": "show access-list",
                "created": "2025-01-11T10:00:00.000Z",
                "createdBy": "user123",
                "lastUpdated": "2025-01-11T11:00:00.000Z",
                "lastUpdatedBy": "user123"
            },
            "edit": "/automation-studio/#/edit?tab=0&template=template123"
        }
        
        mock_client.automation_studio.update_textfsm_template.return_value = expected_response
        
        result = await textfsm_templates.update_textfsm_template(
            ctx=mock_context,
            template_id=template_id,
            name="Updated ACL Parser",
            group="Updated Network Parsers",
            description="Updated parse Cisco ACL configurations",
            template="Value Required,Filldown ACL_NAME (\\S+)\nValue ACL_TYPE (standard|extended)\nValue ACTION (permit|deny)\nValue PROTOCOL ([a-z]+)\n\nStart\n  ^ip\\s+access-list\\s+${ACL_TYPE}\\s+${ACL_NAME}\\s* -> Record\n  ^\\s+${ACTION}\\s+${PROTOCOL}\\s+.* -> Record\n\nEOF",
            data="ip access-list extended updated\n permit tcp host 10.1.1.1 any\n deny ip any any",
            command="show access-list"
        )
        
        assert result.updated.id == template_id
        assert result.updated.name == "Updated ACL Parser"
        assert result.updated.type == "textfsm"
        assert result.edit == "/automation-studio/#/edit?tab=0&template=template123"
        mock_client.automation_studio.update_textfsm_template.assert_called_once_with(
            template_id=template_id,
            name="Updated ACL Parser",
            group="Updated Network Parsers",
            description="Updated parse Cisco ACL configurations",
            template="Value Required,Filldown ACL_NAME (\\S+)\nValue ACL_TYPE (standard|extended)\nValue ACTION (permit|deny)\nValue PROTOCOL ([a-z]+)\n\nStart\n  ^ip\\s+access-list\\s+${ACL_TYPE}\\s+${ACL_NAME}\\s* -> Record\n  ^\\s+${ACTION}\\s+${PROTOCOL}\\s+.* -> Record\n\nEOF",
            data="ip access-list extended updated\n permit tcp host 10.1.1.1 any\n deny ip any any",
            command="show access-list"
        )

    @pytest.mark.asyncio
    async def test_update_textfsm_template_minimal(self, mock_context, mock_client):
        """Test TextFSM template update with minimal parameters."""
        template_id = "template456"
        expected_response = {
            "updated": {
                "_id": template_id,
                "name": "Minimal Update",
                "group": "Minimal Group",
                "description": "Minimal update description",
                "template": "Value NAME (\\S+)\n\nStart\n  ^${NAME} -> Record\n\nEOF",
                "type": "textfsm",
                "data": "",
                "command": "",
                "created": "2025-01-11T10:00:00.000Z",
                "lastUpdated": "2025-01-11T11:00:00.000Z",
                "createdBy": "user123",
                "lastUpdatedBy": "user123",
                "tags": []
            },
            "edit": "/automation-studio/#/edit?tab=0&template=template456"
        }
        
        mock_client.automation_studio.update_textfsm_template.return_value = expected_response
        
        result = await textfsm_templates.update_textfsm_template(
            ctx=mock_context,
            template_id=template_id,
            name="Minimal Update",
            group="Minimal Group",
            description="Minimal update description",
            template="Value NAME (\\S+)\n\nStart\n  ^${NAME} -> Record\n\nEOF",
            data="",
            command=""
        )
        
        assert result.updated.id == template_id
        assert result.updated.name == "Minimal Update"
        assert result.updated.type == "textfsm"
        mock_client.automation_studio.update_textfsm_template.assert_called_once_with(
            template_id=template_id,
            name="Minimal Update",
            group="Minimal Group",
            description="Minimal update description",
            template="Value NAME (\\S+)\n\nStart\n  ^${NAME} -> Record\n\nEOF",
            data="",
            command=""
        )
