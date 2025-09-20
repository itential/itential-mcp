# Copyright (c) 2025 Itential, Inc
# GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)

import os
import configparser

import pytest

from itential_mcp import config as config_module
from itential_mcp.config import validate_tool_name, Tool, EndpointTool


@pytest.fixture(autouse=True)
def clear_config_cache():
    """Ensure config.get() doesn't cache between tests"""
    config_module.get.cache_clear()
    yield
    config_module.get.cache_clear()


def test_get_config_from_env(monkeypatch):
    # Clear all ITENTIAL environment variables first
    for key in list(os.environ.keys()):
        if key.startswith("ITENTIAL_MCP_"):
            monkeypatch.delenv(key, raising=False)

    # Set specific environment variables
    monkeypatch.setenv("ITENTIAL_MCP_SERVER_HOST", "127.0.0.1")
    monkeypatch.setenv("ITENTIAL_MCP_SERVER_PORT", "1234")
    monkeypatch.setenv("ITENTIAL_MCP_PLATFORM_USER", "testuser")
    monkeypatch.setenv("ITENTIAL_MCP_PLATFORM_PASSWORD", "secret")
    monkeypatch.setenv("ITENTIAL_MCP_PLATFORM_DISABLE_TLS", "true")

    cfg = config_module.get()

    assert cfg.server_host == "127.0.0.1"
    assert cfg.server_port == 1234
    assert cfg.platform_user == "testuser"
    assert cfg.platform_password == "secret"
    assert cfg.platform_disable_tls is True


def test_get_config_from_file(tmp_path, monkeypatch):
    config_path = tmp_path / "test.ini"

    cp = configparser.ConfigParser()
    cp["server"] = {"host": "192.168.1.1", "port": "9000"}
    cp["platform"] = {"user": "fileuser", "password": "filepass", "disable_tls": "true"}

    with open(config_path, "w") as f:
        cp.write(f)

    # Clear all ITENTIAL environment variables
    for key in list(os.environ.keys()):
        if key.startswith("ITENTIAL_MCP_"):
            monkeypatch.delenv(key, raising=False)

    monkeypatch.setenv("ITENTIAL_MCP_CONFIG", str(config_path))

    cfg = config_module.get()

    assert cfg.server_host == "192.168.1.1"
    assert cfg.server_port == 9000
    assert cfg.platform_user == "fileuser"
    assert cfg.platform_password == "filepass"
    assert cfg.platform_disable_tls is True


def test_missing_config_file_raises(monkeypatch):
    monkeypatch.setenv("ITENTIAL_MCP_CONFIG", "/nonexistent/path.ini")

    with pytest.raises(FileNotFoundError):
        config_module.get()


def test_config_platform_and_server_properties(monkeypatch):
    # Clear all ITENTIAL environment variables first
    for key in list(os.environ.keys()):
        if key.startswith("ITENTIAL_MCP_"):
            monkeypatch.delenv(key, raising=False)

    monkeypatch.setenv("ITENTIAL_MCP_SERVER_INCLUDE_TAGS", "public,system")
    monkeypatch.setenv("ITENTIAL_MCP_SERVER_EXCLUDE_TAGS", "experimental,beta")

    cfg = config_module.get()

    assert cfg.server["include_tags"] == {"public", "system"}
    assert cfg.server["exclude_tags"] == {"experimental", "beta"}
    assert isinstance(cfg.platform, dict)
    assert "host" in cfg.platform


def test_config_server_tools_path_from_env(monkeypatch):
    """Test server_tools_path configuration from environment variable"""
    test_path = "/custom/tools/path"
    monkeypatch.setenv("ITENTIAL_MCP_SERVER_TOOLS_PATH", test_path)

    cfg = config_module.get()

    assert cfg.server_tools_path == test_path
    assert cfg.server["tools_path"] == test_path


