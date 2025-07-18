# Copyright (c) 2025 Itential, Inc
# GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)

from typing import Annotated

from pydantic import Field

from fastmcp import Context


__tags__ = ("workflow_engine",)


async def _get_job_metrics(
    ctx: Context,
    params: dict | None = None
) -> list[dict]:
    """
    Get aggregate job metrics from the Workflow Engine.

    Args:
        ctx (Context): The FastMCP Context object
        params (dict): Additional paramets to filter the returned jobs

    Returns:
        list[dict]: List of job metrics with the following fields:
            - _id: The id assinged by Itential Platform
            - workflow: The name of the workflow
            - metrics: The job metrics
            - jobsComplete: Number of completed jobs
            - totalRunTime: Cumulative run time in seconds
    """
    await ctx.debug("inside _get_job_metrics(...)")

    client = ctx.request_context.lifespan_context.get("client")

    limit = 100
    skip = 0

    if params is None:
        params = {"limit": limit}
    else:
        params["limit"] = limit

    results = list()

    while True:
        params["skip"] = skip

        res = await client.get(
            "/workflow_engine/jobs/metrics",
            params=params,
        )

        data = res.json()
        elements = data.get("results") or list()

        for ele in elements:
            results.append({
                "_id": ele.get("_id"),
                "workflow": ele.get("workflow"),
                "metrics": ele.get("metrics"),
                "jobsComplete": ele.get("jobsComplete"),
                "totalRunTime": ele.get("totalRunTime")
            })

        if len(elements) == data["total"]:
            break

        skip += limit

    return results


async def get_job_metrics(
    ctx: Annotated[Context, Field(
        description="The FastMCP Context object"
    )]
) -> list[dict]:
    """
    Get aggregate job metrics from the Workflow Engine.

    The Workflow Engine maintains comprehensive metrics about workflow execution
    performance, providing insights into automation efficiency, success rates,
    and resource utilization across all workflow jobs.

    Args:
        ctx (Context): The FastMCP Context object

    Returns:
        list[dict]: List of job metrics with the following fields:
            - _id: The id assinged by Itential Platform
            - workflow: The name of the workflow
            - metrics: The job metrics
            - jobsComplete: Number of completed jobs
            - totalRunTime: Cumulative run time in seconds
    """
    return await _get_job_metrics(ctx)


async def get_job_metrics_for_workflow(
    ctx: Annotated[Context, Field(
        description="The FastMCP Context object"
    )],
    name: Annotated[str, Field(
        description="The name of the workflow to get the job metrics for"
    )]
) -> list[dict]:
    """
    Get the job metrics for the specified workflow from Workflow Engine

    Args:
        ctx (Context): The FastMCP Context object

        name (str): the name of the workflow to retrieve the job metrics for

    Returns:
        list[dict]: List of job metrics with the following fields:
            - _id: The id assinged by Itential Platform
            - workflow: The name of the workflow
            - metrics: The job metrics
            - jobsComplete: Number of completed jobs
            - totalRunTime: Cumulative run time in seconds

    Notes:
        - The name argument is case sensitive
    """
    return await _get_job_metrics(
        ctx,
        params={
            "containsField": "workflow.name",
            "contains": name
        }
    )


async def _get_task_metrics(
    ctx: Context,
    params: dict | None = None
) -> list[dict]:
    """
    Get aggregate task metrics from the Workflow Engine.

    The Workflow Engine tracks detailed task-level metrics within workflows,
    providing granular insights into individual task performance, application
    usage, and execution patterns across automation operations.

    Args:
        ctx (Context): The FastMCP Context object

    Returns:
        list[dict]: List of task metric objects containing task details including
            associated applications, task names and types, and performance metrics
    """
    await ctx.debug("inside get_task_metrics(...)")

    client = ctx.request_context.lifespan_context.get("client")

    limit = 100
    skip = 0
    cnt = 0

    if params is None:
        params = {"limit": limit}
    else:
        params["limit"] = limit


    results = list()

    while True:
        res = await client.get(
            "/workflow_engine/tasks/metrics",
            params=params,
        )

        await ctx.info(res.text)

        data = res.json()

        fields = frozenset(
            ("taskId", "taskType", "name", "metrics", "app", "workflow")
        )

        results = list()

        for ele in data["results"]:
            if ele.get("workflow") is not None:
                results.append(dict([(k, ele.get(k)) for k in fields]))

        cnt += len(data["results"])
        if cnt == data["total"]:
            break

        skip += limit

    return results


