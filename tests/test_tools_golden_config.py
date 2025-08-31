# Copyright (c) 2025 Itential, Inc
# GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)

import pytest
from unittest.mock import AsyncMock, Mock

from fastmcp import Context

from itential_mcp import exceptions
from itential_mcp import errors
from itential_mcp.tools.golden_config import (
    get_golden_config_trees,
    create_golden_config_tree,
    add_golden_config_node,
)
from itential_mcp.models.configuration_manager import (
    GetGoldenConfigTreesResponse,
    CreateGoldenConfigTreeResponse,
    AddGoldenConfigNodeResponse,
)


class TestGoldenConfigTools:
    """Test cases for Golden Configuration tools."""

    @pytest.fixture
    def mock_context(self):
        """Create a mock FastMCP Context."""
        context = AsyncMock(spec=Context)
        mock_client = AsyncMock()
        mock_client.configuration_manager = AsyncMock()

        # Mock the lifespan context structure
        context.request_context.lifespan_context.get.return_value = mock_client

        return context

    @pytest.fixture
    def mock_configuration_manager(self, mock_context):
        """Get the mock configuration manager service."""
        client = mock_context.request_context.lifespan_context.get.return_value
        return client.configuration_manager

    @pytest.mark.asyncio
    async def test_get_golden_config_trees_success(
        self, mock_context, mock_configuration_manager
    ):
        """Test successful retrieval of golden config trees."""
        trees_data = [
            {
                "name": "cisco-base-config",
                "deviceType": "cisco_ios",
                "versions": ["v1.0", "v2.0", "v3.0"],
            },
            {
                "name": "juniper-base-config",
                "deviceType": "juniper_junos",
                "versions": ["initial", "v2.1"],
            },
        ]

        mock_configuration_manager.get_golden_config_trees.return_value = trees_data

        result = await get_golden_config_trees(mock_context)

        mock_context.info.assert_called_once_with("inside get_golden_config_trees(...)")
        mock_configuration_manager.get_golden_config_trees.assert_called_once()

        assert isinstance(result, GetGoldenConfigTreesResponse)
        assert len(result.root) == 2

        assert result.root[0].name == "cisco-base-config"
        assert result.root[0].device_type == "cisco_ios"
        assert result.root[0].versions == ["v1.0", "v2.0", "v3.0"]

        assert result.root[1].name == "juniper-base-config"
        assert result.root[1].device_type == "juniper_junos"
        assert result.root[1].versions == ["initial", "v2.1"]

    @pytest.mark.asyncio
    async def test_get_golden_config_trees_empty(
        self, mock_context, mock_configuration_manager
    ):
        """Test get_golden_config_trees with empty response."""
        mock_configuration_manager.get_golden_config_trees.return_value = []

        result = await get_golden_config_trees(mock_context)

        mock_context.info.assert_called_once_with("inside get_golden_config_trees(...)")
        mock_configuration_manager.get_golden_config_trees.assert_called_once()

        assert isinstance(result, GetGoldenConfigTreesResponse)
        assert len(result.root) == 0
        assert result.root == []

    @pytest.mark.asyncio
    async def test_get_golden_config_trees_single_tree(
        self, mock_context, mock_configuration_manager
    ):
        """Test get_golden_config_trees with single tree."""
        trees_data = [
            {"name": "single-tree", "deviceType": "arista_eos", "versions": ["v1.0"]}
        ]

        mock_configuration_manager.get_golden_config_trees.return_value = trees_data

        result = await get_golden_config_trees(mock_context)

        assert isinstance(result, GetGoldenConfigTreesResponse)
        assert len(result.root) == 1
        assert result.root[0].name == "single-tree"
        assert result.root[0].device_type == "arista_eos"
        assert result.root[0].versions == ["v1.0"]

    @pytest.mark.asyncio
    async def test_create_golden_config_tree_minimal(
        self, mock_context, mock_configuration_manager
    ):
        """Test creating a golden config tree with minimal parameters."""
        service_response = {
            "name": "test-tree",
            "deviceType": "cisco_ios",
            "id": "tree-123",
        }

        mock_configuration_manager.create_golden_config_tree.return_value = (
            service_response
        )

        result = await create_golden_config_tree(
            ctx=mock_context,
            name="test-tree",
            device_type="cisco_ios",
            template=None,
            variables=None,
        )

        mock_context.info.assert_called_once_with(
            "inside create_golden_config_tree(...)"
        )
        mock_configuration_manager.create_golden_config_tree.assert_called_once_with(
            name="test-tree", device_type="cisco_ios", template=None, variables=None
        )

        assert isinstance(result, CreateGoldenConfigTreeResponse)
        assert result.name == "test-tree"
        assert result.device_type == "cisco_ios"

    @pytest.mark.asyncio
    async def test_create_golden_config_tree_with_template(
        self, mock_context, mock_configuration_manager
    ):
        """Test creating a golden config tree with template."""
        template = "interface {{ interface_name }}\n description {{ description }}"
        service_response = {
            "name": "templated-tree",
            "deviceType": "cisco_nxos",
            "id": "tree-456",
        }

        mock_configuration_manager.create_golden_config_tree.return_value = (
            service_response
        )

        result = await create_golden_config_tree(
            ctx=mock_context,
            name="templated-tree",
            device_type="cisco_nxos",
            template=template,
            variables=None,
        )

        mock_configuration_manager.create_golden_config_tree.assert_called_once_with(
            name="templated-tree",
            device_type="cisco_nxos",
            template=template,
            variables=None,
        )

        assert isinstance(result, CreateGoldenConfigTreeResponse)
        assert result.name == "templated-tree"
        assert result.device_type == "cisco_nxos"

    @pytest.mark.asyncio
    async def test_create_golden_config_tree_with_variables(
        self, mock_context, mock_configuration_manager
    ):
        """Test creating a golden config tree with variables."""
        variables = {
            "interface_name": "GigabitEthernet0/1",
            "description": "WAN Interface",
        }
        service_response = {
            "name": "variable-tree",
            "deviceType": "juniper_junos",
            "id": "tree-789",
        }

        mock_configuration_manager.create_golden_config_tree.return_value = (
            service_response
        )

        result = await create_golden_config_tree(
            ctx=mock_context,
            name="variable-tree",
            device_type="juniper_junos",
            template=None,
            variables=variables,
        )

        mock_configuration_manager.create_golden_config_tree.assert_called_once_with(
            name="variable-tree",
            device_type="juniper_junos",
            template=None,
            variables=variables,
        )

        assert isinstance(result, CreateGoldenConfigTreeResponse)
        assert result.name == "variable-tree"
        assert result.device_type == "juniper_junos"

    @pytest.mark.asyncio
    async def test_create_golden_config_tree_with_all_parameters(
        self, mock_context, mock_configuration_manager
    ):
        """Test creating a golden config tree with all parameters."""
        template = "interface {{ interface_name }}"
        variables = {"interface_name": "GigabitEthernet0/1"}
        service_response = {
            "name": "full-tree",
            "deviceType": "arista_eos",
            "id": "tree-full",
        }

        mock_configuration_manager.create_golden_config_tree.return_value = (
            service_response
        )

        result = await create_golden_config_tree(
            ctx=mock_context,
            name="full-tree",
            device_type="arista_eos",
            template=template,
            variables=variables,
        )

        mock_configuration_manager.create_golden_config_tree.assert_called_once_with(
            name="full-tree",
            device_type="arista_eos",
            template=template,
            variables=variables,
        )

        assert isinstance(result, CreateGoldenConfigTreeResponse)
        assert result.name == "full-tree"
        assert result.device_type == "arista_eos"

    @pytest.mark.asyncio
    async def test_create_golden_config_tree_server_exception(
        self, mock_context, mock_configuration_manager
    ):
        """Test create_golden_config_tree with server exception."""
        server_exception = exceptions.ServerException("Tree name already exists")
        mock_configuration_manager.create_golden_config_tree.side_effect = (
            server_exception
        )

        # Mock the errors.internal_server_error function
        expected_error = {"error": "Internal Server Error"}
        errors.internal_server_error = Mock(return_value=expected_error)

        result = await create_golden_config_tree(
            ctx=mock_context,
            name="existing-tree",
            device_type="cisco_ios",
            template=None,
            variables=None,
        )

        errors.internal_server_error.assert_called_once_with("Tree name already exists")
        assert result == expected_error

    @pytest.mark.asyncio
    async def test_add_golden_config_node_minimal(
        self, mock_context, mock_configuration_manager
    ):
        """Test adding a golden config node with minimal parameters."""
        mock_configuration_manager.add_golden_config_node.return_value = None

        result = await add_golden_config_node(
            ctx=mock_context,
            tree_name="test-tree",
            name="interface-config",
            version="initial",
            path="base",
            template=None,
        )

        mock_context.info.assert_called_once_with("inside add_golden_config_node(...)")
        mock_configuration_manager.add_golden_config_node.assert_called_once_with(
            name="interface-config",
            tree_name="test-tree",
            version="initial",
            path="base",
            template=None,
        )

        assert isinstance(result, AddGoldenConfigNodeResponse)
        assert result.message == "Successfully added node interface-config"

    @pytest.mark.asyncio
    async def test_add_golden_config_node_with_version_and_path(
        self, mock_context, mock_configuration_manager
    ):
        """Test adding a golden config node with version and path."""
        mock_configuration_manager.add_golden_config_node.return_value = None

        result = await add_golden_config_node(
            ctx=mock_context,
            tree_name="test-tree",
            name="routing-config",
            version="v2.0",
            path="base/routing",
            template=None,
        )

        mock_configuration_manager.add_golden_config_node.assert_called_once_with(
            name="routing-config",
            tree_name="test-tree",
            version="v2.0",
            path="base/routing",
            template=None,
        )

        assert isinstance(result, AddGoldenConfigNodeResponse)
        assert result.message == "Successfully added node routing-config"

    @pytest.mark.asyncio
    async def test_add_golden_config_node_with_template(
        self, mock_context, mock_configuration_manager
    ):
        """Test adding a golden config node with template."""
        template = "router ospf {{ process_id }}"
        mock_configuration_manager.add_golden_config_node.return_value = None

        result = await add_golden_config_node(
            ctx=mock_context,
            tree_name="test-tree",
            name="ospf-config",
            version="initial",
            path="base",
            template=template,
        )

        mock_configuration_manager.add_golden_config_node.assert_called_once_with(
            name="ospf-config",
            tree_name="test-tree",
            version="initial",
            path="base",
            template=template,
        )

        assert isinstance(result, AddGoldenConfigNodeResponse)
        assert result.message == "Successfully added node ospf-config"

    @pytest.mark.asyncio
    async def test_add_golden_config_node_all_parameters(
        self, mock_context, mock_configuration_manager
    ):
        """Test adding a golden config node with all parameters."""
        template = "interface {{ interface_name }}"
        mock_configuration_manager.add_golden_config_node.return_value = None

        result = await add_golden_config_node(
            ctx=mock_context,
            tree_name="full-tree",
            name="interface-node",
            version="v3.0",
            path="base/interfaces",
            template=template,
        )

        mock_configuration_manager.add_golden_config_node.assert_called_once_with(
            name="interface-node",
            tree_name="full-tree",
            version="v3.0",
            path="base/interfaces",
            template=template,
        )

        assert isinstance(result, AddGoldenConfigNodeResponse)
        assert result.message == "Successfully added node interface-node"

    @pytest.mark.asyncio
    async def test_add_golden_config_node_server_exception(
        self, mock_context, mock_configuration_manager
    ):
        """Test add_golden_config_node with server exception."""
        server_exception = exceptions.ServerException("Node creation failed")
        mock_configuration_manager.add_golden_config_node.side_effect = server_exception

        expected_error = {"error": "Internal Server Error"}
        errors.internal_server_error = Mock(return_value=expected_error)

        result = await add_golden_config_node(
            ctx=mock_context,
            tree_name="test-tree",
            name="failing-node",
            version="initial",
            path="base",
            template=None,
        )

        errors.internal_server_error.assert_called_once_with("Node creation failed")
        assert result == expected_error

    @pytest.mark.asyncio
    async def test_add_golden_config_node_empty_path_handling(
        self, mock_context, mock_configuration_manager
    ):
        """Test add_golden_config_node with empty path parameter."""
        mock_configuration_manager.add_golden_config_node.return_value = None

        result = await add_golden_config_node(
            ctx=mock_context,
            tree_name="test-tree",
            name="test-node",
            version="initial",
            path="",  # Empty path
            template=None,
        )

        # Should still call with the empty path since it's explicitly provided
        mock_configuration_manager.add_golden_config_node.assert_called_once_with(
            name="test-node",
            tree_name="test-tree",
            version="initial",
            path="",
            template=None,
        )

        assert isinstance(result, AddGoldenConfigNodeResponse)

    @pytest.mark.asyncio
    async def test_add_golden_config_node_empty_template_handling(
        self, mock_context, mock_configuration_manager
    ):
        """Test add_golden_config_node with empty template parameter."""
        mock_configuration_manager.add_golden_config_node.return_value = None

        result = await add_golden_config_node(
            ctx=mock_context,
            tree_name="test-tree",
            name="test-node",
            version="initial",
            path="base",
            template="",  # Empty template
        )

        # Empty template should be passed as empty string, not None
        mock_configuration_manager.add_golden_config_node.assert_called_once_with(
            name="test-node",
            tree_name="test-tree",
            version="initial",
            path="base",
            template="",
        )

        assert isinstance(result, AddGoldenConfigNodeResponse)

    def test_tools_module_tags(self):
        """Test that the tools module has correct tags."""
        from itential_mcp.tools.golden_config import __tags__

        assert __tags__ == ("configuration_manager",)

    def test_function_annotations_exist(self):
        """Test that all functions have proper type annotations."""
        from typing import get_type_hints

        # Test get_golden_config_trees annotations
        hints = get_type_hints(get_golden_config_trees)
        assert "ctx" in hints
        assert "return" in hints
        assert hints["return"] == GetGoldenConfigTreesResponse

        # Test create_golden_config_tree annotations
        hints = get_type_hints(create_golden_config_tree)
        assert "ctx" in hints
        assert "name" in hints
        assert "device_type" in hints
        assert "template" in hints
        assert "variables" in hints
        assert "return" in hints
        assert hints["return"] == CreateGoldenConfigTreeResponse

        # Test add_golden_config_node annotations
        hints = get_type_hints(add_golden_config_node)
        assert "ctx" in hints
        assert "tree_name" in hints
        assert "name" in hints
        assert "version" in hints
        assert "path" in hints
        assert "template" in hints
        assert "return" in hints
        assert hints["return"] == AddGoldenConfigNodeResponse

    def test_function_signatures(self):
        """Test that functions have correct signatures."""
        import inspect

        # Test get_golden_config_trees signature
        sig = inspect.signature(get_golden_config_trees)
        assert "ctx" in sig.parameters
        assert len(sig.parameters) == 1

        # Test create_golden_config_tree signature
        sig = inspect.signature(create_golden_config_tree)
        assert "ctx" in sig.parameters
        assert "name" in sig.parameters
        assert "device_type" in sig.parameters
        assert "template" in sig.parameters
        assert "variables" in sig.parameters
        assert len(sig.parameters) == 5

        # Test add_golden_config_node signature
        sig = inspect.signature(add_golden_config_node)
        assert "tree_name" in sig.parameters
        assert "name" in sig.parameters
        assert "version" in sig.parameters
        assert "path" in sig.parameters
        assert "template" in sig.parameters
        assert len(sig.parameters) == 6

    def test_function_defaults(self):
        """Test that function parameters have Pydantic Field defaults."""
        import inspect

        # Test create_golden_config_tree - Pydantic parameters have Field info in annotation
        sig = inspect.signature(create_golden_config_tree)
        template_annotation = sig.parameters["template"].annotation
        variables_annotation = sig.parameters["variables"].annotation

        # Check that these are Annotated types with Field info
        assert hasattr(template_annotation, "__metadata__")
        assert hasattr(variables_annotation, "__metadata__")

        # Test add_golden_config_node defaults
        sig = inspect.signature(add_golden_config_node)
        version_annotation = sig.parameters["version"].annotation
        path_annotation = sig.parameters["path"].annotation
        template_annotation = sig.parameters["template"].annotation

        # Check that these are Annotated types with Field info
        assert hasattr(version_annotation, "__metadata__")
        assert hasattr(path_annotation, "__metadata__")
        assert hasattr(template_annotation, "__metadata__")

    @pytest.mark.asyncio
    async def test_context_info_logging(self, mock_context, mock_configuration_manager):
        """Test that all functions log appropriate info messages."""
        # Test get_golden_config_trees
        mock_configuration_manager.get_golden_config_trees.return_value = []
        await get_golden_config_trees(mock_context)
        mock_context.info.assert_called_with("inside get_golden_config_trees(...)")
        mock_context.info.reset_mock()

        # Test create_golden_config_tree
        mock_configuration_manager.create_golden_config_tree.return_value = {
            "name": "test",
            "deviceType": "cisco_ios",
        }
        await create_golden_config_tree(mock_context, "test", "cisco_ios", None, None)
        mock_context.info.assert_called_with("inside create_golden_config_tree(...)")
        mock_context.info.reset_mock()

        # Test add_golden_config_node
        mock_configuration_manager.add_golden_config_node.return_value = None
        await add_golden_config_node(
            mock_context, "tree", "node", "initial", "base", None
        )
        mock_context.info.assert_called_with("inside add_golden_config_node(...)")

    @pytest.mark.asyncio
    async def test_client_context_retrieval(
        self, mock_context, mock_configuration_manager
    ):
        """Test that client is properly retrieved from context."""
        mock_configuration_manager.get_golden_config_trees.return_value = []

        await get_golden_config_trees(mock_context)

        # Verify that client was retrieved from the correct context path
        mock_context.request_context.lifespan_context.get.assert_called_with("client")

    def test_function_docstrings(self):
        """Test that all functions have comprehensive docstrings."""
        functions = [
            get_golden_config_trees,
            create_golden_config_tree,
            add_golden_config_node,
        ]

        for func in functions:
            assert func.__doc__ is not None
            assert len(func.__doc__.strip()) > 0

            docstring = func.__doc__
            assert "Args:" in docstring
            assert "Returns:" in docstring
            assert "Raises:" in docstring or "None:" in docstring
