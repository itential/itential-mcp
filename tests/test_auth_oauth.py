# Copyright (c) 2025 Itential, Inc
# GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import annotations

import pytest
from unittest.mock import patch, MagicMock

from itential_mcp.server.auth import (
    _build_oauth_provider,
    _build_oauth_proxy_provider,
)
from itential_mcp.config.models import AuthConfig
from itential_mcp.core.exceptions import ConfigurationException

from fastmcp.server.auth import (
    JWTVerifier,
    OAuthProxy,
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
        assert "provider_type" not in data


class TestOAuthProviderBuilding:
    """Test OAuth provider building logic."""

    def test_build_oauth_provider_always_raises(self):
        """Full OAuth authorization server mode is not currently supported.

        ``_build_oauth_provider`` must fail fast with a clear
        ``ConfigurationException`` explaining that dynamic client
        registration cannot persist registered clients, and steering
        users to ``oauth_proxy`` instead -- regardless of what fields are
        present in the configuration. ``OAuthProvider`` must never be
        constructed.
        """
        from itential_mcp.config.converters import auth_to_dict

        auth_config = auth_to_dict(
            make_auth_config(
                type="oauth",
                oauth_redirect_uri="http://localhost:8000/auth/callback",
                oauth_scopes="openid,email",
            )
        )

        with patch("itential_mcp.server.auth.OAuthProvider") as mock_oauth_provider:
            with pytest.raises(ConfigurationException) as exc_info:
                _build_oauth_provider(auth_config)

            mock_oauth_provider.assert_not_called()

        message = str(exc_info.value)
        assert "not currently supported" in message
        assert "oauth_proxy" in message

    def test_build_oauth_provider_missing_required_fields_still_raises(self):
        """Missing redirect_uri also raises the same unsupported-mode error."""
        from itential_mcp.config.converters import auth_to_dict

        auth_config = auth_to_dict(make_auth_config(type="oauth"))

        with pytest.raises(ConfigurationException) as exc_info:
            _build_oauth_provider(auth_config)

        message = str(exc_info.value)
        assert "not currently supported" in message
        assert "oauth_proxy" in message

    @patch("itential_mcp.server.auth.OAuthProxy")
    @patch("itential_mcp.server.auth.JWTVerifier")
    def test_build_oauth_proxy_provider_success(
        self, mock_jwt_verifier, mock_oauth_proxy
    ):
        """Test successful OAuth proxy provider building."""
        from itential_mcp.config.converters import auth_to_dict

        auth_config = auth_to_dict(
            make_auth_config(
                type="oauth_proxy",
                oauth_client_id="test_client",
                oauth_client_secret="test_secret",
                oauth_authorization_url="https://accounts.google.com/oauth/authorize",
                oauth_token_url="https://oauth2.googleapis.com/token",
                oauth_redirect_uri="http://localhost:8000/auth/callback",
                jwks_uri="https://accounts.google.com/.well-known/jwks.json",
            )
        )

        mock_verifier_instance = MagicMock()
        mock_jwt_verifier.return_value = mock_verifier_instance

        mock_provider = MagicMock()
        mock_oauth_proxy.return_value = mock_provider

        result = _build_oauth_proxy_provider(auth_config)

        assert result == mock_provider
        mock_jwt_verifier.assert_called_once_with(
            jwks_uri="https://accounts.google.com/.well-known/jwks.json"
        )
        mock_oauth_proxy.assert_called_once_with(
            upstream_authorization_endpoint="https://accounts.google.com/oauth/authorize",
            upstream_token_endpoint="https://oauth2.googleapis.com/token",
            upstream_client_id="test_client",
            upstream_client_secret="test_secret",
            token_verifier=mock_verifier_instance,
            base_url="http://localhost:8000",
            redirect_path="/auth/callback",
        )

    @patch("itential_mcp.server.auth.OAuthProxy")
    @patch("itential_mcp.server.auth.JWTVerifier")
    def test_build_oauth_proxy_provider_base_url_suffix_removal_only(
        self, mock_jwt_verifier, mock_oauth_proxy
    ):
        """Test that base_url derivation only strips the literal suffix.

        Regression test for a bug where ``str.rstrip("/auth/callback")`` was
        used instead of ``str.removesuffix("/auth/callback")``. ``rstrip``
        treats its argument as a set of characters to strip from the end of
        the string, not a literal suffix, so a redirect URI whose host ends
        in any of the characters in "/auth/callback" (e.g. "u" or "k" from a
        ".uk" TLD) would have those trailing host characters incorrectly
        eaten as well. Under the old ``rstrip`` behavior this would have
        produced "https://auth-host.example." instead of the correct
        "https://auth-host.example.uk".

        base_url/redirect_path derivation now uses ``urllib.parse.urlsplit``
        instead of a suffix-stripping heuristic, so this scenario is handled
        correctly by construction: base_url is always scheme+netloc only and
        redirect_path is always the parsed path, independent of any
        character overlap between host and path.
        """
        from itential_mcp.config.converters import auth_to_dict

        auth_config = auth_to_dict(
            make_auth_config(
                type="oauth_proxy",
                oauth_client_id="test_client",
                oauth_client_secret="test_secret",
                oauth_authorization_url="https://accounts.google.com/oauth/authorize",
                oauth_token_url="https://oauth2.googleapis.com/token",
                oauth_redirect_uri="https://auth-host.example.uk/auth/callback",
                jwks_uri="https://accounts.google.com/.well-known/jwks.json",
            )
        )

        mock_verifier_instance = MagicMock()
        mock_jwt_verifier.return_value = mock_verifier_instance

        mock_provider = MagicMock()
        mock_oauth_proxy.return_value = mock_provider

        _build_oauth_proxy_provider(auth_config)

        mock_oauth_proxy.assert_called_once_with(
            upstream_authorization_endpoint="https://accounts.google.com/oauth/authorize",
            upstream_token_endpoint="https://oauth2.googleapis.com/token",
            upstream_client_id="test_client",
            upstream_client_secret="test_secret",
            token_verifier=mock_verifier_instance,
            base_url="https://auth-host.example.uk",
            redirect_path="/auth/callback",
        )

    @patch("itential_mcp.server.auth.OAuthProxy")
    @patch("itential_mcp.server.auth.JWTVerifier")
    def test_build_oauth_proxy_provider_non_default_redirect_path(
        self, mock_jwt_verifier, mock_oauth_proxy
    ):
        """Redirect URIs at non-``/auth/callback`` paths must derive a
        matching, non-default ``redirect_path`` instead of silently falling
        back to ``OAuthProxy``'s default of ``/auth/callback``.

        This is the exact scenario that was previously silently broken: a
        suffix-based ``removesuffix("/auth/callback")`` was a no-op for any
        redirect URI not ending in that literal suffix, causing the entire
        redirect_uri (path included) to be treated as base_url and
        ``OAuthProxy`` to append its own default ``/auth/callback`` on top,
        producing a callback URL that never matched what was registered with
        the upstream IdP.
        """
        from itential_mcp.config.converters import auth_to_dict

        auth_config = auth_to_dict(
            make_auth_config(
                type="oauth_proxy",
                oauth_client_id="test_client",
                oauth_client_secret="test_secret",
                oauth_authorization_url="https://accounts.google.com/oauth/authorize",
                oauth_token_url="https://oauth2.googleapis.com/token",
                oauth_redirect_uri="https://example.com/callback",
                jwks_uri="https://accounts.google.com/.well-known/jwks.json",
            )
        )

        mock_verifier_instance = MagicMock()
        mock_jwt_verifier.return_value = mock_verifier_instance

        mock_provider = MagicMock()
        mock_oauth_proxy.return_value = mock_provider

        _build_oauth_proxy_provider(auth_config)

        mock_oauth_proxy.assert_called_once_with(
            upstream_authorization_endpoint="https://accounts.google.com/oauth/authorize",
            upstream_token_endpoint="https://oauth2.googleapis.com/token",
            upstream_client_id="test_client",
            upstream_client_secret="test_secret",
            token_verifier=mock_verifier_instance,
            base_url="https://example.com",
            redirect_path="/callback",
        )

    @patch("itential_mcp.server.auth.OAuthProxy")
    @patch("itential_mcp.server.auth.JWTVerifier")
    def test_build_oauth_proxy_provider_nested_redirect_path(
        self, mock_jwt_verifier, mock_oauth_proxy
    ):
        """A deeply nested, non-default redirect path must be preserved in
        full as redirect_path, with base_url containing only scheme+netloc.
        """
        from itential_mcp.config.converters import auth_to_dict

        auth_config = auth_to_dict(
            make_auth_config(
                type="oauth_proxy",
                oauth_client_id="test_client",
                oauth_client_secret="test_secret",
                oauth_authorization_url="https://accounts.google.com/oauth/authorize",
                oauth_token_url="https://oauth2.googleapis.com/token",
                oauth_redirect_uri="https://example.com/sso/oauth/return",
                jwks_uri="https://accounts.google.com/.well-known/jwks.json",
            )
        )

        mock_verifier_instance = MagicMock()
        mock_jwt_verifier.return_value = mock_verifier_instance

        mock_provider = MagicMock()
        mock_oauth_proxy.return_value = mock_provider

        _build_oauth_proxy_provider(auth_config)

        mock_oauth_proxy.assert_called_once_with(
            upstream_authorization_endpoint="https://accounts.google.com/oauth/authorize",
            upstream_token_endpoint="https://oauth2.googleapis.com/token",
            upstream_client_id="test_client",
            upstream_client_secret="test_secret",
            token_verifier=mock_verifier_instance,
            base_url="https://example.com",
            redirect_path="/sso/oauth/return",
        )

    @patch("itential_mcp.server.auth.OAuthProxy")
    @patch("itential_mcp.server.auth.JWTVerifier")
    def test_build_oauth_proxy_provider_non_default_port_and_path(
        self, mock_jwt_verifier, mock_oauth_proxy
    ):
        """A redirect URI with a non-default port and a non-default callback
        path must derive a base_url that includes the port and a
        redirect_path matching the actual configured path.
        """
        from itential_mcp.config.converters import auth_to_dict

        auth_config = auth_to_dict(
            make_auth_config(
                type="oauth_proxy",
                oauth_client_id="test_client",
                oauth_client_secret="test_secret",
                oauth_authorization_url="https://accounts.google.com/oauth/authorize",
                oauth_token_url="https://oauth2.googleapis.com/token",
                oauth_redirect_uri="https://example.com:8443/oauth2/idpresponse",
                jwks_uri="https://accounts.google.com/.well-known/jwks.json",
            )
        )

        mock_verifier_instance = MagicMock()
        mock_jwt_verifier.return_value = mock_verifier_instance

        mock_provider = MagicMock()
        mock_oauth_proxy.return_value = mock_provider

        _build_oauth_proxy_provider(auth_config)

        mock_oauth_proxy.assert_called_once_with(
            upstream_authorization_endpoint="https://accounts.google.com/oauth/authorize",
            upstream_token_endpoint="https://oauth2.googleapis.com/token",
            upstream_client_id="test_client",
            upstream_client_secret="test_secret",
            token_verifier=mock_verifier_instance,
            base_url="https://example.com:8443",
            redirect_path="/oauth2/idpresponse",
        )

    def test_build_oauth_proxy_provider_missing_fields(self):
        """Test OAuth proxy provider building with missing required fields."""
        from itential_mcp.config.converters import auth_to_dict

        auth_config = auth_to_dict(
            make_auth_config(
                type="oauth_proxy",
                oauth_client_id="test_client",
            )
        )

        with pytest.raises(ConfigurationException) as exc_info:
            _build_oauth_proxy_provider(auth_config)

        assert "OAuth proxy authentication requires the following fields" in str(
            exc_info.value
        )
        assert "client_secret" in str(exc_info.value)
        assert "authorization_url" in str(exc_info.value)
        assert "token_url" in str(exc_info.value)
        assert "redirect_uri" in str(exc_info.value)

    def test_build_oauth_proxy_provider_missing_token_verifier_config(self):
        """Test OAuth proxy provider building without jwks_uri or public_key.

        All other required fields are present, but neither jwks_uri nor
        public_key is set, so there is no way to construct a token
        verifier. This must raise a clear ConfigurationException rather
        than crashing with a TypeError at OAuthProxy construction time.
        """
        from itential_mcp.config.converters import auth_to_dict

        auth_config = auth_to_dict(
            make_auth_config(
                type="oauth_proxy",
                oauth_client_id="test_client",
                oauth_client_secret="test_secret",
                oauth_authorization_url="https://accounts.google.com/oauth/authorize",
                oauth_token_url="https://oauth2.googleapis.com/token",
                oauth_redirect_uri="http://localhost:8000/auth/callback",
            )
        )

        with pytest.raises(ConfigurationException) as exc_info:
            _build_oauth_proxy_provider(auth_config)

        assert "token verifier" in str(exc_info.value)

    def test_build_oauth_proxy_provider_real_jwt_verifier_no_mocking(self):
        """Regression test: oauth_proxy must build a real, working JWTVerifier.

        This test does not mock JWTVerifier or OAuthProxy at all. It
        exercises the actual construction path end-to-end. On the old,
        broken code this would fail with:

            TypeError: StaticTokenVerifier.__init__() missing 1 required
            positional argument: 'tokens'

        because the fallback unconditionally constructed
        ``StaticTokenVerifier()`` with no arguments. With the fix, a real
        ``JWTVerifier`` is constructed from ``jwks_uri`` and the resulting
        ``OAuthProxy`` provider is returned successfully.
        """
        from itential_mcp.config.converters import auth_to_dict

        auth_config = auth_to_dict(
            make_auth_config(
                type="oauth_proxy",
                oauth_client_id="test_client",
                oauth_client_secret="test_secret",
                oauth_authorization_url="https://accounts.google.com/oauth/authorize",
                oauth_token_url="https://oauth2.googleapis.com/token",
                oauth_redirect_uri="http://localhost:8000/auth/callback",
                jwks_uri="https://accounts.google.com/.well-known/jwks.json",
            )
        )

        provider = _build_oauth_proxy_provider(auth_config)

        assert isinstance(provider, OAuthProxy)
        # OAuthProxy stores the token verifier internally as
        # `_token_validator` (fastmcp does not expose a public accessor).
        assert isinstance(provider._token_validator, JWTVerifier)


class TestOAuthProviderTypeRemoved:
    """Test the removed oauth_provider_type option stays removed."""

    def test_config_has_no_oauth_provider_type_attr(self):
        """AuthConfig no longer exposes oauth_provider_type."""
        assert not hasattr(make_auth_config(), "oauth_provider_type")

    def test_no_provider_type_cli_argument(self):
        """The --auth-oauth-provider-type flag is rejected by the parser."""
        from itential_mcp.runtime import parser

        with pytest.raises(SystemExit):
            parser.parse_args(["run", "--auth-oauth-provider-type", "google"])

    def test_no_get_provider_config(self):
        """server.auth no longer defines _get_provider_config."""
        from itential_mcp.server import auth

        assert not hasattr(auth, "_get_provider_config")

    def test_oauth_provider_error_message(self):
        """type=oauth still fails fast with the corrected rationale."""
        with pytest.raises(ConfigurationException) as exc_info:
            _build_oauth_provider({})

        message = str(exc_info.value)
        assert "user/credential store" in message
        assert "oauth_proxy" in message
        assert "persist" not in message

    @patch("itential_mcp.server.auth.OAuthProxy")
    @patch("itential_mcp.server.auth.JWTVerifier")
    def test_oauth_proxy_passes_valid_scopes(self, mock_jwt_verifier, mock_oauth_proxy):
        """oauth_scopes are forwarded to OAuthProxy as valid_scopes."""
        from itential_mcp.config.converters import auth_to_dict

        auth_config = auth_to_dict(
            make_auth_config(
                type="oauth_proxy",
                oauth_client_id="c",
                oauth_client_secret="s",
                oauth_authorization_url="https://idp.example.com/authorize",
                oauth_token_url="https://idp.example.com/token",
                oauth_redirect_uri="http://localhost:8000/auth/callback",
                oauth_scopes="openid, email",
                jwks_uri="https://idp.example.com/jwks.json",
            )
        )

        _build_oauth_proxy_provider(auth_config)

        kwargs = mock_oauth_proxy.call_args.kwargs
        assert kwargs["valid_scopes"] == ["openid", "email"]
