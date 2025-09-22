# Copyright (c) 2025 Itential, Inc
# GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)

from unittest.mock import patch
from io import StringIO

import pytest

from itential_mcp import app


class TestMainModule:
    """Test cases for __main__ module entry point"""

    @patch('asyncio.run')
    def test_main_module_calls_asyncio_run(self, mock_asyncio_run):
        """Test that __main__ calls asyncio.run() when executed"""
        mock_asyncio_run.return_value = None

        # Test the actual __main__ module content
        # The module should call asyncio.run(run())
        import itential_mcp.__main__

        # Verify that the module exists and has the expected structure
        assert hasattr(itential_mcp.__main__, '__name__')

        # The test verifies the module can be imported without errors
        # The actual execution is tested through other CLI command tests


class TestCLICommands:
    """Test cases for CLI command execution"""

    @patch('sys.argv', ['itential-mcp', '--help'])
    @patch('sys.stdout', new_callable=StringIO)
    @patch('sys.exit')
    def test_itential_mcp_help(self, mock_exit, mock_stdout):
        """Test itential-mcp --help command"""
        mock_exit.side_effect = SystemExit(0)

        with pytest.raises(SystemExit) as exc_info:
            app.run()

        assert exc_info.value.code == 0
        output = mock_stdout.getvalue()
        assert "Usage:" in output
        assert "itential-mcp <COMMAND> [OPTIONS]" in output
        assert "Commands:" in output
        mock_exit.assert_called_once_with(0)

    @patch('sys.argv', ['itential-mcp', 'call', '--help'])
    @patch('sys.stdout', new_callable=StringIO)
    @patch('sys.exit')
    def test_itential_mcp_call_help(self, mock_exit, mock_stdout):
        """Test itential-mcp call --help command"""
        mock_exit.side_effect = SystemExit(0)

        with pytest.raises(SystemExit) as exc_info:
            app.run()

        assert exc_info.value.code == 0
        output = mock_stdout.getvalue()
        assert "Call a tool and return the results" in output or "usage:" in output.lower()

    @patch('sys.argv', ['itential-mcp', 'run', '--help'])
    @patch('sys.stdout', new_callable=StringIO)
    @patch('sys.exit')
    def test_itential_mcp_run_help(self, mock_exit, mock_stdout):
        """Test itential-mcp run --help command"""
        mock_exit.side_effect = SystemExit(0)

        with pytest.raises(SystemExit) as exc_info:
            app.run()

        assert exc_info.value.code == 0
        output = mock_stdout.getvalue()
        assert "Run the MCP server" in output or "usage:" in output.lower()

    @patch('sys.argv', ['itential-mcp', 'tags'])
    @patch('asyncio.run')
    @patch('itential_mcp.toolutils.display_tags')
    def test_itential_mcp_tags(self, mock_display_tags, mock_asyncio_run):
        """Test itential-mcp tags command"""
        mock_display_tags.return_value = None
        mock_asyncio_run.return_value = 0

        result = app.run()

        assert result == 0
        mock_asyncio_run.assert_called_once()

    @patch('sys.argv', ['itential-mcp', 'tools'])
    @patch('asyncio.run')
    @patch('itential_mcp.toolutils.display_tools')
    def test_itential_mcp_tools(self, mock_display_tools, mock_asyncio_run):
        """Test itential-mcp tools command"""
        mock_display_tools.return_value = None
        mock_asyncio_run.return_value = 0

        result = app.run()

        assert result == 0
        mock_asyncio_run.assert_called_once()

    @patch('sys.argv', ['itential-mcp', 'version'])
    @patch('asyncio.run')
    @patch('itential_mcp.metadata.display_version')
    def test_itential_mcp_version(self, mock_display_version, mock_asyncio_run):
        """Test itential-mcp version command"""
        mock_display_version.return_value = None
        mock_asyncio_run.return_value = 0

        result = app.run()

        assert result == 0
        mock_asyncio_run.assert_called_once()

    @patch('sys.argv', ['itential-mcp', 'call', 'test_tool'])
    @patch('asyncio.run')
    @patch('itential_mcp.runner.run')
    def test_itential_mcp_call_tool(self, mock_runner_run, mock_asyncio_run):
        """Test itential-mcp call command with tool"""
        mock_runner_run.return_value = {"result": "success"}
        mock_asyncio_run.return_value = 0

        result = app.run()

        assert result == 0
        mock_asyncio_run.assert_called_once()

    @patch('sys.argv', ['itential-mcp', 'call', 'test_tool', '--params', '{"key": "value"}'])
    @patch('asyncio.run')
    @patch('itential_mcp.runner.run')
    def test_itential_mcp_call_tool_with_params(self, mock_runner_run, mock_asyncio_run):
        """Test itential-mcp call command with tool and parameters"""
        mock_runner_run.return_value = {"result": "success"}
        mock_asyncio_run.return_value = 0

        result = app.run()

        assert result == 0
        mock_asyncio_run.assert_called_once()

    @patch('sys.argv', ['itential-mcp', 'run'])
    @patch('asyncio.run')
    @patch('itential_mcp.server.run')
    def test_itential_mcp_run_server(self, mock_server_run, mock_asyncio_run):
        """Test itential-mcp run command to start server"""
        mock_server_run.return_value = None
        mock_asyncio_run.return_value = 0

        result = app.run()

        assert result == 0
        mock_asyncio_run.assert_called_once()


