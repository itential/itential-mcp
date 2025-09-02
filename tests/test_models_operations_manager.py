# Copyright (c) 2025 Itential, Inc
# GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)

import pytest
from pydantic import ValidationError

from itential_mcp.models.operations_manager import (
    WorkflowElement,
    GetWorkflowsResponse,
    JobMetrics,
    StartWorkflowResponse,
    JobElement,
    GetJobsResponse,
    DescribeJobResponse,
)


class TestWorkflowElement:
    """Test the WorkflowElement model"""

    def test_workflow_element_basic(self):
        """Test basic WorkflowElement creation"""
        element = WorkflowElement(
            _id="workflow-123",
            name="test-workflow",
            description="A test workflow",
            schema={"type": "object", "properties": {"input": {"type": "string"}}},
            route_name="test-route",
            last_executed="2025-01-01T00:00:00Z"
        )
        
        assert element.object_id == "workflow-123"
        assert element.name == "test-workflow"
        assert element.description == "A test workflow"
        assert element.input_schema == {"type": "object", "properties": {"input": {"type": "string"}}}
        assert element.route_name == "test-route"
        assert element.last_executed == "2025-01-01T00:00:00Z"

    def test_workflow_element_required_only(self):
        """Test WorkflowElement with required fields only"""
        element = WorkflowElement(
            _id="workflow-123",
            name="test-workflow"
        )
        
        assert element.object_id == "workflow-123"
        assert element.name == "test-workflow"
        assert element.description is None
        assert element.input_schema is None
        assert element.route_name is None
        assert element.last_executed is None

    def test_workflow_element_none_fields(self):
        """Test WorkflowElement with explicit None for optional fields"""
        element = WorkflowElement(
            _id="workflow-123",
            name="test-workflow",
            description=None,
            schema=None,
            route_name=None,
            last_executed=None
        )
        
        assert element.object_id == "workflow-123"
        assert element.name == "test-workflow"
        assert element.description is None
        assert element.input_schema is None
        assert element.route_name is None
        assert element.last_executed is None

    def test_workflow_element_missing_required_id(self):
        """Test WorkflowElement validation fails with missing _id"""
        with pytest.raises(ValidationError) as exc_info:
            WorkflowElement(name="test-workflow")
        
        errors = exc_info.value.errors()
        assert len(errors) == 1
        assert errors[0]["type"] == "missing"
        assert errors[0]["loc"] == ("_id",)

    def test_workflow_element_missing_required_name(self):
        """Test WorkflowElement validation fails with missing name"""
        with pytest.raises(ValidationError) as exc_info:
            WorkflowElement(_id="workflow-123")
        
        errors = exc_info.value.errors()
        assert len(errors) == 1
        assert errors[0]["type"] == "missing"
        assert errors[0]["loc"] == ("name",)

    def test_workflow_element_empty_string_values(self):
        """Test WorkflowElement with empty string values"""
        element = WorkflowElement(
            _id="",
            name="",
            description="",
            route_name="",
            last_executed=""
        )
        
        assert element.object_id == ""
        assert element.name == ""
        assert element.description == ""
        assert element.route_name == ""
        assert element.last_executed == ""


