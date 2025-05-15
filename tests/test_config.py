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
            "client_secret": None
        }
        assert get() == expected

    def test_config_with_env_vars(self):
        os.environ.update({
            "PLATFORM_HOST": "platform.local",
            "PLATFORM_PORT": "443",
            "PLATFORM_DISABLE_TLS": "true",
            "PLATFORM_DISABLE_VERFITY": "true",
            "PLATFORM_USER": "itential",
            "PLATFORM_PASSWORD": "secret",
            "PLATFORM_CLIENT_ID": "client123",
            "PLATFORM_CLIENT_SECRET": "secret456"
        })

        expected = {
            "host": "platform.local",
            "port": 443,
            "use_tls": False,
            "verify": False,
            "user": "itential",
            "password": "secret",
            "client_id": "client123",
            "client_secret": "secret456"
        }

        assert get() == expected

