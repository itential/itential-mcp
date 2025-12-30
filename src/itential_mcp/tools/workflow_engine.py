# Copyright (c) 2025 Itential, Inc
# GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from typing import Annotated

from pydantic import Field

from fastmcp import Context

from itential_mcp.models import workflow_engine as models


__tags__ = ("workflow_engine",)


async def _get_job_metrics(
    ctx: Context, params: dict | None = None
) -> models.GetJobMetricsResponse:
    """
    Internal helper to get aggregate job metrics from the Workflow Engine.

    This private function handles the actual API call to retrieve job metrics
    from the workflow engine service. It supports optional filtering parameters
    to narrow the results.

    Args:
        ctx (Context): The FastMCP Context object for accessing the platform client
        params (dict | None): Optional query parameters to filter job metrics.
            Common filters include workflow name, date ranges, or execution status.
            If None, all job metrics will be retrieved.

    Returns:
        GetJobMetricsResponse: Response containing job metrics with the following fields:
            - _id: The id assigned by Itential Platform
            - workflow: The name of the workflow
            - metrics: The job metrics data
            - jobsComplete: Number of completed jobs
            - totalRunTime: Cumulative run time in seconds

    Raises:
        Exception: If there is an error retrieving job metrics from the platform
    """
    await ctx.debug("inside _get_job_metrics(...)")

    client = ctx.request_context.lifespan_context.get("client")
    res = await client.workflow_engine.get_job_metrics(params=params)
    return models.GetJobMetricsResponse(res)


async def get_job_metrics(
    ctx: Annotated[Context, Field(description="The FastMCP Context object")],
) -> models.GetJobMetricsResponse:
    """
    Get aggregate job metrics from the Workflow Engine.

    The Workflow Engine maintains comprehensive metrics about workflow execution
    performance, providing insights into automation efficiency, success rates,
    and resource utilization across all workflow jobs.

    Args:
        ctx (Context): The FastMCP Context object

    Returns:
        GetJobMetricsResponse: Response containing job metrics with the following fields:
            - _id: The id assigned by Itential Platform
            - workflow: The name of the workflow
            - metrics: The job metrics data
            - jobsComplete: Number of completed jobs
            - totalRunTime: Cumulative run time in seconds

    Raises:
        Exception: If there is an error retrieving job metrics from the platform
    """
    return await _get_job_metrics(ctx)


async def get_job_metrics_for_workflow(
    ctx: Annotated[Context, Field(description="The FastMCP Context object")],
    name: Annotated[
        str, Field(description="The name of the workflow to get the job metrics for")
    ],
) -> models.GetJobMetricsResponse:
    """
    Get the job metrics for the specified workflow from Workflow Engine.

    Retrieves job execution metrics filtered by a specific workflow name,
    providing targeted insights into the performance and execution statistics
    for jobs within that particular workflow.

    Args:
        ctx (Context): The FastMCP Context object
        name (str): The name of the workflow to retrieve job metrics for

    Returns:
        GetJobMetricsResponse: Response containing job metrics with the following fields:
            - _id: The id assigned by Itential Platform
            - workflow: The name of the workflow
            - metrics: The job metrics data
            - jobsComplete: Number of completed jobs
            - totalRunTime: Cumulative run time in seconds

    Raises:
        Exception: If there is an error retrieving job metrics from the platform

    Notes:
        - The name argument is case sensitive
    """
    return await _get_job_metrics(
        ctx, params={"containsField": "workflow.name", "contains": name}
    )


async def _get_task_metrics(
    ctx: Context, params: dict | None = None
) -> models.GetTaskMetricsResponse:
    """
    Internal helper to get aggregate task metrics from the Workflow Engine.

    The Workflow Engine tracks detailed task-level metrics within workflows,
    providing granular insights into individual task performance, application
    usage, and execution patterns across automation operations.

    Args:
        ctx (Context): The FastMCP Context object for accessing the platform client
        params (dict | None): Optional query parameters to filter task metrics.
            Common filters include task name, application name, workflow name,
            or task type. If None, all task metrics will be retrieved.

    Returns:
        GetTaskMetricsResponse: Response containing task metrics with the following fields:
            - taskId: The task identifier in the workflow
            - taskType: Task type (automatic, manual)
            - name: The name of the task
            - metrics: The task metrics data
            - app: The application that runs the task
            - workflow: The name of the workflow the task is part of

    Raises:
        Exception: If there is an error retrieving task metrics from the platform
    """
    await ctx.debug("inside get_task_metrics(...)")
    client = ctx.request_context.lifespan_context.get("client")
    res = await client.workflow_engine.get_task_metrics(params=params)
    return models.GetTaskMetricsResponse(res)


