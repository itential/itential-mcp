# Copyright (c) 2025 Itential, Inc
# GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

"""Validation functions for configuration values.

This module provides reusable validation functions for configuration
parameters. All validators follow a consistent pattern of raising
ValueError on invalid input with clear error messages.
"""

import re
import ipaddress


def validate_tool_name(tool_name: str) -> str:
    """Validate that a tool name follows the required naming convention.

    Tool names must start with a letter and only contain letters, numbers,
    and underscores. This ensures compatibility with Python function naming
    and prevents injection attacks.

    Args:
        tool_name: The tool name to validate.

    Returns:
        The validated tool name.

    Raises:
        ValueError: If the tool name does not match the required pattern.
    """
    if not tool_name:
        raise ValueError("Tool name cannot be empty")

    pattern = r"^[a-zA-Z][a-zA-Z0-9_]*$"
    if not re.match(pattern, tool_name):
        raise ValueError(
            f"Tool name '{tool_name}' is invalid. Tool names must start with a letter "
            "and only contain letters, numbers, and underscores."
        )

    return tool_name


def validate_port(port: int) -> int:
    """Validate that a port number is in the valid TCP port range.

    Args:
        port: The port number to validate.

    Returns:
        The validated port number.

    Raises:
        ValueError: If the port is not in the range 1-65535.
    """
    if not (1 <= port <= 65535):
        raise ValueError(f"Platform port must be between 1 and 65535, got {port}")
    return port


def validate_host(host: str) -> str:
    """Validate that a host string is a valid hostname or IP address.

    Performs basic validation to ensure the host string is not empty
    and contains valid characters for a hostname or IP address.

    Args:
        host: The host string to validate.

    Returns:
        The validated host string.

    Raises:
        ValueError: If the host is empty or contains invalid characters.
    """
    if not host or host.isspace():
        raise ValueError("Platform host cannot be empty or whitespace")

    # Try parsing as IP address first
    try:
        ipaddress.ip_address(host)
        return host
    except ValueError:
        pass

    # If not an IP, validate as hostname
    # Hostname rules: alphanumeric, hyphens, dots, max 253 chars
    # Each label (between dots) max 63 chars, can't start/end with hyphen
    if len(host) > 253:
        raise ValueError(f"Platform host is too long (max 253 characters): {host}")

    # Basic hostname validation pattern
    # Allows alphanumeric, hyphens, dots, and underscores (for compatibility)
    hostname_pattern = r"^[a-zA-Z0-9]([a-zA-Z0-9\-_\.]*[a-zA-Z0-9])?$"
    if not re.match(hostname_pattern, host):
        raise ValueError(
            f"Invalid platform host format: {host}. "
            "Must be a valid hostname or IP address."
        )

    return host
