# Copyright (c) 2025 Itential, Inc
# GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

import pytest
from unittest.mock import AsyncMock, MagicMock

from fastmcp import Context

from itential_mcp.tools import device_groups
from itential_mcp.models.device_groups import (
    DeviceGroupElement,
    GetDeviceGroupsResponse,
    CreateDeviceGroupResponse,
    AddDevicesToGroupResponse,
    RemoveDevicesFromGroupResponse,
)


class TestModule:
    """Test the device_groups tools module"""

    def test_module_tags(self):
        """Test module has correct tags"""
        assert hasattr(device_groups, "__tags__")
        assert device_groups.__tags__ == ("configuration_manager",)

    def test_module_functions_exist(self):
        """Test all expected functions exist in the module"""
        expected_functions = [
            "get_device_groups",
            "create_device_group",
            "add_devices_to_group",
            "remove_devices_from_group",
        ]

        for func_name in expected_functions:
            assert hasattr(device_groups, func_name)
            assert callable(getattr(device_groups, func_name))

    def test_functions_are_async(self):
        """Test that all functions are async"""
        import inspect

        functions_to_test = [
            device_groups.get_device_groups,
            device_groups.create_device_group,
            device_groups.add_devices_to_group,
            device_groups.remove_devices_from_group,
        ]

        for func in functions_to_test:
            assert inspect.iscoroutinefunction(func), f"{func.__name__} should be async"


class TestGetDeviceGroups:
    """Test the get_device_groups tool function"""

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
    async def test_get_device_groups_success(self, mock_context):
        """Test get_device_groups with successful response"""
        mock_data = [
            {
                "id": "group-1",
                "name": "Production Routers",
                "devices": ["router1", "router2", "router3"],
                "description": "Production network routers",
            },
            {
                "id": "group-2",
                "name": "Test Switches",
                "devices": ["switch1", "switch2"],
                "description": "Test environment switches",
            },
        ]

        mock_client = mock_context.request_context.lifespan_context.get.return_value
        mock_client.configuration_manager = MagicMock()
        mock_client.configuration_manager.get_device_groups = AsyncMock(
            return_value=mock_data
        )

        result = await device_groups.get_device_groups(mock_context)

        # Verify API call
        mock_client.configuration_manager.get_device_groups.assert_called_once()

        # Verify result type and structure
        assert isinstance(result, GetDeviceGroupsResponse)
        assert len(result.root) == 2

        # Verify first device group
        first_group = result.root[0]
        assert isinstance(first_group, DeviceGroupElement)
        assert first_group.object_id == "group-1"
        assert first_group.name == "Production Routers"
        assert first_group.devices == ["router1", "router2", "router3"]
        assert first_group.description == "Production network routers"

        # Verify second device group
        second_group = result.root[1]
        assert second_group.object_id == "group-2"
        assert second_group.name == "Test Switches"
        assert second_group.devices == ["switch1", "switch2"]

    @pytest.mark.asyncio
    async def test_get_device_groups_empty_response(self, mock_context):
        """Test get_device_groups with empty response"""
        mock_client = mock_context.request_context.lifespan_context.get.return_value
        mock_client.configuration_manager = MagicMock()
        mock_client.configuration_manager.get_device_groups = AsyncMock(return_value=[])

        result = await device_groups.get_device_groups(mock_context)

        assert isinstance(result, GetDeviceGroupsResponse)
        assert len(result.root) == 0
        assert result.root == []

    @pytest.mark.asyncio
    async def test_get_device_groups_logs_info(self, mock_context):
        """Test get_device_groups logs info message"""
        mock_client = mock_context.request_context.lifespan_context.get.return_value
        mock_client.configuration_manager = MagicMock()
        mock_client.configuration_manager.get_device_groups = AsyncMock(return_value=[])

        await device_groups.get_device_groups(mock_context)

        mock_context.info.assert_called_once_with("inside get_device_groups(...)")

    @pytest.mark.asyncio
    async def test_get_device_groups_handles_missing_fields(self, mock_context):
        """Test get_device_groups handles missing optional fields gracefully"""
        mock_data = [
            {
                "id": "group-1",
                "name": "Minimal Group",
                "devices": [],
                "description": "A minimal device group",
            }
        ]

        mock_client = mock_context.request_context.lifespan_context.get.return_value
        mock_client.configuration_manager = MagicMock()
        mock_client.configuration_manager.get_device_groups = AsyncMock(
            return_value=mock_data
        )

        result = await device_groups.get_device_groups(mock_context)

        assert isinstance(result, GetDeviceGroupsResponse)
        assert len(result.root) == 1
        assert result.root[0].devices == []


