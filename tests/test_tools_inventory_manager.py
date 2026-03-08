# Copyright (c) 2025 Itential, Inc
# GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

import pytest
from unittest.mock import AsyncMock, MagicMock

from fastmcp import Context

from itential_mcp.tools import inventory_manager
from itential_mcp.models.inventory_manager import (
    InventoryElement,
    GetInventoriesResponse,
    CreateInventoryResponse,
    DescribeInventoryResponse,
    AddNodesToInventoryResponse,
    DeleteInventoryResponse,
)


class TestModule:
    """Test the inventory_manager tools module"""

    def test_module_tags(self):
        """Test module has correct tags"""
        assert hasattr(inventory_manager, "__tags__")
        assert inventory_manager.__tags__ == ("inventory_manager",)

    def test_module_functions_exist(self):
        """Test all expected functions exist in the module"""
        expected_functions = [
            "get_inventories",
            "describe_inventory",
            "create_inventory",
            "add_nodes_to_inventory",
            "delete_inventory",
        ]

        for func_name in expected_functions:
            assert hasattr(inventory_manager, func_name)
            assert callable(getattr(inventory_manager, func_name))

    def test_functions_are_async(self):
        """Test that all functions are async"""
        import inspect

        functions_to_test = [
            inventory_manager.get_inventories,
            inventory_manager.describe_inventory,
            inventory_manager.create_inventory,
            inventory_manager.add_nodes_to_inventory,
            inventory_manager.delete_inventory,
        ]

        for func in functions_to_test:
            assert inspect.iscoroutinefunction(func), f"{func.__name__} should be async"


class TestGetInventories:
    """Test the get_inventories tool function"""

    @pytest.fixture
    def mock_context(self):
        """Create a mock Context object"""
        context = AsyncMock(spec=Context)
        context.info = AsyncMock()

        # Mock client
        mock_client = MagicMock()
        mock_client.get = AsyncMock()

        # Mock request context and lifespan context
        context.request_context = MagicMock()
        context.request_context.lifespan_context = MagicMock()
        context.request_context.lifespan_context.get.return_value = mock_client

        return context

    @pytest.mark.asyncio
    async def test_get_inventories_success(self, mock_context):
        """Test get_inventories with successful response"""
        mock_data = [
            {
                "_id": "inv-1",
                "name": "Production Inventory",
                "description": "Production network devices",
                "nodeCount": 10,
            },
            {
                "_id": "inv-2",
                "name": "Test Inventory",
                "description": "Test environment devices",
                "nodeCount": 3,
            },
        ]

        mock_client = mock_context.request_context.lifespan_context.get.return_value
        mock_client.inventory_manager = MagicMock()
        mock_client.inventory_manager.get_inventories = AsyncMock(
            return_value=mock_data
        )

        result = await inventory_manager.get_inventories(mock_context)

        # Verify API call
        mock_client.inventory_manager.get_inventories.assert_called_once()

        # Verify result type and structure
        assert isinstance(result, GetInventoriesResponse)
        assert len(result.root) == 2

        # Verify first inventory
        first_inv = result.root[0]
        assert isinstance(first_inv, InventoryElement)
        assert first_inv.object_id == "inv-1"
        assert first_inv.name == "Production Inventory"
        assert first_inv.description == "Production network devices"
        assert first_inv.node_count == 10

        # Verify second inventory
        second_inv = result.root[1]
        assert second_inv.object_id == "inv-2"
        assert second_inv.name == "Test Inventory"
        assert second_inv.node_count == 3

    @pytest.mark.asyncio
    async def test_get_inventories_empty_response(self, mock_context):
        """Test get_inventories with empty response"""
        mock_client = mock_context.request_context.lifespan_context.get.return_value
        mock_client.inventory_manager = MagicMock()
        mock_client.inventory_manager.get_inventories = AsyncMock(return_value=[])

        result = await inventory_manager.get_inventories(mock_context)

        assert isinstance(result, GetInventoriesResponse)
        assert len(result.root) == 0
        assert result.root == []

    @pytest.mark.asyncio
    async def test_get_inventories_logs_info(self, mock_context):
        """Test get_inventories logs info message"""
        mock_client = mock_context.request_context.lifespan_context.get.return_value
        mock_client.inventory_manager = MagicMock()
        mock_client.inventory_manager.get_inventories = AsyncMock(return_value=[])

        await inventory_manager.get_inventories(mock_context)

        mock_context.info.assert_called_once_with("inside get_inventories(...)")

    @pytest.mark.asyncio
    async def test_get_inventories_handles_missing_fields(self, mock_context):
        """Test get_inventories handles missing optional fields gracefully"""
        mock_data = [
            {
                "_id": "inv-1",
                "name": "Minimal Inventory",
            }
        ]

        mock_client = mock_context.request_context.lifespan_context.get.return_value
        mock_client.inventory_manager = MagicMock()
        mock_client.inventory_manager.get_inventories = AsyncMock(
            return_value=mock_data
        )

        result = await inventory_manager.get_inventories(mock_context)

        assert isinstance(result, GetInventoriesResponse)
        assert len(result.root) == 1
        assert result.root[0].node_count == 0
        assert result.root[0].description == ""


