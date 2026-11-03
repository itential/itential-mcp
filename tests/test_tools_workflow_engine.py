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
        self.mock_client.workflow_engine.get_job_metrics.return_value = (
            mock_data,
            len(mock_data),
        )

        # Act
        result = await get_job_metrics(self.mock_context)

        # Assert
        assert isinstance(result, GetJobMetricsResponse)
        assert len(result.results) == 2

        # Check first job metric
        job1 = result.results[0]
        assert isinstance(job1, JobMetricElement)
        assert job1.object_id == "job-metric-123"
        assert job1.workflow == {"name": "test-workflow"}
        assert job1.jobs_complete == 25
        assert job1.total_run_time == 3600.5

        # Check second job metric
        job2 = result.results[1]
        assert job2.object_id == "job-metric-456"
        assert job2.workflow == {"name": "production-workflow"}
        assert job2.jobs_complete == 50

        # Verify API call was made correctly
        self.mock_client.workflow_engine.get_job_metrics.assert_called_once_with(
            params=None, limit=200, skip=0
        )

    @pytest.mark.asyncio
    async def test_get_job_metrics_for_workflow_success(self):
        """Test successful retrieval of job metrics for specific workflow."""
        # Arrange
        mock_data = self.create_mock_job_metrics_data()
        self.mock_client.workflow_engine.get_job_metrics.return_value = (
            mock_data,
            len(mock_data),
        )

        # Act
        result = await get_job_metrics_for_workflow(self.mock_context, "test-workflow")

        # Assert
        assert isinstance(result, GetJobMetricsResponse)
        assert len(result.results) == 2

        # Verify API call was made with correct params
        expected_params = {
            "containsField": "workflow.name",
            "contains": "test-workflow",
        }
        self.mock_client.workflow_engine.get_job_metrics.assert_called_once_with(
            params=expected_params, limit=200, skip=0
        )

    @pytest.mark.asyncio
    async def test_get_task_metrics_success(self):
        """Test successful retrieval of task metrics."""
        # Arrange
        mock_data = self.create_mock_task_metrics_data()
        self.mock_client.workflow_engine.get_task_metrics.return_value = (
            mock_data,
            len(mock_data),
        )

        # Act
        result = await get_task_metrics(self.mock_context)

        # Assert
        assert isinstance(result, GetTaskMetricsResponse)
        assert len(result.results) == 2

        # Check first task metric
        task1 = result.results[0]
        assert isinstance(task1, TaskMetricElement)
        assert task1.task_id == "task-123"
        assert task1.task_type == "automatic"
        assert task1.name == "test-task"
        assert task1.app == "test-app"
        assert task1.workflow == {"name": "test-workflow"}

        # Check second task metric
        task2 = result.results[1]
        assert task2.task_id == "task-456"
        assert task2.task_type == "manual"
        assert task2.name == "approval-task"

        # Verify API call was made correctly
        self.mock_client.workflow_engine.get_task_metrics.assert_called_once_with(
            params=None, limit=200, skip=0
        )

    @pytest.mark.asyncio
    async def test_get_task_metrics_for_workflow_success(self):
        """Test successful retrieval of task metrics for specific workflow."""
        # Arrange
        mock_data = self.create_mock_task_metrics_data()
        self.mock_client.workflow_engine.get_task_metrics.return_value = (
            mock_data,
            len(mock_data),
        )

        # Act
        result = await get_task_metrics_for_workflow(self.mock_context, "test-workflow")

        # Assert
        assert isinstance(result, GetTaskMetricsResponse)
        assert len(result.results) == 2

        # Verify API call was made with correct params
        expected_params = {"equalsField": "workflow.name", "equals": "test-workflow"}
        self.mock_client.workflow_engine.get_task_metrics.assert_called_once_with(
            params=expected_params, limit=200, skip=0
        )

    @pytest.mark.asyncio
    async def test_get_task_metrics_for_app_success(self):
        """Test successful retrieval of task metrics for specific app."""
        # Arrange
        mock_data = self.create_mock_task_metrics_data()
        self.mock_client.workflow_engine.get_task_metrics.return_value = (
            mock_data,
            len(mock_data),
        )

        # Act
        result = await get_task_metrics_for_app(self.mock_context, "test-app")

        # Assert
        assert isinstance(result, GetTaskMetricsResponse)
        assert len(result.results) == 2

        # Verify API call was made with correct params
        expected_params = {"equalsField": "app", "equals": "test-app"}
        self.mock_client.workflow_engine.get_task_metrics.assert_called_once_with(
            params=expected_params, limit=200, skip=0
        )

    @pytest.mark.asyncio
    async def test_get_task_metrics_for_task_success(self):
        """Test successful retrieval of task metrics for specific task."""
        # Arrange
        mock_data = self.create_mock_task_metrics_data()
        self.mock_client.workflow_engine.get_task_metrics.return_value = (
            mock_data,
            len(mock_data),
        )

        # Act
        result = await get_task_metrics_for_task(self.mock_context, "test-task")

        # Assert
        assert isinstance(result, GetTaskMetricsResponse)
        assert len(result.results) == 2

        # Verify API call was made with correct params
        expected_params = {"equalsField": "name", "equals": "test-task"}
        self.mock_client.workflow_engine.get_task_metrics.assert_called_once_with(
            params=expected_params, limit=200, skip=0
        )

    @pytest.mark.asyncio
    async def test_get_job_metrics_empty_response(self):
        """Test handling of empty job metrics response."""
        # Arrange
        mock_data = []
        self.mock_client.workflow_engine.get_job_metrics.return_value = (
            mock_data,
            len(mock_data),
        )

        # Act
        result = await get_job_metrics(self.mock_context)

        # Assert
        assert isinstance(result, GetJobMetricsResponse)
        assert len(result.results) == 0

    @pytest.mark.asyncio
    async def test_get_task_metrics_empty_response(self):
        """Test handling of empty task metrics response."""
        # Arrange
        mock_data = []
        self.mock_client.workflow_engine.get_task_metrics.return_value = (
            mock_data,
            len(mock_data),
        )

        # Act
        result = await get_task_metrics(self.mock_context)

        # Assert
        assert isinstance(result, GetTaskMetricsResponse)
        assert len(result.results) == 0

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

        self.mock_client.workflow_engine.get_task_metrics.return_value = (
            mock_data,
            len(mock_data),
        )

        # Act
        result = await get_task_metrics(self.mock_context)

        # Assert
        assert isinstance(result, GetTaskMetricsResponse)
        assert (
            len(result.results) == 2
        )  # Both should be included since workflow field is optional
        assert result.results[0].task_id == "task-123"
        assert result.results[0].workflow == {"name": "test-workflow"}
        assert result.results[1].task_id == "task-456"
        assert result.results[1].workflow is None

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

        self.mock_client.workflow_engine.get_job_metrics.return_value = (
            mock_data,
            len(mock_data),
        )

        # Act
        result = await get_job_metrics(self.mock_context)

        # Assert
        assert isinstance(result, GetJobMetricsResponse)
        assert len(result.results) == 2
        assert result.results[0].object_id == "job-1"
        assert result.results[1].object_id == "job-2"

        # Verify API call was made
        self.mock_client.workflow_engine.get_job_metrics.assert_called_once_with(
            params=None, limit=200, skip=0
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

        self.mock_client.workflow_engine.get_task_metrics.return_value = (
            mock_data,
            len(mock_data),
        )

        # Act
        result = await get_task_metrics(self.mock_context)

        # Assert
        assert isinstance(result, GetTaskMetricsResponse)
        assert len(result.results) == 2
        assert result.results[0].task_id == "task-1"
        assert result.results[1].task_id == "task-2"

        # Verify API call was made
        self.mock_client.workflow_engine.get_task_metrics.assert_called_once_with(
            params=None, limit=200, skip=0
        )

    @pytest.mark.asyncio
    async def test_context_debug_called(self):
        """Test that context.debug is called."""
        # Arrange
        mock_data = []
        self.mock_client.workflow_engine.get_job_metrics.return_value = (
            mock_data,
            len(mock_data),
        )

        # Act
        await get_job_metrics(self.mock_context)

        # Assert
        self.mock_context.debug.assert_called_once_with("inside _get_job_metrics(...)")

    @pytest.mark.asyncio
    async def test_context_info_called_for_tasks(self):
        """Test that context.debug is called for task metrics."""
        # Arrange
        mock_data = []
        self.mock_client.workflow_engine.get_task_metrics.return_value = (
            mock_data,
            len(mock_data),
        )

        # Act
        await get_task_metrics(self.mock_context)

        # Assert
        self.mock_context.debug.assert_called_once_with("inside get_task_metrics(...)")

    @pytest.mark.asyncio
    async def test_pagination_metadata_and_has_more(self):
        """Response carries total/returned/limit/skip and computes has_more."""
        mock_data = self.create_mock_task_metrics_data()
        self.mock_client.workflow_engine.get_task_metrics.return_value = (
            mock_data,
            5,
        )

        result = await get_task_metrics(self.mock_context, limit=2, skip=0)

        assert result.total == 5
        assert result.returned == 2
        assert result.limit == 2
        assert result.skip == 0
        assert result.has_more is True
        self.mock_client.workflow_engine.get_task_metrics.assert_called_once_with(
            params=None, limit=2, skip=0
        )

    @pytest.mark.asyncio
    async def test_last_page_has_more_false(self):
        """has_more is False when skip + returned reaches total."""
        mock_data = self.create_mock_job_metrics_data()
        self.mock_client.workflow_engine.get_job_metrics.return_value = (
            mock_data,
            12,
        )

        result = await get_job_metrics(self.mock_context, limit=10, skip=10)

        assert result.has_more is False
        assert result.skip == 10

    @pytest.mark.asyncio
    async def test_limit_skip_threaded_with_filters(self):
        """limit/skip are passed alongside the sibling filters for all tools."""
        self.mock_client.workflow_engine.get_job_metrics.return_value = ([], 0)
        self.mock_client.workflow_engine.get_task_metrics.return_value = ([], 0)

        await get_job_metrics_for_workflow(self.mock_context, "wf", limit=7, skip=3)
        self.mock_client.workflow_engine.get_job_metrics.assert_called_once_with(
            params={"containsField": "workflow.name", "contains": "wf"},
            limit=7,
            skip=3,
        )

        await get_task_metrics_for_workflow(self.mock_context, "wf", limit=7, skip=3)
        self.mock_client.workflow_engine.get_task_metrics.assert_called_with(
            params={"equalsField": "workflow.name", "equals": "wf"},
            limit=7,
            skip=3,
        )
        await get_task_metrics_for_app(self.mock_context, "a", limit=7, skip=3)
        self.mock_client.workflow_engine.get_task_metrics.assert_called_with(
            params={"equalsField": "app", "equals": "a"}, limit=7, skip=3
        )
        await get_task_metrics_for_task(self.mock_context, "t", limit=7, skip=3)
        self.mock_client.workflow_engine.get_task_metrics.assert_called_with(
            params={"equalsField": "name", "equals": "t"}, limit=7, skip=3
        )

    @pytest.mark.parametrize(
        "fn,args",
        [
            (get_job_metrics, ()),
            (get_job_metrics_for_workflow, ("x",)),
            (get_task_metrics, ()),
            (get_task_metrics_for_workflow, ("x",)),
            (get_task_metrics_for_app, ("x",)),
            (get_task_metrics_for_task, ("x",)),
        ],
    )
    @pytest.mark.parametrize(
        "kwargs",
        [{"limit": 0}, {"limit": 1001}, {"limit": -5}, {"skip": -1}],
    )
    def test_out_of_range_params_rejected(self, fn, args, kwargs):
        """limit must be 1-1000 and skip >= 0; validated via the tool schema."""
        from pydantic import TypeAdapter, ValidationError

        arguments = {"ctx": self.mock_context, **kwargs}
        if args:
            arguments["name"] = args[0]

        with pytest.raises(ValidationError) as exc_info:
            TypeAdapter(fn).validate_python(arguments)

        rejected = {err["loc"][0] for err in exc_info.value.errors()}
        assert rejected == set(kwargs)

    @pytest.mark.parametrize(
        "fn",
        [
            get_job_metrics,
            get_job_metrics_for_workflow,
            get_task_metrics,
            get_task_metrics_for_workflow,
            get_task_metrics_for_app,
            get_task_metrics_for_task,
        ],
    )
    def test_limit_skip_defaults(self, fn):
        """All six tools default to limit=200, skip=0, keyword-only."""
        import inspect

        sig = inspect.signature(fn)
        assert sig.parameters["limit"].default == 200
        assert sig.parameters["skip"].default == 0
        assert sig.parameters["limit"].kind is inspect.Parameter.KEYWORD_ONLY
        assert sig.parameters["skip"].kind is inspect.Parameter.KEYWORD_ONLY


class _FakePlatformClient:
    """Stand-in for PlatformClient exposing a real workflow_engine Service."""

    def __init__(self, http_client):
        from itential_mcp.platform.services.workflow_engine import Service

        self.workflow_engine = Service(http_client)

    async def __aenter__(self):
        return self

    async def __aexit__(self, *exc):
        return None


class TestMetricsToolsInProcess:
    """End-to-end tests through a real in-process FastMCP Client."""

    def _http_client(self, total):
        """Mock platform HTTP client honoring skip/limit over `total` items."""
        from unittest.mock import MagicMock

        def element(i):
            return {
                "taskId": f"t-{i}",
                "taskType": "automatic",
                "name": f"task-{i}",
                "metrics": [{"n": i}],
                "app": "WorkFlowEngine",
                "workflow": {"name": "wf"},
            }

        async def get(path, params=None):
            skip, limit = params["skip"], params["limit"]
            res = MagicMock()
            res.json.return_value = {
                "results": [element(i) for i in range(skip, min(skip + limit, total))],
                "skip": skip,
                "limit": limit,
                "total": total,
            }
            return res

        client = MagicMock()
        client.get = AsyncMock(side_effect=get)
        return client

    async def _server(self):
        from itential_mcp.config.models import Config, ServerConfig, AuthConfig
        from itential_mcp.server import server as server_module

        cfg = Config(
            server=ServerConfig(transport="stdio", tools_path=None, log_level="INFO"),
            auth=AuthConfig(type="none"),
        )
        return server_module.Server(cfg)

    @pytest.mark.asyncio
    async def test_default_cap_and_schema_validation(self):
        """>200 platform items return 200, with full total and has_more."""
        from unittest.mock import patch

        from fastmcp import Client
        from jsonschema import validate

        http = self._http_client(total=650)

        async def empty_aiter():
            return
            yield

        with (
            patch(
                "itential_mcp.server.server.PlatformClient",
                return_value=_FakePlatformClient(http),
            ),
            patch("itential_mcp.server.auth.build_auth_provider", return_value=None),
            patch(
                "itential_mcp.server.server.bindings.iterbindings",
                return_value=empty_aiter(),
            ),
        ):
            async with await self._server() as srv:
                async with Client(srv.mcp) as client:
                    tools = {t.name: t for t in await client.list_tools()}
                    tool = tools["get_task_metrics"]
                    assert "limit" in tool.input_schema["properties"]
                    assert "skip" in tool.input_schema["properties"]

                    result = await client.call_tool("get_task_metrics", {})
                    data = result.structured_content

                    assert len(data["results"]) == 200
                    assert data["returned"] == 200
                    assert data["total"] == 650
                    assert data["limit"] == 200
                    assert data["skip"] == 0
                    assert data["has_more"] is True
                    assert tool.output_schema is not None
                    first = data["results"][0]
                    assert {"taskId", "taskType"} <= set(first)
                    assert "task_id" not in first
                    validate(instance=data, schema=tool.output_schema)

                    # second page via skip
                    result = await client.call_tool(
                        "get_task_metrics", {"limit": 500, "skip": 200}
                    )
                    data = result.structured_content
                    assert data["returned"] == 450
                    assert data["has_more"] is False
                    validate(instance=data, schema=tool.output_schema)

    @pytest.mark.asyncio
    async def test_out_of_range_rejected_through_client(self):
        """limit > 1000 and skip < 0 are rejected by the MCP layer."""
        from unittest.mock import patch

        from fastmcp import Client
        from mcp.shared.exceptions import MCPError

        http = self._http_client(total=10)

        async def empty_aiter():
            return
            yield

        with (
            patch(
                "itential_mcp.server.server.PlatformClient",
                return_value=_FakePlatformClient(http),
            ),
            patch("itential_mcp.server.auth.build_auth_provider", return_value=None),
            patch(
                "itential_mcp.server.server.bindings.iterbindings",
                return_value=empty_aiter(),
            ),
        ):
            async with await self._server() as srv:
                async with Client(srv.mcp) as client:
                    for args in ({"limit": 1001}, {"limit": 0}, {"skip": -1}):
                        with pytest.raises(MCPError, match="limit|skip"):
                            await client.call_tool("get_task_metrics", args)
                    http.get.assert_not_called()
