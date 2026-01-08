# Copyright (c) 2025 Itential, Inc
# GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

import inspect
from unittest.mock import patch
import argparse

import pytest

from itential_mcp.runtime.handlers import get_command_handler


class TestGetCommandHandler:
    """Test cases for get_command_handler function"""

    @patch("itential_mcp.runtime.commands.run")
    def test_get_command_handler_valid_command(self, mock_run_cmd):
        """Test get_command_handler with a valid command"""

        async def mock_async_func():
            return 0

        mock_run_cmd.return_value = (mock_async_func, None, None)

        args = argparse.Namespace(command="run")
        handler_func, handler_args, handler_kwargs = get_command_handler("run", args)

        assert callable(handler_func)
        assert inspect.iscoroutinefunction(handler_func)
        assert handler_args == ()
        assert handler_kwargs == {}

    @patch("itential_mcp.runtime.commands.call")
    def test_get_command_handler_with_args(self, mock_call_cmd):
        """Test get_command_handler with command that has arguments"""

        async def mock_async_func(tool, params):
            return 0

        mock_call_cmd.return_value = (mock_async_func, ("test_tool", None), {})

        args = argparse.Namespace(command="call", tool="test_tool", params=None)
        handler_func, handler_args, handler_kwargs = get_command_handler("call", args)

        assert callable(handler_func)
        assert inspect.iscoroutinefunction(handler_func)

    def test_get_command_handler_unknown_command(self):
        """Test get_command_handler with unknown command raises AttributeError"""
        args = argparse.Namespace(command="unknown")

        with pytest.raises(AttributeError) as exc_info:
            get_command_handler("nonexistent_command", args)

        assert "Unknown command: nonexistent_command" in str(exc_info.value)

    @patch("itential_mcp.runtime.commands.run")
    def test_get_command_handler_not_callable(self, mock_run_cmd):
        """Test get_command_handler raises TypeError when handler is not callable"""
        # Return a non-callable object
        mock_run_cmd.return_value = ("not_a_function", None, None)

        args = argparse.Namespace(command="run")

        with pytest.raises(TypeError) as exc_info:
            get_command_handler("run", args)

        assert "handler must be callable and awaitable" in str(exc_info.value)

    @patch("itential_mcp.runtime.commands.run")
    def test_get_command_handler_not_coroutine(self, mock_run_cmd):
        """Test get_command_handler raises TypeError when handler is not a coroutine"""

        # Return a regular function (not async)
        def regular_func():
            return 0

        mock_run_cmd.return_value = (regular_func, None, None)

        args = argparse.Namespace(command="run")

        with pytest.raises(TypeError) as exc_info:
            get_command_handler("run", args)

        assert "handler must be callable and awaitable" in str(exc_info.value)