class TestCreateDeviceGroup:
    """Test the create_device_group tool function"""

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
    async def test_create_device_group_success(self, mock_context):
        """Test create_device_group with successful creation"""
        # Mock create response
        mock_response_data = {
            "id": "new-group-123",
            "name": "New Production Group",
            "message": "Device group created successfully",
            "status": "active",
        }

        mock_client = mock_context.request_context.lifespan_context.get.return_value
        mock_client.configuration_manager = MagicMock()
        mock_client.configuration_manager.create_device_group = AsyncMock(
            return_value=mock_response_data
        )

        result = await device_groups.create_device_group(
            mock_context,
            name="New Production Group",
            description="A new production device group",
            devices=["router1", "router2"],
        )

        # Verify response structure
        assert isinstance(result, CreateDeviceGroupResponse)
        assert result.object_id == "new-group-123"
        assert result.name == "New Production Group"
        assert result.message == "Device group created successfully"
        assert result.status == "active"

        # Verify service method was called with correct parameters
        mock_client.configuration_manager.create_device_group.assert_called_once_with(
            name="New Production Group",
            description="A new production device group",
            devices=["router1", "router2"],
        )

    @pytest.mark.asyncio
    async def test_create_device_group_no_devices(self, mock_context):
        """Test create_device_group with no devices specified"""
        mock_response_data = {
            "id": "empty-group-456",
            "name": "Empty Group",
            "message": "Empty device group created",
            "status": "active",
        }

        mock_client = mock_context.request_context.lifespan_context.get.return_value
        mock_client.configuration_manager = MagicMock()
        mock_client.configuration_manager.create_device_group = AsyncMock(
            return_value=mock_response_data
        )

        result = await device_groups.create_device_group(
            mock_context,
            name="Empty Group",
            description="An empty device group",
            devices=[],
        )

        # Verify response structure
        assert isinstance(result, CreateDeviceGroupResponse)
        assert result.object_id == "empty-group-456"
        assert result.name == "Empty Group"
        assert result.message == "Empty device group created"
        assert result.status == "active"

        # Verify service method was called with correct parameters
        mock_client.configuration_manager.create_device_group.assert_called_once_with(
            name="Empty Group", description="An empty device group", devices=[]
        )

    @pytest.mark.asyncio
    async def test_create_device_group_duplicate_name_error(self, mock_context):
        """Test create_device_group raises error for duplicate name"""
        mock_client = mock_context.request_context.lifespan_context.get.return_value
        mock_client.configuration_manager = MagicMock()
        mock_client.configuration_manager.create_device_group = AsyncMock(
            side_effect=ValueError("device group Existing Group already exists")
        )

        with pytest.raises(
            ValueError, match="device group Existing Group already exists"
        ):
            await device_groups.create_device_group(
                mock_context,
                name="Existing Group",
                description="Duplicate group",
                devices=[],
            )

    @pytest.mark.asyncio
    async def test_create_device_group_no_description(self, mock_context):
        """Test create_device_group with no description"""
        mock_response_data = {
            "id": "no-desc-group",
            "name": "No Description Group",
            "message": "Group created without description",
            "status": "active",
        }

        mock_client = mock_context.request_context.lifespan_context.get.return_value
        mock_client.configuration_manager = MagicMock()
        mock_client.configuration_manager.create_device_group = AsyncMock(
            return_value=mock_response_data
        )

        result = await device_groups.create_device_group(
            mock_context, name="No Description Group", description=None, devices=[]
        )

        # Verify response structure
        assert isinstance(result, CreateDeviceGroupResponse)
        assert result.object_id == "no-desc-group"
        assert result.name == "No Description Group"
        assert result.message == "Group created without description"
        assert result.status == "active"

        # Verify service method was called with correct parameters (None description)
        mock_client.configuration_manager.create_device_group.assert_called_once_with(
            name="No Description Group", description=None, devices=[]
        )

    @pytest.mark.asyncio
    async def test_create_device_group_logs_info(self, mock_context):
        """Test create_device_group logs info message"""
        mock_response_data = {
            "id": "test",
            "name": "test",
            "message": "test",
            "status": "test",
        }

        mock_client = mock_context.request_context.lifespan_context.get.return_value
        mock_client.configuration_manager = MagicMock()
        mock_client.configuration_manager.create_device_group = AsyncMock(
            return_value=mock_response_data
        )

        await device_groups.create_device_group(
            mock_context, name="Test", description=None, devices=[]
        )

        mock_context.info.assert_called_once_with("inside create_device_group(...)")


