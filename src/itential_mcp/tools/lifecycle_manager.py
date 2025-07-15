# Copyright (c) 2025 Itential, Inc
# GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)

from typing import Annotated

from pydantic import Field

from fastmcp import Context

from itential_mcp import functions


__tags__ = ("lifecycle_manager",)


async def get_resources(
    ctx: Annotated[Context, Field(
        description="The FastMCP Context object"
    )]
) -> list[dict]:
    """
    Get all Lifecycle Manager resource models from Itential Platform.

    Lifecycle Manager resources define data models and workflows for managing
    network services and infrastructure components throughout their lifecycle.
    They provide structured templates for creating and managing resource instances.

    Args:
        ctx (Context): The FastMCP Context object

    Returns:
        list[dict]: List of resource model objects with the following fields:
            - _id: Unique identifier for the resource
            - name: Resource model name
            - description: Resource model description
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
            })

        if len(results) == data["metadata"]["total"]:
            break

        skip += limit

    return results


async def create_resource(
    ctx: Annotated[Context, Field(
        description="The FastMCP Context object"
    )],
    name: Annotated[str, Field(
        description="The name of the resource model to describe"
    )],
    schema: Annotated[dict, Field(
        description="JSON Schema representation of this resource"
    )],
    description: Annotated[str | None, Field(
        description="Short description of this resource",
        default=None
    )]
) -> dict:
    """
    Create a new Lifecycle Manager resource model on Itential Platform.

    Resource models define the structure, validation rules, and lifecycle workflows
    for network services and infrastructure components. They serve as templates
    for creating and managing resource instances.

    Args:
        ctx (Context): The FastMCP Context object
        name (str): Name of the resource model to create
        schema (dict): JSON Schema definition for resource structure and validation.
            Should include type, properties, and required fields without metadata.
        description (str | None): Human-readable description of the resource (optional)

    Returns:
        dict: Created resource model with the following fields:
            - _id: Unique identifier assigned by Itential
            - name: Resource model name
            - description: Resource description
            - schema: JSON Schema definition

    Raises:
        ValueError: If resource name already exists or schema format is invalid

    Notes:
        - Schema should contain core definition (type, properties, required) only
        - Metadata fields like $schema, title should be passed as separate parameters
        - Resource models enable structured lifecycle management of network services
    """
    await ctx.info("inside create_resource(...)")

    client = ctx.request_context.lifespan_context.get("client")

    existing = None
    try:
        existing = await describe_resource(ctx, name)
    except ValueError:
        pass

    if existing is not None:
        raise ValueError(f"resource {name} already exists")

    body = {
        "name": name,
        "schema": schema
    }

    if description is not None:
        body["description"] = description

    res = await client.post(
        "/lifecycle-manager/resources",
        json=body
    )

    data = res.json()["data"]

    return {
        "_id": data["_id"],
        "name": data["name"],
        "description": data["description"],
        "schema": data["schema"]
    }


async def describe_resource(
    ctx: Annotated[Context, Field(
        description="The FastMCP Context object"
    )],
    name: Annotated[str, Field(
        description="The name of the resource model to describe"
    )]
) -> dict:
    """
    Get detailed information about a Lifecycle Manager resource model.

    Args:
        ctx (Context): The FastMCP Context object
        name (str): Name of the resource model to retrieve

    Returns:
        dict: Resource model details with the following fields:
            - _id: Unique resource identifier
            - name: Resource model name
            - description: Resource description
            - schema: JSON Schema defining resource structure
            - actions: List of lifecycle actions associated with this resource

    Raises:
        ValueError: If the specified resource cannot be found
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
    Get all instances of a Lifecycle Manager resource from Itential Platform.

    Resource instances represent actual network services or infrastructure
    components created from resource models. They contain the specific data
    and state information for managed resources.

    Args:
        ctx (Context): The FastMCP Context object
        resource (str): Name of the resource model to get instances for

    Returns:
        list[dict]: List of resource instance objects with the following fields:
            - _id: Unique instance identifier
            - name: Instance name
            - description: Instance description
            - instanceData: Data object associated with this instance
            - lastAction: Last lifecycle action performed on the instance

    Raises:
        ValueError: If the specified resource model cannot be found
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
            })

        if len(results) == data["metadata"]["total"]:
            break

        skip += limit

    return results
