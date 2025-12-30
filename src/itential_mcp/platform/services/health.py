# Copyright (c) 2025 Itential, Inc
# GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import annotations

from typing import Any

from itential_mcp.platform.services import ServiceBase


class Service(ServiceBase):
    """Service class for retrieving comprehensive health information from Itential Platform.

    This service provides methods for gathering platform health data including
    system status, server information, application states, and adapter connectivity.
    It supports parallel data retrieval for efficient health monitoring.
    """

    name: str = "health"

    async def get_status_health(self) -> dict[str, Any]:
        """
        Get overall platform status information.

        Returns:
            dict: Platform status including services, timestamp, and overall health indicators

        Raises:
            Exception: If there is an error retrieving status information
        """
        res = await self.client.get("/health/status")
        return res.json()

    async def get_system_health(self) -> dict[str, Any]:
        """
        Get system-level hardware and OS information.

        Returns:
            dict: System information including CPU, memory, architecture, and load averages

        Raises:
            Exception: If there is an error retrieving system information
        """
        res = await self.client.get("/health/system")
        return res.json()

    async def get_server_health(self) -> dict[str, Any]:
        """
        Get Node.js server runtime information and performance metrics.

        Returns:
            dict: Server information including versions, memory usage, and dependencies

        Raises:
            Exception: If there is an error retrieving server information
        """
        res = await self.client.get("/health/server")
        return res.json()

    async def get_applications_health(self) -> dict[str, Any]:
        """
        Get comprehensive application health and status information.

        Returns:
            dict: List of applications with status, resource usage, and performance metrics

        Raises:
            Exception: If there is an error retrieving application information
        """
        res = await self.client.get("/health/applications")
        return res.json()

    async def get_adapters_health(self) -> dict[str, Any]:
        """
        Get comprehensive adapter health and connectivity information.

        Returns:
            dict: List of adapters with status, resource usage, and connection details

        Raises:
            Exception: If there is an error retrieving adapter information
        """
        res = await self.client.get("/health/adapters")
        return res.json()
