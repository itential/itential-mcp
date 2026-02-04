# Copyright (c) 2025 Itential, Inc
# GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

import asyncio

from itential_mcp.core import exceptions
from itential_mcp.platform.services import ServiceBase
from itential_mcp.platform.services._enums import ApplicationState


class Service(ServiceBase):
    """Service class for managing Itential Platform applications.

    This service provides methods for starting, stopping, and restarting
    applications on the Itential Platform. It manages application lifecycle
    operations and monitors application state changes.
    """

    name: str = "applications"

    async def _get_application_health(self, name: str) -> dict:
        """Retrieve application health information from the platform.

        Args:
            name (str): The name of the application to retrieve health data for.

        Returns:
            dict: Application health data containing state and other metrics.

        Raises:
            exceptions.NotFoundError: If the application with the specified name
                cannot be found on the platform.
        """
        res = await self.client.get(
            "/health/applications", params={"equals": name, "equalsField": "id"}
        )

        data = res.json()

        if data["total"] != 1:
            raise exceptions.NotFoundError(f"unable to find application {name}")

        return data["results"][0]

    async def _poll_for_state(
        self, name: str, target_state: str, interval: float = 1.0
    ) -> dict:
        """Poll application health until target state is reached.

        Args:
            name: Application name to poll
            target_state: The desired application state to wait for
            interval: Polling interval in seconds (default: 1.0)

        Returns:
            Final application health data when target state is reached
        """
        while True:
            data = await self._get_application_health(name)
            state = data["state"]

            if state == target_state:
                return data

            await asyncio.sleep(interval)

    async def start_application(self, name: str, timeout: int) -> dict:
        """Start an application on the Itential Platform.

        Attempts to start the specified application if it is currently stopped.
        Waits for the application to reach a RUNNING state within the timeout period.

        Args:
            name: The name of the application to start
            timeout: Maximum time in seconds to wait for the application
                to reach RUNNING state

        Returns:
            dict: Application health data after the operation completes

        Raises:
            exceptions.InvalidStateError: If the application is in DEAD or DELETED
                state and cannot be started
            exceptions.TimeoutExceededError: If the application does not reach
                RUNNING state within the specified timeout period
            exceptions.NotFoundError: If the application with the specified name
                cannot be found on the platform
        """
        data = await self._get_application_health(name)
        state = ApplicationState(data["state"])

        if state == ApplicationState.RUNNING:
            return data

        if state in (ApplicationState.DEAD, ApplicationState.DELETED):
            raise exceptions.InvalidStateError(
                f"application '{name}' is in {state.value} state and cannot be started"
            )

        if state == ApplicationState.STOPPED:
            await self.client.put(f"/applications/{name}/start")

            try:
                result = await asyncio.wait_for(
                    self._poll_for_state(name, ApplicationState.RUNNING.value),
                    timeout=timeout,
                )
                return result
            except asyncio.TimeoutError:
                raise exceptions.TimeoutExceededError(
                    f"application '{name}' did not reach RUNNING state within {timeout}s"
                )

        return data

    async def stop_application(self, name: str, timeout: int) -> dict:
        """Stop an application on the Itential Platform.

        Attempts to stop the specified application if it is currently running.
        Waits for the application to reach a STOPPED state within the timeout period.

        Args:
            name: The name of the application to stop
            timeout: Maximum time in seconds to wait for the application
                to reach STOPPED state

        Returns:
            dict: Application health data after the operation completes

        Raises:
            exceptions.InvalidStateError: If the application is in DEAD or DELETED
                state and cannot be stopped
            exceptions.TimeoutExceededError: If the application does not reach
                STOPPED state within the specified timeout period
            exceptions.NotFoundError: If the application with the specified name
                cannot be found on the platform
        """
        data = await self._get_application_health(name)
        state = ApplicationState(data["state"])

        if state == ApplicationState.STOPPED:
            return data

        if state in (ApplicationState.DEAD, ApplicationState.DELETED):
            raise exceptions.InvalidStateError(
                f"application '{name}' is in {state.value} state and cannot be stopped"
            )

        if state == ApplicationState.RUNNING:
            await self.client.put(f"/applications/{name}/stop")

            try:
                result = await asyncio.wait_for(
                    self._poll_for_state(name, ApplicationState.STOPPED.value),
                    timeout=timeout,
                )
                return result
            except asyncio.TimeoutError:
                raise exceptions.TimeoutExceededError(
                    f"application '{name}' did not reach STOPPED state within {timeout}s"
                )

        return data

    async def restart_application(self, name: str, timeout: int) -> dict:
        """Restart an application on the Itential Platform.

        Attempts to restart the specified application if it is currently running.
        Waits for the application to return to RUNNING state within the timeout period.

        Args:
            name: The name of the application to restart
            timeout: Maximum time in seconds to wait for the application
                to return to RUNNING state after restart

        Returns:
            dict: Application health data after the operation completes

        Raises:
            exceptions.InvalidStateError: If the application is in DEAD, DELETED,
                or STOPPED state and cannot be restarted
            exceptions.TimeoutExceededError: If the application does not return to
                RUNNING state within the specified timeout period
            exceptions.NotFoundError: If the application with the specified name
                cannot be found on the platform
        """
        data = await self._get_application_health(name)
        state = ApplicationState(data["state"])

        if state in (
            ApplicationState.DEAD,
            ApplicationState.DELETED,
            ApplicationState.STOPPED,
        ):
            raise exceptions.InvalidStateError(
                f"application '{name}' is in {state.value} state and cannot be restarted"
            )

        if state == ApplicationState.RUNNING:
            await self.client.put(f"/applications/{name}/restart")

            try:
                result = await asyncio.wait_for(
                    self._poll_for_state(name, ApplicationState.RUNNING.value),
                    timeout=timeout,
                )
                return result
            except asyncio.TimeoutError:
                raise exceptions.TimeoutExceededError(
                    f"application '{name}' did not return to RUNNING state within {timeout}s"
                )

        return data
