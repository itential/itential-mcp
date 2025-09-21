# Copyright (c) 2025 Itential, Inc
# GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)

import sys
import inspect
import pathlib

from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from typing import Any

from fastmcp import FastMCP

from fastmcp.server.middleware import Middleware, MiddlewareContext
from fastmcp.server.middleware.logging import LoggingMiddleware
from fastmcp.server.middleware.timing import DetailedTimingMiddleware
from fastmcp.server.middleware.error_handling import ErrorHandlingMiddleware

from . import client
from . import config
from . import toolutils
from . import bindings
from . import logging


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


class DynamicToolInjectionMiddleware(Middleware):
    """Middleware for injecting dynamic tool configurations into MCP calls.

    This middleware automatically injects tool configuration objects into
    the arguments of MCP tool calls when the tool name matches a configured
    dynamic tool. It adds the configuration as a special `_tool_config` parameter
    that can be used by the tool implementation, then removes it after execution.

    The middleware enables dynamic tool behavior based on configuration without
    requiring manual parameter passing from the client.

    Attributes:
        config (config.Config): The application configuration containing tool definitions.
    """

    def __init__(self, cfg: config.Config):
        """Initialize the middleware with configuration.

        Args:
            cfg (config.Config): The application configuration containing tool definitions.

        Returns:
            None

        Raises:
            None
        """
        self.config = cfg

    async def on_call_tool(self, context: MiddlewareContext, call_next):
        """Inject tool configuration into MCP tool calls.

        Automatically adds the `_tool_config` parameter to tool arguments when
        the tool name matches a configured dynamic tool. The configuration is
        removed after the tool execution completes.

        Args:
            context (MiddlewareContext): The middleware context containing the
                message and other request information.
            call_next: The next middleware or handler in the chain.

        Returns:
            Any: The result from the next handler in the middleware chain.

        Raises:
            Any exceptions from the next handler in the chain.
        """
        for t in self.config.tools:
            if t.tool_name == context.message.name:
                context.message.arguments["_tool_config"] = t

        res = await call_next(context)

        for t in self.config.tools:
            if t.tool_name == context.message.name:
                context.message.arguments.pop("_tool_config", None)
                break

        return res


async def new(cfg: config.Config) -> FastMCP:
    """Initialize a new FastMCP server instance with Itential Platform integration.

    Creates and configures a FastMCP server with comprehensive Itential Platform
    integration including tool discovery, middleware setup, and binding registration.
    The server is configured with tool filtering, error handling, timing, logging,
    and dynamic tool injection capabilities.

    The function performs the following setup:
    - Configures FastMCP server with name, instructions, and lifespan management
    - Adds middleware stack for error handling, timing, logging, and tool injection
    - Registers all discovered tools from the tools directory with appropriate tags
    - Registers dynamic tool bindings based on configuration
    - Sets up JSON schema validation for tool outputs where available

    Args:
        cfg (config.Config): The application configuration containing server settings,
            tool definitions, and platform connection details.

    Returns:
        FastMCP: Fully configured server instance ready for execution with all
            tools registered and middleware configured.

    Raises:
        Exception: If tool discovery, binding registration, or server configuration fails.

    Examples:
        >>> config = config.get()
        >>> server = await new(config)
        >>> await server.run_async(transport="stdio")

    Note:
        This function should only be called once during server initialization.
        Multiple calls may result in duplicate tool registrations.
    """
    logging.info("Initializing the MCP server instance")

    # Initialize FastMCP server
    srv = FastMCP(
        name="Itential Platform MCP",
        instructions=inspect.cleandoc(INSTRUCTIONS),
        lifespan=lifespan,
        include_tags=cfg.server.get("include_tags"),
        exclude_tags=cfg.server.get("exclude_tags"),
    )

    logger = logging.get_logger()

    srv.add_middleware(ErrorHandlingMiddleware(logger=logger))
    srv.add_middleware(DetailedTimingMiddleware(logger=logger))
    srv.add_middleware(LoggingMiddleware(logger=logger, include_payloads=True, max_payload_length=1000))
    srv.add_middleware(DynamicToolInjectionMiddleware(cfg))

    logging.info("Adding tools to MCP server")

    tool_paths = [pathlib.Path(__file__).parent / "tools"]

    if cfg.server.get("tools_path") is not None:
        tool_paths.append(
            pathlib.Path(cfg.server.get("tools_path")).resolve()
        )

    for ele in tool_paths:
        logger.info(f"Adding MCP Tools from {ele}")
        for f, tags in toolutils.itertools(ele):
            tags.add("default")
            kwargs = {"tags": tags}

            try:
                schema = toolutils.get_json_schema(f)
                if schema["type"] == "object":
                    kwargs["output_schema"] = toolutils.get_json_schema(f)

            except ValueError:
                # tool does not have an output_schema defined
                logger.warning(f"tool {f.__name__} has a missing or invalid output_schema")
                pass

            srv.tool(f, **kwargs)
            logging.debug(f"Successfully added tool: {f.__name__}")

    logging.info("Creating dynamic bindings for tools")
    async for fn, kwargs in bindings.iterbindings(cfg):
        srv.tool(fn, **kwargs)
        logging.debug(f"Successfully added tool: {kwargs['name']}")
    logging.info("Dynamic tool bindings is now complete")

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

        mcp = await new(cfg)

        kwargs = {
            "transport": cfg.server.get("transport"),
            "show_banner": False
        }

        if kwargs["transport"] in ("sse", "http"):
            kwargs.update(
                {
                    "host": cfg.server.get("host"),
                    "port": cfg.server.get("port"),
                    #"log_level": cfg.server.get("log_level"),
                }
            )

            if kwargs["transport"] == "http":
                kwargs["path"] = cfg.server.get("path")

        await mcp.run_async(**kwargs)

    except KeyboardInterrupt:
        print("Shutting down the server")
        sys.exit(0)

    except Exception as exc:
        print(f"ERROR: server stopped unexpectedly: {str(exc)}", file=sys.stderr)
        sys.exit(1)
