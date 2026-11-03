# Copyright (c) 2025 Itential, Inc
# GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import annotations

from typing import Annotated, Any

from pydantic import Field

from fastmcp import Context

from itential_mcp.models import workflow_engine as models
from itential_mcp.utilities.tool import annotate


__tags__ = ("workflow_engine",)


async def _get_job_metrics(
    ctx: Context,
    params: dict[str, Any] | None = None,
    *,
    limit: int = 200,
    skip: int = 0,
) -> models.GetJobMetricsResponse:
    """
    Internal helper to get aggregate job metrics from the Workflow Engine.

    This private function handles the actual API call to retrieve job metrics
    from the workflow engine service. It supports optional filtering parameters
    to narrow the results.

    Args:
        ctx (Context): The FastMCP Context object for accessing the platform client
        params (dict[str, Any] | None): Optional query parameters to filter job metrics.
            Common filters include workflow name, date ranges, or execution status.
            If None, all job metrics are eligible.
        limit (int): Maximum number of items to return. Defaults to 200.
        skip (int): Number of items to skip before the page starts. Defaults to 0.

    Returns:
        GetJobMetricsResponse: Response containing one page of job metrics with the following fields:
            - results: The job metric elements in this page. Each element has:
                - _id: The id assigned by Itential Platform
                - workflow: The name of the workflow
                - metrics: The job metrics data
                - jobsComplete: Number of completed jobs
                - totalRunTime: Cumulative run time in seconds
            - total: Total number of matching items on the platform
            - returned: Number of items in this page
            - limit: The page size that was requested
            - skip: The number of items skipped
            - has_more: True if more items exist beyond this page

    Raises:
        Exception: If there is an error retrieving job metrics from the platform
    """
    await ctx.debug("inside _get_job_metrics(...)")

    client = ctx.request_context.lifespan_context.get("client")
    items, total = await client.workflow_engine.get_job_metrics(
        params=params, limit=limit, skip=skip
    )
    return models.GetJobMetricsResponse(
        results=items,
        total=total,
        returned=len(items),
        limit=limit,
        skip=skip,
        has_more=skip + len(items) < total,
    )


@annotate(read_only=True, idempotent=True, open_world=False, title="Get Job Metrics")
async def get_job_metrics(
    ctx: Annotated[Context, Field(description="The FastMCP Context object")],
    *,
    limit: Annotated[
        int,
        Field(
            description="Maximum number of items to return (1-1000, default 200)",
            ge=1,
            le=1000,
        ),
    ] = 200,
    skip: Annotated[
        int,
        Field(
            description="Number of items to skip, used to page through large result sets",
            ge=0,
        ),
    ] = 0,
) -> models.GetJobMetricsResponse:
    """
    Get aggregate job metrics from the Workflow Engine.

    The Workflow Engine maintains comprehensive metrics about workflow execution
    performance, providing insights into automation efficiency, success rates,
    and resource utilization across all workflow jobs.

    Args:
        ctx (Context): The FastMCP Context object
        limit (int): Maximum number of items to return (1-1000). Defaults to 200.
        skip (int): Number of items to skip before the page starts. Defaults to 0.

    Returns:
        GetJobMetricsResponse: Response containing one page of job metrics with the following fields:
            - results: The job metric elements in this page. Each element has:
                - _id: The id assigned by Itential Platform
                - workflow: The name of the workflow
                - metrics: The job metrics data
                - jobsComplete: Number of completed jobs
                - totalRunTime: Cumulative run time in seconds
            - total: Total number of matching items on the platform
            - returned: Number of items in this page
            - limit: The page size that was requested
            - skip: The number of items skipped
            - has_more: True if more items exist beyond this page

    Raises:
        Exception: If there is an error retrieving job metrics from the platform
    """
    return await _get_job_metrics(ctx, limit=limit, skip=skip)


