# Copyright (c) 2025 Itential, Inc
# GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

import os
import argparse
import inspect
from unittest.mock import Mock, patch
from io import StringIO

import pytest

from itential_mcp import app
from itential_mcp import runtime
from itential_mcp.cli import Parser
from itential_mcp.runtime import constants


class TestParseArgs:
    """Test cases for parse_args function"""

    @patch("itential_mcp.runtime.commands.run")
    @patch("itential_mcp.cli.argument_groups._get_arguments_from_config")
    def test_parse_args_run_command(self, mock_config_args, mock_run_cmd):
        """Test parsing run command"""
        mock_config_args.return_value = []

        async def mock_async_func():
            return 0

        mock_run_cmd.return_value = (mock_async_func, None, None)

        result = runtime.parse_args(["run"])

        assert result is not None
        assert len(result) == 3
        func, args, kwargs = result
        assert callable(func)
        assert inspect.iscoroutinefunction(func)
        assert args == ()
        assert kwargs == {}

    @patch("itential_mcp.cli.Parser.print_app_help")
    @patch("sys.exit")
    def test_parse_args_help(self, mock_exit, mock_print_help):
        """Test help argument parsing"""
        mock_exit.side_effect = SystemExit(0)

        with pytest.raises(SystemExit):
            runtime.parse_args(["--help"])

        mock_print_help.assert_called_once()
        mock_exit.assert_called_once_with(0)

    @patch("itential_mcp.cli.Parser.print_app_help")
    @patch("sys.exit")
    def test_parse_args_no_command(self, mock_exit, mock_print_help):
        """Test parsing bare invocation (no args at all) still prints help
        to stdout and exits 0 - no regression."""
        mock_exit.side_effect = SystemExit(0)

        with pytest.raises(SystemExit):
            runtime.parse_args([])

        mock_print_help.assert_called_once()
        mock_exit.assert_called_once_with(0)

    @patch("sys.stdout", new_callable=StringIO)
    @patch("sys.stderr", new_callable=StringIO)
    def test_parse_args_config_without_subcommand(self, mock_stderr, mock_stdout):
        """Test that supplying --config without a subcommand exits with
        code 2 and writes the config-specific hint to stderr, not stdout.

        This is the diagnostic behavior for the stdio-transport footgun
        where a host supplies --config but omits the required subcommand
        (e.g. `run`), which previously produced a silent exit-0/stdout-help
        result that was indistinguishable from a healthy stdio handshake.
        """
        with pytest.raises(SystemExit) as excinfo:
            runtime.parse_args(["--config", "/x.conf"])

        assert excinfo.value.code == 2

        stderr_output = mock_stderr.getvalue()
        stdout_output = mock_stdout.getvalue()

        first_line = stderr_output.splitlines()[0]
        assert first_line == constants.CONFIG_WITHOUT_SUBCOMMAND_HINT
        assert "--config" in first_line
        assert stdout_output == ""

    @patch("sys.stdout", new_callable=StringIO)
    @patch("sys.stderr", new_callable=StringIO)
    @patch("itential_mcp.cli.Parser.parse_args")
    def test_parse_args_other_arg_without_subcommand(
        self, mock_parse_args, mock_stderr, mock_stdout
    ):
        """Test that a non-empty args list without a subcommand and without
        --config also exits with code 2 and writes a generic hint to
        stderr, distinct from the --config-specific message.

        The global parser today only exposes --config and -h/--help, so
        this exercises the generic branch directly by supplying a parsed
        namespace where command and config are both None, matching what
        would occur if a future global flag were added without a
        subcommand.
        """
        mock_parse_args.return_value = argparse.Namespace(
            help=False, command=None, config=None
        )

        with pytest.raises(SystemExit) as excinfo:
            runtime.parse_args(["--some-future-flag"])

        assert excinfo.value.code == 2

        stderr_output = mock_stderr.getvalue()
        stdout_output = mock_stdout.getvalue()

        first_line = stderr_output.splitlines()[0]
        assert first_line == constants.MISSING_SUBCOMMAND_MESSAGE
        assert first_line != constants.CONFIG_WITHOUT_SUBCOMMAND_HINT
        assert stdout_output == ""

    @patch("sys.stdout", new_callable=StringIO)
    @patch("sys.stderr", new_callable=StringIO)
    def test_parse_args_env_configured_without_subcommand(
        self, mock_stderr, mock_stdout, monkeypatch
    ):
        """Test that a bare invocation (zero argv args) with ITENTIAL_MCP_*
        environment variables set also exits with code 2 and writes the
        env-var-specific hint to stderr.

        This is the "universal" deployment shape where a container or
        supervisor sets ITENTIAL_MCP_* env vars for platform/server/auth
        config and execs itential-mcp with no CLI args at all, expecting
        the subcommand (typically `run`) to be part of the exec line. A
        zero-argv invocation must not be treated as the curious/interactive
        "just show me help" case when the environment clearly indicates a
        real, non-interactive deployment attempt.
        """
        monkeypatch.setenv("ITENTIAL_MCP_PLATFORM_HOST", "platform.example.com")

        with pytest.raises(SystemExit) as excinfo:
            runtime.parse_args([])

        assert excinfo.value.code == 2

        stderr_output = mock_stderr.getvalue()
        stdout_output = mock_stdout.getvalue()

        first_line = stderr_output.splitlines()[0]
        assert first_line == constants.ENV_CONFIGURED_WITHOUT_SUBCOMMAND_HINT
        assert first_line != constants.CONFIG_WITHOUT_SUBCOMMAND_HINT
        assert first_line != constants.MISSING_SUBCOMMAND_MESSAGE
        assert stdout_output == ""

    @patch("itential_mcp.cli.Parser.print_app_help")
    @patch("sys.exit")
    def test_parse_args_no_command_no_env_still_exits_zero(
        self, mock_exit, mock_print_help, monkeypatch
    ):
        """Test that a truly bare invocation (no args, no ITENTIAL_MCP_*
        env vars) is unaffected by the env-var detection and still prints
        help to stdout and exits 0 - confirms the new check is additive,
        not a regression for the plain interactive case."""
        for key in list(os.environ):
            if key.startswith(constants.ENV_PREFIX):
                monkeypatch.delenv(key, raising=False)

        mock_exit.side_effect = SystemExit(0)

        with pytest.raises(SystemExit):
            runtime.parse_args([])

        mock_print_help.assert_called_once()
        mock_exit.assert_called_once_with(0)

    @patch("itential_mcp.runtime.commands.version")
    @patch("itential_mcp.cli.argument_groups._get_arguments_from_config")
    def test_parse_args_version_command(self, mock_config_args, mock_version_cmd):
        """Test version command parsing"""
        mock_config_args.return_value = []

        async def mock_async_func():
            return 0

        mock_version_cmd.return_value = (mock_async_func, None, None)

        result = runtime.parse_args(["version"])

        assert result is not None
        mock_version_cmd.assert_called_once()

    @patch("itential_mcp.runtime.commands.tools")
    @patch("itential_mcp.cli.argument_groups._get_arguments_from_config")
    def test_parse_args_tools_command(self, mock_config_args, mock_tools_cmd):
        """Test tools command parsing"""
        mock_config_args.return_value = []

        async def mock_async_func():
            return 0

        mock_tools_cmd.return_value = (mock_async_func, None, None)

        result = runtime.parse_args(["tools"])

        assert result is not None
        mock_tools_cmd.assert_called_once()

    @patch("itential_mcp.runtime.commands.tags")
    @patch("itential_mcp.cli.argument_groups._get_arguments_from_config")
    def test_parse_args_tags_command(self, mock_config_args, mock_tags_cmd):
        """Test tags command parsing"""
        mock_config_args.return_value = []

        async def mock_async_func():
            return 0

        mock_tags_cmd.return_value = (mock_async_func, None, None)

        result = runtime.parse_args(["tags"])

        assert result is not None
        mock_tags_cmd.assert_called_once()

    @patch("itential_mcp.runtime.commands.call")
    @patch("itential_mcp.cli.argument_groups._get_arguments_from_config")
    def test_parse_args_call_command(self, mock_config_args, mock_call_cmd):
        """Test call command parsing"""
        mock_config_args.return_value = []

        async def mock_async_func(tool, params):
            return 0

        mock_call_cmd.return_value = (mock_async_func, ("test_tool", None), None)

        result = runtime.parse_args(["call", "test_tool"])

        assert result is not None
        mock_call_cmd.assert_called_once()

    @patch("os.environ", {})
    @patch("itential_mcp.runtime.commands.run")
    @patch("itential_mcp.cli.argument_groups._get_arguments_from_config")
    def test_parse_args_config_file(self, mock_config_args, mock_run_cmd):
        """Test config file argument"""
        mock_config_args.return_value = []

        async def mock_async_func():
            return 0

        mock_run_cmd.return_value = (mock_async_func, None, None)

        app.parse_args(["--config", "/path/to/config.ini", "run"])

        assert os.environ.get("ITENTIAL_MCP_CONFIG") == "/path/to/config.ini"

    @patch("itential_mcp.runtime.commands.run")
    @patch("itential_mcp.cli.argument_groups._get_arguments_from_config")
    def test_parse_args_invalid_handler(self, mock_config_args, mock_run_cmd):
        """Test error handling for invalid command handler"""
        mock_config_args.return_value = []
        mock_run_cmd.return_value = (lambda: None, None, None)  # Not async

        with pytest.raises(TypeError, match="handler must be callable and awaitable"):
            runtime.parse_args(["run"])

    @patch("os.environ", {})
    @patch("itential_mcp.runtime.commands.run")
    @patch("itential_mcp.cli.argument_groups._get_arguments_from_config")
    def test_parse_args_environment_variable_setting(
        self, mock_config_args, mock_run_cmd
    ):
        """Test environment variable setting for server and platform args"""
        # Mock config that would return server and platform arguments
        mock_config_args.return_value = []

        async def mock_async_func():
            return 0

        mock_run_cmd.return_value = (mock_async_func, None, None)

        # Create a mock namespace that includes server_ and platform_ attributes
        with patch("itential_mcp.cli.Parser.parse_args") as mock_parse:
            mock_args = Mock()
            mock_args.help = False
            mock_args.command = "run"
            mock_args.config = None
            mock_args.server_log_level = (
                "INFO"  # Set required attribute with valid log level
            )
            # Use Mock() with side_effect to return a list, avoiding AsyncMock creation
            mock_args._get_kwargs = Mock(
                return_value=[
                    ("server_host", "example.com"),
                    ("platform_username", "testuser"),
                    ("other_arg", "value"),
                ]
            )
            mock_parse.return_value = mock_args

            runtime.parse_args(["run"])

            # Only server_ and platform_ args should be set as env vars
            assert os.environ.get("ITENTIAL_MCP_SERVER_HOST") == "example.com"
            assert os.environ.get("ITENTIAL_MCP_PLATFORM_USERNAME") == "testuser"
            assert "ITENTIAL_MCP_OTHER_ARG" not in os.environ


