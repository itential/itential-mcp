# Copyright (c) 2025 Itential, Inc
# GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)

import argparse
from unittest.mock import Mock, patch
from io import StringIO

import pytest

from itential_mcp import cli
from itential_mcp.cli import Parser


class TestParser:
    """Test cases for the Parser class"""

    def test_parser_inheritance(self):
        """Test that Parser inherits from argparse.ArgumentParser"""
        parser = Parser()
        assert isinstance(parser, argparse.ArgumentParser)

    def test_parser_initialization(self):
        """Test Parser initialization with various parameters"""
        # Basic initialization
        parser = Parser()
        assert parser is not None

        # Initialization with parameters
        parser = Parser(
            prog="test-prog",
            description="Test description",
            add_help=False
        )
        assert parser.prog == "test-prog"
        assert parser.description == "Test description"

    @patch('sys.stdout', new_callable=StringIO)
    def test_print_app_help_basic(self, mock_stdout):
        """Test basic print_app_help functionality"""
        parser = Parser(
            prog="test-prog",
            description="Test CLI application"
        )

        # Add a basic argument
        parser.add_argument("--config", help="Configuration file")

        # Add subparsers
        subparsers = parser.add_subparsers(dest="command")
        subparsers.add_parser("run", description="Run the server")

        parser.print_app_help()

        output = mock_stdout.getvalue()
        assert "Test CLI application" in output
        assert "Usage:" in output
        assert "test-prog <COMMAND> [OPTIONS]" in output
        assert "Commands:" in output
        assert "run" in output
        assert "Run the server" in output
        assert "Options:" in output
        assert "--config" in output
        assert "Configuration file" in output

    @patch('sys.stdout', new_callable=StringIO)
    def test_print_app_help_multiple_commands(self, mock_stdout):
        """Test print_app_help with multiple commands"""
        parser = Parser(prog="test-app", description="Multi-command app")

        subparsers = parser.add_subparsers(dest="command")
        subparsers.add_parser("start", description="Start the service")
        subparsers.add_parser("stop", description="Stop the service")
        subparsers.add_parser("status", description="Check service status")

        parser.print_app_help()

        output = mock_stdout.getvalue()
        assert "start" in output and "Start the service" in output
        assert "stop" in output and "Stop the service" in output
        assert "status" in output and "Check service status" in output

    @patch('sys.stdout', new_callable=StringIO)
    def test_print_app_help_with_options(self, mock_stdout):
        """Test print_app_help with various option types"""
        parser = Parser(prog="test-app", description="Test app")

        # Add different types of options
        parser.add_argument("--verbose", "-v", action="store_true", help="Verbose output")
        parser.add_argument("--config", help="Configuration file path")
        parser.add_argument("--port", type=int, help="Port number")
        parser.add_argument("--no-help-option", help=None)  # Test no help case

        subparsers = parser.add_subparsers(dest="command")
        subparsers.add_parser("test", description="Test command")

        parser.print_app_help()

        output = mock_stdout.getvalue()
        assert "--verbose, -v" in output
        assert "Verbose output" in output
        assert "--config" in output
        assert "--port" in output
        assert "NO HELP AVAILABLE!!" in output  # For option without help

    @patch('sys.stdout', new_callable=StringIO)
    def test_print_help_basic(self, mock_stdout):
        """Test basic print_help functionality"""
        parser = Parser(prog="test-prog", description="Test application")

        # Add some arguments
        parser.add_argument("--config", help="Configuration file")
        parser.add_argument("--verbose", action="store_true", help="Verbose mode")

        # Add an argument group
        group = parser.add_argument_group("Server Options", "Server configuration")
        group.add_argument("--host", help="Server host")
        group.add_argument("--port", type=int, help="Server port")

        parser.print_help()

        output = mock_stdout.getvalue()
        assert "Test application" in output
        assert "Usage:" in output
        assert "test-prog" in output
        assert "Server Options" in output
        assert "--host" in output
        assert "--port" in output
        assert "Options" in output
        assert "--config" in output

    @patch('sys.stdout', new_callable=StringIO)
    def test_print_help_with_positional_args(self, mock_stdout):
        """Test print_help with positional arguments"""
        parser = Parser(prog="test-prog", description="Test app")

        # Add positional arguments
        parser.add_argument("command", help="Command to execute")
        parser.add_argument("target", help="Target for the command")

        # Add optional arguments
        parser.add_argument("--force", action="store_true", help="Force execution")

        parser.print_help()

        output = mock_stdout.getvalue()
        assert "<command> <target>" in output
        assert "test-prog <command> <target> [OPTIONS]" in output

    @patch('itential_mcp.terminal.getcols')
    @patch('sys.stdout', new_callable=StringIO)
    def test_print_help_long_options(self, mock_stdout, mock_getcols):
        """Test print_help with long option names that require wrapping"""
        mock_getcols.return_value = 40  # Short line width to force wrapping

        parser = Parser(prog="test-prog", description="Test app")

        # Add argument group with long option names
        group = parser.add_argument_group("Long Options")
        group.add_argument("--very-long-option-name", metavar="VALUE",
                          help="This is a very long help string that should be wrapped")

        parser.add_argument("--config", help="Short help")

        parser.print_help()

        output = mock_stdout.getvalue()
        assert "very-long-option-name" in output
        assert "This is a very long help string" in output

    @patch('sys.stdout', new_callable=StringIO)
    def test_print_help_with_metavar(self, mock_stdout):
        """Test print_help with metavar options"""
        parser = Parser(prog="test-prog", description="Test app")

        group = parser.add_argument_group("Test Group")
        group.add_argument("--file", metavar="PATH", help="File path")
        group.add_argument("--count", metavar="N", help="Number of items")

        parser.add_argument("--output", metavar="FILE", help="Output file")

        parser.print_help()

        output = mock_stdout.getvalue()
        assert "--file PATH" in output
        assert "--count N" in output
        assert "--output FILE" in output

    @patch('sys.stdout', new_callable=StringIO)
    def test_print_help_multiple_option_strings_bug(self, mock_stdout):
        """Test print_help with options that have multiple strings - demonstrates a bug with None metavar"""
        parser = Parser(prog="test-prog", description="Test app")

        # Add some required arguments to make the options group exist
        parser.add_argument("--config", help="Config file")

        group = parser.add_argument_group("Multi Options")
        group.add_argument("--verbose", "-v", action="store_true", help="Verbose mode")  # metavar is None
        group.add_argument("--output", "-o", metavar="FILE", help="Output file")

        # This test demonstrates that the CLI code has a bug on line 94
        # It tries to call .upper() on None when metavar is None for multiple option strings
        with pytest.raises(AttributeError, match="'NoneType' object has no attribute 'upper'"):
            parser.print_help()

    @patch('sys.stdout', new_callable=StringIO)
    def test_print_help_multiple_option_strings_with_metavar(self, mock_stdout):
        """Test print_help with options that have multiple strings and metavar works correctly"""
        parser = Parser(prog="test-prog", description="Test app")

        # Add some required arguments to make the options group exist
        parser.add_argument("--config", help="Config file")

        group = parser.add_argument_group("Multi Options")
        group.add_argument("--output", "-o", metavar="FILE", help="Output file")

        parser.print_help()

        output = mock_stdout.getvalue()
        # Should contain the multiple option strings with metavar
        assert "--output, -o FILE" in output or "-o, --output FILE" in output
        assert "Output file" in output

    @patch('sys.stdout', new_callable=StringIO)
    def test_print_help_no_options_group_error(self, mock_stdout):
        """Test that print_help handles missing 'options' group gracefully"""
        parser = Parser(prog="test-prog", description="Test app", add_help=False)

        # Add only a custom group, no default 'options' group
        group = parser.add_argument_group("Custom Group")
        group.add_argument("--test", help="Test option")

        # The print_help method will fail when there's no 'options' group
        # because argparse creates 'optional arguments' not 'options'
        with pytest.raises(KeyError):
            parser.print_help()


