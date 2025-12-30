# Copyright (c) 2025 Itential, Inc
# GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

import pytest

from itential_mcp.utilities.string import (
    tostr,
    tobytes,
    toint,
    tobool,
    is_valid_url_path,
)


class TestStringUtils:
    @pytest.mark.parametrize(
        "input_val,expected",
        [
            ("hello", "hello"),
            (123, "123"),
            (None, None),
            (True, "True"),
        ],
    )
    def test_tostr(self, input_val, expected):
        assert tostr(input_val) == (str(expected) if expected is not None else expected)

    @pytest.mark.parametrize(
        "input_val,encoding,expected",
        [
            ("hello", "utf-8", b"hello"),
            ("¡hola!", "utf-8", b"\xc2\xa1hola!"),
            ("test", "ascii", b"test"),
        ],
    )
    def test_tobytes(self, input_val, encoding, expected):
        assert tobytes(input_val, encoding) == expected

    def test_tobytes_invalid_type(self):
        with pytest.raises(AttributeError):
            tobytes(None)

    @pytest.mark.parametrize(
        "input_val,expected",
        [
            ("42", 42),
            ("0", 0),
            ("-15", -15),
        ],
    )
    def test_toint_valid(self, input_val, expected):
        assert toint(input_val) == expected

    @pytest.mark.parametrize("input_val", ["abc", "", None])
    def test_toint_invalid(self, input_val):
        with pytest.raises((ValueError, TypeError)):
            toint(input_val)

    @pytest.mark.parametrize(
        "input_val,expected",
        [
            ("true", True),
            ("True", True),
            ("1", True),
            ("yes", True),
            ("on", True),
            ("false", False),
            ("0", False),
            ("off", False),
            ("", False),
            (None, False),
        ],
    )
    def test_tobool_string_inputs(self, input_val, expected):
        assert tobool(input_val) is expected

    def test_tobool_native_boolean(self):
        assert tobool(True) is True
        assert tobool(False) is False


