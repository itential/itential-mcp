# Copyright (c) 2025 Itential, Inc
# GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)

import os
import sys
import asyncio
import argparse
import traceback

from collections.abc import Sequence

from . import server


LEGACY_ENV_VARS = frozenset((
    ("ITENTIAL_MCP_TRANSPORT", "ITENTIAL_MCP_SERVER_TRANSPORT"),
    ("ITENTIAL_MCP_HOST", "ITENTIAL_MCP_SERVER_HOST"),
    ("ITENTIAL_MCP_PORT", "ITENTIAL_MCP_SERVER_PORT"),
    ("ITENTIAL_MCP_LOG_LEVEL", "ITENTIAL_MCP_SERVER_LOG_LEVEL"),
))


def parse_args(args: Sequence) -> None:
    """
    Parses any arguments

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
    parser = argparse.ArgumentParser(prog="itential-mcp")

    parser.add_argument(
        "--config",
        help="The Itential MCP configuration file"
    )

    # MCP Server arguments
    server_group = parser.add_argument_group("MCP Server")

    server_group.add_argument(
        "--transport",
        dest="server_transport",
        help="The MCP server transport to use (default=stdio)"
    )

    server_group.add_argument(
        "--host",
        dest="server_host",
        help="Address to listen for connections on (default=localhost)"
    )

    server_group.add_argument(
        "--port",
        type=int,
        dest="server_port",
        help="Port to listen for connections on (default=8000)",
    )

    server_group.add_argument(
        "--log-level",
        dest="server_log_level",
        help="Logging level.  One of DEBUG, INFO, WARNING, ERROR, CRITICAL.  (default=INFO)"
    )

    server_group.add_argument(
        "--include-tags",
        dest="server_include_tags",
        help="Include tools that match one of these tags"
    )

    server_group.add_argument(
        "--exclude-tags",
        dest="server_exclude_tags",
        help="Exclude any tool that matches one of these tags"
    )

    # Itential Platform arguments
    platform_group = parser.add_argument_group("Itential Platform")

    platform_group.add_argument(
        "--platform-host",
        help="The host address of Itential Platform to connect to (default=localhost)"
    )

    platform_group.add_argument(
        "--platform-port",
        type=int,
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
        help="Username to use when authenticating to the server (default=admin)"
    )

    platform_group.add_argument(
        "--platform-password",
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
        help="Configure the connection timeout in seconds (default=30)",
    )

    args = parser.parse_args(args=args)

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
        parse_args(sys.argv[1:])
        return asyncio.run(server.run())
    except Exception:
        traceback.print_exc()
        sys.exit(1)
