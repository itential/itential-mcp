# Copyright (c) 2025 Itential, Inc
# GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from typing import Any, Coroutine, Sequence, Mapping, Tuple

from . import runner
from .. import server
from ..core import metadata
from ..utilities import tool


def run(args: Any) -> Tuple[Coroutine, Sequence, Mapping]:
    """Implement the `itential-mcp run` command.

    This function implements the run command and returns the `run` function
    from the `server` module to start the MCP server.

    Args:
        args: The argparse Namespace instance containing command line arguments.

    Returns:
        A tuple consisting of a coroutine function, a sequence that represents
        the input args for the function, and a mapping that represents the
        keyword arguments for the function.

    Raises:
        None
    """
    return server.run, None, None


def version(args: Any) -> Tuple[Coroutine, Sequence, Mapping]:
    """Implement the `itential-mcp version` command.

    This function implements the version command and returns the `display_version`
    function from the `metadata` module to show version information.

    Args:
        args: The argparse Namespace instance containing command line arguments.

    Returns:
        A tuple consisting of a coroutine function, a sequence that represents
        the input args for the function, and a mapping that represents the
        keyword arguments for the function.

    Raises:
        None
    """
    return metadata.display_version, None, None


def tools(args: Any) -> Tuple[Coroutine, Sequence, Mapping]:
    """Implement the `itential-mcp tools` command.

    This function is the implementation of the `tools` command that
    will display the list of all available tools to stdout.

    Args:
        args: The argparse Namespace instance containing command line arguments.

    Returns:
        A tuple consisting of a coroutine function, a sequence that represents
        the input args for the function, and a mapping that represents the
        keyword arguments for the function.

    Raises:
        None
    """
    return tool.display_tools, None, None


def tags(args: Any) -> Tuple[Coroutine, Sequence, Mapping]:
    """Implement the `itential-mcp tags` command.

    This function is the implementation of the `tags` command that
    will display the list of all available tags to stdout.

    Args:
        args: The argparse Namespace instance containing command line arguments.

    Returns:
        A tuple consisting of a coroutine function, a sequence that represents
        the input args for the function, and a mapping that represents the
        keyword arguments for the function.

    Raises:
        None
    """
    return tool.display_tags, None, None


def call(args: Any) -> Tuple[Coroutine, Sequence, Mapping]:
    """Implement the `itential-mcp call` command.

    This function provides the implementation of the `call` command that
    will invoke a tool with (or without) parameters. The tool function
    executes and returns the result.

    Args:
        args: The argparse Namespace instance containing command line arguments,
              including the tool name and parameters to call.

    Returns:
        A tuple consisting of a coroutine function, a sequence that represents
        the input args for the function, and a mapping that represents the
        keyword arguments for the function.

    Raises:
        None
    """
    return runner.run, (args.tool, args.params), None
