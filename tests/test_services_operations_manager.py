# Copyright (c) 2025 Itential, Inc
# GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

import pytest
from unittest.mock import AsyncMock, MagicMock

from itential_mcp.platform.services.operations_manager import Service
from itential_mcp.core import exceptions
from ipsdk.platform import AsyncPlatform


class TestService:
    """Test the operations_manager Service class"""

    @pytest.fixture
    def mock_client(self):
        """Create a mock AsyncPlatform client"""
        return AsyncMock(spec=AsyncPlatform)

    @pytest.fixture
    def service(self, mock_client):
        """Create a Service instance with mock client"""
        return Service(mock_client)

    def test_service_initialization(self, mock_client):
        """Test Service initialization"""
        service = Service(mock_client)

        assert service.client == mock_client
        assert service.name == "operations_manager"

    def test_service_inheritance(self, service):
        """Test Service inherits from ServiceBase"""
        from itential_mcp.platform.services import ServiceBase

        assert isinstance(service, ServiceBase)
        assert hasattr(service, "client")
        assert hasattr(service, "name")

    def test_service_name_attribute(self, service):
        """Test Service has correct name attribute"""
        assert service.name == "operations_manager"


class TestGetWorkflows:
    """Test the get_workflows method"""

    @pytest.fixture
    def mock_client(self):
        """Create a mock AsyncPlatform client"""
        return AsyncMock(spec=AsyncPlatform)

    @pytest.fixture
    def service(self, mock_client):
        """Create a Service instance with mock client"""
        return Service(mock_client)

    @pytest.fixture
    def mock_response_single_page(self):
        """Mock response with workflows that fit in a single page"""
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "data": [
                {
                    "_id": "workflow-1",
                    "name": "Test Workflow 1",
                    "type": "endpoint",
                    "enabled": True,
                },
                {
                    "_id": "workflow-2",
                    "name": "Test Workflow 2",
                    "type": "endpoint",
                    "enabled": True,
                },
            ],
            "metadata": {"total": 2, "count": 2, "skip": 0, "limit": 100},
        }
        return mock_response

    @pytest.fixture
    def mock_response_multi_page(self):
        """Mock responses for multi-page workflow results"""
        # First page response - has 1 item but total is 3, so another page needed
        mock_response_1 = MagicMock()
        mock_response_1.json.return_value = {
            "data": [
                {
                    "_id": "workflow-1",
                    "name": "Test Workflow 1",
                    "type": "endpoint",
                    "enabled": True,
                }
            ],
            "metadata": {"total": 3, "count": 1, "skip": 0, "limit": 100},
        }

        # Second page response - has 2 more items, making total received 3
        mock_response_2 = MagicMock()
        mock_response_2.json.return_value = {
            "data": [
                {
                    "_id": "workflow-2",
                    "name": "Test Workflow 2",
                    "type": "endpoint",
                    "enabled": True,
                },
                {
                    "_id": "workflow-3",
                    "name": "Test Workflow 3",
                    "type": "endpoint",
                    "enabled": True,
                },
            ],
            "metadata": {"total": 3, "count": 2, "skip": 100, "limit": 100},
        }

        return [mock_response_1, mock_response_2]

    @pytest.fixture
    def mock_response_empty(self):
        """Mock response with no workflows"""
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "data": [],
            "metadata": {"total": 0, "count": 0, "skip": 0, "limit": 100},
        }
        return mock_response

    @pytest.mark.asyncio
    async def test_get_workflows_single_page(self, service, mock_response_single_page):
        """Test get_workflows with single page of results"""
        service.client.get = AsyncMock(return_value=mock_response_single_page)

        result = await service.get_workflows()

        assert len(result) == 2
        assert result[0]["_id"] == "workflow-1"
        assert result[0]["name"] == "Test Workflow 1"
        assert result[1]["_id"] == "workflow-2"
        assert result[1]["name"] == "Test Workflow 2"

        # Verify client.get was called with correct parameters
        service.client.get.assert_called_once_with(
            "/operations-manager/triggers",
            params={
                "limit": 100,
                "skip": 0,
                "equalsField": "type",
                "equals": "endpoint",
                "enabled": True,
            },
        )

    @pytest.mark.asyncio
    async def test_get_workflows_multi_page(self, service, mock_response_multi_page):
        """Test get_workflows with multiple pages of results"""
        service.client.get = AsyncMock(side_effect=mock_response_multi_page)

        result = await service.get_workflows()

        assert len(result) == 3
        assert result[0]["_id"] == "workflow-1"
        assert result[1]["_id"] == "workflow-2"
        assert result[2]["_id"] == "workflow-3"

        # Verify client.get was called twice for pagination
        assert service.client.get.call_count == 2

        # Check first call parameters
        first_call = service.client.get.call_args_list[0]
        assert first_call[0] == ("/operations-manager/triggers",)
        assert first_call[1]["params"]["skip"] == 0

        # Check second call parameters
        second_call = service.client.get.call_args_list[1]
        assert second_call[0] == ("/operations-manager/triggers",)
        assert second_call[1]["params"]["skip"] == 100

    @pytest.mark.asyncio
    async def test_get_workflows_empty_result(self, service, mock_response_empty):
        """Test get_workflows with empty result"""
        service.client.get = AsyncMock(return_value=mock_response_empty)

        result = await service.get_workflows()

        assert len(result) == 0
        assert result == []

        service.client.get.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_workflows_parameters(self, service, mock_response_single_page):
        """Test get_workflows uses correct API parameters"""
        service.client.get = AsyncMock(return_value=mock_response_single_page)

        await service.get_workflows()

        call_args = service.client.get.call_args
        params = call_args[1]["params"]

        assert params["limit"] == 100
        assert params["skip"] == 0
        assert params["equalsField"] == "type"
        assert params["equals"] == "endpoint"
        assert params["enabled"] is True

    @pytest.mark.asyncio
    async def test_get_workflows_client_error(self, service):
        """Test get_workflows handles client errors"""
        service.client.get = AsyncMock(side_effect=Exception("API Error"))

        with pytest.raises(Exception, match="API Error"):
            await service.get_workflows()


