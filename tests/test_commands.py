# Copyright (c) 2025 Itential, Inc
# GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

import inspect
import asyncio
from unittest.mock import Mock

import pytest

from itential_mcp.runtime import commands, runner
from itential_mcp import server
from itential_mcp.core import metadata
from itential_mcp.utilities import tool


class TestRunCommand:
    """Test cases for the run command function"""

    def test_run_function_exists(self):
        """Test that the run function exists and is callable"""
        assert hasattr(commands, "run")
        assert callable(commands.run)

    def test_run_returns_correct_tuple(self):
        """Test that run function returns the expected tuple structure"""
        args = Mock()
        result = commands.run(args)

        assert isinstance(result, tuple)
        assert len(result) == 3
        assert result[0] == server.run
        assert result[1] is None
        assert result[2] is None

    def test_run_with_various_args(self):
        """Test run function with different argument types"""
        test_cases = [None, {}, "test", [], Mock(), object(), 42, True]

        for args in test_cases:
            result = commands.run(args)
            assert result == (server.run, None, None)

    def test_run_function_signature(self):
        """Test that run function has correct signature"""
        sig = inspect.signature(commands.run)
        params = list(sig.parameters.keys())

        assert len(params) == 1
        assert params[0] == "args"

        # Check parameter type annotation
        param = sig.parameters["args"]
        assert param.annotation == commands.Any

    def test_run_function_docstring(self):
        """Test that run function has proper docstring"""
        assert commands.run.__doc__ is not None
        assert "Implement the `itential-mcp run` command" in commands.run.__doc__
        assert "server" in commands.run.__doc__

    def test_run_returns_coroutine_function(self):
        """Test that the returned function is a coroutine"""
        args = Mock()
        result = commands.run(args)

        # The first element should be a coroutine function
        assert asyncio.iscoroutinefunction(result[0])

    def test_run_function_is_not_async(self):
        """Test that run command function itself is not async"""
        assert not asyncio.iscoroutinefunction(commands.run)

    def test_run_return_type_annotation(self):
        """Test that run function has correct return type annotation"""
        sig = inspect.signature(commands.run)
        return_annotation = sig.return_annotation

        # Should be Tuple[Coroutine, Sequence, Mapping]
        assert return_annotation is not None


class TestVersionCommand:
    """Test cases for the version command function"""

    def test_version_function_exists(self):
        """Test that the version function exists and is callable"""
        assert hasattr(commands, "version")
        assert callable(commands.version)

    def test_version_returns_correct_tuple(self):
        """Test that version function returns the expected tuple structure"""
        args = Mock()
        result = commands.version(args)

        assert isinstance(result, tuple)
        assert len(result) == 3
        assert result[0] == metadata.display_version
        assert result[1] is None
        assert result[2] is None

    def test_version_with_various_args(self):
        """Test version function with different argument types"""
        test_cases = [None, {}, "test", [], Mock(), object(), 42, True]

        for args in test_cases:
            result = commands.version(args)
            assert result == (metadata.display_version, None, None)

    def test_version_function_signature(self):
        """Test that version function has correct signature"""
        sig = inspect.signature(commands.version)
        params = list(sig.parameters.keys())

        assert len(params) == 1
        assert params[0] == "args"

        # Check parameter type annotation
        param = sig.parameters["args"]
        assert param.annotation == commands.Any

    def test_version_function_docstring(self):
        """Test that version function has proper docstring"""
        assert commands.version.__doc__ is not None
        assert (
            "Implement the `itential-mcp version` command" in commands.version.__doc__
        )
        assert "display_version" in commands.version.__doc__
        assert "show version information" in commands.version.__doc__

    def test_version_returns_coroutine_function(self):
        """Test that the returned function is a coroutine"""
        args = Mock()
        result = commands.version(args)

        # The first element should be a coroutine function
        assert asyncio.iscoroutinefunction(result[0])

    def test_version_function_is_not_async(self):
        """Test that version command function itself is not async"""
        assert not asyncio.iscoroutinefunction(commands.version)


