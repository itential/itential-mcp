# Copyright (c) 2025 Itential, Inc
# GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from typing import Annotated

from pydantic import Field

from fastmcp import Context

from itential_mcp.core import exceptions
from itential_mcp.models import integrations as models


__tags__ = ("integrations",)


async def get_integrations(
    ctx: Annotated[Context, Field(description="The FastMCP Context object")],
    model: Annotated[
        str | None,
        Field(
            description="Return only integrations for the specified model", default=None
        ),
    ],
) -> models.GetIntegrationsResponse:
    """
    Get all integration instances from Itential Platform with optional model filtering.

    This function retrieves integration instances from the Itential Platform.
    Integration instances are configured implementations of integration models
    that define connections to external systems.

    Args:
        ctx (Context): The FastMCP Context object
        model (str | None): Optional model name to filter results. If provided,
            only returns integration instances associated with the specified model.
            Defaults to None (returns all instances).

    Returns:
        GetIntegrationsResponse: Response containing a list of integration instance
            objects with the following fields:
                - name: The integration instance name
                - model: The associated integration model
                - properties: Configuration schema and properties

    Raises:
        Exception: If there is an error retrieving integrations from the platform
    """
    await ctx.info("inside get_integrations(...)")

    client = ctx.request_context.lifespan_context.get("client")

    res = await client.integrations.get_integrations(model=model)

    results = list()

    for ele in res:
        results.append(
            models.GetIntegrationsElement(
                name=ele["name"],
                model=ele["model"],
                properties=ele["properties"],
            )
        )

    return models.GetIntegrationsResponse(root=results)


async def get_integration_models(
    ctx: Annotated[Context, Field(description="The FastMCP Context object")],
) -> models.GetIntegrationModelsResponse:
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
        results.append(
            models.GetIntegrationModelsElement(
                id=ele["versionId"],
                title=ele["versionId"].split(":")[0],
                version=ele["properties"]["version"],
                description=ele.get("description"),
            )
        )

    return models.GetIntegrationModelsResponse(root=results)


async def create_integration_model(
    ctx: Annotated[Context, Field(description="The FastMCP Context object")],
    model: Annotated[dict, Field(description="OpenAPI specification")],
) -> models.CreateIntegrationModelResponse:
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

    return models.CreateIntegrationModelResponse(
        status=res["status"], message=res["message"]
    )