@annotate(
    read_only=True,
    idempotent=True,
    open_world=False,
    title="Get Job Metrics for Workflow",
)
async def get_job_metrics_for_workflow(
    ctx: Annotated[Context, Field(description="The FastMCP Context object")],
    name: Annotated[
        str, Field(description="The name of the workflow to get the job metrics for")
    ],
    *,
    limit: Annotated[
        int,
        Field(
            description="Maximum number of items to return (1-1000, default 200)",
            ge=1,
            le=1000,
        ),
    ] = 200,
    skip: Annotated[
        int,
        Field(
            description="Number of items to skip, used to page through large result sets",
            ge=0,
        ),
    ] = 0,
) -> models.GetJobMetricsResponse:
    """
    Get the job metrics for the specified workflow from Workflow Engine.

    Retrieves job execution metrics filtered by a specific workflow name,
    providing targeted insights into the performance and execution statistics
    for jobs within that particular workflow.

    Args:
        ctx (Context): The FastMCP Context object
        name (str): The name of the workflow to retrieve job metrics for
        limit (int): Maximum number of items to return (1-1000). Defaults to 200.
        skip (int): Number of items to skip before the page starts. Defaults to 0.

    Returns:
        GetJobMetricsResponse: Response containing one page of job metrics with the following fields:
            - results: The job metric elements in this page. Each element has:
                - _id: The id assigned by Itential Platform
                - workflow: The name of the workflow
                - metrics: The job metrics data
                - jobsComplete: Number of completed jobs
                - totalRunTime: Cumulative run time in seconds
            - total: Total number of matching items on the platform
            - returned: Number of items in this page
            - limit: The page size that was requested
            - skip: The number of items skipped
            - has_more: True if more items exist beyond this page

    Raises:
        Exception: If there is an error retrieving job metrics from the platform

    Notes:
        - The name argument is case sensitive
    """
    return await _get_job_metrics(
        ctx,
        params={"containsField": "workflow.name", "contains": name},
        limit=limit,
        skip=skip,
    )


async def _get_task_metrics(
    ctx: Context,
    params: dict[str, Any] | None = None,
    *,
    limit: int = 200,
    skip: int = 0,
) -> models.GetTaskMetricsResponse:
    """
    Internal helper to get aggregate task metrics from the Workflow Engine.

    The Workflow Engine tracks detailed task-level metrics within workflows,
    providing granular insights into individual task performance, application
    usage, and execution patterns across automation operations.

    Args:
        ctx (Context): The FastMCP Context object for accessing the platform client
        params (dict[str, Any] | None): Optional query parameters to filter task metrics.
            Common filters include task name, application name, workflow name,
            or task type. If None, all task metrics are eligible.
        limit (int): Maximum number of items to return. Defaults to 200.
        skip (int): Number of items to skip before the page starts. Defaults to 0.

    Returns:
        GetTaskMetricsResponse: Response containing one page of task metrics with the following fields:
            - results: The task metric elements in this page. Each element has:
                - taskId: The task identifier in the workflow
                - taskType: Task type (automatic, manual)
                - name: The name of the task
                - metrics: The task metrics data
                - app: The application that runs the task
                - workflow: The name of the workflow the task is part of
            - total: Total number of matching items on the platform
            - returned: Number of items in this page
            - limit: The page size that was requested
            - skip: The number of items skipped
            - has_more: True if more items exist beyond this page

    Raises:
        Exception: If there is an error retrieving task metrics from the platform
    """
    await ctx.debug("inside get_task_metrics(...)")
    client = ctx.request_context.lifespan_context.get("client")
    items, total = await client.workflow_engine.get_task_metrics(
        params=params, limit=limit, skip=skip
    )
    return models.GetTaskMetricsResponse(
        results=items,
        total=total,
        returned=len(items),
        limit=limit,
        skip=skip,
        has_more=skip + len(items) < total,
    )


