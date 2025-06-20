# Copyright (c) 2025 Itential, Inc
# GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)

import pytest
import time

from itential_mcp.cache import Cache


@pytest.fixture
def cache():
    c = Cache(cleanup_interval=1)
    yield c
    c.stop()


def test_put_get(cache):
    cache.put("foo", "bar")
    assert cache.get("foo") == "bar"


def test_get_nonexistent_key(cache):
    assert cache.get("missing") is None


def test_put_with_ttl(cache):
    cache.put("foo", "bar", ttl=1)
    time.sleep(1.5)
    assert cache.get("foo") is None


def test_delete_key(cache):
    cache.put("foo", "bar")
    cache.delete("foo")
    assert cache.get("foo") is None


def test_delete_nonexistent_key(cache):
    # Should not raise any exceptions
    assert cache.delete("ghost") is None


def test_keys_include_and_expired(cache):
    cache.put("foo", "bar", ttl=2)
    cache.put("baz", "qux")
    time.sleep(1)
    assert "foo" in cache.keys()
    assert "baz" in cache.keys()
    time.sleep(2)
    assert "foo" not in cache.keys()
    assert "baz" in cache.keys()


def test_clear(cache):
    cache.put("a", 1)
    cache.put("b", 2)
    cache.clear()
    assert cache.get("a") is None
    assert cache.get("b") is None
    assert cache.keys() == []


def test_stop_clears_cache():
    c = Cache(cleanup_interval=1)
    c.put("x", "y")
    c.stop()
    assert c.get("x") is None