class TestAddDevicesToGroup:
    """Test the add_devices_to_group tool function"""

    @pytest.fixture
    def mock_context(self):
        """Create a mock Context object"""
        context = AsyncMock(spec=Context)
        context.info = AsyncMock()

        # Mock client
        mock_client = MagicMock()
        mock_client.put = AsyncMock()

        # Mock request context and lifespan context
        context.request_context = MagicMock()
        context.request_context.lifespan_context = MagicMock()
        context.request_context.lifespan_context.get.return_value = mock_client

        return context

    @pytest.mark.asyncio
    async def test_add_devices_to_group_success(self, mock_context):
        """Test add_devices_to_group with successful addition"""
        mock_response_data = {"status": "success"}

        mock_client = mock_context.request_context.lifespan_context.get.return_value
        mock_client.configuration_manager = MagicMock()
        mock_client.configuration_manager.add_devices_to_group = AsyncMock(
            return_value=mock_response_data
        )

        result = await device_groups.add_devices_to_group(
            mock_context, name="Test Group", devices=["device1", "device2", "device3"]
        )

        # Verify service method was called
        mock_client.configuration_manager.add_devices_to_group.assert_called_once_with(
            "Test Group", ["device1", "device2", "device3"]
        )

        # Verify result
        assert isinstance(result, AddDevicesToGroupResponse)
        assert result.status == "success"
        assert result.message == "Devices added successfully"

    @pytest.mark.asyncio
    async def test_add_devices_to_group_with_message(self, mock_context):
        """Test add_devices_to_group when API returns a message"""
        mock_response_data = {
            "status": "partial",
            "message": "2 of 3 devices added successfully",
        }

        mock_client = mock_context.request_context.lifespan_context.get.return_value
        mock_client.configuration_manager = MagicMock()
        mock_client.configuration_manager.add_devices_to_group = AsyncMock(
            return_value=mock_response_data
        )

        result = await device_groups.add_devices_to_group(
            mock_context,
            name="Partial Group",
            devices=["device1", "device2", "device3"],
        )

        assert result.status == "partial"
        assert result.message == "2 of 3 devices added successfully"

    @pytest.mark.asyncio
    async def test_add_devices_to_group_no_devices(self, mock_context):
        """Test add_devices_to_group with no devices specified"""
        mock_response_data = {"status": "success"}

        mock_client = mock_context.request_context.lifespan_context.get.return_value
        mock_client.configuration_manager = MagicMock()
        mock_client.configuration_manager.add_devices_to_group = AsyncMock(
            return_value=mock_response_data
        )

        await device_groups.add_devices_to_group(
            mock_context, name="No Devices Group", devices=[]
        )

        # Verify empty devices list was handled
        mock_client.configuration_manager.add_devices_to_group.assert_called_once_with(
            "No Devices Group", []
        )

    @pytest.mark.asyncio
    async def test_add_devices_to_group_logs_info(self, mock_context):
        """Test add_devices_to_group logs info message"""
        mock_client = mock_context.request_context.lifespan_context.get.return_value
        mock_client.configuration_manager = MagicMock()
        mock_client.configuration_manager.add_devices_to_group = AsyncMock(
            return_value={"status": "test"}
        )

        await device_groups.add_devices_to_group(mock_context, name="Test", devices=[])

        mock_context.info.assert_called_once_with("inside add_devices_to_group(...)")