class TestRun:
    """Test cases for run function"""

    @patch("asyncio.run")
    @patch("itential_mcp.app.parse_args")
    @patch("sys.argv", ["itential-mcp", "run"])
    def test_run_success(self, mock_parse_args, mock_asyncio_run):
        """Test successful run"""

        async def mock_func():
            return 0

        mock_parse_args.return_value = (mock_func, (), {})

        # Configure mock to consume coroutine properly
        def consume_coroutine(coro):
            coro.close()
            return 0

        mock_asyncio_run.side_effect = consume_coroutine

        result = app.run()

        assert result == 0
        mock_parse_args.assert_called_once_with(["run"])
        mock_asyncio_run.assert_called_once()

    @patch("asyncio.run")
    @patch("itential_mcp.app.parse_args")
    @patch("sys.argv", ["itential-mcp", "run", "--config", "/path/config.ini"])
    def test_run_with_args(self, mock_parse_args, mock_asyncio_run):
        """Test run with arguments"""

        async def mock_func(*args, **kwargs):
            return 0

        mock_parse_args.return_value = (mock_func, ("arg1",), {"key": "value"})

        # Configure mock to consume coroutine properly
        def consume_coroutine(coro):
            coro.close()
            return 0

        mock_asyncio_run.side_effect = consume_coroutine

        result = app.run()

        assert result == 0
        mock_parse_args.assert_called_once_with(["run", "--config", "/path/config.ini"])
        mock_asyncio_run.assert_called_once()

    @patch("itential_mcp.app.parse_args")
    @patch("sys.argv", ["itential-mcp", "run"])
    def test_run_exception_handling(self, mock_parse_args):
        """Test exception handling in run"""
        mock_parse_args.side_effect = Exception("Test exception")

        result = app.run()

        assert result == 1

    @patch("traceback.print_exc")
    @patch("os.environ", {"ITENTIAL_MCP_DEBUG": "true"})
    @patch("itential_mcp.app.parse_args")
    @patch("sys.argv", ["itential-mcp", "run"])
    def test_run_exception_handling_debug_mode(self, mock_parse_args, mock_print_exc):
        """Test exception handling in run with debug mode enabled"""
        mock_parse_args.side_effect = Exception("Test exception")

        result = app.run()

        assert result == 1
        mock_print_exc.assert_called_once()

    @patch("sys.stderr", new_callable=StringIO)
    @patch("os.environ", {})
    @patch("itential_mcp.app.parse_args")
    @patch("sys.argv", ["itential-mcp", "run"])
    def test_run_exception_handling_prints_clean_error_without_debug(
        self, mock_parse_args, mock_stderr
    ):
        """Test that a clean error line is written to stderr by default,
        without ITENTIAL_MCP_DEBUG set, and the exit code is 1."""
        mock_parse_args.side_effect = Exception("Test exception")

        result = app.run()

        assert result == 1
        output = mock_stderr.getvalue()
        assert "ERROR: Test exception" in output

    @patch("traceback.print_exc")
    @patch("sys.stderr", new_callable=StringIO)
    @patch("os.environ", {"ITENTIAL_MCP_DEBUG": "true"})
    @patch("itential_mcp.app.parse_args")
    @patch("sys.argv", ["itential-mcp", "run"])
    def test_run_exception_handling_prints_clean_error_and_traceback_in_debug_mode(
        self, mock_parse_args, mock_stderr, mock_print_exc
    ):
        """Test that in debug mode both the clean stderr error line AND the
        full traceback are emitted together, not just one or the other."""
        mock_parse_args.side_effect = Exception("Test exception")

        result = app.run()

        assert result == 1
        output = mock_stderr.getvalue()
        assert "ERROR: Test exception" in output
        mock_print_exc.assert_called_once()

    @patch("itential_mcp.core.logging.info")
    @patch("asyncio.run")
    @patch("itential_mcp.app.parse_args")
    @patch("sys.argv", ["itential-mcp", "run"])
    def test_run_keyboard_interrupt(
        self, mock_parse_args, mock_asyncio_run, mock_logging_info
    ):
        """Test that KeyboardInterrupt is handled gracefully and returns exit code 130"""

        async def mock_func():
            return 0

        mock_parse_args.return_value = (mock_func, (), {})
        mock_asyncio_run.side_effect = KeyboardInterrupt()

        result = app.run()

        assert result == 130
        mock_logging_info.assert_called_once_with("Application interrupted by user")

    @patch("asyncio.run")
    @patch("itential_mcp.app.parse_args")
    @patch("sys.argv", ["itential-mcp", "version"])
    def test_run_version_command(self, mock_parse_args, mock_asyncio_run):
        """Test run with version command"""

        async def mock_func():
            return 0

        mock_parse_args.return_value = (mock_func, (), {})

        # Configure mock to consume coroutine properly
        def consume_coroutine(coro):
            coro.close()
            return 0

        mock_asyncio_run.side_effect = consume_coroutine

        result = app.run()

        assert result == 0
        mock_parse_args.assert_called_once_with(["version"])
        mock_asyncio_run.assert_called_once()