class TestStartWorkflow:
    """Test the start_workflow method"""

    @pytest.fixture
    def mock_client(self):
        """Create a mock AsyncPlatform client"""
        return AsyncMock(spec=AsyncPlatform)

    @pytest.fixture
    def service(self, mock_client):
        """Create a Service instance with mock client"""
        return Service(mock_client)

    @pytest.fixture
    def mock_workflow_response(self):
        """Mock response for workflow execution"""
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "data": {
                "_id": "job-123",
                "name": "Test Workflow",
                "status": "running",
                "tasks": {"task1": {"type": "action"}},
                "metrics": {"start_time": 1640995200000, "user": "user-123"},
            }
        }
        return mock_response

    @pytest.mark.asyncio
    async def test_start_workflow_with_data(self, service, mock_workflow_response):
        """Test start_workflow with data payload"""
        service.client.post = AsyncMock(return_value=mock_workflow_response)

        input_data = {"parameter": "value"}
        result = await service.start_workflow("test-route", input_data)

        expected_result = {
            "_id": "job-123",
            "name": "Test Workflow",
            "status": "running",
            "tasks": {"task1": {"type": "action"}},
            "metrics": {"start_time": 1640995200000, "user": "user-123"},
        }

        assert result == expected_result

        service.client.post.assert_called_once_with(
            "/operations-manager/triggers/endpoint/test-route", json=input_data
        )

    @pytest.mark.asyncio
    async def test_start_workflow_without_data(self, service, mock_workflow_response):
        """Test start_workflow without data payload"""
        service.client.post = AsyncMock(return_value=mock_workflow_response)

        result = await service.start_workflow("test-route")

        assert result["_id"] == "job-123"
        assert result["name"] == "Test Workflow"

        service.client.post.assert_called_once_with(
            "/operations-manager/triggers/endpoint/test-route", json=None
        )

    @pytest.mark.asyncio
    async def test_start_workflow_explicit_none_data(
        self, service, mock_workflow_response
    ):
        """Test start_workflow with explicit None data"""
        service.client.post = AsyncMock(return_value=mock_workflow_response)

        result = await service.start_workflow("test-route", None)

        assert result["_id"] == "job-123"

        service.client.post.assert_called_once_with(
            "/operations-manager/triggers/endpoint/test-route", json=None
        )

    @pytest.mark.asyncio
    async def test_start_workflow_endpoint_path(self, service, mock_workflow_response):
        """Test start_workflow constructs correct endpoint path"""
        service.client.post = AsyncMock(return_value=mock_workflow_response)

        await service.start_workflow("my-custom-route")

        call_args = service.client.post.call_args
        endpoint_path = call_args[0][0]

        assert endpoint_path == "/operations-manager/triggers/endpoint/my-custom-route"

    @pytest.mark.asyncio
    async def test_start_workflow_complex_data(self, service, mock_workflow_response):
        """Test start_workflow with complex data structure"""
        service.client.post = AsyncMock(return_value=mock_workflow_response)

        complex_data = {
            "nested": {"key": "value", "list": [1, 2, 3]},
            "boolean": True,
            "number": 42,
        }

        await service.start_workflow("test-route", complex_data)

        service.client.post.assert_called_once_with(
            "/operations-manager/triggers/endpoint/test-route", json=complex_data
        )

    @pytest.mark.asyncio
    async def test_start_workflow_client_error(self, service):
        """Test start_workflow handles client errors"""
        service.client.post = AsyncMock(side_effect=Exception("API Error"))

        with pytest.raises(Exception, match="API Error"):
            await service.start_workflow("test-route")

    @pytest.mark.asyncio
    async def test_start_workflow_empty_route_name(
        self, service, mock_workflow_response
    ):
        """Test start_workflow with empty route name"""
        service.client.post = AsyncMock(return_value=mock_workflow_response)

        await service.start_workflow("")

        service.client.post.assert_called_once_with(
            "/operations-manager/triggers/endpoint/", json=None
        )


