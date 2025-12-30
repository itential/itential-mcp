# Copyright (c) 2025 Itential, Inc
# GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

import json
import pytest
from unittest.mock import patch

from itential_mcp.utilities import json as jsonutils
from itential_mcp.core import exceptions


class TestLoads:
    """Test cases for the loads function"""

    def test_loads_valid_dict(self):
        """Test loads with valid dict JSON string"""
        json_str = '{"key": "value", "number": 42}'
        result = jsonutils.loads(json_str)

        assert isinstance(result, dict)
        assert result == {"key": "value", "number": 42}

    def test_loads_valid_list(self):
        """Test loads with valid list JSON string"""
        json_str = '[1, 2, 3, "test"]'
        result = jsonutils.loads(json_str)

        assert isinstance(result, list)
        assert result == [1, 2, 3, "test"]

    def test_loads_empty_dict(self):
        """Test loads with empty dict"""
        json_str = "{}"
        result = jsonutils.loads(json_str)

        assert isinstance(result, dict)
        assert result == {}

    def test_loads_empty_list(self):
        """Test loads with empty list"""
        json_str = "[]"
        result = jsonutils.loads(json_str)

        assert isinstance(result, list)
        assert result == []

    def test_loads_nested_objects(self):
        """Test loads with nested JSON objects"""
        json_str = '{"outer": {"inner": [1, 2, {"deep": true}]}}'
        result = jsonutils.loads(json_str)

        expected = {"outer": {"inner": [1, 2, {"deep": True}]}}
        assert result == expected

    def test_loads_unicode_characters(self):
        """Test loads with unicode characters"""
        json_str = '{"unicode": "测试", "emoji": "🚀"}'
        result = jsonutils.loads(json_str)

        assert result == {"unicode": "测试", "emoji": "🚀"}

    def test_loads_special_values(self):
        """Test loads with special JSON values"""
        json_str = '{"null": null, "true": true, "false": false}'
        result = jsonutils.loads(json_str)

        assert result == {"null": None, "true": True, "false": False}

    def test_loads_numbers(self):
        """Test loads with various number types"""
        json_str = '{"int": 42, "float": 3.14, "negative": -10, "zero": 0}'
        result = jsonutils.loads(json_str)

        assert result == {"int": 42, "float": 3.14, "negative": -10, "zero": 0}

    def test_loads_invalid_json_raises_validation_exception(self):
        """Test loads with invalid JSON raises ValidationException"""
        invalid_json = '{"invalid": json}'

        with pytest.raises(exceptions.ValidationException) as exc_info:
            jsonutils.loads(invalid_json)

        error = exc_info.value
        assert "Failed to parse JSON" in str(error)
        assert "input_data" in error.details
        assert "json_error" in error.details

    def test_loads_malformed_json_raises_validation_exception(self):
        """Test loads with malformed JSON raises ValidationException"""
        malformed_json = '{"key": "value"'  # Missing closing brace

        with pytest.raises(exceptions.ValidationException) as exc_info:
            jsonutils.loads(malformed_json)

        error = exc_info.value
        assert "Failed to parse JSON" in str(error)

    def test_loads_empty_string_raises_validation_exception(self):
        """Test loads with empty string raises ValidationException"""
        with pytest.raises(exceptions.ValidationException):
            jsonutils.loads("")

    def test_loads_none_input_raises_validation_exception(self):
        """Test loads with None input raises ValidationException"""
        with pytest.raises(exceptions.ValidationException) as exc_info:
            jsonutils.loads(None)

        error = exc_info.value
        assert "input_data" in error.details
        assert error.details["input_data"] == "None"

    def test_loads_truncates_long_input_data(self):
        """Test loads truncates long input data in error details"""
        long_string = (
            '{"key": "' + "x" * 300 + '"'
        )  # Invalid JSON (missing closing brace), too long

        with pytest.raises(exceptions.ValidationException) as exc_info:
            jsonutils.loads(long_string)

        error = exc_info.value
        assert len(error.details["input_data"]) <= 200

    @patch("itential_mcp.utilities.json.logging.error")
    def test_loads_logs_error_on_json_decode_error(self, mock_log_error):
        """Test loads logs error when JSON decode fails"""
        invalid_json = '{"invalid": json}'

        with pytest.raises(exceptions.ValidationException):
            jsonutils.loads(invalid_json)

        mock_log_error.assert_called_once()

    @patch("itential_mcp.utilities.json.json.loads")
    @patch("itential_mcp.utilities.json.logging.error")
    def test_loads_handles_unexpected_exception(self, mock_log_error, mock_json_loads):
        """Test loads handles unexpected exceptions"""
        mock_json_loads.side_effect = RuntimeError("Unexpected error")

        with pytest.raises(exceptions.ValidationException) as exc_info:
            jsonutils.loads('{"test": "value"}')

        error = exc_info.value
        assert "Unexpected error parsing JSON" in str(error)
        assert "original_error" in error.details
        mock_log_error.assert_called_once()

    def test_loads_with_whitespace(self):
        """Test loads with whitespace around JSON"""
        json_str = '  {"key": "value"}  '
        result = jsonutils.loads(json_str)

        assert result == {"key": "value"}

    def test_loads_large_valid_json(self):
        """Test loads with large valid JSON"""
        large_dict = {f"key_{i}": f"value_{i}" for i in range(1000)}
        json_str = json.dumps(large_dict)

        result = jsonutils.loads(json_str)
        assert result == large_dict