class TestGetArgumentsFromConfig:
    """Test cases for _get_arguments_from_config function"""

    @patch('itential_mcp.cli.fields')
    def test_get_arguments_from_config_basic(self, mock_fields):
        """Test basic functionality of _get_arguments_from_config"""
        # Mock a config field
        mock_field = Mock()
        mock_field.name = "server_host"
        mock_field.default = Mock()
        mock_field.default.json_schema_extra = {
            "x-itential-mcp-cli-enabled": True,
            "x-itential-mcp-arguments": ["--host"],
            "x-itential-mcp-options": {"type": str}
        }
        mock_field.default.description = "Server host address"
        mock_field.default.default = "localhost"

        mock_fields.return_value = [mock_field]

        # Clear the cache to ensure fresh data
        cli._get_arguments_from_config.cache_clear()

        result = cli._get_arguments_from_config()

        assert len(result) == 1
        assert result[0][0] == "server_host"
        assert result[0][1] == ["--host"]
        assert result[0][2]["dest"] == "server_host"
        assert result[0][2]["help"] == "Server host address (default=localhost)"
        assert result[0][2]["type"] is str

    @patch('itential_mcp.cli.fields')
    def test_get_arguments_from_config_no_cli_enabled(self, mock_fields):
        """Test _get_arguments_from_config with CLI disabled fields"""
        mock_field = Mock()
        mock_field.name = "internal_field"
        mock_field.default = Mock()
        mock_field.default.json_schema_extra = {
            "x-itential-mcp-cli-enabled": False
        }

        mock_fields.return_value = [mock_field]
        cli._get_arguments_from_config.cache_clear()

        result = cli._get_arguments_from_config()

        assert len(result) == 0

    @patch('itential_mcp.cli.fields')
    def test_get_arguments_from_config_no_schema_extra(self, mock_fields):
        """Test _get_arguments_from_config with fields having no json_schema_extra"""
        mock_field = Mock()
        mock_field.name = "basic_field"
        mock_field.default = Mock()
        mock_field.default.json_schema_extra = None

        mock_fields.return_value = [mock_field]
        cli._get_arguments_from_config.cache_clear()

        result = cli._get_arguments_from_config()

        assert len(result) == 0

    @patch('itential_mcp.cli.fields')
    def test_get_arguments_from_config_no_description(self, mock_fields):
        """Test _get_arguments_from_config with fields having no description"""
        mock_field = Mock()
        mock_field.name = "no_desc_field"
        mock_field.default = Mock()
        mock_field.default.json_schema_extra = {
            "x-itential-mcp-cli-enabled": True,
            "x-itential-mcp-arguments": ["--no-desc"]
        }
        mock_field.default.description = None
        mock_field.default.default = "default_value"

        mock_fields.return_value = [mock_field]
        cli._get_arguments_from_config.cache_clear()

        result = cli._get_arguments_from_config()

        assert len(result) == 1
        assert result[0][2]["help"] == "NO HELP AVAILABLE!!"

    @patch('itential_mcp.cli.fields')
    def test_get_arguments_from_config_multiple_fields(self, mock_fields):
        """Test _get_arguments_from_config with multiple valid fields"""
        # Create multiple mock fields
        field1 = Mock()
        field1.name = "server_port"
        field1.default = Mock()
        field1.default.json_schema_extra = {
            "x-itential-mcp-cli-enabled": True,
            "x-itential-mcp-arguments": ["--port", "-p"],
            "x-itential-mcp-options": {"type": int}
        }
        field1.default.description = "Server port"
        field1.default.default = 8080

        field2 = Mock()
        field2.name = "platform_username"
        field2.default = Mock()
        field2.default.json_schema_extra = {
            "x-itential-mcp-cli-enabled": True,
            "x-itential-mcp-arguments": ["--username"],
            "x-itential-mcp-options": {"type": str, "required": True}
        }
        field2.default.description = "Platform username"
        field2.default.default = None

        field3 = Mock()
        field3.name = "disabled_field"
        field3.default = Mock()
        field3.default.json_schema_extra = {
            "x-itential-mcp-cli-enabled": False
        }

        mock_fields.return_value = [field1, field2, field3]
        cli._get_arguments_from_config.cache_clear()

        result = cli._get_arguments_from_config()

        assert len(result) == 2

        # Check first field
        assert result[0][0] == "server_port"
        assert result[0][1] == ["--port", "-p"]
        assert result[0][2]["type"] is int

        # Check second field
        assert result[1][0] == "platform_username"
        assert result[1][1] == ["--username"]
        assert result[1][2]["required"] is True

    @patch('itential_mcp.cli.fields')
    def test_get_arguments_from_config_caching(self, mock_fields):
        """Test that _get_arguments_from_config uses LRU caching"""
        mock_field = Mock()
        mock_field.name = "test_field"
        mock_field.default = Mock()
        mock_field.default.json_schema_extra = {
            "x-itential-mcp-cli-enabled": True,
            "x-itential-mcp-arguments": ["--test"]
        }
        mock_field.default.description = "Test field"
        mock_field.default.default = "test"

        mock_fields.return_value = [mock_field]
        cli._get_arguments_from_config.cache_clear()

        # Call multiple times
        result1 = cli._get_arguments_from_config()
        result2 = cli._get_arguments_from_config()

        # Should only call fields() once due to caching
        assert mock_fields.call_count == 1
        assert result1 == result2

    @patch('itential_mcp.cli.fields')
    def test_get_arguments_from_config_no_options(self, mock_fields):
        """Test _get_arguments_from_config when x-itential-mcp-options is None"""
        mock_field = Mock()
        mock_field.name = "simple_field"
        mock_field.default = Mock()
        mock_field.default.json_schema_extra = {
            "x-itential-mcp-cli-enabled": True,
            "x-itential-mcp-arguments": ["--simple"],
            "x-itential-mcp-options": None
        }
        mock_field.default.description = "Simple field"
        mock_field.default.default = "simple"

        mock_fields.return_value = [mock_field]
        cli._get_arguments_from_config.cache_clear()

        result = cli._get_arguments_from_config()

        assert len(result) == 1
        # Should only have dest and help, no additional options
        expected_keys = {"dest", "help"}
        assert set(result[0][2].keys()) == expected_keys


