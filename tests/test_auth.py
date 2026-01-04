# Copyright (c) 2025 Itential, Inc
# GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

"""Unit tests for authentication provider construction."""

from types import SimpleNamespace
from unittest.mock import patch, MagicMock

import pytest

from itential_mcp.server import auth
from itential_mcp.core.exceptions import ConfigurationException


class TestBuildAuthProvider:
    """Tests for the build_auth_provider helper function."""

    def test_returns_none_when_auth_disabled(self):
        """Authentication provider is not created when type is none."""
        cfg = SimpleNamespace(auth={"type": "none"})

        provider = auth.build_auth_provider(cfg)

        assert provider is None

    @patch("itential_mcp.server.auth.JWTVerifier")
    def test_creates_jwt_provider_with_expected_arguments(self, mock_jwt_verifier):
        """JWT provider receives configuration from the Config object."""
        cfg = SimpleNamespace(
            auth={
                "type": "jwt",
                "public_key": "shared-secret",
                "algorithm": "HS256",
                "required_scopes": ["read:all", "write:all"],
                "audience": ["aud1", "aud2"],
            }
        )

        provider = auth.build_auth_provider(cfg)

        mock_jwt_verifier.assert_called_once()
        kwargs = mock_jwt_verifier.call_args.kwargs
        assert kwargs["public_key"] == "shared-secret"
        assert kwargs["algorithm"] == "HS256"
        assert kwargs["required_scopes"] == ["read:all", "write:all"]
        assert kwargs["audience"] == ["aud1", "aud2"]
        assert provider is mock_jwt_verifier.return_value

    def test_unsupported_auth_type_raises_configuration_exception(self):
        """Unsupported auth types raise ConfigurationException."""
        cfg = SimpleNamespace(auth={"type": "oauth"})

        with pytest.raises(ConfigurationException):
            auth.build_auth_provider(cfg)

    @patch(
        "itential_mcp.server.auth.JWTVerifier", side_effect=ValueError("invalid config")
    )
    def test_jwt_verifier_errors_are_wrapped(self, mock_jwt_verifier):
        """JWT verifier errors are wrapped in ConfigurationException."""
        cfg = SimpleNamespace(auth={"type": "jwt"})

        with pytest.raises(ConfigurationException) as exc:
            auth.build_auth_provider(cfg)

        assert "invalid config" in str(exc.value)
        mock_jwt_verifier.assert_called_once()

    def test_build_auth_provider_with_direct_auth_config(self):
        """Auth provider can be built with direct auth config (bypassing Config validation)."""
        cfg = SimpleNamespace(auth={"type": "jwt", "public_key": "test-key"})

        with patch("itential_mcp.server.auth.JWTVerifier") as mock_jwt_verifier:
            mock_provider = MagicMock()
            mock_jwt_verifier.return_value = mock_provider

            result = auth.build_auth_provider(cfg)

            assert result == mock_provider
            mock_jwt_verifier.assert_called_once_with(public_key="test-key")

    def test_auth_type_case_handling_in_auth_config(self):
        """Auth type is properly handled regardless of case in auth config dict."""
        cfg = SimpleNamespace(auth={"type": "JWT"})

        with patch("itential_mcp.server.auth.JWTVerifier") as mock_jwt_verifier:
            auth.build_auth_provider(cfg)
            mock_jwt_verifier.assert_called_once()

    def test_auth_type_whitespace_handling_in_auth_config(self):
        """Auth type whitespace is properly stripped in auth config dict."""
        cfg = SimpleNamespace(auth={"type": "  jwt  "})

        with patch("itential_mcp.server.auth.JWTVerifier") as mock_jwt_verifier:
            auth.build_auth_provider(cfg)
            mock_jwt_verifier.assert_called_once()

    @patch(
        "itential_mcp.server.auth.JWTVerifier", side_effect=Exception("general error")
    )
    def test_jwt_general_errors_are_wrapped(self, mock_jwt_verifier):
        """General JWT verifier errors are wrapped in ConfigurationException."""
        cfg = SimpleNamespace(auth={"type": "jwt"})

        with pytest.raises(ConfigurationException) as exc:
            auth.build_auth_provider(cfg)

        assert "Failed to initialize JWT authentication provider" in str(exc.value)
        assert "general error" in str(exc.value)
        mock_jwt_verifier.assert_called_once()

    @patch("itential_mcp.server.auth.JWTVerifier")
    def test_jwt_provider_excludes_type_field(self, mock_jwt_verifier):
        """JWT provider configuration excludes the 'type' field."""
        cfg = SimpleNamespace(
            auth={
                "type": "jwt",
                "public_key": "test-key",
                "algorithm": "HS256",
            }
        )

        auth.build_auth_provider(cfg)

        args, kwargs = mock_jwt_verifier.call_args
        assert "type" not in kwargs
        assert kwargs["public_key"] == "test-key"
        assert kwargs["algorithm"] == "HS256"


