# Copyright (c) 2025 Itential, Inc
# GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import annotations

import inspect

from typing import Annotated, Any, Mapping

from pydantic import BaseModel, Field

from itential_mcp.models.base import AliasedModel


class JobMetricElement(AliasedModel):
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


class GetJobMetricsResponse(BaseModel):
    """
    Response model for job metrics collection endpoints.

    This Pydantic model provides a paginated response format for tools that
    return job-level metrics from the Itential Platform workflow engine. It
    wraps one page of JobMetricElement objects together with pagination metadata so
    callers can tell whether more results exist and how to request them.

    Args:
        results: List of JobMetricElement objects in this page. Defaults to an empty list.
        total: Total number of matching items available on the platform.
        returned: Number of items in this page.
        limit: The maximum number of items requested for this page.
        skip: The number of items skipped before this page.
        has_more: Whether more items exist beyond this page
            (skip + returned < total).

    Attributes:
        results (list[JobMetricElement]): The page of job metric elements
        total (int): Total number of matching items on the platform
        returned (int): Number of items in this page
        limit (int): Page size that was requested
        skip (int): Offset of this page
        has_more (bool): True when skip + returned < total

    Example:
        >>> job1 = JobMetricElement(_id="job1", workflow=None, metrics=[],
        ...                        jobsComplete=10, totalRunTime=100.0)
        >>> response = GetJobMetricsResponse(
        ...     results=[job1], total=250, returned=1, limit=1, skip=0, has_more=True
        ... )
        >>> print(len(response.results))  # 1
        >>> print(response.results[0].jobs_complete)  # 10
        >>> print(response.has_more)  # True

    Notes:
        - Use skip=skip + returned on the next call to retrieve the next page
        - Field names are plain (no aliases) so serialization matches the schema
    """

    results: Annotated[
        list[JobMetricElement],
        Field(
            description=inspect.cleandoc(
                """
                The job metric objects in this page, with performance and execution statistics
                """
            ),
            default_factory=list,
        ),
    ]

    total: Annotated[
        int,
        Field(
            description=inspect.cleandoc(
                """
                Total number of job metrics available on the platform for the query, across all pages
                """
            ),
            default=0,
        ),
    ]

    returned: Annotated[
        int,
        Field(
            description=inspect.cleandoc(
                """
                Number of items in results for this page
                """
            ),
            default=0,
        ),
    ]

    limit: Annotated[
        int,
        Field(
            description=inspect.cleandoc(
                """
                The maximum number of items requested for this page
                """
            ),
            default=0,
        ),
    ]

    skip: Annotated[
        int,
        Field(
            description=inspect.cleandoc(
                """
                The number of items skipped before this page
                """
            ),
            default=0,
        ),
    ]

    has_more: Annotated[
        bool,
        Field(
            description=inspect.cleandoc(
                """
                True when more items exist beyond this page. Call again with skip increased by returned to retrieve the next page
                """
            ),
            default=False,
        ),
    ]


class TaskMetricElement(AliasedModel):
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
        app (str | None): Application or service that executes this task
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
        str | None,
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
        str | None,
        Field(
            description=inspect.cleandoc(
                """
                The application that runs the task
                """
            ),
            default=None,
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


class GetTaskMetricsResponse(BaseModel):
    """
    Response model for task metrics collection endpoints.

    This Pydantic model provides a paginated response format for tools that
    return task-level metrics from the Itential Platform workflow engine. It
    wraps one page of TaskMetricElement objects together with pagination metadata so
    callers can tell whether more results exist and how to request them.

    Args:
        results: List of TaskMetricElement objects in this page. Defaults to an empty list.
        total: Total number of matching items available on the platform.
        returned: Number of items in this page.
        limit: The maximum number of items requested for this page.
        skip: The number of items skipped before this page.
        has_more: Whether more items exist beyond this page
            (skip + returned < total).

    Attributes:
        results (list[TaskMetricElement]): The page of task metric elements
        total (int): Total number of matching items on the platform
        returned (int): Number of items in this page
        limit (int): Page size that was requested
        skip (int): Offset of this page
        has_more (bool): True when skip + returned < total

    Example:
        >>> task1 = TaskMetricElement(taskType="automatic", name="validate-config",
        ...                          metrics=[], app="validator")
        >>> response = GetTaskMetricsResponse(
        ...     results=[task1], total=1, returned=1, limit=200, skip=0, has_more=False
        ... )
        >>> print(len(response.results))  # 1
        >>> print(response.results[0].task_type)  # "automatic"
        >>> print(response.has_more)  # False

    Notes:
        - Use skip=skip + returned on the next call to retrieve the next page
        - Field names are plain (no aliases) so serialization matches the schema
    """

    results: Annotated[
        list[TaskMetricElement],
        Field(
            description=inspect.cleandoc(
                """
                The task metric objects in this page, with performance and execution statistics
                """
            ),
            default_factory=list,
        ),
    ]

    total: Annotated[
        int,
        Field(
            description=inspect.cleandoc(
                """
                Total number of task metrics available on the platform for the query, across all pages
                """
            ),
            default=0,
        ),
    ]

    returned: Annotated[
        int,
        Field(
            description=inspect.cleandoc(
                """
                Number of items in results for this page
                """
            ),
            default=0,
        ),
    ]

    limit: Annotated[
        int,
        Field(
            description=inspect.cleandoc(
                """
                The maximum number of items requested for this page
                """
            ),
            default=0,
        ),
    ]

    skip: Annotated[
        int,
        Field(
            description=inspect.cleandoc(
                """
                The number of items skipped before this page
                """
            ),
            default=0,
        ),
    ]

    has_more: Annotated[
        bool,
        Field(
            description=inspect.cleandoc(
                """
                True when more items exist beyond this page. Call again with skip increased by returned to retrieve the next page
                """
            ),
            default=False,
        ),
    ]