class TestToolsCommand:
    """Test cases for the tools command function"""

    def test_tools_function_exists(self):
        """Test that the tools function exists and is callable"""
        assert hasattr(commands, "tools")
        assert callable(commands.tools)

    def test_tools_returns_correct_tuple(self):
        """Test that tools function returns the expected tuple structure"""
        args = Mock()
        result = commands.tools(args)

        assert isinstance(result, tuple)
        assert len(result) == 3
        assert result[0] == tool.display_tools
        assert result[1] is None
        assert result[2] is None

    def test_tools_with_various_args(self):
        """Test tools function with different argument types"""
        test_cases = [None, {}, "test", [], Mock(), object(), 42, True]

        for args in test_cases:
            result = commands.tools(args)
            assert result == (tool.display_tools, None, None)

    def test_tools_function_signature(self):
        """Test that tools function has correct signature"""
        sig = inspect.signature(commands.tools)
        params = list(sig.parameters.keys())

        assert len(params) == 1
        assert params[0] == "args"

        # Check parameter type annotation
        param = sig.parameters["args"]
        assert param.annotation == commands.Any

    def test_tools_function_docstring(self):
        """Test that tools function has proper docstring"""
        assert commands.tools.__doc__ is not None
        assert "Implement the `itential-mcp tools` command" in commands.tools.__doc__
        assert "display the list of all available tools" in commands.tools.__doc__

    def test_tools_returns_coroutine_function(self):
        """Test that the returned function is a coroutine"""
        args = Mock()
        result = commands.tools(args)

        # The first element should be a coroutine function
        assert asyncio.iscoroutinefunction(result[0])

    def test_tools_function_is_not_async(self):
        """Test that tools command function itself is not async"""
        assert not asyncio.iscoroutinefunction(commands.tools)


class TestTagsCommand:
    """Test cases for the tags command function"""

    def test_tags_function_exists(self):
        """Test that the tags function exists and is callable"""
        assert hasattr(commands, "tags")
        assert callable(commands.tags)

    def test_tags_returns_correct_tuple(self):
        """Test that tags function returns the expected tuple structure"""
        args = Mock()
        result = commands.tags(args)

        assert isinstance(result, tuple)
        assert len(result) == 3
        assert result[0] == tool.display_tags
        assert result[1] is None
        assert result[2] is None

    def test_tags_with_various_args(self):
        """Test tags function with different argument types"""
        test_cases = [None, {}, "test", [], Mock(), object(), 42, True]

        for args in test_cases:
            result = commands.tags(args)
            assert result == (tool.display_tags, None, None)

    def test_tags_function_signature(self):
        """Test that tags function has correct signature"""
        sig = inspect.signature(commands.tags)
        params = list(sig.parameters.keys())

        assert len(params) == 1
        assert params[0] == "args"

        # Check parameter type annotation
        param = sig.parameters["args"]
        assert param.annotation == commands.Any

    def test_tags_function_docstring(self):
        """Test that tags function has proper docstring"""
        assert commands.tags.__doc__ is not None
        assert "Implement the `itential-mcp tags` command" in commands.tags.__doc__
        assert "display the list of all available tags" in commands.tags.__doc__

    def test_tags_returns_coroutine_function(self):
        """Test that the returned function is a coroutine"""
        args = Mock()
        result = commands.tags(args)

        # The first element should be a coroutine function
        assert asyncio.iscoroutinefunction(result[0])

    def test_tags_function_is_not_async(self):
        """Test that tags command function itself is not async"""
        assert not asyncio.iscoroutinefunction(commands.tags)


