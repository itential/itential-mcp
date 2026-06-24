# Copyright (c) 2025 Itential, Inc
# GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from pydantic import ValidationError

from fastmcp import Context

from itential_mcp.tools import operations_manager
from itential_mcp.models.operations_manager import (
    GetWorkflowsResponse,
    GetJobsResponse,
    StartWorkflowResponse,
    JobMetrics,
    DescribeJobResponse,
)


class TestModule:
    """Test the operations_manager tools module"""

    def test_module_tags(self):
        """Test module has correct tags"""
        assert hasattr(operations_manager, "__tags__")
        assert operations_manager.__tags__ == ("operations_manager",)

    def test_module_functions_exist(self):
        """Test all expected functions exist in the module"""
        expected_functions = [
            "get_workflows",
            "get_agents",
            "get_automations",
            "trigger_automation",
            "start_workflow",
            "get_jobs",
            "describe_job",
            "describe_session",
            "expose_workflow",
            "expose_agent",
            "_account_id_to_username",
        ]

        for func_name in expected_functions:
            assert hasattr(operations_manager, func_name)
            assert callable(getattr(operations_manager, func_name))

    def test_functions_are_async(self):
        """Test that all functions are async"""
        import inspect

        functions_to_test = [
            operations_manager._account_id_to_username,
            operations_manager.get_workflows,
            operations_manager.get_agents,
            operations_manager.get_automations,
            operations_manager.trigger_automation,
            operations_manager.start_workflow,
            operations_manager.get_jobs,
            operations_manager.describe_job,
            operations_manager.describe_session,
            operations_manager.expose_workflow,
            operations_manager.expose_agent,
        ]

        for func in functions_to_test:
            assert inspect.iscoroutinefunction(func), f"{func.__name__} should be async"


class TestGetWorkflows:
    """Test the get_workflows tool function"""

    @pytest.fixture
    def mock_context(self):
        """Create a mock Context object"""
        context = AsyncMock(spec=Context)
        context.info = AsyncMock()

        # Mock client and operations_manager service
        mock_client = MagicMock()
        mock_operations_manager = AsyncMock()
        mock_client.operations_manager = mock_operations_manager

        # Mock request context and lifespan context
        context.request_context = MagicMock()
        context.request_context.lifespan_context = MagicMock()
        context.request_context.lifespan_context.get.return_value = mock_client

        return context

    @pytest.mark.asyncio
    async def test_get_workflows_validation_error(self, mock_context):
        """Test get_workflows succeeds as WorkflowElement doesn't require _id field"""
        mock_data = [
            {
                "_id": "workflow-123",
                "name": "Test Workflow",
                "description": "A test workflow",
                "schema": {
                    "type": "object",
                    "properties": {"input": {"type": "string"}},
                },
                "routeName": "test-route",
                "lastExecuted": 1640995200000,
            }
        ]
        mock_context.request_context.lifespan_context.get.return_value.operations_manager.get_workflows.return_value = mock_data

        with patch(
            "itential_mcp.tools.operations_manager.timeutils.epoch_to_timestamp"
        ) as mock_timestamp:
            mock_timestamp.return_value = "2022-01-01T00:00:00Z"

            result = await operations_manager.get_workflows(mock_context)

            assert isinstance(result, GetWorkflowsResponse)
            assert len(result.root) == 1
            assert result.root[0].name == "Test Workflow"
            assert result.root[0].description == "A test workflow"
            assert result.root[0].last_executed == "2022-01-01T00:00:00Z"

    @pytest.mark.asyncio
    async def test_get_workflows_empty_data(self, mock_context):
        """Test get_workflows with empty data"""
        empty_data = []
        mock_context.request_context.lifespan_context.get.return_value.operations_manager.get_workflows.return_value = empty_data

        result = await operations_manager.get_workflows(mock_context)

        assert isinstance(result, GetWorkflowsResponse)
        assert len(result.root) == 0

    @pytest.mark.asyncio
    async def test_get_workflows_null_data(self, mock_context):
        """Test get_workflows with None data"""
        null_data = None
        mock_context.request_context.lifespan_context.get.return_value.operations_manager.get_workflows.return_value = null_data

        # This should raise an exception since None is not iterable
        with pytest.raises(TypeError, match="'NoneType' object is not iterable"):
            await operations_manager.get_workflows(mock_context)

    @pytest.mark.asyncio
    async def test_get_workflows_missing_data_key(self, mock_context):
        """Test get_workflows with empty dict returns empty response"""
        empty_response = {}
        mock_context.request_context.lifespan_context.get.return_value.operations_manager.get_workflows.return_value = empty_response

        # Empty dict iteration produces no items, so we get empty response
        result = await operations_manager.get_workflows(mock_context)

        assert isinstance(result, GetWorkflowsResponse)
        assert len(result.root) == 0


class TestStartWorkflow:
    """Test the start_workflow tool function"""

    @pytest.fixture
    def mock_context(self):
        """Create a mock Context object"""
        context = AsyncMock(spec=Context)
        context.info = AsyncMock()

        # Mock client and operations_manager service
        mock_client = MagicMock()
        mock_operations_manager = AsyncMock()
        mock_client.operations_manager = mock_operations_manager

        # Mock request context and lifespan context
        context.request_context = MagicMock()
        context.request_context.lifespan_context = MagicMock()
        context.request_context.lifespan_context.get.return_value = mock_client

        return context

    @pytest.fixture
    def mock_workflow_response(self):
        """Mock workflow execution response"""
        return {
            "_id": "job-123",
            "name": "Test Workflow",
            "description": "A test workflow",
            "tasks": {"task1": {"type": "action", "data": "test"}},
            "status": "running",
            "metrics": {
                "start_time": 1640995200000,
                "end_time": None,
                "user": "user-123",
            },
        }

    @pytest.mark.asyncio
    async def test_start_workflow_success(self, mock_context, mock_workflow_response):
        """Test start_workflow successfully starts a workflow"""
        mock_context.request_context.lifespan_context.get.return_value.operations_manager.start_workflow.return_value = mock_workflow_response

        with (
            patch(
                "itential_mcp.tools.operations_manager.timeutils.epoch_to_timestamp"
            ) as mock_timestamp,
            patch(
                "itential_mcp.tools.operations_manager._account_id_to_username"
            ) as mock_username,
        ):
            mock_timestamp.return_value = "2022-01-01T00:00:00Z"
            mock_username.return_value = "test-user"

            result = await operations_manager.start_workflow(
                mock_context, "test-route", {"param": "value"}
            )

            assert isinstance(result, StartWorkflowResponse)
            assert result.object_id == "job-123"
            assert result.name == "Test Workflow"
            assert result.description == "A test workflow"
            assert result.status == "running"
            assert isinstance(result.metrics, JobMetrics)
            assert result.metrics.start_time == "2022-01-01T00:00:00Z"
            assert result.metrics.user == "test-user"

    @pytest.mark.asyncio
    async def test_start_workflow_no_data(self, mock_context, mock_workflow_response):
        """Test start_workflow with no input data"""
        mock_context.request_context.lifespan_context.get.return_value.operations_manager.start_workflow.return_value = mock_workflow_response

        with (
            patch(
                "itential_mcp.tools.operations_manager.timeutils.epoch_to_timestamp"
            ) as mock_timestamp,
            patch(
                "itential_mcp.tools.operations_manager._account_id_to_username"
            ) as mock_username,
        ):
            mock_timestamp.return_value = "2022-01-01T00:00:00Z"
            mock_username.return_value = "test-user"

            result = await operations_manager.start_workflow(
                mock_context, "test-route", None
            )

            assert isinstance(result, StartWorkflowResponse)
            assert result.object_id == "job-123"

    @pytest.mark.asyncio
    async def test_start_workflow_empty_route_name(self, mock_context):
        """Test start_workflow with empty route name"""
        mock_context.request_context.lifespan_context.get.return_value.operations_manager.start_workflow.side_effect = ValueError(
            "Route name cannot be empty"
        )

        with pytest.raises(ValueError, match="Route name cannot be empty"):
            await operations_manager.start_workflow(
                mock_context, "", {"param": "value"}
            )

    @pytest.mark.asyncio
    async def test_start_workflow_minimal_metrics(self, mock_context):
        """Test start_workflow with minimal metrics data"""
        minimal_response = {
            "_id": "job-456",
            "name": "Minimal Workflow",
            "tasks": {},
            "status": "running",  # Must be a valid literal value
            "metrics": {},
        }
        mock_context.request_context.lifespan_context.get.return_value.operations_manager.start_workflow.return_value = minimal_response

        result = await operations_manager.start_workflow(
            mock_context, "minimal-route", None
        )

        assert isinstance(result, StartWorkflowResponse)
        assert result.object_id == "job-456"
        assert result.metrics.start_time is None
        assert result.metrics.end_time is None
        assert result.metrics.user is None


