# Copyright (c) 2025 Itential, Inc
# GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)

import time

from typing import Annotated

from pydantic import Field

from fastmcp import Context

from itential_mcp import errors


__tags__ = ("applications",)


async def _get_application_health(
    ctx: Context,
    name: str
) -> dict:
    """
    Get the health status of a specific application.

    Args:
        ctx (Context): The FastMCP Context object
        name (str): The case-sensitive name of the application. Use `get_applications`
            to see available applications.

    Returns:
        dict: Application health data containing status and configuration information

    Raises:
        NotFoundError: If the specified application cannot be found
    """
    client = ctx.request_context.lifespan_context.get("client")

    res = await client.get(
        "/health/applications",
        params={
            "equals": name,
            "equalsField": "id"
        }
    )

    data = res.json()

    if data["total"] != 1:
        raise errors.NotFoundError(f"unable to find application {name}")

    return data


async def get_applications(
    ctx: Annotated[Context, Field(
        description="The FastMCP Context object"
    )]
) -> dict:
    """
    Get all applications configured on the Itential Platform instance.

    Args:
        ctx (Context): The FastMCP Context object

    Returns:
        list[dict]: List of application objects with the following fields:
            - name: The application name
            - package: The NodeJS package comprising the application
            - version: The application version
            - description: The application description
            - state: Operational state (DEAD, STOPPED, RUNNING, DELETED)
    """
    await ctx.info("inside get_applications(...)")

    client = ctx.request_context.lifespan_context.get("client")

    res = await client.get("/health/applications")

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


async def start_application(
    ctx: Annotated[Context, Field(
        description="The FastMCP Context object"
    )],
    name: Annotated[str, Field(
        description="The name of the application to start"
    )],
    timeout: Annotated[int, Field(
        description="Timeout waiting for application to start",
        default=10
    )]
) -> dict:
    """
    Start an application on Itential Platform.

    Behavior based on current application state:
    - RUNNING: No action taken (already started)
    - STOPPED: Attempts to start and waits for RUNNING state
    - DEAD/DELETED: Raises InvalidStateError (cannot start)

    Args:
        ctx (Context): The FastMCP Context object
        name (str): Case-sensitive application name. Use `get_applications` to see available applications.
        timeout (int): Seconds to wait for application to reach RUNNING state

    Returns:
        dict: Start operation result
            - name: The application name
            - state: Final application state (RUNNING, DEAD, DELETED, STOPPED)

    Raises:
        TimeoutExceededError: If application doesn't reach RUNNING state within timeout
        InvalidStateError: If application is in DEAD or DELETED state

    Notes:
        - Application name is case-sensitive
        - Function polls application state every second until timeout
    """
    await ctx.info("inside start_application(...)")

    client = ctx.request_context.lifespan_context.get("client")

    data = await _get_application_health(ctx, name)
    state = data["results"][0]["state"]

    if state == "STOPPED":
        await client.put(f"/applications/{name}/start")

        while timeout:
            data = await _get_application_health(ctx, name)
            state = data["results"][0]["state"]

            if state == "RUNNING":
                break

            time.sleep(1)
            timeout -= 1

    elif state in ("DEAD", "DELETED"):
        raise errors.InvalidStateError(f"application `{name}` is `{state}`")

    if timeout == 0:
        raise errors.TimeoutExceededError()

    return {
        "name": name,
        "state": state
    }


async def stop_application(
    ctx: Annotated[Context, Field(
        description="The FastMCP Context object"
    )],
    name: Annotated[str, Field(
        description="The name of the application to stop"
    )],
    timeout: Annotated[int, Field(
        description="Timeout waiting for application to stop",
        default=10
    )]
) -> dict:
    """
    Stop an application on Itential Platform.

    Behavior based on current application state:
    - RUNNING: Attempts to stop and waits for STOPPED state
    - STOPPED: No action taken (already stopped)
    - DEAD/DELETED: Raises InvalidStateError (cannot stop)

    Args:
        ctx (Context): The FastMCP Context object
        name (str): Case-sensitive application name. Use `get_applications` to see available applications.
        timeout (int): Seconds to wait for application to reach STOPPED state

    Returns:
        dict: Stop operation result
            - name: The application name
            - state: Final application state (RUNNING, DEAD, DELETED, STOPPED)

    Raises:
        TimeoutExceededError: If application doesn't reach STOPPED state within timeout
        InvalidStateError: If application is in DEAD or DELETED state

    Notes:
        - Application name is case-sensitive
        - Function polls application state every second until timeout
    """
    await ctx.info("inside stop_application(...)")

    client = ctx.request_context.lifespan_context.get("client")

    data = await _get_application_health(ctx, name)
    state = data["results"][0]["state"]

    if state == "RUNNING":
        await client.put(f"/applications/{name}/stop")

        while timeout:
            data = await _get_application_health(ctx, name)

            state = data["results"][0]["state"]

            if state == "STOPPED":
                break

            time.sleep(1)
            timeout -= 1

    elif state in ("DEAD", "DELETED"):
        raise errors.InvalidStateError(f"application `{name}` is `{state}`")

    if timeout == 0:
        raise errors.TimeoutExceededError()

    return {
        "name": name,
        "state": state
    }


async def restart_application(
    ctx: Annotated[Context, Field(
        description="The FastMCP Context object"
    )],
    name: Annotated[str, Field(
        description="The name of the application to restart"
    )],
    timeout: Annotated[int, Field(
        description="Timeout waiting for application to restart",
        default=10
    )]
) -> dict:
    """
    Restart an application on Itential Platform.

    Behavior based on current application state:
    - RUNNING: Attempts to restart and waits for RUNNING state
    - STOPPED/DEAD/DELETED: Raises InvalidStateError (cannot restart)

    Args:
        ctx (Context): The FastMCP Context object
        name (str): Case-sensitive application name. Use `get_applications` to see available applications.
        timeout (int): Seconds to wait for application to return to RUNNING state

    Returns:
        dict: Restart operation result
            - name: The application name
            - state: Final application state (RUNNING, DEAD, DELETED, STOPPED)

    Raises:
        TimeoutExceededError: If application doesn't return to RUNNING state within timeout
        InvalidStateError: If application is not in RUNNING state initially

    Notes:
        - Application name is case-sensitive
        - Only RUNNING applications can be restarted
        - For STOPPED applications, use `start_application` instead
        - Function polls application state every second until timeout
    """
    await ctx.info("inside restart_application(...)")

    client = ctx.request_context.lifespan_context.get("client")

    data = await _get_application_health(ctx, name)
    state = data["results"][0]["state"]

    if state == "RUNNING":
        await client.put(f"/applications/{name}/restart")

        while timeout:
            data = await _get_application_health(ctx, name)

            state = data["results"][0]["state"]

            if state == "RUNNING":
                break

            time.sleep(1)
            timeout -= 1

    elif state in ("DEAD", "DELETED", "STOPPED"):
        raise errors.InvalidStateError(f"application `{name}` is `{state}`")

    if timeout == 0:
        raise errors.TimeoutExceededError()

    return {
        "name": name,
        "state": state
    }
