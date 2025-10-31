"""Unit tests for authentication provider construction."""

from types import SimpleNamespace
from unittest.mock import patch

import pytest

from itential_mcp import auth
from itential_mcp.config import Config
from itential_mcp.core.exceptions import ConfigurationException


class TestBuildAuthProvider:
    """Tests for the build_auth_provider helper function."""

    def test_returns_none_when_auth_disabled(self):
        """Authentication provider is not created when type is none."""
        cfg = Config(server_auth_type="none")

        provider = auth.build_auth_provider(cfg)

        assert provider is None

    @patch("itential_mcp.auth.JWTVerifier")
    def test_creates_jwt_provider_with_expected_arguments(self, mock_jwt_verifier):
        """JWT provider receives configuration from the Config object."""
        cfg = Config(
            server_auth_type="jwt",
            server_auth_public_key="shared-secret",
            server_auth_algorithm="HS256",
            server_auth_required_scopes="read:all, write:all",
            server_auth_audience="aud1, aud2",
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

    @patch("itential_mcp.auth.JWTVerifier", side_effect=ValueError("invalid config"))
    def test_jwt_verifier_errors_are_wrapped(self, mock_jwt_verifier):
        """JWT verifier errors are wrapped in ConfigurationException."""
        cfg = Config(server_auth_type="jwt")

        with pytest.raises(ConfigurationException) as exc:
            auth.build_auth_provider(cfg)

        assert "invalid config" in str(exc.value)
        mock_jwt_verifier.assert_called_once()
