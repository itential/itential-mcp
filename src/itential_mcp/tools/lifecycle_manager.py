# Copyright (c) 2025 Itential, Inc
# GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)

from typing import Annotated

from pydantic import Field

from fastmcp import Context

from itential_mcp import functions
from itential_mcp import exceptions
from itential_mcp import errors

from itential_mcp.toolutils import tags


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
            - actions: List of lifecycle actions associated with this resource

    Notes:
        - Resource names are case sensitive
        - For each action the following fields will be returned:
            - name: The name of the action
            - type: The type of action (CREATE, UPDATE, DELETE)
            - schema: The input schema required to execute the action
    """
    await ctx.info("inside describe_resource(...)")

    client = ctx.request_context.lifespan_context.get("client")

    item = await client.resources.describe(name)

    actions = list()

    for ele in item["actions"]:
        action_element = {
            "name": ele["name"],
            "type": ele["type"],
            "schema": item["schema"]
        }

        if ele["preWorkflowJst"] is not None:
            try:
                jst = await client.transformations.describe(ele["preWorkflowJst"])
                action_element["schema"] = jst["incoming"]
            except exceptions.NotFoundError:
                return errors.resource_not_found(
                    f"The transformation for the {ele['name']} action could "
                     "not be found, please verify it exists and you have "
                     "permissions to access it"
                )

        elif ele["workflow"] is not None:
            try:
                wf = await client.workflows.describe(ele["workflow"])
                action_element["schema"] = wf["inputSchema"]
            except exceptions.NotFoundError:
                return errors.resource_not_found(
                    f"The workflow for the {ele['name']} action could not be "
                     "found,  please verify it exists and you have "
                     "permissions to access it"
                )

        actions.append(action_element)

    return {
        "_id": item["_id"],
        "name": item["name"],
        "description": item["description"],
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


async def describe_instance(
    ctx: Annotated[Context, Field(
        description="The FastMCP Context object"
    )],
    resource_name: Annotated[str, Field(
        description="The Lifecycle Manager resource name"
    )],
    instance_name: Annotated[str, Field(
        description="The instance name",
        default=None
    )]
) -> dict:
    """
    Get details about an instance of a Lifecycle Manager resource

    Gets the resource instance that is specified in the instance_name
    argument and returns the instance details.  This function will return
    an error if the instance does not exist

    Args:
        ctx (Context): The FastMCP Context object

        resource_name (str): Name of the resource to get the instance for

        instance_name (str): Name of the instance to return

    Returns:
        dict: An object that represents the instance with the following fields:
            - description: Short description of the instance
            - instanceData: Data about the instance
            - lastAction: The name of the last action performed on the instance
            - lastActionType: The type of action last performed.  This will be
                one of create, update or delete
            - lastActionStatus: Status of the last action perform.  This will
                be one of running, error, complete, canceled or paused

    Raises:
        NotFoundError: If the named instance cannot be found on the server
    """
    await ctx.info("inside describe_instance(...)")

    client = ctx.request_context.lifespan_context.get("client")

    resource_id = await functions.resource_name_to_id(ctx, resource_name)

    res = await client.get(
        f"/lifecycle-manager/resources/{resource_id}/instances",
        params={"equals[name]": instance_name}
    )

    json_data = res.json()

    if json_data["metadata"]["total"] != 1:
        raise exceptions.NotFoundError(f"unable to find instance {instance_name}")

    data = json_data["data"][0]

    return {
        "description": data["description"],
        "instanceData": data["instanceData"],
        "lastAction": data["lastAction"]["name"],
        "lastActionType": data["lastAction"]["type"],
        "lastActionStatus": data["lastAction"]["status"]
    }


@tags("experimental",)
async def run_action(
    ctx: Annotated[Context, Field(
        description="The FastMCP Context object"
    )],
    resource_name: Annotated[str, Field(
        description="The Lifecycle Manager resource name"
    )],
    action_name: Annotated[str, Field(
        description="The action to run"
    )],
    instance_name: Annotated[str, Field(
        description="The instance name",
        default=None
    )],
    instance_description: Annotated[str, Field(
        description="The instance description",
        default=None
    )],
    input_params: Annotated[dict, Field(
        description="The input parameters for the action",
        default=None
    )]
) -> dict:
    """
    Run an action that is associated with a Lifecycle Manager resource

    Args:
        ctx (Context): The FastMCP Context object

        resource_name (str): The name of the Lifecycle Manager resource model

        instance_name (str): The name of the instance associated with the
            Lifecycle Manager resource

        instance_description (str): A short description of the instance

        action_name (str): The name of the action to trigger on the instance of
            the Lifecycle Mmanager model

        input_params (dict): An optional object to use as the input parameters
            when running the action

    Returns:
        dict: Action details with the following fields:
            - jobId: Id used to get status updates using describe_job tool
            - startTime: The time the action was started on the server
            - status: The current status of the action
            - message: Status message about the action


    Raises:
        NotFoundError: If a resource, instance or action could not be found on
            the server
    """
    await ctx.info("inside run_action(...)")

    client = ctx.request_context.lifespan_context.get("client")

    res = await client.get(
        "/lifecycle-manager/resources",
        params={"equals[name]": resource_name}
    )

    data = res.json()
    if data["metadata"]["total"] != 1:
        raise exceptions.NotFoundError(f"unable to find resource {resource_name}")

    resource_id = data["data"][0]["_id"]

    action_id = None
    action_type = None

    for ele in data["data"][0]["actions"]:
        if ele["name"] == action_name:
            action_id = ele["_id"]
            action_type = ele["type"]
            break
    else:
        raise exceptions.NotFoundError(
            f"unable to find action {action_name} for resource {resource_name}",
        )

    body = {"actionId": action_id}

    if instance_name is not None:
        if action_type == "create":
            body["instanceName"] = instance_name
        else:
            instance = await functions.get_instance(ctx, instance_name, resource_name)
            body["instance"] = instance["_id"]
            if action_type == "delete" and input_params is None:
                input_params = instance["instanceData"]

    if input_params:
        body["inputs"] = input_params

    if instance_description:
        body["instanceDescription"] = instance_description

    res = await client.post(
        f"/lifecycle-manager/resources/{resource_id}/run-action",
        json=body
    )

    await ctx.info(res.text)

    json_data = res.json()
    data = json_data["data"]

    return {
        "message": json_data.get("message"),
        "startTime": data["startTime"],
        "jobId": data["jobId"],
        "status": data["status"],
    }