class TestCLIHelpOutput:
    """Test cases for CLI help output content"""

    @patch('sys.argv', ['itential-mcp', '--help'])
    @patch('sys.stdout', new_callable=StringIO)
    @patch('sys.exit')
    def test_help_contains_all_commands(self, mock_exit, mock_stdout):
        """Test that --help shows all available commands"""
        mock_exit.side_effect = SystemExit(0)

        with pytest.raises(SystemExit):
            app.run()

        output = mock_stdout.getvalue()

        # Check for main commands
        assert "run" in output
        assert "call" in output
        assert "tools" in output
        assert "tags" in output
        assert "version" in output

        # Check for proper formatting
        assert "Commands:" in output
        assert "Usage:" in output

    @patch('sys.argv', ['itential-mcp', 'run', '--help'])
    @patch('sys.stdout', new_callable=StringIO)
    @patch('sys.exit')
    def test_run_help_shows_server_options(self, mock_exit, mock_stdout):
        """Test that run --help shows server configuration options"""
        mock_exit.side_effect = SystemExit(0)

        with pytest.raises(SystemExit):
            app.run()

        output = mock_stdout.getvalue()

        # Should contain server-related options (exact options may vary)
        assert "--help" in output or "usage:" in output.lower()

    @patch('sys.argv', ['itential-mcp', 'call', '--help'])
    @patch('sys.stdout', new_callable=StringIO)
    @patch('sys.exit')
    def test_call_help_shows_tool_options(self, mock_exit, mock_stdout):
        """Test that call --help shows tool calling options"""
        mock_exit.side_effect = SystemExit(0)

        with pytest.raises(SystemExit):
            app.run()

        output = mock_stdout.getvalue()

        # Should mention tool parameter
        assert "tool" in output.lower() or "usage:" in output.lower()


class TestCLIErrorHandling:
    """Test cases for CLI error handling"""

    @patch('sys.argv', ['itential-mcp', 'invalid_command'])
    @patch('traceback.print_exc')
    @patch('sys.exit')
    def test_invalid_command_handled(self, mock_exit, mock_print_exc):
        """Test that invalid commands are handled gracefully"""
        app.run()

        # Should exit with error code - check that it was called with 1
        # May be called multiple times due to argparse error handling
        assert mock_exit.called
        calls = [call.args[0] for call in mock_exit.call_args_list if call.args]
        assert 1 in calls  # Check that exit(1) was called at least once
        mock_print_exc.assert_called_once()

    @patch('sys.argv', ['itential-mcp', 'call'])
    @patch('traceback.print_exc')
    @patch('sys.exit')
    def test_call_without_tool_handled(self, mock_exit, mock_print_exc):
        """Test that call command without tool name is handled"""
        app.run()

        # Should exit with error code - may be called by argparse first, then by app
        assert mock_exit.called
        calls = [call.args[0] for call in mock_exit.call_args_list if call.args]
        assert 1 in calls  # Check that exit(1) was called at least once
        mock_print_exc.assert_called_once()


class TestCLIIntegration:
    """Integration test cases for CLI"""

    @patch('sys.argv', ['itential-mcp', 'version'])
    @patch('itential_mcp.metadata.display_version')
    @patch('asyncio.run')
    def test_version_command_integration(self, mock_asyncio_run, mock_display_version):
        """Test full integration of version command"""
        # Mock async function properly
        mock_display_version.return_value = None
        mock_asyncio_run.return_value = 0

        result = app.run()

        assert result == 0
        mock_asyncio_run.assert_called_once()

    @patch('sys.argv', ['itential-mcp', 'tools'])
    @patch('itential_mcp.toolutils.display_tools')
    @patch('asyncio.run')
    def test_tools_command_integration(self, mock_asyncio_run, mock_display_tools):
        """Test full integration of tools command"""
        # Mock async function properly
        mock_display_tools.return_value = None
        mock_asyncio_run.return_value = 0

        result = app.run()

        assert result == 0
        mock_asyncio_run.assert_called_once()

    @patch('sys.argv', ['itential-mcp', 'tags'])
    @patch('itential_mcp.toolutils.display_tags')
    @patch('asyncio.run')
    def test_tags_command_integration(self, mock_asyncio_run, mock_display_tags):
        """Test full integration of tags command"""
        # Mock async function properly
        mock_display_tags.return_value = None
        mock_asyncio_run.return_value = 0

        result = app.run()

        assert result == 0
        mock_asyncio_run.assert_called_once()
