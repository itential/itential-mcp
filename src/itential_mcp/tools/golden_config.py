# Copyright (c) 2025 Itential, Inc
# GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)

from typing import Annotated

from pydantic import Field

from fastmcp import Context

from itential_mcp import exceptions
from itential_mcp import errors

from itential_mcp.models.configuration_manager import (
    GetGoldenConfigTreesResponse,
    GoldenConfigTree,
    CreateGoldenConfigTreeResponse,
    AddGoldenConfigNodeResponse
)


__tags__ = ("configuration_manager",)


async def get_golden_config_trees(
    ctx: Annotated[Context, Field(
        description="The FastMCP Context object"
    )]
) -> GetGoldenConfigTreesResponse:
    """
    Get all Golden Configuration trees from Itential Platform.

    Golden Configuration trees are hierarchical templates that define
    configuration structures for network devices. They provide a framework
    for managing device configurations with variable substitution and
    version control capabilities.

    Args:
        ctx (Context): The FastMCP Context object

    Returns:
        GetGoldenConfigTreesResponse: List of Golden Configuration tree objects with the following fields:
            - name: Name of the Golden Configuration tree
            - device_type: The device type this tree is designed for
            - versions: List of available versions for this tree

    Raises:
        None: This function does not raise any exceptions
    """
    await ctx.info("inside get_golden_config_trees(...)")

    client = ctx.request_context.lifespan_context.get("client")

    res = await client.configuration_manager.get_golden_config_trees()

    results = []

    for ele in res:
        tree = GoldenConfigTree(
            name=ele["name"],
            device_type=ele["deviceType"],
            versions=ele["versions"]
        )
        results.append(tree)

    return GetGoldenConfigTreesResponse(root=results)


async def create_golden_config_tree(
    ctx: Annotated[Context, Field(
        description="The FastMCP Context object"
    )],
    name: Annotated[str, Field(
        description="The name of the Golden Configuration tree to create"
    )],
    device_type: Annotated[str, Field(
        description="The configuration device type associated with this tree"
    )],
    template: Annotated[str | None, Field(
        description="The configuration template associated with the base node",
        default=None
    )],
    variables: Annotated[dict | None, Field(
        description="The variables associated with this Golden Config tree",
        default=None
    )]
) -> CreateGoldenConfigTreeResponse:
    """
    Create a new Golden Configuration tree on Itential Platform.

    Golden Configuration trees define hierarchical configuration templates
    for network devices. They support variable substitution and version
    management to provide consistent, reusable configuration structures
    across device types.

    Args:
        ctx (Context): The FastMCP Context object
        name (str): Name of the Golden Configuration tree to create
        device_type (str): The configuration device type associated with this tree
        template (str | None): Optional configuration template for the base node
        variables (dict | None): Optional variables associated with this tree

    Returns:
        CreateGoldenConfigTreeResponse: Created Golden Configuration tree details with the following fields:
            - name: Name of the created Golden Configuration tree
            - device_type: The device type this tree is designed for

    Raises:
        ServerException: If there is an error creating the Golden Configuration tree
    """
    await ctx.info("inside create_golden_config_tree(...)")

    client = ctx.request_context.lifespan_context.get("client")

    try:
        res = await client.configuration_manager.create_golden_config_tree(
            name=name,
            device_type=device_type,
            template=template,
            variables=variables
        )
    except exceptions.ServerException as exc:
        return errors.internal_server_error(str(exc))

    return CreateGoldenConfigTreeResponse(
        name=res["name"],
        device_type=res["deviceType"]
    )


async def add_golden_config_node(
    ctx: Annotated[Context, Field(
        description="The FastMCP Context object"
    )],
    tree_name: Annotated[str, Field(
        description="The name of the Golden Configuration tree to create"
    )],
    name: Annotated[str, Field(
        description="The name of the new node to add"
    )],
    version: Annotated[str, Field(
        description="The version of the tree to add the node to",
        default="initial"
    )],
    path: Annotated[str, Field(
        description="The parent path",
        default="base"
    )],
    template: Annotated[str, Field(
        description="The configuration template associated with this node",
        default=None
    )]
) -> AddGoldenConfigNodeResponse:
    """
    Add a new node to an existing Golden Configuration tree.

    Nodes in Golden Configuration trees represent configuration sections
    or components that can be organized hierarchically. Each node can have
    an associated configuration template and belongs to a specific version
    of the tree structure.

    Args:
        ctx (Context): The FastMCP Context object
        tree_name (str): Name of the existing Golden Configuration tree
        name (str): Name of the new node to add
        version (str): Version of the tree to add the node to. Defaults to "initial"
        path (str): Parent path where the node should be added. Defaults to "base"
        template (str): Optional configuration template associated with this node

    Returns:
        AddGoldenConfigNodeResponse: Operation result with the following fields:
            - message: Success message confirming node addition

    Raises:
        ServerException: If there is an error adding the node to the Golden Configuration tree
    """
    await ctx.info("inside add_golden_config_node(...)")

    client = ctx.request_context.lifespan_context.get("client")

    kwargs = {
        "tree_name": tree_name,
        "name": name,
        "version": version
    }

    if path:
        kwargs["path"] = path

    if template:
        kwargs["template"] = template

    try:
        await client.configuration_manager.add_golden_config_node(
            name=name,
            tree_name=tree_name,
            version=version,
            path=path,
            template=template
        )
    except exceptions.ServerException as exc:
        return errors.internal_server_error(str(exc))

    return AddGoldenConfigNodeResponse(
        message=f"Successfully added node {name}"
    )
