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

from itential_mcp.tools import gateway_manager


async def _get_service(platform_client: PlatformClient, t: config.EndpointTool):
    """Retrieve a service from the platform based on tool configuration.

    Args:
        platform_client (PlatformClient): The platform client instance for API communication.
        t (config.EndpointTool): The tool configuration containing service identification details.

    Returns:
        dict: The service object containing metadata and configuration.

    Raises:
        exceptions.NotFoundError: If the specified service name cannot be found in the platform.
    """
    res = await platform_client.gateway_manager.get_services()

    for ele in res:
        if ele["service_metadata"]["name"] == t.name:
            service = ele
            break
    else:
        raise exceptions.NotFoundError(f"service {t.name} could not be found")

    return service


async def run_service(
    ctx: Context,
    _tool_config: config.Tool | None = None,
    input_params: dict | str | None = None,
) -> BaseModel:
    """Execute a service on the Itential Platform using the configured tool settings.

    Args:
        ctx (Context): The FastMCP context object containing request context and lifecycle information.
        _tool_config (config.Tool | None): The tool configuration object containing service details.
            Defaults to None.
        input_params (dict | None): Optional input parameters to pass to the service execution.
            Defaults to None.

    Returns:
        BaseModel: The response from the service execution containing results and status information.

    Raises:
        exceptions.NotFoundError: If the configured service cannot be found on the platform.
    """
    platform_client = ctx.request_context.lifespan_context.get("client")

    service = await _get_service(platform_client, _tool_config)

    service_name = service["service_metadata"]["name"]
    cluster = service["service_metadata"]["location"]

    # Parse input_params if it's a JSON string
    if isinstance(input_params, str):
        input_params = jsonutils.loads(input_params)

    return await gateway_manager.run_service(
        ctx, name=service_name, cluster=cluster, input_params=input_params
    )


async def new(
    t: config.ServiceTool, platform_client: PlatformClient
) -> Tuple[Callable, str]:
    """Create a new service binding with callable function and documentation.

    This function dynamically creates a service binding by retrieving service metadata
    from the platform and generating appropriate documentation including input schema
    information when available.

    Args:
        t (config.ServiceTool): The service tool configuration containing service identification.
        platform_client (PlatformClient): The platform client instance for API communication.

    Returns:
        Tuple[Callable, str]: A tuple containing the service execution function and its
            documentation string with schema information.

    Raises:
        exceptions.NotFoundError: If the specified service cannot be found on the platform.
    """
    service = await _get_service(platform_client, t)

    description = service["service_metadata"]["description"] or ""
    decorator = service["service_metadata"]["decorator"]

    if decorator:
        description = inspect.cleandoc(
            f"""
            {description}\nArgs:\ndata (dict): Object that provides input
            to the tool using the following input schema:\n{decorator}
            """
        )

    return run_service, description
