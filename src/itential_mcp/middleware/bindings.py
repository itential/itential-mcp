# Copyright (c) 2025 Itential, Inc
# GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import annotations

from fastmcp.server.middleware import Middleware, MiddlewareContext

from .. import config


class BindingsMiddleware(Middleware):
    """Middleware for injecting dynamic tool configurations into MCP calls.

    This middleware automatically injects tool configuration objects into
    the arguments of MCP tool calls when the tool name matches a configured
    dynamic tool. It adds the configuration as a special `_tool_config` parameter
    that can be used by the tool implementation, then removes it after execution.

    The middleware enables dynamic tool behavior based on configuration without
    requiring manual parameter passing from the client.

    Attributes:
        config (config.Config): The application configuration containing tool definitions.
        tool_lookup (dict[str, config.Tool]): O(1) lookup dictionary mapping tool names to tool configs.
    """

    def __init__(self, cfg: config.Config):
        """Initialize the middleware with configuration.

        Creates an O(1) lookup dictionary from tool names to tool configurations
        for efficient tool config injection during request handling.

        Args:
            cfg (config.Config): The application configuration containing tool definitions.

        Returns:
            None

        Raises:
            None
        """
        self.config = cfg
        # Create O(1) lookup dictionary: tool_name -> tool config
        self.tool_lookup: dict[str, config.Tool] = {
            tool.tool_name: tool for tool in cfg.tools
        }

    async def on_call_tool(self, context: MiddlewareContext, call_next):
        """Inject tool configuration into MCP tool calls.

        Automatically adds the `_tool_config` parameter to tool arguments when
        the tool name matches a configured dynamic tool. The configuration is
        removed after the tool execution completes.

        Uses O(1) dictionary lookup for efficient tool config retrieval instead
        of O(n) linear search through all configured tools.

        Args:
            context (MiddlewareContext): The middleware context containing the
                message and other request information.
            call_next: The next middleware or handler in the chain.

        Returns:
            Any: The result from the next handler in the middleware chain.

        Raises:
            Any exceptions from the next handler in the chain.
        """
        # O(1) dictionary lookup instead of O(n) loop
        tool_config = self.tool_lookup.get(context.message.name)

        if tool_config:
            context.message.arguments["_tool_config"] = tool_config

        res = await call_next(context)

        if tool_config:
            context.message.arguments.pop("_tool_config", None)

        return res