async def get_task_metrics(
    ctx: Annotated[Context, Field(
        description="The FastMCP Context object"
    )]
) -> list[dict]:
    """
    Get all aggregate task metrics from the Workflow Engine

    Args:
        ctx (Context): The FastMCP Context object

    Returns:
        list[dict]: List of task metrics with the following fields:
            - taskId: The task identifier in the workflow
            - taskType: Task type (automatic, manual)
            - name: The name of the task
            - metrics: The task metrics
            - app: The application that runs the task
            - workflow: The name of the workflow the task is part of
    """
    return await _get_task_metrics(ctx)


async def get_task_metrics_for_workflow(
    ctx: Annotated[Context, Field(
        description="The FastMCP Context object"
    )],
    name: Annotated[str, Field(
        description="The name of the workflow to retrieve task metrics for"
    )]
) -> list[dict]:
    """
    Get all task metrics for the specified workflow from Workflow Engine

    Args:
        ctx (Context): The FastMCP Context object

        name (str): The name of the workflow to retrieve task metrics for

    Returns:
        list[dict]: List of task metrics with the following fields:
            - taskId: The task identifier in the workflow
            - taskType: Task type (automatic, manual)
            - name: The name of the task
            - metrics: The task metrics
            - app: The application that runs the task
            - workflow: The name of the workflow the task is part of

    Notes:
        - The name argument is case sensitive
    """
    return await _get_task_metrics(
        ctx,
        params={
            "equalsField": "workflow.name",
            "equals": name
        }
    )


async def get_task_metrics_for_app(
    ctx: Annotated[Context, Field(
        description="The FastMCP Context object"
    )],
    name: Annotated[str, Field(
        description="The name of the application to retrieve task metrics for"
    )]
) -> list[dict]:
    """
    Get all task metrics for the specified application from Workflow Engine

    Args:
        ctx (Context): The FastMCP Context object

        name (str): The name of the application to retrieve task metrics for.
            Application names can be obtained using the get_applications tool.

    Returns:
        list[dict]: List of task metrics with the following fields:
            - taskId: The task identifier in the workflow
            - taskType: Task type (automatic, manual)
            - name: The name of the task
            - metrics: The task metrics
            - app: The application that runs the task
            - workflow: The name of the workflow the task is part of

    Notes:
        - The name argument is case sensitive
        - Use get_applications tool to retrieve available application names
    """
    return await _get_task_metrics(
        ctx,
        params={
            "equalsField": "app",
            "equals": name
        }
    )

async def get_task_metrics_for_task(
    ctx: Annotated[Context, Field(
        description="The FastMCP Context object"
    )],
    name: Annotated[str, Field(
        description="The name of the application to retrieve task metrics for"
    )]
) -> list[dict]:
    """
    Get all task metrics for the named task from Workflow Engine

    Args:
        ctx (Context): The FastMCP Context object

        name (str): The name of the task to retrieve task metrics for

    Returns:
        list[dict]: List of task metrics with the following fields:
            - taskId: The task identifier in the workflow
            - taskType: Task type (automatic, manual)
            - name: The name of the task
            - metrics: The task metrics
            - app: The application that runs the task
            - workflow: The name of the workflow the task is part of

    Notes:
        - The name argument is case sensitive
    """
    return await _get_task_metrics(
        ctx,
        params={
            "equalsField": "name",
            "equals": name
        }
    )


