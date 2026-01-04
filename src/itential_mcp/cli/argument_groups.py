# Copyright (c) 2025 Itential, Inc
# GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

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
    response = list()

    # Iterate through nested config dataclasses
    config_classes = [
        (config.ServerConfig, "server_"),
        (config.AuthConfig, "server_auth_"),
        (config.PlatformConfig, "platform_"),
    ]

    for config_class, prefix in config_classes:
        for field in fields(config_class):
            # Skip if field doesn't have default (shouldn't happen with our models)
            if not hasattr(field, "default"):
                continue

            attrs = getattr(field.default, "json_schema_extra", None)
            if not attrs or not attrs.get("x-itential-mcp-cli-enabled"):
                continue

            helpstr = getattr(field.default, "description", None)

            # Get default value
            if hasattr(field.default, "default_factory"):
                try:
                    default_value = field.default.default_factory()
                except Exception:
                    default_value = "UNKNOWN"
            elif hasattr(field.default, "default"):
                default_value = field.default.default
            else:
                default_value = "UNKNOWN"

            if helpstr is not None:
                helpstr += f" (default={default_value})"
            else:
                helpstr = "NO HELP AVAILABLE!!"

            # Use the prefixed name for dest to match legacy behavior
            dest_name = f"{prefix}{field.name}"
            kwargs = {"dest": dest_name, "help": helpstr}

            kwargs.update(attrs.get("x-itential-mcp-options") or {})
            posargs = attrs.get("x-itential-mcp-arguments")

            response.append((dest_name, posargs, kwargs))

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
