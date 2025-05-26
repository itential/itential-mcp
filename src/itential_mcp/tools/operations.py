# Copyright (c) 2025 Itential, Inc
# GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)

from fastmcp import Context
from typing import Optional, Dict, List, Any
import asyncio
from fastmcp.exceptions import FastMCPError

# Constants
DEFAULT_LIMIT = 25
MAX_LIMIT = 100


async def get_automations(
    ctx: Context,
    limit: int = DEFAULT_LIMIT,
    skip: int = 0,
    sort: str = "name",
    order: int = 1,
    component_type: Optional[str] = None,
    equals_field: Optional[str] = None,
    equals: Optional[str] = None
) -> Dict[str, Any]:
    """
    Get list of automations with optional filtering

    Args:
        ctx (Context): The FastMCP Context object
        limit (int): Maximum number of automations to return per page
        skip (int): Number of automations to skip
        sort (str): Field to sort by
        order (int): Sort order (1 for ascending, -1 for descending)
        component_type (Optional[str]): Filter by component type (e.g., "workflows")
        equals_field (Optional[str]): Field to apply equals filter on
        equals (Optional[str]): Value to match for equals filter

    Returns:
        Dict[str, Any]: A dictionary containing:
            - data (List[Dict]): List of automation objects
            - metadata (Dict): Pagination metadata
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
        params["equalsField"] = "componentType"
        params["equals"] = component_type
    elif equals_field and equals:
        params["equalsField"] = equals_field
        params["equals"] = equals

    try:
        res = await asyncio.wait_for(
            client.get("/operations-manager/automations", params=params),
            timeout=30
        )
        return res.json()
    except asyncio.TimeoutError:
        await ctx.error("Timeout while retrieving automations")
        raise
    except Exception as e:
        await ctx.error(f"Error retrieving automations: {str(e)}")
        raise FastMCPError(f"Failed to retrieve automations: {str(e)}")

async def get_automation_triggers(
    ctx: Context,
    automation_id: str,
    limit: int = DEFAULT_LIMIT,
    skip: int = 0,
    sort: str = "name",
    order: int = 1,
    trigger_type: Optional[str] = None,
    enabled: Optional[bool] = None,
    equals_field: Optional[str] = None,
    equals: Optional[str] = None
) -> Dict[str, Any]:
    """
    Get triggers for a specific automation

    Args:
        ctx (Context): The FastMCP Context object
        automation_id (str): The ID of the automation
        limit (int): Maximum number of triggers to return per page
        skip (int): Number of triggers to skip
        sort (str): Field to sort by
        order (int): Sort order (1 for ascending, -1 for descending)
        trigger_type (Optional[str]): Filter by trigger type (e.g., "manual", "endpoint")
        enabled (Optional[bool]): Filter by enabled status
        equals_field (Optional[str]): Field to apply equals filter on
        equals (Optional[str]): Value to match for equals filter

    Returns:
        Dict[str, Any]: A dictionary containing:
            - data (List[Dict]): List of trigger objects
            - metadata (Dict): Pagination metadata
            - message (str): Status message

    Raises:
        FastMCPError: If there is an error retrieving the triggers
        asyncio.TimeoutError: If the request times out
        ValueError: If parameters are invalid
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
        "order": order
    }

    if trigger_type:
        params["equalsField"] = "type"
        params["equals"] = trigger_type
    elif equals_field and equals:
        params["equalsField"] = equals_field
        params["equals"] = equals

    if enabled is not None:
        params["enabled"] = str(enabled).lower()

    try:
        res = await asyncio.wait_for(
            client.get("/operations-manager/triggers", params=params),
            timeout=30
        )
        return res.json()
    except asyncio.TimeoutError:
        await ctx.error(f"Timeout while retrieving triggers for automation {automation_id}")
        raise
    except Exception as e:
        await ctx.error(f"Error retrieving triggers for automation {automation_id}: {str(e)}")
        raise FastMCPError(f"Failed to retrieve triggers for automation {automation_id}: {str(e)}")

async def get_trigger_details(
    ctx: Context,
    trigger_id: str
) -> Dict[str, Any]:
    """
    Get detailed information about a specific trigger

    Args:
        ctx (Context): The FastMCP Context object
        trigger_id (str): The ID of the trigger

    Returns:
        Dict[str, Any]: A dictionary containing:
            - data (Dict): Trigger details
            - metadata (Dict): Additional metadata
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
            client.get(f"/operations-manager/triggers/{trigger_id}"),
            timeout=30
        )
        return res.json()
    except asyncio.TimeoutError:
        await ctx.error(f"Timeout while retrieving trigger details for {trigger_id}")
        raise
    except Exception as e:
        await ctx.error(f"Error retrieving trigger details for {trigger_id}: {str(e)}")
        raise FastMCPError(f"Failed to retrieve trigger details for {trigger_id}: {str(e)}")

async def get_form_details(
    ctx: Context,
    form_id: str
) -> Dict[str, Any]:
    """
    Get detailed information about a specific form

    Args:
        ctx (Context): The FastMCP Context object
        form_id (str): The ID of the form

    Returns:
        Dict[str, Any]: A dictionary containing form details including:
            - id (str): Form ID
            - name (str): Form name
            - description (str): Form description
            - struct (Dict): Form structure
            - schema (Dict): JSON schema
            - uiSchema (Dict): UI schema
            - version (str): Form version
            - namespace (Dict): Form namespace information

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
            client.get(f"/json-forms/forms/{form_id}"),
            timeout=30
        )
        return res.json()
    except asyncio.TimeoutError:
        await ctx.error(f"Timeout while retrieving form details for {form_id}")
        raise
    except Exception as e:
        await ctx.error(f"Error retrieving form details for {form_id}: {str(e)}")
        raise FastMCPError(f"Failed to retrieve form details for {form_id}: {str(e)}")

async def get_automation_details(
    ctx: Context,
    automation_id: str
) -> Dict[str, Any]:
    """
    Get detailed information about a specific automation

    Args:
        ctx (Context): The FastMCP Context object
        automation_id (str): The ID of the automation

    Returns:
        Dict[str, Any]: A dictionary containing automation details including:
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
            client.get(f"/operations-manager/automations/{automation_id}"),
            timeout=30
        )
        return res.json()
    except asyncio.TimeoutError:
        await ctx.error(f"Timeout while retrieving automation details for {automation_id}")
        raise
    except Exception as e:
        await ctx.error(f"Error retrieving automation details for {automation_id}: {str(e)}")
        raise FastMCPError(f"Failed to retrieve automation details for {automation_id}: {str(e)}") 