# Copyright (c) 2025 Itential, Inc
# GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from typing import Any

from ipsdk.platform import AsyncPlatform


class ServiceBase:
    """Abstract base class for Itential Platform service implementations.

    ServiceBase provides a common interface and foundation for all service
    classes that interact with the Itential Platform. Services are responsible
    for encapsulating specific API operations and providing a clean interface
    for tool implementations to consume platform resources.

    This base class provides common utilities such as pagination helpers that
    reduce code duplication across service implementations.

    Args:
        client: An AsyncPlatform client instance for communicating with
            the Itential Platform API

    Attributes:
        client (AsyncPlatform): The platform client used for API communication
    """

    __slots__ = ("client",)

    def __init__(self, client: AsyncPlatform):
        self.client = client

    async def _paginate(
        self,
        endpoint: str,
        *,
        params: dict[str, Any] | None = None,
        limit: int = 100,
        data_key: str = "results",
        total_key: str = "total",
        metadata_key: str | None = None,
    ) -> list[dict[str, Any]]:
        """Generic pagination helper for API endpoints.

        This helper method handles paginated retrieval from Itential Platform APIs
        by making sequential requests with skip/limit parameters until all results
        are retrieved. It supports different response formats through configurable
        keys for data extraction.

        Args:
            endpoint: API endpoint path to paginate (e.g., "/api/resources")
            params: Optional query parameters to include in requests. The method
                will automatically add 'limit' and 'skip' parameters. Defaults to None.
            limit: Page size for each request (default: 100). Higher values reduce
                the number of API calls but may impact response time.
            data_key: Key in response containing data items (default: "results").
                Common values: "results", "data", "items", "list"
            total_key: Key for total count in response (default: "total").
                Used to determine when pagination is complete.
            metadata_key: Optional parent key for total count (default: None).
                When provided, total is extracted from response[metadata_key][total_key].
                Common values: "metadata", "meta"

        Returns:
            list[dict[str, Any]]: Complete list of all paginated results combined
                from all API requests

        Example:
            # Simple pagination with defaults
            results = await self._paginate("/api/resources")

            # With parameters and custom keys
            results = await self._paginate(
                "/api/resources",
                params={"filter": "active"},
                data_key="data",
                total_key="total",
                metadata_key="metadata"
            )

            # For POST-based pagination
            # (Note: This method uses GET; services should override for POST)
        """
        skip = 0
        params = params or {}
        params["limit"] = limit
        results = []

        while True:
            params["skip"] = skip

            res = await self.client.get(endpoint, params=params)
            data = res.json()

            # Extract items from response
            items = data.get(data_key, [])
            results.extend(items)

            # Extract total count (handle nested keys)
            if metadata_key:
                total = data.get(metadata_key, {}).get(total_key, 0)
            else:
                total = data.get(total_key, 0)

            if len(results) >= total:
                break

            skip += limit

        return results
