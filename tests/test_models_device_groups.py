# Copyright (c) 2025 Itential, Inc
# GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

import pytest
from pydantic import ValidationError

from itential_mcp.models.device_groups import (
    DeviceGroupElement,
    GetDeviceGroupsResponse,
    CreateDeviceGroupResponse,
    AddDevicesToGroupResponse,
    RemoveDevicesFromGroupResponse,
)


class TestDeviceGroupElement:
    """Test cases for DeviceGroupElement model"""

    def test_device_group_element_valid_creation(self):
        """Test creating DeviceGroupElement with valid data"""
        element = DeviceGroupElement(
            id="group-123",
            name="test-group",
            devices=["device1", "device2", "device3"],
            description="Test device group for unit testing",
        )

        assert element.object_id == "group-123"
        assert element.name == "test-group"
        assert element.devices == ["device1", "device2", "device3"]
        assert element.description == "Test device group for unit testing"

    def test_device_group_element_empty_devices_list(self):
        """Test DeviceGroupElement with empty devices list"""
        element = DeviceGroupElement(
            id="empty-group",
            name="empty-test",
            devices=[],
            description="Empty device group",
        )

        assert element.devices == []
        assert len(element.devices) == 0

    def test_device_group_element_default_devices_list(self):
        """Test DeviceGroupElement with default devices list"""
        element = DeviceGroupElement(
            id="default-group", name="default-test", description="Default device group"
        )

        assert element.devices == []
        assert isinstance(element.devices, list)

    def test_device_group_element_missing_required_fields(self):
        """Test DeviceGroupElement with missing required fields"""
        with pytest.raises(ValidationError) as exc_info:
            DeviceGroupElement()

        errors = exc_info.value.errors()
        required_fields = {"id", "name", "description"}
        missing_fields = {
            error["loc"][0] for error in errors if error["type"] == "missing"
        }

        assert required_fields == missing_fields

    def test_device_group_element_serialization_with_alias(self):
        """Test DeviceGroupElement serialization with alias"""
        element = DeviceGroupElement(
            id="serialize-group",
            name="serialize-test",
            devices=["dev1", "dev2"],
            description="Serialization test",
        )

        # Test model_dump() - should use field names
        model_dict = element.model_dump()
        assert "object_id" in model_dict
        assert "id" not in model_dict
        assert model_dict["object_id"] == "serialize-group"

        # Test model_dump(by_alias=True) - should use aliases
        alias_dict = element.model_dump(by_alias=True)
        assert "id" in alias_dict
        assert "object_id" not in alias_dict
        assert alias_dict["id"] == "serialize-group"

    def test_device_group_element_field_validation(self):
        """Test DeviceGroupElement field type validation"""
        # Test non-string object_id
        with pytest.raises(ValidationError):
            DeviceGroupElement(id=123, name="test", description="test", devices=[])

        # Test non-list devices
        with pytest.raises(ValidationError):
            DeviceGroupElement(
                id="test-id", name="test", description="test", devices="not-a-list"
            )

    def test_device_group_element_unicode_support(self):
        """Test DeviceGroupElement with Unicode characters"""
        element = DeviceGroupElement(
            id="测试组-123",
            name="测试设备组",
            devices=["设备1", "设备2", "устройство3"],
            description="Device group de test avec émojis 🌐📱",
        )

        assert element.object_id == "测试组-123"
        assert element.name == "测试设备组"
        assert "设备1" in element.devices
        assert "устройство3" in element.devices
        assert "🌐📱" in element.description

    def test_device_group_element_large_devices_list(self):
        """Test DeviceGroupElement with large number of devices"""
        large_devices_list = [f"device-{i:04d}" for i in range(1000)]

        element = DeviceGroupElement(
            id="large-group",
            name="large-device-group",
            devices=large_devices_list,
            description="Group with many devices",
        )

        assert len(element.devices) == 1000
        assert element.devices[0] == "device-0000"
        assert element.devices[-1] == "device-0999"

    def test_device_group_element_duplicate_devices(self):
        """Test DeviceGroupElement with duplicate devices"""
        devices_with_duplicates = [
            "device1",
            "device2",
            "device1",
            "device3",
            "device2",
        ]

        element = DeviceGroupElement(
            id="duplicate-group",
            name="duplicate-test",
            devices=devices_with_duplicates,
            description="Group with duplicate devices",
        )

        # Should preserve duplicates as-is (no automatic deduplication)
        assert len(element.devices) == 5
        assert element.devices.count("device1") == 2
        assert element.devices.count("device2") == 2

    def test_device_group_element_special_characters_in_devices(self):
        """Test DeviceGroupElement with special characters in device names"""
        special_devices = [
            "device-with-dashes",
            "device_with_underscores",
            "device.with.dots",
            "device:with:colons",
            "device@with@symbols",
        ]

        element = DeviceGroupElement(
            id="special-group",
            name="special-devices-test",
            devices=special_devices,
            description="Group with special device names",
        )

        assert all(device in element.devices for device in special_devices)

    def test_device_group_element_empty_strings(self):
        """Test DeviceGroupElement with empty string values"""
        element = DeviceGroupElement(id="", name="", devices=[""], description="")

        assert element.object_id == ""
        assert element.name == ""
        assert element.devices == [""]
        assert element.description == ""