class TestCoerceValue:
    """Unit tests for _coerce_value"""

    def test_string_to_array(self):
        result = operations_manager._coerce_value('["a", "b"]', {"type": "array"})
        assert result == ["a", "b"]

    def test_string_to_object(self):
        result = operations_manager._coerce_value('{"key": "val"}', {"type": "object"})
        assert result == {"key": "val"}

    def test_non_json_string_unchanged(self):
        result = operations_manager._coerce_value("hello", {"type": "array"})
        assert result == "hello"

    def test_single_quoted_string_unchanged(self):
        # Single quotes are not valid JSON — value should pass through unmodified
        result = operations_manager._coerce_value("['a', 'b']", {"type": "array"})
        assert result == "['a', 'b']"

    def test_correct_type_unchanged(self):
        result = operations_manager._coerce_value(["a", "b"], {"type": "array"})
        assert result == ["a", "b"]

    def test_no_schema_type_unchanged(self):
        result = operations_manager._coerce_value('["a"]', {})
        assert result == '["a"]'

    def test_type_mismatch_after_parse_unchanged(self):
        # Schema says array but parsed value is an object — leave it for platform to reject
        result = operations_manager._coerce_value('{"k": "v"}', {"type": "array"})
        assert result == '{"k": "v"}'


class TestCoerceDataToSchema:
    """Unit tests for _coerce_data_to_schema"""

    def test_coerces_stringified_array(self):
        schema = {"properties": {"config": {"type": "array"}}}
        data = {"device": "router1", "config": '["interface eth0"]'}
        result = operations_manager._coerce_data_to_schema(data, schema)
        assert result["config"] == ["interface eth0"]
        assert result["device"] == "router1"

    def test_unknown_keys_passed_through(self):
        schema = {"properties": {}}
        data = {"extra": '["x"]'}
        result = operations_manager._coerce_data_to_schema(data, schema)
        assert result["extra"] == '["x"]'

    def test_empty_schema_no_coercion(self):
        data = {"config": '["a", "b"]'}
        result = operations_manager._coerce_data_to_schema(data, {})
        assert result["config"] == '["a", "b"]'


class TestStartWorkflowCoercion:
    """Test that start_workflow coerces data values using the workflow schema"""

    @pytest.fixture
    def mock_context(self):
        context = AsyncMock(spec=Context)
        context.info = AsyncMock()
        mock_client = MagicMock()
        mock_operations_manager = AsyncMock()
        mock_client.operations_manager = mock_operations_manager
        context.request_context = MagicMock()
        context.request_context.lifespan_context = MagicMock()
        context.request_context.lifespan_context.get.return_value = mock_client
        return context

    @pytest.fixture
    def mock_job_response(self):
        return {
            "_id": "job-999",
            "name": "FRR Device Config",
            "description": None,
            "tasks": {},
            "status": "running",
            "metrics": {},
        }

    @pytest.mark.asyncio
    async def test_stringified_array_coerced_before_post(
        self, mock_context, mock_job_response
    ):
        """A config value sent as a JSON string is coerced to a list before the platform call."""
        workflow_schema = {
            "type": "object",
            "properties": {
                "device": {"type": "string"},
                "config": {"type": "array"},
            },
        }
        mock_context.request_context.lifespan_context.get.return_value.operations_manager.get_workflows.return_value = [
            {"routeName": "frr_device_cfg", "schema": workflow_schema}
        ]
        mock_context.request_context.lifespan_context.get.return_value.operations_manager.start_workflow.return_value = mock_job_response

        await operations_manager.start_workflow(
            mock_context,
            "frr_device_cfg",
            {
                "device": "chicago-p",
                "config": '["interface eth0", "description Management"]',
            },
        )

        call_args = mock_context.request_context.lifespan_context.get.return_value.operations_manager.start_workflow.call_args
        sent_data = call_args[0][1]
        assert sent_data["config"] == ["interface eth0", "description Management"]
        assert sent_data["device"] == "chicago-p"

    @pytest.mark.asyncio
    async def test_no_matching_workflow_data_passed_through(
        self, mock_context, mock_job_response
    ):
        """When route_name has no schema match, data is forwarded unchanged."""
        mock_context.request_context.lifespan_context.get.return_value.operations_manager.get_workflows.return_value = []
        mock_context.request_context.lifespan_context.get.return_value.operations_manager.start_workflow.return_value = mock_job_response

        await operations_manager.start_workflow(
            mock_context,
            "unknown_route",
            {"config": '["a", "b"]'},
        )

        call_args = mock_context.request_context.lifespan_context.get.return_value.operations_manager.start_workflow.call_args
        sent_data = call_args[0][1]
        assert sent_data["config"] == '["a", "b"]'

    @pytest.mark.asyncio
    async def test_schema_fetch_failure_data_passed_through(
        self, mock_context, mock_job_response
    ):
        """If fetching the workflow schema fails, data is forwarded unchanged."""
        mock_context.request_context.lifespan_context.get.return_value.operations_manager.get_workflows.side_effect = Exception(
            "platform unavailable"
        )
        mock_context.request_context.lifespan_context.get.return_value.operations_manager.start_workflow.return_value = mock_job_response

        await operations_manager.start_workflow(
            mock_context,
            "frr_device_cfg",
            {"config": '["a", "b"]'},
        )

        call_args = mock_context.request_context.lifespan_context.get.return_value.operations_manager.start_workflow.call_args
        sent_data = call_args[0][1]
        assert sent_data["config"] == '["a", "b"]'
        mock_context.warning.assert_awaited()


