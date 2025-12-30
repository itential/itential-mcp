# Copyright (c) 2025 Itential, Inc
# GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import annotations

from typing import Mapping, Any, Literal

from itential_mcp.core import exceptions

from itential_mcp.platform.services import ServiceBase


class Service(ServiceBase):
    """Service class for managing Automation Studio workflows in Itential Platform.

    The Service provides methods for interacting with Automation Studio
    workflows, including retrieving workflow details and metadata. Workflows are
    the core automation processes in Itential Platform that define executable
    processes for orchestrating network operations, device management, and
    service provisioning.

    This service handles workflow discovery across both global space and project
    namespaces, providing unified access to workflow resources regardless of
    their organizational scope.

    Inherits from ServiceBase and implements the required describe method for
    retrieving detailed workflow information by unique identifier.

    Args:
        client: An AsyncPlatform client instance for communicating with
            the Itential Platform Automation Studio API

    Attributes:
        client (AsyncPlatform): The platform client used for API communication
        name (str): Service identifier for logging and identification
    """

    name: str = "automation_studio"

    async def _describe_workflow(self, params: dict | None = None) -> Mapping[str, Any]:
        """Internal helper method for retrieving workflow details from Automation Studio.

        This private method handles the common workflow retrieval logic used by both
        describe_workflow_with_id and describe_workflow_with_name methods. It fetches
        workflow data from the Automation Studio API using the provided query parameters
        and validates that exactly one workflow is found.

        Args:
            params (dict | None): Optional query parameters for filtering workflows.
                Common parameters include equals[_id] for ID-based lookups and
                equals[name] for name-based lookups. Defaults to None.

        Returns:
            Mapping[str, Any]: The workflow object containing all workflow details
                including name, description, tasks, and configuration.

        Raises:
            NotFoundError: If no workflow is found or if multiple workflows match
                the query parameters.
        """
        res = await self.client.get("/automation-studio/workflows", params=params)

        data = res.json()

        if data["total"] != 1:
            raise exceptions.NotFoundError("workflow not found")

        return data["items"][0]

    async def describe_workflow_with_id(self, workflow_id: str) -> Mapping[str, Any]:
        """
        Describe an Automation Studio workflow

        This method will attempt to get the specified workflow from the
        server and return it to the calling function as a Python dict
        object.  If the workflow does not exist on the server, this method
        will raise an exception.

        This method will searches for the workflow using the unique
        id field.  It will find the workflow regardless of whether it
        is in global space or in a project.

        Args:
            workflow_id (str): The unique identifer for the workflow
                to retrieve

        Returns:
            Mapping: An object that represents the workflow

        Raises:
            NotFoundError: If the workflow could not be found on
                the server
        """
        return await self._describe_workflow(params={"equals[_id]": workflow_id})

    async def describe_workflow_with_name(self, name: str) -> Mapping[str, Any]:
        """Describe an Automation Studio workflow by name.

        This method retrieves a specific workflow from the Automation Studio
        using the workflow name as the search criteria. It provides an alternative
        to describe_workflow_with_id when the workflow ID is not known but the
        name is available.

        The method searches for workflows across both global space and project
        namespaces to find the specified workflow by exact name match.

        Args:
            name (str): The exact name of the workflow to retrieve. Workflow
                names are case-sensitive and must match exactly.

        Returns:
            Mapping[str, Any]: An object that represents the workflow containing
                all workflow details including configuration, tasks, and metadata.

        Raises:
            NotFoundError: If the workflow with the specified name could not be
                found on the server.
        """
        return await self._describe_workflow(params={"equals[name]": name})

    async def _get_templates(
        self,
        params: dict | None = None,
    ) -> Mapping[str, Any]:
        """Retrieve templates from Automation Studio with pagination support.

        Internal helper method that handles paginated retrieval of templates from
        the Automation Studio API. This method fetches templates in batches of 100
        and continues until all templates matching the specified parameters are
        retrieved.

        Args:
            params (dict | None): Optional query parameters to filter templates.
                Common parameters include equals[type] for filtering by template
                type, equals[name] for specific template names. Defaults to None.

        Returns:
            Mapping[str, Any]: List of template objects containing template
                metadata including name, type, group, description, command,
                template content, and sample data.

        Raises:
            Exception: If there is an error retrieving templates from the
                Automation Studio API.
        """
        limit = 100
        skip = 0

        if params is None:
            params = {"limit": limit}
        else:
            params["limit"] = limit

        results = list()

        while True:
            params["skip"] = skip

            res = await self.client.get(
                "/automation-studio/templates",
                params=params,
            )

            data = res.json()

            results.extend(data["items"])

            if len(results) == data["total"]:
                break

            skip += limit

        return results

    async def get_templates(
        self, template_type: Literal["textfsm", "jinaj2"] | None = None
    ) -> Mapping[str, Any]:
        """Get all templates from Automation Studio.

        Retrieves all templates from the Automation Studio, with optional filtering
        by template type. Templates are used for text processing, configuration
        generation, and data parsing within automation workflows.

        This method performs paginated requests to retrieve all available templates,
        handling large result sets efficiently by fetching results in batches of 100.

        Args:
            template_type (Literal["textfsm", "jinaj2"] | None): Optional filter to
                retrieve only templates of the specified type. Supported types are
                "textfsm" for TextFSM parsing templates and "jinaj2" for Jinja2
                templating. Defaults to None to retrieve all template types.

        Returns:
            Mapping[str, Any]: A list of template objects containing template
                metadata including name, type, group, description, and template
                content.

        Raises:
            Exception: If there is an error retrieving templates from the
                Automation Studio API.
        """
        params = None
        if template_type is not None:
            params = {"equals[type]": template_type}
        return await self._get_templates(params=params)

    async def describe_template(
        self, name: str, project: str | None = None
    ) -> Mapping[str, Any]:
        """Get detailed information about a specific template from Automation Studio.

        Retrieves comprehensive template information by name, with optional project
        scoping. If a project is specified, the template name is prefixed with the
        project ID to search within the project namespace. Templates are used for
        text processing, configuration generation, and data parsing.

        Args:
            name (str): The name of the template to retrieve. Template names are
                case-sensitive and must match exactly.
            project (str | None): The name of the project the template resides in.
                If None, searches for the template in global space. Defaults to None.

        Returns:
            Mapping[str, Any]: Template details containing name, type, group,
                description, command, template content, and sample data fields.

        Raises:
            NotFoundError: If the specified template name cannot be found in the
                Automation Studio, or if the specified project cannot be found.
            Exception: If there is an error retrieving the template information
                from the Automation Studio API.
        """
        if project is not None:
            p = await self.describe_project(project)
            name = f"@{p['_id']}: {name}"
        res = await self._get_templates(params={"equals[name]": name})
        if len(res) != 1:
            raise exceptions.NotFoundError(f"template {name} could not found")
        return res[0]

    async def create_template(
        self,
        name: str,
        template_type: Literal["textfsm", "jinja2"],
        group: str,
        project: str | None = None,
        description: str | None = None,
        command: str | None = None,
        template: str | None = None,
        data: str | None = None,
    ) -> Mapping[str, str]:
        """Create a new template in Automation Studio.

        Creates a new template with the specified name, type, group, and optional
        content including description, command, template text, and sample data.
        Templates are used for text processing, configuration generation, and
        data parsing within automation workflows.

        Args:
            name (str): The name of the template to create. Template names must be
                unique within the specified project or global space.
            template_type (Literal["textfsm", "jinja2"]): Type of template to create.
                "textfsm" for parsing templates or "jinja2" for configuration templating.
            group (str): The group this template belongs to for organizational purposes.
            project (str | None): The name of the project where this template should
                be created. If None, creates in global space. Defaults to None.
            description (str | None): Optional description providing context about
                the template's purpose and usage. Defaults to None.
            command (str | None): The CLI command to be run on the target device to
                generate source text. Defaults to None.
            template (str | None): The template text used to generate the final output.
                For textfsm templates, this contains parsing rules. For jinja2 templates,
                this contains templating syntax. Defaults to None.
            data (str | None): Sample data used to test the template functionality.
                Defaults to None.

        Returns:
            Mapping[str, str]: Created template object containing the template
                details returned by the API.

        Raises:
            ValueError: If a template with the same name already exists in the
                specified project or global space.
            Exception: If there is an error creating the template in the
                Automation Studio API.
        """
        body = {
            "name": name,
            "type": template_type,
            "group": group,
            "description": description or "",
            "command": command or "",
            "template": template or "",
            "data": data or "",
        }

        res = await self.client.post(
            "/automation-studio/templates", json={"template": body}
        )

        return res.json()["created"]

    async def update_template(
        self,
        name: str,
        project: str | None = None,
        description: str | None = None,
        command: str | None = None,
        template: str | None = None,
        data: str | None = None,
    ) -> Mapping[str, str]:
        """Update an existing template in Automation Studio.

        Updates an existing template with new content including description, command,
        template text, and sample data. The method first retrieves the existing template
        to preserve any fields not specified in the update request. Only specified
        fields will be updated; fields not provided will retain their existing values.

        Args:
            name (str): The name of the template to update. Template names are
                case-sensitive and must match exactly.
            project (str | None): The name of the project where this template resides.
                If None, searches in global space. Defaults to None.
            description (str | None): Optional description providing context about
                the template's purpose and usage. If None, existing value is preserved.
                Defaults to None.
            command (str | None): The CLI command to be run on the target device to
                generate source text. If None, existing value is preserved.
                Defaults to None.
            template (str | None): The template text used to generate the final output.
                For textfsm templates, this contains parsing rules. For jinja2 templates,
                this contains templating syntax. If None, existing value is preserved.
                Defaults to None.
            data (str | None): Sample data used to test the template functionality.
                If None, existing value is preserved. Defaults to None.

        Returns:
            Mapping[str, str]: Updated template object containing the template
                details returned by the API.

        Raises:
            NotFoundError: If the specified template name cannot be found in the
                Automation Studio.
            Exception: If there is an error updating the template in the
                Automation Studio API.
        """
        body = {
            "name": name,
            "group": None,
            "type": None,
            "description": description or "",
            "command": command or "",
            "template": template or "",
            "data": data or "",
        }

        existing = await self.describe_template(name=name, project=project)

        for key, value in body.items():
            if existing[key] is not None and not value:
                body[key] = existing[key]

        res = await self.client.put(
            f"/automation-studio/templates/{existing['_id']}", json={"update": body}
        )

        return res.json()["updated"]

    async def get_projects(self) -> list[Mapping[str, Any]]:
        """Get all projects from Automation Studio.

        Retrieves all projects from the Automation Studio. Projects in Automation
        Studio organize workflows, templates, and other automation artifacts into
        logical groupings for team collaboration and asset management.

        This method performs paginated requests to retrieve all available projects,
        handling large result sets efficiently by fetching results in batches of 100.
        The method continues fetching until all projects have been retrieved based
        on the total count returned by the API.

        Returns:
            list[Mapping[str, Any]]: A list of project objects containing project
                metadata including unique identifier, name, description, and other
                project-specific attributes.

        Raises:
            Exception: If there is an error retrieving projects from the
                Automation Studio API.
        """
        limit = 100
        skip = 0

        params = {"limit": limit}

        results = list()

        while True:
            params["skip"] = skip

            res = await self.client.get(
                "/automation-studio/projects",
                params=params,
            )

            data = res.json()

            results.extend(data["data"])

            if len(results) == data["metadata"]["total"]:
                break

            skip += limit

        return results

    async def describe_project(self, name: str) -> dict:
        """Get detailed information about a specific Automation Studio project.

        Retrieves comprehensive project information including all components
        (workflows, templates, and other artifacts) contained within the project
        along with their metadata and organization structure.

        This method first searches for the project by name to get its unique
        identifier, then retrieves the full project details including all
        associated components and their relationships.

        Args:
            name (str): The name of the project to retrieve. Project names are
                case-sensitive and must match exactly.

        Returns:
            dict: Detailed project information containing project metadata,
                components list, and organizational structure including all
                workflows, templates, and other artifacts within the project.

        Raises:
            NotFoundError: If the specified project name cannot be found in
                the Automation Studio.
            Exception: If there is an error retrieving the project information
                from the Automation Studio API.
        """
        res = await self.client.get(
            "/automation-studio/projects", params={"equals[name]": name}
        )

        json_data = res.json()

        if json_data["metadata"]["total"] != 1:
            raise exceptions.NotFoundError(f"unable to find project: {name}")

        project_id = json_data["data"][0]["_id"]

        res = await self.client.get(f"/automation-studio/projects/{project_id}")

        json_data = res.json()

        return json_data["data"]
