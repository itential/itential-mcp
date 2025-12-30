# Copyright (c) 2025 Itential, Inc
# GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

import pytest
from pydantic import ValidationError

from itential_mcp.models.integrations import (
    GetIntegrationModelsElement,
    GetIntegrationModelsResponse,
    CreateIntegrationModelResponse,
    GetIntegrationsElement,
    GetIntegrationsResponse,
)


class TestGetIntegrationModelsElement:
    """Test cases for GetIntegrationModelsElement model"""

    def test_get_integration_models_element_valid_creation(self):
        """Test creating GetIntegrationModelsElement with valid data"""
        element = GetIntegrationModelsElement(
            id="test-model:1.0.0",
            title="test-model",
            version="1.0.0",
            description="Test integration model",
        )

        assert element.id == "test-model:1.0.0"
        assert element.title == "test-model"
        assert element.version == "1.0.0"
        assert element.description == "Test integration model"

    def test_get_integration_models_element_with_none_description(self):
        """Test creating GetIntegrationModelsElement with None description"""
        element = GetIntegrationModelsElement(
            id="test-model:2.0.0", title="test-model", version="2.0.0", description=None
        )

        assert element.id == "test-model:2.0.0"
        assert element.title == "test-model"
        assert element.version == "2.0.0"
        assert element.description is None

    def test_get_integration_models_element_without_description(self):
        """Test creating GetIntegrationModelsElement without description field"""
        element = GetIntegrationModelsElement(
            id="test-model:3.0.0", title="test-model", version="3.0.0"
        )

        assert element.id == "test-model:3.0.0"
        assert element.title == "test-model"
        assert element.version == "3.0.0"
        assert element.description is None

    def test_get_integration_models_element_missing_required_fields(self):
        """Test GetIntegrationModelsElement with missing required fields"""
        with pytest.raises(ValidationError) as exc_info:
            GetIntegrationModelsElement()

        errors = exc_info.value.errors()
        required_fields = {"id", "title", "version"}
        missing_fields = {
            error["loc"][0] for error in errors if error["type"] == "missing"
        }

        assert required_fields == missing_fields

    def test_get_integration_models_element_serialization(self):
        """Test GetIntegrationModelsElement serialization to dict"""
        element = GetIntegrationModelsElement(
            id="serialize-test:1.5.0",
            title="serialize-test",
            version="1.5.0",
            description="Serialization test model",
        )

        expected_dict = {
            "id": "serialize-test:1.5.0",
            "title": "serialize-test",
            "version": "1.5.0",
            "description": "Serialization test model",
        }

        assert element.model_dump() == expected_dict

    def test_get_integration_models_element_serialization_with_none_description(self):
        """Test GetIntegrationModelsElement serialization with None description"""
        element = GetIntegrationModelsElement(
            id="none-test:1.0.0", title="none-test", version="1.0.0", description=None
        )

        serialized = element.model_dump()
        assert serialized["description"] is None

    def test_get_integration_models_element_json_serialization(self):
        """Test GetIntegrationModelsElement JSON serialization"""
        element = GetIntegrationModelsElement(
            id="json-test:2.1.0",
            title="json-test",
            version="2.1.0",
            description="JSON serialization test",
        )

        json_str = element.model_dump_json()
        assert '"id":"json-test:2.1.0"' in json_str
        assert '"title":"json-test"' in json_str
        assert '"version":"2.1.0"' in json_str

    def test_get_integration_models_element_field_validation(self):
        """Test GetIntegrationModelsElement field type validation"""
        # Test non-string id
        with pytest.raises(ValidationError):
            GetIntegrationModelsElement(id=123, title="test", version="1.0.0")

        # Test non-string title
        with pytest.raises(ValidationError):
            GetIntegrationModelsElement(id="test:1.0.0", title=456, version="1.0.0")

        # Test non-string version
        with pytest.raises(ValidationError):
            GetIntegrationModelsElement(id="test:1.0.0", title="test", version=789)

    def test_get_integration_models_element_empty_strings(self):
        """Test GetIntegrationModelsElement with empty string values"""
        element = GetIntegrationModelsElement(
            id="", title="", version="", description=""
        )

        assert element.id == ""
        assert element.title == ""
        assert element.version == ""
        assert element.description == ""

    def test_get_integration_models_element_whitespace_strings(self):
        """Test GetIntegrationModelsElement with whitespace-only strings"""
        element = GetIntegrationModelsElement(
            id="   ", title="\t", version="\n", description="  \t\n  "
        )

        assert element.id == "   "
        assert element.title == "\t"
        assert element.version == "\n"
        assert element.description == "  \t\n  "

    def test_get_integration_models_element_unicode_support(self):
        """Test GetIntegrationModelsElement with Unicode characters"""
        element = GetIntegrationModelsElement(
            id="测试模型:1.0.0",
            title="测试模型",
            version="1.0.0-α",
            description="Modèle de test avec émojis 🚀",
        )

        assert element.id == "测试模型:1.0.0"
        assert element.title == "测试模型"
        assert element.version == "1.0.0-α"
        assert element.description == "Modèle de test avec émojis 🚀"

    def test_get_integration_models_element_realistic_data(self):
        """Test GetIntegrationModelsElement with realistic OpenAPI-style data"""
        element = GetIntegrationModelsElement(
            id="petstore:3.0.0",
            title="Swagger Petstore",
            version="3.0.0",
            description="This is a sample server Petstore server",
        )

        assert element.id == "petstore:3.0.0"
        assert element.title == "Swagger Petstore"
        assert element.version == "3.0.0"
        assert "Petstore server" in element.description


