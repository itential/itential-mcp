# Copyright (c) 2025 Itential, Inc
# GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

import os
import configparser

import pytest

from itential_mcp import config as config_module
from itential_mcp import defaults
from itential_mcp import runtime
from itential_mcp.cli import argument_groups
from itential_mcp.config import validate_tool_name, Tool, EndpointTool
from itential_mcp.config.converters import (
    server_to_dict,
    platform_to_dict,
    auth_to_dict,
)
from itential_mcp.config.loaders import _strip_auth_prefix


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

    assert cfg.server.host == "127.0.0.1"
    assert cfg.server.port == 1234
    assert cfg.platform.user == "testuser"
    assert cfg.platform.password == "secret"
    assert cfg.platform.disable_tls is True


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

    assert cfg.server.host == "192.168.1.1"
    assert cfg.server.port == 9000
    assert cfg.platform.user == "fileuser"
    assert cfg.platform.password == "filepass"
    assert cfg.platform.disable_tls is True


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

    server_dict = server_to_dict(cfg.server)
    assert server_dict["include_tags"] == {"public", "system"}
    assert server_dict["exclude_tags"] == {"experimental", "beta"}

    platform_dict = platform_to_dict(cfg.platform)
    assert isinstance(platform_dict, dict)
    assert "host" in platform_dict


def test_config_server_tools_path_from_env(monkeypatch):
    """Test server_tools_path configuration from environment variable"""
    test_path = "/custom/tools/path"
    monkeypatch.setenv("ITENTIAL_MCP_SERVER_TOOLS_PATH", test_path)

    cfg = config_module.get()

    assert cfg.server.tools_path == test_path
    server_dict = server_to_dict(cfg.server)
    assert server_dict["tools_path"] == test_path


def test_config_server_tools_path_default(monkeypatch):
    """Test server_tools_path defaults to None"""
    # Clear any existing env var
    monkeypatch.delenv("ITENTIAL_MCP_SERVER_TOOLS_PATH", raising=False)

    cfg = config_module.get()

    assert cfg.server.tools_path is None
    server_dict = server_to_dict(cfg.server)
    assert server_dict["tools_path"] is None


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

    assert cfg.server.tools_path == test_tools_path
    server_dict = server_to_dict(cfg.server)
    assert server_dict["tools_path"] == test_tools_path


def test_auth_config_defaults(monkeypatch):
    """Test default authentication configuration values."""
    for key in list(os.environ.keys()):
        if key.startswith("ITENTIAL_MCP_"):
            monkeypatch.delenv(key, raising=False)

    cfg = config_module.get()

    auth_dict = auth_to_dict(cfg.auth)
    assert auth_dict == {"type": "none"}


def test_auth_config_from_env(monkeypatch):
    """Test authentication configuration derived from environment variables."""
    for key in list(os.environ.keys()):
        if key.startswith("ITENTIAL_MCP_"):
            monkeypatch.delenv(key, raising=False)

    monkeypatch.setenv("ITENTIAL_MCP_SERVER_AUTH_TYPE", "jwt")
    monkeypatch.setenv(
        "ITENTIAL_MCP_SERVER_AUTH_JWKS_URI", "https://idp.example.com/jwks.json"
    )
    monkeypatch.setenv("ITENTIAL_MCP_SERVER_AUTH_ISSUER", "https://idp.example.com/")
    monkeypatch.setenv(
        "ITENTIAL_MCP_SERVER_AUTH_AUDIENCE", "itential-mcp,another-client"
    )
    monkeypatch.setenv("ITENTIAL_MCP_SERVER_AUTH_REQUIRED_SCOPES", "read:all,write:all")

    cfg = config_module.get()
    auth_dict = auth_to_dict(cfg.auth)

    assert auth_dict["type"] == "jwt"
    assert auth_dict["jwks_uri"] == "https://idp.example.com/jwks.json"
    assert auth_dict["issuer"] == "https://idp.example.com/"
    assert auth_dict["audience"] == ["itential-mcp", "another-client"]
    assert auth_dict["required_scopes"] == ["read:all", "write:all"]


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
        assert cfg.server.transport == "stdio"
        assert cfg.server.host == "127.0.0.1"
        assert cfg.server.port == 8000
        assert cfg.server.certificate_file == ""
        assert cfg.server.private_key_file == ""
        assert cfg.server.path == "/mcp"
        assert cfg.server.log_level == "NONE"
        assert cfg.server.include_tags is None
        assert cfg.server.exclude_tags == "experimental,beta"

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
        assert cfg.platform.host == "localhost"
        assert cfg.platform.port == 0
        assert cfg.platform.disable_tls is False
        assert cfg.platform.disable_verify is False
        assert cfg.platform.user == "admin"
        assert cfg.platform.password == "admin"
        assert cfg.platform.client_id is None
        assert cfg.platform.client_secret is None
        assert cfg.platform.timeout == 30

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

        # Verify the tools path is set correctly
        assert cfg.server.tools_path == custom_path

    def test_config_server_tools_path_default(self, monkeypatch):
        """Test server tools path uses default when no env var is set."""
        # Clear all ITENTIAL environment variables
        for key in list(os.environ.keys()):
            if key.startswith("ITENTIAL_MCP_"):
                monkeypatch.delenv(key, raising=False)

        cfg = config_module.get()

        # Verify default tools path
        assert cfg.server.tools_path is None

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

        # Verify the tools path from config file
        assert cfg.server.tools_path == custom_tools_path


