# Copyright (c) 2025 Itential, Inc
# GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)

import inspect

from typing import Tuple, Callable, Annotated

from pydantic import BaseModel, Field

from fastmcp import Context

from itential_mcp import config
from itential_mcp import client
from itential_mcp import exceptions

from itential_mcp.tools import operations_manager


async def _get_trigger(platform_client: client.PlatformClient, t: config.EndpointTool):
    """Retrieve a workflow trigger configuration from the platform.

    Searches for an automation by name and then finds the associated trigger
    within that automation. This is used to get trigger details needed for
    workflow execution.

    Args:
        platform_client (client.PlatformClient): The platform client for API communication.
        t (config.EndpointTool): The endpoint tool configuration containing automation
            and trigger names.

    Returns:
        dict: The trigger configuration data from the platform.

    Raises:
        exceptions.NotFoundError: If the automation or trigger cannot be found.
    """
    res = await platform_client.client.get(
        "/operations-manager/automations",
        params={"equals": t.automation, "equalsField": "name"},
    )

    json_data = res.json()

    for ele in json_data["data"]:
        if ele["name"] == t.automation:
            automation_id = ele["_id"]
            break
    else:
        raise exceptions.NotFoundError(f"automation {t.automation} could not be found")

    res = await platform_client.client.get(
        "/operations-manager/triggers",
        params={"equals": automation_id, "equalsField": "actionId"},
    )

    json_data = res.json()

    trigger = None

    for ele in json_data["data"]:
        if ele["name"] == t.name:
            trigger = ele
            break
    else:
        raise exceptions.NotFoundError(f"trigger {t.name} could not be found")

    return trigger


async def start_workflow(
    ctx: Context,
    _tool_config: config.EndpointTool | None = None,
    data: dict | None = None,
) -> BaseModel:
    """Start a workflow using the configured endpoint trigger.

    Retrieves the trigger configuration from the platform and delegates to the
    operations manager to start the workflow execution. This function serves as
    a bridge between the binding configuration and the actual workflow execution.

    Args:
        ctx (Context): The FastMCP context containing request and lifecycle information.
        _tool_config (config.EndpointTool | None): The endpoint tool configuration.
            Defaults to None.
        data (dict | None): Optional input data to pass to the workflow. Defaults to None.

    Returns:
        BaseModel: The workflow execution response from the operations manager.

    Raises:
        exceptions.NotFoundError: If the automation or trigger cannot be found.
        Any exceptions from operations_manager.start_workflow.
    """
    platform_client = ctx.request_context.lifespan_context.get("client")

    trigger = await _get_trigger(platform_client, _tool_config)

    return await operations_manager.start_workflow(
        ctx, route_name=trigger["routeName"], data=data
    )


async def new(
    t: config.EndpointTool,
    platform_client: client.PlatformClient
) -> Tuple[Callable, str]:
    """Create a new bound workflow function with description.

    Creates a bound version of the start_workflow function along with a description
    generated from the trigger configuration. This is used during tool binding to
    create the actual callable function that will be registered with MCP.

    Args:
        t (config.EndpointTool): The endpoint tool configuration.
        platform_client (client.PlatformClient): The platform client for API communication.

    Returns:
        Tuple[Callable, str]: A tuple containing the start_workflow function and
            its description string including schema information.

    Raises:
        exceptions.NotFoundError: If the automation or trigger cannot be found.
    """
    trigger = await _get_trigger(platform_client, t)

    description = trigger["description"] or ""
    schema = trigger.get("schema", {})
    properties = schema.get("properties", {})
    
    # Generate the function dynamically with explicit parameters
    required_params = schema.get('required', [])
    
    # Build the parameter definitions and function body
    required_param_definitions = []
    optional_param_definitions = []
    param_names = []
    annotations = {
        'ctx': Annotated[Context, Field(description="The FastMCP Context object")],
        '_tool_config': config.EndpointTool | None,
        'return': BaseModel
    }
    
    for param_name, param_info in properties.items():
        param_type = str  # Default to string type
        param_description = param_info.get('description', param_info.get('title', param_name))
        param_names.append(param_name)
        
        # Check if parameter is required
        if param_name in required_params:
            required_param_definitions.append(f"{param_name}")
            annotations[param_name] = Annotated[param_type, Field(description=param_description)]
        else:
            optional_param_definitions.append(f"{param_name}=None")
            annotations[param_name] = Annotated[param_type | None, Field(description=param_description, default=None)]
    
    # Create the function code with proper parameter order (required first, then optional)
    all_params = required_param_definitions + ["_tool_config=None"] + optional_param_definitions
    param_list = ", ".join(all_params) if all_params else ""
    data_assembly = "{" + ", ".join([f'"{name}": {name}' for name in param_names]) + "}"
    
    # Create function dynamically using exec
    func_code = f"""
async def dynamic_workflow_function(ctx, {param_list}):
    '''Dynamically created workflow function with proper schema.'''
    # Assemble data object from parameters
    data = {data_assembly}
    # Filter out None values for optional parameters
    data = {{k: v for k, v in data.items() if v is not None}}
    
    # Use the tool config from the closure instead of the injected one
    return await start_workflow(ctx, _tool_config=t, data=data)
"""
    
    # Execute the function definition
    exec_globals = globals().copy()
    exec_globals.update({
        'start_workflow': start_workflow,
        't': t
    })
    local_vars = {}
    exec(func_code, exec_globals, local_vars)
    dynamic_workflow_function = local_vars['dynamic_workflow_function']
    
    # Set the annotations on the function
    dynamic_workflow_function.__annotations__ = annotations

    # Set the function name for better debugging
    dynamic_workflow_function.__name__ = f"workflow_{t.tool_name}"
    
    return dynamic_workflow_function, description
