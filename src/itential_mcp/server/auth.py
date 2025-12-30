# Copyright (c) 2025 Itential, Inc
# GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

"""Authentication provider factory for the Itential MCP server.

This module converts application configuration into FastMCP authentication
providers. Support includes JWT token verification with optional JWKS lookups,
OAuth 2.0 flows via RemoteAuthProvider and OAuthProxy, and is designed to be
extended with additional providers in the future.
"""

from __future__ import annotations

from typing import Any

from fastmcp.server.auth import (
    AuthProvider,
    JWTVerifier,
    RemoteAuthProvider,
    OAuthProxy,
    OAuthProvider,
)

from ..core import logging
from ..config import Config
from ..core.exceptions import ConfigurationException


def build_auth_provider(cfg: Config) -> AuthProvider | None:
    """Create the configured authentication provider instance.

    Args:
        cfg (Config): Application configuration that includes authentication
            settings.

    Returns:
        AuthProvider | None: Configured authentication provider or None when
            authentication is disabled.

    Raises:
        ConfigurationException: Raised when the authentication configuration
            is invalid or references an unsupported provider type.
    """
    auth_config = cfg.auth
    auth_type = (auth_config.get("type") or "none").strip().lower()

    if auth_type in {"", "none"}:
        logging.debug("Server authentication disabled; no provider constructed")
        return None

    if auth_type == "jwt":
        return _build_jwt_provider(auth_config)
    elif auth_type == "oauth":
        return _build_oauth_provider(auth_config)
    elif auth_type == "oauth_proxy":
        return _build_oauth_proxy_provider(auth_config)
    else:
        raise ConfigurationException(
            f"Unsupported authentication type configured: {auth_type}"
        )


def _build_jwt_provider(auth_config: dict[str, Any]) -> AuthProvider:
    """Build a JWT authentication provider.

    Args:
        auth_config (dict[str, Any]): Authentication configuration dictionary.

    Returns:
        AuthProvider: Configured JWT authentication provider.

    Raises:
        ConfigurationException: If JWT provider initialization fails.
    """
    jwt_kwargs = {key: value for key, value in auth_config.items() if key != "type"}

    try:
        provider = JWTVerifier(**jwt_kwargs)
    except ValueError as exc:
        raise ConfigurationException(str(exc)) from exc
    except Exception as exc:
        raise ConfigurationException(
            f"Failed to initialize JWT authentication provider: {exc}"
        ) from exc

    logging.info("Server authentication enabled using JWT provider")
    return provider


def _build_oauth_provider(auth_config: dict[str, Any]) -> AuthProvider:
    """Build a full OAuth 2.0 authorization server.

    Args:
        auth_config (dict[str, Any]): Authentication configuration dictionary.

    Returns:
        AuthProvider: Configured OAuth authorization server provider.

    Raises:
        ConfigurationException: If OAuth provider initialization fails.
    """
    required_fields = ["redirect_uri"]
    missing_fields = [field for field in required_fields if not auth_config.get(field)]

    if missing_fields:
        raise ConfigurationException(
            f"OAuth server requires the following fields: {', '.join(missing_fields)}"
        )

    oauth_kwargs = {
        "base_url": auth_config["redirect_uri"].rstrip("/auth/callback"),
    }

    # Add optional parameters
    if auth_config.get("scopes"):
        oauth_kwargs["required_scopes"] = auth_config["scopes"]

    try:
        provider = OAuthProvider(**oauth_kwargs)
    except ValueError as exc:
        raise ConfigurationException(str(exc)) from exc
    except Exception as exc:
        raise ConfigurationException(
            f"Failed to initialize OAuth authorization server: {exc}"
        ) from exc

    logging.info("Server authentication enabled using OAuth authorization server")
    return provider