class TestGetDeviceGroupsResponse:
    """Test cases for GetDeviceGroupsResponse model"""

    def test_get_device_groups_response_empty_list(self):
        """Test GetDeviceGroupsResponse with empty device groups list"""
        response = GetDeviceGroupsResponse(root=[])
        assert response.root == []

    def test_get_device_groups_response_single_group(self):
        """Test GetDeviceGroupsResponse with single device group"""
        group = DeviceGroupElement(
            id="single-group",
            name="single-test",
            devices=["device1"],
            description="Single device group",
        )

        response = GetDeviceGroupsResponse(root=[group])
        assert len(response.root) == 1
        assert response.root[0].name == "single-test"

    def test_get_device_groups_response_multiple_groups(self):
        """Test GetDeviceGroupsResponse with multiple device groups"""
        groups = [
            DeviceGroupElement(
                id=f"group-{i}",
                name=f"test-group-{i}",
                devices=[f"device-{i}-1", f"device-{i}-2"],
                description=f"Test device group {i}",
            )
            for i in range(5)
        ]

        response = GetDeviceGroupsResponse(root=groups)
        assert len(response.root) == 5

        for i, group in enumerate(response.root):
            assert group.name == f"test-group-{i}"
            assert group.object_id == f"group-{i}"

    def test_get_device_groups_response_mixed_group_sizes(self):
        """Test GetDeviceGroupsResponse with groups of different sizes"""
        groups = [
            DeviceGroupElement(
                id="empty-group",
                name="empty-group",
                devices=[],
                description="Empty group",
            ),
            DeviceGroupElement(
                id="small-group",
                name="small-group",
                devices=["device1"],
                description="Small group",
            ),
            DeviceGroupElement(
                id="large-group",
                name="large-group",
                devices=[f"device-{i}" for i in range(100)],
                description="Large group",
            ),
        ]

        response = GetDeviceGroupsResponse(root=groups)
        assert len(response.root) == 3
        assert len(response.root[0].devices) == 0
        assert len(response.root[1].devices) == 1
        assert len(response.root[2].devices) == 100

    def test_get_device_groups_response_serialization(self):
        """Test GetDeviceGroupsResponse serialization"""
        group = DeviceGroupElement(
            id="serialize-test",
            name="serialize-group",
            devices=["dev1", "dev2"],
            description="Serialization test",
        )

        response = GetDeviceGroupsResponse(root=[group])
        serialized = response.model_dump()

        # GetDeviceGroupsResponse is a RootModel, so it serializes directly as a list
        assert isinstance(serialized, list)
        assert len(serialized) == 1
        assert serialized[0]["name"] == "serialize-group"
        assert serialized[0]["object_id"] == "serialize-test"

    def test_get_device_groups_response_serialization_with_alias(self):
        """Test GetDeviceGroupsResponse serialization with aliases"""
        group = DeviceGroupElement(
            id="alias-test",
            name="alias-group",
            devices=["dev1"],
            description="Alias test",
        )

        response = GetDeviceGroupsResponse(root=[group])
        serialized = response.model_dump(by_alias=True)

        assert isinstance(serialized, list)
        assert len(serialized) == 1
        assert serialized[0]["id"] == "alias-test"
        assert "object_id" not in serialized[0]


