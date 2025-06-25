# Copyright (c) 2025 Itential, Inc
# GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)

import os
import sys
import asyncio
import argparse
import traceback

from collections.abc import Sequence
from dataclasses import fields

from . import server
from . import config


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
    server_group = parser.add_argument_group(
        "MCP Server",
        "Configuration options for the MCP Server instance"
    )

    # Itential Platform arguments
    platform_group = parser.add_argument_group(
        "Itential Platform",
        "Configuration options for connecting to Itential Platform server"
    )

    data = [f for f in fields(config.Config)]

    for ele in data:
        attrs = ele.default.json_schema_extra
        if attrs and attrs.get("x-itential-mcp-cli-enabled"):
            helpstr = ele.default.description
            if helpstr is not None:
                helpstr += f" (default={ele.default.default})"
            else:
                helpstr = "NO HELP AVAILABLE!!"

            kwargs = {
                "dest": ele.name,
                "help": helpstr
            }

            kwargs.update(attrs.get("x-itential-mcp-options") or {})
            posargs = attrs.get("x-itential-mcp-arguments")


        if ele.name.startswith("server"):
            server_group.add_argument(*posargs, **kwargs)
        elif ele.name.startswith("platform"):
            platform_group.add_argument(*posargs, **kwargs)


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
