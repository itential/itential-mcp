# Copyright (c) 2025 Itential, Inc
# GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

"""Command handler logic for the Itential MCP application."""

import inspect
import argparse
from typing import Tuple, Callable, Any

from . import commands
from . import constants


def get_command_handler(
    command: str, args: argparse.Namespace
) -> Tuple[Callable, Tuple[Any, ...], dict]:
    """
    Get the command handler function and its arguments.

    Args:
        command (str): The command name
        args (argparse.Namespace): The parsed arguments

    Returns:
        Tuple[Callable, Tuple, dict]: Handler function, args tuple, and kwargs dict

    Raises:
        TypeError: If the handler is not callable or not a coroutine function
        AttributeError: If the command doesn't exist in the commands module
    """
    try:
        handler_func, handler_args, handler_kwargs = getattr(commands, command)(args)
    except AttributeError as e:
        raise AttributeError(f"Unknown command: {command}") from e

    if not callable(handler_func) or not inspect.iscoroutinefunction(handler_func):
        raise TypeError(constants.HANDLER_TYPE_ERROR)

    return handler_func, (handler_args or ()), (handler_kwargs or {})
