# Copyright (c) 2025 Itential, Inc
# GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)

import asyncio

from itential_mcp import exceptions
from itential_mcp.services import ServiceBase


class Service(ServiceBase):

    name: str = "applications"

    async def _get_application_health(self, name):
        res = await self.client.get(
            "/health/applications",
            params={
                "equals": name,
                "equalsField": "id"
            }
        )

        data = res.json()

        if data["total"] != 1:
            raise exceptions.NotFoundError(f"unable to find application {name}")

        return data["results"][0]

    async def start_application(self, name, timeout):
        data = await self._get_application_health(name)
        state = data["results"][0]["state"]

        if state == "STOPPED":
            await self.client.put(f"/applications/{name}/start")

            while timeout:
                data = await self._get_application_health(name)
                state = data["results"][0]["state"]

                if state == "RUNNING":
                    break

                await asyncio.sleep(1)
                timeout -= 1

        elif state in ("DEAD", "DELETED"):
            raise exceptions.InvalidStateError(f"application `{name}` is `{state}`")

        if timeout == 0:
            raise exceptions.TimeoutExceededError()

        return data


    async def stop_application(self, name, timeout):
        data = await self._get_application_health(name)
        state = data["results"][0]["state"]

        if state == "RUNNING":
            await self.client.put(f"/applications/{name}/stop")

            while timeout:
                data = await self._get_application_health(name)

                state = data["results"][0]["state"]

                if state == "STOPPED":
                    break

                await asyncio.sleep(1)
                timeout -= 1

        elif state in ("DEAD", "DELETED"):
            raise exceptions.InvalidStateError(f"application `{name}` is `{state}`")

        if timeout == 0:
            raise exceptions.TimeoutExceededError()

        return data


    async def restart_application(self, name, timeout):
        data = await self._get_application_health(name)
        state = data["results"][0]["state"]

        if state == "RUNNING":
            await self.client.put(f"/applications/{name}/restart")

            while timeout:
                data = await self._get_application_health(name)

                state = data["results"][0]["state"]

                if state == "RUNNING":
                    break

                await asyncio.sleep(1)
                timeout -= 1

        elif state in ("DEAD", "DELETED", "STOPPED"):
            raise exceptions.InvalidStateError(f"application `{name}` is `{state}`")

        if timeout == 0:
            raise exceptions.TimeoutExceededError()

        return data
