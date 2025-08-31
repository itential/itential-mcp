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

    def test_service_methods_are_async(self, service):
        """Test that all service methods are async."""
        import asyncio

        assert asyncio.iscoroutinefunction(service.get_golden_config_trees)
        assert asyncio.iscoroutinefunction(service.create_golden_config_tree)
        assert asyncio.iscoroutinefunction(service.describe_golden_config_tree_version)
        assert asyncio.iscoroutinefunction(service.set_golden_config_template)
        assert asyncio.iscoroutinefunction(service.add_golden_config_node)