class TestConfigProperties:
    """Test config property methods."""

    def test_server_property_dict_structure(self, monkeypatch):
        """Test that server property returns properly structured dict."""
        # Clear all ITENTIAL environment variables
        for key in list(os.environ.keys()):
            if key.startswith("ITENTIAL_MCP_"):
                monkeypatch.delenv(key, raising=False)

        cfg = config_module.get()
        server_dict = server_to_dict(cfg.server)

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
        platform_dict = platform_to_dict(cfg.platform)

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
        platform_dict = platform_to_dict(cfg.platform)

        # Verify TLS settings are inverted
        assert platform_dict["use_tls"] is False  # disabled TLS = use_tls False
        assert platform_dict["verify"] is False  # disabled verify = verify False


class TestTLSCertificateConfiguration:
    """Test TLS certificate configuration fields."""

    def test_server_certificate_file_from_env(self, monkeypatch):
        """Test server certificate file configuration from environment variable."""
        # Clear all ITENTIAL environment variables
        for key in list(os.environ.keys()):
            if key.startswith("ITENTIAL_MCP_"):
                monkeypatch.delenv(key, raising=False)

        test_cert_path = "/path/to/certificate.pem"
        monkeypatch.setenv("ITENTIAL_MCP_SERVER_CERTIFICATE_FILE", test_cert_path)

        cfg = config_module.get()

        assert cfg.server.certificate_file == test_cert_path
        server_dict = server_to_dict(cfg.server)
        assert server_dict["certificate_file"] == test_cert_path

    def test_server_private_key_file_from_env(self, monkeypatch):
        """Test server private key file configuration from environment variable."""
        # Clear all ITENTIAL environment variables
        for key in list(os.environ.keys()):
            if key.startswith("ITENTIAL_MCP_"):
                monkeypatch.delenv(key, raising=False)

        test_key_path = "/path/to/private_key.pem"
        monkeypatch.setenv("ITENTIAL_MCP_SERVER_PRIVATE_KEY_FILE", test_key_path)

        cfg = config_module.get()

        assert cfg.server.private_key_file == test_key_path
        server_dict = server_to_dict(cfg.server)
        assert server_dict["private_key_file"] == test_key_path

    def test_tls_certificate_fields_default_empty(self, monkeypatch):
        """Test that TLS certificate fields default to empty strings."""
        # Clear all ITENTIAL environment variables
        for key in list(os.environ.keys()):
            if key.startswith("ITENTIAL_MCP_"):
                monkeypatch.delenv(key, raising=False)

        cfg = config_module.get()

        assert cfg.server.certificate_file == ""
        assert cfg.server.private_key_file == ""
        server_dict = server_to_dict(cfg.server)
        assert server_dict["certificate_file"] is None
        assert server_dict["private_key_file"] is None

    def test_tls_certificate_fields_from_config_file(self, tmp_path, monkeypatch):
        """Test TLS certificate fields configuration from config file."""
        config_path = tmp_path / "test.ini"
        test_cert_path = "/file/path/to/cert.pem"
        test_key_path = "/file/path/to/key.pem"

        cp = configparser.ConfigParser()
        cp["server"] = {
            "certificate_file": test_cert_path,
            "private_key_file": test_key_path,
        }

        with open(config_path, "w") as f:
            cp.write(f)

        # Clear all ITENTIAL environment variables
        for key in list(os.environ.keys()):
            if key.startswith("ITENTIAL_MCP_"):
                monkeypatch.delenv(key, raising=False)

        monkeypatch.setenv("ITENTIAL_MCP_CONFIG", str(config_path))

        cfg = config_module.get()

        assert cfg.server.certificate_file == test_cert_path
        assert cfg.server.private_key_file == test_key_path
        server_dict = server_to_dict(cfg.server)
        assert server_dict["certificate_file"] == test_cert_path
        assert server_dict["private_key_file"] == test_key_path

    def test_tls_certificate_fields_env_overrides_file(self, tmp_path, monkeypatch):
        """Test that environment variables override config file for TLS certificate fields."""
        config_path = tmp_path / "test.ini"
        file_cert_path = "/file/path/to/cert.pem"
        file_key_path = "/file/path/to/key.pem"
        env_cert_path = "/env/path/to/cert.pem"
        env_key_path = "/env/path/to/key.pem"

        # Setup config file with certificate paths
        cp = configparser.ConfigParser()
        cp["server"] = {
            "certificate_file": file_cert_path,
            "private_key_file": file_key_path,
        }

        with open(config_path, "w") as f:
            cp.write(f)

        # Clear all ITENTIAL environment variables
        for key in list(os.environ.keys()):
            if key.startswith("ITENTIAL_MCP_"):
                monkeypatch.delenv(key, raising=False)

        # Set environment variables first, then config file
        monkeypatch.setenv("ITENTIAL_MCP_SERVER_CERTIFICATE_FILE", env_cert_path)
        monkeypatch.setenv("ITENTIAL_MCP_SERVER_PRIVATE_KEY_FILE", env_key_path)
        monkeypatch.setenv("ITENTIAL_MCP_CONFIG", str(config_path))

        cfg = config_module.get()

        # Environment must override the config file (documented precedence).
        assert cfg.server.certificate_file == env_cert_path
        assert cfg.server.private_key_file == env_key_path

    def test_server_dict_includes_tls_fields(self, monkeypatch):
        """Test that server property dict includes TLS certificate fields."""
        # Clear all ITENTIAL environment variables
        for key in list(os.environ.keys()):
            if key.startswith("ITENTIAL_MCP_"):
                monkeypatch.delenv(key, raising=False)

        cfg = config_module.get()
        server_dict = server_to_dict(cfg.server)

        assert "certificate_file" in server_dict
        assert "private_key_file" in server_dict
        # When empty strings, the server dict contains None values
        assert server_dict["certificate_file"] is None
        assert server_dict["private_key_file"] is None


