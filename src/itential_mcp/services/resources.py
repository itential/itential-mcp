# Copyright (c) 2025 Itential, Inc
# GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)

from typing import Mapping, Any

from itential_mcp import exceptions

from itential_mcp.services import ServiceBase


class Service(ServiceBase):
    """Service class for managing Lifecycle Manager resource models in Itential Platform.

    The Service provides methods for interacting with Lifecycle Manager
    resource models, which define the structure, validation rules, and lifecycle
    workflows for network services and infrastructure components. Resource models
    serve as templates for creating and managing resource instances throughout
    their operational lifecycle.

    Lifecycle Manager resources enable structured management of network services
    by defining JSON Schema-based data models that specify required fields,
    validation constraints, and relationships. These models support complex
    service provisioning, configuration management, and decommissioning workflows.

    Resource models can include lifecycle actions (CREATE, UPDATE, DELETE) that
    define the specific workflows and operations available for instances of that
    resource type. This enables consistent and repeatable service management
    across diverse network infrastructure.

    Inherits from ServiceBase and implements the required describe method for
    retrieving detailed resource model information by name.

    Args:
        client: An AsyncPlatform client instance for communicating with
            the Itential Platform Lifecycle Manager API

    Attributes:
        client (AsyncPlatform): The platform client used for API communication
        name (str): Service identifier for logging and identification
    """

    name: str = "resources"

    async def describe(self, name: str) -> Mapping[str, Any]:
        """
        Describe a Lifecycle Manage resource model

        This method will retrieve the Lifecycle Manager resource model from
        the server and return it to the calling function as a Python dict
        object.  If the model specified by the name argument could not be
        found on the server, this method will raise an exception.

        Args:
            name (str): Name of the resource model to retrieve.  This
                argument is case sensitive

        Returns:
            Mapping: An object that represents the Lifecycle Manager resource
                model

        Raises:
            NotFoundError: If the resource model could not be found on the
                server
        """
        res = await self.client.get(
            "/lifecycle-manager/resources",
            params={"equals[name]": name},
        )

        data = res.json()

        if data["metadata"]["total"] != 1:
            raise exceptions.NotFoundError(f"could not find resource {name}")

        return data["data"][0]
