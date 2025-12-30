# Copyright (c) 2025 Itential, Inc
# GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

import pytest
from unittest.mock import AsyncMock, MagicMock

from itential_mcp.platform.services.workflow_engine import Service


class TestWorkflowEngineService:
    """Test cases for the Workflow Engine Service class."""

    def setup_method(self):
        """Set up test fixtures before each test method."""
        self.mock_client = AsyncMock()
        self.workflow_service = Service(self.mock_client)

    def test_service_name(self):
        """Test that the service has the correct name."""
        assert self.workflow_service.name == "workflow_engine"

    def test_service_initialization(self):
        """Test service initialization with client."""
        assert self.workflow_service.client == self.mock_client

    @pytest.mark.asyncio
    async def test_get_job_metrics_success(self):
        """Test get_job_metrics returns job metrics data successfully."""
        expected_data = [
            {
                "_id": "job-metric-1",
                "workflow": "Test Workflow 1",
                "metrics": {"avgRunTime": 5.5, "successRate": 0.95},
                "jobsComplete": 100,
                "totalRunTime": 550,
            },
            {
                "_id": "job-metric-2",
                "workflow": "Test Workflow 2",
                "metrics": {"avgRunTime": 10.2, "successRate": 0.88},
                "jobsComplete": 50,
                "totalRunTime": 510,
            },
        ]

        # Mock the _get_route method
        self.workflow_service._get_route = AsyncMock(return_value=expected_data)

        result = await self.workflow_service.get_job_metrics()

        self.workflow_service._get_route.assert_called_once_with(
            "/workflow_engine/jobs/metrics", params=None
        )
        assert result == expected_data

    @pytest.mark.asyncio
    async def test_get_job_metrics_with_params(self):
        """Test get_job_metrics with query parameters."""
        expected_data = [
            {
                "_id": "job-metric-filtered",
                "workflow": "Filtered Workflow",
                "metrics": {"avgRunTime": 3.2, "successRate": 1.0},
                "jobsComplete": 25,
                "totalRunTime": 80,
            }
        ]
        params = {"workflow": "Filtered Workflow"}

        # Mock the _get_route method
        self.workflow_service._get_route = AsyncMock(return_value=expected_data)

        result = await self.workflow_service.get_job_metrics(params=params)

        self.workflow_service._get_route.assert_called_once_with(
            "/workflow_engine/jobs/metrics", params=params
        )
        assert result == expected_data

    @pytest.mark.asyncio
    async def test_get_task_metrics_success(self):
        """Test get_task_metrics returns task metrics data successfully."""
        expected_data = [
            {
                "taskId": "task-1",
                "taskType": "automatic",
                "name": "Process Data",
                "metrics": {"avgExecutionTime": 2.1, "errorRate": 0.02},
                "app": "DataProcessor",
                "workflow": "Data Pipeline",
            },
            {
                "taskId": "task-2",
                "taskType": "manual",
                "name": "Review Results",
                "metrics": {"avgExecutionTime": 120.5, "errorRate": 0.0},
                "app": "ReviewApp",
                "workflow": "Review Pipeline",
            },
        ]

        # Mock the _get_route method
        self.workflow_service._get_route = AsyncMock(return_value=expected_data)

        result = await self.workflow_service.get_task_metrics()

        self.workflow_service._get_route.assert_called_once_with(
            "/workflow_engine/tasks/metrics", params=None
        )
        assert result == expected_data

    @pytest.mark.asyncio
    async def test_get_task_metrics_with_params(self):
        """Test get_task_metrics with query parameters."""
        expected_data = [
            {
                "taskId": "filtered-task",
                "taskType": "automatic",
                "name": "Filtered Task",
                "metrics": {"avgExecutionTime": 5.0, "errorRate": 0.01},
                "app": "FilteredApp",
                "workflow": "Filtered Workflow",
            }
        ]
        params = {"taskType": "automatic"}

        # Mock the _get_route method
        self.workflow_service._get_route = AsyncMock(return_value=expected_data)

        result = await self.workflow_service.get_task_metrics(params=params)

        self.workflow_service._get_route.assert_called_once_with(
            "/workflow_engine/tasks/metrics", params=params
        )
        assert result == expected_data

    @pytest.mark.asyncio
    async def test_get_route_single_page(self):
        """Test _get_route with single page of results."""
        expected_results = [
            {"id": "item1", "data": "test1"},
            {"id": "item2", "data": "test2"},
        ]

        mock_response_data = {"results": expected_results, "total": 2}

        mock_response = MagicMock()
        mock_response.json.return_value = mock_response_data
        self.mock_client.get.return_value = mock_response

        result = await self.workflow_service._get_route("/test/path")

        # Should make one call with limit=100, skip=0
        self.mock_client.get.assert_called_once_with(
            "/test/path", params={"limit": 100, "skip": 0}
        )
        assert result == expected_results

    @pytest.mark.asyncio
    async def test_get_route_multiple_pages(self):
        """Test _get_route with multiple pages of results."""
        page1_results = [{"id": f"item{i}", "data": f"test{i}"} for i in range(1, 101)]
        page2_results = [
            {"id": f"item{i}", "data": f"test{i}"} for i in range(101, 151)
        ]

        all_results = page1_results + page2_results

        # Track call count to return appropriate responses
        call_count = 0

        def mock_get_responses(*args, **kwargs):
            nonlocal call_count
            call_count += 1

            if call_count == 1:
                # First page
                return MagicMock(json=lambda: {"results": page1_results, "total": 150})
            elif call_count == 2:
                # Second page
                return MagicMock(json=lambda: {"results": page2_results, "total": 150})

        self.mock_client.get.side_effect = mock_get_responses

        result = await self.workflow_service._get_route("/test/path")

        # Should make two calls
        assert self.mock_client.get.call_count == 2

        # Check that calls were made with correct path
        first_call = self.mock_client.get.call_args_list[0]
        assert first_call[0] == ("/test/path",)

        second_call = self.mock_client.get.call_args_list[1]
        assert second_call[0] == ("/test/path",)

        assert result == all_results
        assert len(result) == 150

    @pytest.mark.asyncio
    async def test_get_route_with_existing_params(self):
        """Test _get_route preserves existing parameters while adding pagination."""
        expected_results = [{"id": "filtered1", "data": "test"}]

        mock_response_data = {"results": expected_results, "total": 1}

        mock_response = MagicMock()
        mock_response.json.return_value = mock_response_data
        self.mock_client.get.return_value = mock_response

        existing_params = {"filter": "active", "sort": "name"}
        result = await self.workflow_service._get_route(
            "/test/path", params=existing_params
        )

        # Should preserve existing params and add pagination params
        expected_params = {"filter": "active", "sort": "name", "limit": 100, "skip": 0}

        self.mock_client.get.assert_called_once_with(
            "/test/path", params=expected_params
        )
        assert result == expected_results

    @pytest.mark.asyncio
    async def test_get_route_empty_results(self):
        """Test _get_route with empty results."""
        mock_response_data = {"results": [], "total": 0}

        mock_response = MagicMock()
        mock_response.json.return_value = mock_response_data
        self.mock_client.get.return_value = mock_response

        result = await self.workflow_service._get_route("/test/path")

        self.mock_client.get.assert_called_once_with(
            "/test/path", params={"limit": 100, "skip": 0}
        )
        assert result == []

    @pytest.mark.asyncio
    async def test_get_route_exact_page_size(self):
        """Test _get_route when results exactly match page size."""
        expected_results = [
            {"id": f"item{i}", "data": f"test{i}"} for i in range(1, 101)
        ]

        mock_response_data = {"results": expected_results, "total": 100}

        mock_response = MagicMock()
        mock_response.json.return_value = mock_response_data
        self.mock_client.get.return_value = mock_response

        result = await self.workflow_service._get_route("/test/path")

        # Should make only one call since we got all 100 results
        self.mock_client.get.assert_called_once_with(
            "/test/path", params={"limit": 100, "skip": 0}
        )
        assert result == expected_results
        assert len(result) == 100

    @pytest.mark.asyncio
    async def test_get_job_metrics_error_handling(self):
        """Test get_job_metrics handles errors appropriately."""
        # Mock _get_route to raise an exception
        self.workflow_service._get_route = AsyncMock(side_effect=Exception("API Error"))

        with pytest.raises(Exception, match="API Error"):
            await self.workflow_service.get_job_metrics()

        self.workflow_service._get_route.assert_called_once_with(
            "/workflow_engine/jobs/metrics", params=None
        )

    @pytest.mark.asyncio
    async def test_get_task_metrics_error_handling(self):
        """Test get_task_metrics handles errors appropriately."""
        # Mock _get_route to raise an exception
        self.workflow_service._get_route = AsyncMock(side_effect=Exception("API Error"))

        with pytest.raises(Exception, match="API Error"):
            await self.workflow_service.get_task_metrics()

        self.workflow_service._get_route.assert_called_once_with(
            "/workflow_engine/tasks/metrics", params=None
        )

    @pytest.mark.asyncio
    async def test_get_route_client_error_handling(self):
        """Test _get_route handles client errors appropriately."""
        self.mock_client.get.side_effect = Exception("Network error")

        with pytest.raises(Exception, match="Network error"):
            await self.workflow_service._get_route("/test/path")

        self.mock_client.get.assert_called_once_with(
            "/test/path", params={"limit": 100, "skip": 0}
        )

    @pytest.mark.asyncio
    async def test_service_inherits_from_service_base(self):
        """Test that Service class correctly inherits from ServiceBase."""
        from itential_mcp.platform.services import ServiceBase

        assert isinstance(self.workflow_service, ServiceBase)
        assert hasattr(self.workflow_service, "client")
        assert self.workflow_service.client == self.mock_client

    def test_service_class_attributes(self):
        """Test Service class has correct attributes."""
        assert hasattr(Service, "name")
        assert Service.name == "workflow_engine"

    @pytest.mark.asyncio
    async def test_get_job_metrics_empty_results(self):
        """Test get_job_metrics with empty results."""
        expected_data = []

        # Mock the _get_route method
        self.workflow_service._get_route = AsyncMock(return_value=expected_data)

        result = await self.workflow_service.get_job_metrics()

        self.workflow_service._get_route.assert_called_once_with(
            "/workflow_engine/jobs/metrics", params=None
        )
        assert result == []

    @pytest.mark.asyncio
    async def test_get_task_metrics_empty_results(self):
        """Test get_task_metrics with empty results."""
        expected_data = []

        # Mock the _get_route method
        self.workflow_service._get_route = AsyncMock(return_value=expected_data)

        result = await self.workflow_service.get_task_metrics()

        self.workflow_service._get_route.assert_called_once_with(
            "/workflow_engine/tasks/metrics", params=None
        )
        assert result == []

    @pytest.mark.asyncio
    async def test_get_job_metrics_complex_data(self):
        """Test get_job_metrics with complex metric data."""
        expected_data = [
            {
                "_id": "complex-job-1",
                "workflow": "Complex Workflow",
                "metrics": {
                    "avgRunTime": 45.7,
                    "successRate": 0.923,
                    "errorRate": 0.077,
                    "timeoutRate": 0.001,
                    "retryCount": 12,
                    "lastRunTime": "2025-01-15T10:30:00Z",
                    "peakMemoryUsage": "512MB",
                    "avgCpuUsage": 23.5,
                },
                "jobsComplete": 1000,
                "totalRunTime": 45700,
                "jobsFailed": 77,
                "jobsTimeout": 1,
            }
        ]

        # Mock the _get_route method
        self.workflow_service._get_route = AsyncMock(return_value=expected_data)

        result = await self.workflow_service.get_job_metrics()

        self.workflow_service._get_route.assert_called_once_with(
            "/workflow_engine/jobs/metrics", params=None
        )
        assert result == expected_data
        assert result[0]["metrics"]["avgRunTime"] == 45.7
        assert result[0]["metrics"]["successRate"] == 0.923

    @pytest.mark.asyncio
    async def test_get_task_metrics_complex_data(self):
        """Test get_task_metrics with complex metric data."""
        expected_data = [
            {
                "taskId": "complex-task-1",
                "taskType": "automatic",
                "name": "Complex Data Processing",
                "metrics": {
                    "avgExecutionTime": 12.8,
                    "errorRate": 0.05,
                    "retryCount": 5,
                    "timeoutCount": 2,
                    "memoryUsage": {"peak": "256MB", "average": "128MB"},
                    "cpuUsage": {"peak": 85.2, "average": 32.1},
                },
                "app": "ComplexDataProcessor",
                "workflow": "Complex Data Pipeline",
                "executionCount": 500,
                "successCount": 475,
            }
        ]

        # Mock the _get_route method
        self.workflow_service._get_route = AsyncMock(return_value=expected_data)

        result = await self.workflow_service.get_task_metrics()

        self.workflow_service._get_route.assert_called_once_with(
            "/workflow_engine/tasks/metrics", params=None
        )
        assert result == expected_data
        assert result[0]["taskType"] == "automatic"
        assert result[0]["metrics"]["avgExecutionTime"] == 12.8

    def test_service_docstring_exists(self):
        """Test that Service has comprehensive documentation."""
        assert Service.__doc__ is not None
        assert len(Service.__doc__.strip()) > 0

        # Check that key concepts are documented
        docstring = Service.__doc__
        assert "Workflow Engine service" in docstring
        assert "Itential Platform" in docstring
        assert "metrics" in docstring
        assert "Attributes:" in docstring

    def test_get_job_metrics_docstring_exists(self):
        """Test that get_job_metrics has comprehensive documentation."""
        assert Service.get_job_metrics.__doc__ is not None
        assert len(Service.get_job_metrics.__doc__.strip()) > 0

        docstring = Service.get_job_metrics.__doc__
        assert "Args:" in docstring
        assert "Returns:" in docstring
        assert "Raises:" in docstring

    def test_get_task_metrics_docstring_exists(self):
        """Test that get_task_metrics has comprehensive documentation."""
        assert Service.get_task_metrics.__doc__ is not None
        assert len(Service.get_task_metrics.__doc__.strip()) > 0

        docstring = Service.get_task_metrics.__doc__
        assert "Args:" in docstring
        assert "Returns:" in docstring
        assert "Raises:" in docstring

    def test_get_route_docstring_exists(self):
        """Test that _get_route has comprehensive documentation."""
        assert Service._get_route.__doc__ is not None
        assert len(Service._get_route.__doc__.strip()) > 0

        docstring = Service._get_route.__doc__
        assert "Args:" in docstring
        assert "Returns:" in docstring
        assert "Raises:" in docstring
        assert "pagination" in docstring

    @pytest.mark.asyncio
    async def test_get_route_three_pages(self):
        """Test _get_route with exactly three pages of results."""
        page1_results = [{"id": f"item{i}"} for i in range(1, 101)]
        page2_results = [{"id": f"item{i}"} for i in range(101, 201)]
        page3_results = [{"id": f"item{i}"} for i in range(201, 251)]

        all_results = page1_results + page2_results + page3_results

        def mock_get_responses(*args, **kwargs):
            params = kwargs.get("params", {})
            skip = params.get("skip", 0)

            if skip == 0:
                return MagicMock(json=lambda: {"results": page1_results, "total": 250})
            elif skip == 100:
                return MagicMock(json=lambda: {"results": page2_results, "total": 250})
            elif skip == 200:
                return MagicMock(json=lambda: {"results": page3_results, "total": 250})

        self.mock_client.get.side_effect = mock_get_responses

        result = await self.workflow_service._get_route("/test/path")

        # Should make three calls
        assert self.mock_client.get.call_count == 3
        assert result == all_results
        assert len(result) == 250

    @pytest.mark.asyncio
    async def test_params_modification_behavior(self):
        """Test that _get_route modifies the params dictionary (documenting current behavior)."""
        original_params = {"filter": "active"}

        mock_response_data = {"results": [{"id": "test"}], "total": 1}

        mock_response = MagicMock()
        mock_response.json.return_value = mock_response_data
        self.mock_client.get.return_value = mock_response

        await self.workflow_service._get_route("/test/path", params=original_params)

        # The implementation modifies the original params dict by adding pagination params
        assert "limit" in original_params
        assert "skip" in original_params
        assert original_params["filter"] == "active"  # Original params are preserved
        assert original_params["limit"] == 100
        assert original_params["skip"] == 0  # Final skip value after loop completes
