# Copyright (c) 2025 Itential, Inc
# GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)

import os
import sys
import inspect
import importlib.util

from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager, AsyncExitStack

from typing import Any, Literal

from fastmcp import FastMCP

from . import client


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
            "client": client.PlatformClient()
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

            # Add the module to globals
            globals()[module_name] = module

            # Inspect the module to retreive all of the functions
            for name, f in inspect.getmembers(module, inspect.isfunction):
                if not name.startswith("_"):
                    mcp.add_tool(f)


async def run(
    transport: str = "stdio",
    host: str | None = "localhost",
    port: int = 8000,
    log_level: Literal["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"] | int = "INFO",
) -> int:
    """
    Run the MCP server

    This function will run the MCP server using the configured transport
    option.

    Args:
        args (Sequence | None):
        transport (str): Server transport to use.  Valid values for this
            argument are `sse` or `stdio`.  The default value is `stdio`

        host (str | None): The host to run the server on.  The default
            value for host is "localhost"

        port (int): The port on the host to listen for connections on.  The
            default value for port is 0.

    Returns:
        int: Returns a int value as the return code from running the server
            A value of 0 is success and any other value is an error

    Raises:
        ValueError: When the value of transport is not a valid value
        ValueError: When the value of log_level is not a valid value
    """
    if transport not in ("stdio", "sse"):
        raise ValueError("invalid setting for transport")

    if isinstance(log_level, str):
        if log_level.upper() not in ("DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"):
            raise ValueError("invalid setting for log_level")



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
        log_level=log_level.upper(),
    )

    try:
        register_tools(mcp)
    except Exception as exc:
        print(f"ERROR: failed to  import tool: {str(exc)}", file=sys.stderr)
        sys.exit(1)

    kwargs = {
        "transport": transport,
    }

    if transport == "sse":
        kwargs.update({
            "host": host,
            "port": port,
        })

    try:
        await mcp.run_async(**kwargs)
    except KeyboardInterrupt:
        sys.exit(0)
    except Exception as exc:
        print(f"ERROR: failed to  import tool: {str(exc)}", file=sys.stderr)
        sys.exit(1)
