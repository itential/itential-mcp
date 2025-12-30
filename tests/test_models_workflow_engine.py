# Copyright (c) 2025 Itential, Inc
# GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

import pytest
from pydantic import ValidationError

from itential_mcp.models.workflow_engine import (
    JobMetricElement,
    GetJobMetricsResponse,
    TaskMetricElement,
    GetTaskMetricsResponse,
)


class TestJobMetricElement:
    """Test the JobMetricElement model"""

    def test_job_metric_element_basic(self):
        """Test basic JobMetricElement creation"""
        element = JobMetricElement(
            _id="job-metric-123",
            workflow={"name": "test-workflow"},
            metrics=[{"total_runs": 100, "success_rate": 0.95}],
            jobsComplete=25,
            totalRunTime=3600.5,
        )

        assert element.object_id == "job-metric-123"
        assert element.workflow == {"name": "test-workflow"}
        assert element.metrics == [{"total_runs": 100, "success_rate": 0.95}]
        assert element.jobs_complete == 25
        assert element.total_run_time == 3600.5

    def test_job_metric_element_alias_mapping(self):
        """Test JobMetricElement field alias mapping"""
        # Test with original field names (what comes from API)
        data = {
            "_id": "job-metric-456",
            "workflow": {"name": "production-workflow"},
            "metrics": [{"avg_duration": 45.2}],
            "jobsComplete": 50,
            "totalRunTime": 7200.0,
        }

        element = JobMetricElement(**data)

        # Access via snake_case property names
        assert element.object_id == "job-metric-456"
        assert element.workflow == {"name": "production-workflow"}
        assert element.jobs_complete == 50
        assert element.total_run_time == 7200.0

    def test_job_metric_element_serialization_with_aliases(self):
        """Test JobMetricElement serialization preserves API field names"""
        element = JobMetricElement(
            _id="job-789",
            workflow={"name": "test-wf"},
            metrics=[{"key": "value"}],
            jobsComplete=10,
            totalRunTime=1800.0,
        )

        # Serialize with aliases (should match API format)
        serialized = element.model_dump(by_alias=True)

        assert "_id" in serialized
        assert serialized["_id"] == "job-789"
        assert "jobsComplete" in serialized
        assert serialized["jobsComplete"] == 10
        assert "totalRunTime" in serialized
        assert serialized["totalRunTime"] == 1800.0

    def test_job_metric_element_serialization_without_aliases(self):
        """Test JobMetricElement serialization with snake_case field names"""
        element = JobMetricElement(
            _id="job-789",
            workflow={"name": "test-wf"},
            metrics=[{"key": "value"}],
            jobsComplete=10,
            totalRunTime=1800.0,
        )

        # Serialize without aliases (should use snake_case)
        serialized = element.model_dump(by_alias=False)

        assert "object_id" in serialized
        assert serialized["object_id"] == "job-789"
        assert "jobs_complete" in serialized
        assert serialized["jobs_complete"] == 10
        assert "total_run_time" in serialized
        assert serialized["total_run_time"] == 1800.0

    def test_job_metric_element_missing_required_fields(self):
        """Test JobMetricElement validation fails with missing required fields"""
        with pytest.raises(ValidationError) as exc_info:
            JobMetricElement()

        errors = exc_info.value.errors()
        # workflow is optional (has default=None), so only these fields are required
        required_fields = {"_id", "metrics", "jobsComplete", "totalRunTime"}
        error_fields = {error["loc"][0] for error in errors}
        assert error_fields == required_fields

    def test_job_metric_element_invalid_types(self):
        """Test JobMetricElement validation fails with invalid types"""
        with pytest.raises(ValidationError) as exc_info:
            JobMetricElement(
                _id=123,  # Should be string
                workflow="test-workflow",  # Should be dict/mapping
                metrics="not-a-list",  # Should be list
                jobsComplete="not-an-int",  # Should be int
                totalRunTime="not-a-float",  # Should be float
            )

        errors = exc_info.value.errors()
        assert len(errors) >= 4  # At least 4 type errors

    def test_job_metric_element_complex_metrics(self):
        """Test JobMetricElement with complex metrics object"""
        complex_metrics = [
            {
                "execution_stats": {
                    "total_runs": 150,
                    "successful_runs": 145,
                    "failed_runs": 5,
                },
                "performance": {
                    "avg_duration_ms": 2500.5,
                    "min_duration_ms": 1200.0,
                    "max_duration_ms": 4800.3,
                },
                "resource_usage": {"cpu_avg": 0.65, "memory_peak_mb": 512},
            }
        ]

        element = JobMetricElement(
            _id="complex-job-123",
            workflow={"name": "complex-workflow"},
            metrics=complex_metrics,
            jobsComplete=150,
            totalRunTime=15000.75,
        )

        assert element.metrics == complex_metrics
        assert element.metrics[0]["execution_stats"]["total_runs"] == 150
        assert element.metrics[0]["performance"]["avg_duration_ms"] == 2500.5

    def test_job_metric_element_numeric_edge_cases(self):
        """Test JobMetricElement with numeric edge cases"""
        element = JobMetricElement(
            _id="edge-case-job",
            workflow={"name": "edge-workflow"},
            metrics=[],
            jobsComplete=0,  # Zero jobs complete
            totalRunTime=0.0,  # Zero run time
        )

        assert element.jobs_complete == 0
        assert element.total_run_time == 0.0
        assert element.metrics == []

    def test_job_metric_element_large_numbers(self):
        """Test JobMetricElement with large numbers"""
        element = JobMetricElement(
            _id="large-numbers-job",
            workflow={"name": "high-volume-workflow"},
            metrics=[{"processed_items": 1000000}],
            jobsComplete=999999,
            totalRunTime=86400.999,  # ~24 hours
        )

        assert element.jobs_complete == 999999
        assert element.total_run_time == 86400.999