def test_config_server_tools_path_default(monkeypatch):
    """Test server_tools_path defaults to None"""
    # Clear any existing env var
    monkeypatch.delenv("ITENTIAL_MCP_SERVER_TOOLS_PATH", raising=False)

    cfg = config_module.get()

    assert cfg.server_tools_path is None
    assert cfg.server["tools_path"] is None


def test_config_server_tools_path_from_file(tmp_path, monkeypatch):
    """Test server_tools_path configuration from config file"""
    config_path = tmp_path / "test.ini"
    test_tools_path = "/file/tools/path"

    cp = configparser.ConfigParser()
    cp["server"] = {"tools_path": test_tools_path}

    with open(config_path, "w") as f:
        cp.write(f)

    # Clear env vars
    for ele in os.environ.keys():
        if ele.startswith("ITENTIAL"):
            monkeypatch.delenv(ele, raising=False)

    monkeypatch.setenv("ITENTIAL_MCP_CONFIG", str(config_path))

    cfg = config_module.get()

    assert cfg.server_tools_path == test_tools_path
    assert cfg.server["tools_path"] == test_tools_path


class TestValidateToolName:
    """Test cases for validate_tool_name function."""

    def test_validate_tool_name_valid_names(self):
        """Test validate_tool_name with valid tool names."""
        valid_names = [
            "tool",
            "tool_name",
            "tool123",
            "myTool",
            "my_tool_123",
            "Tool",
            "TOOL",
            "a",
            "A",
            "tool_",
            "tool__name",
            "camelCase",
            "PascalCase",
            "snake_case",
            "mixed123_Case",
        ]

        for name in valid_names:
            result = validate_tool_name(name)
            assert result == name

    def test_validate_tool_name_invalid_names(self):
        """Test validate_tool_name with invalid tool names."""
        invalid_names = [
            "",  # empty string
            "123tool",  # starts with number
            "_tool",  # starts with underscore
            "tool-name",  # contains hyphen
            "tool.name",  # contains dot
            "tool name",  # contains space
            "tool@name",  # contains special character
            "tool#name",  # contains special character
            "tool$name",  # contains special character
            "tool%name",  # contains special character
            "tool&name",  # contains special character
            "tool*name",  # contains special character
            "tool+name",  # contains special character
            "tool=name",  # contains equal sign
            "tool/name",  # contains slash
            "tool\\name",  # contains backslash
            "tool|name",  # contains pipe
            "tool<name",  # contains less than
            "tool>name",  # contains greater than
            "tool?name",  # contains question mark
            "tool:name",  # contains colon
            "tool;name",  # contains semicolon
            "tool,name",  # contains comma
            "tool[name",  # contains bracket
            "tool]name",  # contains bracket
            "tool{name",  # contains brace
            "tool}name",  # contains brace
            "tool(name",  # contains parenthesis
            "tool)name",  # contains parenthesis
            "tool'name",  # contains quote
            'tool"name',  # contains double quote
            "tool`name",  # contains backtick
            "tool~name",  # contains tilde
            "tool!name",  # contains exclamation
        ]

        for name in invalid_names:
            with pytest.raises(ValueError) as exc_info:
                validate_tool_name(name)

            if name == "":
                assert "cannot be empty" in str(exc_info.value)
            else:
                assert "is invalid" in str(exc_info.value)
                assert "must start with a letter" in str(exc_info.value)
                assert "only contain letters, numbers, and underscores" in str(
                    exc_info.value
                )

    def test_validate_tool_name_edge_cases(self):
        """Test validate_tool_name with edge cases."""
        # Single character valid names
        assert validate_tool_name("a") == "a"
        assert validate_tool_name("Z") == "Z"

        # Very long valid name
        long_name = "a" + "b" * 100 + "_123"
        assert validate_tool_name(long_name) == long_name


