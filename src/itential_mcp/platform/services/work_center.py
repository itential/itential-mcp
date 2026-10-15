# Copyright (c) 2025 Itential, Inc
# GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import annotations

from typing import Any

from itential_mcp.platform.services import ServiceBase


class Service(ServiceBase):
    """WorkCenter service for Itential Platform manual task (work item) access.

    The Work Center holds work items, which represent manual tasks that wait
    on a human. This service reads work items and can complete a single
    pending work item.

    Attributes:
        name (str): The service identifier used for registration and routing.
            Set to "work_center".

    Inherits:
        ServiceBase: Base service class providing common functionality including
            client initialization and configuration management.
    """

    name: str = "work_center"

    async def get_work_items(self, root_execution_id: str) -> list[dict[str, Any]]:
        """Retrieve the work items attached to a job or agent session.

        Args:
            root_execution_id (str): The job ID or agent session ID.

        Returns:
            list[dict[str, Any]]: The work items from the response `items`
                list. Includes completed items; callers filter on status.

        Raises:
            ItentialMcpException: If the platform returns an HTTP error. An
                HTTP 404 (unknown run, or no work item created yet) is raised
                with `http_status == 404`; callers decide how to treat it.
        """
        res = await self.client.get(
            "/work-center-service/work-items",
            params={"rootExecutionId": root_execution_id},
        )
        data = res.json()
        if isinstance(data, dict):
            return data.get("items") or []
        return data or []

    async def get_work_item(self, work_item_id: str) -> dict[str, Any]:
        """Retrieve a single work item.

        Args:
            work_item_id (str): The work item identifier.

        Returns:
            dict[str, Any]: The work item record, including rootExecution.

        Raises:
            ItentialMcpException: If the platform returns an HTTP error,
                including 404 when the work item does not exist.
        """
        res = await self.client.get(f"/work-center-service/work-items/{work_item_id}")
        return res.json()

    async def get_work_item_incoming(self, work_item_id: str) -> dict[str, Any]:
        """Retrieve the incoming variables presented to a work item's view.

        Args:
            work_item_id (str): The work item identifier.

        Returns:
            dict[str, Any]: The `incoming` mapping (header, message, body,
                variables, btn_success, btn_failure). Empty if absent.

        Raises:
            ItentialMcpException: If the platform returns an HTTP error,
                including 404 when the work item does not exist.
        """
        res = await self.client.get(
            f"/work-center-service/work-items/{work_item_id}/variables/incoming"
        )
        data = res.json()
        return data.get("incoming") or {}

    async def complete_work_item(
        self,
        work_item_id: str,
        *,
        finish_state: str,
        variables: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Complete a single pending work item.

        This is irreversible: the platform does not validate `finish_state`
        against the task's transitions, so callers must validate it before
        calling this method.

        Args:
            work_item_id (str): The work item identifier.
            finish_state (str): The literal finish state, "success" or
                "failure".
            variables (dict[str, Any] | None): Variables to submit with the
                completion. Defaults to an empty mapping.

        Returns:
            dict[str, Any]: The completed work item record, including
                `status` and `metrics`.

        Raises:
            ItentialMcpException: If the platform returns an HTTP error. An
                HTTP 409 (work item not pending) is raised with
                `http_status == 409`.
        """
        res = await self.client.patch(
            f"/work-center-service/work-items/{work_item_id}/complete",
            json={"finishState": finish_state, "variables": variables or {}},
        )
        return res.json()
