# Copyright (c) 2025 Itential, Inc
# GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

"""Unit tests for the defaults module."""

from itential_mcp import defaults


class TestServerDefaults:
    """Test server configuration default values."""

    def test_server_transport_default(self):
        """Test that server transport defaults to stdio."""
        assert defaults.ITENTIAL_MCP_SERVER_TRANSPORT == "stdio"

    def test_server_host_default(self):
        """Test that server host defaults to localhost."""
        assert defaults.ITENTIAL_MCP_SERVER_HOST == "127.0.0.1"

    def test_server_port_default(self):
        """Test that server port defaults to 8000."""
        assert defaults.ITENTIAL_MCP_SERVER_PORT == 8000

    def test_server_certificate_file_default(self):
        """Test that server certificate file defaults to empty string."""
        assert defaults.ITENTIAL_MCP_SERVER_CERTIFICATE_FILE == ""

    def test_server_private_key_file_default(self):
        """Test that server private key file defaults to empty string."""
        assert defaults.ITENTIAL_MCP_SERVER_PRIVATE_KEY_FILE == ""

    def test_server_path_default(self):
        """Test that server path defaults to /mcp."""
        assert defaults.ITENTIAL_MCP_SERVER_PATH == "/mcp"

    def test_server_log_level_default(self):
        """Test that server log level defaults to NONE."""
        assert defaults.ITENTIAL_MCP_SERVER_LOG_LEVEL == "NONE"

    def test_server_include_tags_default(self):
        """Test that server include tags defaults to None."""
        assert defaults.ITENTIAL_MCP_SERVER_INCLUDE_TAGS is None

    def test_server_exclude_tags_default(self):
        """Test that server exclude tags defaults to experimental,beta."""
        assert defaults.ITENTIAL_MCP_SERVER_EXCLUDE_TAGS == "experimental,beta"

    def test_server_auth_type_default(self):
        """Test that server auth type defaults to none."""
        assert defaults.ITENTIAL_MCP_SERVER_AUTH_TYPE == "none"

    def test_server_auth_jwks_uri_default(self):
        """Test that server auth JWKS URI defaults to None."""
        assert defaults.ITENTIAL_MCP_SERVER_AUTH_JWKS_URI is None

    def test_server_auth_public_key_default(self):
        """Test that server auth public key defaults to None."""
        assert defaults.ITENTIAL_MCP_SERVER_AUTH_PUBLIC_KEY is None

    def test_server_auth_issuer_default(self):
        """Test that server auth issuer defaults to None."""
        assert defaults.ITENTIAL_MCP_SERVER_AUTH_ISSUER is None

    def test_server_auth_audience_default(self):
        """Test that server auth audience defaults to None."""
        assert defaults.ITENTIAL_MCP_SERVER_AUTH_AUDIENCE is None

    def test_server_auth_algorithm_default(self):
        """Test that server auth algorithm defaults to None."""
        assert defaults.ITENTIAL_MCP_SERVER_AUTH_ALGORITHM is None

    def test_server_auth_required_scopes_default(self):
        """Test that server auth required scopes defaults to None."""
        assert defaults.ITENTIAL_MCP_SERVER_AUTH_REQUIRED_SCOPES is None


class TestPlatformDefaults:
    """Test platform configuration default values."""

    def test_platform_host_default(self):
        """Test that platform host defaults to localhost."""
        assert defaults.ITENTIAL_MCP_PLATFORM_HOST == "localhost"

    def test_platform_port_default(self):
        """Test that platform port defaults to 0."""
        assert defaults.ITENTIAL_MCP_PLATFORM_PORT == 0

    def test_platform_disable_tls_default(self):
        """Test that platform disable TLS defaults to False."""
        assert defaults.ITENTIAL_MCP_PLATFORM_DISABLE_TLS is False

    def test_platform_disable_verify_default(self):
        """Test that platform disable verify defaults to False."""
        assert defaults.ITENTIAL_MCP_PLATFORM_DISABLE_VERIFY is False

    def test_platform_user_default(self):
        """Test that platform user defaults to admin."""
        assert defaults.ITENTIAL_MCP_PLATFORM_USER == "admin"

    def test_platform_password_default(self):
        """Test that platform password defaults to admin."""
        assert defaults.ITENTIAL_MCP_PLATFORM_PASSWORD == "admin"

    def test_platform_client_id_default(self):
        """Test that platform client ID defaults to None."""
        assert defaults.ITENTIAL_MCP_PLATFORM_CLIENT_ID is None

    def test_platform_client_secret_default(self):
        """Test that platform client secret defaults to None."""
        assert defaults.ITENTIAL_MCP_PLATFORM_CLIENT_SECRET is None

    def test_platform_timeout_default(self):
        """Test that platform timeout defaults to 30."""
        assert defaults.ITENTIAL_MCP_PLATFORM_TIMEOUT == 30


