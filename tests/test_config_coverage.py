# Copyright (c) 2025 Itential, Inc
# GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

"""Additional tests for config package to achieve 100% coverage."""

import os
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


@pytest.fixture(autouse=True)
def clear_config_cache():
    """Ensure config.get() doesn't cache between tests."""
    config.get.cache_clear()
    yield
    config.get.cache_clear()


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


class TestConverterEdgeCases:
    """Tests for edge cases in converter functions."""

    def test_split_comma_separated_with_empty_string(self):
        """Test _split_comma_separated with empty string."""
        from itential_mcp.config.converters import _split_comma_separated

        result = _split_comma_separated("")
        assert result == set()

    def test_split_comma_separated_with_none(self):
        """Test _split_comma_separated with None."""
        from itential_mcp.config.converters import _split_comma_separated

        result = _split_comma_separated(None)
        assert result == set()

    def test_split_to_list_with_none(self):
        """Test _split_to_list with None."""
        from itential_mcp.config.converters import _split_to_list

        result = _split_to_list(None)
        assert result == []

    def test_split_to_list_with_empty_string(self):
        """Test _split_to_list with empty string."""
        from itential_mcp.config.converters import _split_to_list

        result = _split_to_list("")
        assert result == []

    def test_auth_to_dict_with_dict_input(self):
        """Test auth_to_dict with dict input (passthrough)."""
        input_dict = {"type": "jwt", "issuer": "https://example.com"}
        result = auth_to_dict(input_dict)
        assert result == input_dict


