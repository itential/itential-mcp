# Copyright (c) 2025 Itential, Inc
# GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import annotations

from typing import Sequence, Mapping, Any

from itential_mcp.core import exceptions

from itential_mcp.platform.services import ServiceBase


class Service(ServiceBase):
    """Service class for managing inventories in Itential Platform.

    The Inventory Manager service provides methods for creating, retrieving,
    describing, and deleting inventories. Inventories are collections of
    network devices organized for bulk configuration management, compliance
    checking, and automation tasks.

    Attributes:
        name (str): The service name identifier "inventory_manager"
    """

    name: str = "inventory_manager"

    async def get_inventories(self) -> Sequence[Mapping[str, Any]]:
        """
        Retrieve all inventories from the Inventory Manager.

        Inventories are collections of network devices organized for bulk
        configuration management, compliance checking, and automation tasks.
        This method fetches a complete list of all inventories configured
        on the platform.

        Returns:
            Sequence[Mapping[str, Any]]: List of inventory objects containing
                metadata including IDs, names, descriptions, and device counts.
                Each inventory object includes:
                - id: Unique identifier for the inventory
                - name: Human-readable name of the inventory
                - description: Optional description text
                - deviceCount: Number of devices in the inventory

        Raises:
            Exception: If there is an error retrieving inventories from the platform
        """
        res = await self.client.get("/inventory_manager/v1/inventories")
        data = res.json()
        return data["result"]["data"]

    async def describe_inventory(self, name: str) -> Mapping[str, Any]:
        """
        Retrieve detailed information about a specific inventory by name.

        This method fetches comprehensive details about an inventory including
        its unique identifier, description, groups, actions, tags, and the
        list of nodes (devices) with their attributes. The inventory is
        identified by its name.

        Args:
            name (str): Name of the inventory to retrieve details for.
                This argument is case sensitive.

        Returns:
            Mapping[str, Any]: Inventory details containing:
                - _id: Unique identifier for the inventory
                - name: Human-readable name of the inventory
                - description: Optional description text
                - groups: List of authorization group names
                - actions: List of actions configured for the inventory
                - tags: Tags associated with the inventory
                - nodes: List of node objects with name, attributes, and tags

        Raises:
            NotFoundError: If the specified inventory name cannot be found
        """
        inventories = await self.get_inventories()

        for inventory in inventories:
            if inventory["name"] == name:
                inventory_id = inventory["_id"]
                res = await self.client.get(
                    f"/inventory_manager/v1/inventories/{inventory_id}"
                )
                result = res.json()["result"]

                nodes_res = await self.client.get(
                    f"/inventory_manager/v1/inventories/{name}/nodes"
                )
                nodes_data = nodes_res.json()
                result["nodes"] = nodes_data.get("result", {}).get("data", [])

                return result

        raise exceptions.NotFoundError(f"inventory '{name}' not found")

    async def create_inventory(
        self,
        name: str,
        groups: list[str],
        *,
        description: str | None = None,
        devices: list[str] | None = None,
    ) -> Mapping[str, Any]:
        """
        Create a new inventory in the Inventory Manager.

        This method creates a new inventory with the specified name and
        authorization groups. A description and list of device names can
        be provided optionally. The method checks for duplicate inventory
        names and raises an error if an inventory with the same name
        already exists.

        Args:
            name (str): Name of the inventory to create
            groups (list[str]): List of authorization group names to assign
                to the inventory. At least one group is required.
            description (str | None): Optional description for the inventory.
                Defaults to None.
            devices (list[str] | None): Optional list of device names to include
                in the inventory. Use `get_devices` to see available devices.
                Defaults to None.

        Returns:
            Mapping[str, Any]: Created inventory details including ID, name,
                and status

        Raises:
            ValueError: If an inventory with the same name already exists
            Exception: If there is an error creating the inventory
        """
        inventories = await self.get_inventories()

        for inventory in inventories:
            if inventory["name"] == name:
                raise ValueError(f"inventory '{name}' already exists")

        body: dict[str, Any] = {"name": name, "groups": groups}

        if description is not None:
            body["description"] = description

        if devices is not None:
            body["devices"] = [{"name": device} for device in devices]

        res = await self.client.post(
            "/inventory_manager/v1/inventories", json=body
        )

        data = res.json()
        result = data.get("result", data)

        if "message" in data and "message" not in result:
            result["message"] = data["message"]

        return result

    async def add_nodes_to_inventory(
        self,
        inventory_name: str,
        nodes: list[dict[str, Any]],
    ) -> Mapping[str, Any]:
        """
        Add nodes in bulk to an existing inventory.

        This method adds one or more nodes with their attributes and optional
        tags to an inventory identified by name. Each node must include a name
        and an attributes dictionary. Tags are optional per node.

        Args:
            inventory_name (str): Name of the inventory to add nodes to.
                This argument is case sensitive.
            nodes (list[dict[str, Any]]): List of node objects to add. Each
                node must contain:
                - name (str): The node name (required)
                - attributes (dict[str, Any]): Node attributes such as
                    itential_host, itential_platform, cluster_id (required)
                - tags (list[str]): Optional list of tags for the node

        Returns:
            Mapping[str, Any]: Result containing status and message fields

        Raises:
            NotFoundError: If the specified inventory name cannot be found
            Exception: If there is an error adding nodes to the inventory
        """
        inventories = await self.get_inventories()

        for inventory in inventories:
            if inventory["name"] == inventory_name:
                body: dict[str, Any] = {
                    "inventory_identifier": inventory_name,
                    "nodes": nodes,
                }

                res = await self.client.post(
                    "/inventory_manager/v1/nodes/bulk", json=body
                )

                data = res.json()
                result = data.get("result", data)

                if "status" in data and "status" not in result:
                    result["status"] = data["status"]

                if "message" in data and "message" not in result:
                    result["message"] = data["message"]

                return result

        raise exceptions.NotFoundError(f"inventory '{inventory_name}' not found")

    async def delete_inventory(self, name: str) -> Mapping[str, Any]:
        """
        Delete an inventory from the Inventory Manager.

        This method deletes the specified inventory by name. The inventory
        and all its device associations are permanently removed. The devices
        themselves are not affected; only the inventory grouping is deleted.

        Args:
            name (str): Name of the inventory to delete.
                This argument is case sensitive.

        Returns:
            Mapping[str, Any]: Deletion result containing status and
                confirmation message

        Raises:
            NotFoundError: If the specified inventory name cannot be found
            Exception: If there is an error deleting the inventory
        """
        inventories = await self.get_inventories()

        for inventory in inventories:
            if inventory["name"] == name:
                inventory_id = inventory["_id"]
                res = await self.client.delete(
                    f"/inventory_manager/v1/inventories/{inventory_id}"
                )
                data = res.json()
                result = data.get("result", data)

                if "status" in data and "status" not in result:
                    result["status"] = data["status"]

                if "message" in data and "message" not in result:
                    result["message"] = data["message"]

                return result

        raise exceptions.NotFoundError(f"inventory '{name}' not found")
