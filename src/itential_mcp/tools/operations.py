# Copyright (c) 2025 Itential, Inc
# GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)
"""
Operations module for interacting with Itential's Operations Manager APIs.
This module includes async functions to retrieve automations, triggers, forms,
and related metadata from Itential's Operations Manager application using
FastMCP context and schema.
"""
from typing import Any

from fastmcp import Context
import asyncio
from fastmcp.exceptions import FastMCPError

# Constants
DEFAULT_LIMIT = 25
MAX_LIMIT = 100


async def get_automations_operations_manager(
    ctx: Context,
    limit: int = DEFAULT_LIMIT,
    skip: int = 0,
    sort: str = "name",
    order: int = 1,
    component_type: str | None = None,
    equals_field: str | None = None,
    equals: str | None = None,
) -> dict[str, Any]:
    """
    Retrieve a list of automations which might sometime be referred to as a service from the Operations Manager with optional filtering and pagination.

    This function is used to fetch automations that define triggering logic of workflows, compliance plan, lifecycle manager actions from within the system.
    It supports filtering by component type or other fields using equals[] filtering, sorting, and pagination, enabling dynamic interaction with automation configurations.
    The function calls the /operations-manager/automations endpoint and supports additional filter types such as equals[].

    Args:
        ctx (Context): The FastMCP Context object
        limit (int): Maximum number of automations to return per page
        skip (int): Number of automations to skip
        sort (str): Field to sort by
        order (int): Sort order (1 for ascending, -1 for descending)
        component_type (str | None): Filter by component type (e.g., "workflows")
        equals_field (str | None): Field to filter using equals[...] logic.
        equals (str | None): Value to match exactly.

    Returns:
        dict[str, Any]:
            - data (list[dict]): List of automation objects
            - metadata (dict): Pagination metadata
            - message (str): Status message

    Raises:
        FastMCPError: If there is an error retrieving the automations
        asyncio.TimeoutError: If the request times out
        ValueError: If parameters are invalid
    """
    if not isinstance(limit, int) or limit < 1 or limit > MAX_LIMIT:
        raise ValueError(f"Limit must be between 1 and {MAX_LIMIT}")

    if not isinstance(skip, int) or skip < 0:
        raise ValueError("Skip must be a non-negative integer")

    await ctx.info("Retrieving automations")

    client = ctx.request_context.lifespan_context.get("client")
    if not client:
        raise FastMCPError("No client connection available")

    params = {
        "limit": limit, 
        "skip": skip, 
        "sort": sort, 
        "order": order
        }

    if component_type:
        params["equals[componentType]"] = component_type
    if equals_field and equals:
        params[f"equals[{equals_field}]"] = equals

    try:
        res = await asyncio.wait_for(
            client.get("/operations-manager/automations", params=params), 
            timeout=30,
        )
        return res.json()
    except asyncio.TimeoutError:
        await ctx.error("Timeout while retrieving automations")
        raise
    except Exception as e:
        await ctx.error(f"Error retrieving automations: {str(e)}")
        raise FastMCPError(f"Failed to retrieve automations: {str(e)}")


async def get_automation_details(ctx: Context, automation_id: str) -> dict[str, Any]:
    """
    Retrieve full metadata and detailed information about a specific automation by ID.

    This function provides comprehensive details such as creation info, component metadata,
    and update history, which are useful for auditing, visualization, orchestration,
    and managing automation lifecycle.

    Typical use cases include displaying automation details in admin consoles,
    tracking changes, or integrating automation metadata into other systems.

    Args:
        ctx (Context): The FastMCP Context object
        automation_id (str): The ID of the automation

    Returns:
        dict[str, Any]:
            - _id (str): Automation ID
            - name (str): Automation name
            - description (str): Automation description
            - componentName (str): Component name
            - componentType (str): Component type
            - componentId (str): Component ID
            - created (str): Creation timestamp
            - createdBy (str): Creator information
            - lastUpdated (str): Last update timestamp
            - lastUpdatedBy (str): Last updater information

    Raises:
        FastMCPError: If there is an error retrieving the automation details
        asyncio.TimeoutError: If the request times out
    """
    await ctx.info(f"Retrieving details for automation {automation_id}")

    client = ctx.request_context.lifespan_context.get("client")
    if not client:
        raise FastMCPError("No client connection available")

    try:
        res = await asyncio.wait_for(
            client.get(f"/operations-manager/automations/{automation_id}"), timeout=30
        )
        return res.json()
    except asyncio.TimeoutError:
        await ctx.error(
            f"Timeout while retrieving automation details for {automation_id}"
        )
        raise
    except Exception as e:
        await ctx.error(
            f"Error retrieving automation details for {automation_id}: {str(e)}"
        )
        raise FastMCPError(
            f"Failed to retrieve automation details for {automation_id}: {str(e)}"
        )


