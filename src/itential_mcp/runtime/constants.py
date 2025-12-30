# Copyright (c) 2025 Itential, Inc
# GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

"""Constants used throughout the Itential MCP application."""

from __future__ import annotations

from typing import Any
from dataclasses import dataclass

# Application constants
APP_NAME = "itential-mcp"
APP_DESCRIPTION = "Itential MCP\n\n  Find more information at: https://github.com/itential/itential-mcp"
GITHUB_URL = "https://github.com/itential/itential-mcp"

# Environment variable constants
ENV_PREFIX = "ITENTIAL_MCP_"
CONFIG_ENV_VAR = "ITENTIAL_MCP_CONFIG"

# Help messages
GLOBAL_HELP_MESSAGE = "Prints this help message and exits"
CONFIG_HELP_MESSAGE = "The Itential MCP configuration file"
COMMAND_HELP_SUFFIX = (
    '\nUse "itential-mcp <COMMAND> --help" for more information about a command.\n'
)

# Error messages
HANDLER_TYPE_ERROR = "handler must be callable and awaitable"


@dataclass(frozen=True)
class CommandConfig:
    """Configuration for a CLI command."""

    name: str
    description: str
    arguments: dict[str, Any]
    add_platform_group: bool = False
    add_server_group: bool = False


# Command configurations
COMMANDS = [
    CommandConfig(
        name="run",
        description="Run the MCP server",
        arguments={"--config": {"help": CONFIG_HELP_MESSAGE}},
        add_platform_group=True,
        add_server_group=True,
    ),
    CommandConfig(
        name="call",
        description="Call a tool and return the results",
        arguments={
            "tool": {"help": "Name of the tool call"},
            "--params": {
                "metavar": "<object>",
                "help": "Parameters to pass to the tool",
            },
        },
        add_platform_group=True,
    ),
    CommandConfig(
        name="tools",
        description="Get list of available tools",
        arguments={},
    ),
    CommandConfig(
        name="tags",
        description="Get list of available tags",
        arguments={},
    ),
    CommandConfig(
        name="version",
        description="Print the version information",
        arguments={},
    ),
]
