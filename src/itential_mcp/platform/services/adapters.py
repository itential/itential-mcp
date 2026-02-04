# Copyright (c) 2025 Itential, Inc
# GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

import asyncio

from itential_mcp.core import exceptions
from itential_mcp.platform.services import ServiceBase
from itential_mcp.platform.services._enums import AdapterState


class Service(ServiceBase):
    """
    Service class for managing Itential Platform adapters.

    This service provides comprehensive adapter lifecycle management including
    starting, stopping, and restarting adapters. It handles state validation,
    timeout management, and error conditions for adapter operations.

    Attributes:
        name (str): The service name identifier set to "adapters"

    Notes:
        All adapter operations include polling for state transitions with
        configurable timeouts to ensure operations complete successfully.
    """

    name: str = "adapters"

    async def _get_adapter_health(self, name: str) -> dict:
        """
        Retrieve health information for a specific adapter from Itential Platform.

        This internal method queries the platform's health API to get current
        state and metadata for the specified adapter. It validates that exactly
        one adapter matches the provided name.

        Args:
            name (str): The case-sensitive adapter name to retrieve health for

        Returns:
            dict: Complete health response data from the platform API containing:
                - total: Number of matching adapters (should be 1)
                - results: List with single adapter health data including state,
                  version, and other metadata

        Raises:
            NotFoundError: If the adapter name is not found or multiple matches
                are returned by the platform

        Notes:
            This method performs exact string matching on the adapter ID field
            and requires the adapter name to be case-sensitive.
        """
        res = await self.client.get(
            "/health/adapters", params={"equals": name, "equalsField": "id"}
        )

        data = res.json()

        if data["total"] != 1:
            raise exceptions.NotFoundError(f"unable to find adapter {name}")

        return data

    async def _poll_for_state(
        self, name: str, target_state: str, interval: float = 1.0
    ) -> dict:
        """Poll adapter health until target state is reached.

        Args:
            name: Adapter name to poll
            target_state: The desired adapter state to wait for
            interval: Polling interval in seconds (default: 1.0)

        Returns:
            Final adapter health data when target state is reached
        """
        while True:
            data = await self._get_adapter_health(name)
            state = data["results"][0]["state"]

            if state == target_state:
                return data["results"][0]

            await asyncio.sleep(interval)

    async def start_adapter(self, name: str, timeout: int) -> dict:
        """Start an adapter on Itential Platform with state validation and timeout.

        This method manages the complete lifecycle of starting an adapter,
        including initial state validation, issuing start commands, and polling
        for successful state transitions. It handles various adapter states
        and provides appropriate error handling.

        Args:
            name: Case-sensitive adapter name to start. Must match an
                existing adapter configuration on the platform
            timeout: Maximum seconds to wait for the adapter to reach
                RUNNING state

        Returns:
            dict: Response containing adapter health data with:
                - name: The adapter name that was started
                - state: Final operational state after the operation

        Raises:
            NotFoundError: If the specified adapter name cannot be found
            InvalidStateError: If the adapter is in DEAD or DELETED state,
                which cannot be started
            TimeoutExceededError: If the adapter doesn't reach RUNNING state
                within the specified timeout period

        Notes:
            - STOPPED adapters will be started and polled until RUNNING
            - RUNNING adapters return immediately without state change
            - DEAD/DELETED adapters cannot be started and raise an error
            - Polling occurs every 1 second until timeout or success
        """
        data = await self._get_adapter_health(name)
        state = AdapterState(data["results"][0]["state"])

        if state == AdapterState.RUNNING:
            return data["results"][0]

        if state in (AdapterState.DEAD, AdapterState.DELETED):
            raise exceptions.InvalidStateError(
                f"adapter '{name}' is in {state.value} state and cannot be started"
            )

        if state == AdapterState.STOPPED:
            await self.client.put(f"/adapters/{name}/start")

            try:
                result = await asyncio.wait_for(
                    self._poll_for_state(name, AdapterState.RUNNING.value),
                    timeout=timeout,
                )
                return result
            except asyncio.TimeoutError:
                raise exceptions.TimeoutExceededError(
                    f"adapter '{name}' did not reach RUNNING state within {timeout}s"
                )

        return data["results"][0]

    async def stop_adapter(self, name: str, timeout: int) -> dict:
        """Stop an adapter on Itential Platform with state validation and timeout.

        This method manages the complete lifecycle of stopping an adapter,
        including initial state validation, issuing stop commands, and polling
        for successful state transitions. It handles various adapter states
        and provides appropriate error handling.

        Args:
            name: Case-sensitive adapter name to stop. Must match an
                existing adapter configuration on the platform
            timeout: Maximum seconds to wait for the adapter to reach
                STOPPED state

        Returns:
            dict: Response containing adapter health data with:
                - name: The adapter name that was stopped
                - state: Final operational state after the operation

        Raises:
            NotFoundError: If the specified adapter name cannot be found
            InvalidStateError: If the adapter is in DEAD or DELETED state,
                which cannot be stopped
            TimeoutExceededError: If the adapter doesn't reach STOPPED state
                within the specified timeout period

        Notes:
            - RUNNING adapters will be stopped and polled until STOPPED
            - STOPPED adapters return immediately without state change
            - DEAD/DELETED adapters cannot be stopped and raise an error
            - Polling occurs every 1 second until timeout or success
        """
        data = await self._get_adapter_health(name)
        state = AdapterState(data["results"][0]["state"])

        if state == AdapterState.STOPPED:
            return data["results"][0]

        if state in (AdapterState.DEAD, AdapterState.DELETED):
            raise exceptions.InvalidStateError(
                f"adapter '{name}' is in {state.value} state and cannot be stopped"
            )

        if state == AdapterState.RUNNING:
            await self.client.put(f"/adapters/{name}/stop")

            try:
                result = await asyncio.wait_for(
                    self._poll_for_state(name, AdapterState.STOPPED.value),
                    timeout=timeout,
                )
                return result
            except asyncio.TimeoutError:
                raise exceptions.TimeoutExceededError(
                    f"adapter '{name}' did not reach STOPPED state within {timeout}s"
                )

        return data["results"][0]

    async def restart_adapter(self, name: str, timeout: int) -> dict:
        """Restart an adapter on Itential Platform with state validation and timeout.

        This method manages the complete lifecycle of restarting an adapter,
        including initial state validation, issuing restart commands, and polling
        for successful state transitions. Only RUNNING adapters can be restarted.

        Args:
            name: Case-sensitive adapter name to restart. Must match an
                existing adapter configuration on the platform
            timeout: Maximum seconds to wait for the adapter to return to
                RUNNING state

        Returns:
            dict: Response containing adapter health data with:
                - name: The adapter name that was restarted
                - state: Final operational state after the operation (should be RUNNING)

        Raises:
            NotFoundError: If the specified adapter name cannot be found
            InvalidStateError: If the adapter is not in RUNNING state initially.
                STOPPED, DEAD, or DELETED adapters cannot be restarted
            TimeoutExceededError: If the adapter doesn't return to RUNNING state
                within the specified timeout period

        Notes:
            - Only RUNNING adapters can be restarted
            - For STOPPED adapters, use start_adapter() instead
            - Restart operation cycles the adapter through stop/start internally
            - Polling occurs every 1 second until timeout or success
        """
        data = await self._get_adapter_health(name)
        state = AdapterState(data["results"][0]["state"])

        if state in (AdapterState.DEAD, AdapterState.DELETED, AdapterState.STOPPED):
            raise exceptions.InvalidStateError(
                f"adapter '{name}' is in {state.value} state and cannot be restarted"
            )

        if state == AdapterState.RUNNING:
            await self.client.put(f"/adapters/{name}/restart")

            try:
                result = await asyncio.wait_for(
                    self._poll_for_state(name, AdapterState.RUNNING.value),
                    timeout=timeout,
                )
                return result
            except asyncio.TimeoutError:
                raise exceptions.TimeoutExceededError(
                    f"adapter '{name}' did not return to RUNNING state within {timeout}s"
                )

        return data["results"][0]
