# Copyright (c) 2025 Itential, Inc
# GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)

import sys
from unittest.mock import AsyncMock, MagicMock

import pytest

from itential_mcp import server


def test_register_tools_imports_and_registers_functions(tmp_path, monkeypatch):
    # Setup mock tools directory
    tools_dir = tmp_path / "tools"
    tools_dir.mkdir()
    tool_file = tools_dir / "sample.py"
    tool_file.write_text("def test_func():\n    return True")

    # Patch __file__ to trick server into using our tmp tools dir
    monkeypatch.setattr(server, "__file__", str(tmp_path / "server.py"))

    # Patch importlib and FastMCP behavior
    mock_add_tool = MagicMock()
    mock_mcp = MagicMock()
    mock_mcp.add_tool = mock_add_tool

    server.register_tools(mock_mcp)
    assert mock_add_tool.called


@pytest.mark.asyncio
async def test_run_stdio(monkeypatch):
    mock_run_async = AsyncMock()
    mock_mcp_class = MagicMock(return_value=MagicMock(run_async=mock_run_async))

    monkeypatch.setattr(server, "FastMCP", mock_mcp_class)

    exit_calls = []

    def fake_exit(code):
        exit_calls.append(code)
        raise SystemExit()

    monkeypatch.setattr(sys, "exit", fake_exit)

    await server.run(transport="stdio", log_level="INFO")
    mock_run_async.assert_awaited_once()


@pytest.mark.asyncio
async def test_run_invalid_transport_raises():
    with pytest.raises(ValueError, match="invalid setting for transport"):
        await server.run(transport="invalid")


@pytest.mark.asyncio
async def test_run_invalid_log_level_raises():
    with pytest.raises(ValueError, match="invalid setting for log_level"):
        await server.run(log_level="INVALID")

