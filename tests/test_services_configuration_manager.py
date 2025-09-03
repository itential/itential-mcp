# Copyright (c) 2025 Itential, Inc
# GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)

import json
import pytest
from unittest.mock import AsyncMock, Mock

import ipsdk

from itential_mcp import exceptions
from itential_mcp.services.configuration_manager import Service
from itential_mcp.services import ServiceBase


class TestConfigurationManagerService:
    """Test cases for Configuration Manager Service class."""

    @pytest.fixture
    def mock_client(self):
        """Create a mock AsyncPlatform client."""
        return AsyncMock(spec=ipsdk.platform.AsyncPlatform)

    @pytest.fixture
    def service(self, mock_client):
        """Create a Configuration Manager Service instance."""
        return Service(mock_client)

    def test_service_inheritance(self, service):
        """Test that Service inherits from ServiceBase."""
        assert isinstance(service, ServiceBase)
        assert isinstance(service, Service)

    def test_service_name(self, service):
        """Test that service has correct name."""
        assert service.name == "configuration_manager"

    def test_service_client_assignment(self, mock_client, service):
        """Test that client is properly assigned."""
        assert service.client is mock_client

    @pytest.mark.asyncio
    async def test_get_golden_config_trees_success(self, service, mock_client):
        """Test successful retrieval of golden config trees."""
        expected_data = [
            {
                "id": "tree1-id",
                "name": "test-tree-1",
                "deviceType": "cisco_ios",
                "versions": ["v1.0", "v2.0"],
            },
            {
                "id": "tree2-id",
                "name": "test-tree-2",
                "deviceType": "juniper",
                "versions": ["initial"],
            },
        ]

        mock_response = Mock()
        mock_response.json.return_value = expected_data
        mock_client.get.return_value = mock_response

        result = await service.get_golden_config_trees()

        mock_client.get.assert_called_once_with("/configuration_manager/configs")
        assert result == expected_data

    @pytest.mark.asyncio
    async def test_get_golden_config_trees_empty_response(self, service, mock_client):
        """Test get_golden_config_trees with empty response."""
        mock_response = Mock()
        mock_response.json.return_value = []
        mock_client.get.return_value = mock_response

        result = await service.get_golden_config_trees()

        mock_client.get.assert_called_once_with("/configuration_manager/configs")
        assert result == []

    @pytest.mark.asyncio
    async def test_create_golden_config_tree_minimal(self, service, mock_client):
        """Test creating a golden config tree with minimal parameters."""
        expected_response = {
            "id": "new-tree-id",
            "name": "test-tree",
            "deviceType": "cisco_ios",
        }

        mock_response = Mock()
        mock_response.json.return_value = expected_response
        mock_client.post.return_value = mock_response

        result = await service.create_golden_config_tree(
            name="test-tree", device_type="cisco_ios"
        )

        mock_client.post.assert_called_once_with(
            "/configuration_manager/configs",
            json={"name": "test-tree", "deviceType": "cisco_ios"},
        )
        assert result == expected_response

    @pytest.mark.asyncio
    async def test_create_golden_config_tree_with_variables(self, service, mock_client):
        """Test creating a golden config tree with variables."""
        expected_response = {
            "id": "new-tree-id",
            "name": "test-tree",
            "deviceType": "cisco_ios",
        }
        variables = {"var1": "value1", "var2": "value2"}

        mock_response = Mock()
        mock_response.json.return_value = expected_response
        mock_client.post.return_value = mock_response

        result = await service.create_golden_config_tree(
            name="test-tree", device_type="cisco_ios", variables=variables
        )

        mock_client.post.assert_called_once_with(
            "/configuration_manager/configs",
            json={"name": "test-tree", "deviceType": "cisco_ios"},
        )

        mock_client.put.assert_called_once_with(
            "/configuration_manager/configs/new-tree-id/initial",
            json={"name": "initial", "variables": variables},
        )

        assert result == expected_response

    @pytest.mark.asyncio
    async def test_create_golden_config_tree_with_template(self, service, mock_client):
        """Test creating a golden config tree with template."""
        expected_response = {
            "id": "new-tree-id",
            "name": "test-tree",
            "deviceType": "cisco_ios",
        }
        template = "interface {{ interface_name }}\n description {{ description }}"

        mock_response = Mock()
        mock_response.json.return_value = expected_response
        mock_client.post.return_value = mock_response

        # Mock the set_golden_config_template method
        service.set_golden_config_template = AsyncMock(return_value={})

        result = await service.create_golden_config_tree(
            name="test-tree", device_type="cisco_ios", template=template
        )

        mock_client.post.assert_called_once_with(
            "/configuration_manager/configs",
            json={"name": "test-tree", "deviceType": "cisco_ios"},
        )

        service.set_golden_config_template.assert_called_once_with(
            "new-tree-id", "initial", template
        )

        assert result == expected_response

    @pytest.mark.asyncio
    async def test_create_golden_config_tree_with_template_and_variables(
        self, service, mock_client
    ):
        """Test creating a golden config tree with both template and variables."""
        expected_response = {
            "id": "new-tree-id",
            "name": "test-tree",
            "deviceType": "cisco_ios",
        }
        template = "interface {{ interface_name }}"
        variables = {"interface_name": "GigabitEthernet0/1"}

        mock_response = Mock()
        mock_response.json.return_value = expected_response
        mock_client.post.return_value = mock_response

        service.set_golden_config_template = AsyncMock(return_value={})

        result = await service.create_golden_config_tree(
            name="test-tree",
            device_type="cisco_ios",
            template=template,
            variables=variables,
        )

        mock_client.post.assert_called_once_with(
            "/configuration_manager/configs",
            json={"name": "test-tree", "deviceType": "cisco_ios"},
        )

        mock_client.put.assert_called_once_with(
            "/configuration_manager/configs/new-tree-id/initial",
            json={"name": "initial", "variables": variables},
        )

        service.set_golden_config_template.assert_called_once_with(
            "new-tree-id", "initial", template
        )

        assert result == expected_response

    @pytest.mark.asyncio
    async def test_create_golden_config_tree_server_error(self, service, mock_client):
        """Test create_golden_config_tree with server error."""
        error_response = {"error": "Tree name already exists"}
        server_error = ipsdk.exceptions.ServerError(
            "Server Error", details={"response_body": json.dumps(error_response)}
        )
        mock_client.post.side_effect = server_error

        with pytest.raises(exceptions.ServerException) as exc_info:
            await service.create_golden_config_tree(
                name="existing-tree", device_type="cisco_ios"
            )

        # Just verify that the ServerException was raised correctly
        assert isinstance(exc_info.value, exceptions.ServerException)

    @pytest.mark.asyncio
    async def test_describe_golden_config_tree_version(self, service, mock_client):
        """Test describing a golden config tree version."""
        expected_data = {
            "id": "tree-version-id",
            "name": "test-tree",
            "version": "v1.0",
            "root": {"attributes": {"configId": "config-123"}, "children": []},
            "variables": {"var1": "value1"},
        }

        mock_response = Mock()
        mock_response.json.return_value = expected_data
        mock_client.get.return_value = mock_response

        result = await service.describe_golden_config_tree_version("tree-id", "v1.0")

        mock_client.get.assert_called_once_with(
            "/configuration_manager/configs/tree-id/v1.0"
        )
        assert result == expected_data

    @pytest.mark.asyncio
    async def test_set_golden_config_template(self, service, mock_client):
        """Test setting a golden config template."""
        tree_version_data = {
            "root": {"attributes": {"configId": "config-123"}},
            "variables": {"var1": "value1"},
        }
        expected_response = {
            "id": "config-123",
            "template": "new template content",
            "variables": {"var1": "value1"},
        }
        template = "new template content"

        # Mock the describe_golden_config_tree_version call
        service.describe_golden_config_tree_version = AsyncMock(
            return_value=tree_version_data
        )

        mock_response = Mock()
        mock_response.json.return_value = expected_response
        mock_client.put.return_value = mock_response

        result = await service.set_golden_config_template("tree-id", "v1.0", template)

        service.describe_golden_config_tree_version.assert_called_once_with(
            tree_id="tree-id", version="v1.0"
        )

        expected_body = {
            "data": {"template": template, "variables": {"var1": "value1"}}
        }
        mock_client.put.assert_called_once_with(
            "/configuration_manager/config_specs/config-123", json=expected_body
        )

        assert result == expected_response

    @pytest.mark.asyncio
    async def test_add_golden_config_node_success(self, service, mock_client):
        """Test successfully adding a golden config node."""
        trees_data = [
            {"id": "tree-1", "name": "test-tree", "deviceType": "cisco_ios"},
            {"id": "tree-2", "name": "other-tree", "deviceType": "juniper"},
        ]
        expected_response = {
            "id": "node-123",
            "name": "interface-config",
            "path": "base/interfaces",
        }

        # Mock get_golden_config_trees
        service.get_golden_config_trees = AsyncMock(return_value=trees_data)

        mock_response = Mock()
        mock_response.json.return_value = expected_response
        mock_client.post.return_value = mock_response

        # Mock describe_golden_config_tree_version since it's called by set_golden_config_template
        service.describe_golden_config_tree_version = AsyncMock(
            return_value={
                "root": {"attributes": {"configId": "config-123"}},
                "variables": {},
            }
        )

        result = await service.add_golden_config_node(
            tree_name="test-tree",
            version="v1.0",
            path="base",
            name="interface-config",
            template="interface template",
        )

        service.get_golden_config_trees.assert_called_once()
        mock_client.post.assert_called_once_with(
            "/configuration_manager/configs/tree-1/v1.0/base",
            json={"name": "interface-config"},
        )

        assert result == expected_response

    @pytest.mark.asyncio
    async def test_add_golden_config_node_with_template(self, service, mock_client):
        """Test adding a golden config node with template."""
        trees_data = [{"id": "tree-1", "name": "test-tree", "deviceType": "cisco_ios"}]
        expected_response = {"id": "node-123", "name": "interface-config"}
        template = "interface {{ interface_name }}"

        service.get_golden_config_trees = AsyncMock(return_value=trees_data)
        service.set_golden_config_template = AsyncMock(return_value={})

        mock_response = Mock()
        mock_response.json.return_value = expected_response
        mock_client.post.return_value = mock_response

        result = await service.add_golden_config_node(
            tree_name="test-tree",
            version="v1.0",
            path="base",
            name="interface-config",
            template=template,
        )

        service.get_golden_config_trees.assert_called_once()
        mock_client.post.assert_called_once_with(
            "/configuration_manager/configs/tree-1/v1.0/base",
            json={"name": "interface-config"},
        )
        service.set_golden_config_template.assert_called_once_with(
            "tree-1", "v1.0", template
        )

        assert result == expected_response

    @pytest.mark.asyncio
    async def test_add_golden_config_node_tree_not_found(self, service):
        """Test adding a node when tree is not found."""
        trees_data = [{"id": "tree-1", "name": "other-tree", "deviceType": "cisco_ios"}]

        service.get_golden_config_trees = AsyncMock(return_value=trees_data)

        with pytest.raises(exceptions.NotFoundError) as exc_info:
            await service.add_golden_config_node(
                tree_name="non-existent-tree",
                version="v1.0",
                path="base",
                name="interface-config",
                template="template",
            )

        assert "tree non-existent-tree could not be found" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_add_golden_config_node_server_error(self, service, mock_client):
        """Test add_golden_config_node with server error."""
        trees_data = [{"id": "tree-1", "name": "test-tree", "deviceType": "cisco_ios"}]
        error_response = {"error": "Invalid node configuration"}

        service.get_golden_config_trees = AsyncMock(return_value=trees_data)

        server_error = ipsdk.exceptions.ServerError(
            "Server Error", details={"response_body": json.dumps(error_response)}
        )
        mock_client.post.side_effect = server_error

        with pytest.raises(exceptions.ServerException) as exc_info:
            await service.add_golden_config_node(
                tree_name="test-tree",
                version="v1.0",
                path="base",
                name="interface-config",
                template="template",
            )

        # Just verify that the ServerException was raised correctly
        assert isinstance(exc_info.value, exceptions.ServerException)

    @pytest.mark.asyncio
    async def test_add_golden_config_node_without_template(self, service, mock_client):
        """Test adding a golden config node without template."""
        trees_data = [{"id": "tree-1", "name": "test-tree", "deviceType": "cisco_ios"}]
        expected_response = {"id": "node-123", "name": "interface-config"}

        service.get_golden_config_trees = AsyncMock(return_value=trees_data)

        mock_response = Mock()
        mock_response.json.return_value = expected_response
        mock_client.post.return_value = mock_response

        result = await service.add_golden_config_node(
            tree_name="test-tree",
            version="v1.0",
            path="base",
            name="interface-config",
            template="",  # Empty template
        )

        service.get_golden_config_trees.assert_called_once()
        mock_client.post.assert_called_once_with(
            "/configuration_manager/configs/tree-1/v1.0/base",
            json={"name": "interface-config"},
        )

        assert result == expected_response

    @pytest.mark.asyncio
    async def test_multiple_trees_lookup(self, service):
        """Test that tree lookup works correctly with multiple trees."""
        trees_data = [
            {"id": "tree-1", "name": "cisco-tree", "deviceType": "cisco_ios"},
            {"id": "tree-2", "name": "juniper-tree", "deviceType": "juniper"},
            {"id": "tree-3", "name": "arista-tree", "deviceType": "arista_eos"},
        ]

        service.get_golden_config_trees = AsyncMock(return_value=trees_data)
        mock_response = Mock()
        mock_response.json.return_value = {"id": "node-id", "name": "test-node"}
        service.client.post = AsyncMock(return_value=mock_response)

        await service.add_golden_config_node(
            tree_name="juniper-tree",
            version="v1.0",
            path="base",
            name="test-node",
            template="",
        )

        service.client.post.assert_called_once_with(
            "/configuration_manager/configs/tree-2/v1.0/base",
            json={"name": "test-node"},
        )

    def test_service_initialization_parameters(self, mock_client):
        """Test that service can be initialized with different client types."""
        service = Service(mock_client)
        assert service.client is mock_client
        assert service.name == "configuration_manager"

    def test_service_name_attribute(self):
        """Test that the service name is set correctly as a class attribute."""
        assert Service.name == "configuration_manager"
        assert hasattr(Service, "name")

    def test_service_methods_exist(self, service):
        """Test that all required methods exist on the service."""
        assert hasattr(service, "get_golden_config_trees")
        assert hasattr(service, "create_golden_config_tree")
        assert hasattr(service, "describe_golden_config_tree_version")
        assert hasattr(service, "set_golden_config_template")
        assert hasattr(service, "add_golden_config_node")
        assert hasattr(service, "describe_device_group")
        assert hasattr(service, "get_device_groups")
        assert hasattr(service, "create_device_group")
        assert hasattr(service, "add_devices_to_group")
        assert hasattr(service, "remove_devices_from_group")

    def test_service_methods_are_async(self, service):
        """Test that all service methods are async."""
        import asyncio

        assert asyncio.iscoroutinefunction(service.get_golden_config_trees)
        assert asyncio.iscoroutinefunction(service.create_golden_config_tree)
        assert asyncio.iscoroutinefunction(service.describe_golden_config_tree_version)
        assert asyncio.iscoroutinefunction(service.set_golden_config_template)
        assert asyncio.iscoroutinefunction(service.add_golden_config_node)
        assert asyncio.iscoroutinefunction(service.describe_device_group)
        assert asyncio.iscoroutinefunction(service.get_device_groups)
        assert asyncio.iscoroutinefunction(service.create_device_group)
        assert asyncio.iscoroutinefunction(service.add_devices_to_group)
        assert asyncio.iscoroutinefunction(service.remove_devices_from_group)


