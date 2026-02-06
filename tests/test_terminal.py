# Copyright (c) 2025 Itential, Inc
# GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

import pytest
from unittest.mock import Mock, patch
import shutil
import os

from itential_mcp.cli import terminal


class TestGetcols:
    """Test cases for the getcols function."""

    def test_getcols_function_exists(self):
        """Test that getcols function exists and is callable."""
        assert hasattr(terminal, "getcols")
        assert callable(terminal.getcols)

    def test_getcols_returns_integer(self):
        """Test that getcols returns an integer."""
        result = terminal.getcols()
        assert isinstance(result, int)

    def test_getcols_returns_positive_value(self):
        """Test that getcols returns a positive integer."""
        result = terminal.getcols()
        assert result > 0

    def test_getcols_no_parameters(self):
        """Test that getcols accepts no parameters."""
        import inspect

        sig = inspect.signature(terminal.getcols)
        params = list(sig.parameters.keys())

        # Should have no parameters
        assert len(params) == 0

    def test_getcols_docstring(self):
        """Test that getcols has proper docstring."""
        assert terminal.getcols.__doc__ is not None
        assert (
            "Get the number of columns for the current terminal session"
            in terminal.getcols.__doc__
        )
        assert (
            "int: The number of columns for the current terminal"
            in terminal.getcols.__doc__
        )

    @patch("shutil.get_terminal_size")
    def test_getcols_uses_shutil_get_terminal_size(self, mock_get_terminal_size):
        """Test that getcols uses shutil.get_terminal_size."""
        # Mock the terminal size
        mock_size = Mock()
        mock_size.columns = 80
        mock_get_terminal_size.return_value = mock_size

        result = terminal.getcols()

        # Verify the function was called
        mock_get_terminal_size.assert_called_once()
        assert result == 80

    @patch("shutil.get_terminal_size")
    def test_getcols_various_column_sizes(self, mock_get_terminal_size):
        """Test getcols with various column sizes."""
        test_sizes = [1, 20, 80, 120, 200, 999]

        for size in test_sizes:
            mock_size = Mock()
            mock_size.columns = size
            mock_get_terminal_size.return_value = mock_size

            result = terminal.getcols()
            assert result == size

    @patch("shutil.get_terminal_size")
    def test_getcols_edge_cases(self, mock_get_terminal_size):
        """Test getcols with edge case values."""
        # Test with minimum possible value
        mock_size = Mock()
        mock_size.columns = 1
        mock_get_terminal_size.return_value = mock_size

        result = terminal.getcols()
        assert result == 1

        # Test with very large value
        mock_size.columns = 9999
        mock_get_terminal_size.return_value = mock_size

        result = terminal.getcols()
        assert result == 9999

    @patch("shutil.get_terminal_size")
    def test_getcols_returns_columns_attribute(self, mock_get_terminal_size):
        """Test that getcols specifically returns the columns attribute."""
        mock_size = Mock()
        mock_size.columns = 100
        mock_size.lines = 50  # This should be ignored
        mock_get_terminal_size.return_value = mock_size

        result = terminal.getcols()
        assert result == 100
        assert result != 50  # Should not return lines

    def test_getcols_consistent_calls(self):
        """Test that getcols returns consistent results on multiple calls."""
        # Note: This test assumes terminal size doesn't change during test execution
        result1 = terminal.getcols()
        result2 = terminal.getcols()
        result3 = terminal.getcols()

        assert result1 == result2 == result3

    def test_getcols_function_signature(self):
        """Test that getcols has the correct function signature."""
        import inspect

        sig = inspect.signature(terminal.getcols)

        # Check return annotation
        assert sig.return_annotation is int

        # Check no parameters
        assert len(sig.parameters) == 0

    @patch("shutil.get_terminal_size")
    def test_getcols_preserves_shutil_call_format(self, mock_get_terminal_size):
        """Test that getcols calls shutil.get_terminal_size with no arguments."""
        mock_size = Mock()
        mock_size.columns = 80
        mock_get_terminal_size.return_value = mock_size

        terminal.getcols()

        # Verify called with no arguments
        mock_get_terminal_size.assert_called_once_with()

    def test_getcols_integration_with_real_terminal(self):
        """Integration test with real terminal size."""
        # This test uses the actual shutil.get_terminal_size
        result = terminal.getcols()

        # Verify it's a reasonable terminal size
        assert isinstance(result, int)
        assert 1 <= result <= 1000  # Reasonable bounds for terminal width

    def test_getcols_is_not_async(self):
        """Test that getcols is not an async function."""
        import asyncio

        assert not asyncio.iscoroutinefunction(terminal.getcols)


class TestTerminalModule:
    """Test cases for the terminal module as a whole."""

    def test_module_imports(self):
        """Test that the module has correct imports."""
        assert hasattr(terminal, "shutil")
        assert terminal.shutil == shutil

    def test_module_structure(self):
        """Test the overall module structure."""
        # Check that only expected functions/attributes are present
        expected_attrs = ["getcols", "shutil"]

        # Get all public attributes (not starting with _)
        public_attrs = [attr for attr in dir(terminal) if not attr.startswith("_")]

        # Should contain at least our expected attributes
        for attr in expected_attrs:
            assert attr in public_attrs

    def test_module_has_copyright(self):
        """Test that the module file has copyright header."""
        import itential_mcp.cli.terminal
        import inspect

        source = inspect.getsource(itential_mcp.cli.terminal)
        assert "Copyright (c) 2025 Itential, Inc" in source
        assert "GNU General Public License v3.0+" in source