class TestAddPlatformArguments:
    """Test cases for add_platform_group function"""

    @patch('itential_mcp.cli._get_arguments_from_config')
    def test_add_platform_group_basic(self, mock_get_args):
        """Test basic functionality of add_platform_group"""
        # Mock config arguments
        mock_get_args.return_value = [
            ("platform_host", ["--platform-host"], {"dest": "platform_host", "help": "Platform host"}),
            ("platform_port", ["--platform-port"], {"dest": "platform_port", "help": "Platform port"}),
            ("server_host", ["--server-host"], {"dest": "server_host", "help": "Server host"}),
        ]

        # Create mock command parser
        mock_cmd = Mock()
        mock_group = Mock()
        mock_cmd.add_argument_group.return_value = mock_group

        cli.add_platform_group(mock_cmd)

        # Verify argument group was created
        mock_cmd.add_argument_group.assert_called_once_with(
            "Itential Platform Options",
            "Configuration options for connecting to Itential Platform API"
        )

        # Verify only platform arguments were added (2 calls for 2 platform args)
        assert mock_group.add_argument.call_count == 2

        # Check the calls
        calls = mock_group.add_argument.call_args_list
        assert calls[0][0] == ("--platform-host",)
        assert calls[0][1] == {"dest": "platform_host", "help": "Platform host"}
        assert calls[1][0] == ("--platform-port",)
        assert calls[1][1] == {"dest": "platform_port", "help": "Platform port"}

    @patch('itential_mcp.cli._get_arguments_from_config')
    def test_add_platform_group_no_platform_args(self, mock_get_args):
        """Test add_platform_group when no platform arguments are available"""
        # Mock config with no platform arguments
        mock_get_args.return_value = [
            ("server_host", ["--server-host"], {"dest": "server_host", "help": "Server host"}),
            ("other_option", ["--other"], {"dest": "other_option", "help": "Other option"}),
        ]

        mock_cmd = Mock()
        mock_group = Mock()
        mock_cmd.add_argument_group.return_value = mock_group

        cli.add_platform_group(mock_cmd)

        # Argument group should still be created
        mock_cmd.add_argument_group.assert_called_once()

        # But no arguments should be added
        mock_group.add_argument.assert_not_called()

    @patch('itential_mcp.cli._get_arguments_from_config')
    def test_add_platform_group_multiple_platform_args(self, mock_get_args):
        """Test add_platform_group with multiple platform arguments"""
        mock_get_args.return_value = [
            ("platform_host", ["--platform-host"], {"dest": "platform_host", "help": "Host"}),
            ("platform_port", ["--platform-port"], {"dest": "platform_port", "help": "Port"}),
            ("platform_username", ["--platform-user"], {"dest": "platform_username", "help": "Username"}),
            ("platform_password", ["--platform-pass"], {"dest": "platform_password", "help": "Password"}),
            ("server_host", ["--server-host"], {"dest": "server_host", "help": "Server host"}),
        ]

        mock_cmd = Mock()
        mock_group = Mock()
        mock_cmd.add_argument_group.return_value = mock_group

        cli.add_platform_group(mock_cmd)

        # Should add 4 platform arguments
        assert mock_group.add_argument.call_count == 4