class TestGetIntegrationModelsResponse:
    """Test cases for GetIntegrationModelsResponse model"""

    def test_get_integration_models_response_empty_list(self):
        """Test GetIntegrationModelsResponse with empty integration models list"""
        response = GetIntegrationModelsResponse(root=[])
        assert response.root == []

    def test_get_integration_models_response_single_model(self):
        """Test GetIntegrationModelsResponse with single integration model"""
        model = GetIntegrationModelsElement(
            id="single-model:1.0.0",
            title="single-model",
            version="1.0.0",
            description="Single integration model",
        )

        response = GetIntegrationModelsResponse(root=[model])
        assert len(response.root) == 1
        assert response.root[0].id == "single-model:1.0.0"

    def test_get_integration_models_response_multiple_models(self):
        """Test GetIntegrationModelsResponse with multiple integration models"""
        models = [
            GetIntegrationModelsElement(
                id=f"model-{i}:1.0.0",
                title=f"model-{i}",
                version="1.0.0",
                description=f"Test integration model {i}",
            )
            for i in range(5)
        ]

        response = GetIntegrationModelsResponse(root=models)
        assert len(response.root) == 5

        for i, model in enumerate(response.root):
            assert model.id == f"model-{i}:1.0.0"
            assert model.title == f"model-{i}"

    def test_get_integration_models_response_mixed_descriptions(self):
        """Test GetIntegrationModelsResponse with models having different description states"""
        models = [
            GetIntegrationModelsElement(
                id="with-desc:1.0.0",
                title="with-desc",
                version="1.0.0",
                description="Model with description",
            ),
            GetIntegrationModelsElement(
                id="without-desc:1.0.0",
                title="without-desc",
                version="1.0.0",
                description=None,
            ),
            GetIntegrationModelsElement(
                id="empty-desc:1.0.0",
                title="empty-desc",
                version="1.0.0",
                description="",
            ),
        ]

        response = GetIntegrationModelsResponse(root=models)
        descriptions = [model.description for model in response.root]

        assert "Model with description" in descriptions
        assert None in descriptions
        assert "" in descriptions

    def test_get_integration_models_response_serialization(self):
        """Test GetIntegrationModelsResponse serialization"""
        model = GetIntegrationModelsElement(
            id="serialize-test:2.0.0",
            title="serialize-test",
            version="2.0.0",
            description="Serialization test",
        )

        response = GetIntegrationModelsResponse(root=[model])
        serialized = response.model_dump()

        # GetIntegrationModelsResponse is a RootModel, so it serializes directly as a list
        assert isinstance(serialized, list)
        assert len(serialized) == 1
        assert serialized[0]["id"] == "serialize-test:2.0.0"

    def test_get_integration_models_response_invalid_model_data(self):
        """Test GetIntegrationModelsResponse with invalid model data"""
        with pytest.raises(ValidationError):
            GetIntegrationModelsResponse(
                root=[
                    {
                        "id": "test:1.0.0",
                        "title": "test",
                        # Missing required version field
                        "description": "test",
                    }
                ]
            )

    def test_get_integration_models_response_iteration(self):
        """Test that GetIntegrationModelsResponse can be iterated"""
        models = [
            GetIntegrationModelsElement(
                id=f"iter-{i}:1.0.0",
                title=f"iter-{i}",
                version="1.0.0",
                description=f"Iterator test {i}",
            )
            for i in range(3)
        ]

        response = GetIntegrationModelsResponse(root=models)

        # Test direct access
        assert len(response.root) == 3

        # Test iteration
        ids = [model.id for model in response.root]
        assert ids == ["iter-0:1.0.0", "iter-1:1.0.0", "iter-2:1.0.0"]

    def test_get_integration_models_response_different_versions(self):
        """Test GetIntegrationModelsResponse with models having different versions"""
        models = [
            GetIntegrationModelsElement(
                id="api:1.0.0",
                title="api",
                version="1.0.0",
                description="Version 1.0.0",
            ),
            GetIntegrationModelsElement(
                id="api:2.0.0",
                title="api",
                version="2.0.0",
                description="Version 2.0.0",
            ),
            GetIntegrationModelsElement(
                id="api:3.0.0-beta",
                title="api",
                version="3.0.0-beta",
                description="Beta version",
            ),
        ]

        response = GetIntegrationModelsResponse(root=models)
        versions = [model.version for model in response.root]

        assert "1.0.0" in versions
        assert "2.0.0" in versions
        assert "3.0.0-beta" in versions