class TestGetJobMetricsResponse:
    """Test the GetJobMetricsResponse model"""

    def test_get_job_metrics_response_empty(self):
        """Test empty GetJobMetricsResponse"""
        response = GetJobMetricsResponse(root=[])

        assert response.root == []
        assert len(response.root) == 0

    def test_get_job_metrics_response_with_elements(self):
        """Test GetJobMetricsResponse with job metric elements"""
        element1 = JobMetricElement(
            _id="job-1",
            workflow={"name": "workflow-one"},
            metrics=[{"runs": 10}],
            jobsComplete=5,
            totalRunTime=100.0,
        )
        element2 = JobMetricElement(
            _id="job-2",
            workflow={"name": "workflow-two"},
            metrics=[{"runs": 20}],
            jobsComplete=15,
            totalRunTime=300.5,
        )

        response = GetJobMetricsResponse(root=[element1, element2])

        assert len(response.root) == 2
        assert response.root[0].object_id == "job-1"
        assert response.root[0].workflow == {"name": "workflow-one"}
        assert response.root[1].object_id == "job-2"
        assert response.root[1].workflow == {"name": "workflow-two"}

    def test_get_job_metrics_response_default_factory(self):
        """Test GetJobMetricsResponse default factory creates empty list"""
        response = GetJobMetricsResponse()

        assert response.root == []
        assert len(response.root) == 0

    def test_get_job_metrics_response_iteration(self):
        """Test GetJobMetricsResponse can be iterated"""
        element1 = JobMetricElement(
            _id="iter-job-1",
            workflow={"name": "iter-workflow-1"},
            metrics=[],
            jobsComplete=1,
            totalRunTime=10.0,
        )
        element2 = JobMetricElement(
            _id="iter-job-2",
            workflow={"name": "iter-workflow-2"},
            metrics=[],
            jobsComplete=2,
            totalRunTime=20.0,
        )

        response = GetJobMetricsResponse(root=[element1, element2])

        job_metrics = list(response.root)
        assert len(job_metrics) == 2
        assert job_metrics[0].object_id == "iter-job-1"
        assert job_metrics[1].object_id == "iter-job-2"

    def test_get_job_metrics_response_single_element(self):
        """Test GetJobMetricsResponse with single element"""
        element = JobMetricElement(
            _id="single-job",
            workflow={"name": "single-workflow"},
            metrics=[{"test": "data"}],
            jobsComplete=1,
            totalRunTime=5.5,
        )

        response = GetJobMetricsResponse(root=[element])

        assert len(response.root) == 1
        assert response.root[0].object_id == "single-job"

    def test_get_job_metrics_response_large_list(self):
        """Test GetJobMetricsResponse with many elements"""
        elements = []
        for i in range(100):
            element = JobMetricElement(
                _id=f"job-{i}",
                workflow={"name": f"workflow-{i}"},
                metrics=[{"index": i}],
                jobsComplete=i,
                totalRunTime=float(i * 10),
            )
            elements.append(element)

        response = GetJobMetricsResponse(root=elements)

        assert len(response.root) == 100
        assert response.root[0].object_id == "job-0"
        assert response.root[99].object_id == "job-99"
        assert response.root[50].jobs_complete == 50


