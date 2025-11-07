# Copyright (c) 2025 Itential, Inc
# GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)

import argparse
from collections.abc import Sequence
from typing import Tuple, Mapping
from dataclasses import fields
from functools import lru_cache

from .. import config


@lru_cache(maxsize=None)
def _get_arguments_from_config() -> Sequence[Tuple[str, Sequence, Mapping]]:
    """
    Get the CLI options from the Config

    This function will iterate over the fields in the Config object and
    return the set of configuration options to be provided as CLI optional
    arguments.

    Args:
        None

    Returns:
        Sequence: Returns a sequence of tuples where each element contains
            the option name, sequence of arguments, and mapping of keyword
            options

    Raises:
        None
    """
    data = [f for f in fields(config.Config)]
    response = list()

    for ele in data:
        attrs = ele.default.json_schema_extra
        if attrs and attrs.get("x-itential-mcp-cli-enabled"):
            helpstr = ele.default.description

            if hasattr(config.Config, ele.name):
                attr = getattr(config.Config, ele.name)
                if hasattr(attr, "default_factory"):
                    default_value = getattr(config.Config, ele.name).default_factory()
                elif hasattr(attr, "default"):
                    default_value = getattr(config.Config, ele.name).default
            else:
                default_value = "UNKNOWN"

            if helpstr is not None:
                helpstr += f" (default={default_value})"

            else:
                helpstr = "NO HELP AVAILABLE!!"

            kwargs = {"dest": ele.name, "help": helpstr}

            kwargs.update(attrs.get("x-itential-mcp-options") or {})
            posargs = attrs.get("x-itential-mcp-arguments")

            response.append((ele.name, posargs, kwargs))

    return response


def add_platform_group(cmd: argparse.ArgumentParser) -> None:
    """
    Add the optional Platform group command line options

    This function will add the Itential Platform command line options to
    the command.  The Platform command line options group provides options
    for configuration the connection to Itential Platform.

    Args:
        cmd (argparse.ArgumentParser): The argument parser to add the group to

    Returns:
        None

    Raises:
        None
    """
    # Itential Platform arguments
    platform_group = cmd.add_argument_group(
        "Itential Platform Options",
        "Configuration options for connecting to Itential Platform API",
    )

    for ele, posargs, kwargs in _get_arguments_from_config():
        if ele.startswith("platform"):
            platform_group.add_argument(*posargs, **kwargs)


def add_server_group(cmd: argparse.ArgumentParser) -> None:
    """
    Add the optional Server group command line options

    This function will add the MCP Server command line options to
    the command.  The Server command line options group provides options
    for configuring the MCP Server instance.

    Args:
        cmd (argparse.ArgumentParser): The argument parser to add the group to

    Returns:
        None

    Raises:
        None
    """
    # MCP Server arguments
    server_group = cmd.add_argument_group(
        "MCP Server Options", "Configuration options for the MCP Server instance"
    )

    for ele, posargs, kwargs in _get_arguments_from_config():
        if ele.startswith("server"):
            server_group.add_argument(*posargs, **kwargs)