class TestCreateIntegrationModelResponse:
    """Test cases for CreateIntegrationModelResponse model"""

    @pytest.mark.parametrize("status", ["OK", "CREATED"])
    def test_create_integration_model_response_valid_statuses(self, status):
        """Test CreateIntegrationModelResponse with valid status values"""
        response = CreateIntegrationModelResponse(status=status, message="Test message")

        assert response.status == status
        assert response.message == "Test message"

    def test_create_integration_model_response_invalid_status(self):
        """Test CreateIntegrationModelResponse with invalid status"""
        with pytest.raises(ValidationError) as exc_info:
            CreateIntegrationModelResponse(status="INVALID", message="Test message")

        assert "Input should be 'OK' or 'CREATED'" in str(exc_info.value)

    def test_create_integration_model_response_missing_fields(self):
        """Test CreateIntegrationModelResponse with missing required fields"""
        with pytest.raises(ValidationError) as exc_info:
            CreateIntegrationModelResponse()

        errors = exc_info.value.errors()
        missing_fields = {
            error["loc"][0] for error in errors if error["type"] == "missing"
        }

        assert {"status", "message"} == missing_fields

    def test_create_integration_model_response_serialization(self):
        """Test CreateIntegrationModelResponse serialization"""
        response = CreateIntegrationModelResponse(
            status="CREATED", message="Integration model created successfully"
        )

        serialized = response.model_dump()
        expected = {
            "status": "CREATED",
            "message": "Integration model created successfully",
        }

        assert serialized == expected

    def test_create_integration_model_response_json_serialization(self):
        """Test CreateIntegrationModelResponse JSON serialization"""
        response = CreateIntegrationModelResponse(
            status="OK", message="Integration model already exists"
        )

        json_str = response.model_dump_json()
        assert '"status":"OK"' in json_str
        assert '"message":"Integration model already exists"' in json_str

    def test_create_integration_model_response_field_validation(self):
        """Test CreateIntegrationModelResponse field type validation"""
        # Test non-string message
        with pytest.raises(ValidationError):
            CreateIntegrationModelResponse(status="OK", message=123)

    def test_create_integration_model_response_empty_message(self):
        """Test CreateIntegrationModelResponse with empty message"""
        response = CreateIntegrationModelResponse(status="CREATED", message="")

        assert response.status == "CREATED"
        assert response.message == ""

    def test_create_integration_model_response_long_message(self):
        """Test CreateIntegrationModelResponse with very long message"""
        long_message = "Error: " + "x" * 1000

        response = CreateIntegrationModelResponse(status="OK", message=long_message)

        assert response.status == "OK"
        assert len(response.message) == len(long_message)

    def test_create_integration_model_response_unicode_message(self):
        """Test CreateIntegrationModelResponse with Unicode characters in message"""
        unicode_message = "Modèle créé avec succès 🎉"

        response = CreateIntegrationModelResponse(
            status="CREATED", message=unicode_message
        )

        assert response.status == "CREATED"
        assert response.message == unicode_message

    def test_create_integration_model_response_realistic_messages(self):
        """Test CreateIntegrationModelResponse with realistic messages"""
        # Success case
        success_response = CreateIntegrationModelResponse(
            status="CREATED",
            message="Integration model 'petstore:3.0.0' created successfully",
        )

        assert success_response.status == "CREATED"
        assert "petstore:3.0.0" in success_response.message

        # Already exists case
        exists_response = CreateIntegrationModelResponse(
            status="OK", message="Integration model 'petstore:3.0.0' already exists"
        )

        assert exists_response.status == "OK"
        assert "already exists" in exists_response.message