class TestCallCommand:
    """Test cases for the call command function"""

    def test_call_function_exists(self):
        """Test that the call function exists and is callable"""
        assert hasattr(commands, "call")
        assert callable(commands.call)

    def test_call_returns_correct_tuple_structure(self):
        """Test that call function returns the expected tuple structure"""
        args = Mock()
        args.tool = "test_tool"
        args.params = '{"key": "value"}'

        result = commands.call(args)

        assert isinstance(result, tuple)
        assert len(result) == 3
        assert result[0] == runner.run
        assert result[1] == (args.tool, args.params)
        assert result[2] is None

    def test_call_with_tool_and_params(self):
        """Test call function with tool name and parameters"""
        args = Mock()
        args.tool = "get_user"
        args.params = '{"user_id": "12345"}'

        result = commands.call(args)

        assert result[0] == runner.run
        assert result[1] == ("get_user", '{"user_id": "12345"}')
        assert result[2] is None

    def test_call_with_tool_no_params(self):
        """Test call function with tool name but no parameters"""
        args = Mock()
        args.tool = "list_users"
        args.params = None

        result = commands.call(args)

        assert result[0] == runner.run
        assert result[1] == ("list_users", None)
        assert result[2] is None

    def test_call_with_different_tool_names(self):
        """Test call function with various tool names"""
        test_cases = [
            ("simple_tool", None),
            ("complex-tool-name", '{"param": "value"}'),
            ("tool_with_underscores", "{}"),
            ("Tool123", '{"num": 123}'),
            ("", ""),
        ]

        for tool_name, params in test_cases:
            args = Mock()
            args.tool = tool_name
            args.params = params

            result = commands.call(args)

            assert result[0] == runner.run
            assert result[1] == (tool_name, params)
            assert result[2] is None

    def test_call_function_signature(self):
        """Test that call function has correct signature"""
        sig = inspect.signature(commands.call)
        params = list(sig.parameters.keys())

        assert len(params) == 1
        assert params[0] == "args"

        # Check parameter type annotation
        param = sig.parameters["args"]
        assert param.annotation == commands.Any

    def test_call_function_docstring(self):
        """Test that call function has proper docstring"""
        assert commands.call.__doc__ is not None
        assert "Implement the `itential-mcp call` command" in commands.call.__doc__
        assert "invoke a tool" in commands.call.__doc__

    def test_call_returns_coroutine_function(self):
        """Test that the returned function is a coroutine"""
        args = Mock()
        args.tool = "test_tool"
        args.params = None

        result = commands.call(args)

        # The first element should be a coroutine function
        assert asyncio.iscoroutinefunction(result[0])

    def test_call_function_is_not_async(self):
        """Test that call command function itself is not async"""
        assert not asyncio.iscoroutinefunction(commands.call)

    def test_call_args_attribute_access(self):
        """Test that call function properly accesses args attributes"""

        # Test with realistic argparse.Namespace-like object
        class MockArgs:
            def __init__(self, tool, params):
                self.tool = tool
                self.params = params

        args = MockArgs("my_tool", '{"test": true}')
        result = commands.call(args)

        assert result[1] == ("my_tool", '{"test": true}')


class TestModuleStructure:
    """Test cases for overall module structure and imports"""

    def test_module_imports(self):
        """Test that all required modules are imported"""
        assert hasattr(commands, "server")
        assert hasattr(commands, "metadata")
        assert hasattr(commands, "tool")
        assert hasattr(commands, "runner")

        assert commands.server == server
        assert commands.metadata == metadata
        assert commands.tool == tool
        assert commands.runner == runner

    def test_module_functions_exist(self):
        """Test that all expected command functions exist"""
        expected_functions = ["run", "version", "tools", "tags", "call"]

        for func_name in expected_functions:
            assert hasattr(commands, func_name)
            assert callable(getattr(commands, func_name))

    def test_module_typing_imports(self):
        """Test that typing imports are available"""
        # These should be imported from typing module
        assert hasattr(commands, "Any")
        assert hasattr(commands, "Coroutine")
        assert hasattr(commands, "Sequence")
        assert hasattr(commands, "Mapping")
        assert hasattr(commands, "Tuple")

    def test_all_functions_have_consistent_signature(self):
        """Test that all command functions have the same signature pattern"""
        functions = [
            commands.run,
            commands.version,
            commands.tools,
            commands.tags,
            commands.call,
        ]

        for func in functions:
            sig = inspect.signature(func)
            params = list(sig.parameters.keys())

            # All should have exactly one parameter named 'args'
            assert len(params) == 1
            assert params[0] == "args"

            # All should have Any type annotation for args parameter
            param = sig.parameters["args"]
            assert param.annotation == commands.Any

    def test_all_functions_return_tuple(self):
        """Test that all command functions return tuples"""
        functions = [
            commands.run,
            commands.version,
            commands.tools,
            commands.tags,
            commands.call,
        ]
        args = Mock()
        args.tool = "test"
        args.params = None

        for func in functions:
            result = func(args)
            assert isinstance(result, tuple)
            assert len(result) == 3

    def test_functions_are_not_coroutines(self):
        """Test that command functions themselves are not coroutines"""
        functions = [
            commands.run,
            commands.version,
            commands.tools,
            commands.tags,
            commands.call,
        ]

        for func in functions:
            assert not asyncio.iscoroutinefunction(func)

    def test_returned_functions_are_coroutines(self):
        """Test that all command functions return coroutine functions as first element"""
        args = Mock()
        args.tool = "test"
        args.params = None

        functions_and_results = [
            (commands.run, args),
            (commands.version, args),
            (commands.tools, args),
            (commands.tags, args),
            (commands.call, args),
        ]

        for func, test_args in functions_and_results:
            result = func(test_args)
            assert asyncio.iscoroutinefunction(result[0])


