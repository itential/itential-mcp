# Copyright (c) 2025 Itential, Inc
# GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)

import os

from itential_mcp import cli

def test_parse_args_defaults(monkeypatch):
    monkeypatch.delenv("ITENTIAL_MCP_TRANSPORT", raising=False)
    cli.parse_args([])

    assert "ITENTIAL_MCP_SERVER_TRANSPORT" not in os.environ


def test_parse_args_custom_values():
    custom_args = [
        "--transport", "sse",
        "--host", "myhost",
        "--port", "9000",
        "--log-level", "DEBUG",
        "--platform-host", "platformhost",
        "--platform-user", "testuser",
        "--platform-password", "testpass"
    ]
    cli.parse_args(custom_args)

    assert os.environ["ITENTIAL_MCP_SERVER_TRANSPORT"] == "sse"
    assert os.environ["ITENTIAL_MCP_SERVER_HOST"] == "myhost"
    assert os.environ["ITENTIAL_MCP_SERVER_PORT"] == "9000"
    assert os.environ["ITENTIAL_MCP_SERVER_LOG_LEVEL"] == "DEBUG"
    assert os.environ["ITENTIAL_MCP_PLATFORM_HOST"] == "platformhost"
    assert os.environ["ITENTIAL_MCP_PLATFORM_USER"] == "testuser"


def test_env_variable_override(monkeypatch):
    monkeypatch.setenv("ITENTIAL_MCP_HOST", "envhost")
    monkeypatch.delenv("ITENTIAL_MCP_SERVER_HOST", raising=False)

    monkeypatch.setenv("ITENTIAL_MCP_PORT", "1234")
    monkeypatch.delenv("ITENTIAL_MCP_SERVER_PORT", raising=False)

    cli.parse_args([])

    assert os.environ["ITENTIAL_MCP_SERVER_HOST"] == "envhost"
    assert os.environ["ITENTIAL_MCP_SERVER_PORT"] == "1234"  # Still a string because it comes from env


def test_platform_env_variables_set(monkeypatch):
    monkeypatch.delenv("ITENTIAL_MCP_PLATFORM_USER", raising=False)
    cli.parse_args(["--platform-user", "envonly"])
    assert os.environ["ITENTIAL_MCP_PLATFORM_USER"] == "envonly"

