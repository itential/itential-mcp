# Copyright (c) 2025 Itential, Inc
# GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)

"""Itential MCP - Model Context Protocol server for Itential Platform.

This package provides a MCP (Model Context Protocol) server that enables
AI agents to interact with Itential Platform through standardized tools
and functions. The server supports multiple transport mechanisms and
provides comprehensive platform management capabilities.

The package exports the main `run` function for starting the MCP server
and includes version information from package metadata.
"""

from importlib.metadata import version

from .app import run

__version__ = version("itential_mcp")

__all__ = ("run",)