class TestModelInteroperability:
    """Test cases for model interoperability and edge cases"""

    def test_all_models_have_consistent_literal_types(self):
        """Test that status literals are properly defined"""
        # Test valid status values for CreateIntegrationModelResponse
        for status in ["OK", "CREATED"]:
            response = CreateIntegrationModelResponse(
                status=status, message="Test message"
            )
            assert response.status == status

    def test_integration_models_response_from_elements(self):
        """Test creating response from individual elements"""
        elements = [
            GetIntegrationModelsElement(
                id=f"api-{i}:1.{i}.0",
                title=f"api-{i}",
                version=f"1.{i}.0",
                description=f"API version {i}",
            )
            for i in range(3)
        ]

        response = GetIntegrationModelsResponse(root=elements)

        assert len(response.root) == 3
        for i, element in enumerate(response.root):
            assert element.id == f"api-{i}:1.{i}.0"
            assert element.title == f"api-{i}"
            assert element.version == f"1.{i}.0"

    def test_model_field_descriptions_exist(self):
        """Test that all models have proper field descriptions"""
        # Test GetIntegrationModelsElement
        element_schema = GetIntegrationModelsElement.model_json_schema()
        properties = element_schema["properties"]

        for field in ["id", "title", "version", "description"]:
            assert field in properties
            assert "description" in properties[field]
            assert len(properties[field]["description"]) > 0

        # Test CreateIntegrationModelResponse
        create_schema = CreateIntegrationModelResponse.model_json_schema()
        properties = create_schema["properties"]

        for field in ["status", "message"]:
            assert field in properties
            assert "description" in properties[field]
            assert len(properties[field]["description"]) > 0

    def test_json_schema_generation(self):
        """Test JSON schema generation for all models"""
        models = [
            GetIntegrationModelsElement,
            GetIntegrationModelsResponse,
            CreateIntegrationModelResponse,
        ]

        for model_class in models:
            schema = model_class.model_json_schema()
            assert "type" in schema

            # GetIntegrationModelsResponse is a RootModel which has different schema structure
            if model_class == GetIntegrationModelsResponse:
                # RootModel schema has "items" instead of "properties"
                assert "items" in schema
            else:
                assert "properties" in schema

    def test_model_equality_behavior(self):
        """Test model equality behavior"""
        element1 = GetIntegrationModelsElement(
            id="test:1.0.0", title="test", version="1.0.0", description="Test model"
        )
        element2 = GetIntegrationModelsElement(
            id="test:1.0.0", title="test", version="1.0.0", description="Test model"
        )
        element3 = GetIntegrationModelsElement(
            id="different:1.0.0",
            title="different",
            version="1.0.0",
            description="Different model",
        )

        assert element1 == element2
        assert element1 != element3

        response1 = CreateIntegrationModelResponse(status="OK", message="Test")
        response2 = CreateIntegrationModelResponse(status="OK", message="Test")
        response3 = CreateIntegrationModelResponse(status="CREATED", message="Test")

        assert response1 == response2
        assert response1 != response3