def _clear_itential_env(monkeypatch):
    """Remove every ITENTIAL_MCP_* variable from the environment.

    Args:
        monkeypatch: The pytest monkeypatch fixture.

    Returns:
        None.

    Raises:
        None.
    """
    for key in list(os.environ.keys()):
        if key.startswith("ITENTIAL_MCP_"):
            monkeypatch.delenv(key, raising=False)


def _write_config_file(tmp_path, section: str, key: str, value: str):
    """Write a minimal single-key config file and return its path.

    Args:
        tmp_path: pytest tmp_path fixture directory.
        section: The config file section name (e.g. "server").
        key: The bare key name to write within the section.
        value: The string value to write for the key.

    Returns:
        str: The path to the written config file.

    Raises:
        None.
    """
    config_path = tmp_path / "test.ini"
    cp = configparser.ConfigParser()
    cp[section] = {key: value}
    with open(config_path, "w") as f:
        cp.write(f)
    return str(config_path)


# Enumeration of all 38 env-backed fields across ServerConfig (14),
# AuthConfig (14), and PlatformConfig (10), verified directly against
# src/itential_mcp/config/models.py. Each tuple is:
#   (section, file_key, env_var, file_value, env_value, expected)
# "section" is the config-file section name and file_key prefix used to
# build the [section] key=value entry (auth fields use "server" with an
# "auth_" prefixed key, matching the server_auth_ / auth_ handling in
# loaders.py).
_PRECEDENCE_CASES = [
    # --- ServerConfig (14) ---
    ("server", "transport", "ITENTIAL_MCP_SERVER_TRANSPORT", "stdio", "sse", "sse"),
    ("server", "host", "ITENTIAL_MCP_SERVER_HOST", "10.0.0.1", "10.0.0.2", "10.0.0.2"),
    ("server", "port", "ITENTIAL_MCP_SERVER_PORT", "8000", "9001", 9001),
    (
        "server",
        "certificate_file",
        "ITENTIAL_MCP_SERVER_CERTIFICATE_FILE",
        "/file/cert.pem",
        "/env/cert.pem",
        "/env/cert.pem",
    ),
    (
        "server",
        "private_key_file",
        "ITENTIAL_MCP_SERVER_PRIVATE_KEY_FILE",
        "/file/key.pem",
        "/env/key.pem",
        "/env/key.pem",
    ),
    (
        "server",
        "path",
        "ITENTIAL_MCP_SERVER_PATH",
        "/file-path",
        "/env-path",
        "/env-path",
    ),
    (
        "server",
        "log_level",
        "ITENTIAL_MCP_SERVER_LOG_LEVEL",
        "DEBUG",
        "ERROR",
        "ERROR",
    ),
    (
        "server",
        "include_tags",
        "ITENTIAL_MCP_SERVER_INCLUDE_TAGS",
        "file_tag",
        "env_tag",
        "env_tag",
    ),
    (
        "server",
        "exclude_tags",
        "ITENTIAL_MCP_SERVER_EXCLUDE_TAGS",
        "file_tag",
        "env_tag",
        "env_tag",
    ),
    (
        "server",
        "tools_path",
        "ITENTIAL_MCP_SERVER_TOOLS_PATH",
        "/file/tools",
        "/env/tools",
        "/env/tools",
    ),
    (
        "server",
        "keepalive_interval",
        "ITENTIAL_MCP_SERVER_KEEPALIVE_INTERVAL",
        "100",
        "200",
        200,
    ),
    (
        "server",
        "response_format",
        "ITENTIAL_MCP_SERVER_RESPONSE_FORMAT",
        "json",
        "toon",
        "toon",
    ),
    (
        "server",
        "test_connection_on_startup",
        "ITENTIAL_MCP_SERVER_TEST_CONNECTION_ON_STARTUP",
        "false",
        "true",
        True,
    ),
    (
        "server",
        "startup_test_timeout",
        "ITENTIAL_MCP_SERVER_STARTUP_TEST_TIMEOUT",
        "10",
        "20",
        20,
    ),
    # --- AuthConfig (14), written under the [auth] file section using the
    # bare field name. Note: the documented file spelling is actually
    # [server] auth_<field> = ... (see docs/mcp.conf.example); [auth] is an
    # undocumented alternate section that has also always been accepted.
    # Both spellings now correctly route to AuthConfig and resolve field
    # names without mangling (see test_server_section_auth_keys_route_to_auth_config
    # and test_oauth_field_names_not_mangled for the [server] spelling and
    # the oauth_* mangling fix respectively).
    (
        "auth",
        "type",
        "ITENTIAL_MCP_SERVER_AUTH_TYPE",
        "jwt",
        "oauth_proxy",
        "oauth_proxy",
    ),
    (
        "auth",
        "jwks_uri",
        "ITENTIAL_MCP_SERVER_AUTH_JWKS_URI",
        "https://file.example.com/jwks.json",
        "https://env.example.com/jwks.json",
        "https://env.example.com/jwks.json",
    ),
    (
        "auth",
        "public_key",
        "ITENTIAL_MCP_SERVER_AUTH_PUBLIC_KEY",
        "file-key",
        "env-key",
        "env-key",
    ),
    (
        "auth",
        "issuer",
        "ITENTIAL_MCP_SERVER_AUTH_ISSUER",
        "https://file.example.com/",
        "https://env.example.com/",
        "https://env.example.com/",
    ),
    (
        "auth",
        "audience",
        "ITENTIAL_MCP_SERVER_AUTH_AUDIENCE",
        "file-aud",
        "env-aud",
        "env-aud",
    ),
    (
        "auth",
        "algorithm",
        "ITENTIAL_MCP_SERVER_AUTH_ALGORITHM",
        "HS256",
        "RS256",
        "RS256",
    ),
    (
        "auth",
        "required_scopes",
        "ITENTIAL_MCP_SERVER_AUTH_REQUIRED_SCOPES",
        "file:scope",
        "env:scope",
        "env:scope",
    ),
    (
        "auth",
        "oauth_client_id",
        "ITENTIAL_MCP_SERVER_AUTH_OAUTH_CLIENT_ID",
        "file-client-id",
        "env-client-id",
        "env-client-id",
    ),
    (
        "auth",
        "oauth_client_secret",
        "ITENTIAL_MCP_SERVER_AUTH_OAUTH_CLIENT_SECRET",
        "file-secret",
        "env-secret",
        "env-secret",
    ),
    (
        "auth",
        "oauth_authorization_url",
        "ITENTIAL_MCP_SERVER_AUTH_OAUTH_AUTHORIZATION_URL",
        "https://file.example.com/authorize",
        "https://env.example.com/authorize",
        "https://env.example.com/authorize",
    ),
    (
        "auth",
        "oauth_token_url",
        "ITENTIAL_MCP_SERVER_AUTH_OAUTH_TOKEN_URL",
        "https://file.example.com/token",
        "https://env.example.com/token",
        "https://env.example.com/token",
    ),
    (
        "auth",
        "oauth_userinfo_url",
        "ITENTIAL_MCP_SERVER_AUTH_OAUTH_USERINFO_URL",
        "https://file.example.com/userinfo",
        "https://env.example.com/userinfo",
        "https://env.example.com/userinfo",
    ),
    (
        "auth",
        "oauth_scopes",
        "ITENTIAL_MCP_SERVER_AUTH_OAUTH_SCOPES",
        "file-scope",
        "env-scope",
        "env-scope",
    ),
    (
        "auth",
        "oauth_redirect_uri",
        "ITENTIAL_MCP_SERVER_AUTH_OAUTH_REDIRECT_URI",
        "https://file.example.com/callback",
        "https://env.example.com/callback",
        "https://env.example.com/callback",
    ),
    # --- PlatformConfig (10) ---
    (
        "platform",
        "host",
        "ITENTIAL_MCP_PLATFORM_HOST",
        "file-host",
        "env-host",
        "env-host",
    ),
    ("platform", "port", "ITENTIAL_MCP_PLATFORM_PORT", "8080", "8443", 8443),
    (
        "platform",
        "disable_tls",
        "ITENTIAL_MCP_PLATFORM_DISABLE_TLS",
        "false",
        "true",
        True,
    ),
    (
        "platform",
        "disable_verify",
        "ITENTIAL_MCP_PLATFORM_DISABLE_VERIFY",
        "false",
        "true",
        True,
    ),
    (
        "platform",
        "user",
        "ITENTIAL_MCP_PLATFORM_USER",
        "file-user",
        "env-user",
        "env-user",
    ),
    (
        "platform",
        "password",
        "ITENTIAL_MCP_PLATFORM_PASSWORD",
        "file-pass",
        "env-pass",
        "env-pass",
    ),
    (
        "platform",
        "client_id",
        "ITENTIAL_MCP_PLATFORM_CLIENT_ID",
        "file-client-id",
        "env-client-id",
        "env-client-id",
    ),
    (
        "platform",
        "client_secret",
        "ITENTIAL_MCP_PLATFORM_CLIENT_SECRET",
        "file-secret",
        "env-secret",
        "env-secret",
    ),
    ("platform", "timeout", "ITENTIAL_MCP_PLATFORM_TIMEOUT", "15", "45", 45),
    ("platform", "ttl", "ITENTIAL_MCP_PLATFORM_TTL", "60", "120", 120),
]

