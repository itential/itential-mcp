# Copyright (c) 2025 Itential, Inc
# GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)

import os
import inspect
from unittest.mock import Mock, patch
from io import StringIO

import pytest

from itential_mcp import app
from itential_mcp.cli import Parser


class TestParseArgs:
    """Test cases for parse_args function"""

    @patch('itential_mcp.commands.run')
    @patch('itential_mcp.cli._get_arguments_from_config')
    def test_parse_args_run_command(self, mock_config_args, mock_run_cmd):
        """Test parsing run command"""
        mock_config_args.return_value = []
        
        async def mock_async_func():
            return 0
        
        mock_run_cmd.return_value = (mock_async_func, None, None)
        
        result = app.parse_args(["run"])
        
        assert result is not None
        assert len(result) == 3
        func, args, kwargs = result
        assert callable(func)
        assert inspect.iscoroutinefunction(func)
        assert args == ()
        assert kwargs == {}

    @patch('itential_mcp.cli.Parser.print_app_help')
    @patch('sys.exit')
    def test_parse_args_help(self, mock_exit, mock_print_help):
        """Test help argument parsing"""
        mock_exit.side_effect = SystemExit(0)
        
        with pytest.raises(SystemExit):
            app.parse_args(["--help"])
        
        mock_print_help.assert_called_once()
        mock_exit.assert_called_once_with(0)

    @patch('itential_mcp.cli.Parser.print_app_help')
    @patch('sys.exit')
    def test_parse_args_no_command(self, mock_exit, mock_print_help):
        """Test parsing with no command"""
        mock_exit.side_effect = SystemExit(0)
        
        with pytest.raises(SystemExit):
            app.parse_args([])
        
        mock_print_help.assert_called_once()
        mock_exit.assert_called_once_with(0)

    @patch('itential_mcp.commands.version')
    @patch('itential_mcp.cli._get_arguments_from_config')
    def test_parse_args_version_command(self, mock_config_args, mock_version_cmd):
        """Test version command parsing"""
        mock_config_args.return_value = []
        
        async def mock_async_func():
            return 0
        
        mock_version_cmd.return_value = (mock_async_func, None, None)
        
        result = app.parse_args(["version"])
        
        assert result is not None
        mock_version_cmd.assert_called_once()

    @patch('itential_mcp.commands.tools')
    @patch('itential_mcp.cli._get_arguments_from_config')
    def test_parse_args_tools_command(self, mock_config_args, mock_tools_cmd):
        """Test tools command parsing"""
        mock_config_args.return_value = []
        
        async def mock_async_func():
            return 0
        
        mock_tools_cmd.return_value = (mock_async_func, None, None)
        
        result = app.parse_args(["tools"])
        
        assert result is not None
        mock_tools_cmd.assert_called_once()

    @patch('itential_mcp.commands.tags')
    @patch('itential_mcp.cli._get_arguments_from_config')
    def test_parse_args_tags_command(self, mock_config_args, mock_tags_cmd):
        """Test tags command parsing"""
        mock_config_args.return_value = []
        
        async def mock_async_func():
            return 0
        
        mock_tags_cmd.return_value = (mock_async_func, None, None)
        
        result = app.parse_args(["tags"])
        
        assert result is not None
        mock_tags_cmd.assert_called_once()

    @patch('itential_mcp.commands.call')
    @patch('itential_mcp.cli._get_arguments_from_config')
    def test_parse_args_call_command(self, mock_config_args, mock_call_cmd):
        """Test call command parsing"""
        mock_config_args.return_value = []
        
        async def mock_async_func(tool, params):
            return 0
        
        mock_call_cmd.return_value = (mock_async_func, ("test_tool", None), None)
        
        result = app.parse_args(["call", "test_tool"])
        
        assert result is not None
        mock_call_cmd.assert_called_once()

    @patch('os.environ', {})
    @patch('itential_mcp.commands.run')
    @patch('itential_mcp.cli._get_arguments_from_config')
    def test_parse_args_config_file(self, mock_config_args, mock_run_cmd):
        """Test config file argument"""
        mock_config_args.return_value = []
        
        async def mock_async_func():
            return 0
        
        mock_run_cmd.return_value = (mock_async_func, None, None)
        
        app.parse_args(["run", "--config", "/path/to/config.ini"])
        
        assert os.environ.get("ITENTIAL_MCP_CONFIG") == "/path/to/config.ini"

    @patch('os.environ', {"ITENTIAL_MCP_TRANSPORT": "sse"})
    @patch('itential_mcp.commands.run')
    @patch('itential_mcp.cli._get_arguments_from_config')
    def test_parse_args_legacy_environment_variables(self, mock_config_args, mock_run_cmd):
        """Test legacy environment variable migration"""
        mock_config_args.return_value = []
        
        async def mock_async_func():
            return 0
        
        mock_run_cmd.return_value = (mock_async_func, None, None)
        
        app.parse_args(["run"])
        
        # Legacy var should be moved to new var
        assert "ITENTIAL_MCP_TRANSPORT" not in os.environ
        assert os.environ.get("ITENTIAL_MCP_SERVER_TRANSPORT") == "sse"

    @patch('itential_mcp.commands.run')
    @patch('itential_mcp.cli._get_arguments_from_config')
    def test_parse_args_invalid_handler(self, mock_config_args, mock_run_cmd):
        """Test error handling for invalid command handler"""
        mock_config_args.return_value = []
        mock_run_cmd.return_value = (lambda: None, None, None)  # Not async
        
        with pytest.raises(TypeError, match="handler must be callable and awaitable"):
            app.parse_args(["run"])

    @patch('os.environ', {})
    @patch('itential_mcp.commands.run')
    @patch('itential_mcp.cli._get_arguments_from_config')
    def test_parse_args_environment_variable_setting(self, mock_config_args, mock_run_cmd):
        """Test environment variable setting for server and platform args"""
        # Mock config that would return server and platform arguments
        mock_config_args.return_value = []
        
        async def mock_async_func():
            return 0
        
        mock_run_cmd.return_value = (mock_async_func, None, None)
        
        # Create a mock namespace that includes server_ and platform_ attributes
        with patch('itential_mcp.cli.Parser.parse_args') as mock_parse:
            mock_args = Mock()
            mock_args.help = False
            mock_args.command = "run"
            mock_args.config = None
            mock_args._get_kwargs.return_value = [
                ("server_host", "example.com"),
                ("platform_username", "testuser"),
                ("other_arg", "value")
            ]
            mock_parse.return_value = mock_args
            
            app.parse_args(["run"])
            
            # Only server_ and platform_ args should be set as env vars
            assert os.environ.get("ITENTIAL_MCP_SERVER_HOST") == "example.com"
            assert os.environ.get("ITENTIAL_MCP_PLATFORM_USERNAME") == "testuser"
            assert "ITENTIAL_MCP_OTHER_ARG" not in os.environ