class TestDefaultsModuleStructure:
    """Test the structure and organization of the defaults module."""

    def test_module_has_docstring(self):
        """Test that the defaults module has a docstring."""
        assert defaults.__doc__ is not None
        assert len(defaults.__doc__) > 0
        assert "Default configuration values" in defaults.__doc__

    def test_all_server_constants_exist(self):
        """Test that all expected server constants are defined."""
        expected_server_constants = [
            "ITENTIAL_MCP_SERVER_TRANSPORT",
            "ITENTIAL_MCP_SERVER_HOST",
            "ITENTIAL_MCP_SERVER_PORT",
            "ITENTIAL_MCP_SERVER_CERTIFICATE_FILE",
            "ITENTIAL_MCP_SERVER_PRIVATE_KEY_FILE",
            "ITENTIAL_MCP_SERVER_PATH",
            "ITENTIAL_MCP_SERVER_LOG_LEVEL",
            "ITENTIAL_MCP_SERVER_INCLUDE_TAGS",
            "ITENTIAL_MCP_SERVER_EXCLUDE_TAGS",
            "ITENTIAL_MCP_SERVER_TOOLS_PATH",
            "ITENTIAL_MCP_SERVER_AUTH_TYPE",
            "ITENTIAL_MCP_SERVER_AUTH_JWKS_URI",
            "ITENTIAL_MCP_SERVER_AUTH_PUBLIC_KEY",
            "ITENTIAL_MCP_SERVER_AUTH_ISSUER",
            "ITENTIAL_MCP_SERVER_AUTH_AUDIENCE",
            "ITENTIAL_MCP_SERVER_AUTH_ALGORITHM",
            "ITENTIAL_MCP_SERVER_AUTH_REQUIRED_SCOPES",
        ]

        for constant in expected_server_constants:
            assert hasattr(defaults, constant), f"Missing constant: {constant}"

    def test_all_platform_constants_exist(self):
        """Test that all expected platform constants are defined."""
        expected_platform_constants = [
            "ITENTIAL_MCP_PLATFORM_HOST",
            "ITENTIAL_MCP_PLATFORM_PORT",
            "ITENTIAL_MCP_PLATFORM_DISABLE_TLS",
            "ITENTIAL_MCP_PLATFORM_DISABLE_VERIFY",
            "ITENTIAL_MCP_PLATFORM_USER",
            "ITENTIAL_MCP_PLATFORM_PASSWORD",
            "ITENTIAL_MCP_PLATFORM_CLIENT_ID",
            "ITENTIAL_MCP_PLATFORM_CLIENT_SECRET",
            "ITENTIAL_MCP_PLATFORM_TIMEOUT",
        ]

        for constant in expected_platform_constants:
            assert hasattr(defaults, constant), f"Missing constant: {constant}"

    def test_constant_naming_convention(self):
        """Test that all constants follow the naming convention."""
        for attr_name in dir(defaults):
            if not attr_name.startswith("_") and attr_name.isupper():
                assert attr_name.startswith("ITENTIAL_MCP_"), (
                    f"Invalid constant name: {attr_name}"
                )


