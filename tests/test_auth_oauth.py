# Copyright (c) 2025 Itential, Inc
# GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import annotations

import pytest
from unittest.mock import patch, MagicMock

from itential_mcp.server.auth import (
    build_auth_provider,
    _build_oauth_provider,
    _build_oauth_proxy_provider,
    _get_provider_config,
    supports_transport,
)
from itential_mcp.config.models import AuthConfig, Config
from itential_mcp.core.exceptions import ConfigurationException

from fastmcp.server.auth import (
    JWTVerifier,
    RemoteAuthProvider,
    OAuthProxy,
    OAuthProvider,
)


def make_auth_config(**kwargs) -> AuthConfig:
    """Create an AuthConfig instance with sensible defaults for testing.

    Args:
        **kwargs: Override any AuthConfig field.

    Returns:
        AuthConfig: Configured auth config instance.
    """
    defaults = {
        "type": "none",
        "jwks_uri": None,
        "public_key": None,
        "issuer": None,
        "audience": None,
        "algorithm": None,
        "required_scopes": None,
        "oauth_client_id": None,
        "oauth_client_secret": None,
        "oauth_authorization_url": None,
        "oauth_token_url": None,
        "oauth_userinfo_url": None,
        "oauth_scopes": None,
        "oauth_redirect_uri": None,
        "oauth_provider_type": None,
    }
    defaults.update(kwargs)
    return AuthConfig(**defaults)


class TestOAuthConfiguration:
    """Test OAuth configuration parsing and validation."""

    def test_oauth_scopes_parsing_comma_separated(self):
        """Test OAuth scopes parsing with comma-separated values."""
        auth_config = AuthConfig(oauth_scopes="openid, email, profile")

        # Internal converter logic for scopes
        from itential_mcp.config.converters import auth_to_dict

        data = auth_to_dict(auth_config)
        assert data["scopes"] == ["openid", "email", "profile"]

    def test_oauth_scopes_parsing_space_separated(self):
        """Test OAuth scopes parsing with space-separated values."""
        auth_config = AuthConfig(oauth_scopes="openid email profile")

        from itential_mcp.config.converters import auth_to_dict

        data = auth_to_dict(auth_config)
        assert data["scopes"] == ["openid", "email", "profile"]

    def test_oauth_config_includes_all_fields(self):
        """Test that OAuth configuration includes all relevant fields."""
        auth_config = AuthConfig(
            type="oauth",
            oauth_client_id="test_client",
            oauth_client_secret="test_secret",
            oauth_authorization_url="https://auth.example.com/oauth/authorize",
            oauth_token_url="https://auth.example.com/oauth/token",
            oauth_userinfo_url="https://auth.example.com/oauth/userinfo",
            oauth_scopes="openid, email, profile",
            oauth_redirect_uri="http://localhost:8000/callback",
            oauth_provider_type="generic",
        )

        from itential_mcp.config.converters import auth_to_dict

        data = auth_to_dict(auth_config)

        assert data["type"] == "oauth"
        assert data["client_id"] == "test_client"
        assert data["client_secret"] == "test_secret"
        assert data["authorization_url"] == "https://auth.example.com/oauth/authorize"
        assert data["token_url"] == "https://auth.example.com/oauth/token"
        assert data["userinfo_url"] == "https://auth.example.com/oauth/userinfo"
        assert data["scopes"] == ["openid", "email", "profile"]
        assert data["redirect_uri"] == "http://localhost:8000/callback"
        assert data["provider_type"] == "generic"


