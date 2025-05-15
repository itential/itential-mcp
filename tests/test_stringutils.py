# Copyright (c) 2025 Itential, Inc
# GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)

import pytest

from itential_mcp.stringutils import tostr, tobytes, toint, tobool


class TestStringUtils:

    @pytest.mark.parametrize("input_val,expected", [
        ("hello", "hello"),
        (123, "123"),
        (None, None),
        (True, "True"),
    ])
    def test_tostr(self, input_val, expected):
        assert tostr(input_val) == (str(expected) if expected is not None else expected)

    @pytest.mark.parametrize("input_val,encoding,expected", [
        ("hello", "utf-8", b"hello"),
        ("¡hola!", "utf-8", b"\xc2\xa1hola!"),
        ("test", "ascii", b"test"),
    ])
    def test_tobytes(self, input_val, encoding, expected):
        assert tobytes(input_val, encoding) == expected

    def test_tobytes_invalid_type(self):
        with pytest.raises(AttributeError):
            tobytes(None)

    @pytest.mark.parametrize("input_val,expected", [
        ("42", 42),
        ("0", 0),
        ("-15", -15),
    ])
    def test_toint_valid(self, input_val, expected):
        assert toint(input_val) == expected

    @pytest.mark.parametrize("input_val", ["abc", "", None])
    def test_toint_invalid(self, input_val):
        with pytest.raises((ValueError, TypeError)):
            toint(input_val)

    @pytest.mark.parametrize("input_val,expected", [
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
    ])
    def test_tobool_string_inputs(self, input_val, expected):
        assert tobool(input_val) is expected

    def test_tobool_native_boolean(self):
        assert tobool(True) is True
        assert tobool(False) is False

