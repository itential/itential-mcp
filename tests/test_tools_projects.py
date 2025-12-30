# Copyright (c) 2025 Itential, Inc
# GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

import pytest
from unittest.mock import AsyncMock, MagicMock

from itential_mcp.tools.projects import get_projects, describe_project


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
        mock_client.automation_studio = MagicMock()
        mock_client.automation_studio.get_projects = AsyncMock()
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
                        "username": "joksan.flores@itential.com",
                    },
                    "created": "2025-08-18T15:47:52.956Z",
                    "lastUpdated": "2025-08-26T15:24:30.873Z",
                    "iid": 97,
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
                    "iid": 98,
                },
            ],
            "metadata": {
                "skip": 0,
                "limit": 100,
                "total": 29,
                "nextPageSkip": None,
                "previousPageSkip": None,
            },
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
                        "name": ": Application Provisioning",
                        "document": {
                            "name": "Application Provisioning",
                            "tasks": {},
                            "transitions": {},
                        },
                    }
                ],
            },
        }

    @pytest.mark.asyncio
    async def test_get_projects_success(
        self, mock_context, mock_client, mock_response, sample_projects_response
    ):
        """Test successful retrieval of projects."""
        mock_context.request_context.lifespan_context.get.return_value = mock_client
        # Service should return raw data, not response object
        mock_client.automation_studio.get_projects = AsyncMock(
            return_value=sample_projects_response["data"]
        )

        result = await get_projects(mock_context)

        assert len(result.root) == 2
        assert (
            result.root[0].name
            == "Application Infra Provisioning - Python + Infoblox + CMDB"
        )
        assert result.root[0].id == "68a34b28f7a1e4d40186b6aa"
        assert result.root[0].description == ""

        # Test second project
        assert result.root[1].id == "6824fa53eeefcae9174e2140"

        mock_client.automation_studio.get_projects.assert_called_once()
        mock_context.info.assert_called_once_with("inside get_projects(...)")

    @pytest.mark.asyncio
    async def test_get_projects_empty_response(
        self, mock_context, mock_client, mock_response
    ):
        """Test handling of empty projects response."""
        mock_context.request_context.lifespan_context.get.return_value = mock_client
        # Service should return raw data (empty list), not response object
        mock_client.automation_studio.get_projects = AsyncMock(return_value=[])

        result = await get_projects(mock_context)

        assert len(result.root) == 0

    @pytest.mark.asyncio
    async def test_describe_project_success(
        self, mock_context, mock_client, mock_response, sample_project_export_response
    ):
        """Test successful project description."""
        mock_context.request_context.lifespan_context.get.return_value = mock_client
        # Service should return raw data, not response object
        mock_client.automation_studio.describe_project = AsyncMock(
            return_value=sample_project_export_response["data"]
        )

        result = await describe_project(
            mock_context, "Application Infra Provisioning - Python + Infoblox + CMDB"
        )

        assert result.id == "68a34b28f7a1e4d40186b6aa"
        assert (
            result.name == "Application Infra Provisioning - Python + Infoblox + CMDB"
        )
        assert result.description == ""
        assert len(result.components) == 1
        assert result.components[0].type == "workflow"

        mock_client.automation_studio.describe_project.assert_called_once_with(
            name="Application Infra Provisioning - Python + Infoblox + CMDB"
        )
        mock_context.info.assert_called_once_with("inside describe_project(...)")

    @pytest.mark.asyncio
    async def test_describe_project_filters_data_correctly(
        self, mock_context, mock_client, mock_response
    ):
        """Test that describe_project filters data to only required fields."""
        mock_context.request_context.lifespan_context.get.return_value = mock_client
        # Service should return raw data, not response object
        mock_client.automation_studio.describe_project = AsyncMock(
            return_value={
                "_id": "test-id",
                "name": "Test Project",
                "description": "Test Description",
                "components": [
                    {
                        "name": ": workflow-name",
                        "type": "workflow",
                        "reference": "ref-123",
                        "folder": "/workflows",
                    }
                ],
                "extra_field": "should_not_be_included",
                "another_field": "also_not_included",
            }
        )

        result = await describe_project(mock_context, "Test Project")

        # Should only contain the specified fields in the model
        assert result.id == "test-id"
        assert result.name == "Test Project"
        assert result.description == "Test Description"
        assert len(result.components) == 1
        # Extra fields are filtered out by the model

    @pytest.mark.asyncio
    async def test_describe_project_handles_missing_data(
        self, mock_context, mock_client, mock_response
    ):
        """Test handling of missing data in project export response."""
        mock_context.request_context.lifespan_context.get.return_value = mock_client
        # Service should return raw data with minimal required fields
        mock_client.automation_studio.describe_project = AsyncMock(
            return_value={
                "_id": "minimal-project-id",
                "name": "Minimal Project",
                "components": [],
            }
        )

        result = await describe_project(mock_context, "Missing Project")

        assert result.id == "minimal-project-id"
        assert result.name == "Minimal Project"
        assert result.description is None
        assert result.components == []

    @pytest.mark.asyncio
    async def test_get_projects_handles_incomplete_creator_data(
        self, mock_context, mock_client, mock_response
    ):
        """Test handling of projects with incomplete creator information."""
        mock_context.request_context.lifespan_context.get.return_value = mock_client
        # Service should return raw data, not response object
        mock_client.automation_studio.get_projects = AsyncMock(
            return_value=[
                {
                    "_id": "test-id-1",
                    "name": "Project with Complete Creator",
                    "description": "Test project",
                },
                {
                    "_id": "test-id-2",
                    "name": "Project with Incomplete Creator",
                    "description": "Test project",
                },
            ]
        )

        result = await get_projects(mock_context)

        assert len(result.root) == 2

        # Test simplified project data structure
        assert result.root[0].id == "test-id-1"
        assert result.root[0].name == "Project with Complete Creator"
        assert result.root[0].description == "Test project"

        assert result.root[1].id == "test-id-2"
        assert result.root[1].name == "Project with Incomplete Creator"
        assert result.root[1].description == "Test project"
