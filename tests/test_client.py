# Copyright (c) 2025 Itential, Inc
# GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)

import pytest
import httpx
from unittest.mock import AsyncMock, patch

from itential_mcp.client import PlatformClient
from itential_mcp.response import Response


@pytest.fixture
def mock_httpx_response():
    return httpx.Response(
        status_code=200,
        json={"result": "success"},
        request=httpx.Request("GET", "https://example.com")
    )


@pytest.fixture
def patched_platform_factory(mock_httpx_response):
    with patch("itential_mcp.client.ipsdk.platform_factory") as factory_mock:
        client_mock = AsyncMock()
        client_mock._send_request.return_value = mock_httpx_response
        factory_mock.return_value = client_mock
        yield factory_mock


@pytest.mark.asyncio
async def test_init_client(patched_platform_factory):
    client = PlatformClient()
    assert patched_platform_factory.called
    assert isinstance(client.client, AsyncMock)


@pytest.mark.asyncio
async def test_send_request(patched_platform_factory, mock_httpx_response):
    client = PlatformClient()
    response = await client.send_request("GET", "/test", params={"x": "1"}, json={"k": "v"})
    assert isinstance(response, Response)
    assert response.status_code == 200
    assert response.json() == {"result": "success"}


@pytest.mark.asyncio
async def test_get_method(patched_platform_factory, mock_httpx_response):
    client = PlatformClient()
    response = await client.get("/test", params={"a": "b"})
    assert isinstance(response, Response)
    assert response.status_code == 200


@pytest.mark.asyncio
async def test_post_method(patched_platform_factory, mock_httpx_response):
    client = PlatformClient()
    response = await client.post("/test", json={"data": 123})
    assert isinstance(response, Response)
    assert response.status_code == 200


@pytest.mark.asyncio
async def test_put_method(patched_platform_factory, mock_httpx_response):
    client = PlatformClient()
    response = await client.put("/test", json={"update": True})
    assert isinstance(response, Response)
    assert response.status_code == 200


@pytest.mark.asyncio
async def test_delete_method(patched_platform_factory, mock_httpx_response):
    client = PlatformClient()
    response = await client.delete("/test", params={"id": "1"})
    assert isinstance(response, Response)
    assert response.status_code == 200

