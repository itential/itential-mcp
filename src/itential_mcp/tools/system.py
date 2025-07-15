# Copyright (c) 2025 Itential, Inc
# GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)

from typing import Annotated

from pydantic import Field

from fastmcp import Context


__tags__ = ("system",)


async def get_health(
    ctx: Annotated[Context, Field(
        description="The FastMCP Context object"
    )]
) -> dict:
    """
    Get comprehensive health information from Itential Platform.

    System health monitoring provides visibility into platform performance,
    resource utilization, and component status. This enables proactive
    monitoring and troubleshooting of the automation infrastructure.

    Note: This function also provides a complete list of all applications
    and adapters running on the platform as part of the health data.

    Args:
        ctx (Context): The FastMCP Context object

    Returns:
        dict: Comprehensive health data with the following sections:
            - status: Overall system status including core services (mongo, redis)
            - system: Server architecture, total memory, and CPU core details
            - server: Software versions, memory/CPU usage, and library dependencies
            - applications: Complete list of applications with status, resource usage, and uptime
            - adapters: Complete list of adapters with status, resource usage, and uptime
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