class TestGetWorkflowsResponse:
    """Test the GetWorkflowsResponse model"""

    def test_get_workflows_response_empty(self):
        """Test empty GetWorkflowsResponse"""
        response = GetWorkflowsResponse(root=[])
        
        assert response.root == []
        assert len(response.root) == 0

    def test_get_workflows_response_with_elements(self):
        """Test GetWorkflowsResponse with workflow elements"""
        element1 = WorkflowElement(
            _id="workflow-1", name="workflow-one"
        )
        element2 = WorkflowElement(
            _id="workflow-2", name="workflow-two", description="Second workflow"
        )
        
        response = GetWorkflowsResponse(root=[element1, element2])
        
        assert len(response.root) == 2
        assert response.root[0].object_id == "workflow-1"
        assert response.root[0].name == "workflow-one"
        assert response.root[1].object_id == "workflow-2"
        assert response.root[1].name == "workflow-two"
        assert response.root[1].description == "Second workflow"

    def test_get_workflows_response_default_factory(self):
        """Test GetWorkflowsResponse default factory creates empty list"""
        response = GetWorkflowsResponse()
        
        assert response.root == []
        assert len(response.root) == 0

    def test_get_workflows_response_iteration(self):
        """Test GetWorkflowsResponse can be iterated"""
        element1 = WorkflowElement(_id="workflow-1", name="workflow-one")
        element2 = WorkflowElement(_id="workflow-2", name="workflow-two")
        
        response = GetWorkflowsResponse(root=[element1, element2])
        
        workflows = list(response.root)
        assert len(workflows) == 2
        assert workflows[0].name == "workflow-one"
        assert workflows[1].name == "workflow-two"


class TestJobMetrics:
    """Test the JobMetrics model"""

    def test_job_metrics_all_fields(self):
        """Test JobMetrics with all fields"""
        metrics = JobMetrics(
            start_time="2025-01-01T10:00:00Z",
            end_time="2025-01-01T10:05:00Z",
            user="test-user"
        )
        
        assert metrics.start_time == "2025-01-01T10:00:00Z"
        assert metrics.end_time == "2025-01-01T10:05:00Z"
        assert metrics.user == "test-user"

    def test_job_metrics_empty(self):
        """Test JobMetrics with no fields"""
        metrics = JobMetrics()
        
        assert metrics.start_time is None
        assert metrics.end_time is None
        assert metrics.user is None

    def test_job_metrics_partial(self):
        """Test JobMetrics with some fields"""
        metrics = JobMetrics(
            start_time="2025-01-01T10:00:00Z",
            user="test-user"
        )
        
        assert metrics.start_time == "2025-01-01T10:00:00Z"
        assert metrics.end_time is None
        assert metrics.user == "test-user"

    def test_job_metrics_explicit_none(self):
        """Test JobMetrics with explicit None values"""
        metrics = JobMetrics(
            start_time=None,
            end_time=None,
            user=None
        )
        
        assert metrics.start_time is None
        assert metrics.end_time is None
        assert metrics.user is None