class TestIsValidUrlPath:
    """Test the is_valid_url_path function"""

    def test_valid_paths(self):
        """Test is_valid_url_path with valid URL paths"""
        valid_paths = [
            "",  # Empty string is valid (root path)
            "/",  # Root path
            "/api",  # Simple path
            "/api/v1",  # Nested path
            "/api/v1/users",  # Multiple segments
            "/path/with-dashes",  # Dashes are allowed
            "/path/with_underscores",  # Underscores are allowed
            "/path/with.dots",  # Dots are allowed
            "/path/123",  # Numbers are allowed
            "/path/with%20encoded",  # URL encoded characters
            "/a/b/c/d/e/f",  # Deep nesting
            "/users/123/profile",  # Common API pattern
            "api/without/leading/slash",  # No leading slash
            "/mixed-path_with.various123/characters",  # Mixed valid characters
        ]

        for path in valid_paths:
            assert is_valid_url_path(path) is True, f"Path '{path}' should be valid"

    def test_invalid_paths_with_forbidden_characters(self):
        """Test is_valid_url_path with invalid characters"""
        invalid_paths = [
            "/path with spaces",  # Spaces are invalid
            "/path<with>brackets",  # Angle brackets
            '/path"with"quotes',  # Double quotes
            "/path{with}braces",  # Curly braces
            "/path|with|pipes",  # Pipe characters
            "/path\\with\\backslashes",  # Backslashes
            "/path^with^carets",  # Caret characters
            "/path`with`backticks",  # Backticks
        ]

        for path in invalid_paths:
            assert is_valid_url_path(path) is False, f"Path '{path}' should be invalid"

    def test_invalid_paths_with_query_fragment_chars(self):
        """Test is_valid_url_path with query and fragment characters"""
        invalid_paths = [
            "/path?query=value",  # Question mark (query)
            "/path#fragment",  # Hash (fragment)
            "/path?query=value#fragment",  # Both query and fragment
            "/api/users?id=123",  # Common query pattern
            "/page#section",  # Fragment identifier
            "/path/with?multiple&query=params",  # Multiple query parameters
        ]

        for path in invalid_paths:
            assert is_valid_url_path(path) is False, f"Path '{path}' should be invalid"

    def test_paths_with_double_slashes(self):
        """Test is_valid_url_path with double slashes (technically valid)"""
        double_slash_paths = [
            "//",  # Double slash at root
            "/path//with//double//slashes",  # Multiple double slashes
            "/api//v1",  # Double slash between segments
            "//api/v1",  # Leading double slash
            "/api/v1//",  # Trailing double slash
        ]

        for path in double_slash_paths:
            assert is_valid_url_path(path) is True, (
                f"Path '{path}' with double slashes should be valid"
            )

    def test_type_error_for_non_string(self):
        """Test is_valid_url_path raises TypeError for non-string input"""
        non_string_inputs = [
            123,  # Integer
            12.34,  # Float
            True,  # Boolean
            None,  # None
            [],  # List
            {},  # Dictionary
            set(),  # Set
            ("tuple",),  # Tuple
        ]

        for input_val in non_string_inputs:
            with pytest.raises(TypeError, match="Path must be a string"):
                is_valid_url_path(input_val)

    def test_edge_cases(self):
        """Test is_valid_url_path edge cases"""
        # Long path should be valid
        long_path = "/very/long/path/with/many/segments/" + "segment/" * 50
        assert is_valid_url_path(long_path) is True

        # Path with only slashes
        slash_only = "/" * 10
        assert is_valid_url_path(slash_only) is True

        # Single character paths
        assert is_valid_url_path("a") is True
        assert is_valid_url_path("/a") is True
        assert is_valid_url_path("1") is True

    def test_special_valid_characters(self):
        """Test is_valid_url_path with special but valid characters"""
        valid_special_paths = [
            "/path/with-dashes",
            "/path/with_underscores",
            "/path/with.periods",
            "/path/with:colons",
            "/path/with@at-signs",
            "/path/with!exclamations",
            "/path/with$dollar",
            "/path/with&ampersands",
            "/path/with'apostrophes",
            "/path/with(parentheses)",
            "/path/with*asterisks",
            "/path/with+plus",
            "/path/with,commas",
            "/path/with;semicolons",
            "/path/with=equals",
            "/path/123456789",  # All numbers
            "/path/%20encoded",  # URL encoded space
        ]

        for path in valid_special_paths:
            assert is_valid_url_path(path) is True, f"Path '{path}' should be valid"

    def test_unicode_characters(self):
        """Test is_valid_url_path with unicode characters"""
        # Unicode characters should be valid (they can be URL encoded)
        unicode_paths = [
            "/路径/中文",  # Chinese characters
            "/путь/русский",  # Cyrillic characters
            "/パス/日本語",  # Japanese characters
            "/émojis/🚀",  # Emojis
            "/café/naïve",  # Accented characters
        ]

        for path in unicode_paths:
            assert is_valid_url_path(path) is True, (
                f"Unicode path '{path}' should be valid"
            )

    def test_whitespace_characters_validation(self):
        """Test is_valid_url_path with various whitespace characters

        Note: The current implementation only checks for space character,
        not other whitespace like tabs or newlines.
        """
        # These should be invalid (space is explicitly checked)
        invalid_whitespace_paths = [
            "/path with spaces",
            "/path with\x20space",  # \x20 is space character
        ]

        for path in invalid_whitespace_paths:
            assert is_valid_url_path(path) is False, (
                f"Path with space '{path}' should be invalid"
            )

        # These are currently considered valid by the implementation
        # (tabs, newlines are not explicitly checked)
        potentially_valid_paths = [
            "/path\twith\ttabs",  # Tab characters
            "/path\nwith\nnewlines",  # Newline characters
        ]

        for path in potentially_valid_paths:
            # Just document current behavior - these pass validation
            # These currently return True because only specific chars are checked
            assert is_valid_url_path(path) is True, (
                f"Path '{path}' currently passes validation"
            )
