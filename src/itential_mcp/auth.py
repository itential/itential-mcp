"""Authentication provider factory for the Itential MCP server.

This module converts application configuration into FastMCP authentication
providers.  Support currently includes JWT token verification with optional
JWKS lookups and is designed to be extended with additional providers in
the future.
"""

from fastmcp.server.auth.auth import AuthProvider
from fastmcp.server.auth.providers.jwt import JWTVerifier

from .core import logging
from .config import Config
from .core.exceptions import ConfigurationException


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

    if auth_type != "jwt":
        raise ConfigurationException(
            f"Unsupported authentication type configured: {auth_type}"
        )

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
