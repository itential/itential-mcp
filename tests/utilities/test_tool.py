# Copyright (c) 2025 Itential, Inc
# GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import annotations

import os
import tempfile
import pytest
from unittest.mock import patch, MagicMock

from typing import Union

from pydantic import BaseModel

from mcp.types import ToolAnnotations

from itential_mcp.utilities.tool import (
    tags,
    annotate,
    itertools,
    display_tools,
    display_tags,
    get_json_schema,
)


class _SchemaModelA(BaseModel):
    """Simple BaseModel used to test get_json_schema regression behavior."""

    a: str


class _SchemaModelB(BaseModel):
    """Second BaseModel used to test get_json_schema union handling."""

    b: int


class TestGetJsonSchema:
    """Test the get_json_schema function"""

    def test_get_json_schema_with_basemodel(self):
        """A plain BaseModel return annotation should produce an object schema"""

        def fn() -> _SchemaModelA:
            return _SchemaModelA(a="x")

        schema = get_json_schema(fn)

        assert schema["type"] == "object"
        assert "a" in schema["properties"]

    def test_get_json_schema_with_union_of_basemodels_pipe_syntax(self):
        """A `X | Y` union of BaseModel subclasses should produce a valid
        schema instead of raising ValueError"""

        def fn() -> _SchemaModelA | _SchemaModelB:
            return _SchemaModelA(a="x")

        schema = get_json_schema(fn)

        assert "anyOf" in schema
        assert len(schema["anyOf"]) == 2

    def test_get_json_schema_with_typing_union_of_basemodels(self):
        """A typing.Union of BaseModel subclasses should produce a valid
        schema instead of raising ValueError"""

        def fn() -> Union[_SchemaModelA, _SchemaModelB]:
            return _SchemaModelA(a="x")

        schema = get_json_schema(fn)

        assert "anyOf" in schema
        assert len(schema["anyOf"]) == 2

    def test_get_json_schema_with_non_basemodel_raises(self):
        """A return annotation that is not a BaseModel should raise ValueError"""

        def fn() -> dict:
            return {}

        with pytest.raises(ValueError):
            get_json_schema(fn)

    def test_get_json_schema_with_union_of_non_basemodels_raises(self):
        """A union of non-BaseModel types should raise ValueError"""

        def fn() -> int | str:
            return 1

        with pytest.raises(ValueError):
            get_json_schema(fn)

    def test_get_json_schema_operations_manager_trigger_automation(self):
        """Regression test: trigger_automation's union return type must
        produce a valid schema without raising"""
        from itential_mcp.tools import operations_manager

        schema = get_json_schema(operations_manager.trigger_automation)

        assert "anyOf" in schema

    def test_get_json_schema_operations_manager_start_workflow(self):
        """Regression test: start_workflow's union return type must
        produce a valid schema without raising"""
        from itential_mcp.tools import operations_manager

        schema = get_json_schema(operations_manager.start_workflow)

        assert "anyOf" in schema

    def test_get_json_schema_templates_get_templates(self):
        """Regression test: get_templates now returns a RootModel
        (GetTemplatesResponse) so get_json_schema must no longer raise
        ValueError. Previously this tool's bare `list[...]` return
        annotation tripped the "missing or invalid output_schema" warning
        at server startup."""
        from itential_mcp.tools import templates

        schema = get_json_schema(templates.get_templates)

        # RootModel wrapping a list produces a top-level array schema, not
        # an object schema. server.py's own "== object" guard is what
        # decides whether to adopt this as a custom output_schema (it does
        # not, for an array-rooted schema) -- this test only pins that
        # get_json_schema itself succeeds without raising.
        assert schema["type"] == "array"


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

            func_names = [func.__name__ for func, _, _annotations in tools]
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
            func, tags_set, tool_annotations = tools[0]
            assert func.__name__ == "tagged_function"
            assert "module_tag" in tags_set
            assert "shared" in tags_set
            assert "tagged_function" in tags_set  # function name is also added as tag
            assert tool_annotations is None

    def test_itertools_with_function_tags(self):
        """Test itertools with function-level tags decorator"""
        with tempfile.TemporaryDirectory() as temp_dir:
            test_module_content = '''
from itential_mcp.utilities.tool import tags

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
            func, tags_set, tool_annotations = tools[0]
            assert func.__name__ == "decorated_function"
            assert "decorated" in tags_set
            assert "special" in tags_set
            assert "decorated_function" in tags_set
            assert tool_annotations is None

    def test_itertools_ignores_underscore_modules(self):
        """Test that itertools ignores modules starting with underscore"""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create a module starting with underscore
            test_module_content = """
def should_be_ignored():
    return "ignored"
"""

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
            init_content = """
def init_function():
    return "init"
"""

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
            func, _, _annotations = tools[0]
            assert func.__name__ == "local_function"

    def test_itertools_with_explicit_path(self):
        """Test itertools with explicit path parameter"""
        # Test with a simple temp directory that exists
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create the expected tools directory
            tools_dir = os.path.join(temp_dir, "tools")
            os.makedirs(tools_dir)

            test_module_content = """
def explicit_path_function():
    return "explicit"
"""

            test_module_path = os.path.join(tools_dir, "explicit_module.py")
            with open(test_module_path, "w") as f:
                f.write(test_module_content)

            # Test with explicit path
            tools = list(itertools(tools_dir))

            assert len(tools) == 1
            func, _, _annotations = tools[0]
            assert func.__name__ == "explicit_path_function"

    def test_itertools_path_parameter_required(self):
        """Test itertools requires path parameter"""
        # This test verifies the function signature change
        with pytest.raises(TypeError):
            list(itertools())  # Should fail without path parameter


class TestDisplayFunctions:
    """Test the display functions"""

    @pytest.mark.asyncio
    @patch("itential_mcp.utilities.tool.terminal.getcols", return_value=80)
    @patch("itential_mcp.utilities.tool.itertools")
    @patch("builtins.print")
    async def test_display_tools(self, mock_print, mock_itertools, mock_getcols):
        """Test display_tools function"""
        # Mock function with docstring
        mock_func1 = MagicMock()
        mock_func1.__name__ = "test_tool"
        mock_func1.__doc__ = "\n    Test tool description\n    "

        mock_func2 = MagicMock()
        mock_func2.__name__ = "another_tool"
        mock_func2.__doc__ = "\n    Another tool for testing\n    "

        mock_itertools.return_value = [
            (mock_func1, set(), None),
            (mock_func2, set(), None),
        ]

        await display_tools()

        # Check that print was called with appropriate formatting
        assert mock_print.call_count >= 2
        # Verify header was printed
        header_call = mock_print.call_args_list[0]
        assert "TOOLS" in str(header_call)
        assert "DESCRIPTION" in str(header_call)

    @pytest.mark.asyncio
    @patch("itential_mcp.utilities.tool.terminal.getcols", return_value=40)
    @patch("itential_mcp.utilities.tool.itertools")
    @patch("builtins.print")
    async def test_display_tools_long_description_truncation(
        self, mock_print, mock_itertools, mock_getcols
    ):
        """Test that long descriptions are truncated"""
        mock_func = MagicMock()
        mock_func.__name__ = "tool"
        mock_func.__doc__ = "\n    This is a very long description that should be truncated because it exceeds the terminal width\n    "

        mock_itertools.return_value = [(mock_func, set(), None)]

        await display_tools()

        # Check that description was truncated (should contain "...")
        tool_line_calls = [
            call for call in mock_print.call_args_list if "tool" in str(call)
        ]
        assert len(tool_line_calls) > 0
        # At least one call should contain the truncated description
        found_truncation = any("..." in str(call) for call in tool_line_calls)
        assert found_truncation

    @pytest.mark.asyncio
    @patch("itential_mcp.utilities.tool.itertools")
    @patch("builtins.print")
    async def test_display_tags(self, mock_print, mock_itertools):
        """Test display_tags function"""
        mock_func1 = MagicMock()
        mock_func2 = MagicMock()

        tags1 = {"tag1", "shared", "alpha"}
        tags2 = {"tag2", "shared", "beta"}

        mock_itertools.return_value = [
            (mock_func1, tags1, None),
            (mock_func2, tags2, None),
        ]

        await display_tags()

        # Check that print was called with "TAGS" header
        assert mock_print.call_count >= 2
        header_call = mock_print.call_args_list[0]
        assert "TAGS" in str(header_call)

        # Check that all unique tags were printed in sorted order
        expected_tags = sorted(["tag1", "tag2", "shared", "alpha", "beta"])
        tag_calls = mock_print.call_args_list[
            1:-1
        ]  # Exclude header and final empty line

        printed_tags = []
        for call in tag_calls:
            # call_str = str(call)
            # Extract the tag from the call (it's the first argument)
            if call.args:
                printed_tags.append(call.args[0])

        # Verify all expected tags are present (order may vary based on set operations)
        for tag in expected_tags:
            assert tag in printed_tags

    @pytest.mark.asyncio
    @patch("itential_mcp.utilities.tool.itertools")
    @patch("builtins.print")
    async def test_display_tags_empty(self, mock_print, mock_itertools):
        """Test display_tags with no tools"""
        mock_itertools.return_value = []

        await display_tags()

        # Should still print header and empty line
        assert mock_print.call_count == 2
        header_call = mock_print.call_args_list[0]
        assert "TAGS" in str(header_call)

    @pytest.mark.asyncio
    @patch("itential_mcp.utilities.tool.itertools")
    @patch("builtins.print")
    async def test_display_tools_empty(self, mock_print, mock_itertools):
        """Test display_tools with no tools"""
        mock_itertools.return_value = []

        await display_tools()

        # Should still print header and empty line
        assert mock_print.call_count == 2
        header_call = mock_print.call_args_list[0]
        assert "TOOLS" in str(header_call)
        assert "DESCRIPTION" in str(header_call)

    @pytest.mark.asyncio
    @patch("itential_mcp.utilities.tool.terminal.getcols", return_value=80)
    @patch("itential_mcp.utilities.tool.itertools")
    @patch("builtins.print")
    async def test_display_tools_google_style_docstring(
        self, mock_print, mock_itertools, mock_getcols
    ):
        """Google-style docstrings (summary on line 0) render the summary.

        This is a regression guard for the bug where `splitlines()[1]` picked
        the blank separator line instead of the summary for Google-style
        docstrings, rendering a blank description.
        """
        mock_func = MagicMock()
        mock_func.__name__ = "google_tool"
        mock_func.__doc__ = "Summary google style.\n\nBody."

        mock_itertools.return_value = [(mock_func, set(), None)]

        await display_tools()

        tool_line_calls = [
            call for call in mock_print.call_args_list if "google_tool" in str(call)
        ]
        assert len(tool_line_calls) == 1
        assert "Summary google style." in str(tool_line_calls[0])

    @pytest.mark.asyncio
    @patch("itential_mcp.utilities.tool.terminal.getcols", return_value=80)
    @patch("itential_mcp.utilities.tool.itertools")
    @patch("builtins.print")
    async def test_display_tools_leading_blank_docstring(
        self, mock_print, mock_itertools, mock_getcols
    ):
        """Leading-blank-line docstrings (health.py-style) still render correctly.

        Regression guard proving the fix does not break the previously
        working shape.
        """
        mock_func = MagicMock()
        mock_func.__name__ = "leading_blank_tool"
        mock_func.__doc__ = "\n    Summary leading blank.\n\n    Body.\n    "

        mock_itertools.return_value = [(mock_func, set(), None)]

        await display_tools()

        tool_line_calls = [
            call
            for call in mock_print.call_args_list
            if "leading_blank_tool" in str(call)
        ]
        assert len(tool_line_calls) == 1
        assert "Summary leading blank." in str(tool_line_calls[0])

    @pytest.mark.asyncio
    @patch("itential_mcp.utilities.tool.terminal.getcols", return_value=80)
    @patch("itential_mcp.utilities.tool.itertools")
    @patch("builtins.print")
    async def test_display_tools_oneliner_docstring(
        self, mock_print, mock_itertools, mock_getcols
    ):
        """One-liner docstrings with no body render correctly."""
        mock_func = MagicMock()
        mock_func.__name__ = "oneliner_tool"
        mock_func.__doc__ = "Do the thing."

        mock_itertools.return_value = [(mock_func, set(), None)]

        await display_tools()

        tool_line_calls = [
            call for call in mock_print.call_args_list if "oneliner_tool" in str(call)
        ]
        assert len(tool_line_calls) == 1
        assert "Do the thing." in str(tool_line_calls[0])

    @pytest.mark.asyncio
    @patch("itential_mcp.utilities.tool.terminal.getcols", return_value=80)
    @patch("itential_mcp.utilities.tool.itertools")
    @patch("builtins.print")
    async def test_display_tools_undocumented_tool(
        self, mock_print, mock_itertools, mock_getcols
    ):
        """Undocumented tools (`__doc__ is None`) render blank without crashing.

        Guards the `None.splitlines()` AttributeError the old code would
        raise for an undocumented tool.
        """
        mock_func = MagicMock()
        mock_func.__name__ = "undocumented_tool"
        mock_func.__doc__ = None

        mock_itertools.return_value = [(mock_func, set(), None)]

        # Should not raise
        await display_tools()

        tool_line_calls = [
            call
            for call in mock_print.call_args_list
            if "undocumented_tool" in str(call)
        ]
        assert len(tool_line_calls) == 1

    @pytest.mark.asyncio
    @patch("itential_mcp.utilities.tool.terminal.getcols", return_value=200)
    @patch("builtins.print")
    async def test_display_tools_real_affected_tools(self, mock_print, mock_getcols):
        """The 8 real tools named in the roadmap render non-empty, correct summaries.

        Runs the actual `display_tools()` (and therefore the real
        `itertools()` tool discovery) against the real `tools/` directory
        with no mocking of docstrings. This is the test that would have
        caught the original bug and guards against regression if docstring
        shapes drift.
        """
        expected = {
            "create_template": "Create a new template in Automation Studio.",
            "describe_template": (
                "Get detailed information about a specific template from "
                "Automation Studio."
            ),
            "update_template": "Update an existing template in Automation Studio.",
            "get_templates": "Get all templates from Automation Studio.",
            "describe_project": (
                "Get detailed information about a specific Automation Studio project."
            ),
            "get_projects": (
                "Get all Automation Studio projects from Itential Platform."
            ),
            "expose_agent": "Expose an agent as an API endpoint trigger.",
            "expose_workflow": "Expose a workflow as an API endpoint.",
        }

        await display_tools()

        printed_lines = [
            call.args[0] for call in mock_print.call_args_list if call.args
        ]

        for tool_name, summary in expected.items():
            matches = [line for line in printed_lines if line.startswith(tool_name)]
            assert len(matches) == 1, f"expected exactly one line for {tool_name}"
            assert summary in matches[0], (
                f"{tool_name} description missing expected summary: {matches[0]!r}"
            )


class TestAnnotateDecorator:
    """Test the annotate decorator functionality"""

    def test_annotate_sets_annotations_attribute(self):
        @annotate(read_only=True, idempotent=True, title="Get Health")
        def my_func():
            return "hello"

        assert hasattr(my_func, "annotations")
        assert isinstance(my_func.annotations, ToolAnnotations)
        assert my_func.annotations.readOnlyHint is True
        assert my_func.annotations.idempotentHint is True
        assert my_func.annotations.title == "Get Health"

    def test_annotate_destructive_tool(self):
        @annotate(read_only=False, destructive=True, open_world=True)
        def apply_config():
            return "applied"

        assert apply_config.annotations.readOnlyHint is False
        assert apply_config.annotations.destructiveHint is True
        assert apply_config.annotations.openWorldHint is True

    def test_annotate_defaults_to_none(self):
        @annotate()
        def unspecified_func():
            return None

        annotations = unspecified_func.annotations
        assert annotations.readOnlyHint is None
        assert annotations.destructiveHint is None
        assert annotations.idempotentHint is None
        assert annotations.openWorldHint is None
        assert annotations.title is None

    def test_annotate_does_not_modify_function_behavior(self):
        @annotate(read_only=True)
        def simple_func(x):
            return x * 2

        assert simple_func(4) == 8

    def test_annotate_preserves_function_name_and_doc(self):
        @annotate(read_only=True, title="Documented")
        def documented_func():
            """This is a test function"""
            return True

        assert documented_func.__name__ == "documented_func"
        assert documented_func.__doc__ == "This is a test function"


class TestItertoolsDeterministicOrdering:
    """Test that itertools yields tools in a stable, name-sorted order"""

    def test_itertools_stable_order_across_calls(self):
        """Two successive calls to itertools() over the same directory must
        yield tools in the same order."""
        with tempfile.TemporaryDirectory() as temp_dir:
            modules = {
                "zeta.py": "def zeta_func():\n    pass\n",
                "alpha.py": "def alpha_func():\n    pass\n",
                "mu.py": "def mu_func():\n    pass\n",
            }
            for filename, content in modules.items():
                with open(os.path.join(temp_dir, filename), "w") as f:
                    f.write(content)

            first_pass = [f.__name__ for f, _, _ann in itertools(temp_dir)]
            second_pass = [f.__name__ for f, _, _ann in itertools(temp_dir)]

            assert first_pass == second_pass

    def test_itertools_orders_by_module_file_name(self):
        """Module files must be discovered in name-sorted order regardless
        of filesystem/os.listdir() return order."""
        with tempfile.TemporaryDirectory() as temp_dir:
            modules = {
                "zeta.py": "def zeta_func():\n    pass\n",
                "alpha.py": "def alpha_func():\n    pass\n",
                "mu.py": "def mu_func():\n    pass\n",
            }
            for filename, content in modules.items():
                with open(os.path.join(temp_dir, filename), "w") as f:
                    f.write(content)

            names = [f.__name__ for f, _, _ann in itertools(temp_dir)]

            # Modules should be imported in sorted order: alpha, mu, zeta
            assert names == ["alpha_func", "mu_func", "zeta_func"]

    def test_real_tools_directory_discovery_is_stable(self):
        """Discovery order over the real tools/ package must be stable
        across two calls."""
        import pathlib

        path = (
            pathlib.Path(__file__).parent.parent.parent
            / "src"
            / "itential_mcp"
            / "tools"
        )

        first_pass = [f.__name__ for f, _, _ann in itertools(str(path))]
        second_pass = [f.__name__ for f, _, _ann in itertools(str(path))]

        assert first_pass == second_pass


class TestToolAnnotationCompleteness:
    """Completeness guard: every discovered static tool must be decorated
    with @annotate(...), so that a destructive tool can never end up
    unclassified (and therefore un-audited) by omission."""

    def _discover_real_tools(self):
        import pathlib

        path = (
            pathlib.Path(__file__).parent.parent.parent
            / "src"
            / "itential_mcp"
            / "tools"
        )
        return list(itertools(str(path)))

    def test_every_discovered_tool_has_annotations(self):
        tools = self._discover_real_tools()

        assert len(tools) > 0

        missing = [f.__name__ for f, _tags, ann in tools if ann is None]

        assert missing == [], (
            f"the following tools are missing @annotate(...) classification: {missing}"
        )


class TestToolAnnotationSafetyInvariants:
    """Safety-invariant tests over the real, decorated tool set."""

    _EXPLICITLY_DESTRUCTIVE = {
        "apply_device_configuration",
        "run_command",
        "run_command_template",
        "run_service",
        "import_gateway_configuration",
        "run_action",
        "delete_inventory",
        "remove_devices_from_group",
        "trigger_automation",
        "start_workflow",
        "start_adapter",
        "stop_adapter",
        "restart_adapter",
        "start_application",
        "stop_application",
        "restart_application",
    }

    def _discover_real_tools(self):
        import pathlib

        path = (
            pathlib.Path(__file__).parent.parent.parent
            / "src"
            / "itential_mcp"
            / "tools"
        )
        return list(itertools(str(path)))

    def test_no_tool_is_both_read_only_and_destructive(self):
        tools = self._discover_real_tools()

        violations = [
            f.__name__
            for f, _tags, ann in tools
            if ann is not None and ann.readOnlyHint and ann.destructiveHint
        ]

        assert violations == [], (
            f"the following tools are marked both readOnlyHint=True and "
            f"destructiveHint=True, which is a contradiction: {violations}"
        )

    def test_explicitly_destructive_tools_are_correctly_classified(self):
        tools = self._discover_real_tools()

        by_name = {f.__name__: ann for f, _tags, ann in tools}

        missing_from_discovery = self._EXPLICITLY_DESTRUCTIVE - by_name.keys()
        assert missing_from_discovery == set(), missing_from_discovery

        for name in self._EXPLICITLY_DESTRUCTIVE:
            ann = by_name[name]
            assert ann is not None, f"{name} has no annotations at all"
            assert ann.destructiveHint is True, f"{name} must have destructiveHint=True"
            assert not ann.readOnlyHint, f"{name} must not have readOnlyHint truthy"