assert len(_PRECEDENCE_CASES) == 38, (
    f"Expected 38 env-backed fields, found {len(_PRECEDENCE_CASES)}"
)

_FILE_BEATS_DEFAULT_CASES = list(_PRECEDENCE_CASES)


def _get_config_attr(cfg, section: str, file_key: str):
    """Resolve the config attribute value for a precedence test case.

    Args:
        cfg: The loaded Config instance.
        section: The config-file section name used in the test case
            ("server", "auth", or "platform").
        file_key: The bare field name used in the test case.

    Returns:
        The corresponding attribute value on cfg.server / cfg.auth /
        cfg.platform.

    Raises:
        None.
    """
    if section == "platform":
        return getattr(cfg.platform, file_key)
    if section == "auth":
        return getattr(cfg.auth, file_key)
    return getattr(cfg.server, file_key)


class TestConfigPrecedence:
    """Verify env vars (and CLI flags funneled into os.environ) beat the
    config file, which in turn beats defaults -- across all 38 env-backed
    fields on ServerConfig, AuthConfig, and PlatformConfig.
    """

    def test_sse_transport_not_downgraded_by_config_file(self, tmp_path, monkeypatch):
        """Regression test for the reported bug symptom.

        A config file setting transport = stdio must not silently override
        ITENTIAL_MCP_SERVER_TRANSPORT=sse from the environment.
        """
        _clear_itential_env(monkeypatch)

        config_path = _write_config_file(tmp_path, "server", "transport", "stdio")
        monkeypatch.setenv("ITENTIAL_MCP_CONFIG", config_path)
        monkeypatch.setenv("ITENTIAL_MCP_SERVER_TRANSPORT", "sse")

        cfg = config_module.get()

        assert cfg.server.transport == "sse"

    @pytest.mark.parametrize(
        "section,file_key,env_var,file_value,env_value,expected",
        _PRECEDENCE_CASES,
        ids=[f"{c[0]}.{c[1]}" for c in _PRECEDENCE_CASES],
    )
    def test_env_beats_file_for_every_field(
        self,
        tmp_path,
        monkeypatch,
        section,
        file_key,
        env_var,
        file_value,
        env_value,
        expected,
    ):
        """Env var wins over config file for every affected field."""
        _clear_itential_env(monkeypatch)

        config_path = _write_config_file(tmp_path, section, file_key, file_value)
        monkeypatch.setenv("ITENTIAL_MCP_CONFIG", config_path)
        monkeypatch.setenv(env_var, env_value)

        cfg = config_module.get()

        assert _get_config_attr(cfg, section, file_key) == expected

    @pytest.mark.parametrize(
        "section,file_key,env_var,file_value,env_value,expected",
        _FILE_BEATS_DEFAULT_CASES,
        ids=[f"{c[0]}.{c[1]}" for c in _FILE_BEATS_DEFAULT_CASES],
    )
    def test_file_beats_default_when_env_unset(
        self,
        tmp_path,
        monkeypatch,
        section,
        file_key,
        env_var,
        file_value,
        env_value,
        expected,
    ):
        """Config file value wins over default when the env var is unset.

        Regression guard confirming the fix isn't overly aggressive -- the
        file value must still apply when nothing in the environment
        contests it.
        """
        _clear_itential_env(monkeypatch)

        config_path = _write_config_file(tmp_path, section, file_key, file_value)
        monkeypatch.setenv("ITENTIAL_MCP_CONFIG", config_path)

        cfg = config_module.get()
        actual = _get_config_attr(cfg, section, file_key)

        # Compare against the type-coerced file value using the same
        # transform expected/env_value went through (bool/int fields use
        # their real type in "expected" already, so compare structurally).
        if isinstance(expected, bool):
            assert actual == (file_value.strip().lower() in {"true", "1", "yes", "on"})
        elif isinstance(expected, int):
            assert actual == int(file_value)
        else:
            assert actual == file_value

    _DEFAULT_FALLBACK_CASES = [
        c
        for c in _PRECEDENCE_CASES
        if (c[0], c[1])
        in {
            ("server", "transport"),
            ("auth", "type"),
            ("platform", "host"),
        }
    ]

    @pytest.mark.parametrize(
        "section,file_key,env_var,file_value,env_value,expected",
        _DEFAULT_FALLBACK_CASES,
        ids=[f"{c[0]}.{c[1]}" for c in _DEFAULT_FALLBACK_CASES],
    )
    def test_default_when_neither_env_nor_file_set(
        self,
        monkeypatch,
        section,
        file_key,
        env_var,
        file_value,
        env_value,
        expected,
    ):
        """Default value wins when neither env var nor config file is set."""
        _clear_itential_env(monkeypatch)
        monkeypatch.delenv("ITENTIAL_MCP_CONFIG", raising=False)

        cfg = config_module.get()

        if section == "platform":
            assert cfg.platform.host == defaults.ITENTIAL_MCP_PLATFORM_HOST
        elif section == "auth":
            assert cfg.auth.type == defaults.ITENTIAL_MCP_SERVER_AUTH_TYPE
        else:
            assert cfg.server.transport == defaults.ITENTIAL_MCP_SERVER_TRANSPORT

    def test_empty_string_env_var_counts_as_set(self, tmp_path, monkeypatch):
        """An env var set to "" must still beat the config file value.

        Matches parser.py's `in os.environ` semantics -- membership, not
        truthiness, determines precedence.
        """
        _clear_itential_env(monkeypatch)

        config_path = _write_config_file(tmp_path, "server", "include_tags", "file_tag")
        monkeypatch.setenv("ITENTIAL_MCP_CONFIG", config_path)
        monkeypatch.setenv("ITENTIAL_MCP_SERVER_INCLUDE_TAGS", "")

        assert "ITENTIAL_MCP_SERVER_INCLUDE_TAGS" in os.environ

        cfg = config_module.get()

        assert cfg.server.include_tags == ""
        assert cfg.server.include_tags != "file_tag"

    def test_cli_flag_beats_file_when_no_env_var(self, tmp_path, monkeypatch):
        """A CLI flag (funneled into os.environ by parser.py) beats the
        config file when no real env var is set."""
        _clear_itential_env(monkeypatch)
        # _get_arguments_from_config() is an independent lru_cache in
        # cli/argument_groups.py. It is unrelated to this fix but some
        # tests in tests/test_cli.py mock its fields() dependency and
        # populate this cache with mocked data without clearing it
        # afterward, which otherwise leaks into any later test in the
        # same session that calls parse_args(). Clear it defensively so
        # this test is order-independent.
        argument_groups._get_arguments_from_config.cache_clear()

        config_path = _write_config_file(tmp_path, "server", "transport", "stdio")
        monkeypatch.setenv("ITENTIAL_MCP_CONFIG", config_path)

        runtime.parse_args(["run", "--transport", "sse"])

        cfg = config_module.get()

        assert cfg.server.transport == "sse"

    def test_env_var_beats_cli_flag_and_file(self, tmp_path, monkeypatch):
        """A real env var beats both a CLI flag and the config file.

        parser.py's own `if envkey not in os.environ` guard prevents the
        CLI flag from overwriting a real env var; the loader fix then
        keeps the file value out too.
        """
        _clear_itential_env(monkeypatch)
        argument_groups._get_arguments_from_config.cache_clear()

        config_path = _write_config_file(tmp_path, "server", "transport", "stdio")
        monkeypatch.setenv("ITENTIAL_MCP_CONFIG", config_path)
        monkeypatch.setenv("ITENTIAL_MCP_SERVER_TRANSPORT", "http")

        runtime.parse_args(["run", "--transport", "sse"])

        # The real env var must not have been overwritten by the CLI flag.
        assert os.environ["ITENTIAL_MCP_SERVER_TRANSPORT"] == "http"

        cfg = config_module.get()

        assert cfg.server.transport == "http"

    def test_unknown_file_key_passes_through_unfiltered(self, tmp_path, monkeypatch):
        """An unrecognized field name must reach the constructor unfiltered.

        _env_key_for_field() returns None for a name with no matching
        pydantic field, so _filter_file_data() passes it through
        unchanged rather than dropping it. Note: ServerConfig (a Pydantic
        dataclass without extra="forbid") silently ignores unknown
        constructor kwargs -- that behavior is pydantic's own default and
        predates this fix; the assertion here is that the guard itself
        does not add any additional filtering for unknown keys.
        """
        _clear_itential_env(monkeypatch)

        config_path = _write_config_file(
            tmp_path, "server", "not_a_real_field", "some-value"
        )
        monkeypatch.setenv("ITENTIAL_MCP_CONFIG", config_path)

        # Must not raise from the guard itself; server config still loads
        # using its defaults for every real field.
        cfg = config_module.get()
        assert cfg.server.transport == defaults.ITENTIAL_MCP_SERVER_TRANSPORT

    def test_unknown_file_key_with_invalid_value_on_real_field_raises(
        self, tmp_path, monkeypatch
    ):
        """A real field with an invalid file value still raises validation
        errors, proving the guard does not swallow genuine bad input."""
        _clear_itential_env(monkeypatch)

        config_path = _write_config_file(tmp_path, "server", "transport", "bogus")
        monkeypatch.setenv("ITENTIAL_MCP_CONFIG", config_path)

        with pytest.raises(Exception):
            config_module.get()

    def test_auth_server_auth_prefix_env_resolution(self, tmp_path, monkeypatch):
        """Proves the SERVER_AUTH env-key resolution is used, not a naive
        ITENTIAL_MCP_AUTH_* guess."""
        _clear_itential_env(monkeypatch)

        config_path = _write_config_file(tmp_path, "auth", "type", "jwt")
        monkeypatch.setenv("ITENTIAL_MCP_CONFIG", config_path)
        monkeypatch.setenv("ITENTIAL_MCP_SERVER_AUTH_TYPE", "none")

        cfg = config_module.get()

        assert cfg.auth.type == "none"


