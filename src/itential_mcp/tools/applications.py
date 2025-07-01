# Copyright (c) 2025 Itential, Inc
# GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)

import time

from typing import Annotated

from pydantic import Field

from fastmcp import Context

from itential_mcp import errors


async def _get_application_health(
    ctx: Context,
    name: str
) -> dict:
    """
    Get the health of an application

    This internal function will return the the health of the application
    specified by the name argument.  If the specified application does not
    exist, the function will raise a NotFoundError.   If the application
    does exist, it will be returned as a dict object.

    Args:
        ctx (Context): The FastMCP Context object

        name (str): The name of the application to get.  This argument is
            case senstive.  To get a list of all available applications on
            the server see ```get_applications```

    Returns:
        dict: An object the represents the application health

    Raises:
        NotFoundError: If the application specified by name cannot be found
            on the server, a NotFoundError is returned.
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
    Get all applications from Itential Platform

    This tool will retrieve all of the applications configured on the instance
    of Itential Plaform and return them.   The returned list will include
    the application name, package, version, description and running state.

    Args:
        ctx (Context): The FastMCP Context object

    Returns:
        list[dict]: A list of objects where each object represents an
            application with the following fields:
            - name: The name of the application
            - package: The NodeJS package that comprises the application
            - version: The version of the application on the server
            - description: The application description
            - state: The current operational state of the appliacation.  Valid
                states are DEAD, STOPPED, RUNNING, DELETED

    Raises:
        None
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
    Start an application on Itential Platform

    This tool will start an application on an Itential Platform server.  The
    name argument defines the name of the application to start.  If the
    application is already in a running state. this tool will not attempt
    any further action.

    The name argument is case sensitive and must be a valid application
    defined on Itential Platform.  The list of applications running on
    the server can be found using the get_applications tool.

    If the application is in a STOPPED state, this tool will attempt to start
    the application.   It will check to see if the application started.  If
    the application hasn't started within the timeout period, a
    TimeoutExceededError error is raised

    If the application is in either the DEAD or DELETED state, an
    InvalidStateError is raised.

    Args:
        ctx (Context): The FastMCP Context object

        name (str): The name of the application to start

        timeout (int): The timeout in seconds this tool should wait for the
            application to start successfully.  If the application doesn't
            start before the timeout expires, a TimeoutExceeded exception
            is raised

    Returns:
        dict: An object representing the start operation
            - name: The name of the application
            - status: The state of the start operation.  Valid values are
                RUNNING, DEAD, DELETED, STOPPED

    Raises:
        TimeoutExceededError: If the application isn't in a RUNNING state
            before the timeout expires

        InvalidStateError: if the application is in either the DEAD or
            DELETED state, this exception is raised

    Notes:
        - The application name argument is case senstive
        - The timeout value is set in seconds

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
        description="Timeout waiting for application to start",
        default=10
    )]
) -> dict:
    """
    Stop an application on Itential Platform

    This tool will stop an application that is currently in a running
    state on the server.  If the application is already stopped this
    tool will not perform any further action.

    The name argument specifies the name of the application to stop.  The
    value for name must be a valid case senstive name.  The list of
    applications can be found by calling the get_applications tool.  If
    the specified name is not a valid application name, this tool will
    raise a NotFoundError.

    The timeout value sets the number of seconds to wait to verify the
    application has stopped.  If the timeout value expires before the
    application reaches a stopped state, this tool will raise a
    TimeoutExceededError.

    If the application is in either the DEAD or DELETED state, an
    InvalidStateError is raised.

    Args:
        ctx (Context): The FastMCP Context object

        name (str): The name of the application to start

        timeout (int): The timeout in seconds this tool should wait for the
            application to stop successfully.  If the application doesn't
            stop before the timeout expires, a TimeoutExceeded exception
            is raised

    Returns:
        dict: An object representing the stop operation
            - name: The name of the application
            - status: The state of the start operation.  Valid values are
                RUNNING, DEAD, DELETED, STOPPED

    Raises:
        TimeoutExceededError: If the application isn't in a STOPPED state
            before the timeout expires

        InvalidStateError: if the application is in either the DEAD or
            DELETED state, this exception is raised

    Notes:
        - The application name argument is case senstive
        - The timeout value is set in seconds
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
    Restart an application on Itential Platform

    This tool will restart an application on an Itential Platform server.  The
    name argument defines the name of the application to restart.  In order to
    restart an application, the named application must be in a RUNNING state
    otherwise this tool will generate an error

    The name argument specifies the name of the appliciation to restart. If
    the specified applicatin does not exist, this tool will return a
    NotFoundError.  The name argument is case sensitive and must be a valid
    application name.  The list of applications can be found using the
    get_applications tool.

    The timeout value sets the number of seconds to wait when verifying the
    application has succussfully restarted.  If the timeout value expires
    before the application reaches a RUNNING state, a TimeoutExceededError
    will be generated.

    If the application is in a STOPPED, DEAD or DELETED state, an
    InvalidStateError is raised.

    Args:
        ctx (Context): The FastMCP Context object

        name (str): The name of the application to restart

        timeout (int): The timeout in seconds this tool should wait for the
            application to restart successfully.  If the application doesn't
            restart before the timeout expires, a TimeoutExceeded exception
            is raised

    Returns:
        dict: An object representing the restart operation
            - name: The name of the application
            - status: The state of the restart operation.  Valid values are
                RUNNING, DEAD, DELETED, STOPPED

    Raises:
        TimeoutExceededError: If the application isn't in a RUNNING state
            before the timeout expires

        InvalidStateError: if the application is in either the STOPPED, DEAD or
            DELETED state, this exception is raised

    Notes:
        - The application name argument is case senstive
        - The timeout value is set in seconds
        - If the application is in a STOPPED state, use the start_application
          tool instead

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
