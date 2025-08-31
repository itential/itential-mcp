# Copyright (c) 2025 Itential, Inc
# GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)

import pytest
from pydantic import ValidationError

from itential_mcp.models.configuration_manager import (
    GoldenConfigTree,
    GetGoldenConfigTreesResponse,
    CreateGoldenConfigTreeResponse,
    AddGoldenConfigNodeResponse,
)


class TestGoldenConfigTree:
    """Test cases for GoldenConfigTree model."""

    def test_create_valid_golden_config_tree(self):
        """Test creating a valid GoldenConfigTree instance."""
        tree_data = {
            "name": "test-tree",
            "device_type": "cisco_ios",
            "versions": ["v1.0", "v2.0", "v3.0"],
        }

        tree = GoldenConfigTree(**tree_data)

        assert tree.name == "test-tree"
        assert tree.device_type == "cisco_ios"
        assert tree.versions == ["v1.0", "v2.0", "v3.0"]

    def test_create_golden_config_tree_with_empty_versions(self):
        """Test creating a GoldenConfigTree with empty versions list."""
        tree_data = {
            "name": "empty-versions-tree",
            "device_type": "juniper",
            "versions": [],
        }

        tree = GoldenConfigTree(**tree_data)

        assert tree.name == "empty-versions-tree"
        assert tree.device_type == "juniper"
        assert tree.versions == []

    def test_create_golden_config_tree_with_single_version(self):
        """Test creating a GoldenConfigTree with a single version."""
        tree_data = {
            "name": "single-version-tree",
            "device_type": "arista_eos",
            "versions": ["initial"],
        }

        tree = GoldenConfigTree(**tree_data)

        assert tree.name == "single-version-tree"
        assert tree.device_type == "arista_eos"
        assert tree.versions == ["initial"]

    def test_golden_config_tree_missing_name(self):
        """Test GoldenConfigTree validation with missing name field."""
        tree_data = {"device_type": "cisco_ios", "versions": ["v1.0"]}

        with pytest.raises(ValidationError) as exc_info:
            GoldenConfigTree(**tree_data)

        errors = exc_info.value.errors()
        assert len(errors) == 1
        assert errors[0]["type"] == "missing"
        assert errors[0]["loc"] == ("name",)

    def test_golden_config_tree_missing_device_type(self):
        """Test GoldenConfigTree validation with missing device_type field."""
        tree_data = {"name": "test-tree", "versions": ["v1.0"]}

        with pytest.raises(ValidationError) as exc_info:
            GoldenConfigTree(**tree_data)

        errors = exc_info.value.errors()
        assert len(errors) == 1
        assert errors[0]["type"] == "missing"
        assert errors[0]["loc"] == ("device_type",)

    def test_golden_config_tree_missing_versions(self):
        """Test GoldenConfigTree validation with missing versions field."""
        tree_data = {"name": "test-tree", "device_type": "cisco_ios"}

        with pytest.raises(ValidationError) as exc_info:
            GoldenConfigTree(**tree_data)

        errors = exc_info.value.errors()
        assert len(errors) == 1
        assert errors[0]["type"] == "missing"
        assert errors[0]["loc"] == ("versions",)

    def test_golden_config_tree_invalid_name_type(self):
        """Test GoldenConfigTree validation with invalid name type."""
        tree_data = {"name": 123, "device_type": "cisco_ios", "versions": ["v1.0"]}

        with pytest.raises(ValidationError) as exc_info:
            GoldenConfigTree(**tree_data)

        errors = exc_info.value.errors()
        assert len(errors) == 1
        assert errors[0]["type"] == "string_type"
        assert errors[0]["loc"] == ("name",)

    def test_golden_config_tree_invalid_device_type(self):
        """Test GoldenConfigTree validation with invalid device_type type."""
        tree_data = {"name": "test-tree", "device_type": None, "versions": ["v1.0"]}

        with pytest.raises(ValidationError) as exc_info:
            GoldenConfigTree(**tree_data)

        errors = exc_info.value.errors()
        assert len(errors) == 1
        assert errors[0]["type"] == "string_type"
        assert errors[0]["loc"] == ("device_type",)

    def test_golden_config_tree_invalid_versions_type(self):
        """Test GoldenConfigTree validation with invalid versions type."""
        tree_data = {
            "name": "test-tree",
            "device_type": "cisco_ios",
            "versions": "not-a-list",
        }

        with pytest.raises(ValidationError) as exc_info:
            GoldenConfigTree(**tree_data)

        errors = exc_info.value.errors()
        assert len(errors) == 1
        assert errors[0]["type"] == "list_type"
        assert errors[0]["loc"] == ("versions",)

    def test_golden_config_tree_invalid_version_item_type(self):
        """Test GoldenConfigTree validation with invalid version item type."""
        tree_data = {
            "name": "test-tree",
            "device_type": "cisco_ios",
            "versions": ["v1.0", 123, "v3.0"],
        }

        with pytest.raises(ValidationError) as exc_info:
            GoldenConfigTree(**tree_data)

        errors = exc_info.value.errors()
        assert len(errors) == 1
        assert errors[0]["type"] == "string_type"
        assert errors[0]["loc"] == ("versions", 1)

    def test_golden_config_tree_serialization(self):
        """Test GoldenConfigTree model serialization to dict."""
        tree_data = {
            "name": "serialization-tree",
            "device_type": "cisco_nxos",
            "versions": ["v1.0", "v2.0"],
        }

        tree = GoldenConfigTree(**tree_data)
        serialized = tree.model_dump()

        assert serialized == tree_data

    def test_golden_config_tree_json_serialization(self):
        """Test GoldenConfigTree model JSON serialization."""
        tree_data = {
            "name": "json-tree",
            "device_type": "juniper_junos",
            "versions": ["initial", "v2.1"],
        }

        tree = GoldenConfigTree(**tree_data)
        json_str = tree.model_dump_json()

        assert '"name":"json-tree"' in json_str
        assert '"device_type":"juniper_junos"' in json_str
        assert '"versions":["initial","v2.1"]' in json_str