class TestGetJobs:
    """Test the get_jobs method"""

    @pytest.fixture
    def mock_client(self):
        """Create a mock AsyncPlatform client"""
        return AsyncMock(spec=AsyncPlatform)

    @pytest.fixture
    def service(self, mock_client):
        """Create a Service instance with mock client"""
        return Service(mock_client)

    @pytest.fixture
    def mock_jobs_response_single_page(self):
        """Mock response with jobs that fit in a single page"""
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "data": [
                {
                    "_id": "job-1",
                    "name": "Test Workflow Job 1",
                    "description": "First test job",
                    "status": "complete",
                },
                {
                    "_id": "job-2",
                    "name": "Test Workflow Job 2",
                    "description": "Second test job",
                    "status": "running",
                },
            ],
            "metadata": {"total": 2, "count": 2, "skip": 0, "limit": 100},
        }
        return mock_response

    @pytest.fixture
    def mock_jobs_response_multi_page(self):
        """Mock responses for multi-page job results"""
        # First page response
        mock_response_1 = MagicMock()
        mock_response_1.json.return_value = {
            "data": [
                {
                    "_id": "job-1",
                    "name": "Test Workflow Job 1",
                    "description": "First test job",
                    "status": "complete",
                }
            ],
            "metadata": {"total": 3, "count": 1, "skip": 0, "limit": 100},
        }

        # Second page response
        mock_response_2 = MagicMock()
        mock_response_2.json.return_value = {
            "data": [
                {
                    "_id": "job-2",
                    "name": "Test Workflow Job 2",
                    "description": "Second test job",
                    "status": "running",
                },
                {
                    "_id": "job-3",
                    "name": "Test Workflow Job 3",
                    "description": "Third test job",
                    "status": "error",
                },
            ],
            "metadata": {"total": 3, "count": 2, "skip": 100, "limit": 100},
        }

        return [mock_response_1, mock_response_2]

    @pytest.fixture
    def mock_jobs_response_empty(self):
        """Mock response with no jobs"""
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "data": [],
            "metadata": {"total": 0, "count": 0, "skip": 0, "limit": 100},
        }
        return mock_response

    @pytest.mark.asyncio
    async def test_get_jobs_single_page(self, service, mock_jobs_response_single_page):
        """Test get_jobs with single page of results"""
        service.client.get = AsyncMock(return_value=mock_jobs_response_single_page)

        result = await service.get_jobs("Test Workflow")

        assert len(result) == 2
        assert result[0]["_id"] == "job-1"
        assert result[0]["name"] == "Test Workflow Job 1"
        assert result[0]["description"] == "First test job"
        assert result[0]["status"] == "complete"
        assert result[1]["_id"] == "job-2"
        assert result[1]["name"] == "Test Workflow Job 2"
        assert result[1]["status"] == "running"

        # Verify client.get was called with correct parameters
        service.client.get.assert_called_once_with(
            "/operations-manager/jobs",
            params={"limit": 100, "skip": 0, "equals[name]": "Test Workflow"},
        )

    @pytest.mark.asyncio
    async def test_get_jobs_multi_page(self, service, mock_jobs_response_multi_page):
        """Test get_jobs with multiple pages of results"""
        service.client.get = AsyncMock(side_effect=mock_jobs_response_multi_page)

        result = await service.get_jobs("Test Workflow")

        assert len(result) == 3
        assert result[0]["_id"] == "job-1"
        assert result[1]["_id"] == "job-2"
        assert result[2]["_id"] == "job-3"
        assert result[2]["status"] == "error"

        # Verify client.get was called twice for pagination
        assert service.client.get.call_count == 2

        # Check that both calls were made to the correct endpoint
        # Note: params dictionary is reused, so skip values can't be reliably tested
        first_call = service.client.get.call_args_list[0]
        assert first_call[0] == ("/operations-manager/jobs",)
        assert "params" in first_call[1]
        assert first_call[1]["params"]["equals[name]"] == "Test Workflow"
        assert first_call[1]["params"]["limit"] == 100

        second_call = service.client.get.call_args_list[1]
        assert second_call[0] == ("/operations-manager/jobs",)
        assert "params" in second_call[1]
        assert second_call[1]["params"]["equals[name]"] == "Test Workflow"
        assert second_call[1]["params"]["limit"] == 100

    @pytest.mark.asyncio
    async def test_get_jobs_empty_result(self, service, mock_jobs_response_empty):
        """Test get_jobs with empty result"""
        service.client.get = AsyncMock(return_value=mock_jobs_response_empty)

        result = await service.get_jobs("Nonexistent Workflow")

        assert len(result) == 0
        assert result == []

        service.client.get.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_jobs_parameters(self, service, mock_jobs_response_single_page):
        """Test get_jobs uses correct API parameters"""
        service.client.get = AsyncMock(return_value=mock_jobs_response_single_page)

        await service.get_jobs("My Workflow")

        call_args = service.client.get.call_args
        params = call_args[1]["params"]

        assert params["limit"] == 100
        assert params["skip"] == 0
        assert params["equals[name]"] == "My Workflow"
        assert "starts-with[name]" not in params

    @pytest.mark.asyncio
    async def test_get_jobs_with_project_parameter(self, service):
        """Test get_jobs with project parameter (project filtering functionality)"""
        # Mock project lookup response
        mock_project_response = MagicMock()
        mock_project_response.json.return_value = {
            "metadata": {"total": 1},
            "data": [{"_id": "project-123", "name": "test-project"}],
        }

        # Mock jobs response
        mock_jobs_response = MagicMock()
        mock_jobs_response.json.return_value = {
            "data": [
                {
                    "_id": "job-1",
                    "name": "@project-123: Test Workflow",
                    "description": "Project workflow job",
                    "status": "complete",
                }
            ],
            "metadata": {"total": 1},
        }

        service.client.get = AsyncMock(
            side_effect=[mock_project_response, mock_jobs_response]
        )

        result = await service.get_jobs("Test Workflow", "test-project")

        assert len(result) == 1
        assert result[0]["_id"] == "job-1"
        assert result[0]["name"] == "@project-123: Test Workflow"

        # Verify both API calls were made
        assert service.client.get.call_count == 2

        # Check project lookup call
        first_call = service.client.get.call_args_list[0]
        assert first_call[0] == ("/automation-studio/projects",)
        assert first_call[1]["params"]["equals[name]"] == "Test Workflow"

        # Check jobs call with project filtering
        second_call = service.client.get.call_args_list[1]
        assert second_call[0] == ("/operations-manager/jobs",)
        assert second_call[1]["params"]["equals[name]"] == "@project-123: Test Workflow"

    @pytest.mark.asyncio
    async def test_get_jobs_project_not_found(self, service):
        """Test get_jobs raises NotFoundError when project is not found"""
        # Mock empty project response
        mock_project_response = MagicMock()
        mock_project_response.json.return_value = {"metadata": {"total": 0}, "data": []}

        service.client.get = AsyncMock(return_value=mock_project_response)

        with pytest.raises(
            exceptions.NotFoundError,
            match="project nonexistent-project could not be found",
        ):
            await service.get_jobs("Test Workflow", "nonexistent-project")

    @pytest.mark.asyncio
    async def test_get_jobs_with_project_no_workflow_name(self, service):
        """Test get_jobs with project parameter but no specific workflow name"""
        # Mock project lookup response
        mock_project_response = MagicMock()
        mock_project_response.json.return_value = {
            "metadata": {"total": 1},
            "data": [{"_id": "project-456", "name": "test-project"}],
        }

        # Mock jobs response
        mock_jobs_response = MagicMock()
        mock_jobs_response.json.return_value = {"data": [], "metadata": {"total": 0}}

        service.client.get = AsyncMock(
            side_effect=[mock_project_response, mock_jobs_response]
        )

        await service.get_jobs(None, "test-project")

        # Check jobs call uses starts-with filter for all project workflows
        second_call = service.client.get.call_args_list[1]
        assert second_call[1]["params"]["starts-with[name]"] == "@project-456"
        assert "equals[name]" not in second_call[1]["params"]

    @pytest.mark.asyncio
    async def test_get_jobs_client_error(self, service):
        """Test get_jobs handles client errors"""
        service.client.get = AsyncMock(side_effect=Exception("API Error"))

        with pytest.raises(Exception, match="API Error"):
            await service.get_jobs("Test Workflow")

    @pytest.mark.asyncio
    async def test_get_jobs_missing_metadata_fields(self, service):
        """Test get_jobs handles response with missing metadata fields"""
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "data": [
                {
                    "_id": "job-1",
                    "name": "Test Job",
                    "description": None,
                    "status": "complete",
                }
            ],
            "metadata": {"total": 1},
        }
        service.client.get = AsyncMock(return_value=mock_response)

        result = await service.get_jobs("Test Workflow")

        assert len(result) == 1
        assert result[0]["_id"] == "job-1"
        assert result[0]["description"] is None

    @pytest.mark.asyncio
    async def test_get_jobs_missing_data_fields(self, service):
        """Test get_jobs handles job data with missing fields"""
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "data": [
                {
                    "_id": "job-1",
                    "name": "Test Job",
                    # Missing description and status
                }
            ],
            "metadata": {"total": 1},
        }
        service.client.get = AsyncMock(return_value=mock_response)

        result = await service.get_jobs("Test Workflow")

        assert len(result) == 1
        assert result[0]["_id"] == "job-1"
        assert result[0]["name"] == "Test Job"
        assert result[0]["description"] is None
        assert result[0]["status"] is None