class TestCreateDeviceGroupResponse:
    """Test cases for CreateDeviceGroupResponse model"""

    def test_create_device_group_response_valid_creation(self):
        """Test creating CreateDeviceGroupResponse with valid data"""
        response = CreateDeviceGroupResponse(
            id="created-group-123",
            name="created-test-group",
            message="Device group created successfully",
            status="active",
        )

        assert response.object_id == "created-group-123"
        assert response.name == "created-test-group"
        assert response.message == "Device group created successfully"
        assert response.status == "active"

    def test_create_device_group_response_missing_required_fields(self):
        """Test CreateDeviceGroupResponse with missing required fields"""
        with pytest.raises(ValidationError) as exc_info:
            CreateDeviceGroupResponse()

        errors = exc_info.value.errors()
        required_fields = {"id", "name", "message", "status"}
        missing_fields = {
            error["loc"][0] for error in errors if error["type"] == "missing"
        }

        assert required_fields == missing_fields

    def test_create_device_group_response_serialization_with_alias(self):
        """Test CreateDeviceGroupResponse serialization with alias"""
        response = CreateDeviceGroupResponse(
            id="alias-create-test",
            name="alias-create-group",
            message="Created with alias",
            status="created",
        )

        # Test model_dump() - should use field names
        model_dict = response.model_dump()
        assert "object_id" in model_dict
        assert "id" not in model_dict
        assert model_dict["object_id"] == "alias-create-test"

        # Test model_dump(by_alias=True) - should use aliases
        alias_dict = response.model_dump(by_alias=True)
        assert "id" in alias_dict
        assert "object_id" not in alias_dict
        assert alias_dict["id"] == "alias-create-test"

    @pytest.mark.parametrize(
        "status", ["active", "inactive", "pending", "created", "error", "unknown"]
    )
    def test_create_device_group_response_various_statuses(self, status):
        """Test CreateDeviceGroupResponse with various status values"""
        response = CreateDeviceGroupResponse(
            id="status-test",
            name="status-group",
            message=f"Group is {status}",
            status=status,
        )
        assert response.status == status

    def test_create_device_group_response_unicode_support(self):
        """Test CreateDeviceGroupResponse with Unicode characters"""
        response = CreateDeviceGroupResponse(
            id="unicode-组-123",
            name="测试组创建",
            message="Création réussie du groupe avec émojis ✅🎉",
            status="активный",
        )

        assert response.object_id == "unicode-组-123"
        assert response.name == "测试组创建"
        assert "✅🎉" in response.message
        assert response.status == "активный"

    def test_create_device_group_response_field_validation(self):
        """Test CreateDeviceGroupResponse field type validation"""
        # Test non-string object_id
        with pytest.raises(ValidationError):
            CreateDeviceGroupResponse(
                id=123, name="test", message="test", status="active"
            )


class TestAddDevicesToGroupResponse:
    """Test cases for AddDevicesToGroupResponse model"""

    def test_add_devices_to_group_response_valid_creation(self):
        """Test creating AddDevicesToGroupResponse with valid data"""
        response = AddDevicesToGroupResponse(
            status="success", message="Devices added successfully to the group"
        )

        assert response.status == "success"
        assert response.message == "Devices added successfully to the group"

    def test_add_devices_to_group_response_missing_required_fields(self):
        """Test AddDevicesToGroupResponse with missing required fields"""
        with pytest.raises(ValidationError) as exc_info:
            AddDevicesToGroupResponse()

        errors = exc_info.value.errors()
        required_fields = {"status", "message"}
        missing_fields = {
            error["loc"][0] for error in errors if error["type"] == "missing"
        }

        assert required_fields == missing_fields

    @pytest.mark.parametrize(
        "status", ["success", "failure", "partial", "error", "warning", "info"]
    )
    def test_add_devices_to_group_response_various_statuses(self, status):
        """Test AddDevicesToGroupResponse with various status values"""
        response = AddDevicesToGroupResponse(
            status=status, message=f"Operation completed with status: {status}"
        )
        assert response.status == status

    def test_add_devices_to_group_response_error_scenarios(self):
        """Test AddDevicesToGroupResponse for error scenarios"""
        error_response = AddDevicesToGroupResponse(
            status="error",
            message="Failed to add devices: Device 'invalid-device' not found",
        )

        assert error_response.status == "error"
        assert "Failed to add" in error_response.message
        assert "not found" in error_response.message

    def test_add_devices_to_group_response_partial_success(self):
        """Test AddDevicesToGroupResponse for partial success scenarios"""
        partial_response = AddDevicesToGroupResponse(
            status="partial",
            message="2 of 3 devices added successfully. Device 'offline-device' was unreachable.",
        )

        assert partial_response.status == "partial"
        assert "2 of 3" in partial_response.message
        assert "unreachable" in partial_response.message

    def test_add_devices_to_group_response_unicode_support(self):
        """Test AddDevicesToGroupResponse with Unicode characters"""
        response = AddDevicesToGroupResponse(
            status="успех",
            message="设备成功添加到组 ✅ Dispositifs ajoutés avec succès 🚀",
        )

        assert response.status == "успех"
        assert "设备成功添加" in response.message
        assert "✅" in response.message
        assert "🚀" in response.message

    def test_add_devices_to_group_response_serialization(self):
        """Test AddDevicesToGroupResponse serialization"""
        response = AddDevicesToGroupResponse(
            status="success", message="All devices added successfully"
        )

        expected_dict = {
            "status": "success",
            "message": "All devices added successfully",
        }

        assert response.model_dump() == expected_dict