async def get_task_metrics(
    ctx: Annotated[Context, Field(description="The FastMCP Context object")],
) -> models.GetTaskMetricsResponse:
    """
    Get all aggregate task metrics from the Workflow Engine.

    Retrieves comprehensive task-level execution metrics across all workflows,
    providing detailed insights into task performance, application usage patterns,
    and execution statistics for automation monitoring and optimization.

    Args:
        ctx (Context): The FastMCP Context object

    Returns:
        GetTaskMetricsResponse: Response containing task metrics with the following fields:
            - taskId: The task identifier in the workflow
            - taskType: Task type (automatic, manual)
            - name: The name of the task
            - metrics: The task metrics data
            - app: The application that runs the task
            - workflow: The name of the workflow the task is part of

    Raises:
        Exception: If there is an error retrieving task metrics from the platform
    """
    return await _get_task_metrics(ctx)


async def get_task_metrics_for_workflow(
    ctx: Annotated[Context, Field(description="The FastMCP Context object")],
    name: Annotated[
        str, Field(description="The name of the workflow to retrieve task metrics for")
    ],
) -> models.GetTaskMetricsResponse:
    """
    Get all task metrics for the specified workflow from Workflow Engine.

    Retrieves task execution metrics filtered by a specific workflow name,
    providing detailed insights into the performance of individual tasks
    within that particular workflow for targeted analysis and optimization.

    Args:
        ctx (Context): The FastMCP Context object
        name (str): The name of the workflow to retrieve task metrics for

    Returns:
        GetTaskMetricsResponse: Response containing task metrics with the following fields:
            - taskId: The task identifier in the workflow
            - taskType: Task type (automatic, manual)
            - name: The name of the task
            - metrics: The task metrics data
            - app: The application that runs the task
            - workflow: The name of the workflow the task is part of

    Raises:
        Exception: If there is an error retrieving task metrics from the platform

    Notes:
        - The name argument is case sensitive
    """
    return await _get_task_metrics(
        ctx, params={"equalsField": "workflow.name", "equals": name}
    )


async def get_task_metrics_for_app(
    ctx: Annotated[Context, Field(description="The FastMCP Context object")],
    name: Annotated[
        str,
        Field(description="The name of the application to retrieve task metrics for"),
    ],
) -> models.GetTaskMetricsResponse:
    """
    Get all task metrics for the specified application from Workflow Engine.

    Retrieves task execution metrics filtered by a specific application name,
    providing insights into how tasks performed by that application are executing
    across different workflows and automation processes.

    Args:
        ctx (Context): The FastMCP Context object
        name (str): The name of the application to retrieve task metrics for.
            Application names can be obtained using the get_applications tool.

    Returns:
        GetTaskMetricsResponse: Response containing task metrics with the following fields:
            - taskId: The task identifier in the workflow
            - taskType: Task type (automatic, manual)
            - name: The name of the task
            - metrics: The task metrics data
            - app: The application that runs the task
            - workflow: The name of the workflow the task is part of

    Raises:
        Exception: If there is an error retrieving task metrics from the platform

    Notes:
        - The name argument is case sensitive
        - Use get_applications tool to retrieve available application names
    """
    return await _get_task_metrics(ctx, params={"equalsField": "app", "equals": name})


async def get_task_metrics_for_task(
    ctx: Annotated[Context, Field(description="The FastMCP Context object")],
    name: Annotated[
        str, Field(description="The name of the task to retrieve task metrics for")
    ],
) -> models.GetTaskMetricsResponse:
    """
    Get all task metrics for the named task from Workflow Engine.

    Retrieves task execution metrics filtered by a specific task name,
    providing detailed performance insights for that particular task
    across all workflows where it appears.

    Args:
        ctx (Context): The FastMCP Context object
        name (str): The name of the task to retrieve task metrics for

    Returns:
        GetTaskMetricsResponse: Response containing task metrics with the following fields:
            - taskId: The task identifier in the workflow
            - taskType: Task type (automatic, manual)
            - name: The name of the task
            - metrics: The task metrics data
            - app: The application that runs the task
            - workflow: The name of the workflow the task is part of

    Raises:
        Exception: If there is an error retrieving task metrics from the platform

    Notes:
        - The name argument is case sensitive
    """
    return await _get_task_metrics(ctx, params={"equalsField": "name", "equals": name})
