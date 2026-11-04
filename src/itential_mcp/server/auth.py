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
from urllib.parse import urlsplit

from fastmcp.server.auth import (
    AuthProvider,
    JWTVerifier,
    RemoteAuthProvider,
    OAuthProxy,
    OAuthProvider,
)

from ..core import logging
from ..config import Config
from ..config.converters import auth_to_dict
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
    # Convert structured AuthConfig to legacy dictionary format for internal building.
    # This handles complex parsing like comma-separated strings to lists.
    auth_config = auth_to_dict(cfg.auth)
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


def _build_jwt_verifier(auth_config: dict[str, Any]) -> JWTVerifier:
    """Build a JWTVerifier instance from shared JWT-related configuration.

    Args:
        auth_config (dict[str, Any]): Authentication configuration dictionary.

    Returns:
        JWTVerifier: Configured JWT token verifier.

    Raises:
        ConfigurationException: If JWT verifier initialization fails.
    """
    jwt_kwargs = {}
    if auth_config.get("jwks_uri"):
        jwt_kwargs["jwks_uri"] = auth_config["jwks_uri"]
    if auth_config.get("public_key"):
        jwt_kwargs["public_key"] = auth_config["public_key"]
    if auth_config.get("issuer"):
        jwt_kwargs["issuer"] = auth_config["issuer"]
    if auth_config.get("audience"):
        jwt_kwargs["audience"] = auth_config["audience"]
    if auth_config.get("algorithm"):
        jwt_kwargs["algorithm"] = auth_config["algorithm"]
    if auth_config.get("required_scopes"):
        jwt_kwargs["required_scopes"] = auth_config["required_scopes"]

    try:
        return JWTVerifier(**jwt_kwargs)
    except ValueError as exc:
        raise ConfigurationException(str(exc)) from exc
    except Exception as exc:
        raise ConfigurationException(
            f"Failed to initialize JWT authentication provider: {exc}"
        ) from exc


def _build_jwt_provider(auth_config: dict[str, Any]) -> AuthProvider:
    """Build a JWT authentication provider.

    Args:
        auth_config (dict[str, Any]): Authentication configuration dictionary.

    Returns:
        AuthProvider: Configured JWT authentication provider.

    Raises:
        ConfigurationException: If JWT provider initialization fails.
    """
    provider = _build_jwt_verifier(auth_config)

    logging.info("Server authentication enabled using JWT provider")
    return provider


def _build_oauth_provider(auth_config: dict[str, Any]) -> AuthProvider:
    """Reject full OAuth 2.0 authorization server configuration.

    Full authorization server mode (``type=oauth``) is not currently
    supported. FastMCP's ``OAuthProvider`` authorization-server mode needs
    a user/credential store and Platform identity verification, which is
    tracked under the per-user "on behalf of" work. Until that exists,
    this configuration fails fast at startup instead of failing during a
    real authorization-code handshake.

    Args:
        auth_config (dict[str, Any]): Authentication configuration dictionary.

    Returns:
        AuthProvider: Never returns; always raises.

    Raises:
        ConfigurationException: Always raised. Full OAuth authorization
            server mode is not currently supported.
    """
    raise ConfigurationException(
        "Full OAuth authorization server mode ('oauth') is not currently "
        "supported (it requires a user/credential store and Platform identity "
        "verification). Use 'oauth_proxy' to delegate authentication to an "
        "upstream OAuth provider instead."
    )


def _build_oauth_proxy_provider(auth_config: dict[str, Any]) -> AuthProvider:
    """Build an OAuthProxy for upstream OAuth providers.

    Args:
        auth_config (dict[str, Any]): Authentication configuration dictionary.

    Returns:
        AuthProvider: Configured OAuth proxy authentication provider.

    Raises:
        ConfigurationException: If OAuth proxy provider initialization fails.
    """
    missing_fields = []
    if not auth_config.get("client_id"):
        missing_fields.append("client_id")
    if not auth_config.get("client_secret"):
        missing_fields.append("client_secret")
    if not auth_config.get("authorization_url"):
        missing_fields.append("authorization_url")
    if not auth_config.get("token_url"):
        missing_fields.append("token_url")
    if not auth_config.get("redirect_uri"):
        missing_fields.append("redirect_uri")

    if missing_fields:
        raise ConfigurationException(
            f"OAuth proxy authentication requires the following fields: {', '.join(missing_fields)}"
        )

    if not auth_config.get("jwks_uri") and not auth_config.get("public_key"):
        raise ConfigurationException(
            "OAuth proxy authentication requires a token verifier: "
            "set jwks_uri or public_key"
        )

    token_verifier = _build_jwt_verifier(auth_config)

    # Derive base_url and redirect_path from the configured redirect_uri using
    # proper URL parsing rather than a suffix-based heuristic. A naive
    # removesuffix("/auth/callback") is a no-op unless the redirect URI
    # literally ends in that path, silently folding the entire path into
    # base_url for any other callback path and producing a callback URL that
    # never matches what's registered with the upstream IdP.
    parsed_redirect_uri = urlsplit(auth_config["redirect_uri"])
    base_url = f"{parsed_redirect_uri.scheme}://{parsed_redirect_uri.netloc}"
    redirect_path = parsed_redirect_uri.path or "/auth/callback"

    oauth_kwargs = {
        "upstream_authorization_endpoint": auth_config["authorization_url"],
        "upstream_token_endpoint": auth_config["token_url"],
        "upstream_client_id": auth_config["client_id"],
        "upstream_client_secret": auth_config["client_secret"],
        "token_verifier": token_verifier,
        "base_url": base_url,
        "redirect_path": redirect_path,
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
