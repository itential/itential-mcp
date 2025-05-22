# Copyright (c) 2025 Itential, Inc
# GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)

import os

from itential_mcp.config import get


class TestConfig:
    def setup_method(self):
        # Clear and setup env before each test
        self.env_backup = dict(os.environ)
        os.environ.clear()

    def teardown_method(self):
        # Restore environment after each test
        os.environ.clear()
        os.environ.update(self.env_backup)

    def test_config_defaults(self):
        expected = {
            "host": "localhost",
            "port": 0,
            "use_tls": True,
            "verify": True,
            "user": "admin",
            "password": "admin",
            "client_id": None,
            "client_secret": None,
            "timeout": 30,
        }
        assert get() == expected

    def test_config_with_env_vars(self):
        os.environ.update({
            "ITENTIAL_MCP_PLATFORM_HOST": "platform.local",
            "ITENTIAL_MCP_PLATFORM_PORT": "443",
            "ITENTIAL_MCP_PLATFORM_DISABLE_TLS": "true",
            "ITENTIAL_MCP_PLATFORM_DISABLE_VERIFY": "true",
            "ITENTIAL_MCP_PLATFORM_USER": "itential",
            "ITENTIAL_MCP_PLATFORM_PASSWORD": "secret",
            "ITENTIAL_MCP_PLATFORM_CLIENT_ID": "client123",
            "ITENTIAL_MCP_PLATFORM_CLIENT_SECRET": "secret456",
            "ITENTIAL_MCP_PLATFORM_TIMEOUT": "123"
        })

        expected = {
            "host": "platform.local",
            "port": 443,
            "use_tls": False,
            "verify": False,
            "user": "itential",
            "password": "secret",
            "client_id": "client123",
            "client_secret": "secret456",
            "timeout": 123
        }

        assert get() == expected