class TestTaskMetricElement:
    """Test the TaskMetricElement model"""

    def test_task_metric_element_basic(self):
        """Test basic TaskMetricElement creation"""
        element = TaskMetricElement(
            taskId="task-123",
            taskType="automatic",
            name="test-task",
            metrics=[{"execution_count": 50, "avg_time": 2.5}],
            app="test-app",
            workflow={"name": "test-workflow"},
        )

        assert element.task_id == "task-123"
        assert element.task_type == "automatic"
        assert element.name == "test-task"
        assert element.metrics == [{"execution_count": 50, "avg_time": 2.5}]
        assert element.app == "test-app"
        assert element.workflow == {"name": "test-workflow"}

    def test_task_metric_element_alias_mapping(self):
        """Test TaskMetricElement field alias mapping"""
        # Test with original field names (what comes from API)
        data = {
            "taskId": "task-456",
            "taskType": "manual",
            "name": "approval-task",
            "metrics": [{"pending_time": 3600.0}],
            "app": "approval-app",
            "workflow": {"name": "approval-workflow"},
        }

        element = TaskMetricElement(**data)

        # Access via snake_case property names
        assert element.task_id == "task-456"
        assert element.task_type == "manual"
        assert element.name == "approval-task"
        assert element.app == "approval-app"
        assert element.workflow == {"name": "approval-workflow"}

    def test_task_metric_element_serialization_with_aliases(self):
        """Test TaskMetricElement serialization preserves API field names"""
        element = TaskMetricElement(
            taskId="task-789",
            taskType="automatic",
            name="serialize-task",
            metrics=[{"key": "value"}],
            app="serialize-app",
            workflow={"name": "serialize-workflow"},
        )

        # Serialize with aliases (should match API format)
        serialized = element.model_dump(by_alias=True)

        assert "taskId" in serialized
        assert serialized["taskId"] == "task-789"
        assert "taskType" in serialized
        assert serialized["taskType"] == "automatic"

    def test_task_metric_element_serialization_without_aliases(self):
        """Test TaskMetricElement serialization with snake_case field names"""
        element = TaskMetricElement(
            taskId="task-789",
            taskType="automatic",
            name="serialize-task",
            metrics=[{"key": "value"}],
            app="serialize-app",
            workflow={"name": "serialize-workflow"},
        )

        # Serialize without aliases (should use snake_case)
        serialized = element.model_dump(by_alias=False)

        assert "task_id" in serialized
        assert serialized["task_id"] == "task-789"
        assert "task_type" in serialized
        assert serialized["task_type"] == "automatic"

    def test_task_metric_element_task_types(self):
        """Test TaskMetricElement with different task types"""
        task_types = ["automatic", "manual"]

        for task_type in task_types:
            element = TaskMetricElement(
                taskId=f"task-{task_type}",
                taskType=task_type,
                name=f"{task_type}-task",
                metrics=[],
                app="test-app",
                workflow={"name": "test-workflow"},
            )
            assert element.task_type == task_type

    def test_task_metric_element_missing_required_fields(self):
        """Test TaskMetricElement validation fails with missing required fields"""
        with pytest.raises(ValidationError) as exc_info:
            TaskMetricElement()

        errors = exc_info.value.errors()
        # taskId, workflow, and object_id are optional (have default=None), so only these fields are required
        required_fields = {"taskType", "name", "metrics", "app"}
        error_fields = {error["loc"][0] for error in errors}
        assert error_fields == required_fields

    def test_task_metric_element_invalid_types(self):
        """Test TaskMetricElement validation fails with invalid types"""
        with pytest.raises(ValidationError) as exc_info:
            TaskMetricElement(
                taskId=123,  # Should be string
                taskType=456,  # Should be string
                name=789,  # Should be string
                metrics="not-a-list",  # Should be list
                app=101112,  # Should be string
                workflow=131415,  # Should be dict/mapping
            )

        errors = exc_info.value.errors()
        assert len(errors) >= 6  # At least 6 type errors

    def test_task_metric_element_complex_metrics(self):
        """Test TaskMetricElement with complex metrics object"""
        complex_metrics = [
            {
                "timing": {
                    "total_executions": 100,
                    "avg_duration_ms": 1500.5,
                    "percentiles": {"p50": 1200.0, "p95": 2800.0, "p99": 4500.0},
                },
                "success_rate": 0.98,
                "error_categories": {"timeout": 1, "connection_error": 1},
            }
        ]

        element = TaskMetricElement(
            taskId="complex-task-123",
            taskType="automatic",
            name="data-processing-task",
            metrics=complex_metrics,
            app="data-processor",
            workflow={"name": "etl-pipeline"},
        )

        assert element.metrics == complex_metrics
        assert element.metrics[0]["timing"]["total_executions"] == 100
        assert element.metrics[0]["success_rate"] == 0.98

    def test_task_metric_element_empty_metrics(self):
        """Test TaskMetricElement with empty metrics"""
        element = TaskMetricElement(
            taskId="empty-metrics-task",
            taskType="manual",
            name="empty-task",
            metrics=[],
            app="test-app",
            workflow={"name": "test-workflow"},
        )

        assert element.metrics == []

    def test_task_metric_element_long_names(self):
        """Test TaskMetricElement with long names and identifiers"""
        long_name = "very_long_task_name_that_exceeds_typical_lengths_" * 3
        long_app = "application_with_very_long_name_for_testing_purposes"
        long_workflow = "workflow_name_that_is_extremely_long_and_descriptive"

        element = TaskMetricElement(
            taskId="long-id-task-123456789",
            taskType="automatic",
            name=long_name,
            metrics=[{"test": "data"}],
            app=long_app,
            workflow={"name": long_workflow},
        )

        assert element.name == long_name
        assert element.app == long_app
        assert element.workflow == {"name": long_workflow}