class TestDescribeInventory:
    """Test the describe_inventory tool function"""

    @pytest.fixture
    def mock_context(self):
        """Create a mock Context object"""
        context = AsyncMock(spec=Context)
        context.info = AsyncMock()

        # Mock client
        mock_client = MagicMock()
        mock_client.get = AsyncMock()

        # Mock request context and lifespan context
        context.request_context = MagicMock()
        context.request_context.lifespan_context = MagicMock()
        context.request_context.lifespan_context.get.return_value = mock_client

        return context

    @pytest.mark.asyncio
    async def test_describe_inventory_success(self, mock_context):
        """Test describe_inventory with successful response including nodes"""
        mock_data = {
            "_id": "desc-inv-123",
            "name": "Production Inventory",
            "description": "Production network devices",
            "groups": ["Solutions Engineering"],
            "actions": [{"name": "backup", "type": "backup"}],
            "tags": ["production"],
            "nodes": [
                {
                    "name": "core-router-1",
                    "attributes": {
                        "itential_host": "10.1.1.1",
                        "itential_platform": "iosxr",
                        "cluster_id": "cluster_east",
                    },
                    "tags": ["core"],
                },
            ],
        }

        mock_client = mock_context.request_context.lifespan_context.get.return_value
        mock_client.inventory_manager = MagicMock()
        mock_client.inventory_manager.describe_inventory = AsyncMock(
            return_value=mock_data
        )

        result = await inventory_manager.describe_inventory(
            mock_context, name="Production Inventory"
        )

        # Verify response structure
        assert isinstance(result, DescribeInventoryResponse)
        assert result.object_id == "desc-inv-123"
        assert result.name == "Production Inventory"
        assert result.description == "Production network devices"
        assert result.groups == ["Solutions Engineering"]
        assert len(result.actions) == 1
        assert result.tags == ["production"]
        assert len(result.nodes) == 1
        assert result.nodes[0]["name"] == "core-router-1"
        assert result.nodes[0]["attributes"]["itential_host"] == "10.1.1.1"

        # Verify service method was called with correct parameters
        mock_client.inventory_manager.describe_inventory.assert_called_once_with(
            "Production Inventory"
        )

    @pytest.mark.asyncio
    async def test_describe_inventory_not_found(self, mock_context):
        """Test describe_inventory raises error for non-existent inventory"""
        from itential_mcp.core import exceptions

        mock_client = mock_context.request_context.lifespan_context.get.return_value
        mock_client.inventory_manager = MagicMock()
        mock_client.inventory_manager.describe_inventory = AsyncMock(
            side_effect=exceptions.NotFoundError("inventory 'NonExistent' not found")
        )

        with pytest.raises(
            exceptions.NotFoundError, match="inventory 'NonExistent' not found"
        ):
            await inventory_manager.describe_inventory(mock_context, name="NonExistent")

    @pytest.mark.asyncio
    async def test_describe_inventory_logs_info(self, mock_context):
        """Test describe_inventory logs info message"""
        mock_client = mock_context.request_context.lifespan_context.get.return_value
        mock_client.inventory_manager = MagicMock()
        mock_client.inventory_manager.describe_inventory = AsyncMock(
            return_value={"_id": "test", "name": "test"}
        )

        await inventory_manager.describe_inventory(mock_context, name="test")

        mock_context.info.assert_called_once_with("inside describe_inventory(...)")


