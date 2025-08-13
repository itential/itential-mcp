# Copyright (c) 2025 Itential, Inc
# GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)

import time
import asyncio

from typing import Any, Optional


class Cache(object):
    """
    The Cache class implements a basic, async-safe implementation of a
    key/value store that can be used to cache values.  Once instantiated,
    any value can be inserted into the store for later retrieval.
    """

    def __init__(self, cleanup_interval: int = 10):
        """
        Create a new instance of Cache

        This will create a new instance of Cache that can be used to store
        values based on a string key.  The values can later be retrieved.  It
        is the responsibility of the implementation to handle any data
        serialization for the value.

        This object supports a time-to-live value for all entries in the
        store.   It will start a background asyncio task that is responsible
        for iterating over values in the store and expiring them.   The
        clean up interval can be specified using the `cleanup_interval`
        argument.

        Args:
            cleanup_interval (int): The interval specified in seconds to run
                the key expiration process.  The default is 10 seconds.

        Returns:
            Cache: An instance of Cache

        Raises:
            None
        """
        self._store = {}
        self._cleanup_interval = cleanup_interval
        self._stop_event = asyncio.Event()
        self._cleanup_task: Optional[asyncio.Task] = None
        self._started = False

    async def start(self):
        """
        Start the background cleanup task

        This method must be called to start the background cleanup task.
        It should be called after the cache is instantiated and an event
        loop is available.

        Args:
            None

        Returns:
            None

        Raises:
            None
        """
        if not self._started:
            self._cleanup_task = asyncio.create_task(self._cleanup_expired_keys())
            self._started = True

    def put(self, key: str, value: Any, ttl: int | None = None):
        """
        Put a new key into the store

        This method will put a new key into the store.  The value can be
        any Python object.  It is the calling functions responsibility to
        handle any data serialization.

        Args:
            key (str): The key used to store and retrieve the value
            value (Any): The value to store with the key
            ttl (int): Time-to-live for the key.  When the TTL expires the
                key is purged from the store

        Returns:
            None

        Raises:
            None
        """
        expiry = time.time() + ttl if ttl else None
        self._store[key] = (value, expiry)

    def get(self, key: str) -> Any:
        """
        Get the value of `key` from the store

        This method will retrieve the value from the store based on the
        specified `key` argument.   If the key does not exist in the
        store or has expired, this method will return None.

        Args:
            key (str): The key to retrieve the value for

        Returns:
            Any: The value associated with the key.  If the key doesn't exist
                None is returned

        Raises:
            None
        """
        item = self._store.get(key)
        if not item:
            return None

        value, expiry = item
        if expiry and time.time() > expiry:
            del self._store[key]
            return None

        return value

    def delete(self, key: str):
        """
        Delete a key from the store

        This method will delete a previously inserted key from the store.
        If the specified key does not exist in the store, this method
        simply performs a noop

        Args:
            key (str): The key to delete from the store

        Returns:
            None

        Raises:
            None
        """
        return self._store.pop(key, None)

    def keys(self) -> list[str]:
        """
        Returns the list of keys from the store

        This method will return the list of keys that have been added to
        the store that have not expired.

        Args:
            None

        Returns:
            list[str]: A list that represents all keys in the store

        Raises:
            None
        """
        now = time.time()
        return [
            k for k, (v, expiry) in self._store.items()
            if not expiry or now <= expiry
        ]

    def clear(self):
        """
        Remove all entries from the store

        This method will delete all entries from the store regardless of
        the type of entry or TTL value.  After calling this method there
        will be no entries in the store  This is a destructive operation
        that cannot be undone once called.

        Args:
            None

        Returns:
            None

        Raises:
            None
        """
        self._store.clear()

    async def _cleanup_expired_keys(self):
        """
        Internal method that handles cleaning up expired keys using asyncio
        """
        while True:
            try:
                # Wait for stop event or timeout
                await asyncio.wait_for(
                    self._stop_event.wait(),
                    timeout=self._cleanup_interval
                )
                # If we get here, stop event was set
                break
            except asyncio.TimeoutError:
                # Timeout occurred, time to cleanup expired keys
                now = time.time()
                expired_keys = [
                    k for k, (v, expiry) in self._store.items()
                    if expiry and now > expiry
                ]
                for k in expired_keys:
                    del self._store[k]

    async def stop(self):
        """
        Stop the background cleanup task

        This method will gracefully stop the cache service.  It will
        signal the background task that handles content expiration to
        stop and waits for it to complete.  It will also clear out all
        entries from the store.

        Calling this method is required for proper cleanup when shutting
        down the service.

        Args:
            None

        Returns:
            None

        Raises:
            None
        """
        if self._started and self._cleanup_task:
            self._stop_event.set()
            try:
                await self._cleanup_task
            except asyncio.CancelledError:
                pass
            self._cleanup_task = None
            self._started = False
        self.clear()
