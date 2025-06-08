# Copyright (c) 2025 Itential, Inc
# GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)

from typing import Annotated

from pydantic import Field

from fastmcp import Context


async def get_job_metrics(
    ctx: Annotated[Context, Field(
        description="The FastMCP Context object"
    )]
) -> list[dict]:
    """
    Get the aggregate job metrics from workflow engine

    The Itential Platform workflow engine maintains records that aggregate
    workflow job metrics over the life of automation executions. This
    function will return the aggregate job metrics for automations that
    have been executed by Itential Platform.

    It will provide information such as the number of jobs completed in the
    `jobsComplete` key, the name of the workflow that was executed and the
    total run time among other key statistics

    Args:
        ctx (Context): The FastMCP Context object

    Returns:
        list[dict]: A Python list object that contains job metric data as
            a Python dict object

    Raises:
        None
    """
    await ctx.debug("inside get_job_metrics(...)")

    client = ctx.request_context.lifespan_context.get("client")

    limit = 100
    skip = 0

    params = {"limit": limit}

    results = list()

    while True:
        params["skip"] = skip

        res = await client.get(
            "/workflow_engine/jobs/metrics",
            params=params,
        )

        data = res.json()
        elements = data.get("results") or list()

        results.extend(elements)

        if len(elements) == data["total"]:
            break

        skip += limit

    return results


async def get_task_metrics(
    ctx: Annotated[Context, Field(
        description="The FastMCP Context object"
    )]
) -> list[dict]:
    """
    Get the aggregate task metrics from workflow engine

    The Itential Platform workflow engine maintains records that aggregate
    workflow task metrics over the life of automation executions. This
    function will return the aggregate task metrics for automations that
    have been executed by Itential Platform.

    It will provide details about tasks from workflows such as the application
    associated with the task, the task name and type and metrics for the task.

    Args:
        ctx (Context): The FastMCP Context object

    Returns:
        list[dict]: A Python list object that contains task metric data as
            a Python dict object

    Raises:
        None
    """
    await ctx.debug("inside get_task_metrics(...)")

    client = ctx.request_context.lifespan_context.get("client")

    limit = 100
    skip = 0

    results = list()

    while True:
        res = await client.get("/workflow_engine/tasks/metrics")

        data = res.json()
        results.extend(data["results"])

        if len(results) == data["total"]:
            break

        skip += limit

    return results

