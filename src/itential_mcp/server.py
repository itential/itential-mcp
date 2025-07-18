# Copyright (c) 2025 Itential, Inc
# GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)

import sys

from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager, AsyncExitStack

from typing import Any

from fastmcp import FastMCP

from . import client
from . import config
from . import cache
from . import toolutils


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


def new(cfg: config.Config) -> FastMCP:
    """
    Initialize the FastMCP server

    This function will intialize a new instance of the FastMCP server and
    return it to the calling function.  This function should only be called
    once to initialize the server.

    Args:
        cfg (Config): An instance of `config.Config` that provides the
            server configuration values

    Returns:
        FastMCP: An instance of a FastMCP server

    Raises:
        None
    """
    # Initialize FastMCP server
    return FastMCP(
        name="Itential Platform MCP",
        instructions="Itential tools and resources for interacting with Itential Platform",
        lifespan=lifespan,
        include_tags=cfg.server.get("include_tags"),
        exclude_tags=cfg.server.get("exclude_tags")
    )


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

    mcp = new(cfg)

    try:
        for f, tags in toolutils.itertools():
            mcp.tool(f, tags=tags)

    except Exception as exc:
        print(f"ERROR: failed to import tool: {str(exc)}", file=sys.stderr)
        sys.exit(1)

    kwargs = {
        "transport": cfg.server.get("transport")
    }

    if kwargs["transport"] in ("sse", "http"):
        kwargs.update({
            "host": cfg.server.get("host"),
            "port": cfg.server.get("port"),
            "log_level": cfg.server.get("log_level")
        })
        if kwargs["transport"] == "http":
            kwargs["path"] = cfg.server.get("path")

    try:
        await mcp.run_async(**kwargs)

    except KeyboardInterrupt:
        print("Shutting down the server")
        sys.exit(0)

    except Exception as exc:
        print(f"ERROR: server stopped unexpectedly: {str(exc)}", file=sys.stderr)
        sys.exit(1)