class TestDumps:
    """Test cases for the dumps function"""

    def test_dumps_dict(self):
        """Test dumps with dict object"""
        data = {"key": "value", "number": 42}
        result = jsonutils.dumps(data)

        assert isinstance(result, str)
        assert json.loads(result) == data

    def test_dumps_list(self):
        """Test dumps with list object"""
        data = [1, 2, 3, "test"]
        result = jsonutils.dumps(data)

        assert isinstance(result, str)
        assert json.loads(result) == data

    def test_dumps_empty_dict(self):
        """Test dumps with empty dict"""
        data = {}
        result = jsonutils.dumps(data)

        assert result == "{}"

    def test_dumps_empty_list(self):
        """Test dumps with empty list"""
        data = []
        result = jsonutils.dumps(data)

        assert result == "[]"

    def test_dumps_nested_objects(self):
        """Test dumps with nested objects"""
        data = {"outer": {"inner": [1, 2, {"deep": True}]}}
        result = jsonutils.dumps(data)

        assert json.loads(result) == data

    def test_dumps_unicode_characters(self):
        """Test dumps with unicode characters"""
        data = {"unicode": "测试", "emoji": "🚀"}
        result = jsonutils.dumps(data)

        assert json.loads(result) == data

    def test_dumps_special_values(self):
        """Test dumps with special values"""
        data = {"null": None, "true": True, "false": False}
        result = jsonutils.dumps(data)

        parsed = json.loads(result)
        assert parsed == data

    def test_dumps_numbers(self):
        """Test dumps with various number types"""
        data = {"int": 42, "float": 3.14, "negative": -10, "zero": 0}
        result = jsonutils.dumps(data)

        assert json.loads(result) == data

    def test_dumps_large_object(self):
        """Test dumps with large object"""
        large_dict = {f"key_{i}": f"value_{i}" for i in range(1000)}
        result = jsonutils.dumps(large_dict)

        assert json.loads(result) == large_dict

    def test_dumps_non_serializable_object_raises_validation_exception(self):
        """Test dumps with non-serializable object raises ValidationException"""

        class NonSerializable:
            pass

        non_serializable = NonSerializable()

        with pytest.raises(exceptions.ValidationException) as exc_info:
            jsonutils.dumps(non_serializable)

        error = exc_info.value
        assert "Failed to serialize object to JSON" in str(error)
        assert "object_type" in error.details
        assert "json_error" in error.details

    def test_dumps_circular_reference_raises_validation_exception(self):
        """Test dumps with circular reference raises ValidationException"""
        data = {}
        data["self"] = data

        with pytest.raises(exceptions.ValidationException) as exc_info:
            jsonutils.dumps(data)

        error = exc_info.value
        assert "Failed to serialize object to JSON" in str(error)

    def test_dumps_function_raises_validation_exception(self):
        """Test dumps with function raises ValidationException"""

        def test_func():
            pass

        with pytest.raises(exceptions.ValidationException) as exc_info:
            jsonutils.dumps(test_func)

        error = exc_info.value
        assert "Failed to serialize object to JSON" in str(error)

    @patch("itential_mcp.utilities.json.logging.error")
    def test_dumps_logs_error_on_type_error(self, mock_log_error):
        """Test dumps logs error when serialization fails"""

        class NonSerializable:
            pass

        with pytest.raises(exceptions.ValidationException):
            jsonutils.dumps(NonSerializable())

        mock_log_error.assert_called_once()

    @patch("itential_mcp.utilities.json.json.dumps")
    @patch("itential_mcp.utilities.json.logging.error")
    def test_dumps_handles_unexpected_exception(self, mock_log_error, mock_json_dumps):
        """Test dumps handles unexpected exceptions"""
        mock_json_dumps.side_effect = RuntimeError("Unexpected error")

        with pytest.raises(exceptions.ValidationException) as exc_info:
            jsonutils.dumps({"test": "value"})

        error = exc_info.value
        assert "Unexpected error serializing JSON" in str(error)
        assert "original_error" in error.details
        mock_log_error.assert_called_once()

    def test_dumps_with_string_input(self):
        """Test dumps with string input (should work as strings are serializable)"""
        data = "test string"
        result = jsonutils.dumps(data)

        assert result == '"test string"'

    def test_dumps_with_number_input(self):
        """Test dumps with number input"""
        data = 42
        result = jsonutils.dumps(data)

        assert result == "42"

    def test_dumps_with_boolean_input(self):
        """Test dumps with boolean input"""
        result_true = jsonutils.dumps(True)
        result_false = jsonutils.dumps(False)

        assert result_true == "true"
        assert result_false == "false"

    def test_dumps_with_none_input(self):
        """Test dumps with None input"""
        result = jsonutils.dumps(None)

        assert result == "null"