class TestModelValidationEdgeCases:
    """Test edge cases and validation scenarios"""

    def test_extremely_long_field_values(self):
        """Test models with extremely long field values"""
        long_string = "x" * 10000

        element = GetIntegrationModelsElement(
            id=long_string,
            title=long_string,
            version=long_string,
            description=long_string,
        )

        assert len(element.id) == 10000
        assert len(element.title) == 10000
        assert len(element.version) == 10000
        assert len(element.description) == 10000

    def test_special_characters_in_fields(self):
        """Test models with special characters in fields"""
        special_chars = "!@#$%^&*()[]{}|;':\",./<>?"

        element = GetIntegrationModelsElement(
            id=special_chars,
            title=special_chars,
            version=special_chars,
            description=special_chars,
        )

        assert element.id == special_chars
        assert element.title == special_chars

    def test_numeric_strings_in_fields(self):
        """Test models with numeric strings in fields"""
        element = GetIntegrationModelsElement(
            id="12345:67890",
            title="12345",
            version="1.2.3.4.5.6.7.8.9",
            description="0000",
        )

        assert element.id == "12345:67890"
        assert element.title == "12345"
        assert element.version == "1.2.3.4.5.6.7.8.9"
        assert element.description == "0000"

    def test_model_immutability_after_creation(self):
        """Test that models maintain data integrity after creation"""
        element = GetIntegrationModelsElement(
            id="immutable:1.0.0",
            title="immutable",
            version="1.0.0",
            description="Immutability test",
        )

        original_id = element.id
        original_title = element.title

        # Pydantic models are immutable by default
        assert element.id == original_id
        assert element.title == original_title

    def test_version_format_flexibility(self):
        """Test that version field accepts various version formats"""
        version_formats = [
            "1.0.0",
            "2.1.3-alpha",
            "3.0.0-beta.1",
            "4.0.0-rc.1+build.123",
            "0.0.1",
            "10.20.30",
            "v1.2.3",
            "1.0",
            "1",
            "latest",
            "main",
        ]

        for version in version_formats:
            element = GetIntegrationModelsElement(
                id=f"test:{version}",
                title="test",
                version=version,
                description="Version format test",
            )
            assert element.version == version