class TestConfigurationManagerDeviceGroups:
    """Test cases for Configuration Manager Device Group methods."""

    @pytest.fixture
    def mock_client(self):
        """Create a mock AsyncPlatform client."""
        return AsyncMock(spec=ipsdk.platform.AsyncPlatform)

    @pytest.fixture
    def service(self, mock_client):
        """Create a Configuration Manager Service instance."""
        return Service(mock_client)

    @pytest.mark.asyncio
    async def test_describe_device_group_success(self, service, mock_client):
        """Test successful device group description retrieval."""
        expected_data = {
            "id": "group-123",
            "name": "Production Routers",
            "devices": ["router1", "router2", "router3"],
            "description": "Production network routers"
        }

        mock_response = Mock()
        mock_response.json.return_value = expected_data
        mock_client._send_request.return_value = mock_response

        result = await service.describe_device_group("Production Routers")

        mock_client._send_request.assert_called_once_with(
            "GET",
            "/configuration_manager/name/devicegroups",
            json={"groupName": "Production Routers"}
        )
        assert result == expected_data

    @pytest.mark.asyncio
    async def test_describe_device_group_empty_devices(self, service, mock_client):
        """Test describing a device group with empty devices list."""
        expected_data = {
            "id": "group-456",
            "name": "Empty Group",
            "devices": [],
            "description": "Group with no devices"
        }

        mock_response = Mock()
        mock_response.json.return_value = expected_data
        mock_client._send_request.return_value = mock_response

        result = await service.describe_device_group("Empty Group")

        mock_client._send_request.assert_called_once_with(
            "GET",
            "/configuration_manager/name/devicegroups",
            json={"groupName": "Empty Group"}
        )
        assert result == expected_data
        assert result["devices"] == []

    @pytest.mark.asyncio
    async def test_get_device_groups_success(self, service, mock_client):
        """Test successful retrieval of all device groups."""
        expected_data = [
            {
                "id": "group-1",
                "name": "Production Routers",
                "devices": ["router1", "router2", "router3"],
                "description": "Production network routers"
            },
            {
                "id": "group-2", 
                "name": "Test Switches",
                "devices": ["switch1", "switch2"],
                "description": "Test environment switches"
            }
        ]

        mock_response = Mock()
        mock_response.json.return_value = expected_data
        mock_client.get.return_value = mock_response

        result = await service.get_device_groups()

        mock_client.get.assert_called_once_with("/configuration_manager/deviceGroups")
        assert result == expected_data
        assert len(result) == 2

    @pytest.mark.asyncio
    async def test_get_device_groups_empty_response(self, service, mock_client):
        """Test get_device_groups with empty response."""
        mock_response = Mock()
        mock_response.json.return_value = []
        mock_client.get.return_value = mock_response

        result = await service.get_device_groups()

        mock_client.get.assert_called_once_with("/configuration_manager/deviceGroups")
        assert result == []

    @pytest.mark.asyncio
    async def test_create_device_group_success(self, service, mock_client):
        """Test successful device group creation."""
        # Mock get_device_groups to return existing groups (for duplicate check)
        existing_groups = [
            {"id": "group-1", "name": "Existing Group", "devices": [], "description": "Already exists"}
        ]
        service.get_device_groups = AsyncMock(return_value=existing_groups)

        expected_response = {
            "id": "new-group-123",
            "name": "New Production Group",
            "message": "Device group created successfully",
            "status": "active"
        }

        mock_response = Mock()
        mock_response.json.return_value = expected_response
        mock_client.post.return_value = mock_response

        result = await service.create_device_group(
            name="New Production Group",
            devices=["router1", "router2"],
            description="A new production device group"
        )

        # Verify duplicate check was performed
        service.get_device_groups.assert_called_once()

        # Verify API call
        expected_body = {
            "groupName": "New Production Group",
            "groupDescription": "A new production device group",
            "deviceNames": "router1,router2"
        }
        mock_client.post.assert_called_once_with(
            "/configuration_manager/devicegroup",
            json=expected_body
        )

        assert result == expected_response

    @pytest.mark.asyncio
    async def test_create_device_group_no_devices(self, service, mock_client):
        """Test creating device group with no devices."""
        service.get_device_groups = AsyncMock(return_value=[])

        expected_response = {
            "id": "empty-group-456",
            "name": "Empty Group", 
            "message": "Empty device group created",
            "status": "active"
        }

        mock_response = Mock()
        mock_response.json.return_value = expected_response
        mock_client.post.return_value = mock_response

        result = await service.create_device_group(
            name="Empty Group",
            devices=[],
            description="An empty device group"
        )

        # Verify empty deviceNames was sent
        expected_body = {
            "groupName": "Empty Group",
            "groupDescription": "An empty device group",
            "deviceNames": ""
        }
        mock_client.post.assert_called_once_with(
            "/configuration_manager/devicegroup",
            json=expected_body
        )

        assert result == expected_response

    @pytest.mark.asyncio
    async def test_create_device_group_no_description(self, service, mock_client):
        """Test creating device group with no description."""
        service.get_device_groups = AsyncMock(return_value=[])

        expected_response = {
            "id": "no-desc-group",
            "name": "No Description Group",
            "message": "Group created without description",
            "status": "active"
        }

        mock_response = Mock()
        mock_response.json.return_value = expected_response
        mock_client.post.return_value = mock_response

        result = await service.create_device_group(
            name="No Description Group",
            devices=["device1", "device2"]
        )

        # Verify None description was passed
        expected_body = {
            "groupName": "No Description Group",
            "groupDescription": None,
            "deviceNames": "device1,device2"
        }
        mock_client.post.assert_called_once_with(
            "/configuration_manager/devicegroup",
            json=expected_body
        )

        assert result == expected_response

    @pytest.mark.asyncio
    async def test_create_device_group_duplicate_name_error(self, service, mock_client):
        """Test creating device group with duplicate name raises error."""
        # Mock get_device_groups to return existing group with same name
        existing_groups = [
            {"id": "existing-123", "name": "Existing Group", "devices": ["device1"], "description": "Already exists"}
        ]
        service.get_device_groups = AsyncMock(return_value=existing_groups)

        with pytest.raises(ValueError, match="device group Existing Group already exists"):
            await service.create_device_group(
                name="Existing Group",
                devices=["device2"],
                description="Duplicate group"
            )

        # Verify get_device_groups was called but post was not
        service.get_device_groups.assert_called_once()
        mock_client.post.assert_not_called()

    @pytest.mark.asyncio
    async def test_add_devices_to_group_success(self, service, mock_client):
        """Test successfully adding devices to a group."""
        # Mock describe_device_group response
        mock_group_data = {
            "id": "group-123",
            "name": "Test Group",
            "devices": ["device1"],
            "description": "Test device group"
        }

        service.describe_device_group = AsyncMock(return_value=mock_group_data)

        expected_response = {"status": "success"}
        mock_response = Mock()
        mock_response.json.return_value = expected_response
        mock_client.put.return_value = mock_response

        result = await service.add_devices_to_group(
            name="Test Group",
            devices=["device1", "device2", "device3"]
        )

        # Verify describe_device_group was called
        service.describe_device_group.assert_called_once_with("Test Group")

        # Verify API call
        expected_body = {
            "details": {
                "devices": ["device1", "device2", "device3"]
            }
        }
        mock_client.put.assert_called_once_with(
            "/configuration_manager/deviceGroups/group-123",
            json=expected_body
        )

        assert result == expected_response

    @pytest.mark.asyncio
    async def test_add_devices_to_group_empty_list(self, service, mock_client):
        """Test adding empty devices list to a group."""
        mock_group_data = {
            "id": "group-789",
            "name": "Empty Add Group", 
            "devices": ["device1"],
            "description": "Test group"
        }

        service.describe_device_group = AsyncMock(return_value=mock_group_data)

        expected_response = {"status": "success"}
        mock_response = Mock()
        mock_response.json.return_value = expected_response
        mock_client.put.return_value = mock_response

        result = await service.add_devices_to_group(
            name="Empty Add Group",
            devices=[]
        )

        # Verify empty devices list was handled
        expected_body = {
            "details": {
                "devices": []
            }
        }
        mock_client.put.assert_called_once_with(
            "/configuration_manager/deviceGroups/group-789",
            json=expected_body
        )

        assert result == expected_response

    @pytest.mark.asyncio
    async def test_remove_devices_from_group_success(self, service, mock_client):
        """Test successfully removing devices from a group."""
        # Mock describe_device_group response
        mock_group_data = {
            "id": "group-123",
            "devices": ["device1", "device2", "device3", "device4", "device5"]
        }

        service.describe_device_group = AsyncMock(return_value=mock_group_data)

        expected_response = {"status": "success"}
        mock_response = Mock()
        mock_response.json.return_value = expected_response
        mock_client.put.return_value = mock_response

        result = await service.remove_devices_from_group(
            name="Test Group",
            devices=["device2", "device4"]  # Remove 2 devices
        )

        # Verify describe_device_group was called
        service.describe_device_group.assert_called_once_with("Test Group")

        # Verify API call - should contain remaining devices
        expected_body = {
            "details": {
                "devices": ["device1", "device3", "device5"]  # Remaining devices
            }
        }
        mock_client.put.assert_called_once_with(
            "/configuration_manager/deviceGroups/group-123",
            json=expected_body
        )

        assert result == expected_response

    @pytest.mark.asyncio
    async def test_remove_devices_from_group_remove_all(self, service, mock_client):
        """Test removing all devices from a group."""
        mock_group_data = {
            "id": "group-456",
            "devices": ["device1", "device2"]
        }

        service.describe_device_group = AsyncMock(return_value=mock_group_data)

        expected_response = {"status": "success"}
        mock_response = Mock()
        mock_response.json.return_value = expected_response
        mock_client.put.return_value = mock_response

        result = await service.remove_devices_from_group(
            name="Empty Group",
            devices=["device1", "device2"]  # Remove all devices
        )

        # Verify empty devices list was sent
        expected_body = {
            "details": {
                "devices": []  # No remaining devices
            }
        }
        mock_client.put.assert_called_once_with(
            "/configuration_manager/deviceGroups/group-456",
            json=expected_body
        )

        assert result == expected_response

    @pytest.mark.asyncio
    async def test_remove_devices_from_group_nonexistent_devices(self, service, mock_client):
        """Test removing devices that are not in the group."""
        mock_group_data = {
            "id": "group-789",
            "devices": ["device1", "device2", "device3"]
        }

        service.describe_device_group = AsyncMock(return_value=mock_group_data)

        expected_response = {"status": "success"}
        mock_response = Mock()
        mock_response.json.return_value = expected_response
        mock_client.put.return_value = mock_response

        result = await service.remove_devices_from_group(
            name="Test Group",
            devices=["device4", "device5"]  # Devices not in group
        )

        # Verify all original devices remain (no devices actually removed)
        expected_body = {
            "details": {
                "devices": ["device1", "device2", "device3"]  # All original devices remain
            }
        }
        mock_client.put.assert_called_once_with(
            "/configuration_manager/deviceGroups/group-789", 
            json=expected_body
        )

        assert result == expected_response

    @pytest.mark.asyncio 
    async def test_remove_devices_from_group_partial_removal(self, service, mock_client):
        """Test removing devices with partial matches."""
        mock_group_data = {
            "id": "group-mixed",
            "devices": ["device1", "device2", "device3", "device4"]
        }

        service.describe_device_group = AsyncMock(return_value=mock_group_data)

        expected_response = {"status": "partial"}
        mock_response = Mock()
        mock_response.json.return_value = expected_response
        mock_client.put.return_value = mock_response

        result = await service.remove_devices_from_group(
            name="Mixed Group",
            devices=["device2", "device5"]  # device2 exists, device5 doesn't
        )

        # Verify only device2 was removed from the list
        expected_body = {
            "details": {
                "devices": ["device1", "device3", "device4"]  # device2 removed, device5 wasn't there
            }
        }
        mock_client.put.assert_called_once_with(
            "/configuration_manager/deviceGroups/group-mixed",
            json=expected_body
        )

        assert result == expected_response

    @pytest.mark.asyncio
    async def test_remove_devices_from_group_empty_group(self, service, mock_client):
        """Test removing devices from empty group."""
        mock_group_data = {
            "id": "empty-group",
            "devices": []
        }

        service.describe_device_group = AsyncMock(return_value=mock_group_data)

        expected_response = {"status": "warning"}
        mock_response = Mock()
        mock_response.json.return_value = expected_response
        mock_client.put.return_value = mock_response

        result = await service.remove_devices_from_group(
            name="Empty Group",
            devices=["device1"]
        )

        # Verify empty devices list remains empty
        expected_body = {
            "details": {
                "devices": []
            }
        }
        mock_client.put.assert_called_once_with(
            "/configuration_manager/deviceGroups/empty-group",
            json=expected_body
        )

        assert result == expected_response

    @pytest.mark.asyncio
    async def test_device_groups_error_handling(self, service, mock_client):
        """Test error handling for device group operations."""
        # Test client error in get_device_groups
        mock_client.get.side_effect = Exception("API Error")

        with pytest.raises(Exception, match="API Error"):
            await service.get_device_groups()

        # Reset side effect for other operations
        mock_client.get.side_effect = None

        # Test client error in describe_device_group
        mock_client._send_request.side_effect = Exception("Group not found")

        with pytest.raises(Exception, match="Group not found"):
            await service.describe_device_group("NonExistent Group")

    @pytest.mark.asyncio
    async def test_device_group_integration_workflow(self, service, mock_client):
        """Test integration workflow: create group, add devices, remove devices."""
        # Step 1: Create device group
        service.get_device_groups = AsyncMock(return_value=[])  # No existing groups

        create_response = {"id": "workflow-group", "name": "Workflow Test Group", "message": "Created successfully", "status": "active"}
        mock_response = Mock()
        mock_response.json.return_value = create_response
        mock_client.post.return_value = mock_response

        create_result = await service.create_device_group(
            name="Workflow Test Group",
            devices=["device1"],
            description="Test workflow integration"
        )

        assert create_result["id"] == "workflow-group"

        # Step 2: Add more devices to the created group
        service.describe_device_group = AsyncMock(return_value={"id": "workflow-group", "devices": ["device1"]})

        add_response = {"status": "success"}
        mock_response.json.return_value = add_response
        mock_client.put.return_value = mock_response

        add_result = await service.add_devices_to_group(
            name="Workflow Test Group", 
            devices=["device1", "device2", "device3"]
        )

        assert add_result["status"] == "success"

        # Step 3: Remove a device from the group
        service.describe_device_group = AsyncMock(return_value={"id": "workflow-group", "devices": ["device1", "device2", "device3"]})

        remove_response = {"status": "success"}
        mock_response.json.return_value = remove_response

        remove_result = await service.remove_devices_from_group(
            name="Workflow Test Group",
            devices=["device2"]
        )

        assert remove_result["status"] == "success"

        # Verify the final put call had correct remaining devices
        expected_body = {
            "details": {
                "devices": ["device1", "device3"]  # device2 removed
            }
        }
        mock_client.put.assert_called_with(
            "/configuration_manager/deviceGroups/workflow-group",
            json=expected_body
        )
