# Copyright (c) 2025 Itential, Inc
# GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)

import inspect

from typing import Annotated, List, Literal, Mapping, Any

from pydantic import BaseModel, RootModel, Field


class WorkflowElement(BaseModel):
    """
    Represents a single workflow object from the operations manager.

    This model defines the structure for workflow information returned
    from the platform's operations manager API endpoints. Workflows are
    the core automation engine defining executable processes.

    Attributes:
        object_id: Unique identifier for the workflow.
        name: Workflow name (use this as the identifier for workflow operations).
        description: Workflow description.
        input_schema: Input schema for workflow parameters (JSON Schema draft-07 format).
        route_name: API route name for triggering the workflow (use with start_workflow).
        last_executed: ISO 8601 timestamp of last execution (null if never executed).
    """

    object_id: Annotated[
        str,
        Field(
            alias="_id",
            description = inspect.cleandoc(
                """
                Unique identifier for the workflow assiged by Itential Platform
                """
            )
        )
    ]

    name: Annotated[
        str,
        Field(
            description = inspect.cleandoc(
                """
                Workflow name (use this as the identifier for workflow operations)
                """
            )
        )
    ]

    description: Annotated[
        str | None,
        Field(
            description = inspect.cleandoc(
                """
                Workflow description
                """
            ),
            default = None
        )
    ]

    input_schema: Annotated[
        Mapping[str, Any] | None,
        Field(
            alias="schema",
            description = inspect.cleandoc(
                """
                Input schema for workflow parameters (JSON Schema draft-07 format)
                """
            ),
            default = None
        )
    ]

    route_name: Annotated[
        str | None,
        Field(
            description = inspect.cleandoc(
                """
                API route name for triggering the workflow (use with start_workflow)
                """
            ),
            default = None
        )
    ]

    last_executed: Annotated[
        str | None,
        Field(
            description = inspect.cleandoc(
                """
                ISO 8601 timestamp of last execution (null if never executed)
                """
            ),
            default = None
        )
    ]


class GetWorkflowsResponse(RootModel):
    """
    Response model for workflow collection endpoints.

    This root model wraps a list of workflow elements, providing a
    standardized response format for API endpoints that return multiple
    workflows from the operations manager.

    Attributes:
        root: A list of WorkflowElement objects representing all
            available workflows on the platform.
    """

    root: Annotated[
        List[WorkflowElement],
        Field(
            description = inspect.cleandoc(
                """
                List of workflow objects with workflow metadata and configuration
                """
            ),
            default_factory = list
        )
    ]


class JobMetrics(BaseModel):
    """
    Represents job execution metrics from workflow operations.

    This model captures timing and user information about workflow
    job execution for monitoring and auditing purposes.

    Attributes:
        start_time: The time when the job execution was started.
        end_time: The time when the job execution completed (if finished).
        user: Username of the user who initiated the job execution.
    """

    start_time: Annotated[
        str | None,
        Field(
            description = inspect.cleandoc(
                """
                The time when the job execution was started.
                """
            ),
            default = None
        )
    ]

    end_time: Annotated[
        str | None,
        Field(
            description = inspect.cleandoc(
                """
                The time when the job execution completed (if finished).
                """
            ),
            default = None
        )
    ]

    user: Annotated[
        str | None,
        Field(
            description = inspect.cleandoc(
                """
                Username of the user who initiated the job execution
                """
            ),
            default = None
        )
    ]


class StartWorkflowResponse(BaseModel):
    """
    Response model for workflow execution endpoints.

    This model represents the response returned when starting a workflow
    execution through the operations manager API. It contains job details
    that can be monitored for progress and results.

    Attributes:
        object_id: Unique job identifier (use with describe_job for monitoring).
        name: Workflow name that was executed.
        description: Workflow description.
        tasks: Complete set of tasks to be executed in the workflow.
        status: Current job status (error, complete, running, canceled, incomplete, paused).
        metrics: Job execution metrics including start_time, end_time, and user.
    """

    object_id: Annotated[
        str,
        Field(
            description = inspect.cleandoc(
                """
                Unique job identifier (use with describe_job for monitoring)
                """
            )
        )
    ]

    name: Annotated[
        str,
        Field(
            description = inspect.cleandoc(
                """
                Workflow name that was executed
                """
            )
        )
    ]

    description: Annotated[
        str | None,
        Field(
            description = inspect.cleandoc(
                """
                Workflow description
                """
            ),
            default = None
        )
    ]

    tasks: Annotated[
        Mapping[str, Any],
        Field(
            description = inspect.cleandoc(
                """
                Complete set of tasks to be executed in the workflow
                """
            )
        )
    ]

    status: Annotated[
        Literal["error", "complete", "running", "canceled", "incomplete", "paused"],
        Field(
            description = inspect.cleandoc(
                """
                Current job status (error, complete, running, canceled, incomplete, paused)
                """
            )
        )
    ]

    metrics: Annotated[
        JobMetrics,
        Field(
            description = inspect.cleandoc(
                """
                Job execution metrics including start_time, end_time, and user
                """
            )
        )
    ]