class TestDescribeJob:
    """Test the describe_job method"""

    @pytest.fixture
    def mock_client(self):
        """Create a mock AsyncPlatform client"""
        return AsyncMock(spec=AsyncPlatform)

    @pytest.fixture
    def service(self, mock_client):
        """Create a Service instance with mock client"""
        return Service(mock_client)

    @pytest.fixture
    def mock_job_detail_response(self):
        """Mock response for job detail"""
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "data": {
                "_id": "job-123",
                "name": "Test Workflow Execution",
                "description": "Detailed test job execution",
                "type": "automation",
                "status": "complete",
                "tasks": {
                    "task1": {
                        "type": "action",
                        "app": "operations-manager",
                        "status": "complete",
                    },
                    "task2": {"type": "manual", "status": "complete"},
                },
                "metrics": {
                    "start_time": 1640995200000,
                    "end_time": 1640995500000,
                    "user": "user-123",
                },
                "last_updated": "2025-01-01T12:05:00Z",
                "created": "2025-01-01T12:00:00Z",
            }
        }
        return mock_response

    @pytest.fixture
    def mock_job_minimal_response(self):
        """Mock response for job with minimal fields"""
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "data": {"_id": "job-minimal", "name": "Minimal Job", "status": "running"}
        }
        return mock_response

    @pytest.mark.asyncio
    async def test_describe_job_complete_response(
        self, service, mock_job_detail_response
    ):
        """Test describe_job with complete job details"""
        service.client.get = AsyncMock(return_value=mock_job_detail_response)

        result = await service.describe_job("job-123")

        expected_data = {
            "_id": "job-123",
            "name": "Test Workflow Execution",
            "description": "Detailed test job execution",
            "type": "automation",
            "status": "complete",
            "tasks": {
                "task1": {
                    "type": "action",
                    "app": "operations-manager",
                    "status": "complete",
                },
                "task2": {"type": "manual", "status": "complete"},
            },
            "metrics": {
                "start_time": 1640995200000,
                "end_time": 1640995500000,
                "user": "user-123",
            },
            "last_updated": "2025-01-01T12:05:00Z",
            "created": "2025-01-01T12:00:00Z",
        }

        assert result == expected_data

        service.client.get.assert_called_once_with("/operations-manager/jobs/job-123")

    @pytest.mark.asyncio
    async def test_describe_job_minimal_response(
        self, service, mock_job_minimal_response
    ):
        """Test describe_job with minimal job details"""
        service.client.get = AsyncMock(return_value=mock_job_minimal_response)

        result = await service.describe_job("job-minimal")

        expected_data = {
            "_id": "job-minimal",
            "name": "Minimal Job",
            "status": "running",
        }

        assert result == expected_data

        service.client.get.assert_called_once_with(
            "/operations-manager/jobs/job-minimal"
        )

    @pytest.mark.asyncio
    async def test_describe_job_endpoint_path(self, service, mock_job_detail_response):
        """Test describe_job constructs correct endpoint path"""
        service.client.get = AsyncMock(return_value=mock_job_detail_response)

        await service.describe_job("custom-job-id-123")

        call_args = service.client.get.call_args
        endpoint_path = call_args[0][0]

        assert endpoint_path == "/operations-manager/jobs/custom-job-id-123"

    @pytest.mark.asyncio
    async def test_describe_job_client_error(self, service):
        """Test describe_job handles client errors"""
        service.client.get = AsyncMock(side_effect=Exception("Job not found"))

        with pytest.raises(Exception, match="Job not found"):
            await service.describe_job("nonexistent-job")

    @pytest.mark.asyncio
    async def test_describe_job_empty_object_id(
        self, service, mock_job_detail_response
    ):
        """Test describe_job with empty object ID"""
        service.client.get = AsyncMock(return_value=mock_job_detail_response)

        await service.describe_job("")

        service.client.get.assert_called_once_with("/operations-manager/jobs/")

    @pytest.mark.asyncio
    async def test_describe_job_different_statuses(self, service):
        """Test describe_job with jobs in different statuses"""
        statuses = ["running", "complete", "error", "paused", "canceled", "incomplete"]

        for status in statuses:
            mock_response = MagicMock()
            mock_response.json.return_value = {
                "data": {
                    "_id": f"job-{status}",
                    "name": f"Job {status.title()}",
                    "status": status,
                }
            }

            service.client.get = AsyncMock(return_value=mock_response)

            result = await service.describe_job(f"job-{status}")

            assert result["status"] == status
            assert result["_id"] == f"job-{status}"

    @pytest.mark.asyncio
    async def test_describe_job_complex_tasks(self, service):
        """Test describe_job with complex task structure"""
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "data": {
                "_id": "job-complex",
                "name": "Complex Workflow",
                "status": "running",
                "tasks": {
                    "init": {
                        "type": "automation",
                        "app": "operations-manager",
                        "status": "complete",
                        "data": {"initialized": True},
                    },
                    "process": {
                        "type": "automation",
                        "app": "device-manager",
                        "status": "running",
                        "data": {"device_count": 5},
                    },
                    "finalize": {
                        "type": "manual",
                        "status": "pending",
                        "description": "Manual approval required",
                    },
                },
            }
        }

        service.client.get = AsyncMock(return_value=mock_response)

        result = await service.describe_job("job-complex")

        assert "tasks" in result
        assert len(result["tasks"]) == 3
        assert result["tasks"]["init"]["status"] == "complete"
        assert result["tasks"]["process"]["status"] == "running"
        assert result["tasks"]["finalize"]["status"] == "pending"