class TestCreateInventory:
    """Test the create_inventory tool function"""

    @pytest.fixture
    def mock_context(self):
        """Create a mock Context object"""
        context = AsyncMock(spec=Context)
        context.info = AsyncMock()

        # Mock client
        mock_client = MagicMock()
        mock_client.get = AsyncMock()
        mock_client.post = AsyncMock()

        # Mock request context and lifespan context
        context.request_context = MagicMock()
        context.request_context.lifespan_context = MagicMock()
        context.request_context.lifespan_context.get.return_value = mock_client

        return context

    @pytest.mark.asyncio
    async def test_create_inventory_success(self, mock_context):
        """Test create_inventory with successful creation"""
        mock_response_data = {
            "_id": "new-inv-123",
            "name": "New Production Inventory",
            "message": "Inventory created successfully",
        }

        mock_client = mock_context.request_context.lifespan_context.get.return_value
        mock_client.inventory_manager = MagicMock()
        mock_client.inventory_manager.create_inventory = AsyncMock(
            return_value=mock_response_data
        )

        result = await inventory_manager.create_inventory(
            mock_context,
            name="New Production Inventory",
            groups=["Solutions Engineering"],
            description="A new production inventory",
            devices=["router1", "router2"],
        )

        # Verify response structure
        assert isinstance(result, CreateInventoryResponse)
        assert result.object_id == "new-inv-123"
        assert result.name == "New Production Inventory"
        assert result.message == "Inventory created successfully"

        # Verify service method was called with correct parameters
        mock_client.inventory_manager.create_inventory.assert_called_once_with(
            "New Production Inventory",
            ["Solutions Engineering"],
            description="A new production inventory",
            devices=["router1", "router2"],
        )

    @pytest.mark.asyncio
    async def test_create_inventory_minimal(self, mock_context):
        """Test create_inventory with minimal parameters"""
        mock_response_data = {
            "_id": "minimal-inv",
            "name": "Minimal Inventory",
            "message": "Inventory created successfully",
        }

        mock_client = mock_context.request_context.lifespan_context.get.return_value
        mock_client.inventory_manager = MagicMock()
        mock_client.inventory_manager.create_inventory = AsyncMock(
            return_value=mock_response_data
        )

        result = await inventory_manager.create_inventory(
            mock_context,
            name="Minimal Inventory",
            groups=["Solutions Engineering"],
            description=None,
            devices=None,
        )

        # Verify response structure
        assert isinstance(result, CreateInventoryResponse)
        assert result.object_id == "minimal-inv"

        # Verify service method was called with correct parameters
        mock_client.inventory_manager.create_inventory.assert_called_once_with(
            "Minimal Inventory",
            ["Solutions Engineering"],
            description=None,
            devices=None,
        )

    @pytest.mark.asyncio
    async def test_create_inventory_duplicate_name_error(self, mock_context):
        """Test create_inventory raises error for duplicate name"""
        mock_client = mock_context.request_context.lifespan_context.get.return_value
        mock_client.inventory_manager = MagicMock()
        mock_client.inventory_manager.create_inventory = AsyncMock(
            side_effect=ValueError("inventory 'Existing Inventory' already exists")
        )

        with pytest.raises(
            ValueError, match="inventory 'Existing Inventory' already exists"
        ):
            await inventory_manager.create_inventory(
                mock_context,
                name="Existing Inventory",
                groups=["Solutions Engineering"],
                description=None,
                devices=None,
            )

    @pytest.mark.asyncio
    async def test_create_inventory_logs_info(self, mock_context):
        """Test create_inventory logs info message"""
        mock_client = mock_context.request_context.lifespan_context.get.return_value
        mock_client.inventory_manager = MagicMock()
        mock_client.inventory_manager.create_inventory = AsyncMock(
            return_value={"_id": "test", "name": "test"}
        )

        await inventory_manager.create_inventory(
            mock_context,
            name="test",
            groups=["test-group"],
            description=None,
            devices=None,
        )

        mock_context.info.assert_called_once_with("inside create_inventory(...)")


