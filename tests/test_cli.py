# Copyright (c) 2025 Itential, Inc
# GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)

import os
from itential_mcp.cli import parse_args


class TestCLI:
    def setup_method(self):
        self.original_environ = dict(os.environ)
        os.environ.clear()

    def teardown_method(self):
        os.environ.clear()
        os.environ.update(self.original_environ)

    def test_default_arguments(self):
        args = []
        parsed = parse_args(args)

        assert parsed["transport"] == "stdio"
        assert parsed["host"] == "localhost"
        assert parsed["port"] == 8000
        assert parsed["log_level"] == "INFO"

        assert os.environ["ITENTIAL_MCP_PLATFORM_HOST"] == "localhost"
        assert os.environ["ITENTIAL_MCP_PLATFORM_PORT"] == "0"
        assert os.environ["ITENTIAL_MCP_PLATFORM_USER"] == "admin"
        assert os.environ["ITENTIAL_MCP_PLATFORM_PASSWORD"] == "admin"

    def test_explicit_arguments_override_defaults(self):
        args = [
            "--transport", "sse",
            "--host", "0.0.0.0",
            "--port", "9000",
            "--log-level", "DEBUG",
            "--platform-host", "platform.local",
            "--platform-port", "443",
            "--platform-disable-tls",
            "--platform-disable-verify",
            "--platform-user", "itential",
            "--platform-password", "secret",
            "--platform-client-id", "cid",
            "--platform-client-secret", "csecret"
        ]

        parsed = parse_args(args)

        assert parsed["transport"] == "sse"
        assert parsed["host"] == "0.0.0.0"
        assert parsed["port"] == 9000
        assert parsed["log_level"] == "DEBUG"

        assert os.environ["ITENTIAL_MCP_PLATFORM_HOST"] == "platform.local"
        assert os.environ["ITENTIAL_MCP_PLATFORM_PORT"] == "443"
        assert os.environ["ITENTIAL_MCP_PLATFORM_DISABLE_TLS"] == "True"
        assert os.environ["ITENTIAL_MCP_PLATFORM_DISABLE_VERIFY"] == "True"
        assert os.environ["ITENTIAL_MCP_PLATFORM_USER"] == "itential"
        assert os.environ["ITENTIAL_MCP_PLATFORM_PASSWORD"] == "secret"
        assert os.environ["ITENTIAL_MCP_PLATFORM_CLIENT_ID"] == "cid"
        assert os.environ["ITENTIAL_MCP_PLATFORM_CLIENT_SECRET"] == "csecret"

    def test_env_var_override(self):
        os.environ["ITENTIAL_MCP_TRANSPORT"] = "sse"
        os.environ["ITENTIAL_MCP_PORT"] = "1234"

        args = []
        parsed = parse_args(args)

        assert parsed["transport"] == "sse"
        assert parsed["port"] == 1234