class TestJWTProviderBuilder:
    """Tests for the _build_jwt_provider helper function."""

    @patch("itential_mcp.server.auth.JWTVerifier")
    def test_builds_jwt_provider_with_minimal_config(self, mock_jwt_verifier):
        """JWT provider can be built with minimal configuration."""
        auth_config = {"type": "jwt"}
        mock_provider = MagicMock()
        mock_jwt_verifier.return_value = mock_provider

        result = auth._build_jwt_provider(auth_config)

        assert result == mock_provider
        mock_jwt_verifier.assert_called_once_with()

    @patch("itential_mcp.server.auth.JWTVerifier")
    def test_builds_jwt_provider_with_full_config(self, mock_jwt_verifier):
        """JWT provider receives all configuration parameters."""
        auth_config = {
            "type": "jwt",
            "public_key": "test-key",
            "algorithm": "HS256",
            "audience": ["aud1", "aud2"],
            "required_scopes": ["read", "write"],
        }
        mock_provider = MagicMock()
        mock_jwt_verifier.return_value = mock_provider

        result = auth._build_jwt_provider(auth_config)

        assert result == mock_provider
        mock_jwt_verifier.assert_called_once_with(
            public_key="test-key",
            algorithm="HS256",
            audience=["aud1", "aud2"],
            required_scopes=["read", "write"],
        )

    @patch(
        "itential_mcp.server.auth.JWTVerifier", side_effect=ValueError("invalid key")
    )
    def test_handles_jwt_value_error(self, mock_jwt_verifier):
        """JWT provider builder handles ValueError exceptions."""
        auth_config = {"type": "jwt"}

        with pytest.raises(ConfigurationException) as exc:
            auth._build_jwt_provider(auth_config)

        assert "invalid key" in str(exc.value)

    @patch(
        "itential_mcp.server.auth.JWTVerifier",
        side_effect=RuntimeError("runtime error"),
    )
    def test_handles_jwt_general_error(self, mock_jwt_verifier):
        """JWT provider builder handles general exceptions."""
        auth_config = {"type": "jwt"}

        with pytest.raises(ConfigurationException) as exc:
            auth._build_jwt_provider(auth_config)

        assert "Failed to initialize JWT authentication provider" in str(exc.value)
        assert "runtime error" in str(exc.value)