class TestTerminalIntegration:
    """Integration tests for terminal functionality."""

    def test_getcols_with_different_environments(self):
        """Test getcols behavior in different environment scenarios."""
        # Test in current environment
        result = terminal.getcols()
        assert isinstance(result, int)
        assert result > 0

    @patch.dict(os.environ, {"COLUMNS": "100"}, clear=False)
    def test_getcols_with_columns_env_var(self):
        """Test getcols when COLUMNS environment variable is set."""
        # Note: shutil.get_terminal_size may still use actual terminal size
        # This test ensures our function still works regardless
        result = terminal.getcols()
        assert isinstance(result, int)
        assert result > 0

    @patch("shutil.get_terminal_size")
    def test_getcols_error_handling(self, mock_get_terminal_size):
        """Test getcols behavior when shutil.get_terminal_size has issues."""
        # Test what happens if shutil.get_terminal_size raises an exception
        mock_get_terminal_size.side_effect = OSError("Terminal not available")

        with pytest.raises(OSError):
            terminal.getcols()

    def test_getcols_callable_multiple_times(self):
        """Test that getcols can be called multiple times safely."""
        results = []

        for _ in range(10):
            result = terminal.getcols()
            results.append(result)
            assert isinstance(result, int)
            assert result > 0

        # All results should be the same (assuming terminal doesn't resize)
        assert all(r == results[0] for r in results)

    @patch("shutil.get_terminal_size")
    def test_getcols_performance(self, mock_get_terminal_size):
        """Test that getcols performs reasonably well."""
        import time

        mock_size = Mock()
        mock_size.columns = 80
        mock_get_terminal_size.return_value = mock_size

        # Measure time for multiple calls
        start_time = time.time()
        for _ in range(100):
            terminal.getcols()
        end_time = time.time()

        # Should complete 100 calls in less than 1 second
        assert (end_time - start_time) < 1.0


class TestColors:
    """Test cases for Colors class."""

    def test_colors_class_exists(self):
        """Test that Colors class exists."""
        assert hasattr(terminal, "Colors")

    def test_colors_constants_exist(self):
        """Test that all color constants exist."""
        assert hasattr(terminal.Colors, "RED")
        assert hasattr(terminal.Colors, "GREEN")
        assert hasattr(terminal.Colors, "YELLOW")
        assert hasattr(terminal.Colors, "BLUE")
        assert hasattr(terminal.Colors, "RESET")
        assert hasattr(terminal.Colors, "BOLD")

    def test_colors_are_strings(self):
        """Test that all colors are strings."""
        assert isinstance(terminal.Colors.RED, str)
        assert isinstance(terminal.Colors.GREEN, str)
        assert isinstance(terminal.Colors.YELLOW, str)
        assert isinstance(terminal.Colors.BLUE, str)
        assert isinstance(terminal.Colors.RESET, str)
        assert isinstance(terminal.Colors.BOLD, str)


class TestPrintFunctions:
    """Test cases for terminal print functions."""

    def test_print_success_function_exists(self):
        """Test that print_success function exists."""
        assert hasattr(terminal, "print_success")
        assert callable(terminal.print_success)

    def test_print_error_function_exists(self):
        """Test that print_error function exists."""
        assert hasattr(terminal, "print_error")
        assert callable(terminal.print_error)

    def test_print_warning_function_exists(self):
        """Test that print_warning function exists."""
        assert hasattr(terminal, "print_warning")
        assert callable(terminal.print_warning)

    def test_print_info_function_exists(self):
        """Test that print_info function exists."""
        assert hasattr(terminal, "print_info")
        assert callable(terminal.print_info)

    def test_print_success_outputs_message(self, capsys):
        """Test that print_success outputs the message with color."""
        terminal.print_success("Test success message")

        captured = capsys.readouterr()
        assert "Test success message" in captured.out
        assert terminal.Colors.GREEN in captured.out
        assert terminal.Colors.RESET in captured.out

    def test_print_error_outputs_message(self, capsys):
        """Test that print_error outputs the message with color."""
        terminal.print_error("Test error message")

        captured = capsys.readouterr()
        assert "Test error message" in captured.out
        assert terminal.Colors.RED in captured.out
        assert terminal.Colors.RESET in captured.out

    def test_print_warning_outputs_message(self, capsys):
        """Test that print_warning outputs the message with color."""
        terminal.print_warning("Test warning message")

        captured = capsys.readouterr()
        assert "Test warning message" in captured.out
        assert terminal.Colors.YELLOW in captured.out
        assert terminal.Colors.RESET in captured.out

    def test_print_info_outputs_message(self, capsys):
        """Test that print_info outputs the message with color."""
        terminal.print_info("Test info message")

        captured = capsys.readouterr()
        assert "Test info message" in captured.out
        assert terminal.Colors.BLUE in captured.out
        assert terminal.Colors.RESET in captured.out

    def test_print_functions_with_empty_string(self, capsys):
        """Test print functions with empty string."""
        terminal.print_success("")
        terminal.print_error("")
        terminal.print_warning("")
        terminal.print_info("")

        captured = capsys.readouterr()
        # Should output color codes even with empty message
        assert captured.out

    def test_print_functions_with_special_characters(self, capsys):
        """Test print functions with special characters."""
        special_message = "Test: \n\t~!@#$%^&*()_+{}[]|\\:;\"'<>?,./`"

        terminal.print_success(special_message)
        terminal.print_error(special_message)
        terminal.print_warning(special_message)
        terminal.print_info(special_message)

        captured = capsys.readouterr()
        # Should output all instances of the message
        assert captured.out.count(special_message) == 4
