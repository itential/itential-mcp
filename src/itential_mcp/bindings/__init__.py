# Copyright (c) 2025 Itential, Inc
# GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)

import os
import importlib

from types import ModuleType
from typing import Tuple, Callable, Mapping, Any

from fastmcp.utilities.logging import get_logger

from .. import config
from .. import client


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
        module_name,
        os.path.join(path, f"{module_name}.py")
    )
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)

    return module


async def bind_to_tool(
    tool: config.Tool,
    platform_client: client.PlatformClient
) -> Tuple[Callable, Mapping[str, Any]]:
    """Bind a configuration tool to a callable function with metadata.

    Takes a tool configuration and platform client to create a bound function
    that can be registered with the MCP server. The function is dynamically
    created based on the tool type and includes appropriate tags and metadata.

    Args:
        tool (config.Tool): The tool configuration containing type, name, and other settings.
        platform_client (client.PlatformClient): The platform client for API communication.

    Returns:
        Tuple[Callable, Mapping[str, Any]]: A tuple containing the bound function and
            its registration kwargs including name, tags, and exclusions.

    Raises:
        AttributeError: If the tool type module doesn't have a 'new' function.
        KeyError: If the tool type is not found in globals.
    """
    logger.info(f"Adding dynamic binding for tool: {tool.name} (type={tool.type})")

    kwargs = {
        "name": tool.tool_name,
        "exclude_args": ("_tool_config",),
    }

    module = _import_binding(tool.type)

    f = getattr(module, "new")
    fn, description = await f(tool, platform_client)

    kwargs["description"] = description

    tags = f"bindings,{tool.tool_name}"

    if tool.tags is not None:
        tags = f"{tags},{tool.tags}"

    kwargs["tags"] = tags.split(",")

    return fn, kwargs


async def iterbindings(cfg: config.Config):
    """Iterate over tool bindings from configuration.

    Creates an async generator that yields bound tool functions and their
    registration metadata for each tool defined in the configuration. Each
    tool is bound using a shared platform client instance.

    Args:
        cfg (config.Config): The configuration object containing tool definitions.

    Yields:
        Tuple[Callable, Mapping[str, Any]]: Each iteration yields a tuple containing
            the bound function and its registration kwargs.

    Raises:
        AttributeError: If a tool type module doesn't have a 'new' function.
        KeyError: If a tool type is not found in globals.
    """
    platform_client = client.PlatformClient()
    for t in cfg.tools:
        yield await bind_to_tool(t, platform_client)