class TestRemoveDevicesFromGroupResponse:
    """Test cases for RemoveDevicesFromGroupResponse model"""

    def test_remove_devices_from_group_response_valid_creation(self):
        """Test creating RemoveDevicesFromGroupResponse with valid data"""
        response = RemoveDevicesFromGroupResponse(
            status="success", message="3 devices removed successfully"
        )

        assert response.status == "success"
        assert response.message == "3 devices removed successfully"

    def test_remove_devices_from_group_response_missing_required_fields(self):
        """Test RemoveDevicesFromGroupResponse with missing required fields"""
        with pytest.raises(ValidationError) as exc_info:
            RemoveDevicesFromGroupResponse()

        errors = exc_info.value.errors()
        required_fields = {"status", "message"}
        missing_fields = {
            error["loc"][0] for error in errors if error["type"] == "missing"
        }

        assert required_fields == missing_fields

    @pytest.mark.parametrize("deleted_count", [0, 1, 5, 100, 1000])
    def test_remove_devices_from_group_response_various_counts(self, deleted_count):
        """Test RemoveDevicesFromGroupResponse with various deleted counts in message"""
        response = RemoveDevicesFromGroupResponse(
            status="success", message=f"{deleted_count} devices removed successfully"
        )
        assert f"{deleted_count} devices" in response.message

    def test_remove_devices_from_group_response_zero_deleted(self):
        """Test RemoveDevicesFromGroupResponse when no devices were deleted"""
        response = RemoveDevicesFromGroupResponse(
            status="warning", message="No devices were removed"
        )

        assert response.status == "warning"
        assert "No devices" in response.message

    def test_remove_devices_from_group_response_error_scenario(self):
        """Test RemoveDevicesFromGroupResponse for error scenarios"""
        error_response = RemoveDevicesFromGroupResponse(
            status="error",
            message="Failed to remove devices due to access restrictions",
        )

        assert error_response.status == "error"
        assert "Failed to remove" in error_response.message

    def test_remove_devices_from_group_response_partial_removal(self):
        """Test RemoveDevicesFromGroupResponse for partial removal"""
        partial_response = RemoveDevicesFromGroupResponse(
            status="partial",
            message="2 of 5 devices removed successfully",  # Out of 5 requested
        )

        assert partial_response.status == "partial"
        assert "2 of 5" in partial_response.message

    def test_remove_devices_from_group_response_field_validation(self):
        """Test RemoveDevicesFromGroupResponse field type validation"""
        # Test non-string message
        with pytest.raises(ValidationError):
            RemoveDevicesFromGroupResponse(
                status="success",
                message=123,  # Should be string
            )

        # Test non-string status
        with pytest.raises(ValidationError):
            RemoveDevicesFromGroupResponse(
                status=200,  # Should be string
                message="Test message",
            )

    def test_remove_devices_from_group_response_error_message(self):
        """Test RemoveDevicesFromGroupResponse with error message"""
        # Error message for failed operation
        response = RemoveDevicesFromGroupResponse(
            status="error", message="Failed to remove devices: insufficient permissions"
        )

        assert response.status == "error"
        assert "Failed to remove" in response.message

    def test_remove_devices_from_group_response_unicode_status(self):
        """Test RemoveDevicesFromGroupResponse with Unicode status and message"""
        response = RemoveDevicesFromGroupResponse(
            status="删除成功", message="5 台设备已成功移除 ✅"
        )

        assert response.status == "删除成功"
        assert "5 台设备" in response.message
        assert "✅" in response.message

    def test_remove_devices_from_group_response_serialization(self):
        """Test RemoveDevicesFromGroupResponse serialization"""
        response = RemoveDevicesFromGroupResponse(
            status="success", message="7 devices removed successfully"
        )

        expected_dict = {
            "status": "success",
            "message": "7 devices removed successfully",
        }

        assert response.model_dump() == expected_dict


