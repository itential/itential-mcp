# Copyright (c) 2025 Itential, Inc
# GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)

import asyncio

from typing import Annotated

from pydantic import Field

from fastmcp import Context

from itential_mcp import exceptions
from itential_mcp.models import adapters as models


__tags__ = ("adapters",)


async def _get_adapter_health(ctx: Context, name: str) -> dict:
    """
    Get health information for a specific adapter.

    Args:
        ctx (Context): The FastMCP Context object
        name (str): Adapter name to get health for

    Returns:
        dict: Adapter health data from the platform

    Raises:
        NotFoundError: If the adapter is not found
    """
    client = ctx.request_context.lifespan_context.get("client")

    res = await client.get(
        "/health/adapters",
        params={
            "equals": name,
            "equalsField": "id"
        }
    )

    data = res.json()

    if data["total"] != 1:
        raise exceptions.NotFoundError(f"unable to find adapter {name}")

    return data


async def get_adapters(
    ctx: Annotated[Context, Field(
        description="The FastMCP Context object"
    )]
) -> models.GetAdaptersResponse:
    """
    Get all adapters configured on the Itential Platform instance.

    Args:
        ctx (Context): The FastMCP Context object

    Returns:
        GetAdaptersResponse: Response object that provides the list of
            configured adapters from the server
    """
    await ctx.info("inside get_adapters(...)")

    client = ctx.request_context.lifespan_context.get("client")

    res = await client.get("/health/adapters")

    data = res.json()

    elements = list()

    for ele in data["results"]:
        elements.append(models.GetAdaptersElement(
            name=ele["id"],
            package=ele.get("package_id"),
            version=ele["version"],
            description=ele.get("description"),
            state=ele["state"]
        ))

    return models.GetAdaptersResponse(elements)


async def start_adapter(
    ctx: Annotated[Context, Field(
        description="The FastMCP Context object"
    )],
    name: Annotated[str, Field(
        description="The name of the adapter to start"
    )],
    timeout: Annotated[int, Field(
        description="Timeout waiting for adapter to start",
        default=10
    )]
) -> models.StartAdapterResponse:
    """
    Start an adapter on Itential Platform.

    Behavior based on current adapter state:
    - RUNNING: No action taken (already started)
    - STOPPED: Attempts to start and waits for RUNNING state
    - DEAD/DELETED: Raises InvalidStateError (cannot start)

    Args:
        ctx (Context): The FastMCP Context object
        name (str): Case-sensitive adapter name. Use `get_adapters` to see available adapters.
        timeout (int): Seconds to wait for adapter to reach RUNNING state

    Returns:
        StartAdapterResponse: Response object that indicates the status of
            the start adapter operation

    Raises:
        TimeoutExceededError: If adapter doesn't reach RUNNING state within timeout
        InvalidStateError: If adapter is in DEAD or DELETED state

    Notes:
        - Adapter name is case-sensitive
        - Function polls adapter state every second until timeout
    """
    await ctx.info("inside start_adapter(...)")

    client = ctx.request_context.lifespan_context.get("client")

    data = await _get_adapter_health(ctx, name)
    state = data["results"][0]["state"]

    if state == "STOPPED":
        await client.put(f"/adapters/{name}/start")

        while timeout:
            data = await _get_adapter_health(ctx, name)
            state = data["results"][0]["state"]

            if state == "RUNNING":
                break

            await asyncio.sleep(1)
            timeout -= 1

    elif state in ("DEAD", "DELETED"):
        raise exceptions.InvalidStateError(f"adapter `{name}` is `{state}`")

    if timeout == 0:
        raise exceptions.TimeoutExceededError()

    return models.StartAdapterResponse(name=name, state=state)


async def stop_adapter(
    ctx: Annotated[Context, Field(
        description="The FastMCP Context object"
    )],
    name: Annotated[str, Field(
        description="The name of the adapter to stop"
    )],
    timeout: Annotated[int, Field(
        description="Timeout waiting for adapter to stop",
        default=10
    )]
) -> models.StopAdapterResponse:
    """
    Stop an adapter on Itential Platform.

    Behavior based on current adapter state:
    - RUNNING: Attempts to stop and waits for STOPPED state
    - STOPPED: No action taken (already stopped)
    - DEAD/DELETED: Raises InvalidStateError (cannot stop)

    Args:
        ctx (Context): The FastMCP Context object
        name (str): Case-sensitive adapter name. Use `get_adapters` to see available adapters.
        timeout (int): Seconds to wait for adapter to reach STOPPED state

    Returns:
        StopAdapterResponse: Response object that indicates the status of
            the stop adapter operation

    Raises:
        TimeoutExceededError: If adapter doesn't reach STOPPED state within timeout
        InvalidStateError: If adapter is in DEAD or DELETED state

    Notes:
        - Adapter name is case-sensitive
        - Function polls adapter state every second until timeout
    """
    await ctx.info("inside stop_adapter(...)")

    client = ctx.request_context.lifespan_context.get("client")

    data = await _get_adapter_health(ctx, name)
    state = data["results"][0]["state"]

    if state == "RUNNING":
        await client.put(f"/adapters/{name}/stop")

        while timeout:
            data = await _get_adapter_health(ctx, name)

            state = data["results"][0]["state"]

            if state == "STOPPED":
                break

            await asyncio.sleep(1)
            timeout -= 1

    elif state in ("DEAD", "DELETED"):
        raise exceptions.InvalidStateError(f"adapter `{name}` is `{state}`")

    if timeout == 0:
        raise exceptions.TimeoutExceededError()

    return models.StopAdapterResponse(name=name, state=state)


async def restart_adapter(
    ctx: Annotated[Context, Field(
        description="The FastMCP Context object"
    )],
    name: Annotated[str, Field(
        description="The name of the adapter to restart"
    )],
    timeout: Annotated[int, Field(
        description="Timeout waiting for adapter to restart",
        default=10
    )]
) -> models.RestartAdapterResponse:
    """
    Restart an adapter on Itential Platform.

    Behavior based on current adapter state:
    - RUNNING: Attempts to restart and waits for RUNNING state
    - STOPPED/DEAD/DELETED: Raises InvalidStateError (cannot restart)

    Args:
        ctx (Context): The FastMCP Context object
        name (str): Case-sensitive adapter name. Use `get_adapters` to see available adapters.
        timeout (int): Seconds to wait for adapter to return to RUNNING state

    Returns:
        ResartAdapterResponse: Response object that indicates the status of
            the ressart adapter operation

    Raises:
        TimeoutExceededError: If adapter doesn't return to RUNNING state within timeout
        InvalidStateError: If adapter is not in RUNNING state initially

    Notes:
        - Adapter name is case-sensitive
        - Only RUNNING adapters can be restarted
        - For STOPPED adapters, use `start_adapter` instead
        - Function polls adapter state every second until timeout
    """
    await ctx.info("inside restart_adapter(...)")

    client = ctx.request_context.lifespan_context.get("client")

    data = await _get_adapter_health(ctx, name)
    state = data["results"][0]["state"]

    if state == "RUNNING":
        await client.put(f"/adapters/{name}/restart")

        while timeout:
            data = await _get_adapter_health(ctx, name)

            state = data["results"][0]["state"]

            if state == "RUNNING":
                break

            await asyncio.sleep(1)
            timeout -= 1

    elif state in ("DEAD", "DELETED", "STOPPED"):
        raise exceptions.InvalidStateError(f"adapter `{name}` is `{state}`")

    if timeout == 0:
        raise exceptions.TimeoutExceededError()

    return models.RestartAdapterResponse(name=name, state=state)