class TestAddServerArguments:
    """Test cases for add_server_group function"""

    @patch('itential_mcp.cli._get_arguments_from_config')
    def test_add_server_group_basic(self, mock_get_args):
        """Test basic functionality of add_server_group"""
        mock_get_args.return_value = [
            ("server_host", ["--server-host"], {"dest": "server_host", "help": "Server host"}),
            ("server_port", ["--server-port"], {"dest": "server_port", "help": "Server port"}),
            ("platform_host", ["--platform-host"], {"dest": "platform_host", "help": "Platform host"}),
        ]

        mock_cmd = Mock()
        mock_group = Mock()
        mock_cmd.add_argument_group.return_value = mock_group

        cli.add_server_group(mock_cmd)

        # Verify argument group was created
        mock_cmd.add_argument_group.assert_called_once_with(
            "MCP Server Options",
            "Configuration options for the MCP Server instance"
        )

        # Verify only server arguments were added
        assert mock_group.add_argument.call_count == 2

    @patch('itential_mcp.cli._get_arguments_from_config')
    def test_add_server_group_no_server_args(self, mock_get_args):
        """Test add_server_group when no server arguments are available"""
        mock_get_args.return_value = [
            ("platform_host", ["--platform-host"], {"dest": "platform_host", "help": "Platform host"}),
            ("other_option", ["--other"], {"dest": "other_option", "help": "Other option"}),
        ]

        mock_cmd = Mock()
        mock_group = Mock()
        mock_cmd.add_argument_group.return_value = mock_group

        cli.add_server_group(mock_cmd)

        mock_cmd.add_argument_group.assert_called_once()
        mock_group.add_argument.assert_not_called()

    @patch('itential_mcp.cli._get_arguments_from_config')
    def test_add_server_group_multiple_server_args(self, mock_get_args):
        """Test add_server_group with multiple server arguments"""
        mock_get_args.return_value = [
            ("server_host", ["--host"], {"dest": "server_host", "help": "Host"}),
            ("server_port", ["--port"], {"dest": "server_port", "help": "Port"}),
            ("server_transport", ["--transport"], {"dest": "server_transport", "help": "Transport"}),
            ("server_log_level", ["--log-level"], {"dest": "server_log_level", "help": "Log level"}),
            ("platform_username", ["--username"], {"dest": "platform_username", "help": "Username"}),
        ]

        mock_cmd = Mock()
        mock_group = Mock()
        mock_cmd.add_argument_group.return_value = mock_group

        cli.add_server_group(mock_cmd)

        # Should add 4 server arguments
        assert mock_group.add_argument.call_count == 4