class TestGetJobs:
    """Test the get_jobs tool function"""

    @pytest.fixture
    def mock_context(self):
        """Create a mock Context object"""
        context = AsyncMock(spec=Context)
        context.info = AsyncMock()

        # Mock client and operations_manager service
        mock_client = MagicMock()
        mock_operations_manager = AsyncMock()
        mock_client.operations_manager = mock_operations_manager

        # Mock request context and lifespan context
        context.request_context = MagicMock()
        context.request_context.lifespan_context = MagicMock()
        context.request_context.lifespan_context.get.return_value = mock_client

        return context

    @pytest.mark.asyncio
    async def test_get_jobs_validation_error(self, mock_context):
        """Test get_jobs succeeds with valid job data"""
        mock_data = [
            {
                "_id": "job-123",
                "name": "Test Job",
                "description": "A test job",
                "status": "complete",
            }
        ]
        mock_context.request_context.lifespan_context.get.return_value.operations_manager.get_jobs.return_value = mock_data

        result = await operations_manager.get_jobs(mock_context, None, None)

        assert isinstance(result, GetJobsResponse)
        assert len(result.root) == 1
        assert result.root[0].object_id == "job-123"
        assert result.root[0].name == "Test Job"
        assert result.root[0].description == "A test job"
        assert result.root[0].status == "complete"

    @pytest.mark.asyncio
    async def test_get_jobs_with_filters_validation_error(self, mock_context):
        """Test get_jobs with name and project filters succeeds"""
        mock_data = [
            {
                "_id": "job-123",
                "name": "Filtered Job",
                "description": "A filtered job",
                "status": "complete",
            }
        ]
        mock_context.request_context.lifespan_context.get.return_value.operations_manager.get_jobs.return_value = mock_data

        result = await operations_manager.get_jobs(
            mock_context, name="test-workflow", project="test-project"
        )

        assert isinstance(result, GetJobsResponse)
        assert len(result.root) == 1
        assert result.root[0].object_id == "job-123"
        assert result.root[0].name == "Filtered Job"

        # Verify that the filters were passed to the service
        mock_context.request_context.lifespan_context.get.return_value.operations_manager.get_jobs.assert_called_with(
            name="test-workflow", project="test-project"
        )

    @pytest.mark.asyncio
    async def test_get_jobs_empty_data(self, mock_context):
        """Test get_jobs with empty data"""
        mock_context.request_context.lifespan_context.get.return_value.operations_manager.get_jobs.return_value = []

        result = await operations_manager.get_jobs(mock_context, None, None)

        assert isinstance(result, GetJobsResponse)
        assert len(result.root) == 0

    @pytest.mark.asyncio
    async def test_get_jobs_none_data(self, mock_context):
        """Test get_jobs with None data"""
        mock_context.request_context.lifespan_context.get.return_value.operations_manager.get_jobs.return_value = None

        result = await operations_manager.get_jobs(mock_context, None, None)

        assert isinstance(result, GetJobsResponse)
        assert len(result.root) == 0


class TestDescribeJob:
    """Test the describe_job tool function"""

    @pytest.fixture
    def mock_context(self):
        """Create a mock Context object"""
        context = AsyncMock(spec=Context)
        context.info = AsyncMock()

        # Mock client and operations_manager service
        mock_client = MagicMock()
        mock_operations_manager = AsyncMock()
        mock_client.operations_manager = mock_operations_manager

        # Mock request context and lifespan context
        context.request_context = MagicMock()
        context.request_context.lifespan_context = MagicMock()
        context.request_context.lifespan_context.get.return_value = mock_client

        return context

    @pytest.mark.asyncio
    async def test_describe_job_validation_error(self, mock_context):
        """Test describe_job fails due to missing _id field - KeyError for direct access"""
        mock_data = {
            "name": "Detailed Job",
            "description": "A detailed job description",
            "type": "automation",
            "tasks": {"task1": {"type": "action", "status": "complete"}},
            "status": "complete",
            "metrics": {"start_time": 1640995200000, "end_time": 1640999200000},
            "last_updated": "2022-01-01T12:00:00Z",
        }
        mock_context.request_context.lifespan_context.get.return_value.operations_manager.describe_job.return_value = mock_data

        # The source code uses direct access - missing _id causes KeyError
        with pytest.raises(KeyError, match="_id"):
            await operations_manager.describe_job(mock_context, "job-123")

        # Verify that the correct object_id was passed to the service
        mock_context.request_context.lifespan_context.get.return_value.operations_manager.describe_job.assert_called_with(
            "job-123"
        )

    @pytest.mark.asyncio
    async def test_describe_job_multiple_validation_errors(self, mock_context):
        """Test describe_job with multiple validation errors"""
        mock_data = {
            "_id": "job-123",  # Include _id to get past KeyError and test ValidationError
            "name": "Minimal Job",
            "description": None,
            "type": "resource:action",
            "tasks": {},
            "status": "pending",  # This is not a valid status literal
            "metrics": {},
            "last_updated": None,  # This should be a string, not None
        }
        mock_context.request_context.lifespan_context.get.return_value.operations_manager.describe_job.return_value = mock_data

        # The source code has bugs - invalid status, and None for required string field
        with pytest.raises(ValidationError) as exc_info:
            await operations_manager.describe_job(mock_context, "job-456")

        errors = exc_info.value.errors()
        assert len(errors) == 2  # status invalid, updated None

        error_types = [error["type"] for error in errors]
        assert "literal_error" in error_types  # status not in valid literals
        assert "string_type" in error_types  # updated should be string, not None


class TestAccountIdToUsername:
    """Test the _account_id_to_username helper function"""

    @pytest.fixture
    def mock_context(self):
        """Create a mock Context object"""
        context = AsyncMock(spec=Context)

        # Mock client
        mock_client = MagicMock()
        context.request_context = MagicMock()
        context.request_context.lifespan_context = MagicMock()
        context.request_context.lifespan_context.get.return_value = mock_client

        return context

    @pytest.mark.asyncio
    async def test_account_id_to_username_success(self, mock_context):
        """Test _account_id_to_username successfully finds username"""
        mock_data = {
            "results": [
                {"_id": "user-123", "username": "test-user"},
                {"_id": "user-456", "username": "another-user"},
            ],
            "total": 2,
        }
        mock_client = mock_context.request_context.lifespan_context.get.return_value
        mock_response = MagicMock()
        mock_response.json.return_value = mock_data
        mock_client.get = AsyncMock(return_value=mock_response)

        result = await operations_manager._account_id_to_username(
            mock_context, "user-123"
        )

        assert result == "test-user"
        mock_client.get.assert_called_once_with(
            "/authorization/accounts", params={"limit": 100, "skip": 0}
        )

    @pytest.mark.asyncio
    async def test_account_id_to_username_not_found(self, mock_context):
        """Test _account_id_to_username raises ValueError when account not found"""
        mock_data = {
            "results": [{"_id": "user-456", "username": "another-user"}],
            "total": 1,
        }
        mock_client = mock_context.request_context.lifespan_context.get.return_value
        mock_response = MagicMock()
        mock_response.json.return_value = mock_data
        mock_client.get = AsyncMock(return_value=mock_response)

        with pytest.raises(
            ValueError, match="unable to find account with id user-nonexistent"
        ):
            await operations_manager._account_id_to_username(
                mock_context, "user-nonexistent"
            )

    @pytest.mark.asyncio
    async def test_account_id_pagination_logic(self, mock_context):
        """Test _account_id_to_username pagination logic with multiple requests"""
        # First page response - no target user (100 users)
        first_page = {
            "results": [
                {"_id": f"user-{i:03d}", "username": f"user{i}"} for i in range(100)
            ],
            "total": 150,
        }

        # Second page response with target user (50 users to complete total of 150)
        second_page = {
            "results": [
                {"_id": "user-101", "username": "user101"},
                {"_id": "target-user", "username": "found-user"},
            ]
            + [
                {"_id": f"user-{i:03d}", "username": f"user{i}"}
                for i in range(102, 150)
            ],
            "total": 150,
        }

        mock_client = mock_context.request_context.lifespan_context.get.return_value
        mock_response1 = MagicMock()
        mock_response1.json.return_value = first_page
        mock_response2 = MagicMock()
        mock_response2.json.return_value = second_page

        # The function will call get twice because cnt (100) + len(results) (50) = 150 = total
        responses = [mock_response1, mock_response2]
        mock_client.get = AsyncMock(side_effect=responses)

        result = await operations_manager._account_id_to_username(
            mock_context, "target-user"
        )

        assert result == "found-user"
        assert mock_client.get.call_count == 2
        # Just verify it was called multiple times - the exact params are tricky due to mutation

    @pytest.mark.asyncio
    async def test_account_id_empty_results(self, mock_context):
        """Test _account_id_to_username with empty results"""
        mock_data = {"results": [], "total": 0}
        mock_client = mock_context.request_context.lifespan_context.get.return_value
        mock_response = MagicMock()
        mock_response.json.return_value = mock_data
        mock_client.get = AsyncMock(return_value=mock_response)

        with pytest.raises(
            ValueError, match="unable to find account with id nonexistent"
        ):
            await operations_manager._account_id_to_username(
                mock_context, "nonexistent"
            )


