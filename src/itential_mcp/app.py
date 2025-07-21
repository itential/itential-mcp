# Copyright (c) 2025 Itential, Inc
# GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)

import os
import sys
import asyncio
import traceback
import inspect

from collections.abc import Sequence

from . import commands
from . import cli


LEGACY_ENV_VARS = frozenset((
    ("ITENTIAL_MCP_TRANSPORT", "ITENTIAL_MCP_SERVER_TRANSPORT"),
    ("ITENTIAL_MCP_HOST", "ITENTIAL_MCP_SERVER_HOST"),
    ("ITENTIAL_MCP_PORT", "ITENTIAL_MCP_SERVER_PORT"),
    ("ITENTIAL_MCP_LOG_LEVEL", "ITENTIAL_MCP_SERVER_LOG_LEVEL"),
))


def parse_args(args: Sequence) -> None:
    """
    Parses command line arguments

    This function will parse the arguments identified by the `args` argument
    and return a Namespace object with the values. Typically this is used
    to parse command line arguments passed when the application starts.

    Args:
        args (Sequence): The list of arguments to parse

    Returns:
        None

    Raises:
        None
    """
    parser = cli.Parser(
        prog="itential-mcp",
        add_help=False,
        description="Itential MCP\n\n  Find more information at: https://github.com/itential/itential-mcp"
    )

    parser.add_argument(
        "--config",
        help="The Itential MCP configuration file"
    )

    parser.add_argument(
        '-h', '--help',
        action='store_true',
        help="Prints this help message and exits"
    )

    subparsers = parser.add_subparsers(dest="command")

    run_cmd = subparsers.add_parser(
        "run",
        description="Run the MCP server"
    )

    cli.add_server_group(run_cmd)
    cli.add_platform_group(run_cmd)

    call_cmd = subparsers.add_parser(
        "call",
        description="Call a tool and return the results"
    )

    call_cmd.add_argument(
        "tool",
        help="Name of the tool call"
    )

    call_cmd.add_argument(
        "--params",
        metavar="<object>",
        help="Parameters to pass to the tool"
    )

    cli.add_platform_group(call_cmd)

    subparsers.add_parser(
        "tools",
        description="Get list of available tools"
    )

    subparsers.add_parser(
        "tags",
        description="Get list of available tags"
    )

    subparsers.add_parser(
        "version",
        description="Print the version information"
    )

    run_cmd.add_argument(
        "--config",
        help="The Itential MCP configuration file"
    )

    args = parser.parse_args(args=args)

    if args.help or args.command is None:
        parser.print_app_help()
        sys.exit(0)

    for key, value in dict(args._get_kwargs()).items():
        envkey = f"ITENTIAL_MCP_{key}".upper()
        if key.startswith("platform") or key.startswith("server"):
            if value is not None:
                if envkey not in os.environ:
                    if isinstance(value, str):
                        value = ", ".join(value.split(","))
                    os.environ[envkey] = str(value)

    conf_file = args.config
    if conf_file is not None:
        os.environ["ITENTIAL_MCP_CONFIG"] = conf_file

    # XXX (privateip) This will check for any values that use the legacy
    # environment variables which did not include the _SERVER_ in the name.
    for oldvar, newvar in LEGACY_ENV_VARS:
        if oldvar in os.environ and newvar not in os.environ:
            os.environ[newvar] = os.environ.pop(oldvar)

    f, args, kwargs = getattr(commands, args.command)(args)

    if not callable(f) or not inspect.iscoroutinefunction(f):
        raise TypeError("handler must be callable and awaitable")

    return f, (args or ()), (kwargs or {})


def run() -> int:
    """
    Main entry point for the application

    Args:
        None

    Returns:
        int: The application return code

    Raises:
        None
    """
    try:
        f, args, kwargs = parse_args(sys.argv[1:])
        return asyncio.run(f(*args, **kwargs))
    except Exception:
        traceback.print_exc()
        sys.exit(1)
