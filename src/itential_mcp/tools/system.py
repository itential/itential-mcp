# Copyright (c) 2025 Itential, Inc
# GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)

from typing import Annotated

from pydantic import Field

from fastmcp import Context


async def get_health(
    ctx: Annotated[Context, Field(
        description="The FastMCP Context object"
    )]
) -> dict:
    """
    Get the Itential Platforms server health

    The server health response will return data about the overall health of
    the server. It will return keys that include the current server status
    including details about memory and CPU utilization, version information
    for the server and dependencies as well as the system CPU architecture.

    The health response includes keys for `status` which provides the overall
    system status including core dependent service status for mongo and redis.
    It also includes a key for `system` the provides the server architecture,
    total memory and CPU core details.  The `server` key provides details about
    the server software including running versions, memory and CPU usage details
    and dependent library versions.

    The health response also includes details about running applications and
    adapters. The `applications` key provides details about applications and
    the `adapters` key provides detailsa about adapters. This includes the
    current running state of the application or adatper as well as the
    memory and CPU usage statistics and uptime.

    Args:
        ctx (Context): The FastMCP Context object

    Returns:
        dict: A Python dict object with the response

    Raises:
        None
    """
    await ctx.info("inside get_health(...)")

    client = ctx.request_context.lifespan_context.get("client")

    results = {}

    for key, uri in (
        ("status", "/health/status"),
        ("system", "/health/system"),
        ("server", "/health/server"),
        ("applications", "/health/applications"),
        ("adapters", "/health/adapters"),
    ):
        res = await client.get(uri)
        data = res.json()
        results[key] = data.get("results") or data

    return results