class TestOAuthProviderBuilding:
    """Test OAuth provider building logic."""

    @patch("itential_mcp.server.auth.OAuthProvider")
    def test_build_oauth_provider_success(self, mock_oauth_provider):
        """Test successful OAuth provider building."""
        from itential_mcp.config.converters import auth_to_dict
        auth_config = auth_to_dict(make_auth_config(
            type="oauth",
            oauth_redirect_uri="http://localhost:8000/auth/callback",
        ))

        mock_provider = MagicMock()
        mock_oauth_provider.return_value = mock_provider

        result = _build_oauth_provider(auth_config)

        assert result == mock_provider
        mock_oauth_provider.assert_called_once_with(base_url="http://localhost:8000")

    def test_build_oauth_provider_missing_required_fields(self):
        """Test OAuth provider building with missing required fields."""
        from itential_mcp.config.converters import auth_to_dict
        auth_config = auth_to_dict(make_auth_config(type="oauth"))

        with pytest.raises(ConfigurationException) as exc_info:
            _build_oauth_provider(auth_config)

        assert "requires the following fields" in str(exc_info.value)
        assert "redirect_uri" in str(exc_info.value)

    @patch("itential_mcp.server.auth.OAuthProvider")
    def test_build_oauth_provider_with_optional_fields(self, mock_oauth_provider):
        """Test OAuth provider building with optional fields."""
        from itential_mcp.config.converters import auth_to_dict
        auth_config = auth_to_dict(make_auth_config(
            type="oauth",
            oauth_redirect_uri="http://localhost:8000/auth/callback",
            oauth_scopes="openid,email",
        ))

        mock_provider = MagicMock()
        mock_oauth_provider.return_value = mock_provider

        _build_oauth_provider(auth_config)

        mock_oauth_provider.assert_called_once_with(
            base_url="http://localhost:8000", required_scopes=["openid", "email"]
        )

    @patch("itential_mcp.server.auth.OAuthProxy")
    @patch("fastmcp.server.auth.StaticTokenVerifier")
    def test_build_oauth_proxy_provider_success(
        self, mock_token_verifier, mock_oauth_proxy
    ):
        """Test successful OAuth proxy provider building."""
        from itential_mcp.config.converters import auth_to_dict
        auth_config = auth_to_dict(make_auth_config(
            type="oauth_proxy",
            oauth_client_id="test_client",
            oauth_client_secret="test_secret",
            oauth_authorization_url="https://accounts.google.com/oauth/authorize",
            oauth_token_url="https://oauth2.googleapis.com/token",
            oauth_redirect_uri="http://localhost:8000/auth/callback",
        ))

        mock_verifier_instance = MagicMock()
        mock_token_verifier.return_value = mock_verifier_instance

        mock_provider = MagicMock()
        mock_oauth_proxy.return_value = mock_provider

        result = _build_oauth_proxy_provider(auth_config)

        assert result == mock_provider
        mock_oauth_proxy.assert_called_once_with(
            upstream_authorization_endpoint="https://accounts.google.com/oauth/authorize",
            upstream_token_endpoint="https://oauth2.googleapis.com/token",
            upstream_client_id="test_client",
            upstream_client_secret="test_secret",
            token_verifier=mock_verifier_instance,
            base_url="http://localhost:8000",
        )

    def test_build_oauth_proxy_provider_missing_fields(self):
        """Test OAuth proxy provider building with missing required fields."""
        from itential_mcp.config.converters import auth_to_dict
        auth_config = auth_to_dict(make_auth_config(
            type="oauth_proxy",
            oauth_client_id="test_client",
        ))

        with pytest.raises(ConfigurationException) as exc_info:
            _build_oauth_proxy_provider(auth_config)

        assert "OAuth proxy authentication requires the following fields" in str(exc_info.value)
        assert "client_secret" in str(exc_info.value)
        assert "authorization_url" in str(exc_info.value)
        assert "token_url" in str(exc_info.value)
        assert "redirect_uri" in str(exc_info.value)


class TestProviderConfiguration:
    """Test provider-specific configuration logic."""

    def test_google_provider_config(self):
        """Test Google provider configuration defaults."""
        from itential_mcp.config.converters import auth_to_dict
        auth_config = auth_to_dict(make_auth_config())
        config = _get_provider_config("google", auth_config)

        assert config["scopes"] == ["openid", "email", "profile"]

    def test_azure_provider_config(self):
        """Test Azure provider configuration defaults."""
        from itential_mcp.config.converters import auth_to_dict
        auth_config = auth_to_dict(make_auth_config())
        config = _get_provider_config("azure", auth_config)

        assert config["scopes"] == ["openid", "email", "profile"]

    def test_github_provider_config(self):
        """Test GitHub provider configuration defaults."""
        from itential_mcp.config.converters import auth_to_dict
        auth_config = auth_to_dict(make_auth_config())
        config = _get_provider_config("github", auth_config)

        assert config["scopes"] == ["user:email"]

    def test_provider_config_custom_scopes(self):
        """Test provider configuration with custom scopes."""
        from itential_mcp.config.converters import auth_to_dict
        auth_config = auth_to_dict(make_auth_config(oauth_scopes="custom,scope"))
        config = _get_provider_config("google", auth_config)

        assert config["scopes"] == ["custom", "scope"]

    def test_provider_config_custom_redirect_uri(self):
        """Test provider configuration with custom redirect URI."""
        from itential_mcp.config.converters import auth_to_dict
        auth_config = auth_to_dict(make_auth_config(
            oauth_redirect_uri="http://custom.example.com/callback"
        ))
        config = _get_provider_config("google", auth_config)

        assert config["redirect_uri"] == "http://custom.example.com/callback"
        assert config["scopes"] == ["openid", "email", "profile"]

    def test_unsupported_provider_type(self):
        """Test unsupported provider type raises exception."""
        from itential_mcp.config.converters import auth_to_dict
        auth_config = auth_to_dict(make_auth_config())

        with pytest.raises(ConfigurationException) as exc_info:
            _get_provider_config("unsupported", auth_config)

        assert "Unsupported OAuth provider type" in str(exc_info.value)
        assert "unsupported" in str(exc_info.value)


