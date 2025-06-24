# Copyright (c) 2025 Itential, Inc
# GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)

import os
import sys
import inspect
import importlib.util

from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager, AsyncExitStack

from typing import Any

from fastmcp import FastMCP

from . import client
from . import config
from . import cache


@asynccontextmanager
async def lifespan(mcp: FastMCP) -> AsyncGenerator[dict[str | Any], None]:
    """
    Manage the lifespan of Itential Platform servers

    This function is responsible for creating the client connection to
    Itential Platform and yielding it to FastMCP to be included in the
    context.

    Args:
        mcp (FastMCP): An instance of FastMCP

    Returns:
        AsyncGenerator: Yields an AsyncGenerator with a dict object

    Raises:
        None
    """
    async with AsyncExitStack():
        yield {
            "client": client.PlatformClient(),
            "cache": cache.Cache()
        }


def register_tools(mcp: FastMCP) -> None:
    """
    Register all functions in the tools folder with mcp

    This function will recursively load all modules found in the `tools`
    folder as long as they module name does not start with underscore (_).  It
    will then inspect the module to find all public functions and attach
    them to the instance of mcp as a tool.

    Args:
        mcp (FastMCP): An instance of FastMCP to attach tools to

    Returns:
        None

    Raises:
        None
    """
    path = os.path.join(os.path.dirname(os.path.realpath(__file__)), "tools")

    # Get a list of all files in the directory
    module_files = [f[:-3] for f in os.listdir(path) if f.endswith(".py") and f != "__init__.py"]

    # Import the modules, add them to globals and mcp
    for module_name in module_files:
        if not module_name.startswith("_"):
            spec = importlib.util.spec_from_file_location(module_name, os.path.join(path, f"{module_name}.py"))
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)

            # Inspect the module to retreive all of the functions.
            for name, f in inspect.getmembers(module, inspect.isfunction):
                if not name.startswith("_") and f.__module__ == module_name:
                    kwargs = {"tags": {name}}
                    if hasattr(f, "tags"):
                        tags = kwargs["tags"]
                        for ele in f.tags:
                            tags.add(ele)
                        kwargs["tags"] = tags
                    mcp.tool(f, **kwargs)


async def run() -> int:
    """
    Run the MCP server

    This is the server entry point for running the Itential MCP server using
    either stdio or sse.  This function will load the configuration, create
    the MCP server, register all tools and start the server.

    Args:
        None

    Returns:
        int: Returns a int value as the return code from running the server
            A value of 0 is success and any other value is an error

    Raises:
        KeyboardInterrupt: When an operator uses a keyboard interrupt,
            typically CTRL-C to stop the server.  This will cause the
            server to exit with return code 0
        Exception: Generic exception caught while running the server and
            prints the traceback to stdout.  This will cause the server
            to exit with return code 1
    """
    cfg = config.get()

    # Initialize FastMCP server
    # Available keyword args:
    #   - name
    #   - instructions
    #   - lifespan
    #   - tags
    #   - host
    #   - port
    #   - log_level
    #   - on_duplicate_tools
    #   - on_duplicate_resources
    #   - on_duplicate_prompts
    #
    # The server settings can also be passed using env variables prefixed
    # with FASTMCP_SERVER_
    mcp = FastMCP(
        name="Itential Platform MCP",
        instructions="Itential tools and resources for interacting with Itential Platform",
        lifespan=lifespan,
        include_tags=cfg.server.get("include_tags"),
        exclude_tags=cfg.server.get("exclude_tags")
    )

    try:
        register_tools(mcp)
    except Exception as exc:
        print(f"ERROR: failed to import tool: {str(exc)}", file=sys.stderr)
        sys.exit(1)

    kwargs = {
        "transport": cfg.server.get("transport")
    }

    if kwargs["transport"] == "sse":
        kwargs.update({
            "host": cfg.server.get("host"),
            "port": cfg.server.get("port"),
            "log_level": cfg.server.get("log_level")
        })

    try:
        await mcp.run_async(**kwargs)
    except KeyboardInterrupt:
        print("Shutting down the server")
        sys.exit(0)
    except Exception as exc:
        print(f"ERROR: server stopped unexpectedly: {str(exc)}", file=sys.stderr)
        sys.exit(1)
