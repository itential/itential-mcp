# Copyright (c) 2025 Itential, Inc
# GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

import ipsdk

from itential_mcp.core import exceptions

from itential_mcp.platform.services import ServiceBase


class Service(ServiceBase):
    """
    Configuration Manager service for managing network device configurations and templates.

    This service provides comprehensive functionality for managing Golden Configuration trees,
    device groups, device management, compliance plans, and template rendering through the
    Itential Configuration Manager. It enables network operators to create, modify, and deploy
    configuration templates across network devices with version control, variable substitution,
    and hierarchical organization.

    The service supports the following key capabilities:
    - Golden Configuration tree management (create, modify, version control)
    - Configuration node management within hierarchical structures
    - Device group creation and management for bulk operations
    - Device configuration retrieval, backup, and deployment
    - Compliance plans execution and management for configuration validation
    - Jinja2 template rendering with variable substitution
    - Template and variable assignment to configuration nodes

    All operations are performed asynchronously through the Itential Platform API,
    providing scalable configuration management for large network infrastructures.

    Attributes:
        name (str): Service identifier used for registration and routing ("configuration_manager").
        client: AsyncPlatform client instance for API communication with the platform.

    Example:
        Basic usage through the service:

        ```python
        service = Service(client)

        # Create a new Golden Configuration tree
        tree = await service.create_golden_config_tree(
            name="cisco-router-template",
            device_type="cisco_ios"
        )

        # Get device configuration
        config = await service.get_device_configuration("router1")

        # Create and manage device groups
        group = await service.create_device_group(
            name="production-routers",
            devices=["router1", "router2"],
            description="Production network routers"
        )

        # Run compliance plans
        result = await service.run_compliance_plan("security-compliance")
        ```
    """

    name: str = "configuration_manager"

    async def get_configuration_parser_names(self) -> list[str]:
        """
        Retrieve list of valid device type names from configuration parsers.

        This method fetches the available configuration parser names which represent
        the valid device types that can be used when creating Golden Configuration trees.

        Returns:
            list[str]: List of parser names (device types) such as 'cisco-ios',
                'arista-eos', 'juniper-junos', etc.

        Raises:
            Exception: If there are API communication failures or server errors
                during the retrieval process.
        """
        res = await self.client.get("/configuration_manager/configurations/parser")
        data = res.json()
        return [parser["name"] for parser in data["list"]]

    async def get_golden_config_trees(self) -> list[dict]:
        """
        Retrieve all Golden Configuration trees from the Configuration Manager.

        This method fetches a list of all Golden Configuration trees that have been
        created in the Configuration Manager. Golden Configuration trees are
        hierarchical templates used for managing device configurations with
        version control and variable substitution capabilities.

        Returns:
            list[dict]: List of Golden Configuration tree objects containing
                tree metadata including IDs, names, device types, and versions.
                Each tree object includes:
                - id: Unique identifier for the tree
                - name: Human-readable name of the tree
                - deviceType: Target device type (e.g., 'cisco_ios', 'juniper_junos')
                - versions: List of available versions for the tree

        Raises:
            Exception: If there are API communication failures or server errors
                during the retrieval process.
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
            ValueError: If the specified device_type is not a valid configuration parser
            ServerException: If there is an error creating the Golden Configuration tree
                or setting the template/variables
        """
        # Validate device_type against available parsers
        valid_device_types = await self.get_configuration_parser_names()
        if device_type not in valid_device_types:
            raise ValueError(
                f"Invalid device_type '{device_type}'. "
                f"Valid types are: {', '.join(valid_device_types)}"
            )

        try:
            res = await self.client.post(
                "/configuration_manager/configs",
                json={"name": name, "deviceType": device_type},
            )
            tree_id = res.json()["id"]
        except ipsdk.exceptions.HTTPStatusError as exc:
            if hasattr(exc, "response") and exc.response is not None:
                msg = exc.response.json()
            else:
                msg = {"error": str(exc)}
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
                variables, and configuration metadata. The response includes:
                - id: Version identifier
                - name: Tree name
                - root: Root node structure with attributes and children
                - variables: Dictionary of template variables for this version
                - created: Creation timestamp
                - modified: Last modification timestamp

        Raises:
            Exception: If the tree ID or version is invalid, or if there are
                API communication failures during the retrieval process.
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
                template and variables information. The response includes:
                - id: Configuration specification ID
                - template: The updated template content
                - variables: Associated variables for the template
                - updated: Timestamp of the update operation

        Raises:
            Exception: If the tree ID or version is invalid, or if there are
                API communication failures during the template update process.
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
        except ipsdk.exceptions.HTTPStatusError as exc:
            if hasattr(exc, "response") and exc.response is not None:
                msg = exc.response.json()
            else:
                msg = {"error": str(exc)}
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
            dict: Device group details containing ID, name, devices list, and description.
                The response includes:
                - id: Unique identifier for the device group
                - name: Human-readable name of the group
                - devices: List of device names that are members of this group
                - description: Optional description text for the group
                - created: Creation timestamp
                - modified: Last modification timestamp

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
                including IDs, names, device lists, and descriptions. Each group
                object includes:
                - id: Unique identifier for the device group
                - name: Human-readable name of the group
                - devices: List of device names that are members of this group
                - description: Optional description text for the group
                - deviceCount: Number of devices in the group
                - created: Creation timestamp
                - modified: Last modification timestamp

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

        body = {
            "groupName": name,
            "groupDescription": description,
            "deviceNames": ",".join(devices),
        }

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

    async def describe_compliance_report(self, report_id: str) -> dict:
        """
        Retrieve detailed compliance report results from Itential Platform.

        Compliance reports contain the results of executing compliance plans against
        network devices, showing configuration validation outcomes, rule violations,
        and compliance status for each checked device.

        Args:
            report_id (str): Unique identifier of the compliance report to retrieve

        Returns:
            dict: Compliance report details containing validation results, device
                compliance status, rule violations, and configuration analysis from
                running compliance checks against network infrastructure

        Raises:
            ServerException: If there is an error communicating with the server
        """
        res = await self.client.get(
            f"/configuration_manager/compliance_reports/details/{report_id}"
        )
        return res.json()

    async def get_devices(self) -> list[dict]:
        """
        Get all devices known to Itential Platform.

        Itential Platform federates device information from multiple sources and makes
        it available for network automation workflows. Devices represent physical or
        virtual network infrastructure that can be managed, configured, and monitored.

        Returns:
            list[dict]: List of device objects containing device information and metadata

        Raises:
            ServerException: If there is an error communicating with the server
        """
        limit = 100
        start = 0
        results = list()

        while True:
            body = {
                "options": {
                    "order": "ascending",
                    "sort": [{"name": 1}],
                    "start": start,
                    "limit": limit,
                }
            }

            res = await self.client.post("/configuration_manager/devices", json=body)
            data = res.json()
            results.extend(data["list"])

            if len(results) == data["return_count"]:
                break

            start += limit

        return results

    async def get_device_configuration(self, name: str) -> str:
        """
        Retrieve the current configuration from a network device.

        Args:
            name (str): Name of the device to retrieve configuration from

        Returns:
            str: The current device configuration

        Raises:
            ValueError: If there is an error retrieving the configuration or device is not found
            ServerException: If there is an error communicating with the server
        """
        try:
            res = await self.client.get(
                f"/configuration_manager/devices/{name}/configuration"
            )
        except ValueError:
            raise

        return res.json()["config"]

    async def backup_device_configuration(
        self, name: str, description: str | None = None, notes: str | None = None
    ) -> dict:
        """
        Create a backup of a device configuration in Itential Platform.

        Configuration backups provide recovery points and change tracking for network
        devices, enabling rollback capabilities and configuration management workflows.

        Args:
            name (str): Name of the device to backup
            description (str | None): Short description of the backup (optional)
            notes (str | None): Additional notes for the backup (optional)

        Returns:
            dict: Backup operation result with the following fields:
                - id: Unique identifier for the backup
                - status: Status of the backup operation
                - message: Descriptive message about the operation status

        Raises:
            ServerException: If there is an error communicating with the server
        """
        body = {
            "name": name,
            "options": {"description": description or "", "notes": notes or ""},
        }

        res = await self.client.post(
            "/configuration_manager/devices/backups", json=body
        )
        return res.json()

    async def apply_device_configuration(self, device: str, config: str) -> dict:
        """
        Apply configuration commands to a network device through Itential Platform.

        Configuration deployment enables automated provisioning and updates of network
        device settings, supporting configuration management and infrastructure automation.

        Args:
            device (str): Name of the target device
            config (str): Configuration string to apply to the device

        Returns:
            dict: Configuration application results and operation status

        Raises:
            ServerException: If there is an error communicating with the server
        """
        body = {"config": {"device": device, "config": config}}

        res = await self.client.post(
            f"/configuration_manager/devices/{device}/configuration", json=body
        )
        return res.json()

    async def render_template(
        self, template: str, variables: dict | None = None
    ) -> str:
        """
        Render a Jinja2 template with provided variables using Configuration Manager.

        This method processes a Jinja2 template string by substituting variables and
        executing template logic (loops, conditionals, etc.) through the Configuration
        Manager's template rendering engine. The rendered output is commonly used for
        generating network device configurations, commands, and other text-based content
        in network automation workflows.

        The template engine supports full Jinja2 syntax including:
        - Variable substitution: {{ variable_name }}
        - Control structures: {% if %}, {% for %}, {% endfor %}
        - Filters and functions: {{ variable | filter }}
        - Template inheritance and includes
        - Complex data structures (nested dicts, lists)

        Args:
            template (str): Jinja2 template string containing the template content
                with variable placeholders and control structures. The template should
                use standard Jinja2 syntax for variable substitution and logic.
            variables (dict | None): Dictionary containing key-value pairs for variable
                substitution in the template. Keys should match variable names used in
                the template. If None, defaults to an empty dictionary.

        Returns:
            str: The fully rendered template string with all variables substituted
                and template logic executed. The output is ready for use as
                configuration content or command sequences.

        Raises:
            Exception: If there are template syntax errors, variable resolution issues,
                or API communication failures during template rendering.

        Example:
            Basic template rendering with variables:

            ```python
            template = '''
            hostname {{ hostname }}
            !
            {% for interface in interfaces %}
            interface {{ interface.name }}
             description {{ interface.description }}
             ip address {{ interface.ip }} {{ interface.mask }}
            {% endfor %}
            '''

            variables = {
                "hostname": "router1",
                "interfaces": [
                    {
                        "name": "GigabitEthernet0/0",
                        "description": "WAN Interface",
                        "ip": "192.168.1.1",
                        "mask": "255.255.255.0"
                    }
                ]
            }

            rendered_config = await service.render_template(template, variables)
            ```
        """
        res = await self.client.post(
            "/configuration_manager/jinja2",
            json={"template": template, "variables": variables or {}},
        )
        data = res.json()
        return data

    async def get_compliance_plans(self) -> list:
        """
        Retrieve all compliance plans from the Configuration Manager.

        This method fetches a complete list of all compliance plans that have been
        configured in the Configuration Manager. Compliance plans define
        configuration validation rules and checks that can be executed against
        network devices to ensure they meet organizational standards.

        Returns:
            list: List of compliance plan objects containing plan metadata
                including IDs, names, descriptions, and throttle settings

        Raises:
            None: This method does not raise any specific exceptions
        """
        limit = 100
        start = 0

        results = list()

        while True:
            body = {"name": "", "options": {"start": start, "limit": limit}}

            res = await self.client.post(
                "/configuration_manager/search/compliance_plans",
                json=body,
            )

            data = res.json()

            results.extend(data["plans"])

            if len(results) == data["totalCount"]:
                break

            start += limit

        return results

    async def run_compliance_plan(self, name: str) -> dict:
        """
        Execute a compliance plan against network devices.

        This method starts the execution of a specified compliance plan by name.
        Compliance plans validate device configurations against organizational
        standards by running predefined checks and rules. The method returns
        the created compliance plan instance with its execution details.

        Args:
            name (str): Case-sensitive name of the compliance plan to execute

        Returns:
            dict: Running compliance plan instance containing execution details
                including instance ID, name, description, and job status

        Raises:
            ValueError: If the specified compliance plan name is not found
        """
        plans_list = await self.get_compliance_plans()

        plan_id = None

        for plan in plans_list:
            if plan["name"] == name:
                plan_id = plan["id"]
                break
        else:
            raise ValueError(f"compliance plan {name} not found")

        await self.client.post(
            "/configuration_manager/compliance_plans/run", json={"planId": plan_id}
        )

        body = {
            "searchParams": {
                "limit": 1,
                "planId": plan_id,
                "sort": {"started": -1},
                "start": 0,
            }
        }

        res = await self.client.post(
            "/configuration_manager/search/compliance_plan_instances", json=body
        )

        json_data = res.json()

        return json_data["plans"][0]