class TestStartJob:
    """Test the start_job method"""

    @pytest.fixture
    def mock_client(self):
        """Create a mock AsyncPlatform client"""
        return AsyncMock(spec=AsyncPlatform)

    @pytest.fixture
    def service(self, mock_client):
        """Create a Service instance with mock client"""
        return Service(mock_client)

    @pytest.fixture
    def mock_start_job_response(self):
        """Mock response for start_job"""
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "_id": "job-789",
            "name": "Direct Job Execution",
            "description": "Job started directly via workflow name",
            "status": "running",
            "type": "automation",
            "workflow": "test-workflow",
            "variables": {"param1": "value1", "param2": "value2"},
            "created": "2025-01-01T12:00:00Z",
        }
        return mock_response

    @pytest.mark.asyncio
    async def test_start_job_success(self, service, mock_start_job_response):
        """Test start_job with complete parameters"""
        service.client.post = AsyncMock(return_value=mock_start_job_response)

        workflow_name = "test-workflow"
        description = "Test job description"
        variables = {"param1": "value1", "param2": "value2"}

        result = await service.start_job(workflow_name, description, variables)

        expected_result = {
            "_id": "job-789",
            "name": "Direct Job Execution",
            "description": "Job started directly via workflow name",
            "status": "running",
            "type": "automation",
            "workflow": "test-workflow",
            "variables": {"param1": "value1", "param2": "value2"},
            "created": "2025-01-01T12:00:00Z",
        }

        assert result == expected_result

        # Verify API call
        service.client.post.assert_called_once_with(
            "/operations_manager/jobs/start",
            json={
                "workflow": workflow_name,
                "options": {
                    "type": "automation",
                    "groups": [],
                    "description": description,
                    "variables": variables,
                },
            },
        )

    @pytest.mark.asyncio
    async def test_start_job_empty_description(self, service, mock_start_job_response):
        """Test start_job with empty description"""
        service.client.post = AsyncMock(return_value=mock_start_job_response)

        await service.start_job("test-workflow", "", {"key": "value"})

        call_args = service.client.post.call_args
        request_body = call_args[1]["json"]

        assert request_body["options"]["description"] == ""

    @pytest.mark.asyncio
    async def test_start_job_none_description(self, service, mock_start_job_response):
        """Test start_job with None description (should convert to empty string)"""
        service.client.post = AsyncMock(return_value=mock_start_job_response)

        await service.start_job("test-workflow", None, {"key": "value"})

        call_args = service.client.post.call_args
        request_body = call_args[1]["json"]

        assert request_body["options"]["description"] == ""

    @pytest.mark.asyncio
    async def test_start_job_empty_variables(self, service, mock_start_job_response):
        """Test start_job with empty variables dict"""
        service.client.post = AsyncMock(return_value=mock_start_job_response)

        await service.start_job("test-workflow", "description", {})

        call_args = service.client.post.call_args
        request_body = call_args[1]["json"]

        assert request_body["options"]["variables"] == {}

    @pytest.mark.asyncio
    async def test_start_job_none_variables(self, service, mock_start_job_response):
        """Test start_job with None variables (should convert to empty dict)"""
        service.client.post = AsyncMock(return_value=mock_start_job_response)

        await service.start_job("test-workflow", "description", None)

        call_args = service.client.post.call_args
        request_body = call_args[1]["json"]

        assert request_body["options"]["variables"] == {}

    @pytest.mark.asyncio
    async def test_start_job_complex_variables(self, service, mock_start_job_response):
        """Test start_job with complex variables structure"""
        service.client.post = AsyncMock(return_value=mock_start_job_response)

        complex_variables = {
            "nested": {"key": "value", "list": [1, 2, 3]},
            "boolean": True,
            "number": 42,
            "string": "test",
        }

        await service.start_job("complex-workflow", "Complex test", complex_variables)

        call_args = service.client.post.call_args
        request_body = call_args[1]["json"]

        assert request_body["workflow"] == "complex-workflow"
        assert request_body["options"]["variables"] == complex_variables
        assert request_body["options"]["type"] == "automation"
        assert request_body["options"]["groups"] == []

    @pytest.mark.asyncio
    async def test_start_job_endpoint_path(self, service, mock_start_job_response):
        """Test start_job uses correct API endpoint"""
        service.client.post = AsyncMock(return_value=mock_start_job_response)

        await service.start_job("test-workflow", "description", {})

        call_args = service.client.post.call_args
        endpoint_path = call_args[0][0]

        assert endpoint_path == "/operations_manager/jobs/start"

    @pytest.mark.asyncio
    async def test_start_job_request_structure(self, service, mock_start_job_response):
        """Test start_job creates correct request body structure"""
        service.client.post = AsyncMock(return_value=mock_start_job_response)

        workflow = "structure-test-workflow"
        description = "Structure test description"
        variables = {"test": "variable"}

        await service.start_job(workflow, description, variables)

        call_args = service.client.post.call_args
        request_body = call_args[1]["json"]

        # Verify top-level structure
        assert "workflow" in request_body
        assert "options" in request_body
        assert len(request_body) == 2

        # Verify options structure
        options = request_body["options"]
        assert "type" in options
        assert "groups" in options
        assert "description" in options
        assert "variables" in options
        assert len(options) == 4

        # Verify values
        assert request_body["workflow"] == workflow
        assert options["type"] == "automation"
        assert options["groups"] == []
        assert options["description"] == description
        assert options["variables"] == variables

    @pytest.mark.asyncio
    async def test_start_job_client_error(self, service):
        """Test start_job handles client errors"""
        service.client.post = AsyncMock(side_effect=Exception("Workflow not found"))

        with pytest.raises(Exception, match="Workflow not found"):
            await service.start_job("nonexistent-workflow", "description", {})

    @pytest.mark.asyncio
    async def test_start_job_minimal_response(self, service):
        """Test start_job with minimal API response"""
        mock_response = MagicMock()
        mock_response.json.return_value = {"_id": "job-minimal", "status": "queued"}
        service.client.post = AsyncMock(return_value=mock_response)

        result = await service.start_job("test-workflow", "description", {})

        expected_result = {"_id": "job-minimal", "status": "queued"}
        assert result == expected_result

    @pytest.mark.asyncio
    async def test_start_job_workflow_name_types(
        self, service, mock_start_job_response
    ):
        """Test start_job with different workflow name formats"""
        service.client.post = AsyncMock(return_value=mock_start_job_response)

        workflow_names = [
            "simple-workflow",
            "workflow_with_underscores",
            "workflow-with-dashes",
            "workflowCamelCase",
            "Workflow With Spaces",
            "123-numeric-workflow",
        ]

        for workflow_name in workflow_names:
            await service.start_job(workflow_name, "test", {})

            call_args = service.client.post.call_args
            request_body = call_args[1]["json"]
            assert request_body["workflow"] == workflow_name