class TestCommandsIntegration:
    """Integration tests for the commands module"""

    def test_run_with_realistic_args(self):
        """Test run with realistic argument structure"""

        class MockArgs:
            def __init__(self):
                self.transport = "stdio"
                self.host = "localhost"
                self.port = 8000
                self.log_level = "INFO"

        args = MockArgs()
        result = commands.run(args)

        assert result[0] == server.run
        assert result[1] is None
        assert result[2] is None

    def test_call_with_realistic_args(self):
        """Test call with realistic argument structure"""

        class MockArgs:
            def __init__(self):
                self.tool = "get_platform_info"
                self.params = '{"include_version": true, "format": "json"}'

        args = MockArgs()
        result = commands.call(args)

        assert result[0] == runner.run
        assert result[1] == (
            "get_platform_info",
            '{"include_version": true, "format": "json"}',
        )
        assert result[2] is None

    def test_all_commands_can_be_called_multiple_times(self):
        """Test that all command functions can be called multiple times safely"""
        args = Mock()
        args.tool = "test_tool"
        args.params = "{}"

        functions = [
            commands.run,
            commands.version,
            commands.tools,
            commands.tags,
            commands.call,
        ]

        for func in functions:
            # Call multiple times
            results = [func(args) for _ in range(3)]

            # All results should have the same first element (function reference)
            first_func = results[0][0]
            for result in results[1:]:
                assert result[0] == first_func

    def test_command_function_consistency(self):
        """Test that command functions are consistent in behavior"""
        args = Mock()
        args.tool = "test"
        args.params = None

        # Test that calling functions multiple times returns same structure
        for _ in range(5):
            run_result = commands.run(args)
            version_result = commands.version(args)
            tools_result = commands.tools(args)
            tags_result = commands.tags(args)
            call_result = commands.call(args)

            # All should return 3-element tuples
            for result in [
                run_result,
                version_result,
                tools_result,
                tags_result,
                call_result,
            ]:
                assert len(result) == 3
                assert callable(result[0])

    def test_edge_case_arguments(self):
        """Test all commands with edge case arguments"""
        edge_cases = [None, 0, "", [], {}, False, True, object()]

        # These functions don't access args attributes
        simple_functions = [
            commands.run,
            commands.version,
            commands.tools,
            commands.tags,
        ]

        for args in edge_cases:
            for func in simple_functions:
                result = func(args)
                assert isinstance(result, tuple)
                assert len(result) == 3

    def test_call_command_with_missing_attributes(self):
        """Test call command behavior when args lacks expected attributes"""
        # Test with object that doesn't have tool/params attributes
        with pytest.raises(AttributeError):
            commands.call(object())

        # Test with object that has only tool attribute
        class PartialArgs:
            def __init__(self):
                self.tool = "test_tool"

        with pytest.raises(AttributeError):
            commands.call(PartialArgs())


class TestTestCommand:
    """Test cases for the test command function"""

    def test_test_function_exists(self):
        """Test that the test function exists and is callable"""
        assert hasattr(commands, "test")
        assert callable(commands.test)

    def test_test_returns_correct_tuple_structure(self):
        """Test that test function returns the expected tuple structure"""
        args = Mock()
        args.config = None
        args.format = "human"
        args.verbose = False
        args.timeout = 30
        args.quiet = False

        result = commands.test(args)

        assert isinstance(result, tuple)
        assert len(result) == 3
        assert asyncio.iscoroutinefunction(result[0])
        assert result[1] is None
        assert isinstance(result[2], dict)

    def test_test_with_all_options(self):
        """Test test function with all arguments specified"""
        args = Mock()
        args.config = "/path/to/config.ini"
        args.format = "json"
        args.verbose = True
        args.timeout = 60
        args.quiet = True

        result = commands.test(args)

        assert result[0] == commands._execute_test_connection
        assert result[1] is None
        assert result[2]["config_file"] == "/path/to/config.ini"
        assert result[2]["format"] == "json"
        assert result[2]["verbose"] is True
        assert result[2]["timeout"] == 60
        assert result[2]["quiet"] is True

    def test_test_with_default_values(self):
        """Test test function with default values"""
        args = Mock(spec=[])  # Empty spec means no attributes

        result = commands.test(args)

        assert result[2]["config_file"] is None
        assert result[2]["format"] == "human"
        assert result[2]["verbose"] is False
        assert result[2]["timeout"] == 30
        assert result[2]["quiet"] is False

    def test_test_function_signature(self):
        """Test that test function has correct signature"""
        sig = inspect.signature(commands.test)
        params = list(sig.parameters.keys())

        assert len(params) == 1
        assert params[0] == "args"

    def test_test_function_docstring(self):
        """Test that test function has proper docstring"""
        assert commands.test.__doc__ is not None
        assert "Implement the `itential-mcp test` command" in commands.test.__doc__


