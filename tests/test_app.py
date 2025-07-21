# Copyright (c) 2025 Itential, Inc
# GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)

import os
import inspect
from unittest.mock import Mock, patch
from io import StringIO

import pytest

from itential_mcp import app


class TestCli:
    """Test cases for the Cli class"""

    def test_cli_init(self):
        """Test Cli class initialization"""
        cli = app.Cli(
            prog="test-prog",
            add_help=False,
            description="Test description"
        )
        assert cli.prog == "test-prog"
        assert cli.description == "Test description"

    @patch('sys.stdout', new_callable=StringIO)
    def test_print_app_help(self, mock_stdout):
        """Test print_app_help method"""
        cli = app.Cli(
            prog="test-prog",
            description="Test description"
        )
        
        # Add a subparser to test command display
        subparsers = cli.add_subparsers(dest="command")
        subparsers.add_parser("run", description="Run the server")
        
        # Add an argument to test options display
        cli.add_argument("--config", help="Configuration file")
        
        cli.print_app_help()
        
        output = mock_stdout.getvalue()
        assert "Test description" in output
        assert "Usage:" in output
        assert "test-prog <command> [options]" in output
        assert "Commands:" in output
        assert "run" in output
        assert "Options:" in output
        assert "--config" in output

    @patch('sys.stdout', new_callable=StringIO)
    def test_print_help(self, mock_stdout):
        """Test print_help method"""
        cli = app.Cli(
            prog="test-prog",
            description="Test description"
        )
        
        # Add arguments to test different scenarios
        cli.add_argument("--config", help="Configuration file")
        cli.add_argument("--verbose", action="store_true", help="Verbose output")
        
        cli.print_help()
        
        output = mock_stdout.getvalue()
        assert "Test description" in output
        assert "Usage:" in output
        assert "test-prog [options]" in output
        assert "Global Options" in output
        assert "--config" in output
        assert "--verbose" in output

    @patch('itential_mcp.terminal.getcols')
    @patch('sys.stdout', new_callable=StringIO)
    def test_print_help_with_long_option(self, mock_stdout, mock_getcols):
        """Test print_help with long option names"""
        mock_getcols.return_value = 80
        
        cli = app.Cli(
            prog="test-prog",
            description="Test description"
        )
        
        # Add a long option to test wrapping
        cli.add_argument("--very-long-option-name", metavar="VALUE", help="A very long help string that should wrap")
        
        cli.print_help()
        
        output = mock_stdout.getvalue()
        assert "very-long-option-name" in output

    @patch('sys.stdout', new_callable=StringIO)
    def test_print_help_with_argument_groups(self, mock_stdout):
        """Test print_help with argument groups"""
        cli = app.Cli(
            prog="test-prog",
            description="Test description"
        )
        
        # Add argument groups
        server_group = cli.add_argument_group("Server Options")
        server_group.add_argument("--host", help="Server host")
        
        platform_group = cli.add_argument_group("Platform Options")
        platform_group.add_argument("--username", help="Platform username")
        
        cli.print_help()
        
        output = mock_stdout.getvalue()
        assert "Server Options" in output
        assert "Platform Options" in output
        assert "--host" in output
        assert "--username" in output