class TestLegacyEnvVars:
    """Test cases for legacy environment variable constants"""

    def test_legacy_env_vars_constant(self):
        """Test LEGACY_ENV_VARS constant"""
        assert isinstance(app.LEGACY_ENV_VARS, frozenset)
        assert len(app.LEGACY_ENV_VARS) == 4
        
        # Check specific mappings
        expected_mappings = {
            ("ITENTIAL_MCP_TRANSPORT", "ITENTIAL_MCP_SERVER_TRANSPORT"),
            ("ITENTIAL_MCP_HOST", "ITENTIAL_MCP_SERVER_HOST"),
            ("ITENTIAL_MCP_PORT", "ITENTIAL_MCP_SERVER_PORT"),
            ("ITENTIAL_MCP_LOG_LEVEL", "ITENTIAL_MCP_SERVER_LOG_LEVEL"),
        }
        
        assert app.LEGACY_ENV_VARS == expected_mappings


class TestRun:
    """Test cases for run function"""

    @patch('asyncio.run')
    @patch('itential_mcp.app.parse_args')
    @patch('sys.argv', ['itential-mcp', 'run'])
    def test_run_success(self, mock_parse_args, mock_asyncio_run):
        """Test successful run"""
        async def mock_func():
            return 0
        
        mock_parse_args.return_value = (mock_func, (), {})
        mock_asyncio_run.return_value = 0
        
        result = app.run()
        
        assert result == 0
        mock_parse_args.assert_called_once_with(['run'])
        mock_asyncio_run.assert_called_once()

    @patch('asyncio.run')
    @patch('itential_mcp.app.parse_args')
    @patch('sys.argv', ['itential-mcp', 'run', '--config', '/path/config.ini'])
    def test_run_with_args(self, mock_parse_args, mock_asyncio_run):
        """Test run with arguments"""
        async def mock_func(*args, **kwargs):
            return 0
        
        mock_parse_args.return_value = (mock_func, ('arg1',), {'key': 'value'})
        mock_asyncio_run.return_value = 0
        
        result = app.run()
        
        assert result == 0
        mock_parse_args.assert_called_once_with(['run', '--config', '/path/config.ini'])
        mock_asyncio_run.assert_called_once()

    @patch('traceback.print_exc')
    @patch('sys.exit')
    @patch('itential_mcp.app.parse_args')
    @patch('sys.argv', ['itential-mcp', 'run'])
    def test_run_exception_handling(self, mock_parse_args, mock_sys_exit, mock_print_exc):
        """Test exception handling in run"""
        mock_parse_args.side_effect = Exception("Test exception")
        
        app.run()
        
        mock_print_exc.assert_called_once()
        mock_sys_exit.assert_called_once_with(1)

    @patch('asyncio.run')
    @patch('itential_mcp.app.parse_args')
    @patch('sys.argv', ['itential-mcp', 'version'])
    def test_run_version_command(self, mock_parse_args, mock_asyncio_run):
        """Test run with version command"""
        async def mock_func():
            return 0
        
        mock_parse_args.return_value = (mock_func, (), {})
        mock_asyncio_run.return_value = 0
        
        result = app.run()
        
        assert result == 0
        mock_parse_args.assert_called_once_with(['version'])
        mock_asyncio_run.assert_called_once()


