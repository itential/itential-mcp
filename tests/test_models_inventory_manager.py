# Copyright (c) 2025 Itential, Inc
# GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

import pytest
from pydantic import ValidationError

from itential_mcp.models.inventory_manager import (
    InventoryElement,
    GetInventoriesResponse,
    CreateInventoryResponse,
    DescribeInventoryResponse,
    AddNodesToInventoryResponse,
    DeleteInventoryResponse,
)


class TestInventoryElement:
    """Test cases for InventoryElement model"""

    def test_inventory_element_valid_creation(self):
        """Test creating InventoryElement with valid data"""
        element = InventoryElement(
            _id="inv-123",
            name="test-inventory",
            description="Test inventory for unit testing",
            nodeCount=5,
        )

        assert element.object_id == "inv-123"
        assert element.name == "test-inventory"
        assert element.description == "Test inventory for unit testing"
        assert element.node_count == 5

    def test_inventory_element_default_values(self):
        """Test InventoryElement with default values"""
        element = InventoryElement(
            _id="default-inv",
            name="default-test",
        )

        assert element.description == ""
        assert element.node_count == 0

    def test_inventory_element_missing_required_fields(self):
        """Test InventoryElement with missing required fields"""
        with pytest.raises(ValidationError) as exc_info:
            InventoryElement()

        errors = exc_info.value.errors()
        required_fields = {"_id", "name"}
        missing_fields = {
            error["loc"][0] for error in errors if error["type"] == "missing"
        }

        assert required_fields == missing_fields

    def test_inventory_element_serialization_with_alias(self):
        """Test InventoryElement serialization with alias"""
        element = InventoryElement(
            _id="serialize-inv",
            name="serialize-test",
            description="Serialization test",
            nodeCount=3,
        )

        # Test model_dump() - should use field names
        model_dict = element.model_dump()
        assert "object_id" in model_dict
        assert "_id" not in model_dict
        assert model_dict["object_id"] == "serialize-inv"
        assert "node_count" in model_dict
        assert "nodeCount" not in model_dict
        assert model_dict["node_count"] == 3

        # Test model_dump(by_alias=True) - should use aliases
        alias_dict = element.model_dump(by_alias=True)
        assert "_id" in alias_dict
        assert "object_id" not in alias_dict
        assert alias_dict["_id"] == "serialize-inv"
        assert "nodeCount" in alias_dict
        assert "node_count" not in alias_dict
        assert alias_dict["nodeCount"] == 3

    def test_inventory_element_field_validation(self):
        """Test InventoryElement field type validation"""
        # Test non-string object_id
        with pytest.raises(ValidationError):
            InventoryElement(_id=123, name="test")

        # Test non-integer node_count
        with pytest.raises(ValidationError):
            InventoryElement(_id="test-id", name="test", nodeCount="not-a-number")

    def test_inventory_element_unicode_support(self):
        """Test InventoryElement with Unicode characters"""
        element = InventoryElement(
            _id="测试清单-123",
            name="测试设备清单",
            description="Inventory de test avec émojis 🌐📱",
            nodeCount=2,
        )

        assert element.object_id == "测试清单-123"
        assert element.name == "测试设备清单"
        assert "🌐📱" in element.description

    def test_inventory_element_empty_strings(self):
        """Test InventoryElement with empty string values"""
        element = InventoryElement(_id="", name="", description="")

        assert element.object_id == ""
        assert element.name == ""
        assert element.description == ""

    def test_inventory_element_extra_fields_allowed(self):
        """Test InventoryElement allows extra fields"""
        element = InventoryElement(
            _id="extra-inv",
            name="extra-test",
            extraField="extra-value",
            anotherField=42,
        )

        assert element.object_id == "extra-inv"
        assert element.name == "extra-test"


