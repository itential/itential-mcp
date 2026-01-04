# Copyright (c) 2025 Itential, Inc
# GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

"""Additional tests for config package to achieve 100% coverage."""

import configparser
import pytest

from itential_mcp import config
from itential_mcp.config import (
    options,
    validate_port,
    validate_host,
)
from itential_mcp.config.converters import auth_to_dict
from itential_mcp.config.models import AuthConfig


class TestOptionsFunction:
    """Tests for the options() helper function."""

    def test_options_with_no_arguments(self):
        """Test options() with no arguments."""
        result = options()
        assert result == {
            "x-itential-mcp-cli-enabled": True,
            "x-itential-mcp-arguments": (),
            "x-itential-mcp-options": {},
        }

    def test_options_with_args_only(self):
        """Test options() with positional arguments."""
        result = options("--host", "-h")
        assert result == {
            "x-itential-mcp-cli-enabled": True,
            "x-itential-mcp-arguments": ("--host", "-h"),
            "x-itential-mcp-options": {},
        }

    def test_options_with_kwargs_only(self):
        """Test options() with keyword arguments."""
        result = options(type=str, required=True)
        assert result == {
            "x-itential-mcp-cli-enabled": True,
            "x-itential-mcp-arguments": (),
            "x-itential-mcp-options": {"type": str, "required": True},
        }

    def test_options_with_args_and_kwargs(self):
        """Test options() with both positional and keyword arguments."""
        result = options("--port", "-p", type=int, default=8000)
        assert result == {
            "x-itential-mcp-cli-enabled": True,
            "x-itential-mcp-arguments": ("--port", "-p"),
            "x-itential-mcp-options": {"type": int, "default": 8000},
        }


class TestValidatePort:
    """Tests for validate_port() function."""

    def test_validate_port_too_low(self):
        """Test validate_port with port number too low."""
        with pytest.raises(
            ValueError, match="Platform port must be between 1 and 65535"
        ):
            validate_port(0)

    def test_validate_port_too_high(self):
        """Test validate_port with port number too high."""
        with pytest.raises(
            ValueError, match="Platform port must be between 1 and 65535"
        ):
            validate_port(65536)

    def test_validate_port_negative(self):
        """Test validate_port with negative port number."""
        with pytest.raises(
            ValueError, match="Platform port must be between 1 and 65535"
        ):
            validate_port(-1)

    def test_validate_port_valid_range(self):
        """Test validate_port with valid port numbers."""
        assert validate_port(1) == 1
        assert validate_port(8000) == 8000
        assert validate_port(65535) == 65535


class TestValidateHost:
    """Tests for validate_host() function."""

    def test_validate_host_empty_string(self):
        """Test validate_host with empty string."""
        with pytest.raises(ValueError, match="Platform host cannot be empty"):
            validate_host("")

    def test_validate_host_whitespace_only(self):
        """Test validate_host with whitespace only."""
        with pytest.raises(ValueError, match="Platform host cannot be empty"):
            validate_host("   ")

    def test_validate_host_valid_ipv4(self):
        """Test validate_host with valid IPv4 address."""
        assert validate_host("192.168.1.1") == "192.168.1.1"
        assert validate_host("10.0.0.1") == "10.0.0.1"
        assert validate_host("127.0.0.1") == "127.0.0.1"

    def test_validate_host_valid_ipv6(self):
        """Test validate_host with valid IPv6 address."""
        assert validate_host("::1") == "::1"
        assert validate_host("2001:db8::1") == "2001:db8::1"

    def test_validate_host_too_long(self):
        """Test validate_host with hostname exceeding 253 characters."""
        long_host = "a" * 254
        with pytest.raises(ValueError, match="Platform host is too long"):
            validate_host(long_host)

    def test_validate_host_invalid_format_starts_with_hyphen(self):
        """Test validate_host with hostname starting with hyphen."""
        with pytest.raises(ValueError, match="Invalid platform host format"):
            validate_host("-invalid")

    def test_validate_host_invalid_format_ends_with_hyphen(self):
        """Test validate_host with hostname ending with hyphen."""
        with pytest.raises(ValueError, match="Invalid platform host format"):
            validate_host("invalid-")

    def test_validate_host_invalid_format_special_chars(self):
        """Test validate_host with invalid special characters."""
        with pytest.raises(ValueError, match="Invalid platform host format"):
            validate_host("inval!d")


class TestAuthToDictConverter:
    """Tests for auth_to_dict converter function."""

    def test_auth_to_dict_with_single_audience(self):
        """Test auth_to_dict with single audience value."""
        auth_config = AuthConfig(
            type="jwt",
            issuer="https://auth.example.com",
            audience="my-api",
        )
        result = auth_to_dict(auth_config)
        assert result["audience"] == "my-api"
        assert result["type"] == "jwt"
        assert result["issuer"] == "https://auth.example.com"

    def test_auth_to_dict_with_multiple_audiences(self):
        """Test auth_to_dict with multiple comma-separated audiences."""
        auth_config = AuthConfig(
            type="jwt",
            issuer="https://auth.example.com",
            audience="api1,api2,api3",
        )
        result = auth_to_dict(auth_config)
        assert result["audience"] == ["api1", "api2", "api3"]

    def test_auth_to_dict_with_oauth_scopes_space_separated(self):
        """Test auth_to_dict with space-separated OAuth scopes."""
        auth_config = AuthConfig(
            type="oauth",
            oauth_client_id="client123",
            oauth_client_secret="secret456",
            oauth_scopes="openid profile email",
        )
        result = auth_to_dict(auth_config)
        assert result["scopes"] == ["openid", "profile", "email"]
        assert result["client_id"] == "client123"
        assert result["client_secret"] == "secret456"

    def test_auth_to_dict_with_oauth_scopes_comma_separated(self):
        """Test auth_to_dict with comma-separated OAuth scopes."""
        auth_config = AuthConfig(
            type="oauth",
            oauth_client_id="client123",
            oauth_scopes="openid, profile, email",
        )
        result = auth_to_dict(auth_config)
        assert result["scopes"] == ["openid", "profile", "email"]


class TestConfigFileWithAuthPrefix:
    """Tests for config file parsing with auth_ prefix."""

    def test_config_file_with_auth_prefix(self, tmp_path, monkeypatch):
        """Test config file parsing with auth_ prefix instead of server_auth_."""
        config_path = tmp_path / "test.ini"

        cp = configparser.ConfigParser()
        cp["server"] = {"transport": "stdio"}
        cp["auth"] = {
            "type": "jwt",
            "issuer": "https://auth.example.com",
            "audience": "my-api",
        }

        with open(config_path, "w") as f:
            cp.write(f)

        monkeypatch.setenv("ITENTIAL_MCP_CONFIG", str(config_path))
        config.get.cache_clear()

        cfg = config.get()

        assert cfg.auth.type == "jwt"
        assert cfg.auth.issuer == "https://auth.example.com"
        assert cfg.auth.audience == "my-api"