class TestAddNodesToInventory:
    """Test the add_nodes_to_inventory tool function"""

    @pytest.fixture
    def mock_context(self):
        """Create a mock Context object"""
        context = AsyncMock(spec=Context)
        context.info = AsyncMock()

        # Mock client
        mock_client = MagicMock()
        mock_client.post = AsyncMock()

        # Mock request context and lifespan context
        context.request_context = MagicMock()
        context.request_context.lifespan_context = MagicMock()
        context.request_context.lifespan_context.get.return_value = mock_client

        return context

    @pytest.mark.asyncio
    async def test_add_nodes_to_inventory_success(self, mock_context):
        """Test add_nodes_to_inventory with successful response using sample payload"""
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

        mock_response_data = {
            "status": "Success",
            "message": "2 nodes added to inventory",
        }

        mock_client = mock_context.request_context.lifespan_context.get.return_value
        mock_client.inventory_manager = MagicMock()
        mock_client.inventory_manager.add_nodes_to_inventory = AsyncMock(
            return_value=mock_response_data
        )

        result = await inventory_manager.add_nodes_to_inventory(
            mock_context,
            inventory_name="prod-routers",
            nodes=sample_nodes,
        )

        # Verify response structure
        assert isinstance(result, AddNodesToInventoryResponse)
        assert result.status == "Success"
        assert result.message == "2 nodes added to inventory"

        # Verify service method was called with correct parameters
        mock_client.inventory_manager.add_nodes_to_inventory.assert_called_once_with(
            "prod-routers", sample_nodes
        )

    @pytest.mark.asyncio
    async def test_add_nodes_to_inventory_without_tags(self, mock_context):
        """Test add_nodes_to_inventory with nodes that have no tags"""
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

        mock_response_data = {
            "status": "Success",
            "message": "1 node added to inventory",
        }

        mock_client = mock_context.request_context.lifespan_context.get.return_value
        mock_client.inventory_manager = MagicMock()
        mock_client.inventory_manager.add_nodes_to_inventory = AsyncMock(
            return_value=mock_response_data
        )

        result = await inventory_manager.add_nodes_to_inventory(
            mock_context,
            inventory_name="edge-switches",
            nodes=nodes_without_tags,
        )

        assert isinstance(result, AddNodesToInventoryResponse)
        assert result.status == "Success"

    @pytest.mark.asyncio
    async def test_add_nodes_to_inventory_not_found(self, mock_context):
        """Test add_nodes_to_inventory raises error for non-existent inventory"""
        from itential_mcp.core import exceptions

        mock_client = mock_context.request_context.lifespan_context.get.return_value
        mock_client.inventory_manager = MagicMock()
        mock_client.inventory_manager.add_nodes_to_inventory = AsyncMock(
            side_effect=exceptions.NotFoundError("inventory 'NonExistent' not found")
        )

        with pytest.raises(
            exceptions.NotFoundError, match="inventory 'NonExistent' not found"
        ):
            await inventory_manager.add_nodes_to_inventory(
                mock_context,
                inventory_name="NonExistent",
                nodes=[{"name": "test", "attributes": {"itential_host": "1.1.1.1"}}],
            )

    @pytest.mark.asyncio
    async def test_add_nodes_to_inventory_default_status_message(self, mock_context):
        """Test add_nodes_to_inventory uses defaults when status/message missing"""
        mock_response_data = {}

        mock_client = mock_context.request_context.lifespan_context.get.return_value
        mock_client.inventory_manager = MagicMock()
        mock_client.inventory_manager.add_nodes_to_inventory = AsyncMock(
            return_value=mock_response_data
        )

        result = await inventory_manager.add_nodes_to_inventory(
            mock_context,
            inventory_name="test-inventory",
            nodes=[{"name": "node1", "attributes": {"itential_host": "1.1.1.1"}}],
        )

        assert isinstance(result, AddNodesToInventoryResponse)
        assert result.status == "Success"
        assert result.message == "Nodes added successfully"

    @pytest.mark.asyncio
    async def test_add_nodes_to_inventory_logs_info(self, mock_context):
        """Test add_nodes_to_inventory logs info message"""
        mock_client = mock_context.request_context.lifespan_context.get.return_value
        mock_client.inventory_manager = MagicMock()
        mock_client.inventory_manager.add_nodes_to_inventory = AsyncMock(
            return_value={"status": "Success", "message": "Done"}
        )

        await inventory_manager.add_nodes_to_inventory(
            mock_context,
            inventory_name="test",
            nodes=[{"name": "node1", "attributes": {"itential_host": "1.1.1.1"}}],
        )

        mock_context.info.assert_called_once_with("inside add_nodes_to_inventory(...)")


