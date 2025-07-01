# Copyright (c) 2025 Itential, Inc
# GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)

import time

from typing import Annotated

from pydantic import Field

from fastmcp import Context

from itential_mcp import errors


async def _get_adapter_health(
    ctx: Context,
    name: str
) -> dict:
    """
    Get the health of an adapter

    This internal function will return the the health of the adapter
    specified by the name argument.  If the specified adapter does not
    exist, the function will raise a NotFoundError.   If the adapter
    does exist, it will be returned as a dict object.

    Args:
        ctx (Context): The FastMCP Context object

        name (str): The name of the adapter to get.  This argument is
            case senstive.  To get a list of all available adapters on
            the server see ```get_adapters```

    Returns:
        dict: An object the represents the adapter health

    Raises:
        NotFoundError: If the adapter specified by name cannot be found
            on the server, a NotFoundError is returned.
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
    Get all adapters from Itential Platform

    This tool will retrieve all of the adapters configured on the instance
    of Itential Plaform and return them.   The returned list will include
    the adapter name, package, version, description and running state.

    Args:
        ctx (Context): The FastMCP Context object

    Returns:
        list[dict]: A list of objects where each object represents an
            adapter with the following fields:
            - name: The name of the adapter
            - package: The NodeJS package that comprises the adapter
            - version: The version of the adapter on the server
            - description: The adapter description
            - state: The current operational state of the appliacation.  Valid
                states are DEAD, STOPPED, RUNNING, DELETED

    Raises:
        None
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
    Start an adapter on Itential Platform

    This tool will start an adapter on an Itential Platform server.  The
    name argument defines the name of the adapter to start.  If the
    adapter is already in a running state. this tool will not attempt
    any further action.

    The name argument is case sensitive and must be a valid adapter
    defined on Itential Platform.  The list of adapters running on
    the server can be found using the get_adapters tool.

    If the adapter is in a STOPPED state, this tool will attempt to start
    the adapter.   It will check to see if the adapter started.  If
    the adapter hasn't started within the timeout period, a
    TimeoutExceededError error is raised

    If the adapter is in either the DEAD or DELETED state, an
    InvalidStateError is raised.

    Args:
        ctx (Context): The FastMCP Context object

        name (str): The name of the adapter to start

        timeout (int): The timeout in seconds this tool should wait for the
            adapter to start successfully.  If the adapter doesn't
            start before the timeout expires, a TimeoutExceeded exception
            is raised

    Returns:
        dict: An object representing the start operation
            - name: The name of the adapter
            - status: The state of the start operation.  Valid values are
                RUNNING, DEAD, DELETED, STOPPED

    Raises:
        TimeoutExceededError: If the adapter isn't in a RUNNING state
            before the timeout expires

        InvalidStateError: if the adapter is in either the DEAD or
            DELETED state, this exception is raised

    Notes:
        - The adapter name argument is case senstive
        - The timeout value is set in seconds

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
        description="Timeout waiting for adapter to start",
        default=10
    )]
) -> dict:
    """
    Stop an adapter on Itential Platform

    This tool will stop an adapter that is currently in a running
    state on the server.  If the adapter is already stopped this
    tool will not perform any further action.

    The name argument specifies the name of the adapter to stop.  The
    value for name must be a valid case senstive name.  The list of
    adapters can be found by calling the get_adapters tool.  If
    the specified name is not a valid adapter name, this tool will
    raise a NotFoundError.

    The timeout value sets the number of seconds to wait to verify the
    adapter has stopped.  If the timeout value expires before the
    adapter reaches a stopped state, this tool will raise a
    TimeoutExceededError.

    If the adapter is in either the DEAD or DELETED state, an
    InvalidStateError is raised.

    Args:
        ctx (Context): The FastMCP Context object

        name (str): The name of the adapter to start

        timeout (int): The timeout in seconds this tool should wait for the
            adapter to stop successfully.  If the adapter doesn't
            stop before the timeout expires, a TimeoutExceeded exception
            is raised

    Returns:
        dict: An object representing the stop operation
            - name: The name of the adapter
            - status: The state of the start operation.  Valid values are
                RUNNING, DEAD, DELETED, STOPPED

    Raises:
        TimeoutExceededError: If the adapter isn't in a STOPPED state
            before the timeout expires

        InvalidStateError: if the adapter is in either the DEAD or
            DELETED state, this exception is raised

    Notes:
        - The adapter name argument is case senstive
        - The timeout value is set in seconds
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
    Restart an adapter on Itential Platform

    This tool will restart an adapter on an Itential Platform server.  The
    name argument defines the name of the adapter to restart.  In order to
    restart an adapter, the named adapter must be in a RUNNING state
    otherwise this tool will generate an error

    The name argument specifies the name of the appliciation to restart. If
    the specified applicatin does not exist, this tool will return a
    NotFoundError.  The name argument is case sensitive and must be a valid
    adapter name.  The list of adapters can be found using the
    get_adapters tool.

    The timeout value sets the number of seconds to wait when verifying the
    adapter has succussfully restarted.  If the timeout value expires
    before the adapter reaches a RUNNING state, a TimeoutExceededError
    will be generated.

    If the adapter is in a STOPPED, DEAD or DELETED state, an
    InvalidStateError is raised.

    Args:
        ctx (Context): The FastMCP Context object

        name (str): The name of the adapter to restart

        timeout (int): The timeout in seconds this tool should wait for the
            adapter to restart successfully.  If the adapter doesn't
            restart before the timeout expires, a TimeoutExceeded exception
            is raised

    Returns:
        dict: An object representing the restart operation
            - name: The name of the adapter
            - status: The state of the restart operation.  Valid values are
                RUNNING, DEAD, DELETED, STOPPED

    Raises:
        TimeoutExceededError: If the adapter isn't in a RUNNING state
            before the timeout expires

        InvalidStateError: if the adapter is in either the STOPPED, DEAD or
            DELETED state, this exception is raised

    Notes:
        - The adapter name argument is case senstive
        - The timeout value is set in seconds
        - If the adapter is in a STOPPED state, use the start_adapter
          tool instead

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
