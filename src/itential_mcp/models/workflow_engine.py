# Copyright (c) 2025 Itential, Inc
# GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import annotations

import inspect

from typing import Annotated, Any, Mapping

from pydantic import BaseModel, Field, RootModel


class JobMetricElement(BaseModel):
    """
    Represents a single job metric object from the Workflow Engine.

    This Pydantic model defines the structure for job metrics information returned
    from the Itential Platform workflow engine API endpoints. Job metrics provide
    comprehensive insights into automation efficiency, success rates, and resource
    utilization across workflow jobs, enabling performance monitoring and optimization.

    The model supports both camelCase field names (for API compatibility) and
    snake_case property access (for Python conventions) through Pydantic field aliases.

    Args:
        object_id: Unique identifier assigned by Itential Platform (API field: _id)
        workflow: The name or identifier of the workflow
        metrics: Dictionary containing job execution and performance metrics
        jobs_complete: Total number of successfully completed jobs (API field: jobsComplete)
        total_run_time: Cumulative execution time in seconds (API field: totalRunTime)

    Attributes:
        object_id (str): Unique identifier for the job metric record
        workflow (Mapping[str, str]): Workflow name or identifier information
        metrics (List[Mapping[str, Any]]): Performance and execution metrics data
        jobs_complete (int): Count of successfully completed jobs
        total_run_time (float): Total execution time in seconds across all job runs

    Notes:
        - Field aliases ensure compatibility with Itential Platform API responses
        - Serialization with by_alias=True preserves original API field names
        - Snake_case properties provide Pythonic access to the data
    """

    object_id: Annotated[
        str,
        Field(
            alias="_id",
            description=inspect.cleandoc(
                """
                The id assigned by Itential Platform
                """
            ),
        ),
    ]

    workflow: Annotated[
        Mapping[str, str] | None,
        Field(
            description=inspect.cleandoc(
                """
                The name of the workflow
                """
            ),
            default=None,
        ),
    ]

    metrics: Annotated[
        list[Mapping[str, Any]],
        Field(
            description=inspect.cleandoc(
                """
                The job metrics data
                """
            ),
        ),
    ]

    jobs_complete: Annotated[
        int,
        Field(
            alias="jobsComplete",
            description=inspect.cleandoc(
                """
                Number of completed jobs
                """
            ),
        ),
    ]

    total_run_time: Annotated[
        float,
        Field(
            alias="totalRunTime",
            description=inspect.cleandoc(
                """
                Cumulative run time in seconds
                """
            ),
        ),
    ]


class GetJobMetricsResponse(RootModel):
    """
    Response model for job metrics collection endpoints.

    This Pydantic RootModel provides a standardized response format for API endpoints
    that return collections of job metrics from the Itential Platform workflow engine.
    It wraps a list of JobMetricElement objects, enabling type-safe handling of
    job metrics data across the platform.

    The root model pattern allows the response to be treated as a list while
    maintaining proper validation and serialization capabilities for the contained
    job metric elements.

    Args:
        root: List of JobMetricElement objects containing job performance data.
            Defaults to an empty list if not provided.

    Attributes:
        root (List[JobMetricElement]): Collection of job metric elements with
            performance and completion statistics for workflow monitoring

    Example:
        Creating a response with multiple job metrics:

        >>> job1 = JobMetricElement(_id="job1", workflow="wf1", metrics=[],
        ...                        jobsComplete=10, totalRunTime=100.0)
        >>> job2 = JobMetricElement(_id="job2", workflow="wf2", metrics=[],
        ...                        jobsComplete=20, totalRunTime=250.5)
        >>> response = GetJobMetricsResponse([job1, job2])
        >>> print(len(response.root))  # 2
        >>> print(response.root[0].jobs_complete)  # 10

    Notes:
        - Uses default_factory=list to create empty collections when needed
        - Supports iteration and indexing through the root attribute
        - Maintains type safety for all contained JobMetricElement objects
    """

    root: Annotated[
        list[JobMetricElement],
        Field(
            description=inspect.cleandoc(
                """
                List of job metric objects with performance and completion statistics
                """
            ),
            default_factory=list,
        ),
    ]