class TestExposeWorkflow:
    """Test the expose_workflow tool function"""

    @pytest.fixture
    def mock_context(self):
        """Create a mock Context object"""
        context = AsyncMock(spec=Context)
        context.info = AsyncMock()

        # Mock client and services
        mock_client = MagicMock()
        mock_operations_manager = AsyncMock()
        mock_automation_studio = AsyncMock()
        mock_client.operations_manager = mock_operations_manager
        mock_client.automation_studio = mock_automation_studio

        # Mock request context and lifespan context
        context.request_context = MagicMock()
        context.request_context.lifespan_context = MagicMock()
        context.request_context.lifespan_context.get.return_value = mock_client

        return context

    @pytest.mark.asyncio
    async def test_expose_workflow_global_success(self, mock_context):
        """Test expose_workflow succeeds with global workflow"""
        # Mock create_automation response
        mock_context.request_context.lifespan_context.get.return_value.operations_manager.create_automation.return_value = {
            "_id": "automation-123"
        }

        # Mock workflow describe response
        mock_context.request_context.lifespan_context.get.return_value.automation_studio.describe_workflow_with_name.return_value = {
            "inputSchema": {
                "type": "object",
                "properties": {"param": {"type": "string"}},
            }
        }

        # Mock create_endpoint_trigger success
        mock_context.request_context.lifespan_context.get.return_value.operations_manager.create_endpoint_trigger.return_value = {
            "_id": "trigger-123"
        }

        result = await operations_manager.expose_workflow(
            mock_context,
            "Test Workflow",
            route_name=None,
            project=None,
            endpoint_name=None,
            endpoint_description=None,
            endpoint_schema=None,
        )

        assert (
            result.message
            == "Successfully exposed workflow `Test Workflow` with route `None`"
        )

        # Verify create_automation was called
        mock_context.request_context.lifespan_context.get.return_value.operations_manager.create_automation.assert_called_once_with(
            name="Test Workflow",
            component_type="workflows",
            component_name="Test Workflow",
            description="auto-created by itential-mcp",
        )

        # Verify create_endpoint_trigger was called
        mock_context.request_context.lifespan_context.get.return_value.operations_manager.create_endpoint_trigger.assert_called_once()

    @pytest.mark.asyncio
    async def test_expose_workflow_with_project(self, mock_context):
        """Test expose_workflow with project workflow"""
        # Mock describe_project response
        mock_context.request_context.lifespan_context.get.return_value.automation_studio.describe_project.return_value = {
            "_id": "project-123"
        }

        # Mock create_automation response
        mock_context.request_context.lifespan_context.get.return_value.operations_manager.create_automation.return_value = {
            "_id": "automation-456"
        }

        # Mock workflow describe response
        mock_context.request_context.lifespan_context.get.return_value.automation_studio.describe_workflow_with_name.return_value = {
            "inputSchema": {"type": "object"}
        }

        # Mock create_endpoint_trigger success
        mock_context.request_context.lifespan_context.get.return_value.operations_manager.create_endpoint_trigger.return_value = {
            "_id": "trigger-456"
        }

        result = await operations_manager.expose_workflow(
            mock_context,
            "Project Workflow",
            route_name="project-route",
            project="MyProject",
            endpoint_name=None,
            endpoint_description=None,
            endpoint_schema=None,
        )

        assert (
            result.message
            == "Successfully exposed workflow `Project Workflow` with route `project-route`"
        )

        # Verify project lookup
        mock_context.request_context.lifespan_context.get.return_value.automation_studio.describe_project.assert_called_once_with(
            "MyProject"
        )

        # Verify create_automation with project workflow name
        mock_context.request_context.lifespan_context.get.return_value.operations_manager.create_automation.assert_called_once_with(
            name="Project Workflow from MyProject",
            component_type="workflows",
            component_name="@project-123: Project Workflow",
            description="auto-created by itential-mcp",
        )

    @pytest.mark.asyncio
    async def test_expose_workflow_custom_parameters(self, mock_context):
        """Test expose_workflow with custom parameters"""
        # Mock create_automation response
        mock_context.request_context.lifespan_context.get.return_value.operations_manager.create_automation.return_value = {
            "_id": "automation-789"
        }

        # Mock create_endpoint_trigger success
        mock_context.request_context.lifespan_context.get.return_value.operations_manager.create_endpoint_trigger.return_value = {
            "_id": "trigger-789"
        }

        custom_schema = {"type": "object", "properties": {"custom": {"type": "string"}}}

        result = await operations_manager.expose_workflow(
            mock_context,
            "Custom Workflow",
            route_name="custom-route",
            project=None,
            endpoint_name="Custom Endpoint",
            endpoint_description="Custom Description",
            endpoint_schema=custom_schema,
        )

        assert (
            result.message
            == "Successfully exposed workflow `Custom Workflow` with route `custom-route`"
        )

        # Verify create_endpoint_trigger was called with custom parameters
        mock_context.request_context.lifespan_context.get.return_value.operations_manager.create_endpoint_trigger.assert_called_once_with(
            name="Custom Endpoint",
            automation_id="automation-789",
            description="Custom Description",
            route_name="custom-route",
            schema=custom_schema,
        )

    @pytest.mark.asyncio
    async def test_expose_workflow_endpoint_trigger_failure(self, mock_context):
        """Test expose_workflow handles endpoint trigger creation failure"""
        # Mock create_automation response
        mock_context.request_context.lifespan_context.get.return_value.operations_manager.create_automation.return_value = {
            "_id": "automation-fail"
        }

        # Mock workflow describe response
        mock_context.request_context.lifespan_context.get.return_value.automation_studio.describe_workflow_with_name.return_value = {
            "inputSchema": {"type": "object"}
        }

        # Mock endpoint trigger failure
        from itential_mcp.core import exceptions

        mock_context.request_context.lifespan_context.get.return_value.operations_manager.create_endpoint_trigger.side_effect = Exception(
            "Trigger creation failed"
        )

        # Mock delete_automation for cleanup
        mock_context.request_context.lifespan_context.get.return_value.operations_manager.delete_automation.return_value = {
            "message": "deleted"
        }

        with pytest.raises(
            exceptions.ConfigurationException,
            match="failed to expose workflow: Trigger creation failed",
        ):
            await operations_manager.expose_workflow(
                mock_context,
                "Failing Workflow",
                route_name=None,
                project=None,
                endpoint_name=None,
                endpoint_description=None,
                endpoint_schema=None,
            )

        # Verify cleanup was called
        mock_context.request_context.lifespan_context.get.return_value.operations_manager.delete_automation.assert_called_once_with(
            "automation-fail"
        )

    @pytest.mark.asyncio
    async def test_expose_workflow_default_route_name(self, mock_context):
        """Test expose_workflow uses default route name"""
        # Mock create_automation response
        mock_context.request_context.lifespan_context.get.return_value.operations_manager.create_automation.return_value = {
            "_id": "automation-default"
        }

        # Mock workflow describe response
        mock_context.request_context.lifespan_context.get.return_value.automation_studio.describe_workflow_with_name.return_value = {
            "inputSchema": {"type": "object"}
        }

        # Mock create_endpoint_trigger success
        mock_context.request_context.lifespan_context.get.return_value.operations_manager.create_endpoint_trigger.return_value = {
            "_id": "trigger-default"
        }

        await operations_manager.expose_workflow(
            mock_context,
            "Workflow With Spaces",
            route_name=None,
            project=None,
            endpoint_name=None,
            endpoint_description=None,
            endpoint_schema=None,
        )

        # Verify route_name default (spaces replaced with underscores)
        call_args = mock_context.request_context.lifespan_context.get.return_value.operations_manager.create_endpoint_trigger.call_args
        assert call_args[1]["route_name"] == "Workflow_With_Spaces"

    @pytest.mark.asyncio
    async def test_expose_workflow_default_endpoint_name(self, mock_context):
        """Test expose_workflow uses default endpoint name"""
        # Mock create_automation response
        mock_context.request_context.lifespan_context.get.return_value.operations_manager.create_automation.return_value = {
            "_id": "automation-endpoint"
        }

        # Mock workflow describe response
        mock_context.request_context.lifespan_context.get.return_value.automation_studio.describe_workflow_with_name.return_value = {
            "inputSchema": {"type": "object"}
        }

        # Mock create_endpoint_trigger success
        mock_context.request_context.lifespan_context.get.return_value.operations_manager.create_endpoint_trigger.return_value = {
            "_id": "trigger-endpoint"
        }

        await operations_manager.expose_workflow(
            mock_context,
            "Test Workflow",
            route_name=None,
            project=None,
            endpoint_name=None,
            endpoint_description=None,
            endpoint_schema=None,
        )

        # Verify endpoint_name default
        call_args = mock_context.request_context.lifespan_context.get.return_value.operations_manager.create_endpoint_trigger.call_args
        assert call_args[1]["name"] == "API Route for Test Workflow"