class TestStartWorkflowResponse:
    """Test the StartWorkflowResponse model"""

    def test_start_workflow_response_basic(self):
        """Test basic StartWorkflowResponse creation"""
        metrics = JobMetrics(
            start_time="2025-01-01T10:00:00Z",
            user="test-user"
        )
        
        response = StartWorkflowResponse(
            object_id="job-123",
            name="test-workflow",
            description="A test workflow",
            tasks={"task1": {"type": "action"}},
            status="running",
            metrics=metrics
        )
        
        assert response.object_id == "job-123"
        assert response.name == "test-workflow"
        assert response.description == "A test workflow"
        assert response.tasks == {"task1": {"type": "action"}}
        assert response.status == "running"
        assert response.metrics.start_time == "2025-01-01T10:00:00Z"
        assert response.metrics.user == "test-user"

    def test_start_workflow_response_required_only(self):
        """Test StartWorkflowResponse with required fields only"""
        metrics = JobMetrics()
        
        response = StartWorkflowResponse(
            object_id="job-123",
            name="test-workflow",
            tasks={},
            status="complete",
            metrics=metrics
        )
        
        assert response.object_id == "job-123"
        assert response.name == "test-workflow"
        assert response.description is None
        assert response.tasks == {}
        assert response.status == "complete"
        assert response.metrics.start_time is None

    def test_start_workflow_response_all_statuses(self):
        """Test StartWorkflowResponse with all valid status values"""
        metrics = JobMetrics()
        valid_statuses = ["error", "complete", "running", "canceled", "incomplete", "paused"]
        
        for status in valid_statuses:
            response = StartWorkflowResponse(
                object_id="job-123",
                name="test-workflow",
                tasks={},
                status=status,
                metrics=metrics
            )
            assert response.status == status

    def test_start_workflow_response_invalid_status(self):
        """Test StartWorkflowResponse validation fails with invalid status"""
        metrics = JobMetrics()
        
        with pytest.raises(ValidationError) as exc_info:
            StartWorkflowResponse(
                object_id="job-123",
                name="test-workflow",
                tasks={},
                status="invalid-status",
                metrics=metrics
            )
        
        errors = exc_info.value.errors()
        assert len(errors) == 1
        assert errors[0]["type"] == "literal_error"
        assert errors[0]["loc"] == ("status",)

    def test_start_workflow_response_missing_required_fields(self):
        """Test StartWorkflowResponse validation fails with missing required fields"""
        with pytest.raises(ValidationError) as exc_info:
            StartWorkflowResponse()
        
        errors = exc_info.value.errors()
        required_fields = {"object_id", "name", "tasks", "status", "metrics"}
        error_fields = {error["loc"][0] for error in errors}
        assert error_fields == required_fields

    def test_start_workflow_response_complex_tasks(self):
        """Test StartWorkflowResponse with complex tasks object"""
        metrics = JobMetrics()
        complex_tasks = {
            "task1": {
                "type": "automation",
                "app": "operations-manager",
                "data": {"key": "value"}
            },
            "task2": {
                "type": "manual",
                "description": "Manual approval step"
            }
        }
        
        response = StartWorkflowResponse(
            object_id="job-123",
            name="test-workflow",
            tasks=complex_tasks,
            status="running",
            metrics=metrics
        )
        
        assert response.tasks == complex_tasks
        assert "task1" in response.tasks
        assert "task2" in response.tasks
        assert response.tasks["task1"]["type"] == "automation"
        assert response.tasks["task2"]["type"] == "manual"


class TestJobElement:
    """Test the JobElement model"""

    def test_job_element_basic(self):
        """Test basic JobElement creation"""
        job = JobElement(
            _id="job-123",
            name="Test Job",
            description="A test job",
            status="running"
        )
        
        assert job.object_id == "job-123"
        assert job.name == "Test Job"
        assert job.description == "A test job"
        assert job.status == "running"

    def test_job_element_required_only(self):
        """Test JobElement with required fields only"""
        job = JobElement(
            _id="job-123",
            name="Test Job",
            status="complete"
        )
        
        assert job.object_id == "job-123"
        assert job.name == "Test Job"
        assert job.description is None
        assert job.status == "complete"


class TestGetJobsResponse:
    """Test the GetJobsResponse model"""

    def test_get_jobs_response_empty(self):
        """Test GetJobsResponse with no jobs"""
        response = GetJobsResponse(root=[])
        
        assert len(response.root) == 0
        assert list(response.root) == []

    def test_get_jobs_response_with_jobs(self):
        """Test GetJobsResponse with job elements"""
        job1 = JobElement(_id="job-1", name="Job One", status="complete")
        job2 = JobElement(_id="job-2", name="Job Two", status="running")
        
        response = GetJobsResponse(root=[job1, job2])
        
        assert len(response.root) == 2
        assert response.root[0].object_id == "job-1"
        assert response.root[1].object_id == "job-2"


class TestDescribeJobResponse:
    """Test the DescribeJobResponse model"""

    def test_describe_job_response_basic(self):
        """Test basic DescribeJobResponse creation"""
        job_detail = DescribeJobResponse(
            _id="job-123",
            name="Test Job",
            description="A detailed test job",
            type="automation",
            tasks={"task1": {"type": "action"}},
            status="complete",
            metrics={"start_time": 1640995200000},
            updated="2025-01-01T12:00:00Z"
        )
        
        assert job_detail.object_id == "job-123"
        assert job_detail.name == "Test Job"
        assert job_detail.description == "A detailed test job"
        assert job_detail.job_type == "automation"
        assert job_detail.status == "complete"
        assert job_detail.updated == "2025-01-01T12:00:00Z"