@annotate(read_only=True, idempotent=True, open_world=False, title="Get Task Metrics")
async def get_task_metrics(
    ctx: Annotated[Context, Field(description="The FastMCP Context object")],
    *,
    limit: Annotated[
        int,
        Field(
            description="Maximum number of items to return (1-1000, default 200)",
            ge=1,
            le=1000,
        ),
    ] = 200,
    skip: Annotated[
        int,
        Field(
            description="Number of items to skip, used to page through large result sets",
            ge=0,
        ),
    ] = 0,
) -> models.GetTaskMetricsResponse:
    """
    Get a page of aggregate task metrics from the Workflow Engine.

    Retrieves comprehensive task-level execution metrics across all workflows,
    providing detailed insights into task performance, application usage patterns,
    and execution statistics for automation monitoring and optimization.

    Args:
        ctx (Context): The FastMCP Context object
        limit (int): Maximum number of items to return (1-1000). Defaults to 200.
        skip (int): Number of items to skip before the page starts. Defaults to 0.

    Returns:
        GetTaskMetricsResponse: Response containing one page of task metrics with the following fields:
            - results: The task metric elements in this page. Each element has:
                - taskId: The task identifier in the workflow
                - taskType: Task type (automatic, manual)
                - name: The name of the task
                - metrics: The task metrics data
                - app: The application that runs the task
                - workflow: The name of the workflow the task is part of
            - total: Total number of matching items on the platform
            - returned: Number of items in this page
            - limit: The page size that was requested
            - skip: The number of items skipped
            - has_more: True if more items exist beyond this page

    Raises:
        Exception: If there is an error retrieving task metrics from the platform
    """
    return await _get_task_metrics(ctx, limit=limit, skip=skip)


@annotate(
    read_only=True,
    idempotent=True,
    open_world=False,
    title="Get Task Metrics for Workflow",
)
async def get_task_metrics_for_workflow(
    ctx: Annotated[Context, Field(description="The FastMCP Context object")],
    name: Annotated[
        str, Field(description="The name of the workflow to retrieve task metrics for")
    ],
    *,
    limit: Annotated[
        int,
        Field(
            description="Maximum number of items to return (1-1000, default 200)",
            ge=1,
            le=1000,
        ),
    ] = 200,
    skip: Annotated[
        int,
        Field(
            description="Number of items to skip, used to page through large result sets",
            ge=0,
        ),
    ] = 0,
) -> models.GetTaskMetricsResponse:
    """
    Get a page of task metrics for the specified workflow from Workflow Engine.

    Retrieves task execution metrics filtered by a specific workflow name,
    providing detailed insights into the performance of individual tasks
    within that particular workflow for targeted analysis and optimization.

    Args:
        ctx (Context): The FastMCP Context object
        name (str): The name of the workflow to retrieve task metrics for
        limit (int): Maximum number of items to return (1-1000). Defaults to 200.
        skip (int): Number of items to skip before the page starts. Defaults to 0.

    Returns:
        GetTaskMetricsResponse: Response containing one page of task metrics with the following fields:
            - results: The task metric elements in this page. Each element has:
                - taskId: The task identifier in the workflow
                - taskType: Task type (automatic, manual)
                - name: The name of the task
                - metrics: The task metrics data
                - app: The application that runs the task
                - workflow: The name of the workflow the task is part of
            - total: Total number of matching items on the platform
            - returned: Number of items in this page
            - limit: The page size that was requested
            - skip: The number of items skipped
            - has_more: True if more items exist beyond this page

    Raises:
        Exception: If there is an error retrieving task metrics from the platform

    Notes:
        - The name argument is case sensitive
    """
    return await _get_task_metrics(
        ctx,
        params={"equalsField": "workflow.name", "equals": name},
        limit=limit,
        skip=skip,
    )