class TestGetWorkflowsSuccess:
    """Test successful get_workflows scenarios"""

    @pytest.fixture
    def mock_context(self):
        """Create a mock Context object"""
        context = AsyncMock(spec=Context)
        context.info = AsyncMock()

        mock_client = MagicMock()
        mock_operations_manager = AsyncMock()
        mock_client.operations_manager = mock_operations_manager

        context.request_context = MagicMock()
        context.request_context.lifespan_context = MagicMock()
        context.request_context.lifespan_context.get.return_value = mock_client

        return context

    @pytest.mark.asyncio
    async def test_get_workflows_success(self, mock_context):
        """Test get_workflows with successful response"""
        mock_data = [
            {
                "name": "Workflow 1",
                "description": "First workflow",
                "schema": {"type": "object"},
                "routeName": "workflow-1",
                "lastExecuted": 1640995200000,
            },
            {
                "name": "Workflow 2",
                "description": None,
                "schema": None,
                "routeName": "workflow-2",
                "lastExecuted": None,
            },
        ]
        mock_context.request_context.lifespan_context.get.return_value.operations_manager.get_workflows.return_value = mock_data

        with patch(
            "itential_mcp.tools.operations_manager.timeutils.epoch_to_timestamp"
        ) as mock_timestamp:
            mock_timestamp.return_value = "2022-01-01T00:00:00Z"

            result = await operations_manager.get_workflows(mock_context)

            assert isinstance(result, GetWorkflowsResponse)
            assert len(result.root) == 2
            assert result.root[0].name == "Workflow 1"
            assert result.root[0].last_executed == "2022-01-01T00:00:00Z"
            assert result.root[1].name == "Workflow 2"
            assert result.root[1].last_executed is None

    @pytest.mark.asyncio
    async def test_get_workflows_with_missing_fields(self, mock_context):
        """Test get_workflows handles missing optional fields"""
        mock_data = [
            {
                "name": "Minimal Workflow"
                # Missing description, schema, routeName, lastExecuted
            }
        ]
        mock_context.request_context.lifespan_context.get.return_value.operations_manager.get_workflows.return_value = mock_data

        result = await operations_manager.get_workflows(mock_context)

        assert isinstance(result, GetWorkflowsResponse)
        assert len(result.root) == 1
        assert result.root[0].name == "Minimal Workflow"
        assert result.root[0].description is None
        assert result.root[0].input_schema is None
        assert result.root[0].route_name is None
        assert result.root[0].last_executed is None


class TestGetJobsSuccess:
    """Test successful get_jobs scenarios"""

    @pytest.fixture
    def mock_context(self):
        """Create a mock Context object"""
        context = AsyncMock(spec=Context)
        context.info = AsyncMock()

        mock_client = MagicMock()
        mock_operations_manager = AsyncMock()
        mock_client.operations_manager = mock_operations_manager

        context.request_context = MagicMock()
        context.request_context.lifespan_context = MagicMock()
        context.request_context.lifespan_context.get.return_value = mock_client

        return context

    @pytest.mark.asyncio
    async def test_get_jobs_success(self, mock_context):
        """Test get_jobs with successful response"""
        mock_data = [
            {
                "_id": "job-123",
                "name": "Test Job",
                "description": "A test job",
                "status": "complete",
            },
            {
                "_id": "job-456",
                "name": "Another Job",
                "description": None,
                "status": "running",
            },
        ]
        mock_context.request_context.lifespan_context.get.return_value.operations_manager.get_jobs.return_value = mock_data

        result = await operations_manager.get_jobs(mock_context, None, None)

        assert isinstance(result, GetJobsResponse)
        assert len(result.root) == 2
        assert result.root[0].object_id == "job-123"
        assert result.root[0].name == "Test Job"
        assert result.root[0].description == "A test job"
        assert result.root[0].status == "complete"
        assert result.root[1].object_id == "job-456"
        assert result.root[1].name == "Another Job"
        assert result.root[1].description is None
        assert result.root[1].status == "running"

    @pytest.mark.asyncio
    async def test_get_jobs_with_filters_bug_demonstration(self, mock_context):
        """Test get_jobs with name and project filters succeeds"""
        mock_data = [
            {
                "_id": "job-filtered",
                "name": "Filtered Job",
                "description": "A filtered job",
                "status": "complete",
            }
        ]
        mock_context.request_context.lifespan_context.get.return_value.operations_manager.get_jobs.return_value = mock_data

        result = await operations_manager.get_jobs(
            mock_context, name="test-workflow", project="test-project"
        )

        assert isinstance(result, GetJobsResponse)
        assert len(result.root) == 1
        assert result.root[0].object_id == "job-filtered"
        assert result.root[0].name == "Filtered Job"
        assert result.root[0].description == "A filtered job"
        assert result.root[0].status == "complete"

        # Verify filters were passed correctly to the service
        mock_context.request_context.lifespan_context.get.return_value.operations_manager.get_jobs.assert_called_with(
            name="test-workflow", project="test-project"
        )


