# Copyright (c) 2025 Itential, Inc
# GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

import sys
import inspect
import pathlib
import asyncio

from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from typing import Any

import uvicorn

from fastmcp import FastMCP

from fastmcp.server.middleware.logging import LoggingMiddleware
from fastmcp.server.middleware.timing import DetailedTimingMiddleware
from fastmcp.server.middleware.error_handling import ErrorHandlingMiddleware

from .auth import build_auth_provider, supports_transport
from . import routes
from .keepalive import start_keepalive
from ..platform import PlatformClient
from .. import config
from .. import bindings
from ..core import logging
from ..utilities import tool as toolutils
from ..middleware.bindings import BindingsMiddleware
from ..middleware.serialization import SerializationMiddleware


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
    Also starts the keepalive task if configured.

    Args:
        mcp (FastMCP): The FastMCP server instance

    Yields:
        dict: Context containing:
            - client: PlatformClient instance for Itential API calls
    """
    # Use PlatformClient as an async context manager
    async with PlatformClient() as client_instance:
        keepalive_task = None
        try:
            # Start keepalive task if interval is configured (> 0)
            cfg = config.get()
            keepalive_interval = cfg.server.keepalive_interval
            if keepalive_interval > 0:
                keepalive_task = start_keepalive(client_instance, keepalive_interval)

            yield {"client": client_instance}

        finally:
            # Cancel keepalive task if it was started
            if keepalive_task and not keepalive_task.done():
                logging.info("Stopping keepalive task")
                keepalive_task.cancel()
                try:
                    await keepalive_task
                except asyncio.CancelledError:
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
        await self.__init_routes__()
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

        auth_provider = build_auth_provider(self.config)

        # Validate auth provider compatibility with transport
        transport = self.config.server.transport
        if auth_provider and not supports_transport(auth_provider, transport):
            from ..core.exceptions import ConfigurationException

            raise ConfigurationException(
                f"Authentication provider {type(auth_provider).__name__} "
                f"is not supported for transport '{transport}'. "
                f"OAuth providers require HTTP-based transports (sse or http)."
            )

        # Initialize FastMCP server
        self.mcp = FastMCP(
            name="Itential Platform MCP",
            instructions=inspect.cleandoc(INSTRUCTIONS),
            lifespan=lifespan,
            auth=auth_provider,
            include_tags=self.config.server.include_tags,
            exclude_tags=self.config.server.exclude_tags,
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
        self.mcp.add_middleware(SerializationMiddleware(self.config))

    async def __init_routes__(self) -> None:
        """Initialize and register health check routes.

        Registers the Kubernetes-standard health check endpoints with the FastMCP server:
        - /status/healthz: General health check endpoint
        - /status/readyz: Readiness probe endpoint
        - /status/livez: Liveness probe endpoint

        These endpoints follow Kubernetes best practices for health monitoring
        and are used by orchestration systems to determine pod status.
        """
        self.mcp.custom_route("/status/healthz", methods=["GET"])(routes.get_healthz)
        self.mcp.custom_route("/status/readyz", methods=["GET"])(routes.get_readyz)
        self.mcp.custom_route("/status/livez", methods=["GET"])(routes.get_livez)

    async def __init_tools__(self) -> None:
        """Initialize tools."""
        logging.info("Adding tools to MCP server")

        tool_paths = [pathlib.Path(__file__).parent.parent / "tools"]

        if self.config.server.tools_path is not None:
            tool_paths.append(pathlib.Path(self.config.server.tools_path).resolve())

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
        if self.config.server.transport in ("sse", "http"):
            app = self.mcp.http_app(path=self.config.server.path)

            uvicorn_config = uvicorn.Config(
                app=app,
                host=self.config.server.host,
                port=self.config.server.port,
                ssl_certfile=self.config.server.certificate_file,
                ssl_keyfile=self.config.server.private_key_file,
                ws="wsproto",
            )

            srv = uvicorn.Server(uvicorn_config)

            return await srv.serve()
        else:
            return await self.mcp.run_async(transport="stdio", show_banner=False)


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

        logging.set_level(cfg.server.log_level)

        async with Server(cfg) as srv:
            await srv.run()

    except KeyboardInterrupt:
        print("Shutting down the server")
        sys.exit(0)

    except Exception as exc:
        print(f"ERROR: server stopped unexpectedly: {str(exc)}", file=sys.stderr)
        sys.exit(1)
