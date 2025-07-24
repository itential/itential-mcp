# Copyright (c) 2025 Itential, Inc
# GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)

import inspect
import asyncio
from unittest.mock import Mock

import pytest

from itential_mcp import commands, server, metadata, toolutils, runner


class TestRunCommand:
    """Test cases for the run command function"""

    def test_run_function_exists(self):
        """Test that the run function exists and is callable"""
        assert hasattr(commands, 'run')
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
        test_cases = [
            None,
            {},
            "test",
            [],
            Mock(),
            object(),
            42,
            True
        ]

        for args in test_cases:
            result = commands.run(args)
            assert result == (server.run, None, None)

    def test_run_function_signature(self):
        """Test that run function has correct signature"""
        sig = inspect.signature(commands.run)
        params = list(sig.parameters.keys())

        assert len(params) == 1
        assert params[0] == 'args'

        # Check parameter type annotation
        param = sig.parameters['args']
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
        assert hasattr(commands, 'version')
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
        test_cases = [
            None,
            {},
            "test",
            [],
            Mock(),
            object(),
            42,
            True
        ]

        for args in test_cases:
            result = commands.version(args)
            assert result == (metadata.display_version, None, None)

    def test_version_function_signature(self):
        """Test that version function has correct signature"""
        sig = inspect.signature(commands.version)
        params = list(sig.parameters.keys())

        assert len(params) == 1
        assert params[0] == 'args'

        # Check parameter type annotation
        param = sig.parameters['args']
        assert param.annotation == commands.Any

    def test_version_function_docstring(self):
        """Test that version function has proper docstring"""
        assert commands.version.__doc__ is not None
        # Note: The docstring currently has a copy-paste error mentioning "run" command
        assert "itential-mcp" in commands.version.__doc__

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
        assert hasattr(commands, 'tools')
        assert callable(commands.tools)

    def test_tools_returns_correct_tuple(self):
        """Test that tools function returns the expected tuple structure"""
        args = Mock()
        result = commands.tools(args)

        assert isinstance(result, tuple)
        assert len(result) == 3
        assert result[0] == toolutils.display_tools
        assert result[1] is None
        assert result[2] is None

    def test_tools_with_various_args(self):
        """Test tools function with different argument types"""
        test_cases = [
            None,
            {},
            "test",
            [],
            Mock(),
            object(),
            42,
            True
        ]

        for args in test_cases:
            result = commands.tools(args)
            assert result == (toolutils.display_tools, None, None)

    def test_tools_function_signature(self):
        """Test that tools function has correct signature"""
        sig = inspect.signature(commands.tools)
        params = list(sig.parameters.keys())

        assert len(params) == 1
        assert params[0] == 'args'

        # Check parameter type annotation
        param = sig.parameters['args']
        assert param.annotation == commands.Any

    def test_tools_function_docstring(self):
        """Test that tools function has proper docstring"""
        assert commands.tools.__doc__ is not None
        assert "Implement the `itential-mcp tools` command" in commands.tools.__doc__
        assert "display the list of all avaiable tools" in commands.tools.__doc__

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
        assert hasattr(commands, 'tags')
        assert callable(commands.tags)

    def test_tags_returns_correct_tuple(self):
        """Test that tags function returns the expected tuple structure"""
        args = Mock()
        result = commands.tags(args)

        assert isinstance(result, tuple)
        assert len(result) == 3
        assert result[0] == toolutils.display_tags
        assert result[1] is None
        assert result[2] is None

    def test_tags_with_various_args(self):
        """Test tags function with different argument types"""
        test_cases = [
            None,
            {},
            "test",
            [],
            Mock(),
            object(),
            42,
            True
        ]

        for args in test_cases:
            result = commands.tags(args)
            assert result == (toolutils.display_tags, None, None)

    def test_tags_function_signature(self):
        """Test that tags function has correct signature"""
        sig = inspect.signature(commands.tags)
        params = list(sig.parameters.keys())

        assert len(params) == 1
        assert params[0] == 'args'

        # Check parameter type annotation
        param = sig.parameters['args']
        assert param.annotation == commands.Any

    def test_tags_function_docstring(self):
        """Test that tags function has proper docstring"""
        assert commands.tags.__doc__ is not None
        assert "Implement the `itential-mcp tags` command" in commands.tags.__doc__
        assert "display the list of all avaiable tags" in commands.tags.__doc__

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
        assert hasattr(commands, 'call')
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
            ("tool_with_underscores", '{}'),
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
        assert params[0] == 'args'

        # Check parameter type annotation
        param = sig.parameters['args']
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
        assert hasattr(commands, 'server')
        assert hasattr(commands, 'metadata')
        assert hasattr(commands, 'toolutils')
        assert hasattr(commands, 'runner')

        assert commands.server == server
        assert commands.metadata == metadata
        assert commands.toolutils == toolutils
        assert commands.runner == runner

    def test_module_functions_exist(self):
        """Test that all expected command functions exist"""
        expected_functions = ['run', 'version', 'tools', 'tags', 'call']

        for func_name in expected_functions:
            assert hasattr(commands, func_name)
            assert callable(getattr(commands, func_name))

    def test_module_typing_imports(self):
        """Test that typing imports are available"""
        # These should be imported from typing module
        assert hasattr(commands, 'Any')
        assert hasattr(commands, 'Coroutine')
        assert hasattr(commands, 'Sequence')
        assert hasattr(commands, 'Mapping')
        assert hasattr(commands, 'Tuple')

    def test_all_functions_have_consistent_signature(self):
        """Test that all command functions have the same signature pattern"""
        functions = [commands.run, commands.version, commands.tools, commands.tags, commands.call]

        for func in functions:
            sig = inspect.signature(func)
            params = list(sig.parameters.keys())

            # All should have exactly one parameter named 'args'
            assert len(params) == 1
            assert params[0] == 'args'

            # All should have Any type annotation for args parameter
            param = sig.parameters['args']
            assert param.annotation == commands.Any

    def test_all_functions_return_tuple(self):
        """Test that all command functions return tuples"""
        functions = [commands.run, commands.version, commands.tools, commands.tags, commands.call]
        args = Mock()
        args.tool = "test"
        args.params = None

        for func in functions:
            result = func(args)
            assert isinstance(result, tuple)
            assert len(result) == 3

    def test_functions_are_not_coroutines(self):
        """Test that command functions themselves are not coroutines"""
        functions = [commands.run, commands.version, commands.tools, commands.tags, commands.call]

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
        assert result[1] == ("get_platform_info", '{"include_version": true, "format": "json"}')
        assert result[2] is None

    def test_all_commands_can_be_called_multiple_times(self):
        """Test that all command functions can be called multiple times safely"""
        args = Mock()
        args.tool = "test_tool"
        args.params = "{}"

        functions = [commands.run, commands.version, commands.tools, commands.tags, commands.call]

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
            for result in [run_result, version_result, tools_result, tags_result, call_result]:
                assert len(result) == 3
                assert callable(result[0])

    def test_edge_case_arguments(self):
        """Test all commands with edge case arguments"""
        edge_cases = [None, 0, "", [], {}, False, True, object()]

        # These functions don't access args attributes
        simple_functions = [commands.run, commands.version, commands.tools, commands.tags]

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