class TestDefaultValueTypes:
    """Test that default values have the correct types."""

    def test_server_transport_is_string(self):
        """Test that server transport is a string."""
        assert isinstance(defaults.ITENTIAL_MCP_SERVER_TRANSPORT, str)

    def test_server_host_is_string(self):
        """Test that server host is a string."""
        assert isinstance(defaults.ITENTIAL_MCP_SERVER_HOST, str)

    def test_server_port_is_int(self):
        """Test that server port is an integer."""
        assert isinstance(defaults.ITENTIAL_MCP_SERVER_PORT, int)

    def test_server_certificate_file_is_string(self):
        """Test that server certificate file is a string."""
        assert isinstance(defaults.ITENTIAL_MCP_SERVER_CERTIFICATE_FILE, str)

    def test_server_private_key_file_is_string(self):
        """Test that server private key file is a string."""
        assert isinstance(defaults.ITENTIAL_MCP_SERVER_PRIVATE_KEY_FILE, str)

    def test_server_path_is_string(self):
        """Test that server path is a string."""
        assert isinstance(defaults.ITENTIAL_MCP_SERVER_PATH, str)

    def test_server_log_level_is_string(self):
        """Test that server log level is a string."""
        assert isinstance(defaults.ITENTIAL_MCP_SERVER_LOG_LEVEL, str)

    def test_server_include_tags_is_none_or_string(self):
        """Test that server include tags is None or string."""
        value = defaults.ITENTIAL_MCP_SERVER_INCLUDE_TAGS
        assert value is None or isinstance(value, str)

    def test_server_exclude_tags_is_none_or_string(self):
        """Test that server exclude tags is None or string."""
        value = defaults.ITENTIAL_MCP_SERVER_EXCLUDE_TAGS
        assert value is None or isinstance(value, str)

    def test_server_tools_path_is_none_or_string(self):
        """Test that server tools path is None or string."""
        value = defaults.ITENTIAL_MCP_SERVER_TOOLS_PATH
        assert value is None or isinstance(value, str)

    def test_server_auth_type_is_string(self):
        """Test that server auth type is a string."""
        assert isinstance(defaults.ITENTIAL_MCP_SERVER_AUTH_TYPE, str)

    def test_server_auth_jwks_uri_is_none_or_string(self):
        """Test that server auth JWKS URI is None or string."""
        value = defaults.ITENTIAL_MCP_SERVER_AUTH_JWKS_URI
        assert value is None or isinstance(value, str)

    def test_server_auth_public_key_is_none_or_string(self):
        """Test that server auth public key is None or string."""
        value = defaults.ITENTIAL_MCP_SERVER_AUTH_PUBLIC_KEY
        assert value is None or isinstance(value, str)

    def test_server_auth_issuer_is_none_or_string(self):
        """Test that server auth issuer is None or string."""
        value = defaults.ITENTIAL_MCP_SERVER_AUTH_ISSUER
        assert value is None or isinstance(value, str)

    def test_server_auth_audience_is_none_or_string(self):
        """Test that server auth audience is None or string."""
        value = defaults.ITENTIAL_MCP_SERVER_AUTH_AUDIENCE
        assert value is None or isinstance(value, str)

    def test_server_auth_algorithm_is_none_or_string(self):
        """Test that server auth algorithm is None or string."""
        value = defaults.ITENTIAL_MCP_SERVER_AUTH_ALGORITHM
        assert value is None or isinstance(value, str)

    def test_server_auth_required_scopes_is_none_or_string(self):
        """Test that server auth required scopes is None or string."""
        value = defaults.ITENTIAL_MCP_SERVER_AUTH_REQUIRED_SCOPES
        assert value is None or isinstance(value, str)

    def test_platform_host_is_string(self):
        """Test that platform host is a string."""
        assert isinstance(defaults.ITENTIAL_MCP_PLATFORM_HOST, str)

    def test_platform_port_is_int(self):
        """Test that platform port is an integer."""
        assert isinstance(defaults.ITENTIAL_MCP_PLATFORM_PORT, int)

    def test_platform_disable_tls_is_bool(self):
        """Test that platform disable TLS is a boolean."""
        assert isinstance(defaults.ITENTIAL_MCP_PLATFORM_DISABLE_TLS, bool)

    def test_platform_disable_verify_is_bool(self):
        """Test that platform disable verify is a boolean."""
        assert isinstance(defaults.ITENTIAL_MCP_PLATFORM_DISABLE_VERIFY, bool)

    def test_platform_user_is_string(self):
        """Test that platform user is a string."""
        assert isinstance(defaults.ITENTIAL_MCP_PLATFORM_USER, str)

    def test_platform_password_is_string(self):
        """Test that platform password is a string."""
        assert isinstance(defaults.ITENTIAL_MCP_PLATFORM_PASSWORD, str)

    def test_platform_client_id_is_none_or_string(self):
        """Test that platform client ID is None or string."""
        value = defaults.ITENTIAL_MCP_PLATFORM_CLIENT_ID
        assert value is None or isinstance(value, str)

    def test_platform_client_secret_is_none_or_string(self):
        """Test that platform client secret is None or string."""
        value = defaults.ITENTIAL_MCP_PLATFORM_CLIENT_SECRET
        assert value is None or isinstance(value, str)

    def test_platform_timeout_is_int(self):
        """Test that platform timeout is an integer."""
        assert isinstance(defaults.ITENTIAL_MCP_PLATFORM_TIMEOUT, int)


class TestDefaultValueRanges:
    """Test that default values are within reasonable ranges."""

    def test_server_port_is_valid_port_number(self):
        """Test that server port is a valid port number."""
        port = defaults.ITENTIAL_MCP_SERVER_PORT
        assert 1 <= port <= 65535, f"Invalid port number: {port}"

    def test_platform_port_is_valid_port_number(self):
        """Test that platform port is a valid port number."""
        port = defaults.ITENTIAL_MCP_PLATFORM_PORT
        assert 0 <= port <= 65535, f"Invalid port number: {port}"

    def test_platform_timeout_is_positive(self):
        """Test that platform timeout is positive."""
        timeout = defaults.ITENTIAL_MCP_PLATFORM_TIMEOUT
        assert timeout > 0, f"Invalid timeout value: {timeout}"

    def test_server_transport_is_valid_option(self):
        """Test that server transport is a valid transport option."""
        transport = defaults.ITENTIAL_MCP_SERVER_TRANSPORT
        valid_transports = ["stdio", "sse", "http"]
        assert transport in valid_transports, f"Invalid transport: {transport}"

    def test_server_log_level_is_valid_option(self):
        """Test that server log level is a valid logging level."""
        log_level = defaults.ITENTIAL_MCP_SERVER_LOG_LEVEL
        valid_levels = [
            "DEBUG",
            "INFO",
            "WARNING",
            "ERROR",
            "CRITICAL",
            "DISABLED",
            "NONE",
        ]
        assert log_level in valid_levels, f"Invalid log level: {log_level}"

    def test_server_path_starts_with_slash(self):
        """Test that server path starts with a slash."""
        path = defaults.ITENTIAL_MCP_SERVER_PATH
        assert path.startswith("/"), f"Server path should start with '/': {path}"