class TestTransportCompatibility:
    """Test transport compatibility validation."""

    def test_jwt_supports_all_transports(self):
        """Test that JWT providers support all transport types."""
        jwt_provider = MagicMock(spec=JWTVerifier)

        assert supports_transport(jwt_provider, "stdio")
        assert supports_transport(jwt_provider, "sse")
        assert supports_transport(jwt_provider, "http")

    def test_oauth_providers_support_http_transports_only(self):
        """Test that OAuth providers only support HTTP-based transports."""
        remote_provider = MagicMock(spec=RemoteAuthProvider)
        oauth_proxy = MagicMock(spec=OAuthProxy)
        oauth_provider = MagicMock(spec=OAuthProvider)

        for provider in [remote_provider, oauth_proxy, oauth_provider]:
            assert not supports_transport(provider, "stdio")
            assert supports_transport(provider, "sse")
            assert supports_transport(provider, "http")


class TestFullAuthProviderFactory:
    """Test the complete auth provider factory."""

    def test_no_auth_provider(self):
        """Test building no auth provider."""
        config = MagicMock(spec=Config)
        config.auth = AuthConfig(type="none")
        provider = build_auth_provider(config)
        assert provider is None

    def test_none_auth_provider(self):
        """Test building none auth provider."""
        config = MagicMock(spec=Config)
        config.auth = AuthConfig(type="none")
        provider = build_auth_provider(config)
        assert provider is None

    @patch("itential_mcp.server.auth.JWTVerifier")
    def test_jwt_auth_provider(self, mock_jwt):
        """Test building JWT auth provider."""
        config = MagicMock(spec=Config)
        config.auth = AuthConfig(type="jwt", public_key="test_key")

        mock_provider = MagicMock()
        mock_jwt.return_value = mock_provider

        provider = build_auth_provider(config)
        assert provider == mock_provider

    @patch("itential_mcp.server.auth.OAuthProvider")
    def test_oauth_auth_provider(self, mock_oauth_provider):
        """Test building OAuth auth provider."""
        config = MagicMock(spec=Config)
        config.auth = AuthConfig(
            type="oauth",
            oauth_redirect_uri="http://localhost:8000/auth/callback",
        )

        mock_provider = MagicMock()
        mock_oauth_provider.return_value = mock_provider

        provider = build_auth_provider(config)
        assert provider == mock_provider

    @patch("itential_mcp.server.auth.OAuthProxy")
    @patch("fastmcp.server.auth.StaticTokenVerifier")
    def test_oauth_proxy_auth_provider(self, mock_token_verifier, mock_oauth_proxy):
        """Test building OAuth proxy auth provider."""
        config = MagicMock(spec=Config)
        config.auth = AuthConfig(
            type="oauth_proxy",
            oauth_client_id="test_client",
            oauth_client_secret="test_secret",
            oauth_authorization_url="https://accounts.google.com/oauth/authorize",
            oauth_token_url="https://oauth2.googleapis.com/token",
            oauth_redirect_uri="http://localhost:8000/auth/callback",
        )

        mock_verifier_instance = MagicMock()
        mock_token_verifier.return_value = mock_verifier_instance

        mock_provider = MagicMock()
        mock_oauth_proxy.return_value = mock_provider

        provider = build_auth_provider(config)
        assert provider == mock_provider

    def test_unsupported_auth_type(self):
        """Test unsupported auth type raises exception."""
        config = MagicMock(spec=Config)
        # We need a way to pass an unsupported type for testing, but Literal enforces it.
        # Use patch or bypass validation for this test case if needed, or if it raises on initialization.
        with patch.object(AuthConfig, "type", "unsupported"):
            # This might not work if it's a frozen dataclass.
            # Let's mock the whole AuthConfig object for this specific case.
            mock_auth = MagicMock(spec=AuthConfig)
            mock_auth.type = "unsupported"
            config.auth = mock_auth

            with pytest.raises(ConfigurationException) as exc_info:
                build_auth_provider(config)

            assert "Unsupported authentication type" in str(exc_info.value)