class TestExecuteTestConnection:
    """Test cases for _execute_test_connection function"""

    @pytest.mark.asyncio
    async def test_execute_test_connection_exists(self):
        """Test that _execute_test_connection function exists"""
        assert hasattr(commands, "_execute_test_connection")
        assert callable(commands._execute_test_connection)

    @pytest.mark.asyncio
    async def test_execute_test_connection_is_async(self):
        """Test that _execute_test_connection is a coroutine function"""
        assert asyncio.iscoroutinefunction(commands._execute_test_connection)

    @pytest.mark.asyncio
    async def test_execute_test_connection_config_load_failure(self, monkeypatch):
        """Test _execute_test_connection with configuration load failure"""
        from itential_mcp import config

        # Mock config.get to raise an exception
        def mock_get():
            raise RuntimeError("Config load failed")

        monkeypatch.setattr(config, "get", mock_get)

        result = await commands._execute_test_connection()

        assert result == 1

    @pytest.mark.asyncio
    async def test_execute_test_connection_with_config_file(
        self, tmp_path, monkeypatch
    ):
        """Test _execute_test_connection with config file parameter"""
        import os
        from itential_mcp import config
        from unittest.mock import AsyncMock, Mock, patch

        # Create a temporary config file
        config_file = tmp_path / "test.ini"
        config_file.write_text("[server]\ntransport = stdio\n")

        # Clear the cache
        config.get.cache_clear()

        # Mock ConnectionTestService
        mock_service = Mock()
        mock_result = Mock()
        mock_result.success = True
        mock_result.checks = []
        mock_result.platform_version = "2024.1"
        mock_result.authenticated_user = "admin"
        mock_result.duration_ms = 100.5
        mock_result.error = None
        mock_service.run_all_checks = AsyncMock(return_value=mock_result)

        # Clear environment
        monkeypatch.delenv("ITENTIAL_MCP_CONFIG", raising=False)

        with patch(
            "itential_mcp.platform.connection_test.ConnectionTestService",
            return_value=mock_service,
        ):
            result = await commands._execute_test_connection(
                config_file=str(config_file), format="human", quiet=True
            )

        assert result == 0
        assert os.environ.get("ITENTIAL_MCP_CONFIG") == str(config_file)

    @pytest.mark.asyncio
    async def test_execute_test_connection_success_human_format(self):
        """Test _execute_test_connection with successful test in human format"""
        from unittest.mock import AsyncMock, Mock, patch

        # Mock ConnectionTestService
        mock_service = Mock()
        mock_result = Mock()
        mock_result.success = True
        mock_result.checks = []
        mock_result.platform_version = "2024.1"
        mock_result.authenticated_user = "admin"
        mock_result.duration_ms = 100.5
        mock_result.error = None
        mock_service.run_all_checks = AsyncMock(return_value=mock_result)

        with patch(
            "itential_mcp.platform.connection_test.ConnectionTestService",
            return_value=mock_service,
        ):
            result = await commands._execute_test_connection(format="human", quiet=True)

        assert result == 0

    @pytest.mark.asyncio
    async def test_execute_test_connection_failure(self):
        """Test _execute_test_connection with failed test"""
        from unittest.mock import AsyncMock, Mock, patch

        # Mock ConnectionTestService
        mock_service = Mock()
        mock_result = Mock()
        mock_result.success = False
        mock_result.checks = []
        mock_result.error = "Connection failed"
        mock_result.duration_ms = 100.0  # Add duration for JSON output
        mock_result.platform_version = None
        mock_result.authenticated_user = None
        mock_service.run_all_checks = AsyncMock(return_value=mock_result)

        with patch(
            "itential_mcp.platform.connection_test.ConnectionTestService",
            return_value=mock_service,
        ):
            result = await commands._execute_test_connection(format="json", quiet=True)

        assert result == 1

    @pytest.mark.asyncio
    async def test_execute_test_connection_exception_during_check(self):
        """Test _execute_test_connection with exception during check execution"""
        from unittest.mock import AsyncMock, Mock, patch

        # Mock ConnectionTestService to raise exception
        mock_service = Mock()
        mock_service.run_all_checks = AsyncMock(
            side_effect=RuntimeError("Unexpected error")
        )

        with patch(
            "itential_mcp.platform.connection_test.ConnectionTestService",
            return_value=mock_service,
        ):
            result = await commands._execute_test_connection(quiet=True)

        assert result == 1

    @pytest.mark.asyncio
    async def test_execute_test_connection_json_format(self, capsys):
        """Test _execute_test_connection with JSON output format"""
        from unittest.mock import AsyncMock, Mock, patch
        import json

        # Mock ConnectionTestService
        mock_service = Mock()
        mock_result = Mock()
        mock_result.success = True
        mock_result.checks = []
        mock_result.platform_version = "2024.1"
        mock_result.authenticated_user = "admin"
        mock_result.duration_ms = 100.5
        mock_result.error = None
        mock_service.run_all_checks = AsyncMock(return_value=mock_result)

        with patch(
            "itential_mcp.platform.connection_test.ConnectionTestService",
            return_value=mock_service,
        ):
            result = await commands._execute_test_connection(format="json", quiet=True)

        assert result == 0
        captured = capsys.readouterr()
        # Should output JSON
        assert captured.out.strip()
        output = json.loads(captured.out)
        assert "success" in output

    @pytest.mark.asyncio
    async def test_execute_test_connection_with_timeout(self):
        """Test _execute_test_connection with custom timeout"""
        from unittest.mock import AsyncMock, Mock, patch

        # Mock ConnectionTestService
        mock_service = Mock()
        mock_result = Mock()
        mock_result.success = True
        mock_result.checks = []
        mock_result.duration_ms = 150.0
        mock_result.platform_version = "2024.1"
        mock_result.authenticated_user = "admin"
        mock_result.error = None
        mock_service.run_all_checks = AsyncMock(return_value=mock_result)

        with patch(
            "itential_mcp.platform.connection_test.ConnectionTestService",
            return_value=mock_service,
        ):
            result = await commands._execute_test_connection(timeout=60, quiet=True)

        assert result == 0
        mock_service.run_all_checks.assert_called_once_with(timeout=60)

    @pytest.mark.asyncio
    async def test_execute_test_connection_with_progress_messages(self, capsys):
        """Test _execute_test_connection shows progress messages when not quiet"""
        from unittest.mock import AsyncMock, Mock, patch

        # Mock ConnectionTestService
        mock_service = Mock()
        mock_result = Mock()
        mock_result.success = True
        mock_result.checks = []
        mock_result.duration_ms = 150.0
        mock_result.platform_version = "2024.1"
        mock_result.authenticated_user = "admin"
        mock_result.error = None
        mock_service.run_all_checks = AsyncMock(return_value=mock_result)

        with patch(
            "itential_mcp.platform.connection_test.ConnectionTestService",
            return_value=mock_service,
        ):
            result = await commands._execute_test_connection(
                format="human", quiet=False
            )

        assert result == 0
        captured = capsys.readouterr()
        assert "Testing connection to Itential Platform" in captured.out


