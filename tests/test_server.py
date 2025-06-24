# Copyright (c) 2025 Itential, Inc
# GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)

import sys
import asyncio

from unittest.mock import patch, MagicMock, AsyncMock

import pytest

from itential_mcp import server


@pytest.mark.asyncio
async def test_lifespan_yields_client_and_cache():
    mcp = MagicMock()
    async with server.lifespan(mcp) as context:
        assert "client" in context
        assert "cache" in context
        assert context["client"].__class__.__name__ == "PlatformClient"
        assert context["cache"].__class__.__name__ == "Cache"


def test_register_tools(tmp_path, monkeypatch):
    # Setup a temporary tools directory with a sample tool module
    tools_dir = tmp_path / "tools"
    tools_dir.mkdir()
    sample_tool = tools_dir / "echo.py"
    sample_tool.write_text(
        "def hello():\n"
        "    return 'world'\n"
    )

    # Patch __file__ to point to fake module with tools path
    monkeypatch.setattr(server, "__file__", str(tmp_path / "fake.py"))

    mcp = MagicMock()
    server.register_tools(mcp)

    # Tool `hello` from `echo` module should be added
    assert mcp.tool.called
    args, kwargs = mcp.tool.call_args
    assert args[0].__name__ == "hello"
    assert "tags" in kwargs
    assert "hello" in kwargs["tags"]


@pytest.mark.asyncio
@patch("itential_mcp.server.register_tools")
@patch("itential_mcp.server.FastMCP.run_async", new_callable=AsyncMock)
@patch("itential_mcp.server.config.get")
async def test_run_stdio_success(mock_config_get, mock_run_async, mock_register_tools):
    mock_config = MagicMock()
    mock_config.server = {
        "transport": "stdio",
        "log_level": "INFO",
        "include_tags": [],
        "exclude_tags": [],
    }
    mock_config_get.return_value = mock_config

    result = await server.run()
    assert mock_run_async.called
    assert result is None or result == 0


@patch("itential_mcp.server.register_tools", side_effect=Exception("tool error"))
@patch("itential_mcp.server.config.get")
def test_run_tool_import_error(mock_config_get, mock_register_tools):
    mock_config = MagicMock()
    mock_config.server = {
        "transport": "stdio",
        "log_level": "INFO",
        "include_tags": [],
        "exclude_tags": [],
    }
    mock_config_get.return_value = mock_config

    with patch.object(sys, "stderr"), pytest.raises(SystemExit) as excinfo:
        asyncio.run(server.run())

    assert excinfo.value.code == 1