class TestDescribeJobSuccess:
    """Test successful describe_job scenarios"""

    @pytest.fixture
    def mock_context(self):
        """Create a mock Context object"""
        context = AsyncMock(spec=Context)
        context.info = AsyncMock()

        mock_client = MagicMock()
        mock_operations_manager = AsyncMock()
        mock_client.operations_manager = mock_operations_manager

        context.request_context = MagicMock()
        context.request_context.lifespan_context = MagicMock()
        context.request_context.lifespan_context.get.return_value = mock_client

        return context

    @pytest.mark.asyncio
    async def test_describe_job_success(self, mock_context):
        """Test describe_job with successful response"""
        mock_data = {
            "_id": "job-123",
            "name": "Detailed Job",
            "description": "A detailed job description",
            "type": "automation",
            "tasks": {"task1": {"type": "action", "status": "complete"}},
            "status": "complete",
            "metrics": {"start_time": 1640995200000, "end_time": 1640999200000},
            "last_updated": "2022-01-01T12:00:00Z",
        }
        mock_context.request_context.lifespan_context.get.return_value.operations_manager.describe_job.return_value = mock_data

        result = await operations_manager.describe_job(mock_context, "job-123")

        assert isinstance(result, DescribeJobResponse)
        assert result.object_id == "job-123"
        assert result.name == "Detailed Job"
        assert result.description == "A detailed job description"
        assert result.job_type == "automation"
        assert result.status == "complete"
        assert result.updated == "2022-01-01T12:00:00Z"
        assert result.variables is None

        # Verify service was called with correct parameter
        mock_context.request_context.lifespan_context.get.return_value.operations_manager.describe_job.assert_called_with(
            "job-123"
        )

    @pytest.mark.asyncio
    async def test_describe_job_with_variables(self, mock_context):
        """Test describe_job returns variables when present in the API response"""
        mock_data = {
            "_id": "job-456",
            "name": "Job With Variables",
            "description": "A job that produces output variables",
            "type": "automation",
            "tasks": {"task1": {"type": "action", "status": "complete"}},
            "status": "complete",
            "metrics": {"start_time": 1640995200000, "end_time": 1640999200000},
            "last_updated": "2022-01-01T12:00:00Z",
            "variables": {"output_ip": "192.168.1.1", "result_code": 0},
        }
        mock_context.request_context.lifespan_context.get.return_value.operations_manager.describe_job.return_value = mock_data

        result = await operations_manager.describe_job(mock_context, "job-456")

        assert isinstance(result, DescribeJobResponse)
        assert result.object_id == "job-456"
        assert result.variables == {"output_ip": "192.168.1.1", "result_code": 0}

        # Verify service was called with correct parameter
        mock_context.request_context.lifespan_context.get.return_value.operations_manager.describe_job.assert_called_with(
            "job-456"
        )

    @pytest.mark.asyncio
    async def test_describe_job_minimal_data(self, mock_context):
        """Test describe_job with minimal required data"""
        mock_data = {
            "_id": "job-minimal",
            "name": "Minimal Job",
            "description": None,
            "type": "resource:action",
            "tasks": {},
            "status": "running",
            "metrics": {},
            "last_updated": "2022-01-01T00:00:00Z",
        }
        mock_context.request_context.lifespan_context.get.return_value.operations_manager.describe_job.return_value = mock_data

        result = await operations_manager.describe_job(mock_context, "job-minimal")

        assert isinstance(result, DescribeJobResponse)
        assert result.object_id == "job-minimal"
        assert result.name == "Minimal Job"
        assert result.description is None
        assert result.job_type == "resource:action"
        assert result.status == "running"


class TestStartWorkflowMetricsHandling:
    """Test start_workflow metrics processing edge cases"""

    @pytest.fixture
    def mock_context(self):
        """Create a mock Context object"""
        context = AsyncMock(spec=Context)
        context.info = AsyncMock()

        mock_client = MagicMock()
        mock_operations_manager = AsyncMock()
        mock_client.operations_manager = mock_operations_manager

        context.request_context = MagicMock()
        context.request_context.lifespan_context = MagicMock()
        context.request_context.lifespan_context.get.return_value = mock_client

        return context

    @pytest.mark.asyncio
    async def test_start_workflow_no_metrics(self, mock_context):
        """Test start_workflow when metrics field is missing"""
        mock_response = {
            "_id": "job-no-metrics",
            "name": "No Metrics Workflow",
            "tasks": {},
            "status": "running",
            # No metrics field at all
        }
        mock_context.request_context.lifespan_context.get.return_value.operations_manager.start_workflow.return_value = mock_response

        result = await operations_manager.start_workflow(
            mock_context, "test-route", None
        )

        assert isinstance(result, StartWorkflowResponse)
        assert result.metrics.start_time is None
        assert result.metrics.end_time is None
        assert result.metrics.user is None

    @pytest.mark.asyncio
    async def test_start_workflow_with_end_time(self, mock_context):
        """Test start_workflow with both start and end time"""
        mock_response = {
            "_id": "job-complete",
            "name": "Complete Workflow",
            "tasks": {},
            "status": "complete",
            "metrics": {
                "start_time": 1640995200000,
                "end_time": 1640999200000,
                "user": "user-complete",
            },
        }
        mock_context.request_context.lifespan_context.get.return_value.operations_manager.start_workflow.return_value = mock_response

        with (
            patch(
                "itential_mcp.tools.operations_manager.timeutils.epoch_to_timestamp"
            ) as mock_timestamp,
            patch(
                "itential_mcp.tools.operations_manager._account_id_to_username"
            ) as mock_username,
        ):
            mock_timestamp.side_effect = [
                "2022-01-01T00:00:00Z",
                "2022-01-01T01:00:00Z",
            ]
            mock_username.return_value = "complete-user"

            result = await operations_manager.start_workflow(
                mock_context, "complete-route", None
            )

            assert result.metrics.start_time == "2022-01-01T00:00:00Z"
            assert result.metrics.end_time == "2022-01-01T01:00:00Z"
            assert result.metrics.user == "complete-user"

    @pytest.mark.asyncio
    async def test_start_workflow_account_username_error(self, mock_context):
        """Test start_workflow when _account_id_to_username fails"""
        mock_response = {
            "_id": "job-user-error",
            "name": "User Error Workflow",
            "tasks": {},
            "status": "running",
            "metrics": {"start_time": 1640995200000, "user": "invalid-user-id"},
        }
        mock_context.request_context.lifespan_context.get.return_value.operations_manager.start_workflow.return_value = mock_response

        with (
            patch(
                "itential_mcp.tools.operations_manager.timeutils.epoch_to_timestamp"
            ) as mock_timestamp,
            patch(
                "itential_mcp.tools.operations_manager._account_id_to_username"
            ) as mock_username,
        ):
            mock_timestamp.return_value = "2022-01-01T00:00:00Z"
            mock_username.side_effect = ValueError(
                "unable to find account with id invalid-user-id"
            )

            # Should propagate the ValueError from _account_id_to_username
            with pytest.raises(
                ValueError, match="unable to find account with id invalid-user-id"
            ):
                await operations_manager.start_workflow(
                    mock_context, "error-route", None
                )


class TestErrorHandling:
    """Test error handling across all functions"""

    @pytest.fixture
    def mock_context(self):
        """Create a mock Context object"""
        context = AsyncMock(spec=Context)
        context.info = AsyncMock()

        mock_client = MagicMock()
        mock_operations_manager = AsyncMock()
        mock_client.operations_manager = mock_operations_manager

        context.request_context = MagicMock()
        context.request_context.lifespan_context = MagicMock()
        context.request_context.lifespan_context.get.return_value = mock_client

        return context

    @pytest.mark.asyncio
    async def test_get_workflows_client_error(self, mock_context):
        """Test get_workflows handles client errors"""
        mock_context.request_context.lifespan_context.get.return_value.operations_manager.get_workflows.side_effect = Exception(
            "API Error"
        )

        with pytest.raises(Exception, match="API Error"):
            await operations_manager.get_workflows(mock_context)

    @pytest.mark.asyncio
    async def test_start_workflow_client_error(self, mock_context):
        """Test start_workflow handles client errors"""
        mock_context.request_context.lifespan_context.get.return_value.operations_manager.start_workflow.side_effect = Exception(
            "Workflow start failed"
        )

        with pytest.raises(Exception, match="Workflow start failed"):
            await operations_manager.start_workflow(mock_context, "test-route", {})

    @pytest.mark.asyncio
    async def test_get_jobs_client_error(self, mock_context):
        """Test get_jobs handles client errors"""
        mock_context.request_context.lifespan_context.get.return_value.operations_manager.get_jobs.side_effect = Exception(
            "Jobs fetch failed"
        )

        with pytest.raises(Exception, match="Jobs fetch failed"):
            await operations_manager.get_jobs(mock_context, None, None)

    @pytest.mark.asyncio
    async def test_describe_job_client_error(self, mock_context):
        """Test describe_job handles client errors"""
        mock_context.request_context.lifespan_context.get.return_value.operations_manager.describe_job.side_effect = Exception(
            "Job describe failed"
        )

        with pytest.raises(Exception, match="Job describe failed"):
            await operations_manager.describe_job(mock_context, "job-123")

    @pytest.mark.asyncio
    async def test_account_id_to_username_client_error(self, mock_context):
        """Test _account_id_to_username handles client errors"""
        mock_client = mock_context.request_context.lifespan_context.get.return_value
        mock_client.get = AsyncMock(side_effect=Exception("Authorization API Error"))

        with pytest.raises(Exception, match="Authorization API Error"):
            await operations_manager._account_id_to_username(mock_context, "user-123")