class TestParser:
    """Test cases for CLI Parser functionality"""

    @patch("sys.stdout", new_callable=StringIO)
    def test_parser_print_app_help(self, mock_stdout):
        """Test Parser print_app_help method"""
        parser = Parser(prog="test-prog", description="Test description")

        # Add a subparser to test command display
        subparsers = parser.add_subparsers(dest="command")
        subparsers.add_parser("run", description="Run the server")

        # Add an argument to test options display
        parser.add_argument("--config", help="Configuration file")

        parser.print_app_help()

        output = mock_stdout.getvalue()
        assert "Test description" in output
        assert "Usage:" in output
        assert "test-prog <COMMAND> [OPTIONS]" in output
        assert "Commands:" in output
        assert "run" in output
        assert "Options:" in output
        assert "--config" in output

    @patch("sys.stdout", new_callable=StringIO)
    def test_parser_print_help(self, mock_stdout):
        """Test Parser print_help method"""
        parser = Parser(prog="test-prog", description="Test description")

        # Add arguments to test different scenarios
        parser.add_argument("--config", help="Configuration file")
        parser.add_argument("--verbose", action="store_true", help="Verbose output")

        parser.print_help()

        output = mock_stdout.getvalue()
        assert "Test description" in output
        assert "Usage:" in output
        assert "--config" in output
        assert "--verbose" in output


