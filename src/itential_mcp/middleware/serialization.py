# Copyright (c) 2025 Itential, Inc
# GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

"""Middleware for response serialization control.

This module provides middleware for controlling the serialization format of
tool responses based on configuration settings. It supports multiple formats
including JSON and TOON (Token-Oriented Object Notation).
"""

from typing import Any

from fastmcp.server.middleware import Middleware, MiddlewareContext

from .. import config
from ..core import logging
from ..serializers import serialize_toon, serialize_toon_list


class SerializationMiddleware(Middleware):
    """Middleware for controlling response serialization format.

    This middleware automatically serializes tool responses based on the
    configured format (json, toon). It intercepts tool call results
    and transforms Python object responses into the appropriate serialization
    format using serialization functions from the serializers package.

    Serialization Formats:
        - json: Standard JSON format (default for backward compatibility)
        - toon: TOON format for LLM-optimized token efficiency (30-60% reduction)

    The middleware operates on the `on_call_tool` hook, transforming responses
    after tool execution but before returning to the client. It preserves MCP
    protocol compatibility by ensuring responses remain in dictionary format.

    Attributes:
        config (config.Config): The application configuration containing
            serialization format settings.
        format (str): The configured serialization format ("json", "toon").
    """

    def __init__(self, cfg: config.Config):
        """Initialize the middleware with configuration.

        Args:
            cfg (config.Config): The application configuration containing
                the response format setting.

        Returns:
            None

        Raises:
            None
        """
        self.config = cfg
        self.format = cfg.server_response_format

    async def on_call_tool(self, context: MiddlewareContext, call_next) -> Any:
        """Transform tool results based on configured serialization format.

        This method intercepts tool call results and applies the appropriate
        serialization transformation:
        - For dicts and lists, serializes to the configured format
        - For other types, passes through unchanged

        The serialization respects the MCP protocol by converting serialized
        strings back to dictionaries with appropriate structure.

        Args:
            context (MiddlewareContext): The middleware context containing the
                request message and metadata.
            call_next: The next middleware or handler in the chain.

        Returns:
            Any: The transformed result, maintaining MCP protocol compatibility.
                For serialized data, returns a dict with "content" and "format"
                keys. For other types, returns the original result.

        Raises:
            Any exceptions from serialization or the next handler in the chain.
        """
        res = await call_next(context)

        if self.format == "toon":
            # Get the result content from the response
            result = (
                res.structured_content if hasattr(res, "structured_content") else res
            )

            # Apply serialization based on format
            try:
                if isinstance(result, list) and len(result) > 0:
                    serialized = serialize_toon_list(result)
                elif isinstance(result, dict):
                    serialized = serialize_toon(result)

                logging.debug("Serialized result to TOON format")
                res.content[0].text = serialized

            except Exception as e:
                logging.error(f"Error serializing result: {e}")

        return res