class TestGetInventoriesResponse:
    """Test cases for GetInventoriesResponse model"""

    def test_get_inventories_response_empty_list(self):
        """Test GetInventoriesResponse with empty inventory list"""
        response = GetInventoriesResponse(root=[])
        assert response.root == []

    def test_get_inventories_response_single_inventory(self):
        """Test GetInventoriesResponse with single inventory"""
        inv = InventoryElement(
            _id="single-inv",
            name="single-test",
            description="Single inventory",
            nodeCount=1,
        )

        response = GetInventoriesResponse(root=[inv])
        assert len(response.root) == 1
        assert response.root[0].name == "single-test"

    def test_get_inventories_response_multiple_inventories(self):
        """Test GetInventoriesResponse with multiple inventories"""
        inventories = [
            InventoryElement(
                _id=f"inv-{i}",
                name=f"test-inventory-{i}",
                description=f"Test inventory {i}",
                nodeCount=i,
            )
            for i in range(5)
        ]

        response = GetInventoriesResponse(root=inventories)
        assert len(response.root) == 5

        for i, inv in enumerate(response.root):
            assert inv.name == f"test-inventory-{i}"
            assert inv.object_id == f"inv-{i}"
            assert inv.node_count == i

    def test_get_inventories_response_serialization(self):
        """Test GetInventoriesResponse serialization"""
        inv = InventoryElement(
            _id="serialize-test",
            name="serialize-inventory",
            description="Serialization test",
            nodeCount=10,
        )

        response = GetInventoriesResponse(root=[inv])
        serialized = response.model_dump()

        # GetInventoriesResponse is a RootModel, so it serializes directly as a list
        assert isinstance(serialized, list)
        assert len(serialized) == 1
        assert serialized[0]["name"] == "serialize-inventory"
        assert serialized[0]["object_id"] == "serialize-test"

    def test_get_inventories_response_serialization_with_alias(self):
        """Test GetInventoriesResponse serialization with aliases"""
        inv = InventoryElement(
            _id="alias-test",
            name="alias-inventory",
            description="Alias test",
            nodeCount=5,
        )

        response = GetInventoriesResponse(root=[inv])
        serialized = response.model_dump(by_alias=True)

        assert isinstance(serialized, list)
        assert len(serialized) == 1
        assert serialized[0]["_id"] == "alias-test"
        assert "object_id" not in serialized[0]
        assert serialized[0]["nodeCount"] == 5
        assert "node_count" not in serialized[0]


class TestCreateInventoryResponse:
    """Test cases for CreateInventoryResponse model"""

    def test_create_inventory_response_valid_creation(self):
        """Test creating CreateInventoryResponse with valid data"""
        response = CreateInventoryResponse(
            _id="created-inv-123",
            name="created-test-inventory",
            message="Inventory created successfully",
        )

        assert response.object_id == "created-inv-123"
        assert response.name == "created-test-inventory"
        assert response.message == "Inventory created successfully"

    def test_create_inventory_response_default_message(self):
        """Test CreateInventoryResponse with default message"""
        response = CreateInventoryResponse(
            _id="default-msg-inv",
            name="default-message-test",
        )

        assert response.message == "Inventory created successfully"

    def test_create_inventory_response_missing_required_fields(self):
        """Test CreateInventoryResponse with missing required fields"""
        with pytest.raises(ValidationError) as exc_info:
            CreateInventoryResponse()

        errors = exc_info.value.errors()
        required_fields = {"_id", "name"}
        missing_fields = {
            error["loc"][0] for error in errors if error["type"] == "missing"
        }

        assert required_fields == missing_fields

    def test_create_inventory_response_serialization_with_alias(self):
        """Test CreateInventoryResponse serialization with alias"""
        response = CreateInventoryResponse(
            _id="alias-create-test",
            name="alias-create-inventory",
            message="Created with alias",
        )

        # Test model_dump() - should use field names
        model_dict = response.model_dump()
        assert "object_id" in model_dict
        assert "_id" not in model_dict
        assert model_dict["object_id"] == "alias-create-test"

        # Test model_dump(by_alias=True) - should use aliases
        alias_dict = response.model_dump(by_alias=True)
        assert "_id" in alias_dict
        assert "object_id" not in alias_dict
        assert alias_dict["_id"] == "alias-create-test"

    def test_create_inventory_response_unicode_support(self):
        """Test CreateInventoryResponse with Unicode characters"""
        response = CreateInventoryResponse(
            _id="unicode-清单-123",
            name="测试清单创建",
            message="Création réussie de l'inventaire ✅🎉",
        )

        assert response.object_id == "unicode-清单-123"
        assert response.name == "测试清单创建"
        assert "✅🎉" in response.message

    def test_create_inventory_response_field_validation(self):
        """Test CreateInventoryResponse field type validation"""
        # Test non-string object_id
        with pytest.raises(ValidationError):
            CreateInventoryResponse(_id=123, name="test", message="test")

    def test_create_inventory_response_extra_fields_allowed(self):
        """Test CreateInventoryResponse allows extra fields"""
        response = CreateInventoryResponse(
            _id="extra-inv",
            name="extra-test",
            message="test",
            extraField="extra-value",
        )

        assert response.object_id == "extra-inv"


