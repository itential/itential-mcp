# Copyright (c) 2025 Itential, Inc
# GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)

import pytest
import pytest_asyncio
import asyncio

from itential_mcp.cache import Cache


@pytest_asyncio.fixture
async def cache():
    """Async fixture that properly starts and stops the cache"""
    c = Cache(cleanup_interval=1)
    await c.start()
    yield c
    await c.stop()


@pytest.mark.asyncio
async def test_put_get(cache):
    cache.put("foo", "bar")
    assert cache.get("foo") == "bar"


@pytest.mark.asyncio
async def test_get_nonexistent_key(cache):
    assert cache.get("missing") is None


@pytest.mark.asyncio
async def test_put_with_ttl(cache):
    cache.put("foo", "bar", ttl=1)
    await asyncio.sleep(1.2)  # Use asyncio.sleep instead of time.sleep
    assert cache.get("foo") is None


@pytest.mark.asyncio
async def test_delete_key(cache):
    cache.put("foo", "bar")
    cache.delete("foo")
    assert cache.get("foo") is None


@pytest.mark.asyncio
async def test_delete_nonexistent_key(cache):
    # Should not raise any exceptions
    assert cache.delete("ghost") is None


@pytest.mark.asyncio
async def test_keys_include_and_expired(cache):
    cache.put("foo", "bar", ttl=2)
    cache.put("baz", "qux")
    await asyncio.sleep(1)
    assert "foo" in cache.keys()
    assert "baz" in cache.keys()
    await asyncio.sleep(1.2)  # Wait for expiration
    assert "foo" not in cache.keys()
    assert "baz" in cache.keys()


@pytest.mark.asyncio
async def test_clear(cache):
    cache.put("a", 1)
    cache.put("b", 2)
    cache.clear()
    assert cache.get("a") is None
    assert cache.get("b") is None
    assert cache.keys() == []


@pytest.mark.asyncio
async def test_stop_clears_cache():
    """Test that stop properly clears the cache"""
    c = Cache(cleanup_interval=1)
    await c.start()
    c.put("x", "y")
    await c.stop()
    assert c.get("x") is None


@pytest.mark.asyncio
async def test_cache_without_start():
    """Test that cache works without starting (no background cleanup)"""
    c = Cache(cleanup_interval=1)
    c.put("test", "value")
    assert c.get("test") == "value"
    # No need to call stop since we never started


@pytest.mark.asyncio
async def test_background_cleanup():
    """Test that background cleanup actually removes expired keys"""
    c = Cache(cleanup_interval=0.5)  # Short interval for testing
    await c.start()
    
    # Add a key with short TTL
    c.put("expire_me", "value", ttl=1)
    
    # Verify it exists initially
    assert c.get("expire_me") == "value"
    
    # Wait for cleanup to run (should happen after 1.5 seconds total)
    await asyncio.sleep(1.6)
    
    # Key should be removed by background cleanup
    # (even if we don't access it via get())
    assert "expire_me" not in c._store
    
    await c.stop()


@pytest.mark.asyncio
async def test_multiple_start_stop():
    """Test that starting and stopping multiple times works correctly"""
    c = Cache(cleanup_interval=1)
    
    # Start, stop, start again
    await c.start()
    await c.stop()
    await c.start()
    
    c.put("test", "value")
    assert c.get("test") == "value"
    
    await c.stop()


@pytest.mark.asyncio
async def test_concurrent_access():
    """Test concurrent access to cache methods"""
    c = Cache(cleanup_interval=1)
    await c.start()
    
    # Define operations to run concurrently
    async def put_operation(key, value):
        c.put(f"key_{key}", f"value_{value}")
    
    async def get_operation(key):
        return c.get(f"key_{key}")
    
    # Run multiple put operations concurrently
    await asyncio.gather(*[put_operation(i, i) for i in range(10)])
    
    # Run multiple get operations concurrently
    results = await asyncio.gather(*[get_operation(i) for i in range(10)])
    
    # Verify all operations completed correctly
    expected = [f"value_{i}" for i in range(10)]
    assert results == expected
    
    await c.stop()

