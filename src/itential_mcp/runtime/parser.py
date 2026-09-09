# Copyright (c) 2025 Itential, Inc
# GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

"""Argument parsing logic for the Itential MCP application."""

from __future__ import annotations

import os
import sys
import argparse
from typing import Any, Callable
from collections.abc import Sequence

from .. import cli
from . import constants
from ..cli.argument_groups import add_platform_group, add_server_group
from ..core import env
from ..core import logging
from .handlers import get_command_handler


def _create_global_options_parser() -> cli.Parser:
    """
    Create parser for global options that apply to all commands.

    This parser is used as a parent parser for all subcommands to ensure
    global options like --config are available to all commands.

    Returns:
        cli.Parser: Parser with global options (add_help=False for parent)

    Raises:
        None
    """
    parser = cli.Parser(add_help=False)
    parser.add_argument("--config", metavar="FILE", help=constants.CONFIG_HELP_MESSAGE)
    return parser


def _create_main_parser(global_options_parser: cli.Parser) -> cli.Parser:
    """
    Create and configure the main argument parser.

    Args:
        global_options_parser: Parser with global options to inherit

    Returns:
        cli.Parser: The configured main parser

    Raises:
        None
    """
    parser = cli.Parser(
        prog=constants.APP_NAME,
        add_help=False,
        description=constants.APP_DESCRIPTION,
        parents=[global_options_parser],
    )

    parser.add_argument(
        "-h", "--help", action="store_true", help=constants.GLOBAL_HELP_MESSAGE
    )

    return parser


def _create_subparsers(parser: cli.Parser, global_options_parser: cli.Parser) -> None:
    """
    Create and configure subparsers for different commands using configuration.

    Args:
        parser: The main parser to add subparsers to
        global_options_parser: Parser with global options to inherit

    Returns:
        None

    Raises:
        None
    """
    subparsers = parser.add_subparsers(dest="command")

    for command_config in constants.COMMANDS:
        cmd = subparsers.add_parser(
            command_config.name,
            description=command_config.description,
        )

        # Add command-specific arguments
        for arg_name, arg_config in command_config.arguments.items():
            if arg_name.startswith("--"):
                cmd.add_argument(arg_name, **arg_config)
            else:
                cmd.add_argument(arg_name, **arg_config)

        # Add argument groups if specified
        if command_config.add_server_group:
            add_server_group(cmd)
        if command_config.add_platform_group:
            add_platform_group(cmd)


def _process_logging_config(args: argparse.Namespace) -> None:
    """
    Process and configure logging based on parsed arguments.

    Args:
        args (argparse.Namespace): The parsed arguments namespace

    Returns:
        None

    Raises:
        None
    """
    if hasattr(args, "server_log_level") and args.server_log_level is not None:
        propagate = env.getbool("ITENTIAL_MCP_SERVER_LOGGING_PROPAGATION", False)
        logging.set_level(args.server_log_level.upper(), propagate)
        setattr(args, "server_log_level", args.server_log_level.upper())


def _set_environment_variables(args: argparse.Namespace) -> None:
    """
    Set environment variables based on parsed arguments.

    Args:
        args (argparse.Namespace): The parsed arguments namespace

    Returns:
        None

    Raises:
        None
    """
    for key, value in dict(args._get_kwargs()).items():
        envkey = f"{constants.ENV_PREFIX}{key}".upper()
        if key.startswith(("platform", "server")) and value is not None:
            if envkey not in os.environ:
                # Handle comma-separated values
                if isinstance(value, str):
                    value = ", ".join(value.split(","))
                os.environ[envkey] = str(value)

    # Handle config file separately
    if args.config is not None:
        os.environ[constants.CONFIG_ENV_VAR] = args.config


def parse_args(args: Sequence) -> tuple[Callable, tuple[Any, ...], dict]:
    """
    Parse command line arguments and return the command handler.

    This function will parse the arguments identified by the `args` argument
    and return a tuple containing the command handler function and its arguments.
    Typically this is used to parse command line arguments passed when the
    application starts.

    Args:
        args (Sequence): The list of arguments to parse

    Returns:
        tuple[Callable, tuple, dict]: The command handler function, positional
            arguments tuple, and keyword arguments dict

    Raises:
        SystemExit: If help is requested (exit 0); no command is provided
            with no other arguments and no ITENTIAL_MCP_* environment
            variables set (exit 0); or no command is provided while
            arguments were supplied or ITENTIAL_MCP_* environment
            variables are set, indicating a real (non-interactive)
            invocation missing its subcommand (exit 2)
        TypeError: If the command handler is invalid
        AttributeError: If the command doesn't exist
    """
    global_options_parser = _create_global_options_parser()
    parser = _create_main_parser(global_options_parser)
    _create_subparsers(parser, global_options_parser)

    parsed_args = parser.parse_args(args=args)

    _process_logging_config(parsed_args)

    if parsed_args.help:
        parser.print_app_help()
        sys.exit(0)
    elif parsed_args.command is None:
        env_configured = any(key.startswith(constants.ENV_PREFIX) for key in os.environ)

        if len(args) == 0 and not env_configured:
            parser.print_app_help()
            sys.exit(0)

        if parsed_args.config is not None:
            message = constants.CONFIG_WITHOUT_SUBCOMMAND_HINT
        elif len(args) == 0 and env_configured:
            message = constants.ENV_CONFIGURED_WITHOUT_SUBCOMMAND_HINT
        else:
            message = constants.MISSING_SUBCOMMAND_MESSAGE

        parser.print_app_help_to_stderr(message)
        sys.exit(2)

    _set_environment_variables(parsed_args)

    return get_command_handler(parsed_args.command, parsed_args)