class TestGetAgentsTool:
    """Test the get_agents tool function"""

    @pytest.fixture
    def mock_context(self):
        ctx = MagicMock(spec=Context)
        ctx.info = AsyncMock()
        ctx.debug = AsyncMock()
        ctx.warning = AsyncMock()
        mock_client = MagicMock()
        mock_client.operations_manager = AsyncMock()
        ctx.request_context.lifespan_context.get.return_value = mock_client
        return ctx

    @pytest.mark.asyncio
    async def test_get_agents_returns_response(self, mock_context):
        """Test get_agents returns GetAgentsResponse"""
        from itential_mcp.models.operations_manager import GetAgentsResponse

        mock_context.request_context.lifespan_context.get.return_value.operations_manager.get_agents = AsyncMock(
            return_value=[
                {
                    "name": "My Agent",
                    "description": "does stuff",
                    "agent_id": "uuid-001",
                    "route_name": "my-agent",
                    "input_schema": {"type": "object"},
                    "last_executed": None,
                }
            ]
        )

        result = await operations_manager.get_agents(mock_context)

        assert isinstance(result, GetAgentsResponse)
        assert len(result.root) == 1
        assert result.root[0].name == "My Agent"
        assert result.root[0].route_name == "my-agent"

    @pytest.mark.asyncio
    async def test_get_agents_empty(self, mock_context):
        """Test get_agents with empty result"""
        from itential_mcp.models.operations_manager import GetAgentsResponse

        mock_context.request_context.lifespan_context.get.return_value.operations_manager.get_agents = AsyncMock(
            return_value=[]
        )

        result = await operations_manager.get_agents(mock_context)

        assert isinstance(result, GetAgentsResponse)
        assert result.root == []

    @pytest.mark.asyncio
    async def test_get_agents_converts_epoch_timestamp(self, mock_context):
        """Test get_agents converts epoch last_executed to ISO string"""
        mock_context.request_context.lifespan_context.get.return_value.operations_manager.get_agents = AsyncMock(
            return_value=[
                {
                    "name": "Timed Agent",
                    "description": "",
                    "agent_id": "uuid-002",
                    "route_name": "timed",
                    "input_schema": None,
                    "last_executed": 1640995200000,
                }
            ]
        )

        result = await operations_manager.get_agents(mock_context)

        assert result.root[0].last_executed is not None
        assert "2022" in result.root[0].last_executed


class TestStartWorkflowAgentBranch:
    """Test start_workflow when triggered against an agent endpoint"""

    @pytest.fixture
    def mock_context(self):
        ctx = MagicMock(spec=Context)
        ctx.info = AsyncMock()
        ctx.debug = AsyncMock()
        ctx.warning = AsyncMock()
        mock_client = MagicMock()
        mock_client.operations_manager = AsyncMock()
        ctx.request_context.lifespan_context.get.return_value = mock_client
        return ctx

    @pytest.mark.asyncio
    async def test_start_workflow_agent_returns_session(self, mock_context):
        """Test start_workflow returns StartAgentResponse when platform returns sessionId"""
        from itential_mcp.models.operations_manager import StartAgentResponse

        mock_context.request_context.lifespan_context.get.return_value.operations_manager.start_workflow = AsyncMock(
            return_value={"sessionId": "sess-xyz", "status": "RUNNING"}
        )
        mock_context.request_context.lifespan_context.get.return_value.operations_manager.get_workflows = AsyncMock(
            return_value=[]
        )

        result = await operations_manager.start_workflow(
            mock_context, "jfagent", {"input": "hello"}
        )

        assert isinstance(result, StartAgentResponse)
        assert result.session_id == "sess-xyz"
        assert result.status == "RUNNING"

    @pytest.mark.asyncio
    async def test_start_workflow_agent_complete_status(self, mock_context):
        """Test start_workflow handles COMPLETE status from agent session"""
        from itential_mcp.models.operations_manager import StartAgentResponse

        mock_context.request_context.lifespan_context.get.return_value.operations_manager.start_workflow = AsyncMock(
            return_value={"sessionId": "sess-done", "status": "COMPLETE"}
        )
        mock_context.request_context.lifespan_context.get.return_value.operations_manager.get_workflows = AsyncMock(
            return_value=[]
        )

        result = await operations_manager.start_workflow(
            mock_context, "some-agent-route", None
        )

        assert isinstance(result, StartAgentResponse)
        assert result.status == "COMPLETE"


class TestDescribeSessionTool:
    """Test the describe_session tool function"""

    @pytest.fixture
    def mock_context(self):
        ctx = MagicMock(spec=Context)
        ctx.info = AsyncMock()
        ctx.debug = AsyncMock()
        ctx.warning = AsyncMock()
        mock_client = MagicMock()
        mock_client.operations_manager = AsyncMock()
        ctx.request_context.lifespan_context.get.return_value = mock_client
        return ctx

    @pytest.mark.asyncio
    async def test_describe_session_complete(self, mock_context):
        """Test describe_session returns output for a completed session"""
        from itential_mcp.models.operations_manager import DescribeSessionResponse

        mock_ops = mock_context.request_context.lifespan_context.get.return_value.operations_manager
        mock_ops.get_session = AsyncMock(
            return_value={
                "sessionId": "sess-001",
                "status": "COMPLETE",
                "startedAt": "2025-01-01T00:00:00Z",
                "endTime": "2025-01-01T00:00:05Z",
                "durationMs": 5000,
                "agentSnapshot": {"_id": "uuid-001", "name": "JF Agent"},
            }
        )
        mock_ops.get_session_messages = AsyncMock(
            return_value=[
                {
                    "type": "inference-succeeded",
                    "category": "AGENT_REASONING",
                    "text": "Your one liner here.",
                    "timestamp": 1640995200000,
                },
                {
                    "type": "agent-session-completed",
                    "category": "AGENT_STATUS",
                    "timestamp": 1640995200100,
                },
            ]
        )

        result = await operations_manager.describe_session(mock_context, "sess-001")

        assert isinstance(result, DescribeSessionResponse)
        assert result.session_id == "sess-001"
        assert result.status == "COMPLETE"
        assert result.agent_name == "JF Agent"
        assert result.output == "Your one liner here."
        assert result.duration_ms == 5000
        assert len(result.messages) == 2

    @pytest.mark.asyncio
    async def test_describe_session_running_no_output(self, mock_context):
        """Test describe_session returns None output while session is RUNNING"""
        from itential_mcp.models.operations_manager import DescribeSessionResponse

        mock_ops = mock_context.request_context.lifespan_context.get.return_value.operations_manager
        mock_ops.get_session = AsyncMock(
            return_value={
                "sessionId": "sess-002",
                "status": "RUNNING",
                "agentSnapshot": {"name": "Some Agent"},
            }
        )
        mock_ops.get_session_messages = AsyncMock(return_value=[])

        result = await operations_manager.describe_session(mock_context, "sess-002")

        assert isinstance(result, DescribeSessionResponse)
        assert result.status == "RUNNING"
        assert result.output is None
        assert result.messages == []

    @pytest.mark.asyncio
    async def test_describe_session_client_error(self, mock_context):
        """Test describe_session propagates client errors"""
        mock_ops = mock_context.request_context.lifespan_context.get.return_value.operations_manager
        mock_ops.get_session = AsyncMock(side_effect=Exception("Session not found"))

        with pytest.raises(Exception, match="Session not found"):
            await operations_manager.describe_session(mock_context, "bad-id")

    @pytest.mark.asyncio
    async def test_describe_session_no_output_message(self, mock_context):
        """Test describe_session with messages but no inference-succeeded event"""
        mock_ops = mock_context.request_context.lifespan_context.get.return_value.operations_manager
        mock_ops.get_session = AsyncMock(
            return_value={
                "sessionId": "sess-003",
                "status": "FAILED",
                "agentSnapshot": {"name": "Failing Agent"},
            }
        )
        mock_ops.get_session_messages = AsyncMock(
            return_value=[
                {"type": "agent-session-completed", "category": "AGENT_STATUS"},
            ]
        )

        result = await operations_manager.describe_session(mock_context, "sess-003")

        assert result.output is None