class TestGetIntegrationsElement:
    """Test cases for GetIntegrationsElement model"""

    def test_get_integrations_element_valid_creation(self):
        """Test creating GetIntegrationsElement with valid data"""
        element = GetIntegrationsElement(
            name="cisco-switch-01",
            model="cisco-ios",
            properties={
                "hostname": "192.168.1.1",
                "username": "admin",
                "protocol": "ssh",
            },
        )

        assert element.name == "cisco-switch-01"
        assert element.model == "cisco-ios"
        assert element.properties["hostname"] == "192.168.1.1"
        assert element.properties["username"] == "admin"
        assert element.properties["protocol"] == "ssh"

    def test_get_integrations_element_missing_required_fields(self):
        """Test GetIntegrationsElement with missing required fields"""
        with pytest.raises(ValidationError) as exc_info:
            GetIntegrationsElement()

        errors = exc_info.value.errors()
        required_fields = {"name", "model", "properties"}
        missing_fields = {
            error["loc"][0] for error in errors if error["type"] == "missing"
        }

        assert required_fields == missing_fields

    def test_get_integrations_element_serialization(self):
        """Test GetIntegrationsElement serialization to dict"""
        element = GetIntegrationsElement(
            name="test-router",
            model="juniper-junos",
            properties={
                "device_type": "router",
                "management_ip": "10.0.0.1",
                "enabled": True,
            },
        )

        expected_dict = {
            "name": "test-router",
            "model": "juniper-junos",
            "properties": {
                "device_type": "router",
                "management_ip": "10.0.0.1",
                "enabled": True,
            },
        }

        assert element.model_dump() == expected_dict

    def test_get_integrations_element_json_serialization(self):
        """Test GetIntegrationsElement JSON serialization"""
        element = GetIntegrationsElement(
            name="json-test-device",
            model="generic-snmp",
            properties={"community": "public", "version": "v2c"},
        )

        json_str = element.model_dump_json()
        assert '"name":"json-test-device"' in json_str
        assert '"model":"generic-snmp"' in json_str
        assert '"community":"public"' in json_str

    def test_get_integrations_element_field_validation(self):
        """Test GetIntegrationsElement field type validation"""
        # Test non-string name
        with pytest.raises(ValidationError):
            GetIntegrationsElement(name=123, model="test", properties={})

        # Test non-string model
        with pytest.raises(ValidationError):
            GetIntegrationsElement(name="test", model=456, properties={})

        # Test non-dict properties
        with pytest.raises(ValidationError):
            GetIntegrationsElement(name="test", model="test", properties="invalid")

    def test_get_integrations_element_empty_properties(self):
        """Test GetIntegrationsElement with empty properties dict"""
        element = GetIntegrationsElement(
            name="minimal-device", model="minimal-model", properties={}
        )

        assert element.name == "minimal-device"
        assert element.model == "minimal-model"
        assert element.properties == {}

    def test_get_integrations_element_complex_properties(self):
        """Test GetIntegrationsElement with complex nested properties"""
        complex_properties = {
            "connection": {
                "host": "192.168.1.100",
                "port": 22,
                "timeout": 30,
                "credentials": {"username": "netadmin", "auth_method": "key"},
            },
            "capabilities": ["ssh", "netconf", "snmp"],
            "metadata": {
                "location": "datacenter-1",
                "rack": "A-12",
                "environment": "production",
            },
            "monitoring": {
                "enabled": True,
                "interval": 60,
                "thresholds": {"cpu": 80, "memory": 90, "disk": 95},
            },
        }

        element = GetIntegrationsElement(
            name="complex-device",
            model="multi-vendor-network",
            properties=complex_properties,
        )

        assert element.name == "complex-device"
        assert element.model == "multi-vendor-network"
        assert element.properties["connection"]["host"] == "192.168.1.100"
        assert "netconf" in element.properties["capabilities"]
        assert element.properties["monitoring"]["thresholds"]["cpu"] == 80

    def test_get_integrations_element_unicode_support(self):
        """Test GetIntegrationsElement with Unicode characters"""
        element = GetIntegrationsElement(
            name="设备-测试-01",
            model="multi-语言-model",
            properties={"描述": "测试设备", "位置": "北京机房 🏢"},
        )

        assert element.name == "设备-测试-01"
        assert element.model == "multi-语言-model"
        assert element.properties["描述"] == "测试设备"
        assert "🏢" in element.properties["位置"]

    def test_get_integrations_element_realistic_data(self):
        """Test GetIntegrationsElement with realistic network device data"""
        element = GetIntegrationsElement(
            name="core-switch-01",
            model="cisco-catalyst-9000",
            properties={
                "management_ip": "10.1.1.10",
                "snmp_community": "network_ro",
                "ssh_port": 22,
                "device_type": "switch",
                "os_version": "16.12.09",
                "serial_number": "FDO2048A1B2",
                "location": "Main DC - Rack 15",
                "vlans": [10, 20, 30, 100, 200],
                "interfaces": {
                    "GigabitEthernet1/0/1": {"status": "up", "vlan": 10},
                    "GigabitEthernet1/0/2": {"status": "up", "vlan": 20},
                },
            },
        )

        assert element.name == "core-switch-01"
        assert element.model == "cisco-catalyst-9000"
        assert element.properties["management_ip"] == "10.1.1.10"
        assert 100 in element.properties["vlans"]
        assert element.properties["interfaces"]["GigabitEthernet1/0/1"]["vlan"] == 10