class TestGetGoldenConfigTreesResponse:
    """Test cases for GetGoldenConfigTreesResponse model."""

    def test_create_valid_response_with_multiple_trees(self):
        """Test creating a valid GetGoldenConfigTreesResponse with multiple trees."""
        trees_data = [
            {"name": "tree1", "device_type": "cisco_ios", "versions": ["v1.0", "v2.0"]},
            {"name": "tree2", "device_type": "juniper", "versions": ["initial"]},
        ]

        response = GetGoldenConfigTreesResponse(root=trees_data)

        assert len(response.root) == 2
        assert response.root[0].name == "tree1"
        assert response.root[0].device_type == "cisco_ios"
        assert response.root[0].versions == ["v1.0", "v2.0"]
        assert response.root[1].name == "tree2"
        assert response.root[1].device_type == "juniper"
        assert response.root[1].versions == ["initial"]

    def test_create_response_with_empty_list(self):
        """Test creating GetGoldenConfigTreesResponse with empty list."""
        response = GetGoldenConfigTreesResponse(root=[])

        assert response.root == []
        assert len(response.root) == 0

    def test_create_response_with_single_tree(self):
        """Test creating GetGoldenConfigTreesResponse with single tree."""
        tree_data = {
            "name": "single-tree",
            "device_type": "arista_eos",
            "versions": ["v1.0", "v1.1", "v2.0"],
        }

        response = GetGoldenConfigTreesResponse(root=[tree_data])

        assert len(response.root) == 1
        assert response.root[0].name == "single-tree"
        assert response.root[0].device_type == "arista_eos"
        assert response.root[0].versions == ["v1.0", "v1.1", "v2.0"]

    def test_response_with_invalid_tree_data(self):
        """Test GetGoldenConfigTreesResponse validation with invalid tree data."""
        invalid_trees_data = [
            {"name": "valid-tree", "device_type": "cisco_ios", "versions": ["v1.0"]},
            {"device_type": "juniper"},
        ]

        with pytest.raises(ValidationError) as exc_info:
            GetGoldenConfigTreesResponse(root=invalid_trees_data)

        errors = exc_info.value.errors()
        assert len(errors) >= 1
        missing_field_errors = [e for e in errors if e["type"] == "missing"]
        assert len(missing_field_errors) >= 1

    def test_response_direct_list_initialization(self):
        """Test GetGoldenConfigTreesResponse direct initialization with list."""
        trees_data = [
            {"name": "direct-tree1", "device_type": "cisco_ios", "versions": ["v1.0"]},
            {
                "name": "direct-tree2",
                "device_type": "juniper",
                "versions": ["initial", "v2.0"],
            },
        ]

        response = GetGoldenConfigTreesResponse(trees_data)

        assert len(response.root) == 2
        assert response.root[0].name == "direct-tree1"
        assert response.root[1].name == "direct-tree2"

    def test_response_serialization(self):
        """Test GetGoldenConfigTreesResponse serialization."""
        trees_data = [
            {
                "name": "serialize-tree",
                "device_type": "cisco_nxos",
                "versions": ["v1.0", "v2.0"],
            }
        ]

        response = GetGoldenConfigTreesResponse(root=trees_data)
        serialized = response.model_dump()

        assert serialized == trees_data

    def test_response_iteration(self):
        """Test that GetGoldenConfigTreesResponse root can be iterated."""
        trees_data = [
            {"name": f"tree{i}", "device_type": "cisco_ios", "versions": [f"v{i}.0"]}
            for i in range(3)
        ]

        response = GetGoldenConfigTreesResponse(root=trees_data)

        tree_names = []
        for tree in response.root:
            tree_names.append(tree.name)

        assert tree_names == ["tree0", "tree1", "tree2"]


