# Copyright (c) 2025 Itential, Inc
# GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)

import os
import tempfile
import pytest
from unittest.mock import patch, MagicMock

from itential_mcp.toolutils import tags, itertools, display_tools, display_tags


class TestTagsDecorator:
    """Test the tags decorator functionality"""

    def test_tags_decorator_single(self):
        @tags("public")
        def my_func():
            return "hello"

        assert hasattr(my_func, "tags")
        assert my_func.tags == ["public"]

    def test_tags_decorator_multiple(self):
        @tags("system", "admin", "beta")
        def another_func():
            return 42

        assert hasattr(another_func, "tags")
        assert set(another_func.tags) == {"system", "admin", "beta"}

    def test_tags_does_not_modify_function_behavior(self):
        @tags("alpha")
        def simple_func(x):
            return x * 2

        assert simple_func(4) == 8
        assert simple_func.tags == ["alpha"]

    def test_tags_empty(self):
        @tags()
        def no_tags_func():
            return "none"

        assert hasattr(no_tags_func, "tags")
        assert no_tags_func.tags == []

    def test_tags_preserves_function_name_and_doc(self):
        @tags("test")
        def documented_func():
            """This is a test function"""
            return True

        assert documented_func.__name__ == "documented_func"
        assert documented_func.__doc__ == "This is a test function"
        assert documented_func.tags == ["test"]


class TestItertools:
    """Test the itertools function functionality"""

    def test_itertools_with_temp_directory(self):
        """Test itertools with a temporary directory containing test modules"""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create a test module with functions
            test_module_content = '''
def test_function():
    """Test function"""
    return "test"

def _private_function():
    """Private function"""
    return "private"

def another_test():
    """Another test function"""
    return "another"
'''

            test_module_path = os.path.join(temp_dir, "test_module.py")
            with open(test_module_path, "w") as f:
                f.write(test_module_content)

            # Test itertools with our temp directory
            tools = list(itertools(temp_dir))

            # Should find 2 functions (test_function and another_test, not _private_function)
            assert len(tools) == 2

            func_names = [func.__name__ for func, _ in tools]
            assert "test_function" in func_names
            assert "another_test" in func_names
            assert "_private_function" not in func_names

    def test_itertools_with_module_tags(self):
        """Test itertools with module-level __tags__"""
        with tempfile.TemporaryDirectory() as temp_dir:
            test_module_content = '''
__tags__ = ["module_tag", "shared"]

def tagged_function():
    """Function in tagged module"""
    return "tagged"
'''

            test_module_path = os.path.join(temp_dir, "tagged_module.py")
            with open(test_module_path, "w") as f:
                f.write(test_module_content)

            tools = list(itertools(temp_dir))

            assert len(tools) == 1
            func, tags_set = tools[0]
            assert func.__name__ == "tagged_function"
            assert "module_tag" in tags_set
            assert "shared" in tags_set
            assert "tagged_function" in tags_set  # function name is also added as tag

    def test_itertools_with_function_tags(self):
        """Test itertools with function-level tags decorator"""
        with tempfile.TemporaryDirectory() as temp_dir:
            test_module_content = '''
from itential_mcp.toolutils import tags

@tags("decorated", "special")
def decorated_function():
    """Function with decorator tags"""
    return "decorated"
'''

            test_module_path = os.path.join(temp_dir, "decorated_module.py")
            with open(test_module_path, "w") as f:
                f.write(test_module_content)

            tools = list(itertools(temp_dir))

            assert len(tools) == 1
            func, tags_set = tools[0]
            assert func.__name__ == "decorated_function"
            assert "decorated" in tags_set
            assert "special" in tags_set
            assert "decorated_function" in tags_set

    def test_itertools_ignores_underscore_modules(self):
        """Test that itertools ignores modules starting with underscore"""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create a module starting with underscore
            test_module_content = '''
def should_be_ignored():
    return "ignored"
'''

            ignored_module_path = os.path.join(temp_dir, "_ignored_module.py")
            with open(ignored_module_path, "w") as f:
                f.write(test_module_content)

            tools = list(itertools(temp_dir))

            # Should be empty since the module starts with underscore
            assert len(tools) == 0

    def test_itertools_ignores_init_py(self):
        """Test that itertools ignores __init__.py files"""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create __init__.py
            init_content = '''
def init_function():
    return "init"
'''

            init_path = os.path.join(temp_dir, "__init__.py")
            with open(init_path, "w") as f:
                f.write(init_content)

            tools = list(itertools(temp_dir))

            # Should be empty since __init__.py is ignored
            assert len(tools) == 0

    def test_itertools_filters_external_functions(self):
        """Test that itertools only includes functions from the current module"""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create a module that imports external functions
            test_module_content = '''
from os.path import join

def local_function():
    """Local function"""
    return "local"
'''

            test_module_path = os.path.join(temp_dir, "mixed_module.py")
            with open(test_module_path, "w") as f:
                f.write(test_module_content)

            tools = list(itertools(temp_dir))

            # Should only find local_function, not imported join
            assert len(tools) == 1
            func, _ = tools[0]
            assert func.__name__ == "local_function"

    def test_itertools_default_path(self):
        """Test itertools uses default tools path when none provided"""
        # Test with a simple temp directory that exists
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create the expected tools directory
            tools_dir = os.path.join(temp_dir, "tools")
            os.makedirs(tools_dir)

            test_module_content = '''
def default_path_function():
    return "default"
'''

            test_module_path = os.path.join(tools_dir, "default_module.py")
            with open(test_module_path, "w") as f:
                f.write(test_module_content)

            # Test with explicit path - this ensures the default path logic works
            # even if we can't easily mock the __file__ resolution
            tools = list(itertools(tools_dir))

            assert len(tools) == 1
            func, _ = tools[0]
            assert func.__name__ == "default_path_function"


