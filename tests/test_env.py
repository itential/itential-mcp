# Copyright (c) 2025 Itential, Inc
# GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)

import os
import pytest

from itential_mcp.env import get, getstr, getint, getbool


class TestEnv:

    def test_get_with_existing_key(self):
        os.environ["TEST_KEY"] = "123"
        assert get(int, "TEST_KEY", default="0") == 123

    def test_get_with_missing_key_returns_default(self):
        if "MISSING_KEY" in os.environ:
            del os.environ["MISSING_KEY"]
        assert get(str, "MISSING_KEY", default="default") == "default"

    def test_getstr_returns_string(self):
        os.environ["STR_KEY"] = "abc"
        assert getstr("STR_KEY") == "abc"

    def test_getstr_returns_default(self):
        if "MISSING_STR" in os.environ:
            del os.environ["MISSING_STR"]
        assert getstr("MISSING_STR", default="default") == "default"

    def test_getint_valid(self):
        os.environ["INT_KEY"] = "42"
        assert getint("INT_KEY") == 42

    def test_getint_invalid_raises(self):
        os.environ["INT_KEY_INVALID"] = "not_a_number"
        with pytest.raises(ValueError):
            getint("INT_KEY_INVALID")

    def test_getint_default(self):
        if "MISSING_INT" in os.environ:
            del os.environ["MISSING_INT"]
        assert getint("MISSING_INT", default="5") == 5

    @pytest.mark.parametrize("value,expected", [
        ("true", True),
        ("1", True),
        ("yes", True),
        ("on", True),
        ("false", False),
        ("0", False),
        ("off", False),
        ("", False),
        (None, False),
    ])
    def test_getbool_various_inputs(self, value, expected):
        os.environ["BOOL_KEY"] = value if value is not None else ""
        assert getbool("BOOL_KEY") is expected

    def test_getbool_with_missing_key(self):
        if "MISSING_BOOL" in os.environ:
            del os.environ["MISSING_BOOL"]
        assert getbool("MISSING_BOOL", default="true") is True

