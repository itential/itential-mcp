# Copyright (c) 2025 Itential, Inc
# GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

import pytest
from unittest.mock import AsyncMock, Mock

import httpx
import ipsdk

from itential_mcp.core import exceptions
from itential_mcp.platform.services.configuration_manager import Service
from itential_mcp.platform.services import ServiceBase


class TestConfigurationManagerService:
    """
    Comprehensive test cases for Configuration Manager Service class.

    This test class covers all core functionality of the Configuration Manager
    service, including Golden Configuration tree management, service inheritance,
    client configuration, and method validation. Tests ensure proper API
    interactions and error handling for all Configuration Manager operations.
    """

    @pytest.fixture
    def mock_client(self):
        """
        Create a mock AsyncPlatform client for Configuration Manager tests.

        Returns:
            AsyncMock: Mocked ipsdk.platform.AsyncPlatform instance configured
                      with proper specifications for testing Configuration Manager
                      API interactions including GET, POST, PUT operations.
        """
        return AsyncMock(spec=ipsdk.platform.AsyncPlatform)

    @pytest.fixture
    def service(self, mock_client):
        """
        Create a Configuration Manager Service instance for testing.

        Args:
            mock_client: Mocked AsyncPlatform client fixture.

        Returns:
            Service: Configuration Manager service instance configured with
                    the mocked client for testing all service operations
                    including Golden Config trees and device groups.
        """
        return Service(mock_client)

    def test_service_inheritance(self, service):
        """
        Test that Configuration Manager Service inherits from ServiceBase correctly.

        Validates proper inheritance hierarchy ensuring that the Configuration
        Manager service extends the base service functionality and maintains
        the expected class relationships for the service architecture.
        """
        assert isinstance(service, ServiceBase)
        assert isinstance(service, Service)

    def test_service_name(self, service):
        """
        Test that service has the correct identifier name.

        Validates that the service name matches the expected identifier used
        by the platform for routing and service discovery. The name must be
        consistent across the service implementation and registration.
        """
        assert service.name == "configuration_manager"

    def test_service_client_assignment(self, mock_client, service):
        """
        Test that the HTTP client is properly assigned to the service instance.

        Validates that the AsyncPlatform client is correctly injected into
        the service during initialization, enabling the service to make
        API calls to the Configuration Manager endpoints.
        """
        assert service.client is mock_client

    @pytest.mark.asyncio
    async def test_get_golden_config_trees_success(self, service, mock_client):
        """
        Test successful retrieval of Golden Configuration trees from the platform.

        Validates that the service correctly calls the Configuration Manager API
        to retrieve all available Golden Configuration trees and returns the
        expected data structure containing tree metadata, IDs, names, device
        types, and version information for network device configuration templates.
        """
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
    async def test_get_configuration_parser_names_success(self, service, mock_client):
        """Test successful retrieval of configuration parser names."""
        expected_parsers = [
            {"name": "cisco_ios"},
            {"name": "juniper"},
            {"name": "arista_eos"},
        ]

        mock_response = Mock()
        mock_response.json.return_value = {"list": expected_parsers}
        mock_client.get.return_value = mock_response

        result = await service.get_configuration_parser_names()

        mock_client.get.assert_called_once_with(
            "/configuration_manager/configurations/parser"
        )
        assert result == ["cisco_ios", "juniper", "arista_eos"]

    @pytest.mark.asyncio
    async def test_get_configuration_parser_names_empty(self, service, mock_client):
        """Test get_configuration_parser_names with empty list."""
        mock_response = Mock()
        mock_response.json.return_value = {"list": []}
        mock_client.get.return_value = mock_response

        result = await service.get_configuration_parser_names()

        mock_client.get.assert_called_once_with(
            "/configuration_manager/configurations/parser"
        )
        assert result == []

    @pytest.mark.asyncio
    async def test_create_golden_config_tree_minimal(self, service, mock_client):
        """Test creating a golden config tree with minimal parameters."""
        expected_response = {
            "id": "new-tree-id",
            "name": "test-tree",
            "deviceType": "cisco_ios",
        }

        # Mock the parser endpoint for device type validation
        parser_mock_response = Mock()
        parser_mock_response.json.return_value = {
            "list": [{"name": "cisco_ios"}, {"name": "juniper"}]
        }
        mock_client.get.return_value = parser_mock_response

        mock_response = Mock()
        mock_response.json.return_value = expected_response
        mock_client.post.return_value = mock_response

        result = await service.create_golden_config_tree(
            name="test-tree", device_type="cisco_ios"
        )

        mock_client.get.assert_called_once_with(
            "/configuration_manager/configurations/parser"
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

        # Mock the parser endpoint for device type validation
        parser_mock_response = Mock()
        parser_mock_response.json.return_value = {
            "list": [{"name": "cisco_ios"}, {"name": "juniper"}]
        }
        mock_client.get.return_value = parser_mock_response

        mock_response = Mock()
        mock_response.json.return_value = expected_response
        mock_client.post.return_value = mock_response

        result = await service.create_golden_config_tree(
            name="test-tree", device_type="cisco_ios", variables=variables
        )

        mock_client.get.assert_called_once_with(
            "/configuration_manager/configurations/parser"
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

        # Mock the parser endpoint for device type validation
        parser_mock_response = Mock()
        parser_mock_response.json.return_value = {
            "list": [{"name": "cisco_ios"}, {"name": "juniper"}]
        }
        mock_client.get.return_value = parser_mock_response

        mock_response = Mock()
        mock_response.json.return_value = expected_response
        mock_client.post.return_value = mock_response

        # Mock the set_golden_config_template method
        service.set_golden_config_template = AsyncMock(return_value={})

        result = await service.create_golden_config_tree(
            name="test-tree", device_type="cisco_ios", template=template
        )

        mock_client.get.assert_called_once_with(
            "/configuration_manager/configurations/parser"
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

        # Mock the parser endpoint for device type validation
        parser_mock_response = Mock()
        parser_mock_response.json.return_value = {
            "list": [{"name": "cisco_ios"}, {"name": "juniper"}]
        }
        mock_client.get.return_value = parser_mock_response

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

        mock_client.get.assert_called_once_with(
            "/configuration_manager/configurations/parser"
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
        # Mock the parser endpoint for device type validation
        parser_mock_response = Mock()
        parser_mock_response.json.return_value = {
            "list": [{"name": "cisco_ios"}, {"name": "juniper"}]
        }
        mock_client.get.return_value = parser_mock_response

        error_response = {"error": "Tree name already exists"}
        # Create a proper HTTPStatusError with response
        request = httpx.Request("POST", "http://example.com/api")
        response = httpx.Response(500, json=error_response)
        http_error = httpx.HTTPStatusError(
            "Server Error", request=request, response=response
        )
        server_error = ipsdk.exceptions.HTTPStatusError(http_error)
        mock_client.post.side_effect = server_error

        with pytest.raises(exceptions.ServerException) as exc_info:
            await service.create_golden_config_tree(
                name="existing-tree", device_type="cisco_ios"
            )

        # Just verify that the ServerException was raised correctly
        assert isinstance(exc_info.value, exceptions.ServerException)

    @pytest.mark.asyncio
    async def test_create_golden_config_tree_invalid_device_type(
        self, service, mock_client
    ):
        """Test create_golden_config_tree with invalid device type."""
        # Mock the parser endpoint with valid device types
        parser_mock_response = Mock()
        parser_mock_response.json.return_value = {
            "list": [{"name": "cisco_ios"}, {"name": "juniper"}]
        }
        mock_client.get.return_value = parser_mock_response

        with pytest.raises(ValueError) as exc_info:
            await service.create_golden_config_tree(
                name="test-tree", device_type="invalid_device"
            )

        # Verify the error message contains the invalid type and valid types
        assert "invalid_device" in str(exc_info.value)
        assert "cisco_ios" in str(exc_info.value)
        assert "juniper" in str(exc_info.value)

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

        # Mock client.put for set_golden_config_template
        mock_put_response = Mock()
        mock_put_response.json.return_value = {"template": "interface template"}
        mock_client.put = AsyncMock(return_value=mock_put_response)

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

        # Create a proper HTTPStatusError with response
        request = httpx.Request("POST", "http://example.com/api")
        response = httpx.Response(500, json=error_response)
        http_error = httpx.HTTPStatusError(
            "Server Error", request=request, response=response
        )
        server_error = ipsdk.exceptions.HTTPStatusError(http_error)
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
        assert hasattr(service, "describe_compliance_report")
        assert hasattr(service, "get_devices")
        assert hasattr(service, "get_device_configuration")
        assert hasattr(service, "backup_device_configuration")
        assert hasattr(service, "apply_device_configuration")
        assert hasattr(service, "render_template")
        assert hasattr(service, "get_compliance_plans")
        assert hasattr(service, "run_compliance_plan")

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
        assert asyncio.iscoroutinefunction(service.describe_compliance_report)
        assert asyncio.iscoroutinefunction(service.get_devices)
        assert asyncio.iscoroutinefunction(service.get_device_configuration)
        assert asyncio.iscoroutinefunction(service.backup_device_configuration)
        assert asyncio.iscoroutinefunction(service.apply_device_configuration)
        assert asyncio.iscoroutinefunction(service.render_template)
        assert asyncio.iscoroutinefunction(service.get_compliance_plans)
        assert asyncio.iscoroutinefunction(service.run_compliance_plan)


class TestConfigurationManagerDeviceGroups:
    """
    Comprehensive test cases for Configuration Manager Device Group operations.

    This test class focuses on device group management functionality within
    the Configuration Manager service. Tests cover device group creation,
    modification, device addition/removal, error handling, and integration
    workflows. Device groups are logical collections that enable bulk
    management of network devices for configuration and automation tasks.
    """

    @pytest.fixture
    def mock_client(self):
        """
        Create a mock AsyncPlatform client for device group tests.

        Returns:
            AsyncMock: Mocked ipsdk.platform.AsyncPlatform instance configured
                      for testing device group API operations including creating
                      groups, adding/removing devices, and retrieving group data.
        """
        return AsyncMock(spec=ipsdk.platform.AsyncPlatform)

    @pytest.fixture
    def service(self, mock_client):
        """
        Create a Configuration Manager Service instance for device group tests.

        Args:
            mock_client: Mocked AsyncPlatform client fixture.

        Returns:
            Service: Configuration Manager service instance configured with
                    the mocked client for testing device group management
                    operations and API interactions.
        """
        return Service(mock_client)

    @pytest.mark.asyncio
    async def test_describe_device_group_success(self, service, mock_client):
        """Test successful device group description retrieval."""
        expected_data = {
            "id": "group-123",
            "name": "Production Routers",
            "devices": ["router1", "router2", "router3"],
            "description": "Production network routers",
        }

        mock_response = Mock()
        mock_response.json.return_value = expected_data
        mock_client._send_request.return_value = mock_response

        result = await service.describe_device_group("Production Routers")

        mock_client._send_request.assert_called_once_with(
            "GET",
            "/configuration_manager/name/devicegroups",
            json={"groupName": "Production Routers"},
        )
        assert result == expected_data

    @pytest.mark.asyncio
    async def test_describe_device_group_empty_devices(self, service, mock_client):
        """Test describing a device group with empty devices list."""
        expected_data = {
            "id": "group-456",
            "name": "Empty Group",
            "devices": [],
            "description": "Group with no devices",
        }

        mock_response = Mock()
        mock_response.json.return_value = expected_data
        mock_client._send_request.return_value = mock_response

        result = await service.describe_device_group("Empty Group")

        mock_client._send_request.assert_called_once_with(
            "GET",
            "/configuration_manager/name/devicegroups",
            json={"groupName": "Empty Group"},
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
                "description": "Production network routers",
            },
            {
                "id": "group-2",
                "name": "Test Switches",
                "devices": ["switch1", "switch2"],
                "description": "Test environment switches",
            },
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
            {
                "id": "group-1",
                "name": "Existing Group",
                "devices": [],
                "description": "Already exists",
            }
        ]
        service.get_device_groups = AsyncMock(return_value=existing_groups)

        expected_response = {
            "id": "new-group-123",
            "name": "New Production Group",
            "message": "Device group created successfully",
            "status": "active",
        }

        mock_response = Mock()
        mock_response.json.return_value = expected_response
        mock_client.post.return_value = mock_response

        result = await service.create_device_group(
            name="New Production Group",
            devices=["router1", "router2"],
            description="A new production device group",
        )

        # Verify duplicate check was performed
        service.get_device_groups.assert_called_once()

        # Verify API call
        expected_body = {
            "groupName": "New Production Group",
            "groupDescription": "A new production device group",
            "deviceNames": "router1,router2",
        }
        mock_client.post.assert_called_once_with(
            "/configuration_manager/devicegroup", json=expected_body
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
            "status": "active",
        }

        mock_response = Mock()
        mock_response.json.return_value = expected_response
        mock_client.post.return_value = mock_response

        result = await service.create_device_group(
            name="Empty Group", devices=[], description="An empty device group"
        )

        # Verify empty deviceNames was sent
        expected_body = {
            "groupName": "Empty Group",
            "groupDescription": "An empty device group",
            "deviceNames": "",
        }
        mock_client.post.assert_called_once_with(
            "/configuration_manager/devicegroup", json=expected_body
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
            "status": "active",
        }

        mock_response = Mock()
        mock_response.json.return_value = expected_response
        mock_client.post.return_value = mock_response

        result = await service.create_device_group(
            name="No Description Group", devices=["device1", "device2"]
        )

        # Verify None description was passed
        expected_body = {
            "groupName": "No Description Group",
            "groupDescription": None,
            "deviceNames": "device1,device2",
        }
        mock_client.post.assert_called_once_with(
            "/configuration_manager/devicegroup", json=expected_body
        )

        assert result == expected_response

    @pytest.mark.asyncio
    async def test_create_device_group_duplicate_name_error(self, service, mock_client):
        """Test creating device group with duplicate name raises error."""
        # Mock get_device_groups to return existing group with same name
        existing_groups = [
            {
                "id": "existing-123",
                "name": "Existing Group",
                "devices": ["device1"],
                "description": "Already exists",
            }
        ]
        service.get_device_groups = AsyncMock(return_value=existing_groups)

        with pytest.raises(
            ValueError, match="device group Existing Group already exists"
        ):
            await service.create_device_group(
                name="Existing Group",
                devices=["device2"],
                description="Duplicate group",
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
            "description": "Test device group",
        }

        service.describe_device_group = AsyncMock(return_value=mock_group_data)

        expected_response = {"status": "success"}
        mock_response = Mock()
        mock_response.json.return_value = expected_response
        mock_client.put.return_value = mock_response

        result = await service.add_devices_to_group(
            name="Test Group", devices=["device1", "device2", "device3"]
        )

        # Verify describe_device_group was called
        service.describe_device_group.assert_called_once_with("Test Group")

        # Verify API call
        expected_body = {"details": {"devices": ["device1", "device2", "device3"]}}
        mock_client.put.assert_called_once_with(
            "/configuration_manager/deviceGroups/group-123", json=expected_body
        )

        assert result == expected_response

    @pytest.mark.asyncio
    async def test_add_devices_to_group_empty_list(self, service, mock_client):
        """Test adding empty devices list to a group."""
        mock_group_data = {
            "id": "group-789",
            "name": "Empty Add Group",
            "devices": ["device1"],
            "description": "Test group",
        }

        service.describe_device_group = AsyncMock(return_value=mock_group_data)

        expected_response = {"status": "success"}
        mock_response = Mock()
        mock_response.json.return_value = expected_response
        mock_client.put.return_value = mock_response

        result = await service.add_devices_to_group(name="Empty Add Group", devices=[])

        # Verify empty devices list was handled
        expected_body = {"details": {"devices": []}}
        mock_client.put.assert_called_once_with(
            "/configuration_manager/deviceGroups/group-789", json=expected_body
        )

        assert result == expected_response

    @pytest.mark.asyncio
    async def test_remove_devices_from_group_success(self, service, mock_client):
        """Test successfully removing devices from a group."""
        # Mock describe_device_group response
        mock_group_data = {
            "id": "group-123",
            "devices": ["device1", "device2", "device3", "device4", "device5"],
        }

        service.describe_device_group = AsyncMock(return_value=mock_group_data)

        expected_response = {"status": "success"}
        mock_response = Mock()
        mock_response.json.return_value = expected_response
        mock_client.put.return_value = mock_response

        result = await service.remove_devices_from_group(
            name="Test Group",
            devices=["device2", "device4"],  # Remove 2 devices
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
            "/configuration_manager/deviceGroups/group-123", json=expected_body
        )

        assert result == expected_response

    @pytest.mark.asyncio
    async def test_remove_devices_from_group_remove_all(self, service, mock_client):
        """Test removing all devices from a group."""
        mock_group_data = {"id": "group-456", "devices": ["device1", "device2"]}

        service.describe_device_group = AsyncMock(return_value=mock_group_data)

        expected_response = {"status": "success"}
        mock_response = Mock()
        mock_response.json.return_value = expected_response
        mock_client.put.return_value = mock_response

        result = await service.remove_devices_from_group(
            name="Empty Group",
            devices=["device1", "device2"],  # Remove all devices
        )

        # Verify empty devices list was sent
        expected_body = {
            "details": {
                "devices": []  # No remaining devices
            }
        }
        mock_client.put.assert_called_once_with(
            "/configuration_manager/deviceGroups/group-456", json=expected_body
        )

        assert result == expected_response

    @pytest.mark.asyncio
    async def test_remove_devices_from_group_nonexistent_devices(
        self, service, mock_client
    ):
        """Test removing devices that are not in the group."""
        mock_group_data = {
            "id": "group-789",
            "devices": ["device1", "device2", "device3"],
        }

        service.describe_device_group = AsyncMock(return_value=mock_group_data)

        expected_response = {"status": "success"}
        mock_response = Mock()
        mock_response.json.return_value = expected_response
        mock_client.put.return_value = mock_response

        result = await service.remove_devices_from_group(
            name="Test Group",
            devices=["device4", "device5"],  # Devices not in group
        )

        # Verify all original devices remain (no devices actually removed)
        expected_body = {
            "details": {
                "devices": [
                    "device1",
                    "device2",
                    "device3",
                ]  # All original devices remain
            }
        }
        mock_client.put.assert_called_once_with(
            "/configuration_manager/deviceGroups/group-789", json=expected_body
        )

        assert result == expected_response

    @pytest.mark.asyncio
    async def test_remove_devices_from_group_partial_removal(
        self, service, mock_client
    ):
        """Test removing devices with partial matches."""
        mock_group_data = {
            "id": "group-mixed",
            "devices": ["device1", "device2", "device3", "device4"],
        }

        service.describe_device_group = AsyncMock(return_value=mock_group_data)

        expected_response = {"status": "partial"}
        mock_response = Mock()
        mock_response.json.return_value = expected_response
        mock_client.put.return_value = mock_response

        result = await service.remove_devices_from_group(
            name="Mixed Group",
            devices=["device2", "device5"],  # device2 exists, device5 doesn't
        )

        # Verify only device2 was removed from the list
        expected_body = {
            "details": {
                "devices": [
                    "device1",
                    "device3",
                    "device4",
                ]  # device2 removed, device5 wasn't there
            }
        }
        mock_client.put.assert_called_once_with(
            "/configuration_manager/deviceGroups/group-mixed", json=expected_body
        )

        assert result == expected_response

    @pytest.mark.asyncio
    async def test_remove_devices_from_group_empty_group(self, service, mock_client):
        """Test removing devices from empty group."""
        mock_group_data = {"id": "empty-group", "devices": []}

        service.describe_device_group = AsyncMock(return_value=mock_group_data)

        expected_response = {"status": "warning"}
        mock_response = Mock()
        mock_response.json.return_value = expected_response
        mock_client.put.return_value = mock_response

        result = await service.remove_devices_from_group(
            name="Empty Group", devices=["device1"]
        )

        # Verify empty devices list remains empty
        expected_body = {"details": {"devices": []}}
        mock_client.put.assert_called_once_with(
            "/configuration_manager/deviceGroups/empty-group", json=expected_body
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

        create_response = {
            "id": "workflow-group",
            "name": "Workflow Test Group",
            "message": "Created successfully",
            "status": "active",
        }
        mock_response = Mock()
        mock_response.json.return_value = create_response
        mock_client.post.return_value = mock_response

        create_result = await service.create_device_group(
            name="Workflow Test Group",
            devices=["device1"],
            description="Test workflow integration",
        )

        assert create_result["id"] == "workflow-group"

        # Step 2: Add more devices to the created group
        service.describe_device_group = AsyncMock(
            return_value={"id": "workflow-group", "devices": ["device1"]}
        )

        add_response = {"status": "success"}
        mock_response.json.return_value = add_response
        mock_client.put.return_value = mock_response

        add_result = await service.add_devices_to_group(
            name="Workflow Test Group", devices=["device1", "device2", "device3"]
        )

        assert add_result["status"] == "success"

        # Step 3: Remove a device from the group
        service.describe_device_group = AsyncMock(
            return_value={
                "id": "workflow-group",
                "devices": ["device1", "device2", "device3"],
            }
        )

        remove_response = {"status": "success"}
        mock_response.json.return_value = remove_response

        remove_result = await service.remove_devices_from_group(
            name="Workflow Test Group", devices=["device2"]
        )

        assert remove_result["status"] == "success"

        # Verify the final put call had correct remaining devices
        expected_body = {
            "details": {
                "devices": ["device1", "device3"]  # device2 removed
            }
        }
        mock_client.put.assert_called_with(
            "/configuration_manager/deviceGroups/workflow-group", json=expected_body
        )


class TestConfigurationManagerComplianceReports:
    """Test cases for Configuration Manager Compliance Report methods."""

    @pytest.fixture
    def mock_client(self):
        """Create a mock AsyncPlatform client."""
        return AsyncMock(spec=ipsdk.platform.AsyncPlatform)

    @pytest.fixture
    def service(self, mock_client):
        """Create a Configuration Manager Service instance."""
        return Service(mock_client)

    @pytest.mark.asyncio
    async def test_describe_compliance_report_success(self, service, mock_client):
        """Test successful compliance report description retrieval."""
        expected_data = {
            "report_id": "compliance-report-123",
            "status": "complete",
            "devices": [
                {"name": "device1", "compliance_status": "compliant", "violations": []},
                {
                    "name": "device2",
                    "compliance_status": "non-compliant",
                    "violations": [{"rule": "rule1", "severity": "high"}],
                },
            ],
            "summary": {
                "total_devices": 2,
                "compliant_devices": 1,
                "non_compliant_devices": 1,
            },
        }

        mock_response = Mock()
        mock_response.json.return_value = expected_data
        mock_client.get.return_value = mock_response

        result = await service.describe_compliance_report("compliance-report-123")

        mock_client.get.assert_called_once_with(
            "/configuration_manager/compliance_reports/details/compliance-report-123"
        )
        assert result == expected_data

    @pytest.mark.asyncio
    async def test_describe_compliance_report_empty_devices(self, service, mock_client):
        """Test describing a compliance report with empty devices list."""
        expected_data = {
            "report_id": "empty-report-456",
            "status": "complete",
            "devices": [],
            "summary": {
                "total_devices": 0,
                "compliant_devices": 0,
                "non_compliant_devices": 0,
            },
        }

        mock_response = Mock()
        mock_response.json.return_value = expected_data
        mock_client.get.return_value = mock_response

        result = await service.describe_compliance_report("empty-report-456")

        mock_client.get.assert_called_once_with(
            "/configuration_manager/compliance_reports/details/empty-report-456"
        )
        assert result == expected_data
        assert result["devices"] == []


class TestConfigurationManagerDevices:
    """Test cases for Configuration Manager Device methods."""

    @pytest.fixture
    def mock_client(self):
        """Create a mock AsyncPlatform client."""
        return AsyncMock(spec=ipsdk.platform.AsyncPlatform)

    @pytest.fixture
    def service(self, mock_client):
        """Create a Configuration Manager Service instance."""
        return Service(mock_client)

    @pytest.mark.asyncio
    async def test_get_devices_success(self, service, mock_client):
        """Test successful retrieval of all devices."""
        expected_data = [
            {
                "name": "device1",
                "type": "cisco_ios",
                "ip": "192.168.1.1",
                "status": "active",
            },
            {
                "name": "device2",
                "type": "juniper",
                "ip": "192.168.1.2",
                "status": "active",
            },
        ]

        mock_response = Mock()
        mock_response.json.return_value = {"list": expected_data, "return_count": 2}
        mock_client.post.return_value = mock_response

        result = await service.get_devices()

        expected_body = {
            "options": {
                "order": "ascending",
                "sort": [{"name": 1}],
                "start": 0,
                "limit": 100,
            }
        }
        mock_client.post.assert_called_once_with(
            "/configuration_manager/devices", json=expected_body
        )
        assert result == expected_data

    @pytest.mark.asyncio
    async def test_get_devices_pagination(self, service, mock_client):
        """Test get_devices with pagination."""
        first_page = [
            {"name": f"device{i}", "type": "cisco_ios"} for i in range(1, 101)
        ]
        second_page = [
            {"name": f"device{i}", "type": "cisco_ios"} for i in range(101, 151)
        ]

        mock_responses = [
            Mock(**{"json.return_value": {"list": first_page, "return_count": 150}}),
            Mock(**{"json.return_value": {"list": second_page, "return_count": 150}}),
        ]
        mock_client.post.side_effect = mock_responses

        result = await service.get_devices()

        assert len(result) == 150
        assert result[:100] == first_page
        assert result[100:] == second_page
        assert mock_client.post.call_count == 2

    @pytest.mark.asyncio
    async def test_get_devices_empty_response(self, service, mock_client):
        """Test get_devices with empty response."""
        mock_response = Mock()
        mock_response.json.return_value = {"list": [], "return_count": 0}
        mock_client.post.return_value = mock_response

        result = await service.get_devices()

        assert result == []

    @pytest.mark.asyncio
    async def test_get_device_configuration_success(self, service, mock_client):
        """Test successful device configuration retrieval."""
        expected_config = "interface GigabitEthernet0/0/0\n description WAN link\n ip address 192.168.1.1 255.255.255.0"
        expected_response = {"config": expected_config}

        mock_response = Mock()
        mock_response.json.return_value = expected_response
        mock_client.get.return_value = mock_response

        result = await service.get_device_configuration("test-device")

        mock_client.get.assert_called_once_with(
            "/configuration_manager/devices/test-device/configuration"
        )
        assert result == expected_config

    @pytest.mark.asyncio
    async def test_get_device_configuration_value_error(self, service, mock_client):
        """Test get_device_configuration with ValueError."""
        mock_client.get.side_effect = ValueError("Device not found")

        with pytest.raises(ValueError, match="Device not found"):
            await service.get_device_configuration("nonexistent-device")

    @pytest.mark.asyncio
    async def test_backup_device_configuration_success(self, service, mock_client):
        """Test successful device configuration backup."""
        expected_response = {
            "id": "backup-123",
            "status": "success",
            "message": "Configuration backup created successfully",
        }

        mock_response = Mock()
        mock_response.json.return_value = expected_response
        mock_client.post.return_value = mock_response

        result = await service.backup_device_configuration(
            name="test-device", description="Test backup", notes="Backup for testing"
        )

        expected_body = {
            "name": "test-device",
            "options": {"description": "Test backup", "notes": "Backup for testing"},
        }
        mock_client.post.assert_called_once_with(
            "/configuration_manager/devices/backups", json=expected_body
        )
        assert result == expected_response

    @pytest.mark.asyncio
    async def test_backup_device_configuration_minimal(self, service, mock_client):
        """Test device configuration backup with minimal parameters."""
        expected_response = {
            "id": "backup-456",
            "status": "success",
            "message": "Configuration backup created",
        }

        mock_response = Mock()
        mock_response.json.return_value = expected_response
        mock_client.post.return_value = mock_response

        result = await service.backup_device_configuration(name="test-device")

        expected_body = {
            "name": "test-device",
            "options": {"description": "", "notes": ""},
        }
        mock_client.post.assert_called_once_with(
            "/configuration_manager/devices/backups", json=expected_body
        )
        assert result == expected_response

    @pytest.mark.asyncio
    async def test_apply_device_configuration_success(self, service, mock_client):
        """Test successful device configuration application."""
        config = (
            "interface GigabitEthernet0/0/1\n description New interface\n no shutdown"
        )
        expected_response = {
            "status": "success",
            "message": "Configuration applied successfully",
            "job_id": "job-789",
        }

        mock_response = Mock()
        mock_response.json.return_value = expected_response
        mock_client.post.return_value = mock_response

        result = await service.apply_device_configuration(
            device="test-device", config=config
        )

        expected_body = {"config": {"device": "test-device", "config": config}}
        mock_client.post.assert_called_once_with(
            "/configuration_manager/devices/test-device/configuration",
            json=expected_body,
        )
        assert result == expected_response

    @pytest.mark.asyncio
    async def test_apply_device_configuration_empty_config(self, service, mock_client):
        """Test applying empty configuration."""
        expected_response = {
            "status": "warning",
            "message": "Empty configuration applied",
        }

        mock_response = Mock()
        mock_response.json.return_value = expected_response
        mock_client.post.return_value = mock_response

        result = await service.apply_device_configuration(
            device="test-device", config=""
        )

        expected_body = {"config": {"device": "test-device", "config": ""}}
        mock_client.post.assert_called_once_with(
            "/configuration_manager/devices/test-device/configuration",
            json=expected_body,
        )
        assert result == expected_response


class TestConfigurationManagerTemplateRendering:
    """Test cases for Configuration Manager Template Rendering methods."""

    @pytest.fixture
    def mock_client(self):
        """Create a mock AsyncPlatform client."""
        return AsyncMock(spec=ipsdk.platform.AsyncPlatform)

    @pytest.fixture
    def service(self, mock_client):
        """Create a Configuration Manager Service instance."""
        return Service(mock_client)

    @pytest.mark.asyncio
    async def test_render_template_success(self, service, mock_client):
        """Test successful template rendering."""
        template = "interface {{ interface_name }}\n description {{ description }}"
        variables = {
            "interface_name": "GigabitEthernet0/0/1",
            "description": "WAN connection",
        }
        expected_result = "interface GigabitEthernet0/0/1\n description WAN connection"
        expected_response = expected_result

        mock_response = Mock()
        mock_response.json.return_value = expected_response
        mock_client.post.return_value = mock_response

        result = await service.render_template(template=template, variables=variables)

        expected_body = {"template": template, "variables": variables}
        mock_client.post.assert_called_once_with(
            "/configuration_manager/jinja2", json=expected_body
        )
        assert result == expected_result

    @pytest.mark.asyncio
    async def test_render_template_without_variables(self, service, mock_client):
        """Test template rendering without variables."""
        template = "interface GigabitEthernet0/0/1\n description Static interface"
        expected_result = (
            "interface GigabitEthernet0/0/1\n description Static interface"
        )
        expected_response = expected_result

        mock_response = Mock()
        mock_response.json.return_value = expected_response
        mock_client.post.return_value = mock_response

        result = await service.render_template(template=template)

        expected_body = {"template": template, "variables": {}}
        mock_client.post.assert_called_once_with(
            "/configuration_manager/jinja2", json=expected_body
        )
        assert result == expected_result

    @pytest.mark.asyncio
    async def test_render_template_empty_template(self, service, mock_client):
        """Test rendering empty template."""
        template = ""
        expected_result = ""
        expected_response = expected_result

        mock_response = Mock()
        mock_response.json.return_value = expected_response
        mock_client.post.return_value = mock_response

        result = await service.render_template(template=template)

        expected_body = {"template": template, "variables": {}}
        mock_client.post.assert_called_once_with(
            "/configuration_manager/jinja2", json=expected_body
        )
        assert result == expected_result

    @pytest.mark.asyncio
    async def test_render_template_with_empty_variables(self, service, mock_client):
        """Test template rendering with empty variables dict."""
        template = "interface {{ interface_name | default('GigabitEthernet0/0/0') }}"
        variables = {}
        expected_result = "interface GigabitEthernet0/0/0"
        expected_response = expected_result

        mock_response = Mock()
        mock_response.json.return_value = expected_response
        mock_client.post.return_value = mock_response

        result = await service.render_template(template=template, variables=variables)

        expected_body = {
            "template": template,
            "variables": {},
        }  # Empty variables dict is included
        mock_client.post.assert_called_once_with(
            "/configuration_manager/jinja2", json=expected_body
        )
        assert result == expected_result

    @pytest.mark.asyncio
    async def test_render_template_complex_variables(self, service, mock_client):
        """Test template rendering with complex nested variables."""
        template = """
interface {{ interface.name }}
 description {{ interface.description }}
 ip address {{ interface.ip }} {{ interface.mask }}
{% for vlan in vlans %}
 switchport trunk allowed vlan add {{ vlan.id }}
{% endfor %}
        """.strip()

        variables = {
            "interface": {
                "name": "GigabitEthernet0/0/1",
                "description": "Trunk port",
                "ip": "192.168.1.1",
                "mask": "255.255.255.0",
            },
            "vlans": [{"id": 10}, {"id": 20}, {"id": 30}],
        }

        expected_result = """
interface GigabitEthernet0/0/1
 description Trunk port
 ip address 192.168.1.1 255.255.255.0
 switchport trunk allowed vlan add 10
 switchport trunk allowed vlan add 20
 switchport trunk allowed vlan add 30
        """.strip()

        expected_response = expected_result

        mock_response = Mock()
        mock_response.json.return_value = expected_response
        mock_client.post.return_value = mock_response

        result = await service.render_template(template=template, variables=variables)

        expected_body = {"template": template, "variables": variables}
        mock_client.post.assert_called_once_with(
            "/configuration_manager/jinja2", json=expected_body
        )
        assert result == expected_result


class TestConfigurationManagerCompliancePlans:
    """Test cases for Configuration Manager Compliance Plans methods."""

    @pytest.fixture
    def mock_client(self):
        """Create a mock AsyncPlatform client."""
        return AsyncMock(spec=ipsdk.platform.AsyncPlatform)

    @pytest.fixture
    def service(self, mock_client):
        """Create a Configuration Manager Service instance."""
        return Service(mock_client)

    @pytest.mark.asyncio
    async def test_get_compliance_plans_success(self, service, mock_client):
        """Test successful retrieval of compliance plans."""
        # Mock first API call
        mock_response_1 = Mock()
        mock_response_1.json.return_value = {
            "plans": [
                {
                    "id": "plan-1",
                    "name": "Security Compliance",
                    "description": "Security configuration checks",
                    "throttle": 5,
                },
                {
                    "id": "plan-2",
                    "name": "Interface Compliance",
                    "description": "Interface configuration validation",
                    "throttle": 10,
                },
            ],
            "totalCount": 3,
        }

        # Mock second API call
        mock_response_2 = Mock()
        mock_response_2.json.return_value = {
            "plans": [
                {
                    "id": "plan-3",
                    "name": "VLAN Compliance",
                    "description": "VLAN configuration checks",
                    "throttle": 3,
                }
            ],
            "totalCount": 3,
        }

        mock_client.post.side_effect = [mock_response_1, mock_response_2]

        result = await service.get_compliance_plans()

        # Verify API calls were made correctly
        assert mock_client.post.call_count == 2

        expected_body_1 = {"name": "", "options": {"start": 0, "limit": 100}}
        expected_body_2 = {"name": "", "options": {"start": 100, "limit": 100}}

        mock_client.post.assert_any_call(
            "/configuration_manager/search/compliance_plans", json=expected_body_1
        )
        mock_client.post.assert_any_call(
            "/configuration_manager/search/compliance_plans", json=expected_body_2
        )

        # Verify result structure
        assert len(result) == 3
        assert result[0]["id"] == "plan-1"
        assert result[0]["name"] == "Security Compliance"
        assert result[1]["id"] == "plan-2"
        assert result[1]["name"] == "Interface Compliance"
        assert result[2]["id"] == "plan-3"
        assert result[2]["name"] == "VLAN Compliance"

    @pytest.mark.asyncio
    async def test_get_compliance_plans_single_page(self, service, mock_client):
        """Test get_compliance_plans with all results in single page."""
        mock_response = Mock()
        mock_response.json.return_value = {
            "plans": [
                {
                    "id": "plan-1",
                    "name": "Single Plan",
                    "description": "Only one plan",
                    "throttle": 1,
                }
            ],
            "totalCount": 1,
        }

        mock_client.post.return_value = mock_response

        result = await service.get_compliance_plans()

        # Verify only one API call was made
        assert mock_client.post.call_count == 1
        mock_client.post.assert_called_once_with(
            "/configuration_manager/search/compliance_plans",
            json={"name": "", "options": {"start": 0, "limit": 100}},
        )

        assert len(result) == 1
        assert result[0]["id"] == "plan-1"
        assert result[0]["name"] == "Single Plan"

    @pytest.mark.asyncio
    async def test_get_compliance_plans_empty_response(self, service, mock_client):
        """Test get_compliance_plans with empty response."""
        mock_response = Mock()
        mock_response.json.return_value = {"plans": [], "totalCount": 0}

        mock_client.post.return_value = mock_response

        result = await service.get_compliance_plans()

        mock_client.post.assert_called_once_with(
            "/configuration_manager/search/compliance_plans",
            json={"name": "", "options": {"start": 0, "limit": 100}},
        )

        assert result == []

    @pytest.mark.asyncio
    async def test_run_compliance_plan_success(self, service, mock_client):
        """Test successful execution of compliance plan."""
        # Mock get_compliance_plans
        plans_data = [
            {
                "id": "plan-1",
                "name": "Security Plan",
                "description": "Security checks",
                "throttle": 5,
            },
            {
                "id": "plan-2",
                "name": "Network Plan",
                "description": "Security checks",
                "throttle": 10,
            },
        ]
        service.get_compliance_plans = AsyncMock(return_value=plans_data)

        # Mock run compliance plan API call
        mock_run_response = Mock()
        mock_run_response.json.return_value = {"status": "started"}

        # Mock search compliance plan instances API call
        mock_search_response = Mock()
        mock_search_response.json.return_value = {
            "plans": [
                {
                    "id": "instance-123",
                    "name": "Security Plan",
                    "description": "Security checks",
                    "jobStatus": "running",
                }
            ]
        }

        mock_client.post.side_effect = [mock_run_response, mock_search_response]

        result = await service.run_compliance_plan("Security Plan")

        # Verify get_compliance_plans was called
        service.get_compliance_plans.assert_called_once()

        # Verify API calls were made
        assert mock_client.post.call_count == 2

        # First call: run compliance plan
        mock_client.post.assert_any_call(
            "/configuration_manager/compliance_plans/run", json={"planId": "plan-1"}
        )

        # Second call: search instances
        expected_search_body = {
            "searchParams": {
                "limit": 1,
                "planId": "plan-1",
                "sort": {"started": -1},
                "start": 0,
            }
        }
        mock_client.post.assert_any_call(
            "/configuration_manager/search/compliance_plan_instances",
            json=expected_search_body,
        )

        # Verify result
        assert result["id"] == "instance-123"
        assert result["name"] == "Security Plan"
        assert result["jobStatus"] == "running"

    @pytest.mark.asyncio
    async def test_run_compliance_plan_not_found(self, service):
        """Test run_compliance_plan with non-existent plan name."""
        plans_data = [
            {
                "id": "plan-1",
                "name": "Existing Plan",
                "description": "Exists",
                "throttle": 5,
            }
        ]
        service.get_compliance_plans = AsyncMock(return_value=plans_data)

        with pytest.raises(
            ValueError, match="compliance plan Non-Existent Plan not found"
        ):
            await service.run_compliance_plan("Non-Existent Plan")

        service.get_compliance_plans.assert_called_once()

    @pytest.mark.asyncio
    async def test_run_compliance_plan_empty_plans_list(self, service):
        """Test run_compliance_plan with no available plans."""
        service.get_compliance_plans = AsyncMock(return_value=[])

        with pytest.raises(ValueError, match="compliance plan Any Plan not found"):
            await service.run_compliance_plan("Any Plan")

        service.get_compliance_plans.assert_called_once()

    @pytest.mark.asyncio
    async def test_run_compliance_plan_case_sensitive(self, service):
        """Test that run_compliance_plan is case-sensitive."""
        plans_data = [
            {
                "id": "plan-1",
                "name": "Security Plan",
                "description": "Security checks",
                "throttle": 5,
            }
        ]
        service.get_compliance_plans = AsyncMock(return_value=plans_data)

        # Test exact match works
        mock_run_response = Mock()
        mock_run_response.json.return_value = {"status": "started"}

        mock_search_response = Mock()
        mock_search_response.json.return_value = {
            "plans": [
                {
                    "id": "instance-123",
                    "name": "Security Plan",
                    "description": "Security checks",
                    "jobStatus": "running",
                }
            ]
        }

        service.client.post = AsyncMock(
            side_effect=[mock_run_response, mock_search_response]
        )

        result = await service.run_compliance_plan("Security Plan")
        assert result["name"] == "Security Plan"

        # Test case mismatch fails
        with pytest.raises(ValueError, match="compliance plan security plan not found"):
            await service.run_compliance_plan("security plan")

    @pytest.mark.asyncio
    async def test_run_compliance_plan_multiple_instances(self, service, mock_client):
        """Test run_compliance_plan returns most recent instance."""
        plans_data = [
            {"id": "plan-1", "name": "Test Plan", "description": "Test", "throttle": 1}
        ]
        service.get_compliance_plans = AsyncMock(return_value=plans_data)

        mock_run_response = Mock()
        mock_run_response.json.return_value = {"status": "started"}

        # Mock search response with multiple instances (sorted by started desc)
        mock_search_response = Mock()
        mock_search_response.json.return_value = {
            "plans": [
                {
                    "id": "instance-newest",
                    "name": "Test Plan",
                    "description": "Test",
                    "jobStatus": "running",
                }
            ]
        }

        mock_client.post.side_effect = [mock_run_response, mock_search_response]

        result = await service.run_compliance_plan("Test Plan")

        # Verify correct search parameters (limit 1, sort by started desc)
        expected_search_body = {
            "searchParams": {
                "limit": 1,
                "planId": "plan-1",
                "sort": {"started": -1},
                "start": 0,
            }
        }
        mock_client.post.assert_any_call(
            "/configuration_manager/search/compliance_plan_instances",
            json=expected_search_body,
        )

        assert result["id"] == "instance-newest"

    @pytest.mark.asyncio
    async def test_compliance_plans_integration_workflow(self, service, mock_client):
        """Test integration workflow: get plans, find plan, run plan."""
        # Step 1: Get compliance plans returns multiple plans
        plans_data = [
            {
                "id": "plan-1",
                "name": "Security Compliance",
                "description": "Security checks",
                "throttle": 5,
            },
            {
                "id": "plan-2",
                "name": "Interface Compliance",
                "description": "Interface checks",
                "throttle": 10,
            },
            {
                "id": "plan-3",
                "name": "VLAN Compliance",
                "description": "VLAN checks",
                "throttle": 3,
            },
        ]
        service.get_compliance_plans = AsyncMock(return_value=plans_data)

        # Step 2: Run specific plan
        mock_run_response = Mock()
        mock_run_response.json.return_value = {"status": "started", "planId": "plan-2"}

        mock_search_response = Mock()
        mock_search_response.json.return_value = {
            "plans": [
                {
                    "id": "instance-interface-123",
                    "name": "Interface Compliance",
                    "description": "Interface checks",
                    "jobStatus": "running",
                }
            ]
        }

        mock_client.post.side_effect = [mock_run_response, mock_search_response]

        result = await service.run_compliance_plan("Interface Compliance")

        # Verify the workflow
        service.get_compliance_plans.assert_called_once()

        assert mock_client.post.call_count == 2
        mock_client.post.assert_any_call(
            "/configuration_manager/compliance_plans/run",
            json={"planId": "plan-2"},  # Correct plan ID for "Interface Compliance"
        )

        assert result["id"] == "instance-interface-123"
        assert result["name"] == "Interface Compliance"
        assert result["jobStatus"] == "running"
