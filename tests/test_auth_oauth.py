# Copyright (c) 2025 Itential, Inc
# GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

import pytest
from types import SimpleNamespace
from unittest.mock import patch, MagicMock

from itential_mcp.server.auth import (
    build_auth_provider,
    _build_oauth_provider,
    _build_oauth_proxy_provider,
    _get_provider_config,
    supports_transport,
)
from itential_mcp.core.exceptions import ConfigurationException

from fastmcp.server.auth import (
    JWTVerifier,
    RemoteAuthProvider,
    OAuthProxy,
    OAuthProvider,
)


class TestOAuthConfiguration:
    """Test OAuth configuration parsing and validation."""

    def test_oauth_scopes_parsing_comma_separated(self):
        """Test OAuth scopes parsing with comma-separated values."""
        config = SimpleNamespace(auth={"scopes": ["openid", "email", "profile"]})
        auth_config = config.auth

        assert auth_config["scopes"] == ["openid", "email", "profile"]

    def test_oauth_scopes_parsing_space_separated(self):
        """Test OAuth scopes parsing with space-separated values."""
        config = SimpleNamespace(auth={"scopes": ["openid", "email", "profile"]})
        auth_config = config.auth

        assert auth_config["scopes"] == ["openid", "email", "profile"]

    def test_oauth_scopes_parsing_mixed_separators(self):
        """Test OAuth scopes parsing with mixed separators."""
        config = SimpleNamespace(
            auth={"scopes": ["openid", "email", "profile", "user:read"]}
        )
        auth_config = config.auth

        assert auth_config["scopes"] == ["openid", "email", "profile", "user:read"]

    def test_oauth_config_includes_all_fields(self):
        """Test that OAuth configuration includes all relevant fields."""
        config = SimpleNamespace(
            auth={
                "type": "oauth",
                "client_id": "test_client",
                "client_secret": "test_secret",
                "authorization_url": "https://auth.example.com/oauth/authorize",
                "token_url": "https://auth.example.com/oauth/token",
                "userinfo_url": "https://auth.example.com/oauth/userinfo",
                "scopes": ["openid", "email", "profile"],
                "redirect_uri": "http://localhost:8000/callback",
                "provider_type": "generic",
            }
        )
        auth_config = config.auth

        assert auth_config["type"] == "oauth"
        assert auth_config["client_id"] == "test_client"
        assert auth_config["client_secret"] == "test_secret"
        assert (
            auth_config["authorization_url"]
            == "https://auth.example.com/oauth/authorize"
        )
        assert auth_config["token_url"] == "https://auth.example.com/oauth/token"
        assert auth_config["userinfo_url"] == "https://auth.example.com/oauth/userinfo"
        assert auth_config["scopes"] == ["openid", "email", "profile"]
        assert auth_config["redirect_uri"] == "http://localhost:8000/callback"
        assert auth_config["provider_type"] == "generic"

    def test_oauth_config_excludes_none_values(self):
        """Test that OAuth configuration excludes None values."""
        config = SimpleNamespace(
            auth={
                "type": "oauth",
                "client_id": "test_client",
            }
        )
        auth_config = config.auth

        assert "client_secret" not in auth_config
        assert "authorization_url" not in auth_config
        assert "token_url" not in auth_config


class TestOAuthProviderBuilding:
    """Test OAuth provider building logic."""

    @patch("itential_mcp.server.auth.OAuthProvider")
    def test_build_oauth_provider_success(self, mock_oauth_provider):
        """Test successful OAuth provider building."""
        auth_config = {
            "type": "oauth",
            "redirect_uri": "http://localhost:8000/auth/callback",
        }

        mock_provider = MagicMock()
        mock_oauth_provider.return_value = mock_provider

        result = _build_oauth_provider(auth_config)

        assert result == mock_provider
        mock_oauth_provider.assert_called_once_with(base_url="http://localhost:8000")

    def test_build_oauth_provider_missing_required_fields(self):
        """Test OAuth provider building with missing required fields."""
        auth_config = {
            "type": "oauth"
            # Missing redirect_uri
        }

        with pytest.raises(ConfigurationException) as exc_info:
            _build_oauth_provider(auth_config)

        assert "requires the following fields" in str(exc_info.value)
        assert "redirect_uri" in str(exc_info.value)

    @patch("itential_mcp.server.auth.OAuthProvider")
    def test_build_oauth_provider_with_optional_fields(self, mock_oauth_provider):
        """Test OAuth provider building with optional fields."""
        auth_config = {
            "type": "oauth",
            "redirect_uri": "http://localhost:8000/auth/callback",
            "scopes": ["openid", "email"],
        }

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
        auth_config = {
            "type": "oauth_proxy",
            "client_id": "test_client",
            "client_secret": "test_secret",
            "authorization_url": "https://accounts.google.com/oauth/authorize",
            "token_url": "https://oauth2.googleapis.com/token",
            "redirect_uri": "http://localhost:8000/auth/callback",
        }

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
        auth_config = {
            "type": "oauth_proxy",
            "client_id": "test_client",
            # Missing client_secret, authorization_url, token_url, redirect_uri
        }

        with pytest.raises(ConfigurationException) as exc_info:
            _build_oauth_proxy_provider(auth_config)

        assert "requires the following fields" in str(exc_info.value)
        assert "client_secret" in str(exc_info.value)
        assert "authorization_url" in str(exc_info.value)
        assert "token_url" in str(exc_info.value)
        assert "redirect_uri" in str(exc_info.value)