class TestLoaderFunctions:
    """Tests for loader functions edge cases."""

    def test_parse_tool_env_variables_invalid_format_no_underscore(self, monkeypatch):
        """Test _parse_tool_env_variables with invalid format (no underscore)."""
        from itential_mcp.config.loaders import _parse_tool_env_variables

        monkeypatch.setenv("ITENTIAL_MCP_TOOL_INVALID", "value")

        with pytest.raises(
            ValueError, match="Invalid tool environment variable format"
        ):
            _parse_tool_env_variables()

    def test_parse_tool_env_variables_empty_tool_name(self, monkeypatch):
        """Test _parse_tool_env_variables with empty tool name."""
        from itential_mcp.config.loaders import _parse_tool_env_variables

        monkeypatch.setenv("ITENTIAL_MCP_TOOL__TYPE", "endpoint")

        with pytest.raises(
            ValueError, match="Tool name and config key cannot be empty"
        ):
            _parse_tool_env_variables()

    def test_parse_tool_env_variables_empty_config_key(self, monkeypatch):
        """Test _parse_tool_env_variables with empty config key."""
        from itential_mcp.config.loaders import _parse_tool_env_variables

        # This would create ITENTIAL_MCP_TOOL_MYTOOL_ (trailing underscore, empty key)
        # but we need to test the empty key path - let's use a different approach
        # Actually, rsplit on last underscore means if we have "MYTOOL_" it becomes ("MYTOOL", "")
        monkeypatch.setenv("ITENTIAL_MCP_TOOL_MYTOOL_", "value")

        with pytest.raises(
            ValueError, match="Tool name and config key cannot be empty"
        ):
            _parse_tool_env_variables()

    def test_create_tool_from_dict_service_type(self):
        """Test _create_tool_from_dict with service type."""
        from itential_mcp.config.loaders import _create_tool_from_dict

        tool_data = {
            "name": "test-service",
            "tool_name": "test_service_tool",
            "type": "service",
            "cluster": "default",
        }
        tool = _create_tool_from_dict(tool_data)

        from itential_mcp.config.models import ServiceTool

        assert isinstance(tool, ServiceTool)
        assert tool.cluster == "default"

    def test_create_tool_from_dict_default_tool_type(self):
        """Test _create_tool_from_dict with endpoint type returns EndpointTool."""
        from itential_mcp.config.loaders import _create_tool_from_dict

        tool_data = {
            "name": "test-tool",
            "tool_name": "test_tool",
            "type": "endpoint",
            "automation": "Test Automation",
        }
        tool = _create_tool_from_dict(tool_data)

        from itential_mcp.config.models import EndpointTool

        assert isinstance(tool, EndpointTool)
        assert tool.automation == "Test Automation"

    def test_create_tool_from_dict_fallback_to_tool_base(self):
        """Test _create_tool_from_dict fallback to Tool base class (covers line 113)."""
        from itential_mcp.config.loaders import _create_tool_from_dict
        from pydantic_core import ValidationError

        # tool_data with type that's neither "endpoint" nor "service"
        # This will reach line 113 but fail validation
        tool_data = {
            "name": "test-tool",
            "tool_name": "test_tool",
            "type": "invalid_type",
        }

        # This should raise ValidationError because Tool only accepts "endpoint" or "service"
        with pytest.raises(ValidationError):
            _create_tool_from_dict(tool_data)

    def test_parse_config_file_with_tool_section(self, tmp_path, monkeypatch):
        """Test _parse_config_file with tool sections."""
        from itential_mcp.config.loaders import _parse_config_file

        config_path = tmp_path / "test.ini"

        cp = configparser.ConfigParser()
        cp["server"] = {"transport": "stdio"}
        cp["tool:my_workflow"] = {
            "name": "deploy_config",
            "type": "endpoint",
            "automation": "Deploy Configuration",
        }

        with open(config_path, "w") as f:
            cp.write(f)

        # Clear environment tools
        for key in list(os.environ.keys()):
            if key.startswith("ITENTIAL_MCP_TOOL_"):
                monkeypatch.delenv(key, raising=False)

        config_data, tools = _parse_config_file(config_path)

        assert len(tools) == 1
        assert tools[0].tool_name == "my_workflow"
        assert tools[0].type == "endpoint"

    def test_parse_config_file_with_env_tool_override(self, tmp_path, monkeypatch):
        """Test _parse_config_file with environment variable overriding config file."""
        from itential_mcp.config.loaders import _parse_config_file

        config_path = tmp_path / "test.ini"

        # Clear all existing tool environment variables first
        for key in list(os.environ.keys()):
            if key.startswith("ITENTIAL_MCP_TOOL_"):
                monkeypatch.delenv(key, raising=False)

        cp = configparser.ConfigParser()
        cp["tool:my_tool"] = {
            "name": "original_name",
            "type": "endpoint",
            "automation": "Original Automation",
        }

        with open(config_path, "w") as f:
            cp.write(f)

        # Set environment variables that should override (matching the tool_name)
        # The environment variable format uses uppercase and the tool name is "my_tool"
        monkeypatch.setenv("ITENTIAL_MCP_TOOL_my_tool_NAME", "overridden_name")
        monkeypatch.setenv("ITENTIAL_MCP_TOOL_my_tool_TYPE", "endpoint")
        monkeypatch.setenv(
            "ITENTIAL_MCP_TOOL_my_tool_AUTOMATION", "Override Automation"
        )

        config_data, tools = _parse_config_file(config_path)

        # Should have only one tool (config file merged with env vars)
        assert len(tools) == 1
        assert tools[0].name == "overridden_name"
        assert tools[0].automation == "Override Automation"

    def test_parse_config_file_with_env_only_tool(self, tmp_path, monkeypatch):
        """Test _parse_config_file includes environment-only tools."""
        from itential_mcp.config.loaders import _parse_config_file

        config_path = tmp_path / "test.ini"

        cp = configparser.ConfigParser()
        cp["server"] = {"transport": "stdio"}

        with open(config_path, "w") as f:
            cp.write(f)

        # Set environment tool not in config file
        monkeypatch.setenv("ITENTIAL_MCP_TOOL_ENV_ONLY_NAME", "env_tool")
        monkeypatch.setenv("ITENTIAL_MCP_TOOL_ENV_ONLY_TYPE", "service")
        monkeypatch.setenv("ITENTIAL_MCP_TOOL_ENV_ONLY_CLUSTER", "production")

        config_data, tools = _parse_config_file(config_path)

        assert len(tools) == 1
        assert tools[0].tool_name == "ENV_ONLY"
        assert tools[0].type == "service"

    def test_split_comma_separated_in_loaders(self):
        """Test _split_comma_separated function in loaders module."""
        from itential_mcp.config.loaders import _split_comma_separated

        # Test with None
        result = _split_comma_separated(None)
        assert result == []

        # Test with empty string
        result = _split_comma_separated("")
        assert result == []

        # Test with values
        result = _split_comma_separated("a,b,c")
        assert result == ["a", "b", "c"]

    def test_split_space_or_comma_separated(self):
        """Test _split_space_or_comma_separated function."""
        from itential_mcp.config.loaders import _split_space_or_comma_separated

        # Test with None
        result = _split_space_or_comma_separated(None)
        assert result == []

        # Test with empty string
        result = _split_space_or_comma_separated("")
        assert result == []

        # Test with space-separated values
        result = _split_space_or_comma_separated("a b c")
        assert result == ["a", "b", "c"]

        # Test with comma-separated values
        result = _split_space_or_comma_separated("a,b,c")
        assert result == ["a", "b", "c"]

        # Test with mixed separators
        result = _split_space_or_comma_separated("a, b c,d")
        assert result == ["a", "b", "c", "d"]

    def test_load_config_without_file_with_env_tools(self, monkeypatch):
        """Test load_config without config file but with environment tools."""
        from itential_mcp.config.loaders import load_config

        # Clear config file setting
        monkeypatch.delenv("ITENTIAL_MCP_CONFIG", raising=False)

        # Clear existing tools
        for key in list(os.environ.keys()):
            if key.startswith("ITENTIAL_MCP_TOOL_"):
                monkeypatch.delenv(key, raising=False)

        # Set environment tool
        monkeypatch.setenv("ITENTIAL_MCP_TOOL_TEST_NAME", "test_asset")
        monkeypatch.setenv("ITENTIAL_MCP_TOOL_TEST_TYPE", "endpoint")
        monkeypatch.setenv("ITENTIAL_MCP_TOOL_TEST_AUTOMATION", "Test Automation")

        config.get.cache_clear()
        cfg = load_config()

        assert len(cfg.tools) == 1
        assert cfg.tools[0].tool_name == "TEST"
        assert cfg.tools[0].type == "endpoint"


