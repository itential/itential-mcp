# Copyright (c) 2025 Itential, Inc
# GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)

import time
import threading

from typing import Any


class Cache(object):
    """
    The Cache class implements a basic, thread safe implementation of a
    key/value store that can be used to cache values.  One instantiated,
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
        store.   It will start a background thread that is responsible
        for iterating over values in the store and expiring them.   The
        clean up interval can be specified using the `cleanup_interval`
        argument.

        Args:
            cleanup_interval (int): The internal specified in seconds to run
                the key expiration process.  The default is 10 seconds.

        Returns:
            Cache: An instance of Cache

        Raises:
            None
        """
        self._store = {}
        self._lock = threading.Lock()
        self._cleanup_interval = cleanup_interval
        self._stop_event = threading.Event()
        self._thread = threading.Thread(target=self._cleanup_expired_keys, daemon=True)
        self._thread.start()

    def put(self, key: str, value: Any, ttl: int | None = None):
        """
        Put a new key into the store

        This method will put a new key into the store.  The value can be
        any Python object.  It is the calling functions responsibity to
        handle any data serialization.

        Args:
            key (str): The key used to store and retreive the value
            value (Any): The value to store with the key
            ttl (int): Time-to-live for the key.  When the TTL expires the
                key is pruged from the store

        Returns:
            None

        Raises:
            None
        """
        expiry = time.time() + ttl if ttl else None
        with self._lock:
            self._store[key] = (value, expiry)

    def get(self, key: str) -> Any:
        """
        Get the value of `key` from the store

        This method will retreive the value from the store based on the
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
        with self._lock:
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
        simply performs a nooop

        Args:
            key (str): The key to delete from the store

        Returns:
            None

        Raises:
            None
        """
        with self._lock:
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
        with self._lock:
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
        with self._lock:
            self._store.clear()

    def _cleanup_expired_keys(self):
        """
        Internal method that handles cleaning up expired keys
        """
        while not self._stop_event.is_set():
            time.sleep(self._cleanup_interval)
            now = time.time()
            with self._lock:
                expired_keys = [k for k, (v, expiry) in self._store.items() if expiry and now > expiry]
                for k in expired_keys:
                    del self._store[k]

    def stop(self):
        """
        Stop the background cleanup thread

        This method will gracefully stop the store service.  It will
        connect to the background thread that handles content
        expiration and stops the thread from running.  It will also
        clear out all entries from the store

        Calling this method is optional and not required for shutting
        down the service.

        Args:
            None

        Returns:
            None

        Raises:
            None
        """
        self._stop_event.set()
        self._thread.join()
        self.clear()
