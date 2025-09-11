# Copyright (c) 2025 Itential, Inc
# GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)

import pytest
from unittest.mock import AsyncMock, MagicMock

from itential_mcp.tools.automation_studio_projects import get_projects, describe_project


class TestAutomationStudioProjects:
    """Test cases for the automation_studio_projects tool functions"""

    @pytest.fixture
    def mock_context(self):
        """Create a mock FastMCP context."""
        mock_ctx = MagicMock()
        mock_ctx.info = AsyncMock()
        mock_ctx.request_context.lifespan_context.get.return_value = MagicMock()
        return mock_ctx

    @pytest.fixture
    def mock_client(self):
        """Create a mock platform client."""
        mock_client = MagicMock()
        mock_client.get = AsyncMock()
        return mock_client

    @pytest.fixture
    def mock_response(self):
        """Create a mock response object."""
        mock_resp = MagicMock()
        mock_resp.json = MagicMock()
        return mock_resp

    @pytest.fixture
    def sample_projects_response(self):
        """Sample projects API response."""
        return {
            "message": "Successfully retrieved projects",
            "data": [
                {
                    "_id": "68a34b28f7a1e4d40186b6aa",
                    "name": "Application Infra Provisioning - Python + Infoblox + CMDB",
                    "description": "",
                    "createdBy": {
                        "_id": "67c856baabe686cf9cb78b2d",
                        "provenance": "Okta SAML",
                        "username": "joksan.flores@itential.com"
                    },
                    "created": "2025-08-18T15:47:52.956Z",
                    "lastUpdated": "2025-08-26T15:24:30.873Z",
                    "iid": 97
                },
                {
                    "_id": "6824fa53eeefcae9174e2140",
                    "name": "Test Project with Incomplete Creator",
                    "description": "Test project",
                    "createdBy": {
                        "_id": "6824fa53eeefcae9174e2140"
                        # Missing provenance and username
                    },
                    "created": "2025-01-01T00:00:00.000Z",
                    "lastUpdated": "2025-01-01T00:00:00.000Z",
                    "iid": 98
                }
            ],
            "metadata": {
                "skip": 0,
                "limit": 100,
                "total": 29,
                "nextPageSkip": None,
                "previousPageSkip": None
            }
        }

    @pytest.fixture
    def sample_project_export_response(self):
        """Sample project export API response."""
        return {
            "message": "Successfully exported project",
            "data": {
                "_id": "68a34b28f7a1e4d40186b6aa",
                "name": "Application Infra Provisioning - Python + Infoblox + CMDB",
                "description": "",
                "components": [
                    {
                        "iid": 0,
                        "type": "workflow",
                        "folder": "/Workflows",
                        "reference": "aacb2f48-061a-4798-bb58-fa7735c7b9f4",
                        "document": {
                            "name": "Application Provisioning",
                            "tasks": {},
                            "transitions": {}
                        }
                    }
                ]
            }
        }

    @pytest.mark.asyncio
    async def test_get_projects_success(self, mock_context, mock_client, mock_response, sample_projects_response):
        """Test successful retrieval of projects."""
        mock_context.request_context.lifespan_context.get.return_value = mock_client
        mock_client.get.return_value = mock_response
        mock_response.json.return_value = sample_projects_response

        result = await get_projects(mock_context)

        assert result.message == "Successfully retrieved projects"
        assert len(result.data) == 2
        assert result.data[0].name == "Application Infra Provisioning - Python + Infoblox + CMDB"
        assert result.data[0].iid == 97
        assert result.data[0].id == "68a34b28f7a1e4d40186b6aa"
        assert result.data[0].createdBy.provenance == "Okta SAML"
        assert result.data[0].createdBy.username == "joksan.flores@itential.com"
        
        # Test project with incomplete creator data
        assert result.data[1].iid == 98
        assert result.data[1].id == "6824fa53eeefcae9174e2140"
        assert result.data[1].createdBy.provenance is None
        assert result.data[1].createdBy.username is None
        
        assert result.metadata.total == 29

        mock_client.get.assert_called_once_with("/automation-studio/projects")
        mock_context.info.assert_called_once_with("inside get_projects(...)")

    @pytest.mark.asyncio
    async def test_get_projects_empty_response(self, mock_context, mock_client, mock_response):
        """Test handling of empty projects response."""
        mock_context.request_context.lifespan_context.get.return_value = mock_client
        mock_client.get.return_value = mock_response
        mock_response.json.return_value = {
            "message": "No projects found",
            "data": [],
            "metadata": {"skip": 0, "limit": 100, "total": 0, "nextPageSkip": None, "previousPageSkip": None}
        }

        result = await get_projects(mock_context)

        assert result.message == "No projects found"
        assert len(result.data) == 0
        assert result.metadata.total == 0

    @pytest.mark.asyncio
    async def test_describe_project_success(self, mock_context, mock_client, mock_response, sample_project_export_response):
        """Test successful project description."""
        mock_context.request_context.lifespan_context.get.return_value = mock_client
        mock_client.get.return_value = mock_response
        mock_response.json.return_value = sample_project_export_response

        result = await describe_project(mock_context, 97)

        assert result.message == "Successfully exported project"
        assert result.data["id"] == "68a34b28f7a1e4d40186b6aa"
        assert result.data["name"] == "Application Infra Provisioning - Python + Infoblox + CMDB"
        assert result.data["description"] == ""
        assert len(result.data["components"]) == 1
        assert result.data["components"][0]["type"] == "workflow"

        mock_client.get.assert_called_once_with("/automation-studio/projects/97/export")
        mock_context.info.assert_called_once_with("inside describe_project(...) for project_id: 97")

    @pytest.mark.asyncio
    async def test_describe_project_filters_data_correctly(self, mock_context, mock_client, mock_response):
        """Test that describe_project filters data to only required fields."""
        mock_context.request_context.lifespan_context.get.return_value = mock_client
        mock_client.get.return_value = mock_response
        mock_response.json.return_value = {
            "message": "Successfully exported project",
            "data": {
                "_id": "test-id",
                "name": "Test Project",
                "description": "Test Description",
                "components": [{"type": "workflow"}],
                "extra_field": "should_not_be_included",
                "another_field": "also_not_included"
            }
        }

        result = await describe_project(mock_context, 123)

        # Should only contain the specified fields
        assert set(result.data.keys()) == {"id", "name", "description", "components"}
        assert "extra_field" not in result.data
        assert "another_field" not in result.data

    @pytest.mark.asyncio
    async def test_describe_project_handles_missing_data(self, mock_context, mock_client, mock_response):
        """Test handling of missing data in project export response."""
        mock_context.request_context.lifespan_context.get.return_value = mock_client
        mock_client.get.return_value = mock_response
        mock_response.json.return_value = {
            "message": "Successfully exported project",
            "data": {}
        }

        result = await describe_project(mock_context, 456)

        assert result.message == "Successfully exported project"
        assert result.data["id"] is None
        assert result.data["name"] is None
        assert result.data["description"] is None
        assert result.data["components"] == []

    @pytest.mark.asyncio
    async def test_get_projects_handles_incomplete_creator_data(self, mock_context, mock_client, mock_response):
        """Test handling of projects with incomplete creator information."""
        mock_context.request_context.lifespan_context.get.return_value = mock_client
        mock_client.get.return_value = mock_response
        mock_response.json.return_value = {
            "message": "Successfully retrieved projects",
            "data": [
                {
                    "_id": "test-id-1",
                    "name": "Project with Complete Creator",
                    "description": "Test project",
                    "createdBy": {
                        "_id": "creator-1",
                        "provenance": "Okta SAML",
                        "username": "user1@example.com"
                    },
                    "created": "2025-01-01T00:00:00.000Z",
                    "lastUpdated": "2025-01-01T00:00:00.000Z",
                    "iid": 1
                },
                {
                    "_id": "test-id-2",
                    "name": "Project with Incomplete Creator",
                    "description": "Test project",
                    "createdBy": {
                        "_id": "creator-2"
                        # Missing provenance and username
                    },
                    "created": "2025-01-01T00:00:00.000Z",
                    "lastUpdated": "2025-01-01T00:00:00.000Z",
                    "iid": 2
                }
            ],
            "metadata": {
                "skip": 0,
                "limit": 100,
                "total": 2,
                "nextPageSkip": None,
                "previousPageSkip": None
            }
        }

        result = await get_projects(mock_context)

        assert result.message == "Successfully retrieved projects"
        assert len(result.data) == 2
        
        # First project has complete creator data
        assert result.data[0].createdBy.provenance == "Okta SAML"
        assert result.data[0].createdBy.username == "user1@example.com"
        
        # Second project has incomplete creator data
        assert result.data[1].createdBy.provenance is None
        assert result.data[1].createdBy.username is None
        assert result.data[1].createdBy.id == "creator-2"
