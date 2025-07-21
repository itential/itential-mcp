# Copyright (c) 2025 Itential, Inc
# GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)

from typing import Any, Coroutine, Sequence, Mapping, Tuple

from . import server
from . import metadata
from . import toolutils
from . import runner


def run(args: Any) -> Tuple[Coroutine, Sequence, Mapping]:
    """
    Implement the `itential-mcp run` command

    This function implements the run command and returns the `run` function
    from the `server` module.

    Args:
        args (Any): The argparse Namespace instance

    Returns:
        tuple: Returns a tuple that consistes of a coroutine function, a
            sequence that represents the input args for the function and
            a mapping that represents the keyword arguments for the function

    Raises:
        None
    """
    return server.run, None, None


def version(args: Any) -> Tuple[Coroutine, Sequence, Mapping]:
    """
    Implement the `itential-mcp run` command

    This function implements the run command and returns the `run` function
    from the `server` module.

    Args:
        args (Any): The argparse Namespace instance

    Returns:
        tuple: Returns a tuple that consistes of a coroutine function, a
            sequence that represents the input args for the function and
            a mapping that represents the keyword arguments for the function

    Raises:
        None
    """
    return metadata.display_version, None, None


def tools(args: Any) -> Tuple[Coroutine, Sequence, Mapping]:
    """
    Implement the `itential-mcp tools` command

    This function is the implementat of the `tools` command that
    will display the list of all avaiable tools to stdout.

    Args:
        args (Any): The argparse Namespace instance

    Returns:
        tuple: Returns a tuple that consistes of a coroutine function, a
            sequence that represents the input args for the function and
            a mapping that represents the keyword arguments for the function

    Raises:
        None
    """
    return toolutils.display_tools, None, None

def tags(args: Any) -> Tuple[Coroutine, Sequence, Mapping]:
    """
    Implement the `itential-mcp tags` command

    This function is the implementat of the `tags` command that
    will display the list of all avaiable tags to stdout.

    Args:
        args (Any): The argparse Namespace instance

    Returns:
        tuple: Returns a tuple that consistes of a coroutine function, a
            sequence that represents the input args for the function and
            a mapping that represents the keyword arguments for the function

    Raises:
        None
    """
    return toolutils.display_tags, None, None


def call(args: Any) -> Tuple[Coroutine, Sequence, Mapping]:
    """
    Implement the `itential-mcp call` command

    This function provides the implementation of the `call` command that
    will invoke a tool with (or without) parameters.  The tool function
    executes and returns the result.

    Args:
        args (Any): The argparse Namespace instance

    Returns:
        tuple: Returns a tuple that consistes of a coroutine function, a
            sequence that represents the input args for the function and
            a mapping that represents the keyword arguments for the function

    Raises:
        None
    """
    return runner.run, (args.tool, args.params), None