class TestGetTaskMetricsResponse:
    """Test the GetTaskMetricsResponse model"""

    def test_get_task_metrics_response_empty(self):
        """Test empty GetTaskMetricsResponse"""
        response = GetTaskMetricsResponse(root=[])

        assert response.root == []
        assert len(response.root) == 0

    def test_get_task_metrics_response_with_elements(self):
        """Test GetTaskMetricsResponse with task metric elements"""
        element1 = TaskMetricElement(
            taskId="task-1",
            taskType="automatic",
            name="first-task",
            metrics=[{"count": 5}],
            app="app1",
            workflow={"name": "workflow1"},
        )
        element2 = TaskMetricElement(
            taskId="task-2",
            taskType="manual",
            name="second-task",
            metrics=[{"count": 10}],
            app="app2",
            workflow={"name": "workflow2"},
        )

        response = GetTaskMetricsResponse(root=[element1, element2])

        assert len(response.root) == 2
        assert response.root[0].task_id == "task-1"
        assert response.root[0].task_type == "automatic"
        assert response.root[1].task_id == "task-2"
        assert response.root[1].task_type == "manual"

    def test_get_task_metrics_response_default_factory(self):
        """Test GetTaskMetricsResponse default factory creates empty list"""
        response = GetTaskMetricsResponse()

        assert response.root == []
        assert len(response.root) == 0

    def test_get_task_metrics_response_iteration(self):
        """Test GetTaskMetricsResponse can be iterated"""
        element1 = TaskMetricElement(
            taskId="iter-task-1",
            taskType="automatic",
            name="iter-task-1",
            metrics=[],
            app="iter-app-1",
            workflow={"name": "iter-workflow-1"},
        )
        element2 = TaskMetricElement(
            taskId="iter-task-2",
            taskType="manual",
            name="iter-task-2",
            metrics=[],
            app="iter-app-2",
            workflow={"name": "iter-workflow-2"},
        )

        response = GetTaskMetricsResponse(root=[element1, element2])

        task_metrics = list(response.root)
        assert len(task_metrics) == 2
        assert task_metrics[0].task_id == "iter-task-1"
        assert task_metrics[1].task_id == "iter-task-2"

    def test_get_task_metrics_response_mixed_task_types(self):
        """Test GetTaskMetricsResponse with mixed task types"""
        automatic_task = TaskMetricElement(
            taskId="auto-task",
            taskType="automatic",
            name="automated-process",
            metrics=[{"automated": True}],
            app="automation-engine",
            workflow={"name": "auto-workflow"},
        )
        manual_task = TaskMetricElement(
            taskId="manual-task",
            taskType="manual",
            name="manual-review",
            metrics=[{"manual": True}],
            app="review-app",
            workflow={"name": "review-workflow"},
        )

        response = GetTaskMetricsResponse(root=[automatic_task, manual_task])

        assert len(response.root) == 2
        assert response.root[0].task_type == "automatic"
        assert response.root[1].task_type == "manual"

    def test_get_task_metrics_response_same_workflow_different_apps(self):
        """Test GetTaskMetricsResponse with tasks from same workflow, different apps"""
        task1 = TaskMetricElement(
            taskId="task-1",
            taskType="automatic",
            name="preprocess",
            metrics=[{"step": 1}],
            app="preprocessor",
            workflow={"name": "data-pipeline"},
        )
        task2 = TaskMetricElement(
            taskId="task-2",
            taskType="automatic",
            name="transform",
            metrics=[{"step": 2}],
            app="transformer",
            workflow={"name": "data-pipeline"},
        )
        task3 = TaskMetricElement(
            taskId="task-3",
            taskType="automatic",
            name="load",
            metrics=[{"step": 3}],
            app="loader",
            workflow={"name": "data-pipeline"},
        )

        response = GetTaskMetricsResponse(root=[task1, task2, task3])

        assert len(response.root) == 3
        # All tasks should be from same workflow
        assert all(task.workflow == {"name": "data-pipeline"} for task in response.root)
        # But different apps
        apps = [task.app for task in response.root]
        assert apps == ["preprocessor", "transformer", "loader"]

    def test_get_task_metrics_response_large_list(self):
        """Test GetTaskMetricsResponse with many elements"""
        elements = []
        for i in range(50):
            element = TaskMetricElement(
                taskId=f"bulk-task-{i}",
                taskType="automatic" if i % 2 == 0 else "manual",
                name=f"bulk-operation-{i}",
                metrics=[{"index": i, "batch": i // 10}],
                app=f"app-{i % 5}",  # 5 different apps
                workflow={"name": f"workflow-{i % 3}"},  # 3 different workflows
            )
            elements.append(element)

        response = GetTaskMetricsResponse(root=elements)

        assert len(response.root) == 50
        assert response.root[0].task_id == "bulk-task-0"
        assert response.root[49].task_id == "bulk-task-49"

        # Check distribution of task types
        automatic_count = sum(
            1 for task in response.root if task.task_type == "automatic"
        )
        manual_count = sum(1 for task in response.root if task.task_type == "manual")
        assert automatic_count == 25
        assert manual_count == 25
