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
        variables: dict | None = None
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
                json={"name": name, "deviceType": device_type}
            )
            tree_id = res.json()["id"]
        except ipsdk.exceptions.ServerError as exc:
            msg = json.loads(exc.details["response_body"])
            raise exceptions.ServerException(msg)

        if variables:
            body = {
                "name": "initial",
                "variables": variables
            }

            await self.client.put(
                f"/configuration_manager/configs/{tree_id}/initial",
                json=body
            )


        if template:
            await self.set_golden_config_template(tree_id, "initial", template)

        return res.json()

    async def describe_golden_config_tree_version(
        self,
        tree_id: str,
        version: str
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
        self,
        tree_id: str,
        version: str,
        template: str
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

        body = {
            "data": {
                "template": template,
                "variables": variables
            }
        }

        r = await self.client.put(
            f"/configuration_manager/config_specs/{config_id}",
            json=body
        )

        return r.json()


    async def add_golden_config_node(
        self,
        tree_name: str,
        version: str,
        path: str,
        name: str,
        template: str
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
                json={"name": name}
            )
        except ipsdk.exceptions.ServerError as exc:
            msg = json.loads(exc.details["response_body"])
            raise exceptions.ServerException(msg)

        if template:
            await self.set_golden_config_template(tree_id, version, template)

        return res.json()