class TestOutputHuman:
    """Test cases for _output_human function"""

    def test_output_human_exists(self):
        """Test that _output_human function exists"""
        assert hasattr(commands, "_output_human")
        assert callable(commands._output_human)

    def test_output_human_with_passed_checks(self, capsys):
        """Test _output_human with all checks passed"""
        from unittest.mock import Mock
        from itential_mcp.platform.connection_test import CheckStatus

        result = Mock()
        result.success = True
        result.platform_version = "2024.1"
        result.authenticated_user = "admin"
        result.duration_ms = 150.5

        check = Mock()
        check.status = CheckStatus.PASSED
        check.message = "DNS resolution: Successful"
        check.duration_ms = 50.2
        check.details = None
        check.error = None
        check.suggestion = None

        result.checks = [check]
        result.error = None

        commands._output_human(result)

        captured = capsys.readouterr()
        assert "✓" in captured.out
        assert "DNS resolution: Successful" in captured.out
        assert "SUCCESS" in captured.out

    def test_output_human_with_failed_checks(self, capsys):
        """Test _output_human with failed checks"""
        from unittest.mock import Mock
        from itential_mcp.platform.connection_test import CheckStatus

        result = Mock()
        result.success = False
        result.platform_version = None
        result.authenticated_user = None
        result.error = "Connection timeout"

        check = Mock()
        check.status = CheckStatus.FAILED
        check.message = "Connection: Failed"
        check.duration_ms = 5000.0
        check.details = None
        check.error = None
        check.suggestion = "Check firewall settings"

        result.checks = [check]

        commands._output_human(result)

        captured = capsys.readouterr()
        assert "✗" in captured.out
        assert "Connection: Failed" in captured.out
        assert "FAILED" in captured.out
        assert "Suggestion" in captured.out
        assert "Check firewall settings" in captured.out

    def test_output_human_with_skipped_checks(self, capsys):
        """Test _output_human with skipped checks"""
        from unittest.mock import Mock
        from itential_mcp.platform.connection_test import CheckStatus

        result = Mock()
        result.success = True
        result.platform_version = "2024.1"
        result.authenticated_user = "admin"
        result.duration_ms = 100.0
        result.error = None

        check = Mock()
        check.status = CheckStatus.SKIPPED
        check.message = "Optional check: Skipped"
        check.duration_ms = 0.0
        check.details = None
        check.error = None
        check.suggestion = None

        result.checks = [check]

        commands._output_human(result)

        captured = capsys.readouterr()
        assert "○" in captured.out
        assert "Optional check: Skipped" in captured.out

    def test_output_human_with_warning_checks(self, capsys):
        """Test _output_human with warning checks"""
        from unittest.mock import Mock
        from itential_mcp.platform.connection_test import CheckStatus

        result = Mock()
        result.success = True
        result.platform_version = "2024.1"
        result.authenticated_user = "admin"
        result.duration_ms = 100.0
        result.error = None

        check = Mock()
        check.status = CheckStatus.WARNING
        check.message = "Performance warning"
        check.duration_ms = 1000.0
        check.details = None
        check.error = None
        check.suggestion = None

        result.checks = [check]

        commands._output_human(result)

        captured = capsys.readouterr()
        assert "⚠" in captured.out
        assert "Performance warning" in captured.out

    def test_output_human_verbose_mode(self, capsys):
        """Test _output_human in verbose mode showing details"""
        from unittest.mock import Mock
        from itential_mcp.platform.connection_test import CheckStatus

        result = Mock()
        result.success = True
        result.platform_version = "2024.1"
        result.authenticated_user = "admin"
        result.duration_ms = 150.5
        result.error = None

        check = Mock()
        check.status = CheckStatus.PASSED
        check.message = "API check: Successful"
        check.duration_ms = 75.3
        check.details = {"endpoint": "/health", "status_code": 200}
        check.error = None
        check.suggestion = None

        result.checks = [check]

        commands._output_human(result, verbose=True)

        captured = capsys.readouterr()
        assert "Duration:" in captured.out
        assert "75ms" in captured.out
        assert "Details:" in captured.out
        assert "endpoint:" in captured.out
        assert "/health" in captured.out

    def test_output_human_verbose_mode_with_error(self, capsys):
        """Test _output_human in verbose mode showing error details"""
        from unittest.mock import Mock
        from itential_mcp.platform.connection_test import CheckStatus

        result = Mock()
        result.success = False
        result.error = "Test failed"

        check = Mock()
        check.status = CheckStatus.FAILED
        check.message = "Test failed"
        check.duration_ms = 50.0
        check.details = None
        check.error = RuntimeError("Connection refused")
        check.suggestion = None

        result.checks = [check]

        commands._output_human(result, verbose=True)

        captured = capsys.readouterr()
        assert "Error:" in captured.out
        assert "RuntimeError" in captured.out
        assert "Connection refused" in captured.out