class TestCreateAutomation:
    """Test the create_automation method"""

    @pytest.fixture
    def mock_client(self):
        """Create a mock AsyncPlatform client"""
        return AsyncMock(spec=AsyncPlatform)

    @pytest.fixture
    def service(self, mock_client):
        """Create a Service instance with mock client"""
        return Service(mock_client)

    @pytest.fixture
    def mock_automation_response(self):
        """Mock response for create_automation"""
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "data": {
                "_id": "automation-123",
                "name": "Test Automation",
                "componentType": "workflows",
                "componentId": "workflow-456",
                "description": "Test automation description",
            }
        }
        return mock_response

    @pytest.mark.asyncio
    async def test_create_automation_basic(self, service, mock_automation_response):
        """Test create_automation with basic parameters"""
        service.client.post = AsyncMock(return_value=mock_automation_response)

        result = await service.create_automation("Test Automation", "workflows")

        expected_result = {
            "_id": "automation-123",
            "name": "Test Automation",
            "componentType": "workflows",
            "componentId": "workflow-456",
            "description": "Test automation description",
        }

        assert result == expected_result

        # Verify API call
        service.client.post.assert_called_once_with(
            "/operations-manager/automations",
            json={"name": "Test Automation", "componentType": "workflows"},
        )

    @pytest.mark.asyncio
    async def test_create_automation_with_description(
        self, service, mock_automation_response
    ):
        """Test create_automation with description"""
        service.client.post = AsyncMock(return_value=mock_automation_response)

        await service.create_automation(
            "Test Automation", "workflows", description="Custom description"
        )

        call_args = service.client.post.call_args
        request_body = call_args[1]["json"]

        assert request_body["description"] == "Custom description"

    @pytest.mark.asyncio
    async def test_create_automation_with_workflow_component(
        self, service, mock_automation_response
    ):
        """Test create_automation with workflow component lookup"""
        # Mock workflow lookup response
        mock_workflow_response = MagicMock()
        mock_workflow_response.json.return_value = {
            "total": 1,
            "items": [{"_id": "workflow-789", "name": "Target Workflow"}],
        }

        service.client.get = AsyncMock(return_value=mock_workflow_response)
        service.client.post = AsyncMock(return_value=mock_automation_response)

        await service.create_automation(
            "Workflow Automation",
            "workflows",
            component_name="Target Workflow",
            description="Workflow automation",
        )

        # Verify workflow lookup
        service.client.get.assert_called_once_with(
            "/automation-studio/workflows", params={"equals[name]": "Target Workflow"}
        )

        # Verify automation creation with component ID
        call_args = service.client.post.call_args
        request_body = call_args[1]["json"]

        assert request_body["componentId"] == "workflow-789"

    @pytest.mark.asyncio
    async def test_create_automation_workflow_not_found(self, service):
        """Test create_automation raises NotFoundError when workflow not found"""
        # Mock empty workflow response
        mock_workflow_response = MagicMock()
        mock_workflow_response.json.return_value = {"total": 0, "items": []}

        service.client.get = AsyncMock(return_value=mock_workflow_response)

        with pytest.raises(
            exceptions.NotFoundError, match="workflow Nonexistent Workflow not found"
        ):
            await service.create_automation(
                "Test Automation", "workflows", component_name="Nonexistent Workflow"
            )

    @pytest.mark.asyncio
    async def test_create_automation_multiple_workflows_found(self, service):
        """Test create_automation raises NotFoundError when multiple workflows found"""
        # Mock multiple workflow response
        mock_workflow_response = MagicMock()
        mock_workflow_response.json.return_value = {
            "total": 2,
            "items": [
                {"_id": "workflow-1", "name": "Duplicate Workflow"},
                {"_id": "workflow-2", "name": "Duplicate Workflow"},
            ],
        }

        service.client.get = AsyncMock(return_value=mock_workflow_response)

        with pytest.raises(
            exceptions.NotFoundError, match="workflow Duplicate Workflow not found"
        ):
            await service.create_automation(
                "Test Automation", "workflows", component_name="Duplicate Workflow"
            )

    @pytest.mark.asyncio
    async def test_create_automation_ucm_compliance_plan(
        self, service, mock_automation_response
    ):
        """Test create_automation with UCM compliance plan component type"""
        service.client.post = AsyncMock(return_value=mock_automation_response)

        # UCM compliance plan doesn't have lookup logic implemented yet
        await service.create_automation(
            "Compliance Automation", "ucm_compliance_plan", component_name="Test Plan"
        )

        call_args = service.client.post.call_args
        request_body = call_args[1]["json"]

        # Should not include componentId for compliance plans (not implemented)
        assert "componentId" not in request_body
        assert request_body["componentType"] == "ucm_compliance_plan"

    @pytest.mark.asyncio
    async def test_create_automation_client_error(self, service):
        """Test create_automation handles client errors"""
        service.client.post = AsyncMock(side_effect=Exception("API Error"))

        with pytest.raises(Exception, match="API Error"):
            await service.create_automation("Test", "workflows")


