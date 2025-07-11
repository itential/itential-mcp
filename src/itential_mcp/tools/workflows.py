# Copyright (c) 2025 Itential, Inc
# GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)

from typing import Annotated

from pydantic import Field

from fastmcp import Context

from itential_mcp import timeutils
from itential_mcp import functions


__tags__ = ("operations_manager",)


async def get_workflows(
    ctx: Annotated[Context, Field(
        description="The FastMCP Context object"
    )]
) -> list[dict]:
    """
    Get all workflow API endpoints from Itential Platform.

    Workflows are the core automation engine of Itential Platform, defining
    executable processes that orchestrate network operations, device management,
    and service provisioning. Each workflow exposes an API endpoint that can be
    triggered by external systems or other platform components.

    Args:
        ctx (Context): The FastMCP Context object

    Returns:
        list[dict]: List of workflow objects with the following fields:
            - _id: Unique identifier for the workflow
            - name: Workflow name (use this as the identifier for workflow operations)
            - description: Workflow description
            - schema: Input schema for workflow parameters (JSON Schema draft-07 format)
            - routeName: API route name for triggering the workflow (use with `start_workflow`)
            - created: ISO 8601 creation timestamp
            - createdBy: Account name that created the workflow
            - updated: ISO 8601 last update timestamp
            - updatedBy: Account name that last updated the workflow
            - lastExecuted: ISO 8601 timestamp of last execution (null if never executed)

    Notes:
        - Use the 'name' field as the workflow identifier for most operations
        - Use the 'routeName' field specifically for `start_workflow` function
        - The 'schema' field defines required input parameters for workflow execution
        - Only enabled workflows are returned by this function
    """
    await ctx.info("inside get_workflows(...)")

    client = ctx.request_context.lifespan_context.get("client")

    limit = 100
    skip = 0

    params = {"limit": limit}

    results = list()

    while True:
        params.update({
            "skip": skip,
            "equalsField": "type",
            "equals": "endpoint",
            "enabled": True,
        })

        res = await client.get(
            "/operations-manager/triggers",
            params=params,
        )

        data = res.json()

        for item in data.get("data") or list():

            if item.get("lastExecuted") is not None:
                lastExecuted = timeutils.epoch_to_timestamp(item["lastExecuted"])
            else:
                lastExecuted = None

            results.append({
                "_id": item.get("_id"),
                "name": item.get("name"),
                "description": item.get("description"),
                "schema": item.get("schema"),
                "routeName": item.get("routeName"),
                "created": item.get("created"),
                "createdBy": item.get("createdBy"),
                "updated": item.get("lastUpdated"),
                "updatedBy": item.get("lastUpdatedBy"),
                "lastExecuted": lastExecuted,
            })

        if len(results) == data["metadata"]["total"]:
            break

        skip += limit

    return results


async def start_workflow(
    ctx: Annotated[Context, Field(
        description="The FastMCP Context object"
    )],
    route_name: Annotated[str, Field(
        description="The name of the API endpoint used to start the workflow"
    )],
    data: Annotated[dict | None, Field(
        description="Data to include in the request body when calling the route",
        default=None
    )]
) -> dict:
    """
    Execute a workflow by triggering its API endpoint.

    Workflows are the core automation processes in Itential Platform. This function
    initiates workflow execution and returns a job object that can be monitored
    for progress and results.

    Args:
        ctx (Context): The FastMCP Context object
        route_name (str): API route name for the workflow. Use the 'routeName' field from `get_workflows`.
        data (dict | None): Input data for workflow execution. Structure must match the workflow's
            input schema (available in the 'schema' field from `get_workflows`).

    Returns:
        dict: Job execution details with the following fields:
            - _id: Unique job identifier (use with `describe_job` for monitoring)
            - name: Workflow name that was executed
            - description: Workflow description
            - tasks: Complete set of tasks to be executed in the workflow
            - status: Current job status (error, complete, running, canceled, incomplete, paused)
            - metrics: Job execution metrics including start_time, end_time, and user
            - created: Job creation timestamp
            - created_by: Account that created the job
            - updated: Last update timestamp
            - updated_by: Account that last updated the job

    Notes:
        - Use the returned '_id' field with `describe_job` to monitor workflow progress
        - The 'data' parameter must conform to the workflow's input schema
        - Job status can be monitored using the `get_jobs` or `describe_job` functions
        - Workflow schemas are available via the `get_workflows` function
    """
    await ctx.info("inside run_workflow(...)")

    client = ctx.request_context.lifespan_context.get("client")

    res = await client.post(
        f"/operations-manager/triggers/endpoint/{route_name}",
        json=data,
    )

    data = res.json()["data"]

    metrics = {}

    metrics_data = data.get("metrics") or {}

    if metrics_data.get("start_time") is not None:
        metrics["start_time"] = timeutils.epoch_to_timestamp(metrics_data["start_time"])

    if metrics_data.get("end_time") is not None:
        metrics["end_time"] = timeutils.epoch_to_timestamp(metrics_data["end_time"])

    if metrics_data.get("user") is not None:
        metrics["user"] = await functions.account_id_to_username(ctx, metrics_data["user"])

    return {
        "_id": data["_id"],
        "name": data["name"],
        "description": data["description"],
        "tasks": data["tasks"],
        "status": data["status"],
        "metrics": metrics,
        "updated": data["last_updated"],
        "updated_by": data["last_updated_by"],
        "created": data["created"],
        "created_by": data["created_by"],
    }
