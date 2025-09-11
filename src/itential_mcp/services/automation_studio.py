# Copyright (c) 2025 Itential, Inc
# GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)

from typing import Mapping, Any, Sequence

from itential_mcp import exceptions

from itential_mcp.services import ServiceBase


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

    async def describe_workflow(self, workflow_id: str) -> Mapping[str, Any]:
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
        res = await self.client.get(
            "/automation-studio/workflows",
            params={"equals[_id]": workflow_id}
        )

        data = res.json()

        if data["total"] != 1:
            raise exceptions.NotFoundError(f"workflow id {workflow_id} not found")

        return data["items"][0]

    async def get_templates(
        self,
        include: Sequence[str] | None = ("_id", "name", "group"),
        exclude_project_members: bool = True,
        limit: int = 50,
        sort: str = "group",
        skip: int | None = None,
    ) -> Mapping[str, Any]:
        """List Automation Studio templates with pagination and filters.

        Args:
            include (Sequence[str] | None): Fields to include in the response.
            exclude_project_members (bool): Exclude project member data for speed.
            limit (int): Page size limit.
            sort (str): Sort field.
            skip (int | None): Pagination offset.

        Returns:
            Mapping[str, Any]: Envelope with items, total, skip, limit, count, next, previous.
        """
        params: dict[str, Any] = {
            "exclude-project-members": str(exclude_project_members).lower(),
            "limit": limit,
            "sort": sort,
        }

        if include:
            params["include"] = ",".join(include)
        if skip is not None:
            params["skip"] = skip

        res = await self.client.get("/automation-studio/templates", params=params)
        return res.json()

    async def create_template(
        self,
        name: str,
        group: str,
        description: str,
        template: str,
        data: str = "",
        command: str = "",
        type: str = "jinja2",
    ) -> Mapping[str, Any]:
        """Create a new Automation Studio template.

        Args:
            name (str): Template name.
            group (str): Group name.
            description (str): Template description.
            template (str): Template body (e.g., Jinja2).
            data (str): Default data JSON string.
            command (str): Optional command string.
            type (str): Template type (default: jinja2).

        Returns:
            Mapping[str, Any]: API response including created template and edit link.
        """
        body = {
            "template": {
                "command": command,
                "template": template,
                "data": data,
                "type": type,
                "name": name,
                "description": description,
                "group": group,
            }
        }
        res = await self.client.post("/automation-studio/templates", json=body)
        return res.json()

    async def update_template(
        self,
        template_id: str,
        name: str,
        group: str,
        description: str,
        template: str,
        data: str = "",
        command: str = "",
        type: str = "jinja2",
    ) -> Mapping[str, Any]:
        """Update an existing Automation Studio template by id.

        Args:
            template_id (str): The template _id to update.
            name (str): Template name.
            group (str): Group name.
            description (str): Template description.
            template (str): Template body.
            data (str): Default data JSON string.
            command (str): Optional command string.
            type (str): Template type.

        Returns:
            Mapping[str, Any]: API response including updated template and edit link.
        """
        body = {
            "update": {
                "name": name,
                "command": command,
                "template": template,
                "type": type,
                "data": data,
                "group": group,
                "description": description,
            }
        }
        res = await self.client.put(
            f"/automation-studio/templates/{template_id}", json=body
        )
        return res.json()