# Auth-only subset of _PRECEDENCE_CASES, used to build the documented
# "[server] auth_<field> = ..." spelling (see docs/mcp.conf.example) from
# the existing "[auth] <field> = ..." rows.
_AUTH_PRECEDENCE_CASES = [c for c in _PRECEDENCE_CASES if c[0] == "auth"]

# A representative spread for bug #26, plus one oauth_* field to also
# exercise bug #27 on the [server] spelling.
_SERVER_AUTH_SAMPLE_KEYS = {"type", "jwks_uri", "public_key", "oauth_client_id"}
_SERVER_AUTH_SAMPLE_CASES = [
    c for c in _AUTH_PRECEDENCE_CASES if c[1] in _SERVER_AUTH_SAMPLE_KEYS
]

# All 7 oauth_* fields, for bug #27's mangling regression test.
_OAUTH_FIELD_CASES = [c for c in _AUTH_PRECEDENCE_CASES if c[1].startswith("oauth_")]

assert len(_OAUTH_FIELD_CASES) == 7, (
    f"Expected 7 oauth_* fields, found {len(_OAUTH_FIELD_CASES)}"
)


def _write_server_auth_config_file(tmp_path, file_key: str, value: str):
    """Write a config file with a single auth field under [server].

    Mirrors the documented spelling from docs/mcp.conf.example, e.g.
    "[server]\\nauth_type = jwt".

    Args:
        tmp_path: pytest tmp_path fixture directory.
        file_key: The bare AuthConfig field name (e.g. "type",
            "oauth_client_id").
        value: The string value to write.

    Returns:
        str: The path to the written config file.

    Raises:
        None.
    """
    return _write_config_file(tmp_path, "server", f"auth_{file_key}", value)