class TestIntegration:
    """Integration test cases"""

    @patch("os.environ", {})
    @patch("itential_mcp.runtime.commands.run")
    @patch("itential_mcp.cli.argument_groups._get_arguments_from_config")
    def test_full_argument_processing_integration(self, mock_config_args, mock_run_cmd):
        """Test full argument processing flow"""
        mock_config_args.return_value = []

        async def mock_async_func():
            return 0

        mock_run_cmd.return_value = (mock_async_func, None, None)

        # Mock the argument parsing to simulate server and platform arguments
        with patch("itential_mcp.cli.Parser.parse_args") as mock_parse:
            mock_args = Mock()
            mock_args.help = False
            mock_args.command = "run"
            mock_args.config = "/path/to/config.ini"
            mock_args.server_log_level = (
                "INFO"  # Set required attribute with valid log level
            )
            # Use Mock() to avoid AsyncMock creation
            mock_args._get_kwargs = Mock(
                return_value=[
                    ("server_host", "example.com"),
                    ("platform_username", "testuser"),
                ]
            )
            mock_parse.return_value = mock_args

            result = runtime.parse_args(["run"])

            # Verify function returned
            assert result is not None
            func, args, kwargs = result
            assert callable(func)

            # Verify environment variables were set
            assert os.environ.get("ITENTIAL_MCP_SERVER_HOST") == "example.com"
            assert os.environ.get("ITENTIAL_MCP_PLATFORM_USERNAME") == "testuser"
            assert os.environ.get("ITENTIAL_MCP_CONFIG") == "/path/to/config.ini"
