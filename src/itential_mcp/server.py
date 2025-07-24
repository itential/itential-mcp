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
    Manage the lifespan of Itential Platform connections.

    Creates and manages the client connection to Itential Platform and cache
    instance, yielding them to FastMCP for inclusion in the request context.

    Args:
        mcp (FastMCP): The FastMCP server instance

    Yields:
        dict: Context containing:
            - client: PlatformClient instance for Itential API calls
            - cache: Cache instance for performance optimization
    """
    async with AsyncExitStack():
        yield {
            "client": client.PlatformClient(),
            "cache": cache.Cache()
        }


def new(cfg: config.Config) -> FastMCP:
    """
    Initialize a new FastMCP server instance.

    Creates and configures a FastMCP server with Itential Platform integration,
    including tool filtering based on tags.

    Args:
        cfg (Config): Server configuration containing:
            - include_tags: Optional tags to include specific tools
            - exclude_tags: Optional tags to exclude tools (default: experimental,beta)

    Returns:
        FastMCP: Configured server instance ready for tool registration

    Note:
        This function should only be called once during server initialization.
    """
    # Initialize FastMCP server
    srv = FastMCP(
        name="Itential Platform MCP",
        instructions="Tools for Itential - a network and infrastructure automation and orchestration platform. First, examine your available tools to understand your assigned persona: Platform SRE (platform administration, adapter/integration management, health monitoring), Platform Builder (asset development and promotion with full resource creation), Automation Developer (focused code asset development), Platform Operator (execute jobs, run compliance, consume data) or a Custom set of tools. Based on your tool access, adapt your approach - whether monitoring platform health, building automation assets, developing code resources, or operating established workflows. Key tools like get_health, get_workflows, run_command or create_resource will indicate your operational scope.",
        lifespan=lifespan,
        include_tags=cfg.server.get("include_tags"),
        exclude_tags=cfg.server.get("exclude_tags")
    )

    for f, tags in toolutils.itertools():
        srv.tool(f, tags=tags)

    return srv


async def run() -> int:
    """
    Run the MCP server with the configured transport.

    Entry point for the Itential MCP server supporting multiple transport protocols:
    - stdio: Standard input/output for direct process communication
    - sse: Server-Sent Events for web-based real-time communication
    - http: Streamable HTTP for request/response patterns

    The function loads configuration, creates the MCP server, registers all tools,
    and starts the server with the appropriate transport settings.

    Transport-specific configurations:
    - stdio: No additional configuration needed
    - sse/http: Requires host, port, and log_level
    - http: Additionally requires path configuration

    Returns:
        int: Exit code (0 for success, 1 for error)

    Raises:
        KeyboardInterrupt: Graceful shutdown on CTRL-C (returns 0)
        Exception: Any other error during startup or runtime (returns 1)

    Examples:
        # Default stdio transport
        $ itential-mcp

        # SSE transport for web integration
        $ itential-mcp --transport sse --host 0.0.0.0 --port 8000

        # Streamable HTTP transport
        $ itential-mcp --transport http --host 0.0.0.0 --port 8000 --path /mcp
    """
    try:
        cfg = config.get()

        mcp = new(cfg)

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

        await mcp.run_async(**kwargs)

    except KeyboardInterrupt:
        print("Shutting down the server")
        sys.exit(0)

    except Exception as exc:
        print(f"ERROR: server stopped unexpectedly: {str(exc)}", file=sys.stderr)
        sys.exit(1)
