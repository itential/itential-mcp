# Copyright (c) 2025 Itential, Inc
# GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import annotations

import time
from typing import Any

from itential_mcp.platform.services import ServiceBase


class Service(ServiceBase):
    """Service class for MOP (Method of Procedure) command template operations.

    This service provides methods for managing and executing command templates
    on network devices through the Itential Platform MOP module. Command
    templates enable automated device configuration and validation workflows.

    The service supports:
    - Retrieving available command templates
    - Getting detailed template information
    - Executing templates against multiple devices
    - Running individual commands on devices
    """

    name: str = "mop"

    async def _get_project_id_from_name(self, name: str) -> str:
        """
        Get the project ID for a specified project name.

        Args:
            name (str): Case-sensitive project name to locate

        Returns:
            str: The project ID associated with the project name

        Raises:
            ValueError: If the project name cannot be definitively located
        """
        res = await self.client.get(
            "/automation-studio/projects", params={"equals[name]": name}
        )

        data = res.json()

        if len(data["data"]) != 1:
            raise ValueError(f"unable to locate project `{name}`")

        return data["data"][0]["_id"]

    async def get_command_templates(self) -> list[dict[str, Any]]:
        """
        Get all command templates from Itential Platform.

        Command Templates are run-time templates that actively pass commands to devices
        and evaluate responses against defined rules. Retrieves templates from both
        global space and projects.

        Returns:
            list[dict]: List of command template objects with the following fields:
                - _id: Unique identifier
                - name: Template name
                - description: Template description
                - namespace: Project namespace (null for global templates)
                - passRule: Pass rule configuration (True=all must pass, False=one must pass)

        Raises:
            Exception: If there is an error retrieving command templates
        """
        res = await self.client.get("/mop/listTemplates")
        return res.json()

    async def describe_command_template(
        self, name: str, project: str | None = None
    ) -> dict[str, Any]:
        """
        Get detailed information about a specific command template.

        Args:
            name (str): Name of the command template to describe
            project (str | None): Project name containing the template (None for global templates)

        Returns:
            dict: Command template details with the following fields:
                - _id: Unique identifier
                - name: Template name
                - commands: List of commands and associated rules
                - namespace: Project namespace (null for global templates)
                - passRule: Pass rule configuration (True=all must pass, False=one must pass)

        Raises:
            ValueError: If the project name cannot be located
            Exception: If there is an error retrieving the command template
        """
        template_name = name
        if project is not None:
            project_id = await self._get_project_id_from_name(project)
            template_name = f"@{project_id}: {name}"

        res = await self.client.get(f"/mop/listATemplate/{template_name}")

        data = res.json()
        if not data:
            raise ValueError(f"Command template '{name}' not found")

        return data[0]

    async def run_command_template(
        self, name: str, devices: list[str], project: str | None = None
    ) -> dict[str, Any]:
        """
        Execute a command template against specified devices with rule evaluation.

        Command Templates are run-time templates that actively pass commands to a list
        of specified devices during their runtime. After all responses are collected,
        the output set is evaluated against a set of defined rules. These executed
        templates are typically used as Pre and Post steps, which are usually separated
        by a procedure (router upgrade, service migration, etc.).

        Args:
            name (str): Name of the command template to run
            devices (list[str]): List of device names to run the template against
            project (str | None): Project containing the template (None for global templates)

        Returns:
            dict: Execution results with the following structure:
                - name: Command template name that was executed
                - all_pass_flag: Whether all rules must pass for success
                - command_results: List of results for each command/device combination

        Raises:
            ValueError: If the project name cannot be located
            Exception: If there is an error executing the command template
        """
        template_name = name
        if project is not None:
            project_id = await self._get_project_id_from_name(project)
            template_name = f"@{project_id}: {name}"

        body = {
            "template": template_name,
            "devices": devices,
        }

        res = await self.client.post("/mop/RunCommandTemplate", json=body)

        return res.json()

    async def run_command(self, cmd: str, devices: list[str]) -> list[dict[str, Any]]:
        """
        Run a single command against multiple devices.

        Args:
            cmd (str): Command to execute on the devices
            devices (list[str]): List of device names to run the command against

        Returns:
            list[dict]: List of command execution results with the following fields:
                - device: Target device name
                - raw: Original command executed on the remote device
                - response: Output from running the command

        Raises:
            Exception: If there is an error executing the command on devices
        """
        body = {
            "command": cmd,
            "devices": devices,
        }

        res = await self.client.post("/mop/RunCommandDevices", json=body)

        return res.json()

    async def create_command_template(
        self,
        name: str,
        commands: list[dict[str, Any]],
        project: str | None = None,
        description: str | None = None,
        os: str = "",
        pass_rule: bool = True,
        ignore_warnings: bool = False,
    ) -> dict[str, Any]:
        """
        Create a new command template in Itential Platform.

        Creates a new command template with the specified name, commands, and validation rules.
        Templates can be created in the global space or within a specific project.

        Args:
            name (str): Name for the command template
            commands (list[dict[str, Any]]): List of commands with their validation rules
            project (str | None): Project name to create the template in (None for global)
            description (str | None): Optional description for the template
            os (str): Operating system type (default: empty string)
            pass_rule (bool): Pass rule configuration (True=all must pass, False=one must pass)
            ignore_warnings (bool): Whether to ignore warnings during execution

        Returns:
            dict: Created command template object with the following fields:
                - _id: Unique identifier
                - name: Template name
                - commands: List of commands and rules
                - namespace: Project namespace (null for global templates)
                - passRule: Pass rule configuration
                - created: Creation timestamp
                - createdBy: User who created the template

        Raises:
            ValueError: If the project name cannot be located
            Exception: If there is an error creating the command template
        """
        template_name = name
        if project is not None:
            project_id = await self._get_project_id_from_name(project)
            template_name = f"@{project_id}: {name}"

        body = {
            "mop": {
                "name": template_name,
                "os": os,
                "passRule": pass_rule,
                "ignoreWarnings": ignore_warnings,
                "commands": commands,
                "created": int(time.time() * 1000),  # Current timestamp in milliseconds
                "createdBy": "system",  # This should be replaced with actual user
                "lastUpdated": int(time.time() * 1000),
                "lastUpdatedBy": "system",
            }
        }

        if description is not None:
            body["mop"]["description"] = description

        res = await self.client.post("/mop/createTemplate", json=body)
        return res.json()

    async def update_command_template(
        self,
        name: str,
        commands: list[dict[str, Any]],
        project: str | None = None,
        description: str | None = None,
        os: str = "",
        pass_rule: bool = True,
        ignore_warnings: bool = False,
    ) -> dict[str, Any]:
        """
        Update an existing command template in Itential Platform.

        Updates an existing command template with new commands and validation rules.
        The template must exist in the specified project or global space.

        Args:
            name (str): Name of the command template to update
            commands (list[dict[str, Any]]): List of commands with their validation rules
            project (str | None): Project name containing the template (None for global)
            description (str | None): Optional description for the template
            os (str): Operating system type (default: empty string)
            pass_rule (bool): Pass rule configuration (True=all must pass, False=one must pass)
            ignore_warnings (bool): Whether to ignore warnings during execution

        Returns:
            dict: Update result with the following fields:
                - acknowledged: Whether the update was acknowledged
                - modifiedCount: Number of documents modified
                - matchedCount: Number of documents matched

        Raises:
            ValueError: If the project name cannot be located or template not found
            Exception: If there is an error updating the command template
        """
        template_name = name
        if project is not None:
            project_id = await self._get_project_id_from_name(project)
            template_name = f"@{project_id}: {name}"

        # Get existing template to preserve metadata
        try:
            existing_template = await self.describe_command_template(name, project)
        except ValueError:
            raise ValueError(f"Command template '{name}' not found")

        body = {
            "mop": {
                "_id": existing_template["_id"],
                "name": template_name,
                "os": os,
                "passRule": pass_rule,
                "ignoreWarnings": ignore_warnings,
                "commands": commands,
                "created": existing_template.get("created"),
                "createdBy": existing_template.get("createdBy"),
                "lastUpdated": int(time.time() * 1000),
                "lastUpdatedBy": "system",
            }
        }

        if description is not None:
            body["mop"]["description"] = description

        res = await self.client.put(f"/mop/updateTemplate/{template_name}", json=body)
        return res.json()
