# Copyright (c) 2025 Itential, Inc
# GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)




from itential_mcp import exceptions


from itential_mcp.services import ServiceBase


class Service(ServiceBase):
    """
    Integration models service for Itential Platform.
    
    This service provides methods for managing integration models, which define
    API specifications for external systems and services that can be integrated
    with Itential Platform. Integration models are based on OpenAPI specifications
    and enable automated interaction with third-party systems.
    """

    name: str = "integrations"

    async def get_integration_models(self) -> dict:
        """
        Get all integration models from Itential Platform.

        Integration models define API specifications for external systems and services
        that can be integrated with Itential Platform. They are based on OpenAPI
        specifications and enable automated interaction with third-party systems.

        Returns:
            dict: API response containing integration models data with the following structure:
                - integrationModels: List of integration model objects
                
        Raises:
            ConnectionException: If there is an error connecting to the platform
            AuthenticationException: If authentication credentials are invalid
        """
        res = await self.client.get("/integration-models")
        return res.json()


    async def create_integration_model(self, model: dict) -> dict:
        """
        Create a new integration model on Itential Platform from an OpenAPI specification.

        Integration models enable Itential Platform to interact with external systems
        by defining their API structure and capabilities. The model must be a valid
        OpenAPI specification document.

        Args:
            model (dict): Valid OpenAPI specification as a dictionary object containing:
                - info: Required info block with title and version fields
                - paths: API paths and operations
                - components: Reusable components (schemas, parameters, etc.)

        Returns:
            dict: Creation operation result from the platform API response

        Raises:
            AlreadyExistsError: If a model with the same title and version already exists
            ValidationException: If the OpenAPI specification is invalid
            ConnectionException: If there is an error connecting to the platform
            AuthenticationException: If authentication credentials are invalid

        Notes:
            - Model identifier is derived from title:version in the OpenAPI spec info block
            - OpenAPI specification is validated before creation via validation endpoint
        """
        model_id = f"{model['info']['title']}:{model['info']['version']}"

        models_response = await self.get_integration_models()
        for ele in models_response["integrationModels"]:
            if ele["versionId"] == model_id:
                raise exceptions.AlreadyExistsError(f"model {model_id} already exists")

        await self.client.put(
            "/integration-models/validation",
            json={"model": model}
        )

        res = await self.client.post(
            "/integration-models",
            json={"model": model}
        )

        return res.json()
