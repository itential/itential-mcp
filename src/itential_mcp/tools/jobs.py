# Copyright (c) 2025 Itential, Inc
# GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)

from typing import Annotated

from pydantic import Field

from fastmcp import Context

from itential_mcp import functions


__tags__ = ("operations_manager",)


async def get_jobs(
    ctx: Annotated[Context, Field(
        description="The FastMCP Context object"
    )],
    name: Annotated[str | None, Field(
        description="Workflow name used to filter the results",
        default=None
    )],
    project: Annotated[str | None, Field(
        description="Project name used to filter the results",
        default=None
    )]
) -> list[dict]:
    """
    Get all jobs from Itential Platform.

    Jobs represent workflow execution instances that track the status, progress,
    and results of automated tasks. They provide visibility into workflow
    execution and enable monitoring of automation operations.

    Args:
        ctx (Context): The FastMCP Context object
        name (str | None): Filter jobs by workflow name (optional)
        project (str | None): Filter jobs by project name (optional)

    Returns:
        list[dict]: List of job objects with the following fields:
            - _id: Unique job identifier
            - created: Job creation timestamp
            - created_by: ID of user who created the job
            - description: Job description
            - updated: Last update timestamp
            - updated_by: ID of user who last updated the job
            - name: Job name
            - status: Current job status (error, complete, running, cancelled, incomplete, paused)
    """
    await ctx.info("running get_jobs(...)")

    client = ctx.request_context.lifespan_context.get("client")

    results = list()

    limit = 100
    skip = 0

    params = {"limit": limit}

    if project is not None:
        project_id = await functions.project_name_to_id(ctx, project)
        if name is not None:
            params["equals[name]"] = f"@{project_id}: {name}"
        else:
            params["starts-with[name]"] = f"@{project_id}"

    elif name is not None:
        params["equals[name]"] = name

    while True:
        params["skip"] = skip

        res = await client.get("/operations-manager/jobs", params=params)

        data = res.json()
        metadata = data.get("metadata")

        for item in data.get("data") or list():
            results.append({
                "_id": item.get("_id"),
                "created": item.get("created"),
                "created_by": item.get("created_by"),
                "updated": item.get("last_updated"),
                "updated_by": item.get("last_updated_by"),
                "name": item.get("name"),
                "description": item.get("description"),
                "status": item.get("status")
            })

        if len(results) == metadata["total"]:
            break

        skip += limit

    return results


async def describe_job(
    ctx: Annotated[Context, Field(
        description="The FastMCP Context object"
    )],
    job_id: Annotated[str, Field(
        description="The ID used to retrieve the job"
    )]
) -> dict:
    """
    Get detailed information about a specific job from Itential Platform.

    Jobs are created automatically when workflows are executed and contain
    comprehensive information about the workflow execution including status,
    tasks, metrics, and results.

    Args:
        ctx (Context): The FastMCP Context object
        job_id (str): Unique job identifier to retrieve. Job IDs are returned by `start_workflow` and `get_jobs`.

    Returns:
        dict: Job details with the following fields:
            - _id: Unique job identifier
            - name: Job name
            - description: Job description
            - type: Job type (automation, resource:action, resource:compliance)
            - tasks: Complete set of tasks executed
            - status: Current job status (error, complete, running, canceled, incomplete, paused)
            - metrics: Job execution metrics including start time, end time, and account
            - updated: Last update timestamp
    """

    await ctx.info("inside describe_job(...)")

    client = ctx.request_context.lifespan_context.get("client")

    res = await client.get(f"/operations-manager/jobs/{job_id}")

    data = res.json()["data"]

    return {
        "_id": data["_id"],
        "name": data["name"],
        "description": data["description"],
        "type": data["type"],
        "tasks": data["tasks"],
        "status": data["status"],
        "metrics": data["metrics"],
        "updated": data["last_updated"]
    }
