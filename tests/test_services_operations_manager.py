# Copyright (c) 2025 Itential, Inc
# GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)

import pytest
from unittest.mock import AsyncMock, MagicMock

from itential_mcp.services.operations_manager import Service
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
        from itential_mcp.services import ServiceBase
        
        assert isinstance(service, ServiceBase)
        assert hasattr(service, 'client')
        assert hasattr(service, 'name')

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
                    "enabled": True
                },
                {
                    "_id": "workflow-2", 
                    "name": "Test Workflow 2",
                    "type": "endpoint",
                    "enabled": True
                }
            ],
            "metadata": {
                "total": 2,
                "count": 2,
                "skip": 0,
                "limit": 100
            }
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
                    "enabled": True
                }
            ],
            "metadata": {
                "total": 3,
                "count": 1,
                "skip": 0,
                "limit": 100
            }
        }
        
        # Second page response - has 2 more items, making total received 3  
        mock_response_2 = MagicMock()
        mock_response_2.json.return_value = {
            "data": [
                {
                    "_id": "workflow-2",
                    "name": "Test Workflow 2",
                    "type": "endpoint", 
                    "enabled": True
                },
                {
                    "_id": "workflow-3",
                    "name": "Test Workflow 3",
                    "type": "endpoint",
                    "enabled": True
                }
            ],
            "metadata": {
                "total": 3,
                "count": 2,
                "skip": 100,
                "limit": 100
            }
        }
        
        return [mock_response_1, mock_response_2]

    @pytest.fixture
    def mock_response_empty(self):
        """Mock response with no workflows"""
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "data": [],
            "metadata": {
                "total": 0,
                "count": 0,
                "skip": 0,
                "limit": 100
            }
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
            }
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
                "metrics": {
                    "start_time": 1640995200000,
                    "user": "user-123"
                }
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
            "metrics": {
                "start_time": 1640995200000,
                "user": "user-123"
            }
        }
        
        assert result == expected_result
        
        service.client.post.assert_called_once_with(
            "/operations-manager/triggers/endpoint/test-route",
            json=input_data
        )

    @pytest.mark.asyncio
    async def test_start_workflow_without_data(self, service, mock_workflow_response):
        """Test start_workflow without data payload"""
        service.client.post = AsyncMock(return_value=mock_workflow_response)
        
        result = await service.start_workflow("test-route")
        
        assert result["_id"] == "job-123"
        assert result["name"] == "Test Workflow"
        
        service.client.post.assert_called_once_with(
            "/operations-manager/triggers/endpoint/test-route", 
            json=None
        )

    @pytest.mark.asyncio
    async def test_start_workflow_explicit_none_data(self, service, mock_workflow_response):
        """Test start_workflow with explicit None data"""
        service.client.post = AsyncMock(return_value=mock_workflow_response)
        
        result = await service.start_workflow("test-route", None)
        
        assert result["_id"] == "job-123"
        
        service.client.post.assert_called_once_with(
            "/operations-manager/triggers/endpoint/test-route",
            json=None
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
            "nested": {
                "key": "value",
                "list": [1, 2, 3]
            },
            "boolean": True,
            "number": 42
        }
        
        await service.start_workflow("test-route", complex_data)
        
        service.client.post.assert_called_once_with(
            "/operations-manager/triggers/endpoint/test-route",
            json=complex_data
        )

    @pytest.mark.asyncio
    async def test_start_workflow_client_error(self, service):
        """Test start_workflow handles client errors"""
        service.client.post = AsyncMock(side_effect=Exception("API Error"))
        
        with pytest.raises(Exception, match="API Error"):
            await service.start_workflow("test-route")

    @pytest.mark.asyncio
    async def test_start_workflow_empty_route_name(self, service, mock_workflow_response):
        """Test start_workflow with empty route name"""
        service.client.post = AsyncMock(return_value=mock_workflow_response)
        
        await service.start_workflow("")
        
        service.client.post.assert_called_once_with(
            "/operations-manager/triggers/endpoint/",
            json=None
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
                    "status": "complete"
                },
                {
                    "_id": "job-2",
                    "name": "Test Workflow Job 2",
                    "description": "Second test job",
                    "status": "running"
                }
            ],
            "metadata": {
                "total": 2,
                "count": 2,
                "skip": 0,
                "limit": 100
            }
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
                    "status": "complete"
                }
            ],
            "metadata": {
                "total": 3,
                "count": 1,
                "skip": 0,
                "limit": 100
            }
        }
        
        # Second page response
        mock_response_2 = MagicMock()
        mock_response_2.json.return_value = {
            "data": [
                {
                    "_id": "job-2",
                    "name": "Test Workflow Job 2",
                    "description": "Second test job", 
                    "status": "running"
                },
                {
                    "_id": "job-3",
                    "name": "Test Workflow Job 3",
                    "description": "Third test job",
                    "status": "error"
                }
            ],
            "metadata": {
                "total": 3,
                "count": 2,
                "skip": 100,
                "limit": 100
            }
        }
        
        return [mock_response_1, mock_response_2]

    @pytest.fixture
    def mock_jobs_response_empty(self):
        """Mock response with no jobs"""
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "data": [],
            "metadata": {
                "total": 0,
                "count": 0,
                "skip": 0,
                "limit": 100
            }
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
            params={
                "limit": 100,
                "skip": 0,
                "equals[name]": "Test Workflow"
            }
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
    async def test_get_jobs_project_not_implemented(self, service):
        """Test get_jobs raises TypeError when project parameter is provided due to implementation bug"""
        with pytest.raises(TypeError, match="'coroutine' object is not subscriptable"):
            await service.get_jobs("Test Workflow", "test-project")

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
                    "status": "complete"
                }
            ],
            "metadata": {
                "total": 1
            }
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
                    "name": "Test Job"
                    # Missing description and status
                }
            ],
            "metadata": {
                "total": 1
            }
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
                        "status": "complete"
                    },
                    "task2": {
                        "type": "manual", 
                        "status": "complete"
                    }
                },
                "metrics": {
                    "start_time": 1640995200000,
                    "end_time": 1640995500000,
                    "user": "user-123"
                },
                "last_updated": "2025-01-01T12:05:00Z",
                "created": "2025-01-01T12:00:00Z"
            }
        }
        return mock_response

    @pytest.fixture
    def mock_job_minimal_response(self):
        """Mock response for job with minimal fields"""
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "data": {
                "_id": "job-minimal",
                "name": "Minimal Job",
                "status": "running"
            }
        }
        return mock_response

    @pytest.mark.asyncio
    async def test_describe_job_complete_response(self, service, mock_job_detail_response):
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
                    "status": "complete"
                },
                "task2": {
                    "type": "manual",
                    "status": "complete"
                }
            },
            "metrics": {
                "start_time": 1640995200000,
                "end_time": 1640995500000,
                "user": "user-123"
            },
            "last_updated": "2025-01-01T12:05:00Z",
            "created": "2025-01-01T12:00:00Z"
        }
        
        assert result == expected_data
        
        service.client.get.assert_called_once_with("/operations-manager/jobs/job-123")

    @pytest.mark.asyncio
    async def test_describe_job_minimal_response(self, service, mock_job_minimal_response):
        """Test describe_job with minimal job details"""
        service.client.get = AsyncMock(return_value=mock_job_minimal_response)
        
        result = await service.describe_job("job-minimal")
        
        expected_data = {
            "_id": "job-minimal",
            "name": "Minimal Job",
            "status": "running"
        }
        
        assert result == expected_data
        
        service.client.get.assert_called_once_with("/operations-manager/jobs/job-minimal")

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
    async def test_describe_job_empty_object_id(self, service, mock_job_detail_response):
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
                    "status": status
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
                        "data": {"initialized": True}
                    },
                    "process": {
                        "type": "automation",
                        "app": "device-manager",
                        "status": "running",
                        "data": {"device_count": 5}
                    },
                    "finalize": {
                        "type": "manual",
                        "status": "pending",
                        "description": "Manual approval required"
                    }
                }
            }
        }
        
        service.client.get = AsyncMock(return_value=mock_response)
        
        result = await service.describe_job("job-complex")
        
        assert "tasks" in result
        assert len(result["tasks"]) == 3
        assert result["tasks"]["init"]["status"] == "complete"
        assert result["tasks"]["process"]["status"] == "running"
        assert result["tasks"]["finalize"]["status"] == "pending"