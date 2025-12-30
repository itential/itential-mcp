# Copyright (c) 2025 Itential, Inc
# GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from typing import Annotated

from pydantic import Field

from fastmcp import Context

from itential_mcp.utilities import json as jsonutils
from itential_mcp.core import exceptions

from itential_mcp.models import gateway_manager as models


__tags__ = ("gateway_manager",)


async def get_services(
    ctx: Annotated[Context, Field(description="The FastMCP Context object")],
) -> models.GetServicesResponse:
    """
    Get the list of all know services from Itential Platform Gateway Manager

    Args:
        ctx (Context): The FastMCP Context object

    Returns:
        GetServicesResponse: List of service objects with the following fields:
            - name: The service name
            - cluster: The cluster name
            - type: The service type (ansible-playbook, python-script, opentofu-plan)
            - description: Short description of the service
            - decorator: JSON schema that defines the service input

    Raises:
        Exception: If there is an error retrieving services from Gateway Manager
    """
    await ctx.info("inside get_services(...)")

    client = ctx.request_context.lifespan_context.get("client")

    data = await client.gateway_manager.get_services()

    results = []

    for ele in data:
        results.append(
            models.ServiceElement(
                name=ele["service_metadata"]["name"],
                cluster=ele["service_metadata"]["location"],
                type=ele["service_metadata"]["type"],
                description=ele["service_metadata"]["description"],
                decorator=ele["service_metadata"]["decorator"],
            )
        )

    return models.GetServicesResponse(results)


async def get_gateways(
    ctx: Annotated[Context, Field(description="The FastMCP Context object")],
) -> models.GetGatewaysResponse:
    """
    Get the list of all know services from Itential Platform Gateway Manager

    Args:
        ctx (Context): The FastMCP Context object

    Returns:
        GetGatewaysResponse: List of gateway objects with the following fields:
            - name: The gateway name
            - cluster: The cluster name
            - description: Short description of the gateway
            - status: Current status of the gateway connection
            - enabled: Whether or not the gateway is enabled and usable

    Raises:
        Exception: If there is an error retrieving gateways from Gateway Manager
    """
    await ctx.info("inside get_gateways(...)")

    client = ctx.request_context.lifespan_context.get("client")

    data = await client.gateway_manager.get_gateways()

    results = []

    # XXX (privateip) The results are filtered to only return gateways that
    # have a connection status of `connected` since we do not care about
    # disconnected gateways.  Additionally if a gateway status is disconnected,
    # the API does not return the name property.

    # Handle both response formats: direct array or wrapped in "results" key
    gateway_list = data.get("results", data) if isinstance(data, dict) else data

    for ele in gateway_list:
        if (
            ele.get("connection_status") == "connected"
            or ele.get("status") == "connected"
        ):
            results.append(
                models.GatewayElement(
                    name=ele.get("name", ele.get("gateway_name", "")),
                    cluster=ele.get("cluster", ele.get("cluster_id", "")),
                    description=ele.get("description", ""),
                    status=ele.get("status", ele.get("connection_status", "")),
                    enabled=ele.get("enabled", False),
                )
            )

    return models.GetGatewaysResponse(results)


async def run_service(
    ctx: Annotated[Context, Field(description="The FastMCP Context object")],
    name: Annotated[str, Field(description="The name of the service to run")],
    cluster: Annotated[
        str, Field(description="The name of the cluster where the service lives")
    ],
    input_params: Annotated[
        dict | str | None,
        Field(
            description="Optional input parameters to pass to the service", default=None
        ),
    ],
) -> models.RunServiceResponse:
    """
    Run an existing service using the optional input parameters

    Args:
        ctx (Context): The FastMCP Context object
        name (str): The name of the service to run
        cluster (str): The name of the cluster that owns the service
        input_params (dict): Optional input parameters to pass to the service

    Returns:
        RunServiceResponse: An object that represents output from the service
            with the following fields:
                - stdout: The output sent to stdout
                - stderr: The output sent to stderr
                - return_code: The return code generated by the service
                - start_time: The start time when the service was started
                - end_time: The end time when the service run completed
                - elapsed_time: The number of seconds the service ran for

    Raises:
        Exception: If there is an error running the service on Gateway Manager
    """
    await ctx.info("inside run_service(...)")

    client = ctx.request_context.lifespan_context.get("client")

    # Parse input_params if it's a JSON string
    if isinstance(input_params, str):
        input_params = jsonutils.loads(input_params)

    res = await client.gateway_manager.run_service(name, cluster, input_params)

    if "error" in res:
        raise ValueError(res["error"]["data"])

    # Attempt to parse stdout as JSON, but keep raw string if parsing fails
    try:
        stdout_json = jsonutils.loads(res["result"]["stdout"])
        res["result"]["stdout"] = stdout_json
    except (exceptions.ValidationException, ValueError, TypeError):
        # Not valid JSON, keep as raw string
        pass

    return models.RunServiceResponse(**res["result"])
