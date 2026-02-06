# Copyright (c) 2025 Itential, Inc
# GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

"""Additional tests for auth module to achieve better coverage."""

import pytest
from unittest.mock import patch

from itential_mcp.server.auth import (
    _build_oauth_provider,
    _build_oauth_proxy_provider,
    _get_provider_config,
)
from itential_mcp.core.exceptions import ConfigurationException


class TestOAuthProviderExceptionHandling:
    """Test exception handling in OAuth provider builders"""

    @patch("itential_mcp.server.auth.OAuthProvider")
    def test_oauth_provider_value_error(self, mock_oauth_provider):
        """Test _build_oauth_provider handles ValueError"""
        mock_oauth_provider.side_effect = ValueError("Invalid base_url")

        auth_config = {"redirect_uri": "https://example.com/auth/callback"}

        with pytest.raises(ConfigurationException) as exc_info:
            _build_oauth_provider(auth_config)

        assert "Invalid base_url" in str(exc_info.value)

    @patch("itential_mcp.server.auth.OAuthProvider")
    def test_oauth_provider_general_exception(self, mock_oauth_provider):
        """Test _build_oauth_provider handles general Exception"""
        mock_oauth_provider.side_effect = RuntimeError("Unexpected error")

        auth_config = {"redirect_uri": "https://example.com/auth/callback"}

        with pytest.raises(ConfigurationException) as exc_info:
            _build_oauth_provider(auth_config)

        assert "Failed to initialize OAuth authorization server" in str(exc_info.value)
        assert "Unexpected error" in str(exc_info.value)


class TestOAuthProxyProviderCoverage:
    """Test OAuth proxy provider for missing coverage"""

    def test_oauth_proxy_missing_client_id(self):
        """Test _build_oauth_proxy_provider with missing client_id"""
        auth_config = {
            # client_id is missing
            "client_secret": "secret",
            "authorization_url": "https://auth.example.com/oauth/authorize",
            "token_url": "https://auth.example.com/oauth/token",
            "redirect_uri": "https://example.com/auth/callback",
        }

        with pytest.raises(ConfigurationException) as exc_info:
            _build_oauth_proxy_provider(auth_config)

        assert "client_id" in str(exc_info.value)


class TestProviderConfigurationDefaults:
    """Test provider-specific configuration defaults"""

    def test_auth0_default_scopes(self):
        """Test _get_provider_config returns auth0 default scopes"""
        auth_config = {}  # No scopes provided

        config = _get_provider_config("auth0", auth_config)

        assert "scopes" in config
        assert config["scopes"] == ["openid", "email", "profile"]

    def test_okta_default_scopes(self):
        """Test _get_provider_config returns okta default scopes"""
        auth_config = {}  # No scopes provided

        config = _get_provider_config("okta", auth_config)

        assert "scopes" in config
        assert config["scopes"] == ["openid", "email", "profile"]

    def test_generic_provider_no_defaults(self):
        """Test _get_provider_config returns empty config for generic provider"""
        auth_config = {}

        config = _get_provider_config("generic", auth_config)

        # Generic provider should have no default scopes
        assert (
            "scopes" not in config
            or config.get("scopes") is None
            or len(config.get("scopes", [])) == 0
        )

    def test_generic_provider_with_custom_scopes(self):
        """Test _get_provider_config respects custom scopes for generic provider"""
        auth_config = {"scopes": ["custom", "scopes"]}

        config = _get_provider_config("generic", auth_config)

        assert config["scopes"] == ["custom", "scopes"]
