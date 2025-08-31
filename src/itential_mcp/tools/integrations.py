# Copyright (c) 2025 Itential, Inc
# GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)

from typing import Annotated

from pydantic import Field

from fastmcp import Context

from itential_mcp import exceptions
from itential_mcp.models.integrations import (
    GetIntegrationModelsResponse,
    GetIntegrationModelsElement,
    CreateIntegrationModelResponse
)


__tags__ = ("integrations",)


async def get_integration_models(
    ctx: Annotated[Context, Field(
        description="The FastMCP Context object"
    )]
) -> GetIntegrationModelsResponse:
    """
    Get all integration models from Itential Platform.

    Integration models define API specifications for external systems and services
    that can be integrated with Itential Platform. They are based on OpenAPI
    specifications and enable automated interaction with third-party systems.

    Args:
        ctx (Context): The FastMCP Context object

    Returns:
        GetIntegrationModelsResponse: List of integration model objects with the following fields:
            - id: Unique identifier assigned by Itential Platform
            - title: Model title from the OpenAPI spec info block
            - version: Model version from the OpenAPI spec info block
            - description: Optional model description
    """
    await ctx.info("inside get_integration_models(...)")

    client = ctx.request_context.lifespan_context.get("client")

    res = await client.integrations.get_integration_models()

    results = list()

    for ele in res["integrationModels"]:
        results.append(GetIntegrationModelsElement(
            id=ele["versionId"],
            title=ele["versionId"].split(":")[0],
            version=ele["properties"]["version"],
            description=ele.get("description"),
        ))

    return GetIntegrationModelsResponse(root=results)


async def create_integration_model(
    ctx: Annotated[Context, Field(
        description="The FastMCP Context object"
    )],
    model: Annotated[dict, Field(
        description="OpenAPI specification"
    )]
) -> CreateIntegrationModelResponse:
    """
    Create a new integration model on Itential Platform from an OpenAPI specification.

    Integration models enable Itential Platform to interact with external systems
    by defining their API structure and capabilities. The model must be a valid
    OpenAPI specification document.

    Args:
        ctx (Context): The FastMCP Context object
        model (dict): Valid OpenAPI specification as a dictionary object

    Returns:
        CreateIntegrationModelResponse: Creation operation result with the following fields:
            - status: Operation status (OK or CREATED)
            - message: Descriptive message about the operation

    Raises:
        AlreadyExistsError: If a model with the same title and version already exists

    Notes:
        - Model identifier is derived from title:version in the OpenAPI spec info block
        - OpenAPI specification is validated before creation
    """
    await ctx.info("inside create_integration_model(...)")

    model_id = f"{model['info']['title']}:{model['info']['version']}"

    models_response = await get_integration_models(ctx)
    for ele in models_response.root:
        if ele.id == model_id:
            raise exceptions.AlreadyExistsError(f"model {model_id} already exists")

    client = ctx.request_context.lifespan_context.get("client")

    res = await client.integrations.create_integration_model(model)

    return CreateIntegrationModelResponse(
        status=res["status"],
        message=res["message"]
    )