class TestSupportsTransport:
    """Tests for the supports_transport helper function."""

    def test_jwt_verifier_supports_all_transports(self):
        """JWT verifiers support all transport types."""
        from fastmcp.server.auth import JWTVerifier

        provider = MagicMock(spec=JWTVerifier)

        assert auth.supports_transport(provider, "stdio") is True
        assert auth.supports_transport(provider, "sse") is True
        assert auth.supports_transport(provider, "http") is True

    def test_remote_auth_provider_supports_http_only(self):
        """RemoteAuthProvider only supports HTTP-based transports."""
        from fastmcp.server.auth import RemoteAuthProvider

        provider = MagicMock(spec=RemoteAuthProvider)

        assert auth.supports_transport(provider, "stdio") is False
        assert auth.supports_transport(provider, "sse") is True
        assert auth.supports_transport(provider, "http") is True

    def test_oauth_proxy_supports_http_only(self):
        """OAuthProxy only supports HTTP-based transports."""
        from fastmcp.server.auth import OAuthProxy

        provider = MagicMock(spec=OAuthProxy)

        assert auth.supports_transport(provider, "stdio") is False
        assert auth.supports_transport(provider, "sse") is True
        assert auth.supports_transport(provider, "http") is True

    def test_oauth_provider_supports_http_only(self):
        """OAuthProvider only supports HTTP-based transports."""
        from fastmcp.server.auth import OAuthProvider

        provider = MagicMock(spec=OAuthProvider)

        assert auth.supports_transport(provider, "stdio") is False
        assert auth.supports_transport(provider, "sse") is True
        assert auth.supports_transport(provider, "http") is True

    def test_unknown_provider_defaults_to_compatible(self):
        """Unknown provider types default to being transport compatible."""
        unknown_provider = MagicMock()

        assert auth.supports_transport(unknown_provider, "stdio") is True
        assert auth.supports_transport(unknown_provider, "sse") is True
        assert auth.supports_transport(unknown_provider, "http") is True

    def test_supports_various_transport_strings(self):
        """Function works with different transport string variations."""
        from fastmcp.server.auth import JWTVerifier

        provider = MagicMock(spec=JWTVerifier)

        assert auth.supports_transport(provider, "STDIO") is True
        assert auth.supports_transport(provider, "Http") is True
        assert auth.supports_transport(provider, "SSE") is True


