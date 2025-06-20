# Copyright (c) 2025 Itential, Inc
# GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)

from typing import Annotated

from pydantic import Field

from fastmcp import Context

from itential_mcp import functions


async def get_resources(
    ctx: Annotated[Context, Field(
        description="The FastMCP Context object"
    )]
) -> list[dict]:
    """
    Get all Lifecycle Manager resource models from the server

    This tool will get all of the configured Lifecycle Manager resource models
    and return them as elements in a list.   The tool will return a list where
    each element represents a configured Lifecycle Model.

    The fields available for each element include:

        * _id: The unique identifier for this route
        * name: The name of the resource model
        * description: Short description of the model
        * created: ISO 8601 timestamp of when the model was created
        * createdBy: Account name that created the model
        * updated: ISO 8601 timestamp of when the model was last updated
        * updatedBy: Account name that last updated the model

    Args:
        ctx (Context): The FastMCP Context object

    Returns:
        list[dict]: A Python list of dict objects that represent the available
            resources found on the server.

    Raises:
        None
    """
    await ctx.info("inside get_resources(...)")

    client = ctx.request_context.lifespan_context.get("client")

    limit = 100
    skip = 0

    params = {"limit": limit}

    results = list()

    while True:
        params["skip"] = skip

        res = await client.get(
            "/lifecycle-manager/resources",
            params=params,
        )

        data = res.json()

        for item in data.get("data") or list():
            results.append({
                "_id": item["_id"],
                "name": item["name"],
                "description": item["description"],
                "created": item["created"],
                "createdBy": await functions.account_id_to_username(ctx, item["createdBy"]),
                "updated": item["lastUpdated"],
                "updatedBy": await functions.account_id_to_username(ctx, item["lastUpdatedBy"]),
            })

        if len(results) == data["metadata"]["total"]:
            break

        skip += limit

    return results


async def describe_resource(
    ctx: Annotated[Context, Field(
        description="The FastMCP Context object"
    )],
    name: Annotated[str, Field(
        description="The name of the resource model to describe"
    )]
) -> dict:
    """
    Describe a Lifecycle Manager resource identified by name

    This tool will retrieve the Lifecycle Manager resource using the specified
    `name` argument and return it.   The returned value will be a Python
    dict object that represents the Lifecycle Manager resource.

    The returned object includes the following fields:

        * _id: The resource unique identifier
        * name: The name of the resource
        * description: Short description of the model
        * schema: The JSON schema that defines the resource which can be used
            to create a new instance of the resource
        * actions: The list of actions assoicated with this resource.  Actions
            can be invoked on instances of the resource to transition from
            one state to another
        * created: ISO 8601 timestamp of when the model was created
        * createdBy: Account name that created the model
        * updated: ISO 8601 timestamp of when the model was last updated
        * updatedBy: Account name that last updated the model

    Args:
        ctx (Context): The FastMCP Context object
        name (str): The name of the resource to get from the server

    Returns:
        dict: A Python dict object that represents the Lifecycle
            Manager resource

    Raises:
        ValueError: Raised if the specified Lifecycle Manager could not
            be uniquely identified on the server
    """
    await ctx.info("inside describe_resource(...)")

    client = ctx.request_context.lifespan_context.get("client")

    res = await client.get(
        "/lifecycle-manager/resources",
        params={"equals[name]": name},
    )

    data = res.json()

    if data["metadata"]["total"] != 1:
        raise ValueError(f"error attempting to find resource {name}")

    item = data["data"][0]

    actions = list()

    for ele in item["actions"]:
        if ele["workflow"] is not None:
            ele["workflow"] = await functions.workflow_id_to_name(ctx, ele["workflow"])

        if ele["preWorkflowJst"] is not None:
               ele["preWorkflowJst"] = await functions.transformation_id_to_name(ctx, ele["preWorkflowJst"])

        if ele["postWorkflowJst"] is not None:
               ele["postWorkflowJst"] = await functions.transformation_id_to_name(ctx, ele["postWorkflowJst"])

        actions.append(ele)

    return {
        "_id": item["_id"],
        "name": item["name"],
        "description": item["description"],
        "schema": item["schema"],
        "actions": actions,
        "created": item["created"],
        "createdBy": await functions.account_id_to_username(ctx, item["createdBy"]),
        "updated": item["lastUpdated"],
        "updatedBy": await functions.account_id_to_username(ctx, item["lastUpdatedBy"])
    }


async def get_instances(
    ctx: Annotated[Context, Field(
        description="The FastMCP Context object"
    )],
    resource: Annotated[str, Field(
        description="The Lifecycle Manager resource name to retrieve instances for"
    )]
) -> list[dict]:
    """
    Get all instances for the resource from Itential Platform

    This tool will take the name of a Lifecycle Manager resource name and
    retrieve all configured instances of that resource.  The set of instances
    will be returned as a list.

    Each element in the list returns the following fields:

        * _id: The unique identifier for this route
        * name: The name of the resource model
        * description: Short description of the model
        * instanceData: Data object associated with this instance
        * lastAction: The last action performed on the instance
        * created: ISO 8601 timestamp of when the model was created
        * createdBy: Account name that created the model
        * updated: ISO 8601 timestamp of when the model was last updated
        * updatedBy: Account name that last updated the model

    Args:
        ctx (Context): The FastMCP Context object

        resource (str): The name of the resource to get instances for

    Returns:
        list[dict]: A list of Python dict objects where each element
            represents an instance of the resource

    Raises:
        ValueError: Raised if the specified resource could not be uniquely
            identified on the server

    """
    await ctx.info("inside get_instances(...)")

    client = ctx.request_context.lifespan_context.get("client")

    model_id = await functions.resource_name_to_id(ctx, resource)

    limit = 100
    skip = 0

    params = {"limit": limit}

    results = list()

    while True:
        params["skip"] = skip

        res = await client.get(
            f"/lifecycle-manager/resources/{model_id}/instances",
            params=params
        )

        data = res.json()

        for ele in data.get("data") or {}:
            results.append({
                "_id": ele["_id"],
                "name": ele["name"],
                "description": ele["description"],
                "instanceData": ele["instanceData"],
                "lastAction": ele["lastAction"],
                "created": ele["created"],
                "createdBy": await functions.account_id_to_username(ctx, ele["createdBy"]),
                "updated": ele["lastUpdated"],
                "updatedBy": await functions.account_id_to_username(ctx, ele["lastUpdatedBy"])
            })

        if len(results) == data["metadata"]["total"]:
            break

        skip += limit

    return results
