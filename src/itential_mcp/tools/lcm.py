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
    Create a new Lifecycle Manager resource in Itential Platform

    This tool will create a new Lifecycle Manager resource model on the
    server. The resource model defines the structure and validation rules
    for resource instances.

    IMPORTANT: The schema parameter should contain ONLY the core schema
    definition (type, properties, required, etc.) WITHOUT JSON Schema
    metadata fields like $schema, title, description, or examples.

    Args:
        ctx (Context): The FastMCP Context object

        name (str):  The name of the resource to create. This should be a
            simple string identifier for the resource, e.g.,
            "PE-CE Network Connection" NOT a JSON object or schema document.

        schema (dict): The core schema definition object that defines the
            structure of the resource. This should include:
            - type: Usually "object"
            - properties: The properties definition
            - required: List of required property names

            DO NOT INCLUDE:
            - $schema: JSON Schema version reference
            - title: Schema title (use the 'name' parameter instead)
            - description: Schema description (use the 'description' parameter)
            - examples: Example values

            Example of CORRECT schema format:
            {
                "type": "object",
                "required": ["field1", "field2"],
                "properties": {
                    "field1": {
                        "type": "string",
                        "minLength": 1
                    },
                    "field2": {
                        "type": "number",
                        "minimum": 0
                    }
                }
            }

        description (str, optional): A human-readable description of what this
            resource represents. This is stored separately from the schema and
            used for documentation purposes.
            Example: "Provider Edge router with CE connections and billing info"

    Returns:
        dict: An object representing the created resource with fields:
            - _id: The unique identifier assigned by Itential
            - name: The resource name as provided
            - description: The description if provided
            - schema: The schema definition as stored
            - created: Timestamp of creation
            - createdBy: User who created the resource

    Raises:
        ValueError: Raised if:
            - The specified resource name already exists on Itential Platform
            - The schema format is invalid
            - Required parameters are missing or malformed

    Example Usage:
        # CORRECT way to create a resource:
        result = create_resource(
            ctx,
            name="Network Device",
            schema={
                "type": "object",
                "required": ["hostname", "ipAddress"],
                "properties": {
                    "hostname": {"type": "string"},
                    "ipAddress": {"type": "string", "format": "ipv4"}
                }
            },
            description="Basic network device configuration"
        )

        # WRONG - Don't pass the entire JSON Schema document as name:
        # result = create_resource(ctx, name=full_json_schema_doc, ...)

        # WRONG - Don't include metadata in schema:
        # result = create_resource(ctx, name="Device", schema={
        #     "$schema": "http://json-schema.org/draft-07/schema#",
        #     "title": "Device",  # Don't include this
        #     "type": "object",
        #     ...
        # })

        Notes:
            - The schema parameter defines the validation rules for resource instances
            - Once created, the resource can be used to create multiple instances
            - The schema follows JSON Schema draft-07 specification for validation
            - Metadata fields should be passed as separate parameters, not in the schema
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
            })

        if len(results) == data["metadata"]["total"]:
            break

        skip += limit

    return results