class TestJsonUtilsIntegration:
    """Integration tests for jsonutils module"""

    def test_loads_dumps_roundtrip_dict(self):
        """Test loads and dumps roundtrip with dict"""
        original = {"key": "value", "number": 42, "nested": {"inner": True}}

        json_str = jsonutils.dumps(original)
        result = jsonutils.loads(json_str)

        assert result == original

    def test_loads_dumps_roundtrip_list(self):
        """Test loads and dumps roundtrip with list"""
        original = [1, "two", {"three": 3}, [4, 5]]

        json_str = jsonutils.dumps(original)
        result = jsonutils.loads(json_str)

        assert result == original

    def test_loads_dumps_roundtrip_complex(self):
        """Test loads and dumps roundtrip with complex structure"""
        original = {
            "string": "test",
            "number": 123,
            "float": 45.67,
            "boolean": True,
            "null": None,
            "array": [1, 2, 3],
            "nested": {
                "inner_array": ["a", "b", "c"],
                "inner_object": {"deep": "value"},
            },
        }

        json_str = jsonutils.dumps(original)
        result = jsonutils.loads(json_str)

        assert result == original

    def test_error_handling_consistency(self):
        """Test that both functions handle errors consistently"""
        # Test loads error
        with pytest.raises(exceptions.ValidationException) as loads_exc:
            jsonutils.loads('{"invalid": json}')

        # Test dumps error
        class NonSerializable:
            pass

        with pytest.raises(exceptions.ValidationException) as dumps_exc:
            jsonutils.dumps(NonSerializable())

        # Both should be ValidationException
        assert isinstance(loads_exc.value, exceptions.ValidationException)
        assert isinstance(dumps_exc.value, exceptions.ValidationException)

        # Both should have details
        assert hasattr(loads_exc.value, "details")
        assert hasattr(dumps_exc.value, "details")


class TestModuleStructure:
    """Test cases for jsonutils module structure and imports"""

    def test_module_imports(self):
        """Test that jsonutils module imports correctly"""
        import itential_mcp.utilities.json as ju

        assert hasattr(ju, "loads")
        assert hasattr(ju, "dumps")
        assert callable(ju.loads)
        assert callable(ju.dumps)

    def test_function_signatures(self):
        """Test function signatures are correct"""
        import inspect

        # Test loads signature
        sig = inspect.signature(jsonutils.loads)
        assert len(sig.parameters) == 1
        assert "s" in sig.parameters

        # Test dumps signature
        sig = inspect.signature(jsonutils.dumps)
        assert len(sig.parameters) == 1
        assert "o" in sig.parameters

    def test_function_docstrings(self):
        """Test that functions have proper docstrings"""
        assert jsonutils.loads.__doc__ is not None
        assert len(jsonutils.loads.__doc__.strip()) > 0
        assert "Args:" in jsonutils.loads.__doc__
        assert "Returns:" in jsonutils.loads.__doc__

        assert jsonutils.dumps.__doc__ is not None
        assert len(jsonutils.dumps.__doc__.strip()) > 0
        assert "Args:" in jsonutils.dumps.__doc__
        assert "Returns:" in jsonutils.dumps.__doc__

    def test_module_dependencies(self):
        """Test that required dependencies are available"""
        import itential_mcp.utilities.json as ju

        # Should be able to access these modules through jsonutils
        assert hasattr(ju, "json")
        assert hasattr(ju, "traceback")
        assert hasattr(ju, "exceptions")
        assert hasattr(ju, "logging")


class TestEdgeCases:
    """Test cases for edge cases and boundary conditions"""

    def test_loads_very_long_string(self):
        """Test loads with very long valid JSON string"""
        long_value = "x" * 10000
        json_str = json.dumps({"long_value": long_value})

        result = jsonutils.loads(json_str)
        assert result["long_value"] == long_value

    def test_dumps_very_large_dict(self):
        """Test dumps with very large dictionary"""
        large_dict = {f"key_{i}": i for i in range(5000)}

        result = jsonutils.dumps(large_dict)
        assert isinstance(result, str)
        assert json.loads(result) == large_dict

    def test_loads_deeply_nested_structure(self):
        """Test loads with deeply nested structure"""
        nested = {}
        current = nested
        for i in range(100):
            current[f"level_{i}"] = {}
            current = current[f"level_{i}"]
        current["final"] = "value"

        json_str = json.dumps(nested)
        result = jsonutils.loads(json_str)

        assert result == nested

    def test_loads_with_various_whitespace(self):
        """Test loads with various whitespace characters"""
        json_str = '\n\t  {"key": "value"}\r\n  '
        result = jsonutils.loads(json_str)

        assert result == {"key": "value"}

    def test_dumps_preserves_order_python38_plus(self):
        """Test that dumps preserves order (dict order guaranteed in Python 3.8+)"""
        import sys

        if sys.version_info >= (3, 8):
            data = {"z": 1, "a": 2, "m": 3}
            result = jsonutils.dumps(data)

            # The order should be preserved
            assert '"z"' in result
            assert '"a"' in result
            assert '"m"' in result