class TestTriggerAutomation:
    """Test the trigger_automation tool function"""

    @pytest.fixture
    def mock_context(self):
        ctx = MagicMock(spec=Context)
        ctx.info = AsyncMock()
        ctx.warning = AsyncMock()
        mock_client = MagicMock()
        mock_client.operations_manager = AsyncMock()
        ctx.request_context.lifespan_context.get.return_value = mock_client
        return ctx

    @pytest.mark.asyncio
    async def test_trigger_automation_workflow_response(self, mock_context):
        """Test trigger_automation returns StartWorkflowResponse for a workflow automation"""
        mock_ops = mock_context.request_context.lifespan_context.get.return_value.operations_manager
        mock_ops.start_workflow = AsyncMock(
            return_value={
                "_id": "job-ta-001",
                "name": "My Workflow",
                "description": None,
                "tasks": {},
                "status": "running",
                "metrics": {},
            }
        )
        mock_ops.get_workflows = AsyncMock(return_value=[])

        result = await operations_manager.trigger_automation(
            mock_context, "my-workflow-route", None
        )

        assert isinstance(result, StartWorkflowResponse)
        assert result.object_id == "job-ta-001"
        assert result.name == "My Workflow"
        assert result.status == "running"

    @pytest.mark.asyncio
    async def test_trigger_automation_agent_response(self, mock_context):
        """Test trigger_automation returns StartAgentResponse for an agent automation"""
        from itential_mcp.models.operations_manager import StartAgentResponse

        mock_ops = mock_context.request_context.lifespan_context.get.return_value.operations_manager
        mock_ops.start_workflow = AsyncMock(
            return_value={"sessionId": "sess-ta-001", "status": "RUNNING"}
        )
        mock_ops.get_workflows = AsyncMock(return_value=[])

        result = await operations_manager.trigger_automation(
            mock_context, "my-agent-route", {"input": "hello"}
        )

        assert isinstance(result, StartAgentResponse)
        assert result.session_id == "sess-ta-001"
        assert result.status == "RUNNING"

    @pytest.mark.asyncio
    async def test_trigger_automation_json_string_data(self, mock_context):
        """Test trigger_automation parses JSON string data before sending"""
        mock_ops = mock_context.request_context.lifespan_context.get.return_value.operations_manager
        mock_ops.start_workflow = AsyncMock(
            return_value={
                "_id": "job-ta-002",
                "name": "Workflow",
                "tasks": {},
                "status": "complete",
                "metrics": {},
            }
        )
        mock_ops.get_workflows = AsyncMock(return_value=[])

        result = await operations_manager.trigger_automation(
            mock_context, "route", '{"key": "value"}'
        )

        assert isinstance(result, StartWorkflowResponse)

    @pytest.mark.asyncio
    async def test_start_workflow_delegates_to_trigger_automation(self, mock_context):
        """Test start_workflow is a thin alias that delegates to trigger_automation"""
        from itential_mcp.models.operations_manager import StartAgentResponse

        mock_ops = mock_context.request_context.lifespan_context.get.return_value.operations_manager
        mock_ops.start_workflow = AsyncMock(
            return_value={"sessionId": "sess-alias-001", "status": "RUNNING"}
        )
        mock_ops.get_workflows = AsyncMock(return_value=[])

        result = await operations_manager.start_workflow(
            mock_context, "agent-route", None
        )

        assert isinstance(result, StartAgentResponse)
        assert result.session_id == "sess-alias-001"
        assert result.status == "RUNNING"


class TestGetAutomationsTool:
    """Test the get_automations tool function"""

    @pytest.fixture
    def mock_context(self):
        ctx = MagicMock(spec=Context)
        ctx.info = AsyncMock()
        mock_client = MagicMock()
        mock_client.operations_manager = AsyncMock()
        ctx.request_context.lifespan_context.get.return_value = mock_client
        return ctx

    @pytest.mark.asyncio
    async def test_get_automations_mixed_types(self, mock_context):
        """Test get_automations returns workflow and agent entries with correct types"""
        from itential_mcp.models.operations_manager import GetAutomationsResponse

        mock_ops = mock_context.request_context.lifespan_context.get.return_value.operations_manager
        mock_ops.get_automations = AsyncMock(
            return_value=[
                {
                    "name": "My Workflow",
                    "description": "A workflow",
                    "component_type": "workflows",
                    "component_id": "wf-id-001",
                    "route_name": "my_workflow",
                    "input_schema": {"type": "object"},
                    "last_executed": None,
                },
                {
                    "name": "JF Agent",
                    "description": "An agent",
                    "component_type": "agents",
                    "component_id": "agent-uuid-001",
                    "route_name": "jfagent",
                    "input_schema": None,
                    "last_executed": None,
                },
            ]
        )

        result = await operations_manager.get_automations(mock_context)

        assert isinstance(result, GetAutomationsResponse)
        assert len(result.root) == 2
        assert result.root[0].component_type == "workflows"
        assert result.root[0].route_name == "my_workflow"
        assert result.root[1].component_type == "agents"
        assert result.root[1].component_id == "agent-uuid-001"

    @pytest.mark.asyncio
    async def test_get_automations_no_endpoint_trigger(self, mock_context):
        """Test get_automations handles automations with no endpoint trigger (route_name None)"""
        from itential_mcp.models.operations_manager import GetAutomationsResponse

        mock_ops = mock_context.request_context.lifespan_context.get.return_value.operations_manager
        mock_ops.get_automations = AsyncMock(
            return_value=[
                {
                    "name": "Unexposed Automation",
                    "description": None,
                    "component_type": "workflows",
                    "component_id": "wf-id-002",
                    "route_name": None,
                    "input_schema": None,
                    "last_executed": None,
                },
            ]
        )

        result = await operations_manager.get_automations(mock_context)

        assert isinstance(result, GetAutomationsResponse)
        assert len(result.root) == 1
        assert result.root[0].route_name is None

    @pytest.mark.asyncio
    async def test_get_automations_empty(self, mock_context):
        """Test get_automations with no automations configured"""
        from itential_mcp.models.operations_manager import GetAutomationsResponse

        mock_ops = mock_context.request_context.lifespan_context.get.return_value.operations_manager
        mock_ops.get_automations = AsyncMock(return_value=[])

        result = await operations_manager.get_automations(mock_context)

        assert isinstance(result, GetAutomationsResponse)
        assert result.root == []

    @pytest.mark.asyncio
    async def test_get_automations_epoch_timestamp_converted(self, mock_context):
        """Test get_automations converts epoch last_executed to ISO 8601"""
        from itential_mcp.models.operations_manager import GetAutomationsResponse

        mock_ops = mock_context.request_context.lifespan_context.get.return_value.operations_manager
        mock_ops.get_automations = AsyncMock(
            return_value=[
                {
                    "name": "Timestamped Automation",
                    "description": None,
                    "component_type": "workflows",
                    "component_id": "wf-id-003",
                    "route_name": "ts_wf",
                    "input_schema": None,
                    "last_executed": 1640995200000,
                },
            ]
        )

        with patch(
            "itential_mcp.tools.operations_manager.timeutils.epoch_to_timestamp"
        ) as mock_ts:
            mock_ts.return_value = "2022-01-01T00:00:00Z"
            result = await operations_manager.get_automations(mock_context)

        assert isinstance(result, GetAutomationsResponse)
        assert result.root[0].last_executed == "2022-01-01T00:00:00Z"
        mock_ts.assert_called_once_with(1640995200000)