class TestCreateGoldenConfigTreeResponse:
    """Test cases for CreateGoldenConfigTreeResponse model."""

    def test_create_valid_response(self):
        """Test creating a valid CreateGoldenConfigTreeResponse."""
        response_data = {"name": "created-tree", "device_type": "cisco_ios"}

        response = CreateGoldenConfigTreeResponse(**response_data)

        assert response.name == "created-tree"
        assert response.device_type == "cisco_ios"

    def test_create_response_with_different_device_types(self):
        """Test creating response with various device types."""
        device_types = [
            "cisco_ios",
            "cisco_nxos",
            "juniper_junos",
            "arista_eos",
            "custom_device",
        ]

        for device_type in device_types:
            response_data = {"name": f"tree-{device_type}", "device_type": device_type}

            response = CreateGoldenConfigTreeResponse(**response_data)

            assert response.name == f"tree-{device_type}"
            assert response.device_type == device_type

    def test_response_missing_name(self):
        """Test CreateGoldenConfigTreeResponse validation with missing name."""
        response_data = {"device_type": "cisco_ios"}

        with pytest.raises(ValidationError) as exc_info:
            CreateGoldenConfigTreeResponse(**response_data)

        errors = exc_info.value.errors()
        assert len(errors) == 1
        assert errors[0]["type"] == "missing"
        assert errors[0]["loc"] == ("name",)

    def test_response_missing_device_type(self):
        """Test CreateGoldenConfigTreeResponse validation with missing device_type."""
        response_data = {"name": "test-tree"}

        with pytest.raises(ValidationError) as exc_info:
            CreateGoldenConfigTreeResponse(**response_data)

        errors = exc_info.value.errors()
        assert len(errors) == 1
        assert errors[0]["type"] == "missing"
        assert errors[0]["loc"] == ("device_type",)

    def test_response_invalid_name_type(self):
        """Test CreateGoldenConfigTreeResponse validation with invalid name type."""
        response_data = {"name": None, "device_type": "cisco_ios"}

        with pytest.raises(ValidationError) as exc_info:
            CreateGoldenConfigTreeResponse(**response_data)

        errors = exc_info.value.errors()
        assert len(errors) == 1
        assert errors[0]["type"] == "string_type"
        assert errors[0]["loc"] == ("name",)

    def test_response_invalid_device_type_type(self):
        """Test CreateGoldenConfigTreeResponse validation with invalid device_type type."""
        response_data = {"name": "test-tree", "device_type": 123}

        with pytest.raises(ValidationError) as exc_info:
            CreateGoldenConfigTreeResponse(**response_data)

        errors = exc_info.value.errors()
        assert len(errors) == 1
        assert errors[0]["type"] == "string_type"
        assert errors[0]["loc"] == ("device_type",)

    def test_response_serialization(self):
        """Test CreateGoldenConfigTreeResponse serialization."""
        response_data = {"name": "serialize-tree", "device_type": "juniper_junos"}

        response = CreateGoldenConfigTreeResponse(**response_data)
        serialized = response.model_dump()

        assert serialized == response_data

    def test_response_json_serialization(self):
        """Test CreateGoldenConfigTreeResponse JSON serialization."""
        response_data = {"name": "json-tree", "device_type": "arista_eos"}

        response = CreateGoldenConfigTreeResponse(**response_data)
        json_str = response.model_dump_json()

        assert '"name":"json-tree"' in json_str
        assert '"device_type":"arista_eos"' in json_str


