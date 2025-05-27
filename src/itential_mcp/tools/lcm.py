# Copyright (c) 2025 Itential, Inc
# GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)

from fastmcp import Context
from typing import Any
import asyncio
from fastmcp.exceptions import FastMCPError


async def get_resource_models(
    ctx: Context, 
    limit: int = 50, 
    skip: int = 0, 
    sort: str = "name", 
    order: int = 1, 
    name_filter: str | None = None
    ) -> dict[str, Any]:
    """
    Retrieves a list of all defined resource models within Itential's Lifecycle Manager.
    A resource model is a JSON schema that defines the structure, attributes, and validations 
    for a particular type of managed entity (e.g., switch, firewall, application). This endpoint 
    allows consumers to discover what resources are available for lifecycle orchestration and 
    what properties each expects.

    Args:
        ctx (Context): The FastMCP context object.
        limit (int): Maximum number of records to return.
        skip (int): Number of records to skip for pagination.
        sort (str): Field to sort results by.
        order (int): Sort order (1 for ascending, -1 for descending).
        name_filter (str | None): Optional filter to match resource names.

    Returns:
        dict[str, Any]: A dictionary containing the resource models and related metadata.

    Raises:
        FastMCPError: If there is an error retrieving the resource models.
        asyncio.TimeoutError: If the request times out.
    """
    await ctx.info("inside get_resource_models(...)")

    client = ctx.request_context.lifespan_context.get("client")
    
    params = {
        "limit": limit,
        "skip": skip,
        "sort": sort,
        "order": order
    }
    
    if name_filter:
        params["contains[name]"] = name_filter

    try:
        res = await asyncio.wait_for(
            client.get("/lifecycle-manager/resources", params=params),
            timeout=30
        )
        return res.json()
    except asyncio.TimeoutError:
        await ctx.error("Timeout while retrieving resource models")
        raise
    except Exception as e:
        await ctx.error(f"Error retrieving resource models: {str(e)}")
        raise FastMCPError(f"Failed to retrieve resource models: {str(e)}")


async def get_resource_model(
        ctx: Context, 
        model_id: str
        ) -> dict[str, Any]:
    """
    Retrieves the full definition of a specific resource model in Itential's Lifecycle Manager.
    A resource model defines the structure and validation rules for a resource type using a JSON schema. 
    This endpoint fetches the schema and metadata of a single resource model by its ID.

    Args:
        ctx (Context): The FastMCP context object.
        model_id (str): The unique identifier of the resource model to retrieve.

    Returns:
        dict[str, Any]: A dictionary containing the resource model's schema, metadata, and actions.

    Raises:
        FastMCPError: If there is an error retrieving the resource model.
        asyncio.TimeoutError: If the request times out.
    """
    await ctx.info(f"inside get_resource_model(...) for model_id: {model_id}")

    client = ctx.request_context.lifespan_context.get("client")

    try:
        res = await asyncio.wait_for(
            client.get(
                f"/lifecycle-manager/resources/{model_id}",
                params={"dereference": "action-schemas"}
            ),
            timeout=30
        )
        return res.json()
    except asyncio.TimeoutError:
        await ctx.error(f"Timeout while retrieving resource model {model_id}")
        raise
    except Exception as e:
        await ctx.error(f"Error retrieving resource model {model_id}: {str(e)}")
        raise FastMCPError(f"Failed to retrieve resource model {model_id}: {str(e)}")


