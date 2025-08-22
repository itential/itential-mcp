# Copyright (c) 2025 Itential, Inc
# GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)

from typing import Mapping, Any

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
