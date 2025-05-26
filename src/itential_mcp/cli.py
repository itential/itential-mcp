# Copyright (c) 2025 Itential, Inc
# GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)

import os
import sys
import asyncio
import argparse

from collections.abc import Sequence

from typing import Any

from . import server
from . import env


def parse_args(args: Sequence) -> dict[str, Any]:
    """
    Parses any arguments

    This function will parse the arguments identified by the `args` argument
    and return a Namespace object with the values.   Typically this is used
    to parse command line arguments passed when the application starts.

    Args:
        args (Sequence): The list of arguments to parse

    Returns:
        dict[str, Any]: Returns a Python dict object that has parsed the args

    Raises:
        None
    """
    parser = argparse.ArgumentParser(prog="itential-mcp")

    # MCP Server arguments
    server_group = parser.add_argument_group("MCP Server")

    server_group.add_argument(
        "--transport",
        default="stdio",
        help="The MCP server transport to use (default=stdio)"
    )

    server_group.add_argument(
        "--host",
        default="localhost",
        help="Address to listen for connections on (default=localhost)"
    )

    server_group.add_argument(
        "--port",
        type=int,
        default=8000,
        help="Port to listen for connections on (default=8000)",
    )

    server_group.add_argument(
        "--log-level",
        default="INFO",
        help="Logging level.  One of DEBUG, INFO, WARNING, ERROR, CRITICAL.  (default=INFO)"
    )

    # Itential Platform arguments
    platform_group = parser.add_argument_group("Itential Platform")

    platform_group.add_argument(
        "--platform-host",
        default="localhost",
        help="The host address of Itential Platform to connect to (default=localhost)"
    )

    platform_group.add_argument(
        "--platform-port",
        type=int,
        default=0,
        help="The port to use when connecting to Itential Platform (default=0)"
    )

    platform_group.add_argument(
        "--platform-disable-tls",
        action="store_true",
        help="Disable using TLS to connect to the server (default=False)"
    )

    platform_group.add_argument(
        "--platform-disable-verify",
        action="store_true",
        help="Disable certificate verification (default=False)",
    )

    platform_group.add_argument(
        "--platform-user",
        default="admin",
        help="Username to use when authenticating to the server (default=admin)"
    )

    platform_group.add_argument(
        "--platform-password",
        default="admin",
        help="Password to use when authenticating to the server (default=admin)"
    )

    platform_group.add_argument(
        "--platform-client-id",
        help="Client ID to use when authenticating to the server with OAuth",
    )

    platform_group.add_argument(
        "--platform-client-secret",
        help="Client secret to use when authenticating to the server with OAuth",
    )

    platform_group.add_argument(
        "--platform-timeout",
        type=int,
        default=30,
        help="Configure the connection timeout in seconds (default=30)",
    )

    args = parser.parse_args(args=args)

    kwargs = {}

    for key, value in dict(args._get_kwargs()).items():
        envkey = f"ITENTIAL_MCP_{key}".upper()

        if key.startswith("platform"):
            if value is not None:
                if envkey not in os.environ:
                    os.environ[envkey] = str(value)
        else:
            if isinstance(value, bool):
                v = env.getbool(envkey, default=value)
            elif isinstance(value, int):
                v = env.getint(envkey, default=value)
            elif isinstance(value, str):
                v = env.getstr(envkey, default=value)
            else:
                v = value
            kwargs[key] = v

    return kwargs


def run() -> int:
    """
    Main entry point for the application

    Args:
        None

    Returns:
        int:

    Raises:
        None
    """
    try:
        return asyncio.run(server.run(**parse_args(sys.argv[1:])))
    except Exception:
        sys.exit(1)