class TestCreateManualTrigger:
    """Test the create_manual_trigger method"""

    @pytest.fixture
    def mock_client(self):
        """Create a mock AsyncPlatform client"""
        return AsyncMock(spec=AsyncPlatform)

    @pytest.fixture
    def service(self, mock_client):
        """Create a Service instance with mock client"""
        return Service(mock_client)

    @pytest.fixture
    def mock_trigger_response(self):
        """Mock response for create_manual_trigger"""
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "data": {
                "_id": "trigger-123",
                "name": "Manual Test Trigger",
                "type": "manual",
                "actionId": "automation-456",
                "actionType": "automations",
                "enabled": True,
                "description": "Test manual trigger",
            }
        }
        return mock_response

    @pytest.mark.asyncio
    async def test_create_manual_trigger_success(self, service, mock_trigger_response):
        """Test create_manual_trigger with basic parameters"""
        service.client.post = AsyncMock(return_value=mock_trigger_response)

        result = await service.create_manual_trigger(
            "Manual Test Trigger", "automation-456"
        )

        expected_result = {
            "_id": "trigger-123",
            "name": "Manual Test Trigger",
            "type": "manual",
            "actionId": "automation-456",
            "actionType": "automations",
            "enabled": True,
            "description": "Test manual trigger",
        }

        assert result == expected_result

        # Verify API call
        service.client.post.assert_called_once_with(
            "/operations-manager/triggers",
            json={
                "actionId": "automation-456",
                "actionType": "automations",
                "name": "Manual Test Trigger",
                "type": "manual",
                "description": None,
                "enabled": True,
            },
        )

    @pytest.mark.asyncio
    async def test_create_manual_trigger_with_description(
        self, service, mock_trigger_response
    ):
        """Test create_manual_trigger with description"""
        service.client.post = AsyncMock(return_value=mock_trigger_response)

        await service.create_manual_trigger(
            "Described Trigger",
            "automation-789",
            description="Custom trigger description",
        )

        call_args = service.client.post.call_args
        request_body = call_args[1]["json"]

        assert request_body["description"] == "Custom trigger description"
        assert request_body["actionId"] == "automation-789"

    @pytest.mark.asyncio
    async def test_create_manual_trigger_request_structure(
        self, service, mock_trigger_response
    ):
        """Test create_manual_trigger creates correct request structure"""
        service.client.post = AsyncMock(return_value=mock_trigger_response)

        await service.create_manual_trigger("Test Trigger", "automation-123")

        call_args = service.client.post.call_args
        request_body = call_args[1]["json"]

        # Verify all required fields
        assert request_body["actionId"] == "automation-123"
        assert request_body["actionType"] == "automations"
        assert request_body["name"] == "Test Trigger"
        assert request_body["type"] == "manual"
        assert request_body["enabled"] is True
        assert "description" in request_body

    @pytest.mark.asyncio
    async def test_create_manual_trigger_endpoint_path(
        self, service, mock_trigger_response
    ):
        """Test create_manual_trigger uses correct API endpoint"""
        service.client.post = AsyncMock(return_value=mock_trigger_response)

        await service.create_manual_trigger("Test", "automation-id")

        call_args = service.client.post.call_args
        endpoint_path = call_args[0][0]

        assert endpoint_path == "/operations-manager/triggers"

    @pytest.mark.asyncio
    async def test_create_manual_trigger_client_error(self, service):
        """Test create_manual_trigger handles client errors"""
        service.client.post = AsyncMock(side_effect=Exception("Automation not found"))

        with pytest.raises(Exception, match="Automation not found"):
            await service.create_manual_trigger("Test", "nonexistent-automation")