def _build_oauth_proxy_provider(auth_config: dict[str, Any]) -> AuthProvider:
    """Build an OAuthProxy for upstream OAuth providers.

    Args:
        auth_config (dict[str, Any]): Authentication configuration dictionary.

    Returns:
        AuthProvider: Configured OAuth proxy authentication provider.

    Raises:
        ConfigurationException: If OAuth proxy provider initialization fails.
    """
    required_fields = [
        "client_id",
        "client_secret",
        "authorization_url",
        "token_url",
        "redirect_uri",
    ]
    missing_fields = [field for field in required_fields if not auth_config.get(field)]

    if missing_fields:
        raise ConfigurationException(
            f"OAuth proxy authentication requires the following fields: {', '.join(missing_fields)}"
        )

    # Create a token verifier (can use JWTVerifier or StaticTokenVerifier)
    try:
        from fastmcp.server.auth import StaticTokenVerifier

        token_verifier = StaticTokenVerifier()  # Basic token verifier
    except ImportError:
        # Fallback to JWT verifier if StaticTokenVerifier not available
        token_verifier = JWTVerifier()

    base_url = auth_config["redirect_uri"].rstrip("/auth/callback")

    oauth_kwargs = {
        "upstream_authorization_endpoint": auth_config["authorization_url"],
        "upstream_token_endpoint": auth_config["token_url"],
        "upstream_client_id": auth_config["client_id"],
        "upstream_client_secret": auth_config["client_secret"],
        "token_verifier": token_verifier,
        "base_url": base_url,
    }

    # Add optional parameters
    if auth_config.get("userinfo_url"):
        oauth_kwargs["upstream_revocation_endpoint"] = auth_config["userinfo_url"]
    if auth_config.get("scopes"):
        oauth_kwargs["valid_scopes"] = auth_config["scopes"]

    try:
        provider = OAuthProxy(**oauth_kwargs)
    except ValueError as exc:
        raise ConfigurationException(str(exc)) from exc
    except Exception as exc:
        raise ConfigurationException(
            f"Failed to initialize OAuth proxy authentication provider: {exc}"
        ) from exc

    logging.info("Server authentication enabled using OAuth proxy provider")
    return provider


def _get_provider_config(
    provider_type: str, auth_config: dict[str, Any]
) -> dict[str, Any]:
    """Get provider-specific OAuth configuration.

    Args:
        provider_type (str): The OAuth provider type (google, azure, etc.)
        auth_config (dict[str, Any]): Full authentication configuration.

    Returns:
        dict[str, Any]: Provider-specific configuration parameters.

    Raises:
        ConfigurationException: If provider type is not supported.
    """
    config = {}

    # Add custom scopes if specified
    if auth_config.get("scopes"):
        config["scopes"] = auth_config["scopes"]

    # Add custom redirect URI if specified
    if auth_config.get("redirect_uri"):
        config["redirect_uri"] = auth_config["redirect_uri"]

    # Provider-specific defaults and overrides
    if provider_type == "google":
        if not auth_config.get("scopes"):
            config["scopes"] = ["openid", "email", "profile"]
    elif provider_type == "azure":
        if not auth_config.get("scopes"):
            config["scopes"] = ["openid", "email", "profile"]
    elif provider_type == "auth0":
        if not auth_config.get("scopes"):
            config["scopes"] = ["openid", "email", "profile"]
    elif provider_type == "github":
        if not auth_config.get("scopes"):
            config["scopes"] = ["user:email"]
    elif provider_type == "okta":
        if not auth_config.get("scopes"):
            config["scopes"] = ["openid", "email", "profile"]
    elif provider_type == "generic":
        # Generic provider requires explicit configuration
        pass
    else:
        raise ConfigurationException(
            f"Unsupported OAuth provider type: {provider_type}. "
            f"Supported types: google, azure, auth0, github, okta, generic"
        )

    return config


def supports_transport(auth_provider: AuthProvider, transport: str) -> bool:
    """Check if an auth provider supports a given transport.

    Args:
        auth_provider (AuthProvider): The authentication provider to check.
        transport (str): The transport type (stdio, sse, http).

    Returns:
        bool: True if the provider supports the transport, False otherwise.
    """
    # OAuth providers only work with HTTP-based transports
    if isinstance(auth_provider, (RemoteAuthProvider, OAuthProxy, OAuthProvider)):
        return transport in ("sse", "http")

    # JWT can work with any transport
    if isinstance(auth_provider, JWTVerifier):
        return True

    # Default: assume compatibility
    return True
