# Copyright (c) 2025 Itential, Inc
# GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)

from typing import Any, Coroutine, Sequence, Mapping, Tuple

from . import server
from . import metadata


def run(args: Any) -> Tuple[Coroutine, Sequence, Mapping]:
    """
    Implements the `itential-mcp run` command

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
    Implements the `itential-mcp run` command

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
