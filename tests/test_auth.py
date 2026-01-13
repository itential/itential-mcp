# Copyright (c) 2025 Itential, Inc
# GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

"""Unit tests for authentication provider construction."""

from unittest.mock import patch, MagicMock

import pytest

from itential_mcp.server import auth
from itential_mcp.config.models import AuthConfig, Config
from itential_mcp.core.exceptions import ConfigurationException


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


class TestBuildAuthProvider:
    """Tests for the build_auth_provider helper function."""

    def test_returns_none_when_auth_disabled(self):
        """Authentication provider is not created when type is none."""
        cfg = MagicMock(spec=Config)
        cfg.auth = AuthConfig(type="none")

        provider = auth.build_auth_provider(cfg)

        assert provider is None

    @patch("itential_mcp.server.auth.JWTVerifier")
    def test_creates_jwt_provider_with_expected_arguments(self, mock_jwt_verifier):
        """JWT provider receives configuration from the Config object."""
        cfg = MagicMock(spec=Config)
        cfg.auth = AuthConfig(
            type="jwt",
            public_key="shared-secret",
            algorithm="HS256",
            required_scopes="read:all, write:all",
            audience="aud1, aud2",
        )

        provider = auth.build_auth_provider(cfg)

        mock_jwt_verifier.assert_called_once()
        kwargs = mock_jwt_verifier.call_args.kwargs
        assert kwargs["public_key"] == "shared-secret"
        assert kwargs["algorithm"] == "HS256"
        # Since we use auth_to_dict which parses these into lists
        assert kwargs["required_scopes"] == ["read:all", "write:all"]
        assert kwargs["audience"] == ["aud1", "aud2"]
        assert provider is mock_jwt_verifier.return_value

    def test_unsupported_auth_type_raises_configuration_exception(self):
        """Unsupported auth types raise ConfigurationException."""
        cfg = MagicMock(spec=Config)
        # AuthConfig type is a Literal, so we mock it to test unsupported types
        mock_auth = MagicMock(spec=AuthConfig)
        mock_auth.type = "oauth-unknown"
        cfg.auth = mock_auth

        with pytest.raises(ConfigurationException) as exc:
            auth.build_auth_provider(cfg)

        assert "Unsupported authentication type" in str(exc.value)

    @patch(
        "itential_mcp.server.auth.JWTVerifier", side_effect=ValueError("invalid config")
    )
    def test_jwt_verifier_errors_are_wrapped(self, mock_jwt_verifier):
        """JWT verifier errors are wrapped in ConfigurationException."""
        cfg = MagicMock(spec=Config)
        cfg.auth = AuthConfig(type="jwt")

        with pytest.raises(ConfigurationException) as exc:
            auth.build_auth_provider(cfg)

        assert "invalid config" in str(exc.value)
        mock_jwt_verifier.assert_called_once()

    def test_build_auth_provider_with_direct_auth_config(self):
        """Auth provider can be built with direct auth config (bypassing Config validation)."""
        cfg = MagicMock(spec=Config)
        cfg.auth = AuthConfig(type="jwt", public_key="test-key")

        with patch("itential_mcp.server.auth.JWTVerifier") as mock_jwt_verifier:
            mock_provider = MagicMock()
            mock_jwt_verifier.return_value = mock_provider

            result = auth.build_auth_provider(cfg)

            assert result == mock_provider
            mock_jwt_verifier.assert_called_once_with(public_key="test-key")

    def test_auth_type_case_handling_in_auth_config(self):
        """Auth type is properly handled regardless of case in auth config dict."""
        cfg = MagicMock(spec=Config)
        # Use MagicMock to bypass Literal validation in constructor if needed,
        # or just pass it if converter handles it.
        mock_auth = MagicMock(spec=AuthConfig)
        mock_auth.type = "JWT"
        cfg.auth = mock_auth

        with patch("itential_mcp.server.auth.JWTVerifier") as mock_jwt_verifier:
            auth.build_auth_provider(cfg)
            mock_jwt_verifier.assert_called_once()

    def test_auth_type_whitespace_handling_in_auth_config(self):
        """Auth type whitespace is properly stripped in auth config dict."""
        cfg = MagicMock(spec=Config)
        mock_auth = MagicMock(spec=AuthConfig)
        mock_auth.type = "  jwt  "
        cfg.auth = mock_auth

        with patch("itential_mcp.server.auth.JWTVerifier") as mock_jwt_verifier:
            auth.build_auth_provider(cfg)
            mock_jwt_verifier.assert_called_once()

    @patch(
        "itential_mcp.server.auth.JWTVerifier", side_effect=Exception("general error")
    )
    def test_jwt_general_errors_are_wrapped(self, mock_jwt_verifier):
        """General JWT ver errors are wrapped in ConfigurationException."""
        cfg = MagicMock(spec=Config)
        cfg.auth = AuthConfig(type="jwt")

        with pytest.raises(ConfigurationException) as exc:
            auth.build_auth_provider(cfg)

        assert "Failed to initialize JWT authentication provider" in str(exc.value)
        assert "general error" in str(exc.value)
        mock_jwt_verifier.assert_called_once()

    @patch("itential_mcp.server.auth.JWTVerifier")
    def test_jwt_provider_excludes_type_field(self, mock_jwt_verifier):
        """JWT provider configuration excludes the 'type' field."""
        cfg = MagicMock(spec=Config)
        cfg.auth = AuthConfig(
            type="jwt",
            public_key="test-key",
            algorithm="HS256",
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
        # Note: _build_jwt_provider now expects a dict after build_auth_provider conversion
        from itential_mcp.config.converters import auth_to_dict

        auth_config = auth_to_dict(make_auth_config(type="jwt"))
        mock_provider = MagicMock()
        mock_jwt_verifier.return_value = mock_provider

        result = auth._build_jwt_provider(auth_config)

        assert result == mock_provider
        mock_jwt_verifier.assert_called_once_with()

    @patch("itential_mcp.server.auth.JWTVerifier")
    def test_builds_jwt_provider_with_full_config(self, mock_jwt_verifier):
        """JWT provider receives all configuration parameters."""
        from itential_mcp.config.converters import auth_to_dict

        auth_config = auth_to_dict(
            make_auth_config(
                type="jwt",
                public_key="test-key",
                algorithm="HS256",
                audience="aud1,aud2",
                required_scopes="read,write",
            )
        )
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
        from itential_mcp.config.converters import auth_to_dict

        auth_config = auth_to_dict(make_auth_config(type="jwt"))

        with pytest.raises(ConfigurationException) as exc:
            auth._build_jwt_provider(auth_config)

        assert "invalid key" in str(exc.value)

    @patch(
        "itential_mcp.server.auth.JWTVerifier",
        side_effect=RuntimeError("runtime error"),
    )
    def test_handles_jwt_general_error(self, mock_jwt_verifier):
        """JWT provider builder handles general exceptions."""
        from itential_mcp.config.converters import auth_to_dict

        auth_config = auth_to_dict(make_auth_config(type="jwt"))

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

        assert auth.supports_transport(provider, "stdio") is True
        assert auth.supports_transport(provider, "http") is True
        assert auth.supports_transport(provider, "sse") is True