class TestCreateEndpointTrigger:
    """Test the create_endpoint_trigger method"""

    @pytest.fixture
    def mock_client(self):
        """Create a mock AsyncPlatform client"""
        return AsyncMock(spec=AsyncPlatform)

    @pytest.fixture
    def service(self, mock_client):
        """Create a Service instance with mock client"""
        return Service(mock_client)

    @pytest.fixture
    def mock_endpoint_trigger_response(self):
        """Mock response for create_endpoint_trigger"""
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "data": {
                "_id": "trigger-456",
                "name": "API Endpoint Trigger",
                "type": "endpoint",
                "verb": "POST",
                "routeName": "test-route",
                "actionId": "automation-789",
                "actionType": "automations",
                "enabled": True,
                "schema": {"type": "object", "properties": {}},
            }
        }
        return mock_response

    @pytest.mark.asyncio
    async def test_create_endpoint_trigger_basic(
        self, service, mock_endpoint_trigger_response
    ):
        """Test create_endpoint_trigger with basic parameters"""
        service.client.post = AsyncMock(return_value=mock_endpoint_trigger_response)

        result = await service.create_endpoint_trigger(
            "API Endpoint Trigger", "automation-789", "test-route"
        )

        expected_result = {
            "_id": "trigger-456",
            "name": "API Endpoint Trigger",
            "type": "endpoint",
            "verb": "POST",
            "routeName": "test-route",
            "actionId": "automation-789",
            "actionType": "automations",
            "enabled": True,
            "schema": {"type": "object", "properties": {}},
        }

        assert result == expected_result

        # Verify API call with default schema
        service.client.post.assert_called_once_with(
            "/operations-manager/triggers",
            json={
                "actionId": "automation-789",
                "actionType": "automations",
                "name": "API Endpoint Trigger",
                "type": "endpoint",
                "verb": "POST",
                "routeName": "test-route",
                "description": None,
                "enabled": True,
                "schema": {
                    "type": "object",
                    "properties": {},
                    "additionalProperties": True,
                },
            },
        )

    @pytest.mark.asyncio
    async def test_create_endpoint_trigger_with_custom_schema(
        self, service, mock_endpoint_trigger_response
    ):
        """Test create_endpoint_trigger with custom schema"""
        service.client.post = AsyncMock(return_value=mock_endpoint_trigger_response)

        custom_schema = {
            "type": "object",
            "properties": {"device": {"type": "string"}, "action": {"type": "string"}},
            "required": ["device"],
        }

        await service.create_endpoint_trigger(
            "Custom Schema Trigger",
            "automation-123",
            "custom-route",
            schema=custom_schema,
        )

        call_args = service.client.post.call_args
        request_body = call_args[1]["json"]

        assert request_body["schema"] == custom_schema

    @pytest.mark.asyncio
    async def test_create_endpoint_trigger_with_description(
        self, service, mock_endpoint_trigger_response
    ):
        """Test create_endpoint_trigger with description"""
        service.client.post = AsyncMock(return_value=mock_endpoint_trigger_response)

        await service.create_endpoint_trigger(
            "Described Trigger",
            "automation-456",
            "described-route",
            description="Custom endpoint description",
        )

        call_args = service.client.post.call_args
        request_body = call_args[1]["json"]

        assert request_body["description"] == "Custom endpoint description"

    @pytest.mark.asyncio
    async def test_create_endpoint_trigger_route_validation(self, service):
        """Test create_endpoint_trigger validates route name"""
        # Mock stringutils.is_valid_url_path to return False
        with pytest.raises(ValueError, match="route_name is invalid"):
            await service.create_endpoint_trigger(
                "Invalid Route Trigger",
                "automation-123",
                "invalid route with spaces",  # Invalid route name
            )

    @pytest.mark.asyncio
    async def test_create_endpoint_trigger_valid_route_names(
        self, service, mock_endpoint_trigger_response
    ):
        """Test create_endpoint_trigger with various valid route names"""
        service.client.post = AsyncMock(return_value=mock_endpoint_trigger_response)

        valid_routes = [
            "simple-route",
            "route_with_underscores",
            "route123",
            "route/with/slashes",
            "complex-route_123/with.dots",
        ]

        for route in valid_routes:
            await service.create_endpoint_trigger(
                f"Trigger for {route}", "automation-test", route
            )

            call_args = service.client.post.call_args
            request_body = call_args[1]["json"]
            assert request_body["routeName"] == route

    @pytest.mark.asyncio
    async def test_create_endpoint_trigger_request_structure(
        self, service, mock_endpoint_trigger_response
    ):
        """Test create_endpoint_trigger creates correct request structure"""
        service.client.post = AsyncMock(return_value=mock_endpoint_trigger_response)

        await service.create_endpoint_trigger(
            "Structure Test Trigger", "automation-structure", "structure-route"
        )

        call_args = service.client.post.call_args
        request_body = call_args[1]["json"]

        # Verify all required fields
        assert request_body["actionId"] == "automation-structure"
        assert request_body["actionType"] == "automations"
        assert request_body["name"] == "Structure Test Trigger"
        assert request_body["type"] == "endpoint"
        assert request_body["verb"] == "POST"
        assert request_body["routeName"] == "structure-route"
        assert request_body["enabled"] is True
        assert "schema" in request_body

    @pytest.mark.asyncio
    async def test_create_endpoint_trigger_default_schema_structure(
        self, service, mock_endpoint_trigger_response
    ):
        """Test create_endpoint_trigger default schema structure"""
        service.client.post = AsyncMock(return_value=mock_endpoint_trigger_response)

        await service.create_endpoint_trigger(
            "Default Schema Test", "automation-default", "default-route"
        )

        call_args = service.client.post.call_args
        request_body = call_args[1]["json"]

        expected_schema = {
            "type": "object",
            "properties": {},
            "additionalProperties": True,
        }

        assert request_body["schema"] == expected_schema

    @pytest.mark.asyncio
    async def test_create_endpoint_trigger_client_error(self, service):
        """Test create_endpoint_trigger handles client errors"""
        service.client.post = AsyncMock(side_effect=Exception("Route already exists"))

        with pytest.raises(Exception, match="Route already exists"):
            await service.create_endpoint_trigger(
                "Error Test", "automation-error", "error-route"
            )


class TestDeleteAutomation:
    """Test the delete_automation method"""

    @pytest.fixture
    def mock_client(self):
        """Create a mock AsyncPlatform client"""
        return AsyncMock(spec=AsyncPlatform)

    @pytest.fixture
    def service(self, mock_client):
        """Create a Service instance with mock client"""
        return Service(mock_client)

    @pytest.fixture
    def mock_delete_response(self):
        """Mock response for delete_automation"""
        mock_response = MagicMock()
        mock_response.json.return_value = {"message": "Automation successfully deleted"}
        return mock_response

    @pytest.mark.asyncio
    async def test_delete_automation_success(self, service, mock_delete_response):
        """Test delete_automation successful deletion"""
        service.client.delete = AsyncMock(return_value=mock_delete_response)

        result = await service.delete_automation("automation-123")

        expected_result = {"message": "Automation successfully deleted"}

        assert result == expected_result

        # Verify API call
        service.client.delete.assert_called_once_with(
            "/operations-manager/automations/automation-123"
        )

    @pytest.mark.asyncio
    async def test_delete_automation_endpoint_path(self, service, mock_delete_response):
        """Test delete_automation constructs correct endpoint path"""
        service.client.delete = AsyncMock(return_value=mock_delete_response)

        await service.delete_automation("automation-custom-id-456")

        call_args = service.client.delete.call_args
        endpoint_path = call_args[0][0]

        assert (
            endpoint_path == "/operations-manager/automations/automation-custom-id-456"
        )

    @pytest.mark.asyncio
    async def test_delete_automation_client_error(self, service):
        """Test delete_automation handles client errors"""
        service.client.delete = AsyncMock(side_effect=Exception("Automation not found"))

        with pytest.raises(Exception, match="Automation not found"):
            await service.delete_automation("nonexistent-automation")

    @pytest.mark.asyncio
    async def test_delete_automation_different_message_formats(self, service):
        """Test delete_automation handles different response message formats"""
        messages = [
            "Automation deleted successfully",
            "Successfully removed automation",
            "Automation removal completed",
        ]

        for message in messages:
            mock_response = MagicMock()
            mock_response.json.return_value = {"message": message}
            service.client.delete = AsyncMock(return_value=mock_response)

            result = await service.delete_automation(f"automation-{message[:5]}")

            assert result["message"] == message

    @pytest.mark.asyncio
    async def test_delete_automation_empty_id(self, service, mock_delete_response):
        """Test delete_automation with empty automation ID"""
        service.client.delete = AsyncMock(return_value=mock_delete_response)

        await service.delete_automation("")

        # Should still make the API call with empty ID
        service.client.delete.assert_called_once_with(
            "/operations-manager/automations/"
        )