class TestToolDataclass:
    """Test cases for Tool dataclass validation."""

    def test_tool_valid_tool_name(self):
        """Test Tool creation with valid tool_name."""
        tool = Tool(
            name="test-asset",
            tool_name="valid_tool_name",
            type="endpoint",
            description="Test tool",
            tags="test",
        )
        assert tool.tool_name == "valid_tool_name"

    def test_tool_invalid_tool_name(self):
        """Test Tool creation with invalid tool_name raises ValidationError."""
        with pytest.raises(ValueError) as exc_info:
            Tool(
                name="test-asset",
                tool_name="123invalid",
                type="endpoint",
                description="Test tool",
                tags="test",
            )

        assert "is invalid" in str(exc_info.value)

    def test_tool_empty_tool_name(self):
        """Test Tool creation with empty tool_name raises ValidationError."""
        with pytest.raises(ValueError) as exc_info:
            Tool(
                name="test-asset",
                tool_name="",
                type="endpoint",
                description="Test tool",
                tags="test",
            )

        assert "cannot be empty" in str(exc_info.value)

    def test_endpoint_tool_valid_tool_name(self):
        """Test EndpointTool creation with valid tool_name."""
        tool = EndpointTool(
            name="test-asset",
            tool_name="valid_endpoint_tool",
            type="endpoint",
            automation="test-automation",
            description="Test endpoint tool",
            tags="test",
        )
        assert tool.tool_name == "valid_endpoint_tool"

    def test_endpoint_tool_invalid_tool_name(self):
        """Test EndpointTool creation with invalid tool_name raises ValidationError."""
        with pytest.raises(ValueError) as exc_info:
            EndpointTool(
                name="test-asset",
                tool_name="invalid-tool-name",
                type="endpoint",
                automation="test-automation",
                description="Test endpoint tool",
                tags="test",
            )

        assert "is invalid" in str(exc_info.value)


class TestConfigDefaults:
    """Test that config uses proper defaults when no values are provided."""

    def test_config_server_defaults(self, monkeypatch):
        """Test that server config uses defaults when no env vars or config file."""
        # Clear all ITENTIAL environment variables
        for key in list(os.environ.keys()):
            if key.startswith("ITENTIAL_MCP_"):
                monkeypatch.delenv(key, raising=False)

        # Ensure no config file is specified
        monkeypatch.delenv("ITENTIAL_MCP_CONFIG", raising=False)

        cfg = config_module.get()

        # Check server defaults
        assert cfg.server_transport == "stdio"
        assert cfg.server_host == "127.0.0.1"
        assert cfg.server_port == 8000
        assert cfg.server_path == "/mcp"
        assert cfg.server_log_level == "INFO"
        assert cfg.server_include_tags is None
        assert cfg.server_exclude_tags == "experimental,beta"

    def test_config_platform_defaults(self, monkeypatch):
        """Test that platform config uses defaults when no env vars or config file."""
        # Clear all ITENTIAL environment variables
        for key in list(os.environ.keys()):
            if key.startswith("ITENTIAL_MCP_"):
                monkeypatch.delenv(key, raising=False)

        # Ensure no config file is specified
        monkeypatch.delenv("ITENTIAL_MCP_CONFIG", raising=False)

        cfg = config_module.get()

        # Check platform defaults
        assert cfg.platform_host == "localhost"
        assert cfg.platform_port == 0
        assert cfg.platform_disable_tls is False
        assert cfg.platform_disable_verify is False
        assert cfg.platform_user == "admin"
        assert cfg.platform_password == "admin"
        assert cfg.platform_client_id is None
        assert cfg.platform_client_secret is None
        assert cfg.platform_timeout == 30

    def test_config_server_tools_path_from_env(self, monkeypatch):
        """Test server tools path configuration from environment variable."""
        # Clear all ITENTIAL environment variables
        for key in list(os.environ.keys()):
            if key.startswith("ITENTIAL_MCP_"):
                monkeypatch.delenv(key, raising=False)

        # Test with custom tools path
        custom_path = "/custom/tools/path"
        monkeypatch.setenv("ITENTIAL_MCP_SERVER_TOOLS_PATH", custom_path)

        cfg = config_module.get()

        # Verify the tools path is set correctly if the field exists
        # Note: This test assumes server_tools_path field exists in Config
        if hasattr(cfg, "server_tools_path"):
            assert cfg.server_tools_path == custom_path

    def test_config_server_tools_path_default(self, monkeypatch):
        """Test server tools path uses default when no env var is set."""
        # Clear all ITENTIAL environment variables
        for key in list(os.environ.keys()):
            if key.startswith("ITENTIAL_MCP_"):
                monkeypatch.delenv(key, raising=False)

        cfg = config_module.get()

        # Verify default tools path if the field exists
        # Note: This test assumes server_tools_path field exists in Config
        if hasattr(cfg, "server_tools_path"):
            # The default should be None or a default path
            assert cfg.server_tools_path is None or isinstance(
                cfg.server_tools_path, str
            )

    def test_config_server_tools_path_from_file(self, tmp_path, monkeypatch):
        """Test server tools path configuration from config file."""
        config_path = tmp_path / "test.ini"
        custom_tools_path = "/file/tools/path"

        cp = configparser.ConfigParser()
        cp["server"] = {"tools_path": custom_tools_path}

        with open(config_path, "w") as f:
            cp.write(f)

        # Clear all ITENTIAL environment variables
        for key in list(os.environ.keys()):
            if key.startswith("ITENTIAL_MCP_"):
                monkeypatch.delenv(key, raising=False)

        monkeypatch.setenv("ITENTIAL_MCP_CONFIG", str(config_path))

        cfg = config_module.get()

        # Verify the tools path from config file if the field exists
        if hasattr(cfg, "server_tools_path"):
            assert cfg.server_tools_path == custom_tools_path