class TestDescribeInventoryResponse:
    """Test cases for DescribeInventoryResponse model"""

    def test_describe_inventory_response_valid_creation(self):
        """Test creating DescribeInventoryResponse with valid data"""
        response = DescribeInventoryResponse(
            _id="desc-inv-123",
            name="described-inventory",
            description="A described inventory",
            groups=["group1", "group2"],
            actions=[{"name": "action1", "type": "backup"}],
            tags=["production", "critical"],
            nodes=[
                {
                    "name": "core-router-1",
                    "attributes": {
                        "itential_host": "10.1.1.1",
                        "itential_platform": "iosxr",
                    },
                    "tags": ["core"],
                },
            ],
        )

        assert response.object_id == "desc-inv-123"
        assert response.name == "described-inventory"
        assert response.description == "A described inventory"
        assert response.groups == ["group1", "group2"]
        assert len(response.actions) == 1
        assert response.actions[0]["name"] == "action1"
        assert response.tags == ["production", "critical"]
        assert len(response.nodes) == 1
        assert response.nodes[0]["name"] == "core-router-1"
        assert response.nodes[0]["attributes"]["itential_host"] == "10.1.1.1"

    def test_describe_inventory_response_default_values(self):
        """Test DescribeInventoryResponse with default values"""
        response = DescribeInventoryResponse(
            _id="default-desc-inv",
            name="default-describe-test",
        )

        assert response.description == ""
        assert response.groups == []
        assert response.actions == []
        assert response.tags == []
        assert response.nodes == []

    def test_describe_inventory_response_with_multiple_nodes(self):
        """Test DescribeInventoryResponse with multiple nodes including tags"""
        nodes = [
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
                "name": "edge-switch-1",
                "attributes": {
                    "itential_host": "10.2.1.1",
                    "itential_platform": "nxos",
                    "cluster_id": "cluster_west",
                },
            },
        ]

        response = DescribeInventoryResponse(
            _id="multi-node",
            name="multi-node-test",
            nodes=nodes,
        )

        assert len(response.nodes) == 2
        assert response.nodes[0]["name"] == "core-router-1"
        assert response.nodes[0]["tags"] == ["core", "datacenter-1"]
        assert response.nodes[1]["name"] == "edge-switch-1"
        assert "tags" not in response.nodes[1]

    def test_describe_inventory_response_missing_required_fields(self):
        """Test DescribeInventoryResponse with missing required fields"""
        with pytest.raises(ValidationError) as exc_info:
            DescribeInventoryResponse()

        errors = exc_info.value.errors()
        required_fields = {"_id", "name"}
        missing_fields = {
            error["loc"][0] for error in errors if error["type"] == "missing"
        }

        assert required_fields == missing_fields

    def test_describe_inventory_response_serialization_with_alias(self):
        """Test DescribeInventoryResponse serialization with alias"""
        response = DescribeInventoryResponse(
            _id="alias-desc-test",
            name="alias-describe-inventory",
            groups=["Solutions Engineering"],
        )

        # Test model_dump() - should use field names
        model_dict = response.model_dump()
        assert "object_id" in model_dict
        assert "_id" not in model_dict

        # Test model_dump(by_alias=True) - should use aliases
        alias_dict = response.model_dump(by_alias=True)
        assert "_id" in alias_dict
        assert "object_id" not in alias_dict

    def test_describe_inventory_response_empty_groups(self):
        """Test DescribeInventoryResponse with empty groups"""
        response = DescribeInventoryResponse(
            _id="empty-groups",
            name="empty-groups-test",
            groups=[],
        )

        assert response.groups == []

    def test_describe_inventory_response_multiple_actions(self):
        """Test DescribeInventoryResponse with multiple actions"""
        actions = [
            {"name": "backup", "type": "backup"},
            {"name": "compliance", "type": "compliance"},
            {"name": "upgrade", "type": "upgrade"},
        ]

        response = DescribeInventoryResponse(
            _id="multi-action",
            name="multi-action-test",
            actions=actions,
        )

        assert len(response.actions) == 3

    def test_describe_inventory_response_extra_fields_allowed(self):
        """Test DescribeInventoryResponse allows extra fields"""
        response = DescribeInventoryResponse(
            _id="extra-inv",
            name="extra-test",
            extraField="extra-value",
        )

        assert response.object_id == "extra-inv"


