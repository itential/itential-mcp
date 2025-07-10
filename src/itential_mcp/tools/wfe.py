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
    Get aggregate job metrics from the Workflow Engine.

    The Workflow Engine maintains comprehensive metrics about workflow execution 
    performance, providing insights into automation efficiency, success rates, 
    and resource utilization across all workflow jobs.

    Args:
        ctx (Context): The FastMCP Context object

    Returns:
        list[dict]: List of job metric objects containing execution statistics 
            including jobs completed, workflow names, total runtime, and other 
            performance metrics
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

    results = list()

    while True:
        res = await client.get("/workflow_engine/tasks/metrics")

        data = res.json()
        results.extend(data["results"])

        if len(results) == data["total"]:
            break

        skip += limit

    return results
