# Copyright (c) 2025 Itential, Inc
# GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)

import os
import configparser

import pytest

from itential_mcp import config as config_module


@pytest.fixture(autouse=True)
def clear_config_cache():
    """Ensure config.get() doesn't cache between tests"""
    config_module.get.cache_clear()
    yield
    config_module.get.cache_clear()


def test_get_config_from_env(monkeypatch):
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
    cp["server"] = {
        "host": "192.168.1.1",
        "port": "9000"
    }
    cp["platform"] = {
        "user": "fileuser",
        "password": "filepass",
        "disable_tls": "true"
    }

    with open(config_path, "w") as f:
        cp.write(f)

    for ele in os.environ.keys():
        if ele.startswith("ITENTIAL"):
            monkeypatch.delenv(ele, raising=False)

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
    monkeypatch.setenv("ITENTIAL_MCP_SERVER_INCLUDE_TAGS", "public,system")
    monkeypatch.setenv("ITENTIAL_MCP_SERVER_EXCLUDE_TAGS", "experimental,beta")

    cfg = config_module.get()

    assert cfg.server["include_tags"] == {"public", "system"}
    assert cfg.server["exclude_tags"] == {"experimental", "beta"}
    assert isinstance(cfg.platform, dict)
    assert "host" in cfg.platform