class TestAddNodesToInventoryResponse:
    """Test cases for AddNodesToInventoryResponse model"""

    def test_add_nodes_response_valid_creation(self):
        """Test creating AddNodesToInventoryResponse with valid data"""
        response = AddNodesToInventoryResponse(
            status="Success",
            message="Nodes added successfully",
        )

        assert response.status == "Success"
        assert response.message == "Nodes added successfully"

    def test_add_nodes_response_missing_required_fields(self):
        """Test AddNodesToInventoryResponse with missing required fields"""
        with pytest.raises(ValidationError) as exc_info:
            AddNodesToInventoryResponse()

        errors = exc_info.value.errors()
        required_fields = {"status", "message"}
        missing_fields = {
            error["loc"][0] for error in errors if error["type"] == "missing"
        }

        assert required_fields == missing_fields

    @pytest.mark.parametrize(
        "status", ["Success", "Error", "Partial", "pending", "unknown"]
    )
    def test_add_nodes_response_various_statuses(self, status):
        """Test AddNodesToInventoryResponse with various status values"""
        response = AddNodesToInventoryResponse(
            status=status,
            message=f"Operation status: {status}",
        )
        assert response.status == status

    def test_add_nodes_response_error_scenario(self):
        """Test AddNodesToInventoryResponse for error scenarios"""
        error_response = AddNodesToInventoryResponse(
            status="Error",
            message="Failed to add nodes due to invalid attributes",
        )

        assert error_response.status == "Error"
        assert "Failed to add nodes" in error_response.message

    def test_add_nodes_response_field_validation(self):
        """Test AddNodesToInventoryResponse field type validation"""
        # Test non-string message
        with pytest.raises(ValidationError):
            AddNodesToInventoryResponse(
                status="Success",
                message=123,
            )

        # Test non-string status
        with pytest.raises(ValidationError):
            AddNodesToInventoryResponse(
                status=200,
                message="Test message",
            )

    def test_add_nodes_response_unicode_status(self):
        """Test AddNodesToInventoryResponse with Unicode status and message"""
        response = AddNodesToInventoryResponse(
            status="添加成功", message="节点已成功添加到清单 ✅"
        )

        assert response.status == "添加成功"
        assert "✅" in response.message

    def test_add_nodes_response_serialization(self):
        """Test AddNodesToInventoryResponse serialization"""
        response = AddNodesToInventoryResponse(
            status="Success", message="Nodes added successfully"
        )

        expected_dict = {
            "status": "Success",
            "message": "Nodes added successfully",
        }

        assert response.model_dump() == expected_dict


class TestDeleteInventoryResponse:
    """Test cases for DeleteInventoryResponse model"""

    def test_delete_inventory_response_valid_creation(self):
        """Test creating DeleteInventoryResponse with valid data"""
        response = DeleteInventoryResponse(
            status="Success",
            message="Inventory deleted successfully",
        )

        assert response.status == "Success"
        assert response.message == "Inventory deleted successfully"

    def test_delete_inventory_response_missing_required_fields(self):
        """Test DeleteInventoryResponse with missing required fields"""
        with pytest.raises(ValidationError) as exc_info:
            DeleteInventoryResponse()

        errors = exc_info.value.errors()
        required_fields = {"status", "message"}
        missing_fields = {
            error["loc"][0] for error in errors if error["type"] == "missing"
        }

        assert required_fields == missing_fields

    @pytest.mark.parametrize(
        "status", ["Success", "Error", "Partial", "pending", "unknown"]
    )
    def test_delete_inventory_response_various_statuses(self, status):
        """Test DeleteInventoryResponse with various status values"""
        response = DeleteInventoryResponse(
            status=status,
            message=f"Operation status: {status}",
        )
        assert response.status == status

    def test_delete_inventory_response_error_scenario(self):
        """Test DeleteInventoryResponse for error scenarios"""
        error_response = DeleteInventoryResponse(
            status="Error",
            message="Failed to delete inventory due to access restrictions",
        )

        assert error_response.status == "Error"
        assert "Failed to delete" in error_response.message

    def test_delete_inventory_response_field_validation(self):
        """Test DeleteInventoryResponse field type validation"""
        # Test non-string message
        with pytest.raises(ValidationError):
            DeleteInventoryResponse(
                status="Success",
                message=123,
            )

        # Test non-string status
        with pytest.raises(ValidationError):
            DeleteInventoryResponse(
                status=200,
                message="Test message",
            )

    def test_delete_inventory_response_unicode_status(self):
        """Test DeleteInventoryResponse with Unicode status and message"""
        response = DeleteInventoryResponse(
            status="删除成功", message="清单已成功删除 ✅"
        )

        assert response.status == "删除成功"
        assert "✅" in response.message

    def test_delete_inventory_response_serialization(self):
        """Test DeleteInventoryResponse serialization"""
        response = DeleteInventoryResponse(
            status="Success", message="Inventory deleted successfully"
        )

        expected_dict = {
            "status": "Success",
            "message": "Inventory deleted successfully",
        }

        assert response.model_dump() == expected_dict


