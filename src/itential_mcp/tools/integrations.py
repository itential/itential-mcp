# Copyright (c) 2025 Itential, Inc
# GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)

from typing import Annotated

from pydantic import Field

from fastmcp import Context

from itential_mcp import errors


async def get_integration_models(
    ctx: Annotated[Context, Field(
        description="The FastMCP Context object"
    )]
) -> dict:
    """
    Get all integration models available from Itential Platform

    This tool will retrieve all of the integration models that have been
    added to Itential Platform.  It will return a list of objects where
    each element represents an available integration model.

    Args:
        ctx (Context): The FastMCP Context object

    Returns:
        list[dict]: A list of objects that present the integrationt models
            with the following fields defined:
            - id: The unique identifer assigned by Itential Platform
            - title: The text title of the model taken from the info block
                of the OpenAPI spec document
            - version: The version of the model taken from the info block
                of the OpenAPI spec document
            - description: An optional description of the model

    Raises:
        None
    """
    await ctx.info("inside get_integration_models(...)")

    client = ctx.request_context.lifespan_context.get("client")

    res = await client.get("/integration-models")

    data = res.json()

    results = list()

    for ele in data["integrationModels"]:
        results.append({
            "id": ele["versionId"],
            "title": ele["versionId"].split(":")[0],
            "version": ele["properties"]["version"],
            "description": ele.get("description"),
        })

    return results


async def create_integration_model(
    ctx: Annotated[Context, Field(
        description="The FastMCP Context object"
    )],
    model: Annotated[dict, Field(
        description="OpenAPI specification"
    )]
) -> dict:
    """
    Create a new integration model on Itential Platform

    This tool will create a new integration model on Itential Platform from
    the provided model schema defined in the model argument.  The schema
    must be a valid OpenAPI spec document in order to create the
    integration model.

    This tool will check if the model already exists on the server and raise
    an error if it does.  The model identifer is a combination of the title
    and version both found in the info block of the OpenAPI spec.

    If the model already exists, an error will be raised.

    This tool will also attempt to validate the OpenAPI spec document before
    attempting to create the integration model.  If the OpenAPI spec
    document is not properly formated, an error will be raised.

    Args:
        ctx (Context): The FastMCP Context object

        model (dict): The OpenAPI schema as a dict object

    Returns:
        dict: An object that represents the create operation with the
            following fields:
            - status: Status of the operation.  Valid values for status
              are OK, CREATED
            - model: The OpenAPI specification used to create the
              integration model

    Raises:
        AlreadyExistsError: If the model already exists on the server

    Notes:
        - Allowed values for status are OK or CREATED
    """
    await ctx.info("inside create_integration_model(...)")

    model_id = f"{model['info']['title']}:{model['info']['version']}"

    for ele in await get_integration_models(ctx):
        if ele["id"] == model_id:
            raise errors.AlreadyExistsError(f"model {model_id} already exists")

    client = ctx.request_context.lifespan_context.get("client")

    body = {"model": model}

    await client.put(
        "/integration-models/validation",
        json=body
    )

    res = await client.post(
        "/integration-models",
        json=body
    )

    data = res.json()

    return {
        "status": data["status"],
        "message": data["message"]
    }
