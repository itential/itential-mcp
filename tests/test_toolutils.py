# Copyright (c) 2025 Itential, Inc
# GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)

from itential_mcp.toolutils import tags

def test_tags_decorator_single():
    @tags("public")
    def my_func():
        return "hello"

    assert hasattr(my_func, "tags")
    assert my_func.tags == ["public"]

def test_tags_decorator_multiple():
    @tags("system", "admin", "beta")
    def another_func():
        return 42

    assert hasattr(another_func, "tags")
    assert set(another_func.tags) == {"system", "admin", "beta"}

def test_tags_does_not_modify_function_behavior():
    @tags("alpha")
    def simple_func(x):
        return x * 2

    assert simple_func(4) == 8
    assert simple_func.tags == ["alpha"]

def test_tags_empty():
    @tags()
    def no_tags_func():
        return "none"

    assert hasattr(no_tags_func, "tags")
    assert no_tags_func.tags == []