class TestAddGoldenConfigNodeResponse:
    """Test cases for AddGoldenConfigNodeResponse model."""

    def test_create_valid_response(self):
        """Test creating a valid AddGoldenConfigNodeResponse."""
        response_data = {
            "message": "Node added successfully to the Golden Configuration tree"
        }

        response = AddGoldenConfigNodeResponse(**response_data)

        assert (
            response.message
            == "Node added successfully to the Golden Configuration tree"
        )

    def test_create_response_with_various_messages(self):
        """Test creating response with various success messages."""
        messages = [
            "Node 'interface-config' added to tree 'cisco-base'",
            "Successfully added node to path 'base/routing/ospf'",
            "Node creation completed",
            "Configuration node added with template",
        ]

        for message in messages:
            response_data = {"message": message}
            response = AddGoldenConfigNodeResponse(**response_data)

            assert response.message == message

    def test_response_missing_message(self):
        """Test AddGoldenConfigNodeResponse validation with missing message."""
        response_data = {}

        with pytest.raises(ValidationError) as exc_info:
            AddGoldenConfigNodeResponse(**response_data)

        errors = exc_info.value.errors()
        assert len(errors) == 1
        assert errors[0]["type"] == "missing"
        assert errors[0]["loc"] == ("message",)

    def test_response_invalid_message_type(self):
        """Test AddGoldenConfigNodeResponse validation with invalid message type."""
        response_data = {"message": 12345}

        with pytest.raises(ValidationError) as exc_info:
            AddGoldenConfigNodeResponse(**response_data)

        errors = exc_info.value.errors()
        assert len(errors) == 1
        assert errors[0]["type"] == "string_type"
        assert errors[0]["loc"] == ("message",)

    def test_response_none_message(self):
        """Test AddGoldenConfigNodeResponse validation with None message."""
        response_data = {"message": None}

        with pytest.raises(ValidationError) as exc_info:
            AddGoldenConfigNodeResponse(**response_data)

        errors = exc_info.value.errors()
        assert len(errors) == 1
        assert errors[0]["type"] == "string_type"
        assert errors[0]["loc"] == ("message",)

    def test_response_empty_message(self):
        """Test AddGoldenConfigNodeResponse with empty message string."""
        response_data = {"message": ""}

        response = AddGoldenConfigNodeResponse(**response_data)

        assert response.message == ""

    def test_response_serialization(self):
        """Test AddGoldenConfigNodeResponse serialization."""
        response_data = {"message": "Node successfully added to configuration tree"}

        response = AddGoldenConfigNodeResponse(**response_data)
        serialized = response.model_dump()

        assert serialized == response_data

    def test_response_json_serialization(self):
        """Test AddGoldenConfigNodeResponse JSON serialization."""
        response_data = {"message": "Configuration node added successfully"}

        response = AddGoldenConfigNodeResponse(**response_data)
        json_str = response.model_dump_json()

        assert '"message":"Configuration node added successfully"' in json_str

    def test_response_with_special_characters(self):
        """Test AddGoldenConfigNodeResponse with special characters in message."""
        special_messages = [
            "Node 'test-node' added with template 'base/config'",
            "Success: Added node @path='/base/interfaces'",
            "Node creation completed with 100% success rate",
            "Added node with config: {'key': 'value'}",
        ]

        for message in special_messages:
            response_data = {"message": message}
            response = AddGoldenConfigNodeResponse(**response_data)

            assert response.message == message
