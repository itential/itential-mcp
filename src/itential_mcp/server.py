# Copyright (c) 2025 Itential, Inc
# GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)

import sys
import inspect
import pathlib

from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from typing import Any

from fastmcp import FastMCP

from fastmcp.server.middleware.logging import LoggingMiddleware
from fastmcp.server.middleware.timing import DetailedTimingMiddleware
from fastmcp.server.middleware.error_handling import ErrorHandlingMiddleware

from . import auth
from . import client
from . import config
from .utilities import tool as toolutils
from . import bindings
from .core import logging

from .middleware.bindings import BindingsMiddleware


INSTRUCTIONS = """
Tools for Itential - a network and infrastructure automation and orchestration
platform. First, examine your available tools to understand your assigned
persona: Platform SRE (platform administration, adapter/integration management,
health monitoring), Platform Builder (asset development and promotion with full
resource creation), Automation Developer (focused code asset development),
Platform Operator (execute jobs, run compliance, consume data) or a Custom set
of tools. Based on your tool access, adapt your approach - whether monitoring
platform health, building automation assets, developing code resources, or
operating established workflows. Key tools like get_health, get_workflows,
run_command or create_resource will indicate your operational scope.
"""


@asynccontextmanager
async def lifespan(mcp: FastMCP) -> AsyncGenerator[dict[str | Any], None]:
    """
    Manage the lifespan of Itential Platform connections.

    Creates and manages the client connection to Itential Platform,
    yielding it to FastMCP for inclusion in the request context.

    Args:
        mcp (FastMCP): The FastMCP server instance

    Yields:
        dict: Context containing:
            - client: PlatformClient instance for Itential API calls
    """
    # Create client instance
    client_instance = client.PlatformClient()

    try:
        yield {"client": client_instance}

    finally:
        # No cleanup needed for client
        pass


class Server:
    def __init__(self, cfg: config.Config):
        self.config = cfg
        self.mcp = None

    async def __aenter__(self):
        """Async context manager entry point.

        Initializes the server, tools, and bindings when entering the context.

        Returns:
            Server: The initialized server instance

        Raises:
            Exception: If server initialization fails
        """
        await self.__init_server__()
        await self.__init_tools__()
        await self.__init_bindings__()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit point.

        Performs cleanup when exiting the context.

        Args:
            exc_type: Exception type if an exception occurred
            exc_val: Exception value if an exception occurred
            exc_tb: Exception traceback if an exception occurred

        Returns:
            None
        """
        # Cleanup code if needed
        pass

    async def __init_server__(self) -> None:
        """Initialize a new FastMCP server instance with Itential Platform integration."""
        logging.info("Initializing the MCP server instance")

        auth_provider = auth.build_auth_provider(self.config)

        # Initialize FastMCP server
        self.mcp = FastMCP(
            name="Itential Platform MCP",
            instructions=inspect.cleandoc(INSTRUCTIONS),
            lifespan=lifespan,
            auth=auth_provider,
            include_tags=self.config.server.get("include_tags"),
            exclude_tags=self.config.server.get("exclude_tags"),
        )

        logger = logging.get_logger()

        self.mcp.add_middleware(ErrorHandlingMiddleware(logger=logger))
        self.mcp.add_middleware(DetailedTimingMiddleware(logger=logger))
        self.mcp.add_middleware(
            LoggingMiddleware(
                logger=logger, include_payloads=True, max_payload_length=1000
            )
        )
        self.mcp.add_middleware(BindingsMiddleware(self.config))

    async def __init_tools__(self) -> None:
        """Initialize tools."""
        logging.info("Adding tools to MCP server")

        tool_paths = [pathlib.Path(__file__).parent / "tools"]

        if self.config.server.get("tools_path") is not None:
            tool_paths.append(
                pathlib.Path(self.config.server.get("tools_path")).resolve()
            )

        logger = logging.get_logger()

        for ele in tool_paths:
            logger.info(f"Adding MCP Tools from {ele}")
            for f, tags in toolutils.itertools(ele):
                tags.add("default")
                kwargs = {"tags": tags}

                try:
                    schema = toolutils.get_json_schema(f)
                    if schema["type"] == "object":
                        kwargs["output_schema"] = schema

                except ValueError:
                    # tool does not have an output_schema defined
                    logger.warning(
                        f"tool {f.__name__} has a missing or invalid output_schema"
                    )
                    pass

                self.mcp.tool(f, **kwargs)
                logging.debug(f"Successfully added tool: {f.__name__}")

    async def __init_bindings__(self) -> None:
        """Initialize bindings."""
        logging.info("Creating dynamic bindings for tools")
        async for fn, kwargs in bindings.iterbindings(self.config):
            self.mcp.tool(fn, **kwargs)
            logging.debug(f"Successfully added tool: {kwargs['name']}")
        logging.info("Dynamic tool bindings is now complete")

    async def run(self):
        """Run the server."""
        kwargs = {
            "transport": self.config.server.get("transport"),
            "show_banner": False,
        }

        if kwargs["transport"] in ("sse", "http"):
            kwargs.update(
                {
                    "host": self.config.server.get("host"),
                    "port": self.config.server.get("port"),
                }
            )

            if kwargs["transport"] == "http":
                kwargs["path"] = self.config.server.get("path")

        return await self.mcp.run_async(**kwargs)


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

        logging.set_level(cfg.server_log_level)

        async with Server(cfg) as srv:
            await srv.run()

    except KeyboardInterrupt:
        print("Shutting down the server")
        sys.exit(0)

    except Exception as exc:
        print(f"ERROR: server stopped unexpectedly: {str(exc)}", file=sys.stderr)
        sys.exit(1)
