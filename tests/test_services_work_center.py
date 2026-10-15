# Copyright (c) 2025 Itential, Inc
# GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

import pytest
from unittest.mock import AsyncMock, MagicMock, patch

from ipsdk.platform import AsyncPlatform

from itential_mcp.platform.client import PlatformClient
from itential_mcp.platform.services import ServiceBase
from itential_mcp.platform.services.work_center import Service


class TestService:
    """Test the work_center Service class"""

    @pytest.fixture
    def mock_client(self):
        return AsyncMock(spec=AsyncPlatform)

    @pytest.fixture
    def service(self, mock_client):
        return Service(mock_client)

    def test_initialization(self, mock_client):
        service = Service(mock_client)
        assert service.client == mock_client
        assert service.name == "work_center"
        assert isinstance(service, ServiceBase)

    def test_service_is_discovered_by_client(self):
        """The platform client must load the service plugin (load failures are
        swallowed at DEBUG, so assert explicitly)."""
        with (
            patch("itential_mcp.platform.client.ipsdk.platform_factory"),
            patch("itential_mcp.platform.client.config.get") as config_get,
        ):
            config_get.return_value = MagicMock()
            client = PlatformClient()
        assert hasattr(client, "work_center")
        # Plugins are loaded by file path, so the class object differs.
        assert type(client.work_center).__name__ == "Service"
        assert callable(client.work_center.get_work_items)
        assert client.work_center.name == "work_center"

    @pytest.mark.asyncio
    async def test_get_work_items_returns_items(self, service, mock_client):
        res = MagicMock()
        res.json.return_value = {"items": [{"id": "a"}, {"id": "b"}]}
        mock_client.get.return_value = res

        result = await service.get_work_items("job-1")

        assert result == [{"id": "a"}, {"id": "b"}]
        mock_client.get.assert_called_once_with(
            "/work-center-service/work-items",
            params={"rootExecutionId": "job-1"},
        )

    @pytest.mark.asyncio
    async def test_get_work_items_missing_items_is_empty(self, service, mock_client):
        res = MagicMock()
        res.json.return_value = {}
        mock_client.get.return_value = res

        assert await service.get_work_items("job-1") == []

    @pytest.mark.asyncio
    async def test_get_work_items_propagates_errors(self, service, mock_client):
        mock_client.get.side_effect = RuntimeError("boom")

        with pytest.raises(RuntimeError):
            await service.get_work_items("job-1")

    @pytest.mark.asyncio
    async def test_get_work_item(self, service, mock_client):
        res = MagicMock()
        res.json.return_value = {"id": "wi-1"}
        mock_client.get.return_value = res

        assert await service.get_work_item("wi-1") == {"id": "wi-1"}
        mock_client.get.assert_called_once_with("/work-center-service/work-items/wi-1")

    @pytest.mark.asyncio
    async def test_get_work_item_incoming(self, service, mock_client):
        res = MagicMock()
        res.json.return_value = {"incoming": {"header": "h", "btn_success": "OK"}}
        mock_client.get.return_value = res

        result = await service.get_work_item_incoming("wi-1")

        assert result == {"header": "h", "btn_success": "OK"}
        mock_client.get.assert_called_once_with(
            "/work-center-service/work-items/wi-1/variables/incoming"
        )

    @pytest.mark.asyncio
    async def test_get_work_item_incoming_absent_is_empty(self, service, mock_client):
        res = MagicMock()
        res.json.return_value = {}
        mock_client.get.return_value = res

        assert await service.get_work_item_incoming("wi-1") == {}