class TestRemoveDevicesFromGroup:
    """Test the remove_devices_from_group tool function"""

    @pytest.fixture
    def mock_context(self):
        """Create a mock Context object"""
        context = AsyncMock(spec=Context)
        context.info = AsyncMock()

        # Mock client with configuration_manager
        mock_client = MagicMock()
        mock_client.put = AsyncMock()
        mock_client.configuration_manager = MagicMock()
        mock_client.configuration_manager.describe_device_group = AsyncMock()

        # Mock request context and lifespan context
        context.request_context = MagicMock()
        context.request_context.lifespan_context = MagicMock()
        context.request_context.lifespan_context.get.return_value = mock_client

        return context

    @pytest.mark.asyncio
    async def test_remove_devices_from_group_success(self, mock_context):
        """Test remove_devices_from_group with successful removal"""
        mock_response_data = {"status": "success"}

        mock_client = mock_context.request_context.lifespan_context.get.return_value
        mock_client.configuration_manager = MagicMock()
        mock_client.configuration_manager.remove_devices_from_group = AsyncMock(
            return_value=mock_response_data
        )

        result = await device_groups.remove_devices_from_group(
            mock_context,
            name="Test Group",
            devices=["device2", "device4"],  # Remove 2 devices
        )

        # Verify service method was called
        mock_client.configuration_manager.remove_devices_from_group.assert_called_once_with(
            "Test Group", ["device2", "device4"]
        )

        # Verify result
        assert isinstance(result, RemoveDevicesFromGroupResponse)
        assert result.status == "success"
        assert result.message == "Devices removed successfully"

    @pytest.mark.asyncio
    async def test_remove_devices_from_group_remove_all(self, mock_context):
        """Test remove_devices_from_group removing all devices"""
        mock_client = mock_context.request_context.lifespan_context.get.return_value
        mock_client.configuration_manager = MagicMock()
        mock_client.configuration_manager.remove_devices_from_group = AsyncMock(
            return_value={"status": "success"}
        )

        result = await device_groups.remove_devices_from_group(
            mock_context,
            name="Empty Group",
            devices=["device1", "device2"],  # Remove all devices
        )

        # Verify service method was called
        mock_client.configuration_manager.remove_devices_from_group.assert_called_once_with(
            "Empty Group", ["device1", "device2"]
        )

        assert result.status == "success"

    @pytest.mark.asyncio
    async def test_remove_devices_from_group_nonexistent_devices(self, mock_context):
        """Test remove_devices_from_group with devices not in group"""
        mock_client = mock_context.request_context.lifespan_context.get.return_value
        mock_client.configuration_manager = MagicMock()
        mock_client.configuration_manager.remove_devices_from_group = AsyncMock(
            return_value={"status": "success"}
        )

        result = await device_groups.remove_devices_from_group(
            mock_context,
            name="Test Group",
            devices=["device4", "device5"],  # Devices not in group
        )

        # Verify service method was called
        mock_client.configuration_manager.remove_devices_from_group.assert_called_once_with(
            "Test Group", ["device4", "device5"]
        )

        assert result.status == "success"

    @pytest.mark.asyncio
    async def test_remove_devices_from_group_partial_removal(self, mock_context):
        """Test remove_devices_from_group with partial device removal"""
        mock_client = mock_context.request_context.lifespan_context.get.return_value
        mock_client.configuration_manager = MagicMock()
        mock_client.configuration_manager.remove_devices_from_group = AsyncMock(
            return_value={"status": "partial"}
        )

        result = await device_groups.remove_devices_from_group(
            mock_context,
            name="Mixed Group",
            devices=["device2", "device5"],  # device2 exists, device5 doesn't
        )

        # Verify service method was called
        mock_client.configuration_manager.remove_devices_from_group.assert_called_once_with(
            "Mixed Group", ["device2", "device5"]
        )

        assert result.status == "partial"

    @pytest.mark.asyncio
    async def test_remove_devices_from_group_no_devices_specified(self, mock_context):
        """Test remove_devices_from_group with no devices specified"""
        mock_client = mock_context.request_context.lifespan_context.get.return_value
        mock_client.configuration_manager = MagicMock()
        mock_client.configuration_manager.remove_devices_from_group = AsyncMock(
            return_value={"status": "success"}
        )

        result = await device_groups.remove_devices_from_group(
            mock_context, name="No Remove Group", devices=[]
        )

        # Verify service method was called
        mock_client.configuration_manager.remove_devices_from_group.assert_called_once_with(
            "No Remove Group", []
        )

        assert result.status == "success"

    @pytest.mark.asyncio
    async def test_remove_devices_from_group_empty_group(self, mock_context):
        """Test remove_devices_from_group with empty group"""
        mock_client = mock_context.request_context.lifespan_context.get.return_value
        mock_client.configuration_manager = MagicMock()
        mock_client.configuration_manager.remove_devices_from_group = AsyncMock(
            return_value={"status": "warning"}
        )

        result = await device_groups.remove_devices_from_group(
            mock_context, name="Empty Group", devices=["device1"]
        )

        # Verify service method was called
        mock_client.configuration_manager.remove_devices_from_group.assert_called_once_with(
            "Empty Group", ["device1"]
        )

        assert result.status == "warning"

    @pytest.mark.asyncio
    async def test_remove_devices_from_group_logs_info(self, mock_context):
        """Test remove_devices_from_group logs info message"""
        mock_client = mock_context.request_context.lifespan_context.get.return_value
        mock_client.configuration_manager = MagicMock()
        mock_client.configuration_manager.remove_devices_from_group = AsyncMock(
            return_value={"status": "test"}
        )

        await device_groups.remove_devices_from_group(
            mock_context, name="Test", devices=[]
        )

        mock_context.info.assert_called_once_with(
            "inside remove_devices_from_group(...)"
        )


