# Copyright (c) 2025 Itential, Inc
# GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

import inspect

from typing import Tuple, Callable

from pydantic import BaseModel

from fastmcp import Context

from itential_mcp import config
from itential_mcp.platform import PlatformClient
from itential_mcp.core import exceptions
from itential_mcp.utilities import json as jsonutils

from itential_mcp.tools import operations_manager


async def _get_trigger(platform_client: PlatformClient, t: config.EndpointTool):
    """Retrieve a workflow trigger configuration from the platform.

    Searches for an automation by name and then finds the associated trigger
    within that automation. This is used to get trigger details needed for
    workflow execution.

    Args:
        platform_client (PlatformClient): The platform client for API communication.
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
    data: dict | str | None = None,
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

    # Parse data if it's a JSON string
    if isinstance(data, str):
        data = jsonutils.loads(data)

    return await operations_manager.start_workflow(
        ctx, route_name=trigger["routeName"], data=data
    )


async def new(
    t: config.EndpointTool, platform_client: PlatformClient
) -> Tuple[Callable, str]:
    """Create a new bound workflow function with description.

    Creates a bound version of the start_workflow function along with a description
    generated from the trigger configuration. This is used during tool binding to
    create the actual callable function that will be registered with MCP.

    Args:
        t (config.EndpointTool): The endpoint tool configuration.
        platform_client (PlatformClient): The platform client for API communication.

    Returns:
        Tuple[Callable, str]: A tuple containing the start_workflow function and
            its description string including schema information.

    Raises:
        exceptions.NotFoundError: If the automation or trigger cannot be found.
    """
    trigger = await _get_trigger(platform_client, t)

    description = trigger["description"] or ""
    description = inspect.cleandoc(
        f"""
        {description}\nArgs:\ndata (dict): Object that provides input
        to the tool using the following input schema:\n{trigger["schema"]}
        """
    )

    return start_workflow, description