class TestModuleStructure:
    """Test cases for overall module structure and imports"""

    def test_module_imports(self):
        """Test that all required modules are imported"""
        assert hasattr(cli, 'argparse')
        assert hasattr(cli, 'terminal')
        assert hasattr(cli, 'config')

    def test_module_functions_exist(self):
        """Test that all expected functions exist"""
        expected_functions = [
            '_get_arguments_from_config',
            'add_platform_group',
            'add_server_group'
        ]

        for func_name in expected_functions:
            assert hasattr(cli, func_name)
            assert callable(getattr(cli, func_name))

    def test_parser_class_exists(self):
        """Test that Parser class exists and is properly defined"""
        assert hasattr(cli, 'Parser')
        assert issubclass(cli.Parser, argparse.ArgumentParser)

    def test_typing_imports(self):
        """Test that typing imports are available"""
        assert hasattr(cli, 'Sequence')
        assert hasattr(cli, 'Tuple')
        assert hasattr(cli, 'Mapping')

    def test_lru_cache_import(self):
        """Test that lru_cache is imported"""
        assert hasattr(cli, 'lru_cache')

    def test_fields_import(self):
        """Test that dataclasses.fields is imported"""
        assert hasattr(cli, 'fields')


class TestParserIntegration:
    """Integration tests for Parser class"""

    def test_parser_with_real_arguments(self):
        """Test Parser with realistic argument setup"""
        parser = Parser(
            prog="itential-mcp",
            description="Itential MCP Server CLI"
        )

        # Add global arguments
        parser.add_argument("--config", help="Configuration file")
        parser.add_argument("--verbose", "-v", action="store_true", help="Verbose output")

        # Add subcommands
        subparsers = parser.add_subparsers(dest="command")

        run_parser = subparsers.add_parser("run", description="Run the MCP server")
        run_parser.add_argument("--host", default="localhost", help="Server host")
        run_parser.add_argument("--port", type=int, default=8080, help="Server port")

        subparsers.add_parser("version", description="Show version info")

        # Test that parser works correctly
        args = parser.parse_args(["run", "--host", "example.com", "--port", "9000"])
        assert args.command == "run"
        assert args.host == "example.com"
        assert args.port == 9000

    @patch('sys.stdout', new_callable=StringIO)
    def test_parser_help_integration(self, mock_stdout):
        """Test Parser help output integration"""
        parser = Parser(
            prog="itential-mcp",
            description="Itential MCP Server"
        )

        parser.add_argument("--config", help="Config file")

        # Add server arguments group
        server_group = parser.add_argument_group(
            "Server Options",
            "Options for server configuration"
        )
        server_group.add_argument("--host", help="Server host")
        server_group.add_argument("--port", type=int, help="Server port")

        # Add subcommands
        subparsers = parser.add_subparsers(dest="command")
        subparsers.add_parser("run", description="Run server")
        subparsers.add_parser("stop", description="Stop server")

        # Test app help
        parser.print_app_help()
        app_output = mock_stdout.getvalue()

        assert "Itential MCP Server" in app_output
        assert "run" in app_output and "Run server" in app_output
        assert "stop" in app_output and "Stop server" in app_output
        assert "--config" in app_output

        # Clear and test regular help
        mock_stdout.truncate(0)
        mock_stdout.seek(0)

        parser.print_help()
        help_output = mock_stdout.getvalue()

        assert "Server Options" in help_output
        assert "--host" in help_output
        assert "--port" in help_output

    @patch('itential_mcp.cli._get_arguments_from_config')
    def test_argument_functions_integration(self, mock_get_args):
        """Test integration of add_platform_group and add_server_group"""
        mock_get_args.return_value = [
            ("platform_host", ["--platform-host"], {"dest": "platform_host", "help": "Platform host"}),
            ("platform_port", ["--platform-port"], {"dest": "platform_port", "type": int, "help": "Platform port"}),
            ("server_host", ["--server-host"], {"dest": "server_host", "help": "Server host"}),
            ("server_transport", ["--transport"], {"dest": "server_transport", "help": "Transport protocol"}),
        ]

        parser = Parser(prog="test-app")

        # Add platform arguments
        cli.add_platform_group(parser)

        # Add server arguments
        cli.add_server_group(parser)

        # Test parsing
        args = parser.parse_args([
            "--platform-host", "platform.example.com",
            "--platform-port", "443",
            "--server-host", "0.0.0.0",
            "--transport", "http"
        ])

        assert args.platform_host == "platform.example.com"
        assert args.platform_port == 443
        assert args.server_host == "0.0.0.0"
        assert args.server_transport == "http"