class TestGetIntegrationsResponse:
    """Test cases for GetIntegrationsResponse model"""

    def test_get_integrations_response_empty_list(self):
        """Test GetIntegrationsResponse with empty integrations list"""
        response = GetIntegrationsResponse(root=[])
        assert response.root == []

    def test_get_integrations_response_single_integration(self):
        """Test GetIntegrationsResponse with single integration"""
        integration = GetIntegrationsElement(
            name="single-device",
            model="single-model",
            properties={"ip": "192.168.1.1"},
        )

        response = GetIntegrationsResponse(root=[integration])
        assert len(response.root) == 1
        assert response.root[0].name == "single-device"

    def test_get_integrations_response_multiple_integrations(self):
        """Test GetIntegrationsResponse with multiple integrations"""
        integrations = [
            GetIntegrationsElement(
                name=f"device-{i}",
                model=f"model-{i}",
                properties={"id": i, "status": "active"},
            )
            for i in range(5)
        ]

        response = GetIntegrationsResponse(root=integrations)
        assert len(response.root) == 5

        for i, integration in enumerate(response.root):
            assert integration.name == f"device-{i}"
            assert integration.model == f"model-{i}"
            assert integration.properties["id"] == i

    def test_get_integrations_response_different_models(self):
        """Test GetIntegrationsResponse with integrations using different models"""
        integrations = [
            GetIntegrationsElement(
                name="cisco-switch",
                model="cisco-ios",
                properties={"vendor": "cisco", "os": "ios"},
            ),
            GetIntegrationsElement(
                name="juniper-router",
                model="juniper-junos",
                properties={"vendor": "juniper", "os": "junos"},
            ),
            GetIntegrationsElement(
                name="arista-switch",
                model="arista-eos",
                properties={"vendor": "arista", "os": "eos"},
            ),
        ]

        response = GetIntegrationsResponse(root=integrations)
        models = [integration.model for integration in response.root]

        assert "cisco-ios" in models
        assert "juniper-junos" in models
        assert "arista-eos" in models

    def test_get_integrations_response_serialization(self):
        """Test GetIntegrationsResponse serialization"""
        integration = GetIntegrationsElement(
            name="serialize-test",
            model="test-model",
            properties={"test": True},
        )

        response = GetIntegrationsResponse(root=[integration])
        serialized = response.model_dump()

        # GetIntegrationsResponse is a RootModel, so it serializes directly as a list
        assert isinstance(serialized, list)
        assert len(serialized) == 1
        assert serialized[0]["name"] == "serialize-test"

    def test_get_integrations_response_invalid_integration_data(self):
        """Test GetIntegrationsResponse with invalid integration data"""
        with pytest.raises(ValidationError):
            GetIntegrationsResponse(
                root=[
                    {
                        "name": "test-device",
                        "model": "test-model",
                        # Missing required properties field
                    }
                ]
            )

    def test_get_integrations_response_iteration(self):
        """Test that GetIntegrationsResponse can be iterated"""
        integrations = [
            GetIntegrationsElement(
                name=f"iter-device-{i}",
                model=f"iter-model-{i}",
                properties={"index": i},
            )
            for i in range(3)
        ]

        response = GetIntegrationsResponse(root=integrations)

        # Test direct access
        assert len(response.root) == 3

        # Test iteration
        names = [integration.name for integration in response.root]
        assert names == ["iter-device-0", "iter-device-1", "iter-device-2"]

    def test_get_integrations_response_mixed_properties(self):
        """Test GetIntegrationsResponse with integrations having different property structures"""
        integrations = [
            GetIntegrationsElement(
                name="simple-device",
                model="simple-model",
                properties={"ip": "192.168.1.1"},
            ),
            GetIntegrationsElement(
                name="complex-device",
                model="complex-model",
                properties={
                    "connection": {"ip": "192.168.1.2", "port": 22},
                    "capabilities": ["ssh", "snmp"],
                    "metadata": {"location": "dc1"},
                },
            ),
            GetIntegrationsElement(
                name="empty-device",
                model="empty-model",
                properties={},
            ),
        ]

        response = GetIntegrationsResponse(root=integrations)
        assert len(response.root) == 3

        # Verify different property structures are preserved
        simple_props = response.root[0].properties
        complex_props = response.root[1].properties
        empty_props = response.root[2].properties

        assert simple_props == {"ip": "192.168.1.1"}
        assert "connection" in complex_props
        assert "capabilities" in complex_props
        assert empty_props == {}


