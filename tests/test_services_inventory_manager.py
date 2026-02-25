# Copyright (c) 2025 Itential, Inc
# GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

import pytest
from unittest.mock import AsyncMock, Mock

import ipsdk

from itential_mcp.core import exceptions
from itential_mcp.platform.services.inventory_manager import Service
from itential_mcp.platform.services import ServiceBase


class TestInventoryManagerService:
    """
    Comprehensive test cases for Inventory Manager Service class.

    This test class covers all core functionality of the Inventory Manager
    service, including inventory CRUD operations, service inheritance,
    client configuration, and method validation.
    """

    @pytest.fixture
    def mock_client(self):
        """
        Create a mock AsyncPlatform client for Inventory Manager tests.

        Returns:
            AsyncMock: Mocked ipsdk.platform.AsyncPlatform instance configured
                      with proper specifications for testing Inventory Manager
                      API interactions including GET, POST, DELETE operations.
        """
        return AsyncMock(spec=ipsdk.platform.AsyncPlatform)

    @pytest.fixture
    def service(self, mock_client):
        """
        Create an Inventory Manager Service instance for testing.

        Args:
            mock_client: Mocked AsyncPlatform client fixture.

        Returns:
            Service: Inventory Manager service instance configured with
                    the mocked client for testing all service operations.
        """
        return Service(mock_client)

    def test_service_inheritance(self, service):
        """Test that Inventory Manager Service inherits from ServiceBase correctly."""
        assert isinstance(service, ServiceBase)
        assert isinstance(service, Service)

    def test_service_name(self, service):
        """Test that service has the correct identifier name."""
        assert service.name == "inventory_manager"

    def test_service_client_assignment(self, mock_client, service):
        """Test that the HTTP client is properly assigned to the service instance."""
        assert service.client is mock_client

    def test_service_methods_exist(self, service):
        """Test that all required methods exist on the service."""
        assert hasattr(service, "get_inventories")
        assert hasattr(service, "describe_inventory")
        assert hasattr(service, "create_inventory")
        assert hasattr(service, "add_nodes_to_inventory")
        assert hasattr(service, "delete_inventory")

    def test_service_methods_are_async(self, service):
        """Test that all service methods are async."""
        import asyncio

        assert asyncio.iscoroutinefunction(service.get_inventories)
        assert asyncio.iscoroutinefunction(service.describe_inventory)
        assert asyncio.iscoroutinefunction(service.create_inventory)
        assert asyncio.iscoroutinefunction(service.add_nodes_to_inventory)
        assert asyncio.iscoroutinefunction(service.delete_inventory)

    # =========================================================================
    # get_inventories tests
    # =========================================================================

    @pytest.mark.asyncio
    async def test_get_inventories_success(self, service, mock_client):
        """Test successful retrieval of inventories from the platform."""
        expected_data = [
            {
                "_id": "inv-1",
                "name": "Production Inventory",
                "description": "Production devices",
                "nodeCount": 10,
            },
            {
                "_id": "inv-2",
                "name": "Test Inventory",
                "description": "Test devices",
                "nodeCount": 3,
            },
        ]

        mock_response = Mock()
        mock_response.json.return_value = {"result": {"data": expected_data}}
        mock_client.get.return_value = mock_response

        result = await service.get_inventories()

        mock_client.get.assert_called_once_with("/inventory_manager/v1/inventories")
        assert result == expected_data

    @pytest.mark.asyncio
    async def test_get_inventories_empty_response(self, service, mock_client):
        """Test get_inventories with empty response."""
        mock_response = Mock()
        mock_response.json.return_value = {"result": {"data": []}}
        mock_client.get.return_value = mock_response

        result = await service.get_inventories()

        mock_client.get.assert_called_once_with("/inventory_manager/v1/inventories")
        assert result == []

    # =========================================================================
    # describe_inventory tests
    # =========================================================================

    @pytest.mark.asyncio
    async def test_describe_inventory_success(self, service, mock_client):
        """Test successful retrieval of a specific inventory by name."""
        # Mock get_inventories response
        inventories_data = [
            {"_id": "inv-1", "name": "Target Inventory", "nodeCount": 5},
            {"_id": "inv-2", "name": "Other Inventory", "nodeCount": 2},
        ]

        inventory_detail = {
            "_id": "inv-1",
            "name": "Target Inventory",
            "description": "Detailed inventory info",
            "groups": ["Solutions Engineering"],
            "actions": [],
            "tags": ["production"],
        }

        nodes_data = [
            {
                "name": "core-router-1",
                "attributes": {
                    "itential_host": "10.1.1.1",
                    "itential_platform": "iosxr",
                    "cluster_id": "cluster_east",
                },
                "tags": ["core", "datacenter-1"],
            },
            {
                "name": "core-router-2",
                "attributes": {
                    "itential_host": "10.1.1.2",
                    "itential_platform": "iosxr",
                    "cluster_id": "cluster_east",
                },
                "tags": ["core", "datacenter-1"],
            },
        ]

        # First call returns inventories list, second returns inventory detail,
        # third returns nodes for the inventory
        mock_list_response = Mock()
        mock_list_response.json.return_value = {"result": {"data": inventories_data}}

        mock_detail_response = Mock()
        mock_detail_response.json.return_value = {"result": inventory_detail}

        mock_nodes_response = Mock()
        mock_nodes_response.json.return_value = {"result": {"data": nodes_data}}

        mock_client.get.side_effect = [
            mock_list_response,
            mock_detail_response,
            mock_nodes_response,
        ]

        result = await service.describe_inventory("Target Inventory")

        assert result["_id"] == "inv-1"
        assert result["name"] == "Target Inventory"
        assert result["groups"] == ["Solutions Engineering"]
        assert result["tags"] == ["production"]
        assert len(result["nodes"]) == 2
        assert result["nodes"][0]["name"] == "core-router-1"
        assert result["nodes"][0]["attributes"]["itential_host"] == "10.1.1.1"
        assert result["nodes"][1]["name"] == "core-router-2"

        assert mock_client.get.call_count == 3
        mock_client.get.assert_any_call("/inventory_manager/v1/inventories")
        mock_client.get.assert_any_call("/inventory_manager/v1/inventories/inv-1")
        mock_client.get.assert_any_call(
            "/inventory_manager/v1/inventories/Target Inventory/nodes"
        )

    @pytest.mark.asyncio
    async def test_describe_inventory_empty_nodes(self, service, mock_client):
        """Test describe_inventory when inventory has no nodes."""
        inventories_data = [
            {"_id": "inv-1", "name": "Empty Inventory", "nodeCount": 0},
        ]

        inventory_detail = {
            "_id": "inv-1",
            "name": "Empty Inventory",
            "description": "No devices yet",
            "groups": ["admin"],
            "actions": [],
            "tags": [],
        }

        mock_list_response = Mock()
        mock_list_response.json.return_value = {"result": {"data": inventories_data}}

        mock_detail_response = Mock()
        mock_detail_response.json.return_value = {"result": inventory_detail}

        mock_nodes_response = Mock()
        mock_nodes_response.json.return_value = {"result": {"data": []}}

        mock_client.get.side_effect = [
            mock_list_response,
            mock_detail_response,
            mock_nodes_response,
        ]

        result = await service.describe_inventory("Empty Inventory")

        assert result["nodes"] == []

    @pytest.mark.asyncio
    async def test_describe_inventory_not_found(self, service, mock_client):
        """Test describe_inventory raises NotFoundError for non-existent inventory."""
        inventories_data = [
            {"_id": "inv-1", "name": "Existing Inventory", "nodeCount": 5},
        ]

        mock_response = Mock()
        mock_response.json.return_value = {"result": {"data": inventories_data}}
        mock_client.get.return_value = mock_response

        with pytest.raises(
            exceptions.NotFoundError, match="inventory 'NonExistent' not found"
        ):
            await service.describe_inventory("NonExistent")

    @pytest.mark.asyncio
    async def test_describe_inventory_empty_inventories(self, service, mock_client):
        """Test describe_inventory when no inventories exist."""
        mock_response = Mock()
        mock_response.json.return_value = {"result": {"data": []}}
        mock_client.get.return_value = mock_response

        with pytest.raises(
            exceptions.NotFoundError, match="inventory 'Any Name' not found"
        ):
            await service.describe_inventory("Any Name")

    @pytest.mark.asyncio
    async def test_describe_inventory_case_sensitive(self, service, mock_client):
        """Test describe_inventory is case sensitive."""
        inventories_data = [
            {"_id": "inv-1", "name": "Production", "nodeCount": 5},
        ]

        mock_response = Mock()
        mock_response.json.return_value = {"result": {"data": inventories_data}}
        mock_client.get.return_value = mock_response

        with pytest.raises(exceptions.NotFoundError):
            await service.describe_inventory("production")

    # =========================================================================
    # create_inventory tests
    # =========================================================================

    @pytest.mark.asyncio
    async def test_create_inventory_success(self, service, mock_client):
        """Test successful creation of an inventory."""
        # Mock get_inventories (empty - no duplicates)
        mock_list_response = Mock()
        mock_list_response.json.return_value = {"result": {"data": []}}

        # Mock create response
        mock_create_response = Mock()
        mock_create_response.json.return_value = {
            "status": "Success",
            "result": {"_id": "new-inv-123", "name": "New Inventory"},
            "message": "Inventory created successfully",
        }

        mock_client.get.return_value = mock_list_response
        mock_client.post.return_value = mock_create_response

        result = await service.create_inventory(
            "New Inventory",
            ["Solutions Engineering"],
            description="A new inventory",
            devices=["router1", "router2"],
        )

        assert result["_id"] == "new-inv-123"
        assert result["name"] == "New Inventory"
        assert result["message"] == "Inventory created successfully"

        mock_client.post.assert_called_once_with(
            "/inventory_manager/v1/inventories",
            json={
                "name": "New Inventory",
                "groups": ["Solutions Engineering"],
                "description": "A new inventory",
                "devices": [{"name": "router1"}, {"name": "router2"}],
            },
        )

    @pytest.mark.asyncio
    async def test_create_inventory_minimal(self, service, mock_client):
        """Test creating an inventory with minimal parameters."""
        mock_list_response = Mock()
        mock_list_response.json.return_value = {"result": {"data": []}}

        mock_create_response = Mock()
        mock_create_response.json.return_value = {
            "result": {"_id": "minimal-inv", "name": "Minimal"},
            "message": "Created",
        }

        mock_client.get.return_value = mock_list_response
        mock_client.post.return_value = mock_create_response

        result = await service.create_inventory("Minimal", ["admin"])

        assert result["_id"] == "minimal-inv"

        mock_client.post.assert_called_once_with(
            "/inventory_manager/v1/inventories",
            json={"name": "Minimal", "groups": ["admin"]},
        )

    @pytest.mark.asyncio
    async def test_create_inventory_with_description_only(self, service, mock_client):
        """Test creating an inventory with description but no devices."""
        mock_list_response = Mock()
        mock_list_response.json.return_value = {"result": {"data": []}}

        mock_create_response = Mock()
        mock_create_response.json.return_value = {
            "result": {"_id": "desc-inv", "name": "With Description"},
        }

        mock_client.get.return_value = mock_list_response
        mock_client.post.return_value = mock_create_response

        await service.create_inventory(
            "With Description",
            ["Solutions Engineering"],
            description="Has a description",
        )

        mock_client.post.assert_called_once_with(
            "/inventory_manager/v1/inventories",
            json={
                "name": "With Description",
                "groups": ["Solutions Engineering"],
                "description": "Has a description",
            },
        )

    @pytest.mark.asyncio
    async def test_create_inventory_with_devices_only(self, service, mock_client):
        """Test creating an inventory with devices but no description."""
        mock_list_response = Mock()
        mock_list_response.json.return_value = {"result": {"data": []}}

        mock_create_response = Mock()
        mock_create_response.json.return_value = {
            "result": {"_id": "dev-inv", "name": "With Devices"},
        }

        mock_client.get.return_value = mock_list_response
        mock_client.post.return_value = mock_create_response

        await service.create_inventory(
            "With Devices",
            ["admin"],
            devices=["device1"],
        )

        mock_client.post.assert_called_once_with(
            "/inventory_manager/v1/inventories",
            json={
                "name": "With Devices",
                "groups": ["admin"],
                "devices": [{"name": "device1"}],
            },
        )

    @pytest.mark.asyncio
    async def test_create_inventory_duplicate_name_error(self, service, mock_client):
        """Test create_inventory raises ValueError for duplicate name."""
        inventories_data = [
            {"_id": "existing-inv", "name": "Existing Inventory", "nodeCount": 5},
        ]

        mock_response = Mock()
        mock_response.json.return_value = {"result": {"data": inventories_data}}
        mock_client.get.return_value = mock_response

        with pytest.raises(
            ValueError, match="inventory 'Existing Inventory' already exists"
        ):
            await service.create_inventory(
                "Existing Inventory", ["Solutions Engineering"]
            )

        # Verify POST was never called
        mock_client.post.assert_not_called()

    @pytest.mark.asyncio
    async def test_create_inventory_message_merge(self, service, mock_client):
        """Test that message from outer response is merged into result."""
        mock_list_response = Mock()
        mock_list_response.json.return_value = {"result": {"data": []}}

        # Simulate API where message is at outer level, not in result
        mock_create_response = Mock()
        mock_create_response.json.return_value = {
            "result": {"_id": "msg-inv", "name": "Message Test"},
            "message": "Outer message",
        }

        mock_client.get.return_value = mock_list_response
        mock_client.post.return_value = mock_create_response

        result = await service.create_inventory("Message Test", ["admin"])

        assert result["message"] == "Outer message"

    @pytest.mark.asyncio
    async def test_create_inventory_message_not_overwritten(self, service, mock_client):
        """Test that existing message in result is not overwritten by outer message."""
        mock_list_response = Mock()
        mock_list_response.json.return_value = {"result": {"data": []}}

        mock_create_response = Mock()
        mock_create_response.json.return_value = {
            "result": {
                "_id": "msg-inv",
                "name": "Message Test",
                "message": "Inner message",
            },
            "message": "Outer message",
        }

        mock_client.get.return_value = mock_list_response
        mock_client.post.return_value = mock_create_response

        result = await service.create_inventory("Message Test", ["admin"])

        # Inner message should be preserved
        assert result["message"] == "Inner message"

    @pytest.mark.asyncio
    async def test_create_inventory_devices_format(self, service, mock_client):
        """Test that devices are formatted as list of dicts with name key."""
        mock_list_response = Mock()
        mock_list_response.json.return_value = {"result": {"data": []}}

        mock_create_response = Mock()
        mock_create_response.json.return_value = {
            "result": {"_id": "fmt-inv", "name": "Format Test"},
        }

        mock_client.get.return_value = mock_list_response
        mock_client.post.return_value = mock_create_response

        await service.create_inventory(
            "Format Test",
            ["admin"],
            devices=["router1", "switch1", "firewall1"],
        )

        call_args = mock_client.post.call_args
        body = call_args[1]["json"]
        assert body["devices"] == [
            {"name": "router1"},
            {"name": "switch1"},
            {"name": "firewall1"},
        ]

    # =========================================================================
    # add_nodes_to_inventory tests
    # =========================================================================

    @pytest.mark.asyncio
    async def test_add_nodes_to_inventory_success(self, service, mock_client):
        """Test successful bulk addition of nodes to an inventory."""
        inventories_data = [
            {"_id": "inv-1", "name": "prod-routers", "nodeCount": 0},
        ]

        sample_nodes = [
            {
                "name": "core-router-1",
                "attributes": {
                    "itential_host": "10.1.1.1",
                    "itential_platform": "iosxr",
                    "cluster_id": "cluster_east",
                    "itential_user": "$SECRET.network_devices.username",
                    "itential_password": "$SECRET.network_devices.password",
                },
                "tags": ["core", "datacenter-1"],
            },
            {
                "name": "core-router-2",
                "attributes": {
                    "itential_host": "10.1.1.2",
                    "itential_platform": "iosxr",
                    "cluster_id": "cluster_east",
                    "itential_user": "$SECRET.network_devices.username",
                    "itential_password": "$SECRET.network_devices.password",
                },
                "tags": ["core", "datacenter-1"],
            },
        ]

        mock_list_response = Mock()
        mock_list_response.json.return_value = {"result": {"data": inventories_data}}

        mock_add_response = Mock()
        mock_add_response.json.return_value = {
            "status": "Success",
            "result": {},
            "message": "2 nodes added to inventory",
        }

        mock_client.get.return_value = mock_list_response
        mock_client.post.return_value = mock_add_response

        result = await service.add_nodes_to_inventory("prod-routers", sample_nodes)

        assert result["status"] == "Success"
        assert result["message"] == "2 nodes added to inventory"

        mock_client.post.assert_called_once_with(
            "/inventory_manager/v1/nodes/bulk",
            json={
                "inventory_identifier": "prod-routers",
                "nodes": sample_nodes,
            },
        )

    @pytest.mark.asyncio
    async def test_add_nodes_to_inventory_without_tags(self, service, mock_client):
        """Test adding nodes without optional tags field."""
        inventories_data = [
            {"_id": "inv-1", "name": "edge-switches", "nodeCount": 0},
        ]

        nodes_without_tags = [
            {
                "name": "edge-switch-1",
                "attributes": {
                    "itential_host": "10.2.1.1",
                    "itential_platform": "nxos",
                    "cluster_id": "cluster_west",
                },
            },
        ]

        mock_list_response = Mock()
        mock_list_response.json.return_value = {"result": {"data": inventories_data}}

        mock_add_response = Mock()
        mock_add_response.json.return_value = {
            "status": "Success",
            "result": {},
            "message": "1 node added to inventory",
        }

        mock_client.get.return_value = mock_list_response
        mock_client.post.return_value = mock_add_response

        result = await service.add_nodes_to_inventory(
            "edge-switches", nodes_without_tags
        )

        assert result["status"] == "Success"

        # Verify nodes are passed as-is (without tags)
        call_args = mock_client.post.call_args
        body = call_args[1]["json"]
        assert body["nodes"] == nodes_without_tags
        assert "tags" not in body["nodes"][0]

    @pytest.mark.asyncio
    async def test_add_nodes_to_inventory_not_found(self, service, mock_client):
        """Test add_nodes_to_inventory raises NotFoundError for non-existent inventory."""
        inventories_data = [
            {"_id": "inv-1", "name": "Existing", "nodeCount": 5},
        ]

        mock_response = Mock()
        mock_response.json.return_value = {"result": {"data": inventories_data}}
        mock_client.get.return_value = mock_response

        with pytest.raises(
            exceptions.NotFoundError, match="inventory 'NonExistent' not found"
        ):
            await service.add_nodes_to_inventory(
                "NonExistent",
                [{"name": "node1", "attributes": {"itential_host": "1.1.1.1"}}],
            )

        # Verify POST was never called
        mock_client.post.assert_not_called()

    @pytest.mark.asyncio
    async def test_add_nodes_to_inventory_empty_inventories(self, service, mock_client):
        """Test add_nodes_to_inventory when no inventories exist."""
        mock_response = Mock()
        mock_response.json.return_value = {"result": {"data": []}}
        mock_client.get.return_value = mock_response

        with pytest.raises(exceptions.NotFoundError):
            await service.add_nodes_to_inventory(
                "Any Name",
                [{"name": "node1", "attributes": {"itential_host": "1.1.1.1"}}],
            )

    @pytest.mark.asyncio
    async def test_add_nodes_to_inventory_case_sensitive(self, service, mock_client):
        """Test add_nodes_to_inventory is case sensitive."""
        inventories_data = [
            {"_id": "inv-1", "name": "Production", "nodeCount": 5},
        ]

        mock_response = Mock()
        mock_response.json.return_value = {"result": {"data": inventories_data}}
        mock_client.get.return_value = mock_response

        with pytest.raises(exceptions.NotFoundError):
            await service.add_nodes_to_inventory(
                "production",
                [{"name": "node1", "attributes": {"itential_host": "1.1.1.1"}}],
            )

    @pytest.mark.asyncio
    async def test_add_nodes_to_inventory_status_merge(self, service, mock_client):
        """Test that status from outer response is merged into result."""
        inventories_data = [
            {"_id": "inv-1", "name": "Target", "nodeCount": 5},
        ]

        mock_list_response = Mock()
        mock_list_response.json.return_value = {"result": {"data": inventories_data}}

        # Simulate API where status is at outer level, not in result
        mock_add_response = Mock()
        mock_add_response.json.return_value = {
            "status": "Success",
            "result": {},
            "message": "Nodes added",
        }

        mock_client.get.return_value = mock_list_response
        mock_client.post.return_value = mock_add_response

        result = await service.add_nodes_to_inventory(
            "Target",
            [{"name": "node1", "attributes": {"itential_host": "1.1.1.1"}}],
        )

        assert result["status"] == "Success"
        assert result["message"] == "Nodes added"

    @pytest.mark.asyncio
    async def test_add_nodes_to_inventory_status_not_overwritten(
        self, service, mock_client
    ):
        """Test that existing status in result is not overwritten by outer status."""
        inventories_data = [
            {"_id": "inv-1", "name": "Target", "nodeCount": 5},
        ]

        mock_list_response = Mock()
        mock_list_response.json.return_value = {"result": {"data": inventories_data}}

        mock_add_response = Mock()
        mock_add_response.json.return_value = {
            "status": "Outer Status",
            "result": {"status": "Inner Status"},
            "message": "Outer message",
        }

        mock_client.get.return_value = mock_list_response
        mock_client.post.return_value = mock_add_response

        result = await service.add_nodes_to_inventory(
            "Target",
            [{"name": "node1", "attributes": {"itential_host": "1.1.1.1"}}],
        )

        # Inner status should be preserved
        assert result["status"] == "Inner Status"

    @pytest.mark.asyncio
    async def test_add_nodes_to_inventory_request_body_structure(
        self, service, mock_client
    ):
        """Test that the request body uses inventory_identifier and nodes fields."""
        inventories_data = [
            {"_id": "inv-1", "name": "prod-routers", "nodeCount": 0},
        ]

        nodes = [
            {
                "name": "core-router-1",
                "attributes": {
                    "itential_host": "10.1.1.1",
                    "itential_platform": "iosxr",
                    "cluster_id": "cluster_east",
                },
                "tags": ["core"],
            },
        ]

        mock_list_response = Mock()
        mock_list_response.json.return_value = {"result": {"data": inventories_data}}

        mock_add_response = Mock()
        mock_add_response.json.return_value = {"result": {}}

        mock_client.get.return_value = mock_list_response
        mock_client.post.return_value = mock_add_response

        await service.add_nodes_to_inventory("prod-routers", nodes)

        call_args = mock_client.post.call_args
        body = call_args[1]["json"]

        assert "inventory_identifier" in body
        assert body["inventory_identifier"] == "prod-routers"
        assert "nodes" in body
        assert len(body["nodes"]) == 1
        assert body["nodes"][0]["name"] == "core-router-1"
        assert body["nodes"][0]["attributes"]["itential_host"] == "10.1.1.1"
        assert body["nodes"][0]["tags"] == ["core"]

    @pytest.mark.asyncio
    async def test_add_nodes_to_inventory_additional_attributes(
        self, service, mock_client
    ):
        """Test adding nodes with additional custom attributes beyond standard ones."""
        inventories_data = [
            {"_id": "inv-1", "name": "custom-inv", "nodeCount": 0},
        ]

        nodes_with_extra_attrs = [
            {
                "name": "custom-device-1",
                "attributes": {
                    "itential_host": "10.3.1.1",
                    "itential_platform": "eos",
                    "cluster_id": "cluster_south",
                    "custom_region": "us-east-1",
                    "custom_rack": "rack-42",
                    "firmware_version": "4.28.1F",
                },
                "tags": ["custom", "eos"],
            },
        ]

        mock_list_response = Mock()
        mock_list_response.json.return_value = {"result": {"data": inventories_data}}

        mock_add_response = Mock()
        mock_add_response.json.return_value = {
            "status": "Success",
            "result": {},
            "message": "1 node added",
        }

        mock_client.get.return_value = mock_list_response
        mock_client.post.return_value = mock_add_response

        result = await service.add_nodes_to_inventory(
            "custom-inv", nodes_with_extra_attrs
        )

        assert result["status"] == "Success"

        # Verify additional attributes are passed through
        call_args = mock_client.post.call_args
        body = call_args[1]["json"]
        attrs = body["nodes"][0]["attributes"]
        assert attrs["custom_region"] == "us-east-1"
        assert attrs["custom_rack"] == "rack-42"
        assert attrs["firmware_version"] == "4.28.1F"

    # =========================================================================
    # delete_inventory tests
    # =========================================================================

    @pytest.mark.asyncio
    async def test_delete_inventory_success(self, service, mock_client):
        """Test successful deletion of an inventory."""
        inventories_data = [
            {"_id": "del-inv-1", "name": "Delete Me", "nodeCount": 5},
            {"_id": "del-inv-2", "name": "Keep Me", "nodeCount": 3},
        ]

        mock_list_response = Mock()
        mock_list_response.json.return_value = {"result": {"data": inventories_data}}

        mock_delete_response = Mock()
        mock_delete_response.json.return_value = {
            "status": "Success",
            "result": {},
            "message": "Inventory deleted successfully",
        }

        mock_client.get.return_value = mock_list_response
        mock_client.delete.return_value = mock_delete_response

        result = await service.delete_inventory("Delete Me")

        assert result["status"] == "Success"
        assert result["message"] == "Inventory deleted successfully"

        mock_client.delete.assert_called_once_with(
            "/inventory_manager/v1/inventories/del-inv-1"
        )

    @pytest.mark.asyncio
    async def test_delete_inventory_not_found(self, service, mock_client):
        """Test delete_inventory raises NotFoundError for non-existent inventory."""
        inventories_data = [
            {"_id": "inv-1", "name": "Existing", "nodeCount": 5},
        ]

        mock_response = Mock()
        mock_response.json.return_value = {"result": {"data": inventories_data}}
        mock_client.get.return_value = mock_response

        with pytest.raises(
            exceptions.NotFoundError, match="inventory 'NonExistent' not found"
        ):
            await service.delete_inventory("NonExistent")

        # Verify DELETE was never called
        mock_client.delete.assert_not_called()

    @pytest.mark.asyncio
    async def test_delete_inventory_empty_inventories(self, service, mock_client):
        """Test delete_inventory when no inventories exist."""
        mock_response = Mock()
        mock_response.json.return_value = {"result": {"data": []}}
        mock_client.get.return_value = mock_response

        with pytest.raises(exceptions.NotFoundError):
            await service.delete_inventory("Any Name")

    @pytest.mark.asyncio
    async def test_delete_inventory_status_merge(self, service, mock_client):
        """Test that status from outer response is merged into result."""
        inventories_data = [
            {"_id": "inv-1", "name": "Target", "nodeCount": 5},
        ]

        mock_list_response = Mock()
        mock_list_response.json.return_value = {"result": {"data": inventories_data}}

        # Simulate API where status is at outer level, not in result
        mock_delete_response = Mock()
        mock_delete_response.json.return_value = {
            "status": "Success",
            "result": {},
            "message": "Deleted",
        }

        mock_client.get.return_value = mock_list_response
        mock_client.delete.return_value = mock_delete_response

        result = await service.delete_inventory("Target")

        assert result["status"] == "Success"
        assert result["message"] == "Deleted"

    @pytest.mark.asyncio
    async def test_delete_inventory_status_not_overwritten(self, service, mock_client):
        """Test that existing status in result is not overwritten by outer status."""
        inventories_data = [
            {"_id": "inv-1", "name": "Target", "nodeCount": 5},
        ]

        mock_list_response = Mock()
        mock_list_response.json.return_value = {"result": {"data": inventories_data}}

        mock_delete_response = Mock()
        mock_delete_response.json.return_value = {
            "status": "Outer Status",
            "result": {"status": "Inner Status"},
            "message": "Outer message",
        }

        mock_client.get.return_value = mock_list_response
        mock_client.delete.return_value = mock_delete_response

        result = await service.delete_inventory("Target")

        # Inner status should be preserved
        assert result["status"] == "Inner Status"

    @pytest.mark.asyncio
    async def test_delete_inventory_case_sensitive(self, service, mock_client):
        """Test delete_inventory is case sensitive."""
        inventories_data = [
            {"_id": "inv-1", "name": "Production", "nodeCount": 5},
        ]

        mock_response = Mock()
        mock_response.json.return_value = {"result": {"data": inventories_data}}
        mock_client.get.return_value = mock_response

        with pytest.raises(exceptions.NotFoundError):
            await service.delete_inventory("production")