class JobElement(BaseModel):
    """
    Represents a single job object from the operations manager.

    This model defines the structure for job information returned
    from the platform's operations manager API endpoints. Jobs represent
    workflow execution instances that track status, progress, and results.

    Attributes:
        object_id: Unique job identifier.
        name: Job name.
        description: Job description.
        status: Current job status (error, complete, running, cancelled, incomplete, paused).
    """

    object_id: Annotated[
        str,
        Field(
            alias="_id",
            description = inspect.cleandoc(
                """
                Unique job identifier
                """
            )
        )
    ]

    name: Annotated[
        str,
        Field(
            description = inspect.cleandoc(
                """
                Job name
                """
            )
        )
    ]

    description: Annotated[
        str | None,
        Field(
            description = inspect.cleandoc(
                """
                Job description
                """
            ),
            default = None
        )
    ]

    status: Annotated[
        Literal["error", "complete", "running", "cancelled", "incomplete", "paused"],
        Field(
            description = inspect.cleandoc(
                """
                Current job status (error, complete, running, cancelled, incomplete, paused)
                """
            )
        )
    ]


class GetJobsResponse(RootModel):
    """
    Response model for job collection endpoints.

    This root model wraps a list of job elements, providing a
    standardized response format for API endpoints that return multiple
    jobs from the operations manager.

    Attributes:
        root: A list of JobElement objects representing all
            available jobs on the platform.
    """

    root: Annotated[
        List[JobElement],
        Field(
            description = inspect.cleandoc(
                """
                List of job objects with job metadata and status
                """
            ),
            default_factory = list
        )
    ]


class DescribeJobResponse(BaseModel):
    """
    Response model for job detail endpoints.

    This model represents detailed information about a specific job
    from the operations manager API, including comprehensive execution
    details, status, tasks, and metrics.

    Attributes:
        object_id: Unique job identifier.
        name: Job name.
        description: Job description.
        job_type: Job type (automation, resource:action, resource:compliance).
        tasks: Complete set of tasks executed.
        status: Current job status (error, complete, running, canceled, incomplete, paused).
        metrics: Job execution metrics including start time, end time, and account.
        updated: Last update timestamp.
    """

    object_id: Annotated[
        str,
        Field(
            alias="_id",
            description = inspect.cleandoc(
                """
                Unique job identifier
                """
            )
        )
    ]

    name: Annotated[
        str,
        Field(
            description = inspect.cleandoc(
                """
                Job name
                """
            )
        )
    ]

    description: Annotated[
        str | None,
        Field(
            description = inspect.cleandoc(
                """
                Job description
                """
            ),
            default = None
        )
    ]

    job_type: Annotated[
        str,
        Field(
            alias="type",
            description = inspect.cleandoc(
                """
                Job type (automation, resource:action, resource:compliance)
                """
            )
        )
    ]

    tasks: Annotated[
        Mapping[str, Any],
        Field(
            description = inspect.cleandoc(
                """
                Complete set of tasks executed
                """
            )
        )
    ]

    status: Annotated[
        Literal["error", "complete", "running", "canceled", "incomplete", "paused"],
        Field(
            description = inspect.cleandoc(
                """
                Current job status (error, complete, running, canceled,
                incomplete, paused)
                """
            )
        )
    ]

    metrics: Annotated[
        Mapping[str, Any],
        Field(
            description = inspect.cleandoc(
                """
                Job execution metrics including start time, end time, and account
                """
            )
        )
    ]

    updated: Annotated[
        str,
        Field(
            description = inspect.cleandoc(
                """
                Last update timestamp
                """
            )
        )
    ]

