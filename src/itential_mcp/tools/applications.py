# Copyright (c) 2025 Itential, Inc
# GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from typing import Annotated

from pydantic import Field

from fastmcp import Context

from itential_mcp.models import applications as models


__tags__ = ("applications",)


async def get_applications(
    ctx: Annotated[Context, Field(description="The FastMCP Context object")],
) -> models.GetApplicationsResponse:
    """
    Get all applications configured on the Itential Platform instance.

    Args:
        ctx (Context): The FastMCP Context object

    Returns:
        GetApplicationsResponse: List of objects where each element represents
            a configured application from the server

    Raises:
        Exception: If there is an error retrieving applications from the platform
    """
    await ctx.info("inside get_applications(...)")

    client = ctx.request_context.lifespan_context.get("client")

    res = await client.get("/health/applications")

    data = res.json()

    elements = list()

    for ele in data["results"]:
        elements.append(
            models.GetApplicationsElement(
                name=ele["id"],
                package=ele.get("package_id"),
                version=ele.get("version"),
                description=ele.get("description"),
                state=ele["state"],
            )
        )

    return models.GetApplicationsResponse(root=elements)


async def start_application(
    ctx: Annotated[Context, Field(description="The FastMCP Context object")],
    name: Annotated[str, Field(description="The name of the application to start")],
    timeout: Annotated[
        int, Field(description="Timeout waiting for application to start", default=10)
    ],
) -> models.StartApplicationResponse:
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
        StartApplicationResponse: An object that represents the start
            application response

    Raises:
        TimeoutExceededError: If application doesn't reach RUNNING state within timeout
        InvalidStateError: If application is in DEAD or DELETED state

    Notes:
        - Application name is case-sensitive
        - Function polls application state every second until timeout
    """
    await ctx.info("inside start_application(...)")
    client = ctx.request_context.lifespan_context.get("client")
    data = client.applications.start_application(name, timeout)
    return models.StartApplicationResponse(name=data["id"], state=data["state"])


async def stop_application(
    ctx: Annotated[Context, Field(description="The FastMCP Context object")],
    name: Annotated[str, Field(description="The name of the application to stop")],
    timeout: Annotated[
        int, Field(description="Timeout waiting for application to stop", default=10)
    ],
) -> models.StopApplicationResponse:
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
        StopApplicationResponse: An object that represents the stop
            operation for the application

    Raises:
        TimeoutExceededError: If application doesn't reach STOPPED state within timeout
        InvalidStateError: If application is in DEAD or DELETED state

    Notes:
        - Application name is case-sensitive
        - Function polls application state every second until timeout
    """
    await ctx.info("inside stop_application(...)")
    client = ctx.request_context.lifespan_context.get("client")
    data = await client.applications.stop_application(name=name, timeout=timeout)
    return models.StopApplicationResponse(name=data["id"], state=data["state"])


async def restart_application(
    ctx: Annotated[Context, Field(description="The FastMCP Context object")],
    name: Annotated[str, Field(description="The name of the application to restart")],
    timeout: Annotated[
        int, Field(description="Timeout waiting for application to restart", default=10)
    ],
) -> models.RestartApplicationResponse:
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
        RestartApplicationResponse: An object that provides the operational
            status of the restart application action

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
    data = await client.applications.restart_application(name=name, timeout=timeout)
    return models.RestartApplicationResponse(name=data["id"], state=data["state"])