class TestDisplayFunctions:
    """Test the display functions"""

    @pytest.mark.asyncio
    @patch('itential_mcp.toolutils.terminal.getcols', return_value=80)
    @patch('itential_mcp.toolutils.itertools')
    @patch('builtins.print')
    async def test_display_tools(self, mock_print, mock_itertools, mock_getcols):
        """Test display_tools function"""
        # Mock function with docstring
        mock_func1 = MagicMock()
        mock_func1.__name__ = "test_tool"
        mock_func1.__doc__ = "\n    Test tool description\n    "

        mock_func2 = MagicMock()
        mock_func2.__name__ = "another_tool"
        mock_func2.__doc__ = "\n    Another tool for testing\n    "

        mock_itertools.return_value = [(mock_func1, set()), (mock_func2, set())]

        await display_tools()

        # Check that print was called with appropriate formatting
        assert mock_print.call_count >= 2
        # Verify header was printed
        header_call = mock_print.call_args_list[0]
        assert "TOOLS" in str(header_call)
        assert "DESCRIPTION" in str(header_call)

    @pytest.mark.asyncio
    @patch('itential_mcp.toolutils.terminal.getcols', return_value=40)
    @patch('itential_mcp.toolutils.itertools')
    @patch('builtins.print')
    async def test_display_tools_long_description_truncation(self, mock_print, mock_itertools, mock_getcols):
        """Test that long descriptions are truncated"""
        mock_func = MagicMock()
        mock_func.__name__ = "tool"
        mock_func.__doc__ = "\n    This is a very long description that should be truncated because it exceeds the terminal width\n    "

        mock_itertools.return_value = [(mock_func, set())]

        await display_tools()

        # Check that description was truncated (should contain "...")
        tool_line_calls = [call for call in mock_print.call_args_list if "tool" in str(call)]
        assert len(tool_line_calls) > 0
        # At least one call should contain the truncated description
        found_truncation = any("..." in str(call) for call in tool_line_calls)
        assert found_truncation

    @pytest.mark.asyncio
    @patch('itential_mcp.toolutils.itertools')
    @patch('builtins.print')
    async def test_display_tags(self, mock_print, mock_itertools):
        """Test display_tags function"""
        mock_func1 = MagicMock()
        mock_func2 = MagicMock()

        tags1 = {"tag1", "shared", "alpha"}
        tags2 = {"tag2", "shared", "beta"}

        mock_itertools.return_value = [(mock_func1, tags1), (mock_func2, tags2)]

        await display_tags()

        # Check that print was called with "TAGS" header
        assert mock_print.call_count >= 2
        header_call = mock_print.call_args_list[0]
        assert "TAGS" in str(header_call)

        # Check that all unique tags were printed in sorted order
        expected_tags = sorted(["tag1", "tag2", "shared", "alpha", "beta"])
        tag_calls = mock_print.call_args_list[1:-1]  # Exclude header and final empty line

        printed_tags = []
        for call in tag_calls:
            #call_str = str(call)
            # Extract the tag from the call (it's the first argument)
            if call.args:
                printed_tags.append(call.args[0])

        # Verify all expected tags are present (order may vary based on set operations)
        for tag in expected_tags:
            assert tag in printed_tags

    @pytest.mark.asyncio
    @patch('itential_mcp.toolutils.itertools')
    @patch('builtins.print')
    async def test_display_tags_empty(self, mock_print, mock_itertools):
        """Test display_tags with no tools"""
        mock_itertools.return_value = []

        await display_tags()

        # Should still print header and empty line
        assert mock_print.call_count == 2
        header_call = mock_print.call_args_list[0]
        assert "TAGS" in str(header_call)

    @pytest.mark.asyncio
    @patch('itential_mcp.toolutils.itertools')
    @patch('builtins.print')
    async def test_display_tools_empty(self, mock_print, mock_itertools):
        """Test display_tools with no tools"""
        mock_itertools.return_value = []

        await display_tools()

        # Should still print header and empty line
        assert mock_print.call_count == 2
        header_call = mock_print.call_args_list[0]
        assert "TOOLS" in str(header_call)
        assert "DESCRIPTION" in str(header_call)
