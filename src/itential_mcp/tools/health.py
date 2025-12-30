# Copyright (c) 2025 Itential, Inc
# GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

import asyncio
from typing import Annotated

from pydantic import Field

from fastmcp import Context

from itential_mcp.models.health import HealthResponse


__tags__ = ("health",)


async def get_health(
    ctx: Annotated[Context, Field(description="The FastMCP Context object")],
) -> HealthResponse:
    """
    Get comprehensive health information from Itential Platform.

    System health monitoring provides visibility into platform performance,
    resource utilization, and component status. This enables proactive
    monitoring and troubleshooting of the automation infrastructure.

    This function uses parallel async API calls to efficiently retrieve
    health data from all platform endpoints simultaneously, providing
    optimal performance for comprehensive health monitoring.

    Note: This function also provides a complete list of all applications
    and adapters running on the platform as part of the health data.

    Args:
        ctx (Context): The FastMCP Context object

    Returns:
        HealthResponse: Comprehensive health data model with the following sections:
            - status: Overall system status including core services (mongo, redis)
            - system: Server architecture, total memory, and CPU core details
            - server: Software versions, memory/CPU usage, and library dependencies
            - applications: Complete list of applications with status, resource usage, and uptime
            - adapters: Complete list of adapters with status, resource usage, and uptime

    Raises:
        Exception: If there is an error retrieving health information from
            any platform component
    """
    await ctx.info("inside get_health(...)")

    client = ctx.request_context.lifespan_context.get("client")

    tasks = [
        client.health.get_status_health(),
        client.health.get_system_health(),
        client.health.get_server_health(),
        client.health.get_applications_health(),
        client.health.get_adapters_health(),
    ]

    status, system, server, applications, adapters = await asyncio.gather(
        *tasks, return_exceptions=False
    )

    return HealthResponse(
        status=status,
        system=system,
        server=server,
        applications=applications["results"],
        adapters=adapters["results"],
    )