class TestOutputJson:
    """Test cases for _output_json function"""

    def test_output_json_exists(self):
        """Test that _output_json function exists"""
        assert hasattr(commands, "_output_json")
        assert callable(commands._output_json)

    def test_output_json_basic_structure(self, capsys):
        """Test _output_json outputs valid JSON with correct structure"""
        from unittest.mock import Mock
        import json

        result = Mock()
        result.success = True
        result.duration_ms = 150.5
        result.platform_version = "2024.1"
        result.authenticated_user = "admin"
        result.error = None
        result.checks = []

        commands._output_json(result)

        captured = capsys.readouterr()
        output = json.loads(captured.out)

        assert output["success"] is True
        assert output["duration_ms"] == 150.5
        assert "timestamp" in output
        assert "checks" in output
        assert "summary" in output
        assert output["platform_version"] == "2024.1"
        assert output["authenticated_user"] == "admin"

    def test_output_json_with_checks(self, capsys):
        """Test _output_json with check results"""
        from unittest.mock import Mock
        from itential_mcp.platform.connection_test import CheckStatus
        import json

        result = Mock()
        result.success = True
        result.duration_ms = 150.5
        result.platform_version = None
        result.authenticated_user = None
        result.error = None

        check = Mock()
        check.name = "dns_resolution"
        check.status = CheckStatus.PASSED
        check.message = "DNS resolution successful"
        check.duration_ms = 50.2
        check.details = {"resolved_ip": "192.168.1.1"}
        check.suggestion = None
        check.error = None

        result.checks = [check]

        commands._output_json(result)

        captured = capsys.readouterr()
        output = json.loads(captured.out)

        assert len(output["checks"]) == 1
        assert output["checks"][0]["name"] == "dns_resolution"
        assert output["checks"][0]["status"] == CheckStatus.PASSED
        assert output["checks"][0]["message"] == "DNS resolution successful"
        assert output["checks"][0]["duration_ms"] == 50.2
        assert output["checks"][0]["details"]["resolved_ip"] == "192.168.1.1"

    def test_output_json_with_error(self, capsys):
        """Test _output_json with error information"""
        from unittest.mock import Mock
        from itential_mcp.platform.connection_test import CheckStatus
        import json

        result = Mock()
        result.success = False
        result.duration_ms = 100.0
        result.platform_version = None
        result.authenticated_user = None
        result.error = "Connection timeout"

        check = Mock()
        check.name = "connectivity"
        check.status = CheckStatus.FAILED
        check.message = "Connection failed"
        check.duration_ms = 100.0
        check.details = None
        check.suggestion = "Check network settings"
        check.error = TimeoutError("Connection timeout")

        result.checks = [check]

        commands._output_json(result)

        captured = capsys.readouterr()
        output = json.loads(captured.out)

        assert output["success"] is False
        assert output["error"] == "Connection timeout"
        assert output["checks"][0]["suggestion"] == "Check network settings"
        assert output["checks"][0]["error"]["type"] == "TimeoutError"
        assert output["checks"][0]["error"]["message"] == "Connection timeout"

    def test_output_json_summary_statistics(self, capsys):
        """Test _output_json includes correct summary statistics"""
        from unittest.mock import Mock
        from itential_mcp.platform.connection_test import CheckStatus
        import json

        result = Mock()
        result.success = True
        result.duration_ms = 200.0
        result.platform_version = None
        result.authenticated_user = None
        result.error = None

        check1 = Mock()
        check1.name = "check1"
        check1.status = CheckStatus.PASSED
        check1.message = "Passed"
        check1.duration_ms = 50.0
        check1.details = None
        check1.suggestion = None
        check1.error = None

        check2 = Mock()
        check2.name = "check2"
        check2.status = CheckStatus.FAILED
        check2.message = "Failed"
        check2.duration_ms = 50.0
        check2.details = None
        check2.suggestion = None
        check2.error = None

        check3 = Mock()
        check3.name = "check3"
        check3.status = CheckStatus.SKIPPED
        check3.message = "Skipped"
        check3.duration_ms = 0.0
        check3.details = None
        check3.suggestion = None
        check3.error = None

        check4 = Mock()
        check4.name = "check4"
        check4.status = CheckStatus.WARNING
        check4.message = "Warning"
        check4.duration_ms = 50.0
        check4.details = None
        check4.suggestion = None
        check4.error = None

        result.checks = [check1, check2, check3, check4]

        commands._output_json(result)

        captured = capsys.readouterr()
        output = json.loads(captured.out)

        assert output["summary"]["total_checks"] == 4
        assert output["summary"]["passed"] == 1
        assert output["summary"]["failed"] == 1
        assert output["summary"]["skipped"] == 1
        assert output["summary"]["warnings"] == 1