class TestModelInteroperability:
    """Test cases for model interoperability and edge cases"""

    def test_all_models_have_proper_field_descriptions(self):
        """Test that all models have proper field descriptions"""
        models_to_test = [
            DeviceGroupElement,
            CreateDeviceGroupResponse,
            AddDevicesToGroupResponse,
            RemoveDevicesFromGroupResponse,
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
            DeviceGroupElement,
            GetDeviceGroupsResponse,
            CreateDeviceGroupResponse,
            AddDevicesToGroupResponse,
            RemoveDevicesFromGroupResponse,
        ]

        for model_class in models:
            schema = model_class.model_json_schema()
            assert "type" in schema

            # RootModels have different schema structure
            if model_class == GetDeviceGroupsResponse:
                assert "items" in schema
            else:
                assert "properties" in schema

    def test_model_equality(self):
        """Test model equality behavior"""
        group1 = DeviceGroupElement(
            id="test-id", name="test", devices=["dev1"], description="test"
        )
        group2 = DeviceGroupElement(
            id="test-id", name="test", devices=["dev1"], description="test"
        )
        group3 = DeviceGroupElement(
            id="different-id", name="test", devices=["dev1"], description="test"
        )

        assert group1 == group2
        assert group1 != group3

    def test_object_id_alias_consistency(self):
        """Test that object_id alias works consistently across models"""
        models_with_object_id = [DeviceGroupElement, CreateDeviceGroupResponse]

        for model_class in models_with_object_id:
            # Create instance with object_id parameter
            instance = model_class(
                id="test-id-123",
                name="test-name",
                **(
                    {"devices": [], "description": "test"}
                    if model_class == DeviceGroupElement
                    else {"message": "test", "status": "test"}
                ),
            )

            # Verify object_id is accessible
            assert instance.object_id == "test-id-123"

            # Verify serialization without alias uses object_id
            model_dict = instance.model_dump()
            assert "object_id" in model_dict
            assert "id" not in model_dict

            # Verify serialization with alias uses id
            alias_dict = instance.model_dump(by_alias=True)
            assert "id" in alias_dict
            assert "object_id" not in alias_dict
            assert alias_dict["id"] == "test-id-123"


class TestModelValidationEdgeCases:
    """Test edge cases and validation scenarios"""

    def test_extremely_long_field_values(self):
        """Test models with extremely long field values"""
        long_string = "x" * 10000

        group = DeviceGroupElement(
            id=long_string,
            name=long_string,
            devices=[long_string] * 100,
            description=long_string,
        )

        assert len(group.object_id) == 10000
        assert len(group.name) == 10000
        assert len(group.devices) == 100
        assert len(group.description) == 10000

    def test_special_characters_in_fields(self):
        """Test models with special characters in fields"""
        special_chars = "!@#$%^&*()[]{}|;':\",./<>?"

        create_response = CreateDeviceGroupResponse(
            id=special_chars,
            name=special_chars,
            message=special_chars,
            status=special_chars,
        )

        assert create_response.object_id == special_chars
        assert create_response.name == special_chars

    def test_empty_and_whitespace_strings(self):
        """Test models with empty and whitespace-only strings"""
        add_response = AddDevicesToGroupResponse(status="", message="   \t\n   ")

        assert add_response.status == ""
        assert add_response.message == "   \t\n   "

    def test_response_models_with_json_data(self):
        """Test response models that might contain JSON-like data in strings"""
        json_like_message = '{"result": "success", "devices_added": 5, "warnings": []}'

        response = AddDevicesToGroupResponse(
            status="success", message=json_like_message
        )

        assert response.message == json_like_message
        assert '"result": "success"' in response.message
