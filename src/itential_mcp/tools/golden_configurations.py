# Copyright (c) 2025 Itential, Inc
# GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)

from typing import Annotated, Optional
from pydantic import Field
from fastmcp import Context
import re


async def get_allowed_device_os_types(
    ctx: Annotated[Context, Field(
        description="The FastMCP Context object"
    )]
) -> list:
    """
    Retrieve the list of allowed device OS types from the Itential Platform cache.

    Returns:
        list: The list of allowed OS types.
    """
    client = ctx.request_context.lifespan_context.get("client")
    res = await client.get("/configuration_manager/cache/devices/ostype")
    data = res.json()
    return data.get("osTypes", [])


async def create_golden_config_tree(
    ctx: Annotated[Context, Field(
        description="The FastMCP Context object"
    )],
    name: Annotated[str, Field(
        description="The name of the golden configuration tree to create"
    )],
    device_type: Annotated[str, Field(
        description="The device type for this configuration tree (e.g., cisco-ios, arista-eos)"
    )],
    version: Annotated[str, Field(
        description="The version label for the configuration tree (e.g., 'initial')",
        default="initial"
    )],
    variables: Annotated[Optional[dict], Field(
        description="Optional variables to set for this config tree/version",
        default=None
    )] = None
) -> dict:
    """
    Create a new golden configuration tree (root node) on the Itential Platform server.
    Validates the device_type against the allowed OS types.
    """
    allowed_os_types = await get_allowed_device_os_types(ctx)
    if device_type not in allowed_os_types:
        raise ValueError(f"Device type not found. These are the current ones that are available: {allowed_os_types}")

    await ctx.info(f"Creating golden configuration tree: {name}")
    client = ctx.request_context.lifespan_context.get("client")
    body = {
        "name": name,
        "deviceType": device_type,
        "versions": [version]
    }
    if variables is not None:
        body["variables"] = variables
    res = await client.post("/configuration_manager/configs", json=body)
    return res.json()


async def add_child_node(
    ctx: Annotated[Context, Field(
        description="The FastMCP Context object"
    )],
    config_id: Annotated[str, Field(
        description="The ID of the golden configuration tree"
    )],
    version: Annotated[str, Field(
        description="The version label (e.g., 'initial')"
    )],
    parent_path: Annotated[str, Field(
        description="The path to the parent node (e.g., 'base' or 'base/parent1')"
    )],
    name: Annotated[str, Field(
        description="The name of the new child node"
    )]
) -> dict:
    """
    Add a child node to a golden configuration tree at the specified parent path.

    Args:
        ctx (Context): The FastMCP Context object
        config_id (str): The ID of the configuration tree
        version (str): The version label
        parent_path (str): The path to the parent node (e.g., 'base', 'base/parent1')
        name (str): The name of the new child node

    Returns:
        dict: The created child node metadata
    """
    await ctx.info(f"Adding child node '{name}' to {parent_path} in config {config_id}")
    client = ctx.request_context.lifespan_context.get("client")
    url = f"/configuration_manager/configs/{config_id}/{version}/{parent_path}"
    body = {"name": name}
    res = await client.post(url, json=body)
    return res.json()


async def get_golden_config_tree(
    ctx: Annotated[Context, Field(
        description="The FastMCP Context object"
    )],
    config_id: Annotated[str, Field(
        description="The ID of the golden configuration tree"
    )],
    version: Annotated[str, Field(
        description="The version label (e.g., 'initial')"
    )]
) -> dict:
    """
    Retrieve the full golden configuration tree structure for a given config ID and version.

    Args:
        ctx (Context): The FastMCP Context object
        config_id (str): The ID of the configuration tree
        version (str): The version label

    Returns:
        dict: The configuration tree structure
    """
    await ctx.info(f"Retrieving golden configuration tree {config_id} version {version}")
    client = ctx.request_context.lifespan_context.get("client")
    url = f"/configuration_manager/configs/{config_id}/{version}"
    res = await client.get(url)
    return res.json()


def extract_jinja2_variables(template: str) -> set:
    """
    Extract Jinja2-style variables from a template string.
    Returns a set of variable names.
    """
    return set(re.findall(r'{{\s*([\w\.]+)', template))


async def set_node_template(
    ctx: Annotated[Context, Field(
        description="The FastMCP Context object"
    )],
    spec_id: Annotated[str, Field(
        description="The config spec/template ID for the node"
    )],
    template: Annotated[str, Field(
        description="The configuration template string (Jinja2 or raw config)"
    )],
    config_id: Annotated[str, Field(
        description="The ID of the golden configuration tree this node belongs to"
    )],
    version: Annotated[str, Field(
        description="The version label (e.g., 'initial')"
    )],
    variables: Annotated[Optional[dict], Field(
        description="Optional variables for the template",
        default=None
    )] = None
) -> dict:
    """
    Set or update the configuration template for a specific node in the golden configuration tree.
    Ensures all variables referenced in the template are present in the tree's variables dict (defaulting to empty string if missing).

    Args:
        ctx (Context): The FastMCP Context object
        spec_id (str): The config spec/template ID for the node
        template (str): The configuration template string
        config_id (str): The ID of the golden configuration tree
        version (str): The version label
        variables (dict, optional): Variables for the template

    Returns:
        dict: The updated template metadata
    """
    await ctx.info(f"Setting template for spec {spec_id} and ensuring variables are present in tree")
    client = ctx.request_context.lifespan_context.get("client")

    # Step 1: Extract variables from the template
    referenced_vars = extract_jinja2_variables(template)

    # Step 2: Get current tree variables
    url_tree = f"/configuration_manager/configs/{config_id}/{version}"
    res_tree = await client.get(url_tree)
    tree = res_tree.json()
    tree_vars = tree.get("variables", {})

    # Step 3: Add any missing variables (default to empty string)
    updated = False
    for var in referenced_vars:
        if var not in tree_vars:
            tree_vars[var] = ""
            updated = True

    # Step 4: Update the tree's variables if needed
    if updated:
        url_update = f"/configuration_manager/configs/{config_id}/{version}"
        body_update = {"name": version, "variables": tree_vars}
        await client.put(url_update, json=body_update)

    # Step 5: Set the node template as before
    body = {"data": {"template": template, "variables": variables or {}}}
    url = f"/configuration_manager/config_specs/{spec_id}"
    res = await client.put(url, json=body)
    return res.json()


async def update_golden_config_variables(
    ctx: Annotated[Context, Field(
        description="The FastMCP Context object"
    )],
    config_id: Annotated[str, Field(
        description="The ID of the golden configuration tree"
    )],
    version: Annotated[str, Field(
        description="The version label (e.g., 'initial')"
    )],
    variables: Annotated[dict, Field(
        description="The variables to set for this config tree/version"
    )]
) -> dict:
    """
    Update the variables for a golden configuration tree version.

    Args:
        ctx (Context): The FastMCP Context object
        config_id (str): The ID of the configuration tree
        version (str): The version label
        variables (dict): The variables to set

    Returns:
        dict: The updated configuration tree metadata
    """
    await ctx.info(f"Updating variables for config {config_id} version {version}")
    client = ctx.request_context.lifespan_context.get("client")
    url = f"/configuration_manager/configs/{config_id}/{version}"
    body = {
        "name": version,
        "variables": variables
    }
    res = await client.put(url, json=body)
    return res.json() 