class TaskMetricElement(BaseModel):
    """
    Represents a single task metric object from the Workflow Engine.

    This Pydantic model defines the structure for task-level metrics information
    returned from the Itential Platform workflow engine API endpoints. Task metrics
    provide granular insights into individual task performance, execution patterns,
    application usage, and resource utilization within workflow automation processes.

    The model supports both camelCase field names (for API compatibility) and
    snake_case property access (for Python conventions) through Pydantic field aliases.
    Several fields are optional to accommodate different API response variations.

    Args:
        object_id: Optional unique identifier assigned by Itential Platform (API field: _id)
        task_id: Optional task identifier within the workflow (API field: taskId)
        task_type: Type of task execution (API field: taskType)
        name: Human-readable task name
        metrics: Dictionary containing task execution and performance metrics
        app: Name of the application responsible for executing the task
        workflow: Optional workflow name or identifier information

    Attributes:
        object_id (str | None): Unique identifier for the task metric record
        task_id (str | None): Identifier of the task within its workflow context
        task_type (str): Task execution type ("automatic", "manual")
        name (str): Human-readable name of the task
        metrics (List[Mapping[str, Any]]): Performance and execution metrics data
        app (str): Application or service that executes this task
        workflow (Mapping[str, str] | None): Workflow information containing the task

    Example:
        Creating a TaskMetricElement from API response data:

        >>> task_data = {
        ...     "taskId": "task-456",
        ...     "taskType": "automatic",
        ...     "name": "deploy-config",
        ...     "metrics": [{"avg_time": 15.2, "success_rate": 0.98}],
        ...     "app": "config-manager",
        ...     "workflow": "deployment-pipeline"
        ... }
        >>> task_metric = TaskMetricElement(**task_data)
        >>> print(task_metric.task_id)  # "task-456"
        >>> print(task_metric.task_type)  # "automatic"

    Notes:
        - Field aliases ensure compatibility with Itential Platform API responses
        - Optional fields handle variations in API response structure
        - Serialization with by_alias=True preserves original API field names
        - Snake_case properties provide Pythonic access to the data
    """

    object_id: Annotated[
        str,
        Field(
            alias="_id",
            description=inspect.cleandoc(
                """
                The id assigned by Itential Platform
                """
            ),
            default=None,
        ),
    ]

    task_id: Annotated[
        str | None,
        Field(
            alias="taskId",
            description=inspect.cleandoc(
                """
                The task identifier in the workflow
                """
            ),
            default=None,
        ),
    ]

    task_type: Annotated[
        str,
        Field(
            alias="taskType",
            description=inspect.cleandoc(
                """
                Task type (automatic, manual)
                """
            ),
        ),
    ]

    name: Annotated[
        str,
        Field(
            description=inspect.cleandoc(
                """
                The name of the task
                """
            )
        ),
    ]

    metrics: Annotated[
        list[Mapping[str, Any]],
        Field(
            description=inspect.cleandoc(
                """
                The task metrics data
                """
            )
        ),
    ]

    app: Annotated[
        str,
        Field(
            description=inspect.cleandoc(
                """
                The application that runs the task
                """
            )
        ),
    ]

    workflow: Annotated[
        Mapping[str, str] | None,
        Field(
            description=inspect.cleandoc(
                """
                The name of the workflow the task is part of
                """
            ),
            default=None,
        ),
    ]


class GetTaskMetricsResponse(RootModel):
    """
    Response model for task metrics collection endpoints.

    This Pydantic RootModel provides a standardized response format for API endpoints
    that return collections of task-level metrics from the Itential Platform workflow
    engine. It wraps a list of TaskMetricElement objects, enabling type-safe handling
    of task performance data across automation workflows.

    The root model pattern allows the response to be treated as a list while
    maintaining proper validation and serialization capabilities for the contained
    task metric elements, supporting comprehensive workflow monitoring and analysis.

    Args:
        root: List of TaskMetricElement objects containing task performance data.
            Defaults to an empty list if not provided.

    Attributes:
        root (List[TaskMetricElement]): Collection of task metric elements with
            application usage patterns and execution statistics for workflow analysis

    Example:
        Creating a response with multiple task metrics:

        >>> task1 = TaskMetricElement(taskType="automatic", name="validate-config",
        ...                          metrics=[], app="validator")
        >>> task2 = TaskMetricElement(taskType="manual", name="approve-deploy",
        ...                          metrics=[], app="approval-service")
        >>> response = GetTaskMetricsResponse([task1, task2])
        >>> print(len(response.root))  # 2
        >>> print(response.root[0].task_type)  # "automatic"
        >>> print(response.root[1].name)  # "approve-deploy"

    Notes:
        - Uses default_factory=list to create empty collections when needed
        - Supports iteration and indexing through the root attribute
        - Maintains type safety for all contained TaskMetricElement objects
        - Enables filtering and analysis of tasks by application, workflow, or type
    """

    root: Annotated[
        list[TaskMetricElement],
        Field(
            description=inspect.cleandoc(
                """
                List of task metric objects with application usage and execution patterns
                """
            ),
            default_factory=list,
        ),
    ]