class TestPlatformConfigValidators:
    """Tests for PlatformConfig field validators."""

    def test_platform_config_invalid_port_triggers_validation(self, monkeypatch):
        """Test PlatformConfig with invalid port triggers validation."""
        from itential_mcp.config.models import PlatformConfig

        # Clear environment variables
        for key in list(os.environ.keys()):
            if key.startswith("ITENTIAL_MCP_PLATFORM_"):
                monkeypatch.delenv(key, raising=False)

        # Try to create with invalid port
        with pytest.raises(
            ValueError, match="Platform port must be between 1 and 65535"
        ):
            PlatformConfig(port=0)

    def test_platform_config_invalid_host_triggers_validation(self, monkeypatch):
        """Test PlatformConfig with invalid host triggers validation."""
        from itential_mcp.config.models import PlatformConfig

        # Clear environment variables
        for key in list(os.environ.keys()):
            if key.startswith("ITENTIAL_MCP_PLATFORM_"):
                monkeypatch.delenv(key, raising=False)

        # Try to create with invalid host (empty string)
        with pytest.raises(ValueError, match="Platform host cannot be empty"):
            PlatformConfig(host="")


class TestValidateHostCompleteHostnamePath:
    """Test validate_host to ensure all code paths are covered."""

    def test_validate_host_with_valid_hostname(self):
        """Test validate_host with valid hostname returns the hostname."""
        result = validate_host("valid-hostname.example.com")
        assert result == "valid-hostname.example.com"