class TestDeleteInventory:
    """Test the delete_inventory tool function"""

    @pytest.fixture
    def mock_context(self):
        """Create a mock Context object"""
        context = AsyncMock(spec=Context)
        context.info = AsyncMock()

        # Mock client
        mock_client = MagicMock()
        mock_client.delete = AsyncMock()

        # Mock request context and lifespan context
        context.request_context = MagicMock()
        context.request_context.lifespan_context = MagicMock()
        context.request_context.lifespan_context.get.return_value = mock_client

        return context

    @pytest.mark.asyncio
    async def test_delete_inventory_success(self, mock_context):
        """Test delete_inventory with successful deletion"""
        mock_response_data = {
            "status": "Success",
            "message": "Inventory deleted successfully",
        }

        mock_client = mock_context.request_context.lifespan_context.get.return_value
        mock_client.inventory_manager = MagicMock()
        mock_client.inventory_manager.delete_inventory = AsyncMock(
            return_value=mock_response_data
        )

        result = await inventory_manager.delete_inventory(
            mock_context, name="Old Inventory"
        )

        # Verify response structure
        assert isinstance(result, DeleteInventoryResponse)
        assert result.status == "Success"
        assert result.message == "Inventory deleted successfully"

        # Verify service method was called with correct parameters
        mock_client.inventory_manager.delete_inventory.assert_called_once_with(
            "Old Inventory"
        )

    @pytest.mark.asyncio
    async def test_delete_inventory_not_found(self, mock_context):
        """Test delete_inventory raises error for non-existent inventory"""
        from itential_mcp.core import exceptions

        mock_client = mock_context.request_context.lifespan_context.get.return_value
        mock_client.inventory_manager = MagicMock()
        mock_client.inventory_manager.delete_inventory = AsyncMock(
            side_effect=exceptions.NotFoundError("inventory 'NonExistent' not found")
        )

        with pytest.raises(
            exceptions.NotFoundError, match="inventory 'NonExistent' not found"
        ):
            await inventory_manager.delete_inventory(mock_context, name="NonExistent")

    @pytest.mark.asyncio
    async def test_delete_inventory_logs_info(self, mock_context):
        """Test delete_inventory logs info message"""
        mock_client = mock_context.request_context.lifespan_context.get.return_value
        mock_client.inventory_manager = MagicMock()
        mock_client.inventory_manager.delete_inventory = AsyncMock(
            return_value={"status": "Success", "message": "Deleted"}
        )

        await inventory_manager.delete_inventory(mock_context, name="test")

        mock_context.info.assert_called_once_with("inside delete_inventory(...)")


class TestToolsIntegration:
    """Integration tests for inventory_manager tools"""

    @pytest.fixture
    def mock_context(self):
        """Create a mock Context object for integration tests"""
        context = AsyncMock(spec=Context)
        context.info = AsyncMock()

        mock_client = MagicMock()

        context.request_context = MagicMock()
        context.request_context.lifespan_context = MagicMock()
        context.request_context.lifespan_context.get.return_value = mock_client

        return context

    @pytest.mark.asyncio
    async def test_create_then_get_inventories(self, mock_context):
        """Test creating an inventory then listing all inventories"""
        mock_client = mock_context.request_context.lifespan_context.get.return_value
        mock_client.inventory_manager = MagicMock()

        # Create inventory
        mock_client.inventory_manager.create_inventory = AsyncMock(
            return_value={
                "_id": "new-inv",
                "name": "Integration Test Inventory",
                "message": "Created",
            }
        )

        create_result = await inventory_manager.create_inventory(
            mock_context,
            name="Integration Test Inventory",
            groups=["test-group"],
            description="Integration test",
            devices=None,
        )

        assert isinstance(create_result, CreateInventoryResponse)
        assert create_result.name == "Integration Test Inventory"

        # Get inventories
        mock_client.inventory_manager.get_inventories = AsyncMock(
            return_value=[
                {
                    "_id": "new-inv",
                    "name": "Integration Test Inventory",
                    "description": "Integration test",
                    "nodeCount": 0,
                }
            ]
        )

        get_result = await inventory_manager.get_inventories(mock_context)

        assert isinstance(get_result, GetInventoriesResponse)
        assert len(get_result.root) == 1
        assert get_result.root[0].name == "Integration Test Inventory"

    @pytest.mark.asyncio
    async def test_create_then_add_nodes(self, mock_context):
        """Test creating an inventory then adding nodes to it"""
        mock_client = mock_context.request_context.lifespan_context.get.return_value
        mock_client.inventory_manager = MagicMock()

        # Create inventory
        mock_client.inventory_manager.create_inventory = AsyncMock(
            return_value={
                "_id": "new-inv",
                "name": "prod-routers",
                "message": "Created",
            }
        )

        create_result = await inventory_manager.create_inventory(
            mock_context,
            name="prod-routers",
            groups=["Solutions Engineering"],
            description="Production routers",
            devices=None,
        )

        assert isinstance(create_result, CreateInventoryResponse)
        assert create_result.name == "prod-routers"

        # Add nodes
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
        ]

        mock_client.inventory_manager.add_nodes_to_inventory = AsyncMock(
            return_value={
                "status": "Success",
                "message": "1 node added to inventory",
            }
        )

        add_result = await inventory_manager.add_nodes_to_inventory(
            mock_context,
            inventory_name="prod-routers",
            nodes=sample_nodes,
        )

        assert isinstance(add_result, AddNodesToInventoryResponse)
        assert add_result.status == "Success"
