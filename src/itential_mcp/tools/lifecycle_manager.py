# Copyright (c) 2025 Itential, Inc
# GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)

import json

from typing import Annotated

from pydantic import Field

from fastmcp import Context

from itential_mcp import exceptions
from itential_mcp import errors
from itential_mcp.models.lifecycle_manager import (
    GetResourcesResponse,
    GetResourcesElement,
    CreateResourceResponse,
    DescribeResourceResponse,
    GetInstancesResponse,
    GetInstancesElement,
    DescribeInstanceResponse,
    RunActionResponse,
    LastAction,
    Action
)


__tags__ = ("lifecycle_manager",)


async def get_resources(
    ctx: Annotated[Context, Field(
        description="The FastMCP Context object"
    )]
) -> GetResourcesResponse:
    """
    Get all Lifecycle Manager resource models from Itential Platform.

    Lifecycle Manager resources define data models and workflows for managing
    network services and infrastructure components throughout their lifecycle.
    They provide structured templates for creating and managing resource instances.

    Args:
        ctx (Context): The FastMCP Context object

    Returns:
        GetResourcesResponse: List of resource model objects with the following fields:
            - name: Resource model name
            - description: Resource model description
    """
    await ctx.info("inside get_resources(...)")

    client = ctx.request_context.lifespan_context.get("client")

    res = await client.lifecycle_manager.get_resources()

    results = []

    for ele in res:
        results.append(GetResourcesElement(
            name=ele["name"],
            description=ele.get("description"),
        ))

    return GetResourcesResponse(root=results)


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
) -> CreateResourceResponse:
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
        CreateResourceResponse: Created resource model response

    Raises:
        ValueError: If resource name already exists or schema format is invalid

    Notes:
        - Schema should contain core definition (type, properties, required) only
        - Metadata fields like $schema, title should be passed as separate parameters
        - Resource models enable structured lifecycle management of network services
    """
    await ctx.info("inside create_resource(...)")

    client = ctx.request_context.lifespan_context.get("client")

    try:
        await client.lifecycle_manager.describe_resource(name)
        return errors.resource_already_exists(
            f"resource {name} already exists"
        )
    except exceptions.NotFoundError:
        # Resource doesn't exist, we can create it
        pass

    await client.lifecycle_manager.create_resource(name, schema, description)

    return CreateResourceResponse()


async def describe_resource(
    ctx: Annotated[Context, Field(
        description="The FastMCP Context object"
    )],
    name: Annotated[str, Field(
        description="The name of the resource model to describe"
    )]
) -> DescribeResourceResponse:
    """
    Get detailed information about a Lifecycle Manager resource model.

    Args:
        ctx (Context): The FastMCP Context object
        name (str): Name of the resource model to retrieve

    Returns:
        DescribeResourceResponse: Resource model details with the following fields:
            - name: Resource model name
            - description: Resource description
            - actions: List of lifecycle actions associated with this resource

    Notes:
        - Resource names are case sensitive
        - For each action the following fields will be returned:
            - name: The name of the action
            - type: The type of action (CREATE, UPDATE, DELETE)
            - input_schema: The input schema required to execute the action
    """
    await ctx.info("inside describe_resource(...)")

    client = ctx.request_context.lifespan_context.get("client")

    try:
        item = await client.lifecycle_manager.describe_resource(name)
    except exceptions.NotFoundError:
        return errors.resource_not_found(f"resource {name} not found on the server")

    actions = []

    for ele in item["actions"]:
        action_schema = item["schema"]

        if ele["preWorkflowJst"] is not None:
            try:
                jst = await client.transformations.describe_transformation(ele["preWorkflowJst"])
                action_schema = jst["incoming"]
            except exceptions.NotFoundError:
                return errors.resource_not_found(
                    f"The transformation for the {ele['name']} action could "
                     "not be found, please verify it exists and you have "
                     "permissions to access it"
                )

        elif ele["workflow"] is not None:
            try:
                wf = await client.automation_studio.describe_workflow(ele["workflow"])
                action_schema = wf["inputSchema"]
            except exceptions.NotFoundError:
                return errors.resource_not_found(
                    f"The workflow for the {ele['name']} action could not be "
                     "found,  please verify it exists and you have "
                     "permissions to access it"
                )

        actions.append(Action(
            name=ele["name"],
            type=ele["type"],
            input_schema=action_schema
        ))

    return DescribeResourceResponse(
        name=item["name"],
        description=item.get("description"),
        actions=actions
    )


async def get_instances(
    ctx: Annotated[Context, Field(
        description="The FastMCP Context object"
    )],
    resource_name: Annotated[str, Field(
        description="The Lifecycle Manager resource name to retrieve instances for"
    )]
) -> GetInstancesResponse:
    """
    Get all instances of a Lifecycle Manager resource from Itential Platform.

    Resource instances represent actual network services or infrastructure
    components created from resource models. They contain the specific data
    and state information for managed resources.

    Args:
        ctx (Context): The FastMCP Context object
        resource_name (str): Name of the resource model to get instances for

    Returns:
        GetInstancesResponse: List of resource instance objects with the following fields:
            - name: Instance name
            - description: Instance description
            - instance_data: Data object associated with this instance
            - last_action: Last lifecycle action performed on the instance
    """
    await ctx.info("inside get_instances(...)")

    client = ctx.request_context.lifespan_context.get("client")

    data = await client.lifecycle_manager.get_instances(resource_name)

    results = []

    for ele in data:
        results.append(GetInstancesElement(
            name=ele["name"],
            description=ele.get("description"),
            instance_data=ele["instanceData"],
            last_action=LastAction(
                name=ele["lastAction"]["name"],
                type=ele["lastAction"]["type"],
                status=ele["lastAction"]["status"]
            )
        ))

    return GetInstancesResponse(root=results)


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
) -> DescribeInstanceResponse:
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
        DescribeInstanceResponse: An object that represents the instance with the following fields:
            - description: Short description of the instance
            - instance_data: Data about the instance
            - last_action: The last action performed on the instance

    Raises:
        NotFoundError: If the named instance cannot be found on the server
    """
    await ctx.info("inside describe_instance(...)")

    client = ctx.request_context.lifespan_context.get("client")

    data = await client.lifecycle_manager.describe_instance(
        resource_name, instance_name
    )

    return DescribeInstanceResponse(
        description=data.get("description"),
        instance_data=data["instanceData"],
        last_action=LastAction(
            name=data["lastAction"]["name"],
            type=data["lastAction"]["type"],
            status=data["lastAction"]["status"]
        )
    )


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
) -> RunActionResponse:
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
        RunActionResponse: Action details with the following fields:
            - job_id: Id used to get status updates using describe_job tool
            - start_time: The time the action was started on the server
            - status: The current status of the action
            - message: Status message about the action


    Raises:
        NotFoundError: If a resource, instance or action could not be found on
            the server
    """
    await ctx.info("inside run_action(...)")

    client = ctx.request_context.lifespan_context.get("client")

    try:
        json_data = await client.lifecycle_manager.run_action(
            resource_name, action_name, instance_name, instance_description,
            input_params
        )
    except exceptions.NotFoundError:
        return errors.resource_not_found(
            f"Could not find a resource named {resource_name}"
        )
    except exceptions.ClientException as exc:
        return errors.bad_request(exc.message)
    except exceptions.ItentialMcpException as exc:
        json_data = json.loads(exc.message)
        return errors.bad_request(json_data["message"])

    return RunActionResponse(
        message=json_data.get("message"),
        start_time=json_data["data"]["startTime"],
        job_id=json_data["data"]["jobId"],
        status=json_data["data"]["status"]
    )