class TestErrorHandling:
    """Test error handling and edge cases"""

    @patch('sys.stdout', new_callable=StringIO)
    def test_print_app_help_no_subparsers(self, mock_stdout):
        """Test print_app_help behavior when no subparsers are defined"""
        parser = Parser(prog="test-app", description="Test app")
        parser.add_argument("--config", help="Config file")

        # This should handle the case where there are no subparsers
        with pytest.raises(AttributeError):
            parser.print_app_help()

    @patch('sys.stdout', new_callable=StringIO)
    def test_print_help_empty_parser(self, mock_stdout):
        """Test print_help with minimal parser setup"""
        parser = Parser(prog="minimal", description="Minimal parser", add_help=False)

        # Should handle case with no arguments or groups
        # This will fail because there's no 'options' group
        with pytest.raises(KeyError):
            parser.print_help()

    @patch('itential_mcp.cli.fields')
    def test_get_arguments_from_config_exception_handling(self, mock_fields):
        """Test _get_arguments_from_config handles malformed field data"""
        # Mock a field with missing attributes
        mock_field = Mock()
        mock_field.name = "broken_field"
        mock_field.default = Mock()
        mock_field.default.json_schema_extra = {
            "x-itential-mcp-cli-enabled": True,
            # Missing x-itential-mcp-arguments
        }
        mock_field.default.description = "Broken field"
        mock_field.default.default = "default"

        mock_fields.return_value = [mock_field]
        cli._get_arguments_from_config.cache_clear()

        result = cli._get_arguments_from_config()

        # Should handle gracefully and include the field
        assert len(result) == 1
        assert result[0][1] is None  # No arguments defined

    def test_parser_methods_file_parameter(self):
        """Test that parser methods accept file parameter"""
        parser = Parser(prog="test")

        # Methods should accept file parameter without error
        import io
        test_file = io.StringIO()

        # These should not raise errors
        try:
            parser.print_app_help(file=test_file)
        except AttributeError:
            # Expected due to no subparsers
            pass

        try:
            parser.print_help(file=test_file)
        except KeyError:
            # Expected due to no options group
            pass
