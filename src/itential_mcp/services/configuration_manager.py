# Copyright (c) 2025 Itential, Inc
# GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)

import json

import ipsdk

from itential_mcp import exceptions

from itential_mcp.services import ServiceBase


class Service(ServiceBase):

    name: str = "configuration_manager"

    async def get_golden_config_trees(self) -> list[dict]:
        """
        Retrieve all Golden Configuration trees from the Configuration Manager.

        This method fetches a list of all Golden Configuration trees that have been
        created in the Configuration Manager. Golden Configuration trees are
        hierarchical templates used for managing device configurations with
        version control and variable substitution capabilities.

        Returns:
            list[dict]: List of Golden Configuration tree objects containing
                tree metadata including IDs, names, device types, and versions

        Raises:
            None: This method does not raise any specific exceptions
        """
        res = await self.client.get("/configuration_manager/configs")
        return res.json()

    async def create_golden_config_tree(
        self,
        name: str,
        device_type: str,
        template: str | None = None,
        variables: dict | None = None,
    ) -> dict:
        """
        Create a new Golden Configuration tree in the Configuration Manager.

        This method creates a new Golden Configuration tree with the specified name
        and device type. Optionally, it can set initial variables and a template
        for the root node. The tree provides a hierarchical structure for managing
        device configurations with version control capabilities.

        Args:
            name (str): Name of the Golden Configuration tree to create
            device_type (str): Device type this tree is designed for
            template (str | None): Optional configuration template for the root node
            variables (dict | None): Optional variables to associate with the initial version

        Returns:
            dict: Created tree object containing tree metadata including ID and name

        Raises:
            ServerException: If there is an error creating the Golden Configuration tree
                or setting the template/variables
        """
        try:
            res = await self.client.post(
                "/configuration_manager/configs",
                json={"name": name, "deviceType": device_type},
            )
            tree_id = res.json()["id"]
        except ipsdk.exceptions.ServerError as exc:
            msg = json.loads(exc.details["response_body"])
            raise exceptions.ServerException(msg)

        if variables:
            body = {"name": "initial", "variables": variables}

            await self.client.put(
                f"/configuration_manager/configs/{tree_id}/initial", json=body
            )

        if template:
            await self.set_golden_config_template(tree_id, "initial", template)

        return res.json()

    async def describe_golden_config_tree_version(
        self, tree_id: str, version: str
    ) -> dict:
        """
        Retrieve detailed information about a specific version of a Golden Configuration tree.

        This method fetches comprehensive details about a specific version of a
        Golden Configuration tree, including the tree structure, node configurations,
        variables, and metadata associated with that version.

        Args:
            tree_id (str): Unique identifier of the Golden Configuration tree
            version (str): Version identifier of the tree to describe

        Returns:
            dict: Detailed tree version information including root node structure,
                variables, and configuration metadata

        Raises:
            None: This method does not raise any specific exceptions
        """
        res = await self.client.get(
            f"/configuration_manager/configs/{tree_id}/{version}"
        )
        return res.json()

    async def set_golden_config_template(
        self, tree_id: str, version: str, template: str
    ) -> dict:
        """
        Set or update the configuration template for a specific tree version.

        This method updates the configuration template associated with the root node
        of a specific version of a Golden Configuration tree. The template defines
        the configuration structure and can include variable placeholders for
        dynamic configuration generation.

        Args:
            tree_id (str): Unique identifier of the Golden Configuration tree
            version (str): Version identifier of the tree to update
            template (str): Configuration template content to set for the tree

        Returns:
            dict: Updated configuration specification object containing the
                template and variables information

        Raises:
            None: This method does not raise any specific exceptions
        """
        tree_version = await self.describe_golden_config_tree_version(
            tree_id=tree_id,
            version=version,
        )

        config_id = tree_version["root"]["attributes"]["configId"]
        variables = tree_version["variables"]

        body = {"data": {"template": template, "variables": variables}}

        r = await self.client.put(
            f"/configuration_manager/config_specs/{config_id}", json=body
        )

        return r.json()

    async def add_golden_config_node(
        self, tree_name: str, version: str, path: str, name: str, template: str
    ) -> dict:
        """
        Add a new node to a specific version of a Golden Configuration tree.

        This method creates a new node within the hierarchical structure of a
        Golden Configuration tree at the specified path. The node can have an
        associated configuration template and becomes part of the tree's
        configuration structure.

        Args:
            tree_name (str): Name of the Golden Configuration tree
            version (str): Version of the tree to add the node to
            path (str): Parent path where the node should be added
            name (str): Name of the new node to create
            template (str): Configuration template to associate with the node

        Returns:
            dict: Created node object containing node metadata and configuration details

        Raises:
            NotFoundError: If the specified tree name cannot be found
            ServerException: If there is an error creating the node or setting its template
        """
        # Lookup tree id
        trees = await self.get_golden_config_trees()
        for ele in trees:
            if ele["name"] == tree_name:
                tree_id = ele["id"]
                break
        else:
            raise exceptions.NotFoundError(f"tree {tree_name} could not be found")

        try:
            res = await self.client.post(
                f"/configuration_manager/configs/{tree_id}/{version}/{path}",
                json={"name": name},
            )
        except ipsdk.exceptions.ServerError as exc:
            msg = json.loads(exc.details["response_body"])
            raise exceptions.ServerException(msg)

        if template:
            await self.set_golden_config_template(tree_id, version, template)

        return res.json()

    async def describe_device_group(self, name: str) -> dict:
        """
        Retrieve detailed information about a specific device group by name.

        This method fetches comprehensive details about a device group including
        its unique identifier, list of member devices, description, and other
        metadata. The device group is identified by its name.

        Args:
            name (str): Name of the device group to retrieve details for

        Returns:
            dict: Device group details containing ID, name, devices list, and description

        Raises:
            NotFoundError: If the specified device group name cannot be found
            ServerException: If there is an error communicating with the server
        """
        res = await self.client._send_request(
            "GET", "/configuration_manager/name/devicegroups", json={"groupName": name}
        )
        return res.json()

    async def get_device_groups(self) -> list[dict]:
        """
        Retrieve all device groups from the Configuration Manager.

        This method fetches a complete list of all device groups that have been
        configured in the Configuration Manager. Device groups are logical
        collections of network devices that can be managed together for
        configuration, compliance, and automation tasks.

        Returns:
            list[dict]: List of device group objects containing group metadata
                including IDs, names, device lists, and descriptions

        Raises:
            ServerException: If there is an error communicating with the server
        """
        res = await self.client.get("/configuration_manager/deviceGroups")
        return res.json()

    async def create_device_group(
        self, name: str, devices: list, description: str | None = None
    ) -> dict:
        """
        Create a new device group in the Configuration Manager.

        This method creates a new device group with the specified name and
        optional description. A list of device names can be provided to
        populate the group initially. The method checks for duplicate
        group names and raises an error if a group with the same name
        already exists.

        Args:
            name (str): Name of the device group to create
            devices (list): List of device names to include in the group
            description (str | None): Optional description for the device group

        Returns:
            dict: Created device group details including ID, name, and status

        Raises:
            ValueError: If a device group with the same name already exists
            ServerException: If there is an error creating the device group
        """
        groups_response = await self.get_device_groups()

        for ele in groups_response:
            if ele["name"] == name:
                raise ValueError(f"device group {name} already exists")

        body = {"groupName": name, "groupDescription": description}

        if devices:
            body["deviceNames"] = ",".join(devices)
        else:
            body["deviceNames"] = ""

        res = await self.client.post("/configuration_manager/devicegroup", json=body)

        return res.json()

    async def add_devices_to_group(self, name: str, devices: list) -> dict:
        """
        Add one or more devices to an existing device group.

        This method adds a list of devices to the specified device group.
        The method first retrieves the device group ID by name, then updates
        the group to include the new devices. The devices list replaces any
        existing devices in the group.

        Args:
            name (str): Name of the device group to add devices to
            devices (list): List of device names to add to the group

        Returns:
            dict: Operation result containing status and details of the update

        Raises:
            NotFoundError: If the specified device group name cannot be found
            ServerException: If there is an error updating the device group
        """
        device_group = await self.describe_device_group(name)
        device_group_id = device_group["id"]

        body = {"details": {"devices": devices}}

        res = await self.client.put(
            f"/configuration_manager/deviceGroups/{device_group_id}", json=body
        )

        return res.json()

    async def remove_devices_from_group(self, name: str, devices: list) -> dict:
        """
        Remove one or more devices from an existing device group.

        This method removes specified devices from a device group by
        reconstructing the device list without the devices to be removed.
        The method retrieves the current group configuration, filters out
        the specified devices, and updates the group with the remaining devices.

        Args:
            name (str): Name of the device group to remove devices from
            devices (list): List of device names to remove from the group

        Returns:
            dict: Operation result containing status and details of the update

        Raises:
            NotFoundError: If the specified device group name cannot be found
            ServerException: If there is an error updating the device group
        """
        data = await self.describe_device_group(name)

        device_group_id = data["id"]

        device_groups = list()
        for ele in data["devices"]:
            if ele not in devices:
                device_groups.append(ele)

        body = {"details": {"devices": device_groups}}

        res = await self.client.put(
            f"/configuration_manager/deviceGroups/{device_group_id}", json=body
        )

        return res.json()
