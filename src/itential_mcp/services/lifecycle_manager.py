# Copyright (c) 2025 Itential, Inc
# GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)

import asyncio

from typing import Mapping, Any, Sequence

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

    name: str = "lifecycle_manager"

    async def get_resources(self) -> Sequence[Mapping[str, Any]]:
        """Get all Lifecycle Manager resource models from Itential Platform.

        Retrieves all resource models using efficient parallel pagination to minimize
        total retrieval time. Makes parallel API calls in chunks of 100 documents
        until all resources are retrieved.

        Returns:
            Sequence[Mapping[str, Any]]: List of resource model objects with the
                following fields:
                - _id: Unique identifier for the resource
                - name: Resource model name
                - description: Resource model description

        Raises:
            Exception: If there is an error retrieving resources from the platform
        """
        limit = 100

        # Get the first page to determine total count
        res = await self.client.get(
            "/lifecycle-manager/resources",
            params={"limit": limit, "skip": 0},
        )

        data = res.json()
        total = data["metadata"]["total"]

        # If no resources, return empty list early
        if total == 0:
            return []

        # If we got all data in the first request, return it
        if total <= limit:
            return data["data"]

        # Create tasks for parallel retrieval of remaining pages
        tasks = []
        results = data["data"]  # Start with first page data

        # Calculate remaining pages and create parallel tasks
        for skip in range(limit, total, limit):
            remaining = total - skip
            current_limit = min(limit, remaining)

            task = self._fetch_page(
                "/lifecycle-manager/resources", skip, current_limit
            )
            tasks.append(task)

        # Execute all tasks in parallel
        if tasks:
            page_results = await asyncio.gather(*tasks, return_exceptions=True)

            # Process results and handle any exceptions
            for result in page_results:
                if isinstance(result, Exception):
                    raise result
                results.extend(result)

        return results

    async def _fetch_page(
        self,
        endpoint: str,
        skip: int,
        limit: int
    ) -> Sequence[Mapping[str, Any]]:
        """Fetch a single page of data from the specified endpoint.

        Args:
            endpoint (str): The API endpoint to fetch data from
            skip (int): Number of documents to skip
            limit (int): Maximum number of documents to retrieve

        Returns:
            Sequence[Mapping[str, Any]]: List of objects from this page
        """
        res = await self.client.get(
            endpoint,
            params={"limit": limit, "skip": skip},
        )

        data = res.json()
        return data["data"]

    async def describe_resource(self, name: str) -> Mapping[str, Any]:
        """
        Describe a Lifecycle Manager resource model

        This method will retrieve the Lifecycle Manager resource model from
        the server and return it to the calling function as a Python dict
        object. If the model specified by the name argument could not be
        found on the server, this method will raise an exception.

        Args:
            name (str): Name of the resource model to retrieve. This
                argument is case sensitive

        Returns:
            Mapping[str, Any]: An object that represents the Lifecycle Manager
                resource model

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

    async def create_resource(
        self, name: str, schema: str | dict, description: str | None = None
    ) -> dict:
        """Create a new Lifecycle Manager resource model in Itential Platform.

        Creates a new resource model with the specified name, JSON schema definition,
        and optional description. The schema defines the structure, validation rules,
        and lifecycle workflows for instances of this resource type.

        Args:
            name (str): Unique name for the resource model. Must be unique within
                the platform and is case sensitive.
            schema (str | dict): JSON Schema definition for the resource model.
                Can be provided as a JSON string or Python dictionary. Defines
                the structure and validation rules for resource instances.
            description (str | None, optional): Human-readable description of
                the resource model. Defaults to None.

        Returns:
            dict: The created resource model object containing:
                - _id: Unique identifier for the resource model
                - name: Resource model name
                - schema: The JSON schema definition
                - description: Resource model description (if provided)
                - Additional metadata fields

        Raises:
            Exception: If there is an error creating the resource model,
                such as duplicate names or invalid schema definitions.
        """
        body = {"name": name, "schema": schema}

        if description is not None:
            body["description"] = description

        res = await self.client.post("/lifecycle-manager/resources", json=body)

        return res.json()["data"]

    async def get_instances(
        self,
        resource_name: str,
    ) -> Sequence[Mapping[str, Any]]:
        """Get all instances of a Lifecycle Manager resource model from Itential Platform.

        Retrieves all instances of the specified resource model using efficient parallel
        pagination to minimize total retrieval time. Makes parallel API calls in chunks
        of 100 documents until all instances are retrieved.

        Args:
            resource_name (str): Name of the resource model to get instances for

        Returns:
            Sequence[Mapping[str, Any]]: List of resource instance objects with the
                following fields:
                - _id: Unique identifier for the instance
                - Additional fields based on the resource model schema

        Raises:
            NotFoundError: If the resource model could not be found
            Exception: If there is an error retrieving instances from the platform
        """
        resource = await self.describe_resource(resource_name)
        model_id = resource["_id"]

        limit = 100

        # Get the first page to determine total count
        res = await self.client.get(
            f"/lifecycle-manager/resources/{model_id}/instances",
            params={"limit": limit, "skip": 0},
        )

        data = res.json()
        total = data["metadata"]["total"]

        # If no instances, return empty list early
        if total == 0:
            return []

        # If we got all data in the first request, return it
        if total <= limit:
            return data["data"]

        # Create tasks for parallel retrieval of remaining pages
        tasks = []
        results = data["data"]  # Start with first page data

        # Calculate remaining pages and create parallel tasks
        for skip in range(limit, total, limit):
            remaining = total - skip
            current_limit = min(limit, remaining)

            task = self._fetch_page(
                f"/lifecycle-manager/resources/{model_id}/instances",
                skip,
                current_limit,
            )
            tasks.append(task)

        # Execute all tasks in parallel
        if tasks:
            page_results = await asyncio.gather(*tasks, return_exceptions=True)

            # Process results and handle any exceptions
            for result in page_results:
                if isinstance(result, Exception):
                    raise result
                results.extend(result)

        return results


    async def describe_instance(
        self,
        resource_name: str,
        instance_name: str
    ) -> dict:
        """Retrieve a specific instance of a Lifecycle Manager resource model.

        Looks up and returns detailed information for a specific resource instance
        by name within the specified resource model. The instance contains the
        actual data values conforming to the resource model's schema.

        Args:
            resource_name (str): Name of the resource model that contains
                the instance. Must match an existing resource model name exactly.
            instance_name (str): Name of the specific instance to retrieve.
                Must match an existing instance name exactly.

        Returns:
            dict: The resource instance object containing:
                - _id: Unique identifier for the instance
                - name: Instance name
                - instanceData: The actual data values for this instance
                - Additional metadata fields

        Raises:
            NotFoundError: If the resource model or instance cannot be found
                on the server.
        """
        resource = await self.describe_resource(resource_name)
        model_id = resource["_id"]

        res = await self.client.get(
            f"/lifecycle-manager/resources/{model_id}/instances",
            params={"equals[name]": instance_name}
        )

        json_data = res.json()

        if json_data["metadata"]["total"] != 1:
            raise exceptions.NotFoundError(f"unable to find instance {instance_name}")

        return json_data["data"][0]

    async def run_action(
        self,
        resource_name: str,
        action_name: str,
        instance_name: str | None = None,
        instance_description: str | None = None,
        input_params: dict | None = None
    ) -> dict:
        """Execute a lifecycle action on a Lifecycle Manager resource model.

        Runs a specific lifecycle action (CREATE, UPDATE, DELETE) defined in
        the resource model. Actions can operate on existing instances or create
        new ones depending on the action type and parameters provided.

        Args:
            resource_name (str): Name of the resource model that defines
                the action. Must match an existing resource model name exactly.
            action_name (str): Name of the lifecycle action to execute.
                Must match an action defined in the resource model.
            instance_name (str | None, optional): Name of the instance to
                operate on. Required for UPDATE and DELETE actions, used as
                the name for new instances in CREATE actions. Defaults to None.
            instance_description (str | None, optional): Description for
                the instance being created or updated. Defaults to None.
            input_params (dict | None, optional): Input parameters for the
                action execution. For DELETE actions on existing instances,
                defaults to the instance's current data if not provided.
                Defaults to None.

        Returns:
            dict: An object that represents the status of the action

        Raises:
            NotFoundError: If the resource model, action, or instance
                (when required) cannot be found on the server.
        """
        resource = await self.describe_resource(resource_name)
        resource_id = resource["_id"]

        action_id = None
        action_type = None

        for ele in resource["actions"]:
            if ele["name"] == action_name:
                action_id = ele["_id"]
                action_type = ele["type"]
                break
        else:
            raise exceptions.NotFoundError(
                f"unable to find action {action_name} for resource {resource_name}",
            )

        body = {"actionId": action_id}

        if instance_name is not None:
            if action_type == "create":
                body["instanceName"] = instance_name
            else:
                instance = await self.describe_instance(resource_name, instance_name)
                body["instance"] = instance["_id"]
                if action_type == "delete" and input_params is None:
                    input_params = instance["instanceData"]

        if input_params:
            body["inputs"] = input_params

        if instance_description:
            body["instanceDescription"] = instance_description

        res = await self.client.post(
            f"/lifecycle-manager/resources/{resource_id}/run-action",
            json=body
        )

        return res.json()
