# Copyright (c) 2025 Itential, Inc
# GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)

import time

from typing import Annotated

from pydantic import Field

from fastmcp import Context

from itential_mcp import errors


__tags__ = ("adapters",)


async def _get_adapter_health(
    ctx: Context,
    name: str
) -> dict:
    """
    Get the health status of a specific adapter.

    Args:
        ctx (Context): The FastMCP Context object
        name (str): The case-sensitive name of the adapter. Use `get_adapters`
            to see available adapters.

    Returns:
        dict: Adapter health data containing status and configuration information

    Raises:
        NotFoundError: If the specified adapter cannot be found
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
        raise errors.NotFoundError(f"unable to find adapter {name}")

    return data


async def get_adapters(
    ctx: Annotated[Context, Field(
        description="The FastMCP Context object"
    )]
) -> dict:
    """
    Get all adapters configured on the Itential Platform instance.

    Args:
        ctx (Context): The FastMCP Context object

    Returns:
        list[dict]: List of adapter objects with the following fields:
            - name: The adapter name
            - package: The NodeJS package comprising the adapter
            - version: The adapter version
            - description: The adapter description
            - state: Operational state (DEAD, STOPPED, RUNNING, DELETED)
    """
    await ctx.info("inside get_adapters(...)")

    client = ctx.request_context.lifespan_context.get("client")

    res = await client.get("/health/adapters")

    data = res.json()

    results = list()

    for ele in data["results"]:
        results.append({
            "name": ele["id"],
            "package": ele.get("package_id"),
            "version": ele["version"],
            "description": ele.get("description"),
            "state": ele["state"],
        })

    return results


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
) -> dict:
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
        dict: Start operation result
            - name: The adapter name
            - state: Final adapter state (RUNNING, DEAD, DELETED, STOPPED)

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

            time.sleep(1)
            timeout -= 1

    elif state in ("DEAD", "DELETED"):
        raise errors.InvalidStateError(f"adapter `{name}` is `{state}`")

    if timeout == 0:
        raise errors.TimeoutExceededError()

    return {
        "name": name,
        "state": state
    }


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
) -> dict:
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
        dict: Stop operation result
            - name: The adapter name
            - state: Final adapter state (RUNNING, DEAD, DELETED, STOPPED)

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

            time.sleep(1)
            timeout -= 1

    elif state in ("DEAD", "DELETED"):
        raise errors.InvalidStateError(f"adapter `{name}` is `{state}`")

    if timeout == 0:
        raise errors.TimeoutExceededError()

    return {
        "name": name,
        "state": state
    }


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
) -> dict:
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
        dict: Restart operation result
            - name: The adapter name
            - state: Final adapter state (RUNNING, DEAD, DELETED, STOPPED)

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

            time.sleep(1)
            timeout -= 1

    elif state in ("DEAD", "DELETED", "STOPPED"):
        raise errors.InvalidStateError(f"adapter `{name}` is `{state}`")

    if timeout == 0:
        raise errors.TimeoutExceededError()

    return {
        "name": name,
        "state": state
    }
