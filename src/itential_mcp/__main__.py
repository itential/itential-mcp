# Copyright (c) 2025 Itential, Inc
# GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)

"""Entry point for running Itential MCP server as a module.

This module provides the entry point for executing the Itential MCP server
using `python -m itential_mcp`. It imports and runs the main application
function asynchronously.
"""

import asyncio

from .app import run

if __name__ == "__main__":
    asyncio.run(run())
