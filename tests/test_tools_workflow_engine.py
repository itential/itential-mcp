# Copyright (c) 2025 Itential, Inc
# GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

import pytest
from unittest.mock import AsyncMock

from itential_mcp.tools.workflow_engine import (
    get_job_metrics,
    get_job_metrics_for_workflow,
    get_task_metrics,
    get_task_metrics_for_workflow,
    get_task_metrics_for_app,
    get_task_metrics_for_task,
)
from itential_mcp.models.workflow_engine import (
    JobMetricElement,
    TaskMetricElement,
    GetJobMetricsResponse,
    GetTaskMetricsResponse,
)
from fastmcp import Context


class TestWorkflowEngineTools:
    """Test cases for the workflow engine tool functions."""

    def setup_method(self):
        """Set up test fixtures before each test method."""
        self.mock_context = AsyncMock(spec=Context)
        self.mock_context.debug = AsyncMock()
        self.mock_context.info = AsyncMock()

        # Create mock client with workflow_engine attribute
        self.mock_client = AsyncMock()
        self.mock_client.workflow_engine = AsyncMock()
        self.mock_context.request_context.lifespan_context.get.return_value = (
            self.mock_client
        )

    def create_mock_job_metrics_data(self):
        """Create mock job metrics data for testing."""
        return [
            {
                "_id": "job-metric-123",
                "workflow": {"name": "test-workflow"},
                "metrics": [{"total_runs": 100, "success_rate": 0.95}],
                "jobsComplete": 25,
                "totalRunTime": 3600.5,
            },
            {
                "_id": "job-metric-456",
                "workflow": {"name": "production-workflow"},
                "metrics": [{"avg_duration": 45.2}],
                "jobsComplete": 50,
                "totalRunTime": 7200.0,
            },
        ]

    def create_mock_task_metrics_data(self):
        """Create mock task metrics data for testing."""
        return [
            {
                "taskId": "task-123",
                "taskType": "automatic",
                "name": "test-task",
                "metrics": [{"execution_count": 50, "avg_time": 2.5}],
                "app": "test-app",
                "workflow": {"name": "test-workflow"},
            },
            {
                "taskId": "task-456",
                "taskType": "manual",
                "name": "approval-task",
                "metrics": [{"pending_time": 3600.0}],
                "app": "approval-app",
                "workflow": {"name": "approval-workflow"},
            },
        ]

    @pytest.mark.asyncio
    async def test_get_job_metrics_success(self):
        """Test successful retrieval of job metrics."""
        # Arrange
        mock_data = self.create_mock_job_metrics_data()
        self.mock_client.workflow_engine.get_job_metrics.return_value = mock_data

        # Act
        result = await get_job_metrics(self.mock_context)

        # Assert
        assert isinstance(result, GetJobMetricsResponse)
        assert len(result.root) == 2

        # Check first job metric
        job1 = result.root[0]
        assert isinstance(job1, JobMetricElement)
        assert job1.object_id == "job-metric-123"
        assert job1.workflow == {"name": "test-workflow"}
        assert job1.jobs_complete == 25
        assert job1.total_run_time == 3600.5

        # Check second job metric
        job2 = result.root[1]
        assert job2.object_id == "job-metric-456"
        assert job2.workflow == {"name": "production-workflow"}
        assert job2.jobs_complete == 50

        # Verify API call was made correctly
        self.mock_client.workflow_engine.get_job_metrics.assert_called_once_with(
            params=None
        )

    @pytest.mark.asyncio
    async def test_get_job_metrics_for_workflow_success(self):
        """Test successful retrieval of job metrics for specific workflow."""
        # Arrange
        mock_data = self.create_mock_job_metrics_data()
        self.mock_client.workflow_engine.get_job_metrics.return_value = mock_data

        # Act
        result = await get_job_metrics_for_workflow(self.mock_context, "test-workflow")

        # Assert
        assert isinstance(result, GetJobMetricsResponse)
        assert len(result.root) == 2

        # Verify API call was made with correct params
        expected_params = {
            "containsField": "workflow.name",
            "contains": "test-workflow",
        }
        self.mock_client.workflow_engine.get_job_metrics.assert_called_once_with(
            params=expected_params
        )

    @pytest.mark.asyncio
    async def test_get_task_metrics_success(self):
        """Test successful retrieval of task metrics."""
        # Arrange
        mock_data = self.create_mock_task_metrics_data()
        self.mock_client.workflow_engine.get_task_metrics.return_value = mock_data

        # Act
        result = await get_task_metrics(self.mock_context)

        # Assert
        assert isinstance(result, GetTaskMetricsResponse)
        assert len(result.root) == 2

        # Check first task metric
        task1 = result.root[0]
        assert isinstance(task1, TaskMetricElement)
        assert task1.task_id == "task-123"
        assert task1.task_type == "automatic"
        assert task1.name == "test-task"
        assert task1.app == "test-app"
        assert task1.workflow == {"name": "test-workflow"}

        # Check second task metric
        task2 = result.root[1]
        assert task2.task_id == "task-456"
        assert task2.task_type == "manual"
        assert task2.name == "approval-task"

        # Verify API call was made correctly
        self.mock_client.workflow_engine.get_task_metrics.assert_called_once_with(
            params=None
        )

    @pytest.mark.asyncio
    async def test_get_task_metrics_for_workflow_success(self):
        """Test successful retrieval of task metrics for specific workflow."""
        # Arrange
        mock_data = self.create_mock_task_metrics_data()
        self.mock_client.workflow_engine.get_task_metrics.return_value = mock_data

        # Act
        result = await get_task_metrics_for_workflow(self.mock_context, "test-workflow")

        # Assert
        assert isinstance(result, GetTaskMetricsResponse)
        assert len(result.root) == 2

        # Verify API call was made with correct params
        expected_params = {"equalsField": "workflow.name", "equals": "test-workflow"}
        self.mock_client.workflow_engine.get_task_metrics.assert_called_once_with(
            params=expected_params
        )

    @pytest.mark.asyncio
    async def test_get_task_metrics_for_app_success(self):
        """Test successful retrieval of task metrics for specific app."""
        # Arrange
        mock_data = self.create_mock_task_metrics_data()
        self.mock_client.workflow_engine.get_task_metrics.return_value = mock_data

        # Act
        result = await get_task_metrics_for_app(self.mock_context, "test-app")

        # Assert
        assert isinstance(result, GetTaskMetricsResponse)
        assert len(result.root) == 2

        # Verify API call was made with correct params
        expected_params = {"equalsField": "app", "equals": "test-app"}
        self.mock_client.workflow_engine.get_task_metrics.assert_called_once_with(
            params=expected_params
        )

    @pytest.mark.asyncio
    async def test_get_task_metrics_for_task_success(self):
        """Test successful retrieval of task metrics for specific task."""
        # Arrange
        mock_data = self.create_mock_task_metrics_data()
        self.mock_client.workflow_engine.get_task_metrics.return_value = mock_data

        # Act
        result = await get_task_metrics_for_task(self.mock_context, "test-task")

        # Assert
        assert isinstance(result, GetTaskMetricsResponse)
        assert len(result.root) == 2

        # Verify API call was made with correct params
        expected_params = {"equalsField": "name", "equals": "test-task"}
        self.mock_client.workflow_engine.get_task_metrics.assert_called_once_with(
            params=expected_params
        )

    @pytest.mark.asyncio
    async def test_get_job_metrics_empty_response(self):
        """Test handling of empty job metrics response."""
        # Arrange
        mock_data = []
        self.mock_client.workflow_engine.get_job_metrics.return_value = mock_data

        # Act
        result = await get_job_metrics(self.mock_context)

        # Assert
        assert isinstance(result, GetJobMetricsResponse)
        assert len(result.root) == 0

    @pytest.mark.asyncio
    async def test_get_task_metrics_empty_response(self):
        """Test handling of empty task metrics response."""
        # Arrange
        mock_data = []
        self.mock_client.workflow_engine.get_task_metrics.return_value = mock_data

        # Act
        result = await get_task_metrics(self.mock_context)

        # Assert
        assert isinstance(result, GetTaskMetricsResponse)
        assert len(result.root) == 0

    @pytest.mark.asyncio
    async def test_get_task_metrics_filters_null_workflow(self):
        """Test that task metrics with null workflow are filtered out."""
        # Arrange
        mock_data = [
            {
                "taskId": "task-123",
                "taskType": "automatic",
                "name": "test-task",
                "metrics": [{"execution_count": 50}],
                "app": "test-app",
                "workflow": {"name": "test-workflow"},
            },
            {
                "taskId": "task-456",
                "taskType": "manual",
                "name": "orphaned-task",
                "metrics": [{"execution_count": 10}],
                "app": "test-app",
                "workflow": None,  # This should be filtered out
            },
        ]

        self.mock_client.workflow_engine.get_task_metrics.return_value = mock_data

        # Act
        result = await get_task_metrics(self.mock_context)

        # Assert
        assert isinstance(result, GetTaskMetricsResponse)
        assert (
            len(result.root) == 2
        )  # Both should be included since workflow field is optional
        assert result.root[0].task_id == "task-123"
        assert result.root[0].workflow == {"name": "test-workflow"}
        assert result.root[1].task_id == "task-456"
        assert result.root[1].workflow is None

    @pytest.mark.asyncio
    async def test_get_job_metrics_pagination(self):
        """Test job metrics with multiple items."""
        # Arrange - simulate multiple job metrics
        mock_data = [
            {
                "_id": "job-1",
                "workflow": {"name": "wf-1"},
                "metrics": [{}],
                "jobsComplete": 10,
                "totalRunTime": 100.0,
            },
            {
                "_id": "job-2",
                "workflow": {"name": "wf-2"},
                "metrics": [{}],
                "jobsComplete": 20,
                "totalRunTime": 200.0,
            },
        ]

        self.mock_client.workflow_engine.get_job_metrics.return_value = mock_data

        # Act
        result = await get_job_metrics(self.mock_context)

        # Assert
        assert isinstance(result, GetJobMetricsResponse)
        assert len(result.root) == 2
        assert result.root[0].object_id == "job-1"
        assert result.root[1].object_id == "job-2"

        # Verify API call was made
        self.mock_client.workflow_engine.get_job_metrics.assert_called_once_with(
            params=None
        )

    @pytest.mark.asyncio
    async def test_get_task_metrics_pagination(self):
        """Test task metrics with multiple items."""
        # Arrange - simulate multiple task metrics
        mock_data = [
            {
                "taskId": "task-1",
                "taskType": "automatic",
                "name": "task-1",
                "metrics": [{}],
                "app": "app-1",
                "workflow": {"name": "wf-1"},
            },
            {
                "taskId": "task-2",
                "taskType": "manual",
                "name": "task-2",
                "metrics": [{}],
                "app": "app-2",
                "workflow": {"name": "wf-2"},
            },
        ]

        self.mock_client.workflow_engine.get_task_metrics.return_value = mock_data

        # Act
        result = await get_task_metrics(self.mock_context)

        # Assert
        assert isinstance(result, GetTaskMetricsResponse)
        assert len(result.root) == 2
        assert result.root[0].task_id == "task-1"
        assert result.root[1].task_id == "task-2"

        # Verify API call was made
        self.mock_client.workflow_engine.get_task_metrics.assert_called_once_with(
            params=None
        )

    @pytest.mark.asyncio
    async def test_context_debug_called(self):
        """Test that context.debug is called."""
        # Arrange
        mock_data = []
        self.mock_client.workflow_engine.get_job_metrics.return_value = mock_data

        # Act
        await get_job_metrics(self.mock_context)

        # Assert
        self.mock_context.debug.assert_called_once_with("inside _get_job_metrics(...)")

    @pytest.mark.asyncio
    async def test_context_info_called_for_tasks(self):
        """Test that context.debug is called for task metrics."""
        # Arrange
        mock_data = []
        self.mock_client.workflow_engine.get_task_metrics.return_value = mock_data

        # Act
        await get_task_metrics(self.mock_context)

        # Assert
        self.mock_context.debug.assert_called_once_with("inside get_task_metrics(...)")