@annotate(
    read_only=True,
    idempotent=True,
    open_world=False,
    title="Get Task Metrics for App",
)
async def get_task_metrics_for_app(
    ctx: Annotated[Context, Field(description="The FastMCP Context object")],
    name: Annotated[
        str,
        Field(description="The name of the application to retrieve task metrics for"),
    ],
    *,
    limit: Annotated[
        int,
        Field(
            description="Maximum number of items to return (1-1000, default 200)",
            ge=1,
            le=1000,
        ),
    ] = 200,
    skip: Annotated[
        int,
        Field(
            description="Number of items to skip, used to page through large result sets",
            ge=0,
        ),
    ] = 0,
) -> models.GetTaskMetricsResponse:
    """
    Get a page of task metrics for the specified application from Workflow Engine.

    Retrieves task execution metrics filtered by a specific application name,
    providing insights into how tasks performed by that application are executing
    across different workflows and automation processes.

    Args:
        ctx (Context): The FastMCP Context object
        name (str): The name of the application to retrieve task metrics for.
            Application names can be obtained using the get_applications tool.
        limit (int): Maximum number of items to return (1-1000). Defaults to 200.
        skip (int): Number of items to skip before the page starts. Defaults to 0.

    Returns:
        GetTaskMetricsResponse: Response containing one page of task metrics with the following fields:
            - results: The task metric elements in this page. Each element has:
                - taskId: The task identifier in the workflow
                - taskType: Task type (automatic, manual)
                - name: The name of the task
                - metrics: The task metrics data
                - app: The application that runs the task
                - workflow: The name of the workflow the task is part of
            - total: Total number of matching items on the platform
            - returned: Number of items in this page
            - limit: The page size that was requested
            - skip: The number of items skipped
            - has_more: True if more items exist beyond this page

    Raises:
        Exception: If there is an error retrieving task metrics from the platform

    Notes:
        - The name argument is case sensitive
        - Use get_applications tool to retrieve available application names
    """
    return await _get_task_metrics(
        ctx, params={"equalsField": "app", "equals": name}, limit=limit, skip=skip
    )


@annotate(
    read_only=True,
    idempotent=True,
    open_world=False,
    title="Get Task Metrics for Task",
)
async def get_task_metrics_for_task(
    ctx: Annotated[Context, Field(description="The FastMCP Context object")],
    name: Annotated[
        str, Field(description="The name of the task to retrieve task metrics for")
    ],
    *,
    limit: Annotated[
        int,
        Field(
            description="Maximum number of items to return (1-1000, default 200)",
            ge=1,
            le=1000,
        ),
    ] = 200,
    skip: Annotated[
        int,
        Field(
            description="Number of items to skip, used to page through large result sets",
            ge=0,
        ),
    ] = 0,
) -> models.GetTaskMetricsResponse:
    """
    Get a page of task metrics for the named task from Workflow Engine.

    Retrieves task execution metrics filtered by a specific task name,
    providing detailed performance insights for that particular task
    across all workflows where it appears.

    Args:
        ctx (Context): The FastMCP Context object
        name (str): The name of the task to retrieve task metrics for
        limit (int): Maximum number of items to return (1-1000). Defaults to 200.
        skip (int): Number of items to skip before the page starts. Defaults to 0.

    Returns:
        GetTaskMetricsResponse: Response containing one page of task metrics with the following fields:
            - results: The task metric elements in this page. Each element has:
                - taskId: The task identifier in the workflow
                - taskType: Task type (automatic, manual)
                - name: The name of the task
                - metrics: The task metrics data
                - app: The application that runs the task
                - workflow: The name of the workflow the task is part of
            - total: Total number of matching items on the platform
            - returned: Number of items in this page
            - limit: The page size that was requested
            - skip: The number of items skipped
            - has_more: True if more items exist beyond this page

    Raises:
        Exception: If there is an error retrieving task metrics from the platform

    Notes:
        - The name argument is case sensitive
    """
    return await _get_task_metrics(
        ctx, params={"equalsField": "name", "equals": name}, limit=limit, skip=skip
    )