class TestToolsIntegration:
    """Test integration scenarios between tools functions"""

    @pytest.fixture
    def mock_context(self):
        """Create a mock Context object"""
        context = AsyncMock(spec=Context)
        context.info = AsyncMock()

        # Mock client
        mock_client = MagicMock()
        mock_client.get = AsyncMock()
        mock_client.post = AsyncMock()
        mock_client.put = AsyncMock()
        mock_client.configuration_manager = MagicMock()
        mock_client.configuration_manager.describe_device_group = AsyncMock()

        # Mock request context and lifespan context
        context.request_context = MagicMock()
        context.request_context.lifespan_context = MagicMock()
        context.request_context.lifespan_context.get.return_value = mock_client

        return context

    @pytest.mark.asyncio
    async def test_create_then_add_devices_workflow(self, mock_context):
        """Test workflow: create device group then add devices to it"""
        # Step 1: Create device group
        create_response_data = {
            "id": "workflow-group",
            "name": "Workflow Test Group",
            "message": "Created successfully",
            "status": "active",
        }

        mock_client = mock_context.request_context.lifespan_context.get.return_value
        mock_client.configuration_manager = MagicMock()
        mock_client.configuration_manager.create_device_group = AsyncMock(
            return_value=create_response_data
        )

        create_result = await device_groups.create_device_group(
            mock_context,
            name="Workflow Test Group",
            description="Test workflow integration",
            devices=[],
        )

        assert create_result.object_id == "workflow-group"
        assert create_result.status == "active"

        # Step 2: Add devices to the created group
        mock_client.configuration_manager.add_devices_to_group = AsyncMock(
            return_value={"status": "success"}
        )

        add_result = await device_groups.add_devices_to_group(
            mock_context,
            name="Workflow Test Group",
            devices=["device1", "device2", "device3"],
        )

        assert add_result.status == "success"
        assert "successfully" in add_result.message

    @pytest.mark.asyncio
    async def test_list_create_list_workflow(self, mock_context):
        """Test workflow: list groups, create new one, list again to verify"""
        mock_client = mock_context.request_context.lifespan_context.get.return_value

        # Step 1: List existing groups (empty)
        mock_client.configuration_manager = MagicMock()
        mock_client.configuration_manager.get_device_groups = AsyncMock(return_value=[])

        initial_groups = await device_groups.get_device_groups(mock_context)
        assert len(initial_groups.root) == 0

        # Step 2: Create new group
        create_response_data = {
            "id": "new-workflow-group",
            "name": "New Workflow Group",
            "message": "Created in workflow",
            "status": "active",
        }
        mock_client.configuration_manager.create_device_group = AsyncMock(
            return_value=create_response_data
        )

        create_result = await device_groups.create_device_group(
            mock_context,
            name="New Workflow Group",
            description="Created in integration test",
            devices=[],
        )

        assert create_result.object_id == "new-workflow-group"

        # Step 3: List groups again (should include new one)
        updated_data = [
            {
                "id": "new-workflow-group",
                "name": "New Workflow Group",
                "devices": [],
                "description": "Created in integration test",
            }
        ]
        mock_client.configuration_manager.get_device_groups = AsyncMock(
            return_value=updated_data
        )

        updated_groups = await device_groups.get_device_groups(mock_context)
        assert len(updated_groups.root) == 1
        assert updated_groups.root[0].name == "New Workflow Group"

    @pytest.mark.asyncio
    async def test_error_handling_consistency(self, mock_context):
        """Test that all functions handle errors consistently"""
        mock_client = mock_context.request_context.lifespan_context.get.return_value

        # Test get_device_groups with client error
        mock_client.configuration_manager = MagicMock()
        mock_client.configuration_manager.get_device_groups = AsyncMock(
            side_effect=Exception("API Error")
        )

        with pytest.raises(Exception, match="API Error"):
            await device_groups.get_device_groups(mock_context)

        # Test create_device_group with duplicate name detection
        # Reset the mock to raise an exception for duplicate detection
        mock_client.configuration_manager.create_device_group = AsyncMock(
            side_effect=ValueError("device group Existing Group already exists")
        )

        with pytest.raises(ValueError, match="already exists"):
            await device_groups.create_device_group(
                mock_context,
                name="Existing Group",
                description="Should fail",
                devices=[],
            )