class TestIntegrationsModelInteroperability:
    """Test cases for integrations model interoperability"""

    def test_integrations_response_from_elements(self):
        """Test creating response from individual elements"""
        elements = [
            GetIntegrationsElement(
                name=f"network-device-{i}",
                model="generic-network",
                properties={
                    "ip": f"192.168.1.{i + 10}",
                    "port": 22,
                    "enabled": i % 2 == 0,
                },
            )
            for i in range(3)
        ]

        response = GetIntegrationsResponse(root=elements)

        assert len(response.root) == 3
        for i, element in enumerate(response.root):
            assert element.name == f"network-device-{i}"
            assert element.model == "generic-network"
            assert element.properties["ip"] == f"192.168.1.{i + 10}"

    def test_integration_model_field_descriptions_exist(self):
        """Test that integration models have proper field descriptions"""
        # Test GetIntegrationsElement
        element_schema = GetIntegrationsElement.model_json_schema()
        properties = element_schema["properties"]

        for field in ["name", "model", "properties"]:
            assert field in properties
            assert "description" in properties[field]
            assert len(properties[field]["description"]) > 0

    def test_integration_json_schema_generation(self):
        """Test JSON schema generation for integration models"""
        models = [
            GetIntegrationsElement,
            GetIntegrationsResponse,
        ]

        for model_class in models:
            schema = model_class.model_json_schema()
            assert "type" in schema

            # GetIntegrationsResponse is a RootModel which has different schema structure
            if model_class == GetIntegrationsResponse:
                # RootModel schema has "items" instead of "properties"
                assert "items" in schema
            else:
                assert "properties" in schema

    def test_integration_model_equality_behavior(self):
        """Test integration model equality behavior"""
        element1 = GetIntegrationsElement(
            name="test-device", model="test-model", properties={"test": True}
        )
        element2 = GetIntegrationsElement(
            name="test-device", model="test-model", properties={"test": True}
        )
        element3 = GetIntegrationsElement(
            name="different-device", model="different-model", properties={"test": False}
        )

        assert element1 == element2
        assert element1 != element3
