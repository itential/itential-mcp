# Copyright (c) 2025 Itential, Inc
# GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

import os
import importlib

from types import ModuleType
from typing import Tuple, Callable, Mapping, Any

from fastmcp.utilities.logging import get_logger

from .. import config
from ..platform import PlatformClient


logger = get_logger(__name__)


def _import_binding(module_name: str) -> ModuleType:
    """Dynamically import a binding module by name.

    Imports a Python module from the current directory using importlib utilities.
    This function creates a module spec from the file location and executes it
    to return the loaded module object.

    Args:
        module_name (str): The name of the module to import (without .py extension).

    Returns:
        ModuleType: The imported module object containing binding functions and classes.

    Raises:
        ImportError: If the module file cannot be found or loaded.
        AttributeError: If the module spec cannot be created from the file location.
    """
    path = os.path.dirname(os.path.realpath(__file__))

    spec = importlib.util.spec_from_file_location(
        module_name, os.path.join(path, f"{module_name}.py")
    )
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)

    return module


async def bind_to_tool(
    tool: config.Tool, platform_client: PlatformClient
) -> Tuple[Callable, Mapping[str, Any]]:
    """Bind a configuration tool to a callable function with metadata.

    This function implements the core of the dynamic tool binding system. It takes
    a tool configuration (defined via config file or environment variables) and
    creates a callable function that can be registered as an MCP tool.

    **Binding Process:**
    1. Import the appropriate binding module based on tool type (endpoint, service)
    2. Call the module's 'new' function to create the bound callable
    3. Construct registration metadata (name, tags, description)
    4. Return the bound function ready for MCP registration

    **Tool Types:**
    - "endpoint": Binds to Itential Platform workflow endpoints
    - "service": Binds to Gateway Manager external services

    **Tag Construction:**
    Tags are built hierarchically:
    - Base: "bindings" (marks all dynamic tools)
    - Tool name: Added automatically
    - Custom tags: From tool.tags config field
    Example: "bindings,my_tool,network,automation"

    Args:
        tool (config.Tool): The tool configuration containing:
            - type: "endpoint" or "service" (determines binding module)
            - name: The asset name in Itential Platform
            - tool_name: The MCP tool name to expose
            - tags: Optional comma-separated custom tags
        platform_client (PlatformClient): The platform client for API communication,
            passed to the binding module for runtime API calls.

    Returns:
        Tuple[Callable, Mapping[str, Any]]: A tuple containing:
            - Callable: The bound function ready for MCP registration
            - Mapping[str, Any]: Registration kwargs with:
                - name: Tool name exposed to MCP clients
                - description: Tool description from binding module
                - tags: Complete list of tags for filtering
                - exclude_args: Arguments to hide from MCP schema

    Raises:
        AttributeError: If the tool type module doesn't have a 'new' function.
        ImportError: If the binding module for the tool type cannot be loaded.
    """
    logger.info(f"Adding dynamic binding for tool: {tool.name} (type={tool.type})")

    # Step 1: Prepare base registration kwargs
    # exclude_args hides internal parameters from the MCP tool schema
    kwargs = {
        "name": tool.tool_name,
        "exclude_args": ("_tool_config",),
    }

    # Step 2: Import the appropriate binding module for this tool type
    # This dynamically loads bindings/endpoint.py or bindings/service.py
    module = _import_binding(tool.type)

    # Step 3: Call the binding module's 'new' function to create the bound callable
    # Each binding module implements: async def new(tool, client) -> (fn, description)
    f = getattr(module, "new")
    fn, description = await f(tool, platform_client)

    # Step 4: Add the description returned by the binding module
    kwargs["description"] = description

    # Step 5: Build complete tag hierarchy
    # Start with "bindings" to mark all dynamically bound tools
    tags = f"bindings,{tool.tool_name}"

    # Add any custom tags from the configuration
    if tool.tags is not None:
        tags = f"{tags},{tool.tags}"

    # Convert comma-separated string to list for FastMCP
    kwargs["tags"] = tags.split(",")

    return fn, kwargs


async def iterbindings(cfg: config.Config):
    """Iterate over tool bindings from configuration.

    Creates an async generator that yields bound tool functions and their
    registration metadata for each tool defined in the configuration. Each
    tool is bound using a shared platform client instance that is properly
    cleaned up via async context manager.

    Args:
        cfg (config.Config): The configuration object containing tool definitions.

    Yields:
        Tuple[Callable, Mapping[str, Any]]: Each iteration yields a tuple containing
            the bound function and its registration kwargs.

    Raises:
        AttributeError: If a tool type module doesn't have a 'new' function.
        KeyError: If a tool type is not found in globals.
    """
    # Use context manager to ensure proper cleanup of platform client connections
    async with PlatformClient() as platform_client:
        for t in cfg.tools:
            yield await bind_to_tool(t, platform_client)
