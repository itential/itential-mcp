# Copyright (c) 2025 Itential, Inc
# GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from typing import Annotated

from pydantic import Field

from fastmcp import Context

from itential_mcp.models import inventory_manager as models


__tags__ = ("inventory_manager",)


async def get_inventories(
    ctx: Annotated[Context, Field(description="The FastMCP Context object")],
) -> models.GetInventoriesResponse:
    """
    Get all inventories from Itential Platform.

    Inventories are collections of network devices organized for bulk
    configuration management, compliance checking, and automation tasks.
    They provide an organizational structure for grouping devices by
    function, location, or type.

    Args:
        ctx (Context): The FastMCP Context object

    Returns:
        GetInventoriesResponse: List of inventory objects with the following fields:
            - id: Unique identifier for the inventory
            - name: Inventory name
            - description: Inventory description
            - nodeCount: Number of nodes (devices) in the inventory

    Raises:
        Exception: If there is an error retrieving inventories from the platform
    """
    await ctx.info("inside get_inventories(...)")

    client = ctx.request_context.lifespan_context.get("client")

    data = await client.inventory_manager.get_inventories()

    return models.GetInventoriesResponse(
        [models.InventoryElement(**ele) for ele in data]
    )


async def describe_inventory(
    ctx: Annotated[Context, Field(description="The FastMCP Context object")],
    name: Annotated[
        str,
        Field(description="The name of the inventory to describe"),
    ],
) -> models.DescribeInventoryResponse:
    """
    Get detailed information about a specific inventory from Itential Platform.

    Retrieves comprehensive details about an inventory including its
    description, groups, actions, tags, and the list of nodes (devices)
    with their attributes. The inventory is identified by its name.

    Args:
        ctx (Context): The FastMCP Context object
        name (str): Name of the inventory to describe. Use `get_inventories`
            to see available inventories.

    Returns:
        DescribeInventoryResponse: Inventory details with the following fields:
            - id: Unique identifier for the inventory
            - name: Inventory name
            - description: Inventory description
            - groups: List of authorization group names associated with the inventory
            - actions: List of actions configured for the inventory
            - tags: Tags associated with the inventory
            - nodes: List of node objects with name, attributes, and tags

    Raises:
        NotFoundError: If the specified inventory name cannot be found
    """
    await ctx.info("inside describe_inventory(...)")

    client = ctx.request_context.lifespan_context.get("client")

    data = await client.inventory_manager.describe_inventory(name)

    return models.DescribeInventoryResponse(**data)


async def create_inventory(
    ctx: Annotated[Context, Field(description="The FastMCP Context object")],
    name: Annotated[
        str,
        Field(description="The name of the inventory to create"),
    ],
    groups: Annotated[
        list[str],
        Field(
            description="List of authorization group names to assign to the inventory. At least one group is required.",
        ),
    ],
    description: Annotated[
        str | None,
        Field(
            description="Short description of the inventory",
            default=None,
        ),
    ],
    devices: Annotated[
        list[str] | None,
        Field(
            description="List of device names to include in the inventory. Use `get_devices` to see available devices.",
            default=None,
        ),
    ],
) -> models.CreateInventoryResponse:
    """
    Create a new inventory and optionally populate it with devices on Itential Platform.

    Inventories enable logical organization of network devices for streamlined
    management, configuration deployment, compliance checking, and automation
    workflows. Devices can be added during creation or later.

    Args:
        ctx (Context): The FastMCP Context object
        name (str): Name of the inventory to create
        groups (list[str]): List of authorization group names to assign
            to the inventory. At least one group is required.
        description (str | None): Short description of the inventory (optional)
        devices (list[str] | None): List of device names to include in the
            inventory. Use `get_devices` to see available devices. (optional)

    Returns:
        CreateInventoryResponse: Creation operation result with the following fields:
            - id: Unique identifier for the created inventory
            - name: Name of the inventory
            - message: Status message describing the create operation

    Raises:
        ValueError: If an inventory with the same name already exists
    """
    await ctx.info("inside create_inventory(...)")

    client = ctx.request_context.lifespan_context.get("client")

    res = await client.inventory_manager.create_inventory(
        name, groups, description=description, devices=devices
    )

    return models.CreateInventoryResponse(**res)


async def add_nodes_to_inventory(
    ctx: Annotated[Context, Field(description="The FastMCP Context object")],
    inventory_name: Annotated[
        str,
        Field(
            description="The name of the inventory to add nodes to. Use `get_inventories` to see available inventories.",
        ),
    ],
    nodes: Annotated[
        list[dict],
        Field(
            description=(
                "List of node objects to add to the inventory. Each node must "
                "include 'name' (str) and 'attributes' (dict with keys like "
                "itential_host, itential_platform, cluster_id, itential_user, "
                "itential_password). Optionally include 'tags' (list of strings)."
            ),
        ),
    ],
) -> models.AddNodesToInventoryResponse:
    """
    Add nodes in bulk to an existing inventory on Itential Platform.

    Adds one or more nodes with full attribute details to an inventory. Each
    node requires a name and attributes dictionary containing connection and
    platform details. Tags can be optionally provided per node for classification.

    Args:
        ctx (Context): The FastMCP Context object

        inventory_name (str): The name of the inventory to add nodes to.
            Use `get_inventories` to see available inventories.

        nodes (list[dict]): List of node objects to add. Each node must include:
            - name (str): The node name (required)
            - attributes (dict): Node attributes such as itential_host,
                itential_platform, cluster_id, itential_user,
                itential_password (required)
            - tags (list[str]): Optional list of tags for the node

    Returns:
        AddNodesToInventoryResponse: An object representing the status of the
            operation with the following fields:
            - status: Message that provides the status of the operation
            - message: Short description of the status of the operation

    Raises:
        NotFoundError: If the specified inventory name cannot be found
        Exception: If there is an error adding nodes to the inventory
    """
    await ctx.info("inside add_nodes_to_inventory(...)")

    client = ctx.request_context.lifespan_context.get("client")

    data = await client.inventory_manager.add_nodes_to_inventory(inventory_name, nodes)

    return models.AddNodesToInventoryResponse(
        status=data.get("status", "Success"),
        message=data.get("message", "Nodes added successfully"),
    )


async def delete_inventory(
    ctx: Annotated[Context, Field(description="The FastMCP Context object")],
    name: Annotated[
        str,
        Field(description="The name of the inventory to delete"),
    ],
) -> models.DeleteInventoryResponse:
    """
    Delete an inventory from Itential Platform.

    Permanently removes an inventory and all its device associations.
    The devices themselves are not affected; only the inventory grouping
    is deleted. This operation cannot be undone.

    Args:
        ctx (Context): The FastMCP Context object
        name (str): Name of the inventory to delete. Use `get_inventories`
            to see available inventories.

    Returns:
        DeleteInventoryResponse: Deletion result with the following fields:
            - status: Status of the delete operation
            - message: Short description of the status of the operation

    Raises:
        NotFoundError: If the specified inventory name cannot be found
    """
    await ctx.info("inside delete_inventory(...)")

    client = ctx.request_context.lifespan_context.get("client")

    data = await client.inventory_manager.delete_inventory(name)

    return models.DeleteInventoryResponse(**data)