class TestOAuthProviderBuilder:
    """Tests for OAuth provider builder functions."""

    @patch("itential_mcp.server.auth.OAuthProvider")
    def test_build_oauth_provider_minimal_config(self, mock_oauth_provider):
        """OAuth provider can be built with minimal configuration."""
        auth_config = {
            "type": "oauth",
            "redirect_uri": "http://localhost:8000/auth/callback",
        }
        mock_provider = MagicMock()
        mock_oauth_provider.return_value = mock_provider

        result = auth._build_oauth_provider(auth_config)

        assert result == mock_provider
        mock_oauth_provider.assert_called_once_with(base_url="http://localhost:8000")

    def test_build_oauth_provider_missing_redirect_uri(self):
        """OAuth provider building fails without redirect_uri."""
        auth_config = {"type": "oauth"}

        with pytest.raises(ConfigurationException) as exc:
            auth._build_oauth_provider(auth_config)

        assert "OAuth server requires the following fields" in str(exc.value)
        assert "redirect_uri" in str(exc.value)

    @patch("itential_mcp.server.auth.OAuthProvider")
    def test_build_oauth_provider_with_scopes(self, mock_oauth_provider):
        """OAuth provider includes scopes when provided."""
        auth_config = {
            "type": "oauth",
            "redirect_uri": "http://localhost:8000/auth/callback",
            "scopes": ["read", "write"],
        }
        mock_provider = MagicMock()
        mock_oauth_provider.return_value = mock_provider

        auth._build_oauth_provider(auth_config)

        mock_oauth_provider.assert_called_once_with(
            base_url="http://localhost:8000", required_scopes=["read", "write"]
        )

    @patch(
        "itential_mcp.server.auth.OAuthProvider",
        side_effect=ValueError("invalid config"),
    )
    def test_build_oauth_provider_value_error(self, mock_oauth_provider):
        """OAuth provider builder handles ValueError exceptions."""
        auth_config = {
            "type": "oauth",
            "redirect_uri": "http://localhost:8000/auth/callback",
        }

        with pytest.raises(ConfigurationException) as exc:
            auth._build_oauth_provider(auth_config)

        assert "invalid config" in str(exc.value)

    @patch(
        "itential_mcp.server.auth.OAuthProvider",
        side_effect=RuntimeError("runtime error"),
    )
    def test_build_oauth_provider_general_error(self, mock_oauth_provider):
        """OAuth provider builder handles general exceptions."""
        auth_config = {
            "type": "oauth",
            "redirect_uri": "http://localhost:8000/auth/callback",
        }

        with pytest.raises(ConfigurationException) as exc:
            auth._build_oauth_provider(auth_config)

        assert "Failed to initialize OAuth authorization server" in str(exc.value)
        assert "runtime error" in str(exc.value)

    @patch("itential_mcp.server.auth.OAuthProxy")
    @patch("fastmcp.server.auth.StaticTokenVerifier")
    def test_build_oauth_proxy_provider_minimal_config(
        self, mock_static_verifier, mock_oauth_proxy
    ):
        """OAuth proxy provider can be built with minimal configuration."""
        auth_config = {
            "type": "oauth_proxy",
            "client_id": "test_client",
            "client_secret": "test_secret",
            "authorization_url": "https://auth.example.com/oauth/authorize",
            "token_url": "https://auth.example.com/oauth/token",
            "redirect_uri": "http://localhost:8000/auth/callback",
        }
        mock_verifier = MagicMock()
        mock_static_verifier.return_value = mock_verifier
        mock_provider = MagicMock()
        mock_oauth_proxy.return_value = mock_provider

        result = auth._build_oauth_proxy_provider(auth_config)

        assert result == mock_provider
        mock_oauth_proxy.assert_called_once_with(
            upstream_authorization_endpoint="https://auth.example.com/oauth/authorize",
            upstream_token_endpoint="https://auth.example.com/oauth/token",
            upstream_client_id="test_client",
            upstream_client_secret="test_secret",
            token_verifier=mock_verifier,
            base_url="http://localhost:8000",
        )

    def test_build_oauth_proxy_provider_missing_fields(self):
        """OAuth proxy provider building fails with missing required fields."""
        auth_config = {"type": "oauth_proxy", "client_id": "test_client"}

        with pytest.raises(ConfigurationException) as exc:
            auth._build_oauth_proxy_provider(auth_config)

        assert "OAuth proxy authentication requires the following fields" in str(
            exc.value
        )
        for field in [
            "client_secret",
            "authorization_url",
            "token_url",
            "redirect_uri",
        ]:
            assert field in str(exc.value)

    @patch("itential_mcp.server.auth.OAuthProxy")
    @patch("fastmcp.server.auth.StaticTokenVerifier")
    def test_build_oauth_proxy_provider_with_optional_fields(
        self, mock_static_verifier, mock_oauth_proxy
    ):
        """OAuth proxy provider includes optional fields when provided."""
        auth_config = {
            "type": "oauth_proxy",
            "client_id": "test_client",
            "client_secret": "test_secret",
            "authorization_url": "https://auth.example.com/oauth/authorize",
            "token_url": "https://auth.example.com/oauth/token",
            "redirect_uri": "http://localhost:8000/auth/callback",
            "userinfo_url": "https://auth.example.com/oauth/userinfo",
            "scopes": ["openid", "email"],
        }
        mock_verifier = MagicMock()
        mock_static_verifier.return_value = mock_verifier
        mock_provider = MagicMock()
        mock_oauth_proxy.return_value = mock_provider

        auth._build_oauth_proxy_provider(auth_config)

        args, kwargs = mock_oauth_proxy.call_args
        assert (
            kwargs["upstream_revocation_endpoint"]
            == "https://auth.example.com/oauth/userinfo"
        )
        assert kwargs["valid_scopes"] == ["openid", "email"]

    @patch("itential_mcp.server.auth.OAuthProxy")
    @patch("fastmcp.server.auth.StaticTokenVerifier", side_effect=ImportError)
    @patch("itential_mcp.server.auth.JWTVerifier")
    def test_build_oauth_proxy_provider_fallback_verifier(
        self, mock_jwt_verifier, mock_static_verifier, mock_oauth_proxy
    ):
        """OAuth proxy provider falls back to JWT verifier when StaticTokenVerifier unavailable."""
        auth_config = {
            "type": "oauth_proxy",
            "client_id": "test_client",
            "client_secret": "test_secret",
            "authorization_url": "https://auth.example.com/oauth/authorize",
            "token_url": "https://auth.example.com/oauth/token",
            "redirect_uri": "http://localhost:8000/auth/callback",
        }
        mock_jwt_instance = MagicMock()
        mock_jwt_verifier.return_value = mock_jwt_instance
        mock_provider = MagicMock()
        mock_oauth_proxy.return_value = mock_provider

        result = auth._build_oauth_proxy_provider(auth_config)

        assert result == mock_provider
        mock_jwt_verifier.assert_called_once_with()
        args, kwargs = mock_oauth_proxy.call_args
        assert kwargs["token_verifier"] == mock_jwt_instance