class TestParseArgs:
    """Test cases for parse_args function"""

    @patch('itential_mcp.app.fields')
    def test_parse_args_basic(self, mock_fields):
        """Test basic argument parsing"""
        # Mock config fields
        mock_field = Mock()
        mock_field.name = "server_host"
        mock_field.default = Mock()
        mock_field.default.json_schema_extra = {
            "x-itential-mcp-cli-enabled": True,
            "x-itential-mcp-arguments": ["--host"],
            "x-itential-mcp-options": {"type": str}
        }
        mock_field.default.description = "Server host"
        mock_field.default.default = "localhost"
        mock_fields.return_value = [mock_field]
        
        async def mock_async_func():
            return 0
        
        with patch('itential_mcp.commands.run') as mock_run_cmd:
            mock_run_cmd.return_value = (mock_async_func, [], {})
            
            result = app.parse_args(["run", "--host", "example.com"])
            
            assert result is not None
            assert len(result) == 3
            func, args, kwargs = result
            assert callable(func)
            assert inspect.iscoroutinefunction(func)

    @patch('itential_mcp.app.fields')
    def test_parse_args_help(self, mock_fields):
        """Test help argument parsing"""
        mock_fields.return_value = []
        
        with patch.object(app.Cli, 'print_app_help') as mock_print_help:
            with patch('sys.exit') as mock_exit:
                mock_exit.side_effect = SystemExit(0)
                with pytest.raises(SystemExit):
                    app.parse_args(["--help"])
                mock_print_help.assert_called_once()
                mock_exit.assert_called_once_with(0)

    @patch('itential_mcp.app.fields')
    def test_parse_args_no_command(self, mock_fields):
        """Test parsing with no command"""
        mock_fields.return_value = []
        
        with patch.object(app.Cli, 'print_app_help') as mock_print_help:
            with patch('sys.exit') as mock_exit:
                mock_exit.side_effect = SystemExit(0)
                with pytest.raises(SystemExit):
                    app.parse_args([])
                mock_print_help.assert_called_once()
                mock_exit.assert_called_once_with(0)

    @patch('os.environ', {})
    @patch('itential_mcp.app.fields')
    def test_parse_args_environment_variables(self, mock_fields):
        """Test environment variable setting"""
        mock_field = Mock()
        mock_field.name = "server_host"
        mock_field.default = Mock()
        mock_field.default.json_schema_extra = {
            "x-itential-mcp-cli-enabled": True,
            "x-itential-mcp-arguments": ["--host"],
            "x-itential-mcp-options": {"type": str}
        }
        mock_field.default.description = "Server host"
        mock_field.default.default = "localhost"
        mock_fields.return_value = [mock_field]
        
        async def mock_async_func():
            return 0
        
        with patch('itential_mcp.commands.run') as mock_run_cmd:
            mock_run_cmd.return_value = (mock_async_func, [], {})
            
            app.parse_args(["run", "--host", "example.com"])
            
            assert os.environ.get("ITENTIAL_MCP_SERVER_HOST") == "example.com"

    @patch('os.environ', {})
    @patch('itential_mcp.app.fields')
    def test_parse_args_config_file(self, mock_fields):
        """Test config file argument"""
        mock_fields.return_value = []
        
        async def mock_async_func():
            return 0
        
        with patch('itential_mcp.commands.run') as mock_run_cmd:
            mock_run_cmd.return_value = (mock_async_func, [], {})
            
            app.parse_args(["run", "--config", "/path/to/config.ini"])
            
            assert os.environ.get("ITENTIAL_MCP_CONFIG") == "/path/to/config.ini"

    @patch('os.environ', {"ITENTIAL_MCP_TRANSPORT": "sse"})
    @patch('itential_mcp.app.fields')
    def test_parse_args_legacy_environment_variables(self, mock_fields):
        """Test legacy environment variable migration"""
        mock_fields.return_value = []
        
        async def mock_async_func():
            return 0
        
        with patch('itential_mcp.commands.run') as mock_run_cmd:
            mock_run_cmd.return_value = (mock_async_func, [], {})
            
            app.parse_args(["run"])
            
            # Legacy var should be moved to new var
            assert "ITENTIAL_MCP_TRANSPORT" not in os.environ
            assert os.environ.get("ITENTIAL_MCP_SERVER_TRANSPORT") == "sse"

    @patch('itential_mcp.app.fields')
    def test_parse_args_version_command(self, mock_fields):
        """Test version command parsing"""
        mock_fields.return_value = []
        
        async def mock_async_func():
            return 0
        
        with patch('itential_mcp.commands.version') as mock_version_cmd:
            mock_version_cmd.return_value = (mock_async_func, [], {})
            
            result = app.parse_args(["version"])
            
            assert result is not None
            mock_version_cmd.assert_called_once()

    @patch('itential_mcp.app.fields')
    def test_parse_args_invalid_handler(self, mock_fields):
        """Test error handling for invalid command handler"""
        mock_fields.return_value = []
        
        with patch('itential_mcp.commands.run') as mock_run_cmd:
            mock_run_cmd.return_value = (lambda: None, [], {})  # Not async
            
            with pytest.raises(TypeError, match="handler must be callable and awaitable"):
                app.parse_args(["run"])

    @patch('itential_mcp.app.fields')
    def test_parse_args_string_value_processing(self, mock_fields):
        """Test string value processing for comma-separated values"""
        mock_field = Mock()
        mock_field.name = "server_tags"
        mock_field.default = Mock()
        mock_field.default.json_schema_extra = {
            "x-itential-mcp-cli-enabled": True,
            "x-itential-mcp-arguments": ["--tags"],
            "x-itential-mcp-options": {"type": str}
        }
        mock_field.default.description = "Server tags"
        mock_field.default.default = ""
        mock_fields.return_value = [mock_field]
        
        async def mock_async_func():
            return 0
        
        with patch('itential_mcp.commands.run') as mock_run_cmd:
            mock_run_cmd.return_value = (mock_async_func, [], {})
            
            app.parse_args(["run", "--tags", "tag1,tag2,tag3"])
            
            # Should process comma-separated values
            assert os.environ.get("ITENTIAL_MCP_SERVER_TAGS") == "tag1, tag2, tag3"


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
        
        mock_parse_args.return_value = (mock_func, [], {})
        mock_asyncio_run.return_value = 0
        
        result = app.run()
        
        assert result == 0
        mock_parse_args.assert_called_once_with(['run'])
        # Check that asyncio.run was called with the function
        assert mock_asyncio_run.call_count == 1

    @patch('asyncio.run')
    @patch('itential_mcp.app.parse_args')
    @patch('sys.argv', ['itential-mcp', 'run', '--host', 'example.com'])
    def test_run_with_args(self, mock_parse_args, mock_asyncio_run):
        """Test run with arguments"""
        async def mock_func(*args, **kwargs):
            return 0
        
        mock_parse_args.return_value = (mock_func, ['arg1'], {'key': 'value'})
        mock_asyncio_run.return_value = 0
        
        result = app.run()
        
        assert result == 0
        mock_parse_args.assert_called_once_with(['run', '--host', 'example.com'])
        # Check that asyncio.run was called with the function and args
        assert mock_asyncio_run.call_count == 1

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
        
        mock_parse_args.return_value = (mock_func, [], {})
        mock_asyncio_run.return_value = 0
        
        result = app.run()
        
        assert result == 0
        mock_parse_args.assert_called_once_with(['version'])
        # Check that asyncio.run was called with the function
        assert mock_asyncio_run.call_count == 1