class TestModelInteroperability:
    """Test cases for model interoperability and edge cases"""

    def test_all_models_have_proper_field_descriptions(self):
        """Test that all models have proper field descriptions"""
        models_to_test = [
            InventoryElement,
            CreateInventoryResponse,
            DescribeInventoryResponse,
            AddNodesToInventoryResponse,
            DeleteInventoryResponse,
        ]

        for model_class in models_to_test:
            schema = model_class.model_json_schema()
            properties = schema["properties"]

            for field_name, field_info in properties.items():
                assert "description" in field_info
                assert len(field_info["description"]) > 0

    def test_json_schema_generation(self):
        """Test JSON schema generation for all models"""
        models = [
            InventoryElement,
            GetInventoriesResponse,
            CreateInventoryResponse,
            DescribeInventoryResponse,
            AddNodesToInventoryResponse,
            DeleteInventoryResponse,
        ]

        for model_class in models:
            schema = model_class.model_json_schema()
            assert "type" in schema

            # RootModels have different schema structure
            if model_class == GetInventoriesResponse:
                assert "items" in schema
            else:
                assert "properties" in schema

    def test_model_equality(self):
        """Test model equality behavior"""
        inv1 = InventoryElement(
            _id="test-id", name="test", description="test", nodeCount=1
        )
        inv2 = InventoryElement(
            _id="test-id", name="test", description="test", nodeCount=1
        )
        inv3 = InventoryElement(
            _id="different-id", name="test", description="test", nodeCount=1
        )

        assert inv1 == inv2
        assert inv1 != inv3

    def test_object_id_alias_consistency(self):
        """Test that object_id alias works consistently across models"""
        models_with_object_id = [
            InventoryElement,
            CreateInventoryResponse,
            DescribeInventoryResponse,
        ]

        for model_class in models_with_object_id:
            # Create instance with alias parameter
            instance = model_class(
                _id="test-id-123",
                name="test-name",
            )

            # Verify object_id is accessible
            assert instance.object_id == "test-id-123"

            # Verify serialization without alias uses object_id
            model_dict = instance.model_dump()
            assert "object_id" in model_dict
            assert "_id" not in model_dict

            # Verify serialization with alias uses _id
            alias_dict = instance.model_dump(by_alias=True)
            assert "_id" in alias_dict
            assert "object_id" not in alias_dict
            assert alias_dict["_id"] == "test-id-123"


class TestModelValidationEdgeCases:
    """Test edge cases and validation scenarios"""

    def test_extremely_long_field_values(self):
        """Test models with extremely long field values"""
        long_string = "x" * 10000

        inv = InventoryElement(
            _id=long_string,
            name=long_string,
            description=long_string,
            nodeCount=999999,
        )

        assert len(inv.object_id) == 10000
        assert len(inv.name) == 10000
        assert len(inv.description) == 10000

    def test_special_characters_in_fields(self):
        """Test models with special characters in fields"""
        special_chars = "!@#$%^&*()[]{}|;':\",./<>?"

        create_response = CreateInventoryResponse(
            _id=special_chars,
            name=special_chars,
            message=special_chars,
        )

        assert create_response.object_id == special_chars
        assert create_response.name == special_chars

    def test_empty_and_whitespace_strings(self):
        """Test models with empty and whitespace-only strings"""
        delete_response = DeleteInventoryResponse(status="", message="   \t\n   ")

        assert delete_response.status == ""
        assert delete_response.message == "   \t\n   "

    def test_response_models_with_json_data(self):
        """Test response models that might contain JSON-like data in strings"""
        json_like_message = (
            '{"result": "success", "inventories_created": 1, "warnings": []}'
        )

        response = DeleteInventoryResponse(status="Success", message=json_like_message)

        assert response.message == json_like_message
        assert '"result": "success"' in response.message
