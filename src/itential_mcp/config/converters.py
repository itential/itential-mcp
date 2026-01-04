# Copyright (c) 2025 Itential, Inc
# GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

"""Configuration converters for backward compatibility.

This module provides functions to convert the new structured configuration
format into the legacy dictionary-based format used by existing code.
This maintains backward compatibility during the migration period.
"""

from __future__ import annotations

from typing import Any

from .models import ServerConfig, AuthConfig, PlatformConfig


def _split_comma_separated(value: str | None) -> set[str]:
    """Convert comma-separated string to a set of trimmed strings.

    Args:
        value: Comma-separated string to convert, or None.

    Returns:
        Set of trimmed string elements, or empty set if value is None.

    Raises:
        None.
    """
    if value is None:
        return set()

    items = set()
    for ele in value.split(","):
        stripped = ele.strip()
        if stripped:
            items.add(stripped)
    return items


def _split_to_list(value: str | None) -> list[str]:
    """Convert comma-separated string to a list of trimmed values.

    Args:
        value: Comma separated string value to parse, or None.

    Returns:
        List of trimmed values, excluding empty entries.
        Returns empty list if value is None.

    Raises:
        None.
    """
    if value is None:
        return []
    return [item.strip() for item in value.split(",") if item.strip()]


def server_to_dict(server_config: ServerConfig) -> dict[str, Any]:
    """Convert ServerConfig to legacy dictionary format.

    Args:
        server_config: ServerConfig instance to convert.

    Returns:
        Dictionary with server configuration in legacy format.

    Raises:
        None.
    """
    return {
        "transport": server_config.transport,
        "host": server_config.host,
        "port": server_config.port,
        "certificate_file": server_config.certificate_file or None,
        "private_key_file": server_config.private_key_file or None,
        "path": server_config.path,
        "tools_path": server_config.tools_path,
        "log_level": server_config.log_level,
        "keepalive_interval": server_config.keepalive_interval,
        "include_tags": _split_comma_separated(server_config.include_tags)
        if server_config.include_tags
        else None,
        "exclude_tags": _split_comma_separated(server_config.exclude_tags)
        if server_config.exclude_tags
        else None,
    }


def auth_to_dict(auth_config: AuthConfig) -> dict[str, Any]:
    """Convert AuthConfig to legacy dictionary format.

    Args:
        auth_config: AuthConfig instance to convert.

    Returns:
        Dictionary with auth configuration in legacy format.
        Keys with None/empty values are filtered out.

    Raises:
        None.
    """
    auth_type = (auth_config.type or "none").strip().lower()

    audience: str | list[str] | None = None
    if auth_config.audience:
        values = _split_to_list(auth_config.audience)
        if len(values) == 1:
            audience = values[0]
        elif values:
            audience = values

    required_scopes = (
        _split_to_list(auth_config.required_scopes)
        if auth_config.required_scopes
        else None
    )

    # Handle OAuth scopes parsing
    oauth_scopes = None
    if auth_config.oauth_scopes:
        # Support both space and comma separated scopes
        scopes_str = auth_config.oauth_scopes.replace(",", " ")
        oauth_scopes = [s.strip() for s in scopes_str.split() if s.strip()]

    data: dict[str, Any] = {
        "type": auth_type,
        # JWT-specific fields
        "jwks_uri": auth_config.jwks_uri or None,
        "public_key": auth_config.public_key or None,
        "issuer": auth_config.issuer or None,
        "audience": audience,
        "algorithm": auth_config.algorithm or None,
        "required_scopes": required_scopes,
        # OAuth-specific fields
        "client_id": auth_config.oauth_client_id or None,
        "client_secret": auth_config.oauth_client_secret or None,
        "authorization_url": auth_config.oauth_authorization_url or None,
        "token_url": auth_config.oauth_token_url or None,
        "userinfo_url": auth_config.oauth_userinfo_url or None,
        "scopes": oauth_scopes,
        "redirect_uri": auth_config.oauth_redirect_uri or None,
        "provider_type": auth_config.oauth_provider_type or None,
    }

    return {k: v for k, v in data.items() if v not in (None, "", [])}


def platform_to_dict(platform_config: PlatformConfig) -> dict[str, Any]:
    """Convert PlatformConfig to legacy dictionary format.

    Args:
        platform_config: PlatformConfig instance to convert.

    Returns:
        Dictionary with platform configuration in legacy format.

    Raises:
        None.
    """
    return {
        "host": platform_config.host,
        "port": platform_config.port,
        "use_tls": not platform_config.disable_tls,
        "verify": not platform_config.disable_verify,
        "user": platform_config.user,
        "password": platform_config.password,
        "client_id": None
        if platform_config.client_id == ""
        else platform_config.client_id,
        "client_secret": None
        if platform_config.client_secret == ""
        else platform_config.client_secret,
        "timeout": platform_config.timeout,
        "ttl": platform_config.ttl,
    }