class TestGetProviderConfig:
    """Tests for the _get_provider_config helper function."""

    def test_google_provider_default_scopes(self):
        """Google provider gets default scopes when none specified."""
        auth_config = {}

        config = auth._get_provider_config("google", auth_config)

        assert config["scopes"] == ["openid", "email", "profile"]

    def test_azure_provider_default_scopes(self):
        """Azure provider gets default scopes when none specified."""
        auth_config = {}

        config = auth._get_provider_config("azure", auth_config)

        assert config["scopes"] == ["openid", "email", "profile"]

    def test_auth0_provider_default_scopes(self):
        """Auth0 provider gets default scopes when none specified."""
        auth_config = {}

        config = auth._get_provider_config("auth0", auth_config)

        assert config["scopes"] == ["openid", "email", "profile"]

    def test_github_provider_default_scopes(self):
        """GitHub provider gets default scopes when none specified."""
        auth_config = {}

        config = auth._get_provider_config("github", auth_config)

        assert config["scopes"] == ["user:email"]

    def test_okta_provider_default_scopes(self):
        """Okta provider gets default scopes when none specified."""
        auth_config = {}

        config = auth._get_provider_config("okta", auth_config)

        assert config["scopes"] == ["openid", "email", "profile"]

    def test_generic_provider_no_default_scopes(self):
        """Generic provider gets no default scopes."""
        auth_config = {}

        config = auth._get_provider_config("generic", auth_config)

        assert "scopes" not in config

    def test_provider_config_custom_scopes_override_defaults(self):
        """Custom scopes override default scopes for any provider."""
        auth_config = {"scopes": ["custom", "scope"]}

        config = auth._get_provider_config("google", auth_config)

        assert config["scopes"] == ["custom", "scope"]

    def test_provider_config_custom_redirect_uri(self):
        """Custom redirect URI is included in provider config."""
        auth_config = {"redirect_uri": "http://custom.example.com/callback"}

        config = auth._get_provider_config("google", auth_config)

        assert config["redirect_uri"] == "http://custom.example.com/callback"

    def test_provider_config_both_custom_fields(self):
        """Provider config includes both custom scopes and redirect URI."""
        auth_config = {
            "scopes": ["custom", "scope"],
            "redirect_uri": "http://custom.example.com/callback",
        }

        config = auth._get_provider_config("azure", auth_config)

        assert config["scopes"] == ["custom", "scope"]
        assert config["redirect_uri"] == "http://custom.example.com/callback"

    def test_unsupported_provider_type_raises_exception(self):
        """Unsupported provider type raises ConfigurationException."""
        auth_config = {}

        with pytest.raises(ConfigurationException) as exc:
            auth._get_provider_config("unsupported_provider", auth_config)

        assert "Unsupported OAuth provider type: unsupported_provider" in str(exc.value)
        assert "google, azure, auth0, github, okta, generic" in str(exc.value)