class TestIntegration:
    """Integration test cases"""

    @patch('os.environ', {})
    @patch('itential_mcp.app.fields')
    def test_full_argument_processing_integration(self, mock_fields):
        """Test full argument processing flow"""
        # Mock multiple config fields
        server_field = Mock()
        server_field.name = "server_host"
        server_field.default = Mock()
        server_field.default.json_schema_extra = {
            "x-itential-mcp-cli-enabled": True,
            "x-itential-mcp-arguments": ["--host"],
            "x-itential-mcp-options": {"type": str}
        }
        server_field.default.description = "Server host"
        server_field.default.default = "localhost"
        
        platform_field = Mock()
        platform_field.name = "platform_username"
        platform_field.default = Mock()
        platform_field.default.json_schema_extra = {
            "x-itential-mcp-cli-enabled": True,
            "x-itential-mcp-arguments": ["--username"],
            "x-itential-mcp-options": {"type": str}
        }
        platform_field.default.description = "Platform username"
        platform_field.default.default = "admin"
        
        mock_fields.return_value = [server_field, platform_field]
        
        async def mock_async_func():
            return 0
        
        with patch('itential_mcp.commands.run') as mock_run_cmd:
            mock_run_cmd.return_value = (mock_async_func, [], {})
            
            result = app.parse_args([
                "run",
                "--host", "example.com",
                "--username", "testuser",
                "--config", "/path/to/config.ini"
            ])
            
            # Verify function returned
            assert result is not None
            func, args, kwargs = result
            assert callable(func)
            
            # Verify environment variables were set
            assert os.environ.get("ITENTIAL_MCP_SERVER_HOST") == "example.com"
            assert os.environ.get("ITENTIAL_MCP_PLATFORM_USERNAME") == "testuser"
            assert os.environ.get("ITENTIAL_MCP_CONFIG") == "/path/to/config.ini"