class TestConfigProperties:
    """Test config property methods."""

    def test_server_property_dict_structure(self, monkeypatch):
        """Test that server property returns properly structured dict."""
        # Clear all ITENTIAL environment variables
        for key in list(os.environ.keys()):
            if key.startswith("ITENTIAL_MCP_"):
                monkeypatch.delenv(key, raising=False)

        cfg = config_module.get()
        server_dict = cfg.server

        # Verify server dict structure
        assert isinstance(server_dict, dict)
        assert "transport" in server_dict
        assert "host" in server_dict
        assert "port" in server_dict
        assert "path" in server_dict
        assert "log_level" in server_dict
        assert "include_tags" in server_dict
        assert "exclude_tags" in server_dict

    def test_platform_property_dict_structure(self, monkeypatch):
        """Test that platform property returns properly structured dict."""
        # Clear all ITENTIAL environment variables
        for key in list(os.environ.keys()):
            if key.startswith("ITENTIAL_MCP_"):
                monkeypatch.delenv(key, raising=False)

        cfg = config_module.get()
        platform_dict = cfg.platform

        # Verify platform dict structure
        assert isinstance(platform_dict, dict)
        assert "host" in platform_dict
        assert "port" in platform_dict
        assert "use_tls" in platform_dict
        assert "verify" in platform_dict
        assert "user" in platform_dict
        assert "password" in platform_dict
        assert "client_id" in platform_dict
        assert "client_secret" in platform_dict
        assert "timeout" in platform_dict

    def test_platform_tls_inversion(self, monkeypatch):
        """Test that platform TLS settings are properly inverted."""
        # Clear all ITENTIAL environment variables
        for key in list(os.environ.keys()):
            if key.startswith("ITENTIAL_MCP_"):
                monkeypatch.delenv(key, raising=False)

        monkeypatch.setenv("ITENTIAL_MCP_PLATFORM_DISABLE_TLS", "true")
        monkeypatch.setenv("ITENTIAL_MCP_PLATFORM_DISABLE_VERIFY", "true")

        cfg = config_module.get()
        platform_dict = cfg.platform

        # Verify TLS settings are inverted
        assert platform_dict["use_tls"] is False  # disabled TLS = use_tls False
        assert platform_dict["verify"] is False  # disabled verify = verify False
