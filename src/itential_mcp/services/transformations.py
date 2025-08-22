# Copyright (c) 2025 Itential, Inc
# GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)

from typing import Mapping, Any

from itential_mcp.services import ServiceBase


class Service(ServiceBase):
    """Service class for managing Automation Studio transformations in Itential Platform.

    The Service provides methods for interacting with Automation Studio
    transformations, which are data processing and mapping components used within
    workflows to convert, filter, and manipulate data between different formats
    and structures. Transformations enable seamless data integration between
    various network devices, applications, and systems.

    Transformations in Itential Platform support various operations including
    JSON-to-JSON mapping, template rendering, data filtering, and custom
    JavaScript-based data processing. They are essential building blocks for
    creating robust automation workflows that can handle diverse data sources
    and formats.

    This service handles transformation discovery across both global space and
    project namespaces, providing unified access to transformation resources
    regardless of their organizational scope.

    Inherits from ServiceBase and implements the required describe method for
    retrieving detailed transformation information by unique identifier.

    Args:
        client: An AsyncPlatform client instance for communicating with
            the Itential Platform Automation Studio API

    Attributes:
        client (AsyncPlatform): The platform client used for API communication
        name (str): Service identifier for logging and identification
    """

    name: str = "transformations"

    async def describe_transformation(self, transformation_id: str) -> Mapping[str, Any]:
        """
        Describe an Automation Studio transformation

        This method will retreive the transformation from the server and
        return it to the calling function as a Python dict object.  If
        the transformation does not exist on the server, this method will
        raise an exception.

        This method will searches for the transformation using the unique
        id field.  It will find the transformation regardless of whether it
        is in global space or in a project.

        Args:
            transformation_id (str): The unique identifer for the transformation
                to retrieve

        Returns:
            Mapping: An object that represents the transformation

        Raises:
            NotFoundError: If the transformation could not be found on
                the server
        """
        res = await self.client.get(f"/transformations/{transformation_id}")
        return res.json()
