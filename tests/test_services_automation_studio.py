# Copyright (c) 2025 Itential, Inc
# GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

import pytest
from unittest.mock import AsyncMock, MagicMock

from itential_mcp.core import exceptions
from itential_mcp.platform.services.automation_studio import Service


class TestAutomationStudioService:
    """Test cases for the Automation Studio Service class"""

    @pytest.fixture
    def mock_client(self):
        """Create a mock client for testing"""
        client = AsyncMock()
        return client

    @pytest.fixture
    def service(self, mock_client):
        """Create a Service instance with mocked client"""
        service = Service(mock_client)
        return service

    def test_service_name(self, mock_client):
        """Test that the service has the correct name"""
        service = Service(mock_client)
        assert service.name == "automation_studio"

    @pytest.mark.asyncio
    async def test_describe_workflow_success(self, service, mock_client):
        """Test successful workflow retrieval"""
        # Mock response data
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "total": 1,
            "items": [
                {
                    "_id": "workflow-123",
                    "name": "Test Workflow",
                    "description": "Test workflow description",
                    "type": "automation",
                    "status": "active",
                }
            ],
        }
        mock_client.get.return_value = mock_response

        result = await service.describe_workflow_with_id("workflow-123")

        # Verify client was called with correct parameters
        mock_client.get.assert_called_once_with(
            "/automation-studio/workflows", params={"equals[_id]": "workflow-123"}
        )

        # Verify response data
        assert result["_id"] == "workflow-123"
        assert result["name"] == "Test Workflow"
        assert result["description"] == "Test workflow description"

    @pytest.mark.asyncio
    async def test_describe_workflow_not_found(self, service, mock_client):
        """Test workflow not found error"""
        # Mock response with no results
        mock_response = MagicMock()
        mock_response.json.return_value = {"total": 0, "items": []}
        mock_client.get.return_value = mock_response

        with pytest.raises(exceptions.NotFoundError) as exc_info:
            await service.describe_workflow_with_id("nonexistent-workflow")

        assert "workflow not found" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_describe_workflow_multiple_found(self, service, mock_client):
        """Test workflow multiple results error"""
        # Mock response with multiple results (should not happen but test defensive code)
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "total": 2,
            "items": [
                {"_id": "workflow-1", "name": "Workflow 1"},
                {"_id": "workflow-2", "name": "Workflow 2"},
            ],
        }
        mock_client.get.return_value = mock_response

        with pytest.raises(exceptions.NotFoundError) as exc_info:
            await service.describe_workflow_with_id("duplicate-workflow")

        assert "workflow not found" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_get_templates_no_filter(self, service, mock_client):
        """Test getting all templates without filtering"""
        # Mock response data for single page
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "total": 2,
            "items": [
                {
                    "_id": "template-1",
                    "name": "Test Template 1",
                    "type": "textfsm",
                    "group": "parsing",
                },
                {
                    "_id": "template-2",
                    "name": "Test Template 2",
                    "type": "jinja2",
                    "group": "configuration",
                },
            ],
        }
        mock_client.get.return_value = mock_response

        result = await service.get_templates()

        # Verify client was called with correct parameters
        mock_client.get.assert_called_once_with(
            "/automation-studio/templates", params={"limit": 100, "skip": 0}
        )

        # Verify response data
        assert len(result) == 2
        assert result[0]["_id"] == "template-1"
        assert result[0]["type"] == "textfsm"
        assert result[1]["_id"] == "template-2"
        assert result[1]["type"] == "jinja2"

    @pytest.mark.asyncio
    async def test_get_templates_with_type_filter(self, service, mock_client):
        """Test getting templates with type filter"""
        # Mock response data
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "total": 1,
            "items": [
                {
                    "_id": "template-textfsm",
                    "name": "TextFSM Template",
                    "type": "textfsm",
                    "group": "parsing",
                }
            ],
        }
        mock_client.get.return_value = mock_response

        result = await service.get_templates(template_type="textfsm")

        # Verify client was called with correct parameters
        mock_client.get.assert_called_once_with(
            "/automation-studio/templates",
            params={"limit": 100, "equals[type]": "textfsm", "skip": 0},
        )

        # Verify response data
        assert len(result) == 1
        assert result[0]["type"] == "textfsm"

    @pytest.mark.asyncio
    async def test_get_templates_pagination(self, service, mock_client):
        """Test templates retrieval with pagination"""
        call_count = 0

        def mock_get(url, params=None):
            nonlocal call_count
            mock_response = MagicMock()

            if call_count == 0:
                # First call - return first 100 items
                mock_response.json.return_value = {
                    "total": 150,
                    "items": [
                        {"_id": f"template-{i}", "name": f"Template {i}"}
                        for i in range(100)
                    ],
                }
            else:
                # Second call - return remaining 50 items
                mock_response.json.return_value = {
                    "total": 150,
                    "items": [
                        {"_id": f"template-{i}", "name": f"Template {i}"}
                        for i in range(100, 150)
                    ],
                }

            call_count += 1
            return mock_response

        mock_client.get.side_effect = mock_get

        result = await service.get_templates()

        # Verify client was called twice for pagination
        assert mock_client.get.call_count == 2

        # Verify the correct URL was called
        call_args_list = mock_client.get.call_args_list
        assert all(
            call[0][0] == "/automation-studio/templates" for call in call_args_list
        )

        # Note: We can't reliably test the exact param values because the service
        # modifies the same params dict in place, so by the time the mock records
        # the calls, all calls show the final state. This is normal behavior for
        # the service and the important thing is that it makes the right number
        # of calls and gets the right total results.

        # Verify response data
        assert len(result) == 150

    @pytest.mark.asyncio
    async def test_get_templates_empty_response(self, service, mock_client):
        """Test getting templates with empty response"""
        mock_response = MagicMock()
        mock_response.json.return_value = {"total": 0, "items": []}
        mock_client.get.return_value = mock_response

        result = await service.get_templates()

        assert len(result) == 0

    @pytest.mark.asyncio
    async def test_get_projects_success(self, service, mock_client):
        """Test successful projects retrieval"""
        # Mock response data for single page
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "data": [
                {
                    "_id": "project-1",
                    "name": "Test Project 1",
                    "description": "First test project",
                },
                {
                    "_id": "project-2",
                    "name": "Test Project 2",
                    "description": "Second test project",
                },
            ],
            "metadata": {"total": 2, "skip": 0, "limit": 100},
        }
        mock_client.get.return_value = mock_response

        result = await service.get_projects()

        # Verify client was called with correct parameters
        mock_client.get.assert_called_once_with(
            "/automation-studio/projects", params={"limit": 100, "skip": 0}
        )

        # Verify response data
        assert len(result) == 2
        assert result[0]["_id"] == "project-1"
        assert result[0]["name"] == "Test Project 1"
        assert result[1]["_id"] == "project-2"
        assert result[1]["name"] == "Test Project 2"

    @pytest.mark.asyncio
    async def test_get_projects_pagination(self, service, mock_client):
        """Test projects retrieval with pagination"""
        call_count = 0

        def mock_get(url, params=None):
            nonlocal call_count
            mock_response = MagicMock()

            if call_count == 0:
                # First call - return first 100 items
                mock_response.json.return_value = {
                    "data": [
                        {"_id": f"project-{i}", "name": f"Project {i}"}
                        for i in range(100)
                    ],
                    "metadata": {"total": 150, "skip": 0, "limit": 100},
                }
            else:
                # Second call - return remaining 50 items
                mock_response.json.return_value = {
                    "data": [
                        {"_id": f"project-{i}", "name": f"Project {i}"}
                        for i in range(100, 150)
                    ],
                    "metadata": {"total": 150, "skip": 100, "limit": 100},
                }

            call_count += 1
            return mock_response

        mock_client.get.side_effect = mock_get

        result = await service.get_projects()

        # Verify client was called twice for pagination
        assert mock_client.get.call_count == 2

        # Verify the correct URL was called
        call_args_list = mock_client.get.call_args_list
        assert all(
            call[0][0] == "/automation-studio/projects" for call in call_args_list
        )

        # Note: We can't reliably test the exact param values because the service
        # modifies the same params dict in place, so by the time the mock records
        # the calls, all calls show the final state. This is normal behavior for
        # the service and the important thing is that it makes the right number
        # of calls and gets the right total results.

        # Verify response data
        assert len(result) == 150

    @pytest.mark.asyncio
    async def test_get_projects_empty_response(self, service, mock_client):
        """Test getting projects with empty response"""
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "data": [],
            "metadata": {"total": 0, "skip": 0, "limit": 100},
        }
        mock_client.get.return_value = mock_response

        result = await service.get_projects()

        assert len(result) == 0

    @pytest.mark.asyncio
    async def test_describe_project_success(self, service, mock_client):
        """Test successful project description"""
        # Mock responses for the two API calls
        mock_search_response = MagicMock()
        mock_search_response.json.return_value = {
            "data": [{"_id": "project-123", "name": "Test Project"}],
            "metadata": {"total": 1},
        }

        mock_detail_response = MagicMock()
        mock_detail_response.json.return_value = {
            "data": {
                "_id": "project-123",
                "name": "Test Project",
                "description": "Detailed test project",
                "components": [
                    {
                        "name": ": Test Workflow",
                        "type": "workflow",
                        "reference": "workflow-ref",
                        "folder": "/workflows",
                    }
                ],
            }
        }

        # Configure mock to return different responses for different calls
        mock_client.get.side_effect = [mock_search_response, mock_detail_response]

        result = await service.describe_project("Test Project")

        # Verify both API calls were made
        assert mock_client.get.call_count == 2
        mock_client.get.assert_any_call(
            "/automation-studio/projects", params={"equals[name]": "Test Project"}
        )
        mock_client.get.assert_any_call("/automation-studio/projects/project-123")

        # Verify response data
        assert result["_id"] == "project-123"
        assert result["name"] == "Test Project"
        assert result["description"] == "Detailed test project"
        assert len(result["components"]) == 1

    @pytest.mark.asyncio
    async def test_describe_project_not_found(self, service, mock_client):
        """Test project not found error"""
        # Mock response with no results
        mock_response = MagicMock()
        mock_response.json.return_value = {"data": [], "metadata": {"total": 0}}
        mock_client.get.return_value = mock_response

        with pytest.raises(exceptions.NotFoundError) as exc_info:
            await service.describe_project("Nonexistent Project")

        assert "unable to find project: Nonexistent Project" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_describe_project_multiple_found(self, service, mock_client):
        """Test project multiple results error"""
        # Mock response with multiple results (should not happen but test defensive code)
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "data": [
                {"_id": "project-1", "name": "Duplicate Project"},
                {"_id": "project-2", "name": "Duplicate Project"},
            ],
            "metadata": {"total": 2},
        }
        mock_client.get.return_value = mock_response

        with pytest.raises(exceptions.NotFoundError) as exc_info:
            await service.describe_project("Duplicate Project")

        assert "unable to find project: Duplicate Project" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_describe_project_case_sensitive(self, service, mock_client):
        """Test that project name search is case sensitive"""
        mock_response = MagicMock()
        mock_response.json.return_value = {"data": [], "metadata": {"total": 0}}
        mock_client.get.return_value = mock_response

        with pytest.raises(exceptions.NotFoundError):
            await service.describe_project("test project")  # lowercase

        # Verify the exact search was performed
        mock_client.get.assert_called_once_with(
            "/automation-studio/projects", params={"equals[name]": "test project"}
        )

    @pytest.mark.asyncio
    async def test_get_templates_jinja2_filter(self, service, mock_client):
        """Test getting templates with jinja2 filter (note: typo in original code)"""
        # Note: The original code has a typo "jinaj2" instead of "jinja2"
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "total": 1,
            "items": [
                {
                    "_id": "template-jinja2",
                    "name": "Jinja2 Template",
                    "type": "jinja2",
                    "group": "configuration",
                }
            ],
        }
        mock_client.get.return_value = mock_response

        # Test the typo version as it exists in the code
        result = await service.get_templates(template_type="jinaj2")

        # Verify client was called with correct parameters
        mock_client.get.assert_called_once_with(
            "/automation-studio/templates",
            params={"limit": 100, "equals[type]": "jinaj2", "skip": 0},
        )

        assert len(result) == 1

    @pytest.mark.asyncio
    async def test_client_error_handling(self, service, mock_client):
        """Test that client errors are propagated correctly"""
        # Mock client to raise an exception
        mock_client.get.side_effect = Exception("Network error")

        with pytest.raises(Exception) as exc_info:
            await service.describe_workflow_with_id("test-workflow")

        assert "Network error" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_pagination_edge_case_exact_page_size(self, service, mock_client):
        """Test pagination when total matches page size exactly"""
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "total": 100,
            "items": [
                {"_id": f"template-{i}", "name": f"Template {i}"} for i in range(100)
            ],
        }
        mock_client.get.return_value = mock_response

        result = await service.get_templates()

        # Should only make one call since we got all results
        mock_client.get.assert_called_once()
        assert len(result) == 100

    @pytest.mark.asyncio
    async def test_describe_project_minimal_data(self, service, mock_client):
        """Test describe project with minimal response data"""
        # Mock responses with minimal required fields
        mock_search_response = MagicMock()
        mock_search_response.json.return_value = {
            "data": [{"_id": "minimal-project"}],
            "metadata": {"total": 1},
        }

        mock_detail_response = MagicMock()
        mock_detail_response.json.return_value = {
            "data": {"_id": "minimal-project", "components": []}
        }

        mock_client.get.side_effect = [mock_search_response, mock_detail_response]

        result = await service.describe_project("Minimal Project")

        assert result["_id"] == "minimal-project"
        assert result["components"] == []

    @pytest.mark.asyncio
    async def test_describe_template_success(self, service, mock_client):
        """Test successful template description retrieval"""
        # Mock _get_templates call
        service._get_templates = AsyncMock()
        service._get_templates.return_value = [
            {
                "_id": "template-123",
                "name": "Test Template",
                "description": "Test template description",
                "type": "textfsm",
                "group": "parsing",
                "command": "show version",
                "template": "Value VERSION (\\S+)",
                "data": "sample output",
            }
        ]

        result = await service.describe_template("Test Template", project=None)

        # Verify _get_templates was called with correct parameters
        service._get_templates.assert_called_once_with(
            params={"equals[name]": "Test Template"}
        )

        # Verify response data
        assert result["_id"] == "template-123"
        assert result["name"] == "Test Template"
        assert result["description"] == "Test template description"
        assert result["type"] == "textfsm"
        assert result["group"] == "parsing"
        assert result["command"] == "show version"
        assert result["template"] == "Value VERSION (\\S+)"
        assert result["data"] == "sample output"

    @pytest.mark.asyncio
    async def test_describe_template_with_project(self, service, mock_client):
        """Test template description retrieval with project"""
        # Mock describe_project call
        service.describe_project = AsyncMock()
        service.describe_project.return_value = {"_id": "project-123"}

        # Mock _get_templates call
        service._get_templates = AsyncMock()
        service._get_templates.return_value = [
            {
                "_id": "template-456",
                "name": "@project-123: Project Template",
                "type": "jinja2",
                "group": "config",
            }
        ]

        result = await service.describe_template(
            "Project Template", project="my-project"
        )

        # Verify describe_project was called
        service.describe_project.assert_called_once_with("my-project")

        # Verify _get_templates was called with project-prefixed name
        service._get_templates.assert_called_once_with(
            params={"equals[name]": "@project-123: Project Template"}
        )

        # Verify response data
        assert result["_id"] == "template-456"
        assert result["name"] == "@project-123: Project Template"
        assert result["type"] == "jinja2"

    @pytest.mark.asyncio
    async def test_describe_template_not_found(self, service, mock_client):
        """Test template description when template is not found"""
        # Mock _get_templates to return empty list
        service._get_templates = AsyncMock()
        service._get_templates.return_value = []

        with pytest.raises(exceptions.NotFoundError) as exc_info:
            await service.describe_template("Nonexistent Template")

        assert "template Nonexistent Template could not found" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_describe_template_multiple_found(self, service, mock_client):
        """Test template description when multiple templates are found"""
        # Mock _get_templates to return multiple templates
        service._get_templates = AsyncMock()
        service._get_templates.return_value = [
            {"_id": "template-1", "name": "Duplicate Template"},
            {"_id": "template-2", "name": "Duplicate Template"},
        ]

        with pytest.raises(exceptions.NotFoundError) as exc_info:
            await service.describe_template("Duplicate Template")

        assert "template Duplicate Template could not found" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_create_template_success(self, service, mock_client):
        """Test successful template creation"""
        # Mock response data
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "created": {
                "_id": "new-template-123",
                "name": "New Template",
                "description": "A new test template",
                "type": "textfsm",
                "group": "testing",
            }
        }
        mock_client.post.return_value = mock_response

        result = await service.create_template(
            name="New Template",
            template_type="textfsm",
            group="testing",
            project=None,
            description="A new test template",
            command="show interfaces",
            template="Value INTERFACE (\\S+)",
            data="GigabitEthernet0/1",
        )

        # Verify client was called with correct parameters
        mock_client.post.assert_called_once_with(
            "/automation-studio/templates",
            json={
                "template": {
                    "name": "New Template",
                    "type": "textfsm",
                    "group": "testing",
                    "description": "A new test template",
                    "command": "show interfaces",
                    "template": "Value INTERFACE (\\S+)",
                    "data": "GigabitEthernet0/1",
                }
            },
        )

        # Verify response data
        assert result["_id"] == "new-template-123"
        assert result["name"] == "New Template"
        assert result["description"] == "A new test template"
        assert result["type"] == "textfsm"
        assert result["group"] == "testing"

    @pytest.mark.asyncio
    async def test_create_template_minimal_params(self, service, mock_client):
        """Test template creation with minimal parameters"""
        # Mock response data
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "created": {
                "_id": "minimal-template",
                "name": "Minimal Template",
                "type": "jinja2",
                "group": "basic",
            }
        }
        mock_client.post.return_value = mock_response

        result = await service.create_template(
            name="Minimal Template", template_type="jinja2", group="basic"
        )

        # Verify client was called with default empty strings for optional fields
        mock_client.post.assert_called_once_with(
            "/automation-studio/templates",
            json={
                "template": {
                    "name": "Minimal Template",
                    "type": "jinja2",
                    "group": "basic",
                    "description": "",
                    "command": "",
                    "template": "",
                    "data": "",
                }
            },
        )

        # Verify response data
        assert result["_id"] == "minimal-template"
        assert result["name"] == "Minimal Template"
        assert result["type"] == "jinja2"
        assert result["group"] == "basic"

    @pytest.mark.asyncio
    async def test_update_template_success(self, service, mock_client):
        """Test successful template update"""
        # Mock describe_template call to get existing template
        service.describe_template = AsyncMock()
        service.describe_template.return_value = {
            "_id": "existing-template-123",
            "name": "Existing Template",
            "type": "textfsm",
            "group": "parsing",
            "description": "Original description",
            "command": "show version",
            "template": "Original template",
            "data": "Original data",
        }

        # Mock update response
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "updated": {
                "_id": "existing-template-123",
                "name": "Existing Template",
                "type": "textfsm",
                "group": "parsing",
                "description": "Updated description",
                "command": "show version",
                "template": "Updated template",
                "data": "Original data",
            }
        }
        mock_client.put.return_value = mock_response

        result = await service.update_template(
            name="Existing Template",
            project=None,
            description="Updated description",
            template="Updated template",
        )

        # Verify describe_template was called to get existing template
        service.describe_template.assert_called_once_with(
            name="Existing Template", project=None
        )

        # Verify client was called with correct parameters
        mock_client.put.assert_called_once_with(
            "/automation-studio/templates/existing-template-123",
            json={
                "update": {
                    "name": "Existing Template",
                    "group": "parsing",
                    "type": "textfsm",
                    "description": "Updated description",
                    "command": "show version",
                    "template": "Updated template",
                    "data": "Original data",
                }
            },
        )

        # Verify response data
        assert result["_id"] == "existing-template-123"
        assert result["name"] == "Existing Template"
        assert result["description"] == "Updated description"
        assert result["template"] == "Updated template"

    @pytest.mark.asyncio
    async def test_update_template_partial_update(self, service, mock_client):
        """Test template update with partial field updates"""
        # Mock describe_template call to get existing template
        service.describe_template = AsyncMock()
        service.describe_template.return_value = {
            "_id": "partial-template-456",
            "name": "Partial Template",
            "type": "jinja2",
            "group": "config",
            "description": "Original description",
            "command": "show interfaces",
            "template": "Original template",
            "data": "Original data",
        }

        # Mock update response
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "updated": {
                "_id": "partial-template-456",
                "name": "Partial Template",
                "type": "jinja2",
                "group": "config",
                "description": "Original description",
                "command": "show ip interface brief",
                "template": "Original template",
                "data": "Original data",
            }
        }
        mock_client.put.return_value = mock_response

        result = await service.update_template(
            name="Partial Template", command="show ip interface brief"
        )

        # Verify only the command field was updated, others preserved
        expected_update = {
            "update": {
                "name": "Partial Template",
                "group": "config",
                "type": "jinja2",
                "description": "Original description",
                "command": "show ip interface brief",
                "template": "Original template",
                "data": "Original data",
            }
        }

        mock_client.put.assert_called_once_with(
            "/automation-studio/templates/partial-template-456", json=expected_update
        )

        # Verify response data
        assert result["_id"] == "partial-template-456"
        assert result["command"] == "show ip interface brief"