async def get_automation_triggers(
    ctx: Context,
    automation_id: str,
    limit: int = DEFAULT_LIMIT,
    skip: int = 0,
    sort: str = "name",
    order: int = 1,
    trigger_type: str | None = None,
    enabled: bool | None = None,
    equals_field: str | None = None,
    equals: str | None = None,
) -> dict[str, Any]:
    """
    Retrieve triggers associated with a specific automation from the Operations Manager service.

    This function calls the `/operations-manager/triggers` endpoint to return all configured triggers related to a specific automation (via `actionId`).
    It supports advanced filtering such as `equals[field]` and optional filters on trigger type, enablement status, and pagination metadata.

    This is useful for clients needing to dynamically discover what kinds of events (manual, webhook, etc.) can initiate automation flows,
    as well as for UI layers that surface trigger configurations or perform administrative actions.

    Args:
        ctx (Context): The FastMCP Context object.
        automation_id (str): The ID of the automation (sent as `actionId`).
        limit (int): Maximum number of triggers to return per page.
        skip (int): Number of triggers to skip.
        sort (str): Field to sort by.
        order (int): Sort order (1 for ascending, -1 for descending).
        trigger_type (str | None): Optional filter for trigger type (e.g., "manual", "endpoint").
        enabled (bool | None): Optional filter by trigger enablement state.
        equals_field (str | None): Field to filter using equals[field]=value logic.
        equals (str | None): Value to match exactly for the specified field.

    Returns:
        dict[str, Any]:
            - data (list[dict]): List of trigger objects.
            - metadata (dict): Pagination metadata.
            - message (str): Status message.

    Raises:
        FastMCPError: If there is an error retrieving the triggers.
        asyncio.TimeoutError: If the request times out.
        ValueError: If input parameters are invalid.
    """
    if not isinstance(limit, int) or limit < 1 or limit > MAX_LIMIT:
        raise ValueError(f"Limit must be between 1 and {MAX_LIMIT}")

    if not isinstance(skip, int) or skip < 0:
        raise ValueError("Skip must be a non-negative integer")

    await ctx.info(f"Retrieving triggers for automation {automation_id}")

    client = ctx.request_context.lifespan_context.get("client")
    if not client:
        raise FastMCPError("No client connection available")

    params = {
        "actionId": automation_id,
        "limit": limit,
        "skip": skip,
        "sort": sort,
        "order": order,
    }

    if trigger_type:
        params["equals[type]"] = trigger_type
    if equals_field and equals:
        params[f"equals[{equals_field}]"] = equals

    if enabled is not None:
        params["enabled"] = str(enabled).lower()

    try:
        res = await asyncio.wait_for(
            client.get("/operations-manager/triggers", params=params), timeout=30
        )
        return res.json()
    except asyncio.TimeoutError:
        await ctx.error(
            f"Timeout while retrieving triggers for automation {automation_id}"
        )
        raise
    except Exception as e:
        await ctx.error(
            f"Error retrieving triggers for automation {automation_id}: {str(e)}"
        )
        raise FastMCPError(
            f"Failed to retrieve triggers for automation {automation_id}: {str(e)}"
        )


async def get_trigger_details(ctx: Context, trigger_id: str) -> dict[str, Any]:
    """
    Retrieve detailed information about a specific trigger by its ID.

    This function calls the /operations-manager/triggers/:id endpoint to fetch
    the configuration and metadata of a single trigger, such as its type, status,
    associated automation, and other properties.

    Args:
        ctx (Context): The FastMCP Context object
        trigger_id (str): The ID of the trigger

    Returns:
        dict[str, Any]: A dictionary containing:
            - data (dict): Trigger details
            - metadata (dict): Additional metadata
            - message (str): Status message

    Raises:
        FastMCPError: If there is an error retrieving the trigger details
        asyncio.TimeoutError: If the request times out
    """
    await ctx.info(f"Retrieving details for trigger {trigger_id}")

    client = ctx.request_context.lifespan_context.get("client")
    if not client:
        raise FastMCPError("No client connection available")

    try:
        res = await asyncio.wait_for(
            client.get(f"/operations-manager/triggers/{trigger_id}"), timeout=30
        )
        return res.json()
    except asyncio.TimeoutError:
        await ctx.error(f"Timeout while retrieving trigger details for {trigger_id}")
        raise
    except Exception as e:
        await ctx.error(f"Error retrieving trigger details for {trigger_id}: {str(e)}")
        raise FastMCPError(
            f"Failed to retrieve trigger details for {trigger_id}: {str(e)}"
        )


async def get_form_details(ctx: Context, form_id: str) -> dict[str, Any]:
    """
    Load detailed information about a specific form including its structure and schemas.

    This function retrieves the form's JSON schema, UI schema, version, and namespace information,
    which are essential for dynamically generating user interfaces and validating user input.
    Typical use cases include rendering dynamic forms in web applications, validating form data,
    and managing form versions and metadata.

    Args:
        ctx (Context): The FastMCP Context object
        form_id (str): The ID of the form

    Returns:
        dict[str, Any]:
            - id (str): Form ID
            - name (str): Form name
            - description (str): Form description
            - struct (dict): Form structure
            - schema (dict): JSON schema
            - uiSchema (dict): UI schema
            - version (str): Form version
            - namespace (dict): Form namespace information

    Raises:
        FastMCPError: If there is an error retrieving the form details
        asyncio.TimeoutError: If the request times out
    """
    await ctx.info(f"Retrieving details for form {form_id}")

    client = ctx.request_context.lifespan_context.get("client")
    if not client:
        raise FastMCPError("No client connection available")

    try:
        res = await asyncio.wait_for(
            client.get(f"/json-forms/forms/{form_id}"), timeout=30
        )
        return res.json()
    except asyncio.TimeoutError:
        await ctx.error(f"Timeout while retrieving form details for {form_id}")
        raise
    except Exception as e:
        await ctx.error(f"Error retrieving form details for {form_id}: {str(e)}")
        raise FastMCPError(f"Failed to retrieve form details for {form_id}: {str(e)}")