class TestConfigFileAuthSectionParsing:
    """Regression tests for Tier B #26 and #27 (config-loader auth parsing).

    #26: documented "[server] auth_*" / "[server] auth_oauth_*" file keys
    were silently dropped because the broad "server_" dispatch check ran
    before the more specific "server_auth_"/"auth_" check.

    #27: a global (non-prefix) string replace mangled every oauth_* field
    name (e.g. "oauth_client_id" -> "oclient_id") once it did reach the
    auth arm.
    """

    @pytest.mark.parametrize(
        "section,file_key,env_var,file_value,env_value,expected",
        _SERVER_AUTH_SAMPLE_CASES,
        ids=[f"server.auth_{c[1]}" for c in _SERVER_AUTH_SAMPLE_CASES],
    )
    def test_server_section_auth_keys_route_to_auth_config(
        self,
        tmp_path,
        monkeypatch,
        section,
        file_key,
        env_var,
        file_value,
        env_value,
        expected,
    ):
        """Documented "[server] auth_<field>" keys must populate AuthConfig.

        Pre-fix, these keys land in server_data (as "auth_<field>",
        stripped only of "server_") and are silently dropped by
        ServerConfig's constructor, so cfg.auth.<field> stays at its
        default. Post-fix they route to auth_data with the field name
        intact.
        """
        _clear_itential_env(monkeypatch)

        config_path = _write_server_auth_config_file(tmp_path, file_key, file_value)
        monkeypatch.setenv("ITENTIAL_MCP_CONFIG", config_path)

        cfg = config_module.get()

        assert getattr(cfg.auth, file_key) == file_value

    @pytest.mark.parametrize(
        "section,file_key,env_var,file_value,env_value,expected",
        _OAUTH_FIELD_CASES,
        ids=[f"server.auth_{c[1]}" for c in _OAUTH_FIELD_CASES],
    )
    def test_oauth_field_names_not_mangled_server_section(
        self,
        tmp_path,
        monkeypatch,
        section,
        file_key,
        env_var,
        file_value,
        env_value,
        expected,
    ):
        """Every oauth_* field survives the documented [server] spelling.

        Pre-fix: the [server] spelling drops entirely (bug #26). Once #26
        is fixed without #27, the inner "auth_" substring in "oauth_*"
        would still be stripped (e.g. "oauth_client_id" -> "oclient_id"),
        so this must also fail pre-#27-fix.
        """
        _clear_itential_env(monkeypatch)

        config_path = _write_server_auth_config_file(tmp_path, file_key, file_value)
        monkeypatch.setenv("ITENTIAL_MCP_CONFIG", config_path)

        cfg = config_module.get()

        assert getattr(cfg.auth, file_key) == file_value

    @pytest.mark.parametrize(
        "section,file_key,env_var,file_value,env_value,expected",
        _OAUTH_FIELD_CASES,
        ids=[f"auth.{c[1]}" for c in _OAUTH_FIELD_CASES],
    )
    def test_oauth_field_names_not_mangled_auth_section(
        self,
        tmp_path,
        monkeypatch,
        section,
        file_key,
        env_var,
        file_value,
        env_value,
        expected,
    ):
        """Every oauth_* field survives the undocumented [auth] spelling.

        Pre-fix: "[auth] oauth_client_id" resolves to "oclient_id" via the
        global replace, so cfg.auth.oauth_client_id stays None.
        """
        _clear_itential_env(monkeypatch)

        config_path = _write_config_file(tmp_path, "auth", file_key, file_value)
        monkeypatch.setenv("ITENTIAL_MCP_CONFIG", config_path)

        cfg = config_module.get()

        assert getattr(cfg.auth, file_key) == file_value

    @pytest.mark.parametrize(
        "raw_key,expected",
        [
            ("server_auth_oauth_client_id", "oauth_client_id"),
            ("server_auth_type", "type"),
            ("auth_oauth_client_id", "oauth_client_id"),
            ("auth_type", "type"),
            ("auth_required_scopes", "required_scopes"),
        ],
        ids=[
            "server_auth_oauth_client_id",
            "server_auth_type",
            "auth_oauth_client_id",
            "auth_type",
            "auth_required_scopes",
        ],
    )
    def test_strip_auth_prefix(self, raw_key, expected):
        """Direct unit test of the _strip_auth_prefix() helper."""
        assert _strip_auth_prefix(raw_key) == expected

    def test_server_section_nonauth_keys_still_route_to_server(
        self, tmp_path, monkeypatch
    ):
        """Plain [server] keys must still route to ServerConfig after the
        dispatch-order reorder, not be accidentally diverted into auth."""
        _clear_itential_env(monkeypatch)

        config_path = _write_config_file(tmp_path, "server", "transport", "sse")
        monkeypatch.setenv("ITENTIAL_MCP_CONFIG", config_path)

        cfg = config_module.get()

        assert cfg.server.transport == "sse"

    def test_env_beats_server_section_auth_oauth_field(self, tmp_path, monkeypatch):
        """ITENTIAL_MCP_SERVER_AUTH_OAUTH_CLIENT_ID still beats a
        "[server] auth_oauth_client_id" file value.

        Confirms #403's env/file precedence fix composes correctly with
        the newly-fixed [server] auth dispatch path.
        """
        _clear_itential_env(monkeypatch)

        config_path = _write_server_auth_config_file(
            tmp_path, "oauth_client_id", "file-client-id"
        )
        monkeypatch.setenv("ITENTIAL_MCP_CONFIG", config_path)
        monkeypatch.setenv("ITENTIAL_MCP_SERVER_AUTH_OAUTH_CLIENT_ID", "env-client-id")

        cfg = config_module.get()

        assert cfg.auth.oauth_client_id == "env-client-id"

    def test_auth_section_still_works_unchanged(self, tmp_path, monkeypatch):
        """The undocumented [auth] section (bare field names) must keep
        working exactly as before -- no regression from the reorder or
        the prefix-strip fix."""
        _clear_itential_env(monkeypatch)

        config_path = _write_config_file(tmp_path, "auth", "type", "jwt")
        monkeypatch.setenv("ITENTIAL_MCP_CONFIG", config_path)

        cfg = config_module.get()

        assert cfg.auth.type == "jwt"
