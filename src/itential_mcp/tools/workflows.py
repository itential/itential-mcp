# Copyright (c) 2025 Itential, Inc
# GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)

from typing import Annotated

from pydantic import Field

from fastmcp import Context

from itential_mcp import timeutils
from itential_mcp import functions


async def get_workflows(
    ctx: Annotated[Context, Field(
        description="The FastMCP Context object"
    )]
) -> list[dict]:
    """
    Get all API endpoint triggers from Itential Platform

    This tool will retrieve all of the API endpoint triggers (routes) that
    can be called by external services.  The tool will return a list of
    triggers where each element in the list represents a callable API
    route. Use the name as the identifier for the workflow. The routeName 
    is used for job triggering only.

    The fields available for each element include:

        * _id: The unique identifier for this route
        * name: The name of the workflow as configured in Platform
        * description: Short description of the triggers function
        * schema: The input schema for the launching the trigger based
            on http://json-schema.org/draft-07/schema
        * routeName: The API route used to start the endpoint
        * created: ISO 8601 timestamp of when the trigger was created
        * createdBy: Account name that created the trigger
        * updated: ISO 8601 timestamp of when the trigger was last updated
        * updatedBy: Account name that last updated the trigger
        * lastExecuted: ISO 8601 timestamp this trigger was last executed

    Args:
        ctx (Context): The FastMCP Context object

    Returns:
        list[dict]: A Python list of dict objects that represent the available
            workflows found on the server.

    Raises:
        None
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
    Start an API endpoint trigger from Itential Platform

    This tool is responsible for calling the API endpoint trigger based
    on the `route` argument.  The `route` argument provides the name of
    API endpoint trigger to call.

    Optionally, the `data` argument can be used to provide data in the
    body of the request when invoking the API endpoint route.

    The tool will return an object that represents the started job
    in Itential Platform.  It containes the following fields:

        * _id: The unique identifier for this job
        * name: The name of the API endpoint trigger
        * description: Short description of the API endpoint trigger
        * tasks: The full set of tasks to be executed
        * created: ISO 8601 timestamp of when the trigger was created
        * createdBy: Account name that created the trigger
        * updated: ISO 8601 timestamp of when the trigger was last updated
        * updatedBy: Account name that last updated the trigger
        * status: The status of the job.  This will return one of the
            following values: `error`, `complete`, `running`, `canceled`,
            `incomplete` or `paused`
        * metrics: Job metrics that include the job start time, job end
            time and account

    Args:
        ctx (Context): The FastMCP Context object
        route_name (str): The API endpoint route to start
        data: (dict): Data to use in the request as input to the API route

    Returns:
        dict: A Python dict object that represents the relevant data from
            the job document API.

    Raises:
        None

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
