# Copyright (c) 2025 Itential, Inc
# GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

"""Configuration package for Itential MCP Server.

This package provides a clean, modular configuration system with:
- Immutable dataclass-based models for type safety
- Clear separation of concerns between models, loaders, and validators
- Support for multiple configuration sources (env, file, defaults)

Public API:
    Config: Main configuration dataclass
    ServerConfig: Server configuration section
    AuthConfig: Authentication configuration section
    PlatformConfig: Platform connection configuration section
    Tool, EndpointTool, ServiceTool: Tool configuration models
    get(): Load and return cached configuration instance
    validate_tool_name(): Validate tool naming conventions
"""

from __future__ import annotations

from functools import lru_cache

from .models import (
    Config,
    ServerConfig,
    AuthConfig,
    PlatformConfig,
    Tool,
    EndpointTool,
    ServiceTool,
)
from .validators import validate_tool_name, validate_port, validate_host
from .loaders import load_config, _parse_tool_env_variables


# Expose internal function for backward compatibility with tests
_get_tools_from_env = _parse_tool_env_variables


__all__ = (
    "Config",
    "ServerConfig",
    "AuthConfig",
    "PlatformConfig",
    "Tool",
    "EndpointTool",
    "ServiceTool",
    "validate_tool_name",
    "validate_port",
    "validate_host",
    "get",
    "options",
    "_get_tools_from_env",
)


def options(*args, **kwargs) -> dict:
    """Utility function to add extra parameters to fields.

    This function will add extra parameters to a Field in the Config
    class. Specifically it handles adding the necessary keys to support
    generating the CLI options from the configuration. This unifies the
    parameter descriptions and default values for consistency.

    Args:
        *args: Positional arguments to be added to the CLI command line option.
        **kwargs: Optional arguments to be added to the CLI command line option.

    Returns:
        Dictionary to be added to the Field function signature.

    Raises:
        None.
    """
    return {
        "x-itential-mcp-cli-enabled": True,
        "x-itential-mcp-arguments": args,
        "x-itential-mcp-options": kwargs,
    }


@lru_cache(maxsize=None)
def get() -> Config:
    """Return the configuration instance.

    This function will load the configuration and return an instance. This
    function is cached and is safe to call multiple times. The configuration
    is loaded only once and the cached instance is returned with every call.

    Access config via nested attributes:
        - config.server.host, config.server.port, etc.
        - config.auth.type, config.auth.issuer, etc.
        - config.platform.host, config.platform.timeout, etc.

    Returns:
        Config instance with nested dataclass structure.

    Raises:
        FileNotFoundError: If a configuration file is specified but not found.
    """
    return load_config()