async def get_resource_instances(
    ctx: Context,
    model_id: str,
    limit: int = 25,
    skip: int = 0,
    sort: str = "name",
    order: int = 1,
    name_filter: str | None = None,
    include_deleted: bool = False
    ) -> dict[str, Any]:
    """
    Fetches a list of all existing instances of a specified resource model in Itential Lifecycle Manager. 
    Each instance represents a real-world entity (e.g., a specific firewall, router, or virtual machine) that conforms to the structure defined by its resource model.

    Args:
        ctx (Context): The FastMCP context object.
        model_id (str): ID of the resource model
        limit (int): Maximum number of records to return
        skip (int): Number of records to skip
        sort (str): Field to sort by
        order (int): Sort order (1 for ascending, -1 for descending)
        name_filter (str | None): Filter instances by name
        include_deleted (bool): Whether to include deleted instances

    Returns:
        dict[str, Any]: Dictionary containing resource instances and metadata

    Raises:
        FastMCPError: If there is an error retrieving the resource instances
        asyncio.TimeoutError: If the request times out
    """
    await ctx.info(f"inside get_resource_instances(...) for model_id: {model_id}")

    client = ctx.request_context.lifespan_context.get("client")

    params = {
        "limit": limit,
        "skip": skip,
        "sort": sort,
        "order": order,
        "equals[modelId]": model_id,
        "include-deleted": str(include_deleted).lower()
    }

    if name_filter:
        params["starts-with[name]"] = name_filter

    try:
        res = await asyncio.wait_for(
            client.get(
                f"/lifecycle-manager/resources/{model_id}/instances",
                params=params
            ),
            timeout=30
        )
        return res.json()
    except asyncio.TimeoutError:
        await ctx.error(f"Timeout while retrieving resource instances for model {model_id}")
        raise
    except Exception as e:
        await ctx.error(f"Error retrieving resource instances for model {model_id}: {str(e)}")
        raise FastMCPError(f"Failed to retrieve resource instances for model {model_id}: {str(e)}")


async def get_resource_instance(
        ctx: Context, 
        model_id: str, 
        instance_id: str
        ) -> dict[str, Any]:
    """
    Retrieves the complete data and metadata for a specific resource instance in Itential Lifecycle Manager. A resource instance represents an individual deployment of a resource model (e.g., one specific router or firewall) and contains all its configured properties.

    Args:
        ctx (Context): The FastMCP context object.
        model_id (str): ID of the resource model
        instance_id (str): ID of the resource instance

    Returns:
        dict[str, Any]: Resource instance details

    Raises:
        FastMCPError: If there is an error retrieving the resource instance
        asyncio.TimeoutError: If the request times out
    """
    await ctx.info(f"inside get_resource_instance(...) for model_id: {model_id}, instance_id: {instance_id}")

    client = ctx.request_context.lifespan_context.get("client")

    try:
        res = await asyncio.wait_for(
            client.get(
                f"/lifecycle-manager/resources/{model_id}/instances/{instance_id}"
            ),
            timeout=30
        )
        return res.json()
    except asyncio.TimeoutError:
        await ctx.error(f"Timeout while retrieving resource instance {instance_id} for model {model_id}")
        raise
    except Exception as e:
        await ctx.error(f"Error retrieving resource instance {instance_id} for model {model_id}: {str(e)}")
        raise FastMCPError(f"Failed to retrieve resource instance {instance_id} for model {model_id}: {str(e)}")


async def get_action_executions(
    ctx: Context,
    limit: int = 25,
    skip: int = 0,
    sort: str = "startTime",
    order: int = -1,
    execution_types: list[str] | None = None
    ) -> dict[str, Any]:
    """
    Retrieves a list of all executions of actions performed on resource instances in Itential Lifecycle Manager. 
    Each action execution represents a recorded lifecycle event (e.g., create, update, delete) and includes execution details, status, timestamps, and outputs.

    Args:
        ctx (Context): The FastMCP context object.
        limit (int): Maximum number of records to return
        skip (int): Number of records to skip
        sort (str): Field to sort by
        order (int): Sort order (1 for ascending, -1 for descending)
        execution_types (list[str] | None): Optional filter by execution types

    Returns:
        dict[str, Any]: Dictionary containing action executions and metadata

    Raises:
        FastMCPError: If there is an error retrieving the action executions
        asyncio.TimeoutError: If the request times out
    """
    await ctx.info("inside get_action_executions(...)")

    client = ctx.request_context.lifespan_context.get("client")

    params = {
        "limit": limit,
        "skip": skip,
        "sort": sort,
        "order": order
    }

    if execution_types:
        params["in[executionType]"] = ",".join(execution_types)

    try:
        res = await asyncio.wait_for(
            client.get("/lifecycle-manager/action-executions", params=params),
            timeout=30
        )
        return res.json()
    except asyncio.TimeoutError:
        await ctx.error("Timeout while retrieving action executions")
        raise
    except Exception as e:
        await ctx.error(f"Error retrieving action executions: {str(e)}")
        raise FastMCPError(f"Failed to retrieve action executions: {str(e)}")