class TestParser:
    """Test cases for CLI Parser functionality"""

    @patch('sys.stdout', new_callable=StringIO)
    def test_parser_print_app_help(self, mock_stdout):
        """Test Parser print_app_help method"""
        parser = Parser(
            prog="test-prog",
            description="Test description"
        )
        
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

    @patch('sys.stdout', new_callable=StringIO)
    def test_parser_print_help(self, mock_stdout):
        """Test Parser print_help method"""
        parser = Parser(
            prog="test-prog",
            description="Test description"
        )
        
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

    @patch('os.environ', {})
    @patch('itential_mcp.commands.run')
    @patch('itential_mcp.cli._get_arguments_from_config')
    def test_full_argument_processing_integration(self, mock_config_args, mock_run_cmd):
        """Test full argument processing flow"""
        mock_config_args.return_value = []
        
        async def mock_async_func():
            return 0
        
        mock_run_cmd.return_value = (mock_async_func, None, None)
        
        # Mock the argument parsing to simulate server and platform arguments
        with patch('itential_mcp.cli.Parser.parse_args') as mock_parse:
            mock_args = Mock()
            mock_args.help = False
            mock_args.command = "run"
            mock_args.config = "/path/to/config.ini"
            mock_args._get_kwargs.return_value = [
                ("server_host", "example.com"),
                ("platform_username", "testuser"),
            ]
            mock_parse.return_value = mock_args
            
            result = app.parse_args(["run"])
            
            # Verify function returned
            assert result is not None
            func, args, kwargs = result
            assert callable(func)
            
            # Verify environment variables were set
            assert os.environ.get("ITENTIAL_MCP_SERVER_HOST") == "example.com"
            assert os.environ.get("ITENTIAL_MCP_PLATFORM_USERNAME") == "testuser"
            assert os.environ.get("ITENTIAL_MCP_CONFIG") == "/path/to/config.ini"