class TestProviderConfiguration:
    """Test provider-specific configuration logic."""

    def test_google_provider_config(self):
        """Test Google provider configuration defaults."""
        auth_config = {}
        config = _get_provider_config("google", auth_config)

        assert config["scopes"] == ["openid", "email", "profile"]

    def test_azure_provider_config(self):
        """Test Azure provider configuration defaults."""
        auth_config = {}
        config = _get_provider_config("azure", auth_config)

        assert config["scopes"] == ["openid", "email", "profile"]

    def test_github_provider_config(self):
        """Test GitHub provider configuration defaults."""
        auth_config = {}
        config = _get_provider_config("github", auth_config)

        assert config["scopes"] == ["user:email"]

    def test_provider_config_custom_scopes(self):
        """Test provider configuration with custom scopes."""
        auth_config = {"scopes": ["custom", "scope"]}
        config = _get_provider_config("google", auth_config)

        assert config["scopes"] == ["custom", "scope"]

    def test_provider_config_custom_redirect_uri(self):
        """Test provider configuration with custom redirect URI."""
        auth_config = {"redirect_uri": "http://custom.example.com/callback"}
        config = _get_provider_config("google", auth_config)

        assert config["redirect_uri"] == "http://custom.example.com/callback"
        assert config["scopes"] == ["openid", "email", "profile"]

    def test_unsupported_provider_type(self):
        """Test unsupported provider type raises exception."""
        auth_config = {}

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
        config = SimpleNamespace(auth={"type": "none"})
        provider = build_auth_provider(config)
        assert provider is None

    def test_none_auth_provider(self):
        """Test building none auth provider."""
        config = SimpleNamespace(auth={"type": "none"})
        provider = build_auth_provider(config)
        assert provider is None

    @patch("itential_mcp.server.auth.JWTVerifier")
    def test_jwt_auth_provider(self, mock_jwt):
        """Test building JWT auth provider."""
        config = SimpleNamespace(auth={"type": "jwt", "public_key": "test_key"})

        mock_provider = MagicMock()
        mock_jwt.return_value = mock_provider

        provider = build_auth_provider(config)
        assert provider == mock_provider

    @patch("itential_mcp.server.auth.OAuthProvider")
    def test_oauth_auth_provider(self, mock_oauth_provider):
        """Test building OAuth auth provider."""
        config = SimpleNamespace(
            auth={
                "type": "oauth",
                "redirect_uri": "http://localhost:8000/auth/callback",
            }
        )

        mock_provider = MagicMock()
        mock_oauth_provider.return_value = mock_provider

        provider = build_auth_provider(config)
        assert provider == mock_provider

    @patch("itential_mcp.server.auth.OAuthProxy")
    @patch("fastmcp.server.auth.StaticTokenVerifier")
    def test_oauth_proxy_auth_provider(self, mock_token_verifier, mock_oauth_proxy):
        """Test building OAuth proxy auth provider."""
        config = SimpleNamespace(
            auth={
                "type": "oauth_proxy",
                "client_id": "test_client",
                "client_secret": "test_secret",
                "authorization_url": "https://accounts.google.com/oauth/authorize",
                "token_url": "https://oauth2.googleapis.com/token",
                "redirect_uri": "http://localhost:8000/auth/callback",
            }
        )

        mock_verifier_instance = MagicMock()
        mock_token_verifier.return_value = mock_verifier_instance

        mock_provider = MagicMock()
        mock_oauth_proxy.return_value = mock_provider

        provider = build_auth_provider(config)
        assert provider == mock_provider

    def test_unsupported_auth_type(self):
        """Test unsupported auth type raises exception."""
        config = SimpleNamespace(auth={"type": "unsupported"})

        with pytest.raises(ConfigurationException) as exc_info:
            build_auth_provider(config)

        assert "Unsupported authentication type" in str(exc_info.value)
