# Copyright (c) 2025 Itential, Inc
# GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

import pytest
from pydantic import ValidationError

from itential_mcp.models.gateway_manager import (
    ServiceElement,
    GetServicesResponse,
    GatewayElement,
    GetGatewaysResponse,
    RunServiceResponse,
)


class TestServiceElement:
    """Test cases for ServiceElement model"""

    def test_service_element_valid_creation(self):
        """Test creating ServiceElement with valid data"""
        element = ServiceElement(
            name="test-service",
            cluster="test-cluster",
            type="python-script",
            description="Test service for unit testing",
            decorator={"type": "object", "properties": {"param1": {"type": "string"}}},
        )

        assert element.name == "test-service"
        assert element.cluster == "test-cluster"
        assert element.type == "python-script"
        assert element.description == "Test service for unit testing"
        assert element.decorator == {
            "type": "object",
            "properties": {"param1": {"type": "string"}},
        }

    @pytest.mark.parametrize(
        "service_type",
        ["ansible-playbook", "python-script", "opentofu-plan", "custom-script"],
    )
    def test_service_element_valid_types(self, service_type):
        """Test ServiceElement with various service types"""
        element = ServiceElement(
            name="service",
            cluster="cluster",
            type=service_type,
            description="description",
            decorator={},
        )
        assert element.type == service_type

    def test_service_element_missing_required_fields(self):
        """Test ServiceElement with missing required fields"""
        with pytest.raises(ValidationError) as exc_info:
            ServiceElement()

        errors = exc_info.value.errors()
        required_fields = {"name", "cluster", "type", "description", "decorator"}
        missing_fields = {
            error["loc"][0] for error in errors if error["type"] == "missing"
        }

        assert required_fields == missing_fields

    def test_service_element_serialization(self):
        """Test ServiceElement serialization to dict"""
        decorator = {"type": "object", "required": ["input"]}
        element = ServiceElement(
            name="serialize-service",
            cluster="test-cluster",
            type="ansible-playbook",
            description="Serialization test",
            decorator=decorator,
        )

        expected_dict = {
            "name": "serialize-service",
            "cluster": "test-cluster",
            "type": "ansible-playbook",
            "description": "Serialization test",
            "decorator": decorator,
        }

        assert element.model_dump() == expected_dict

    def test_service_element_json_serialization(self):
        """Test ServiceElement JSON serialization"""
        element = ServiceElement(
            name="json-service",
            cluster="json-cluster",
            type="python-script",
            description="JSON test service",
            decorator={"schema": "test"},
        )

        json_str = element.model_dump_json()
        assert '"name":"json-service"' in json_str
        assert '"type":"python-script"' in json_str

    def test_service_element_field_validation(self):
        """Test ServiceElement field type validation"""
        # Test non-string name
        with pytest.raises(ValidationError):
            ServiceElement(
                name=123,
                cluster="cluster",
                type="python-script",
                description="description",
                decorator={},
            )

    def test_service_element_empty_strings(self):
        """Test ServiceElement with empty string values"""
        element = ServiceElement(
            name="", cluster="", type="", description="", decorator={}
        )

        assert element.name == ""
        assert element.cluster == ""
        assert element.type == ""
        assert element.description == ""

    def test_service_element_unicode_support(self):
        """Test ServiceElement with Unicode characters"""
        element = ServiceElement(
            name="测试服务",
            cluster="тест-кластер",
            type="скрипт-питон",
            description="Service de test avec émojis 🚀",
            decorator={"unicode": "支持"},
        )

        assert element.name == "测试服务"
        assert element.cluster == "тест-кластер"
        assert element.type == "скрипт-питон"
        assert element.description == "Service de test avec émojis 🚀"

    def test_service_element_complex_decorator(self):
        """Test ServiceElement with complex decorator schema"""
        complex_decorator = {
            "type": "object",
            "properties": {
                "username": {"type": "string", "minLength": 1},
                "password": {"type": "string", "format": "password"},
                "options": {
                    "type": "array",
                    "items": {"type": "string"},
                    "default": [],
                },
                "config": {
                    "type": "object",
                    "properties": {"timeout": {"type": "integer", "minimum": 1}},
                },
            },
            "required": ["username", "password"],
        }

        element = ServiceElement(
            name="complex-service",
            cluster="complex-cluster",
            type="ansible-playbook",
            description="Service with complex decorator",
            decorator=complex_decorator,
        )

        assert element.decorator == complex_decorator


class TestGetServicesResponse:
    """Test cases for GetServicesResponse model"""

    def test_get_services_response_empty_list(self):
        """Test GetServicesResponse with empty service list"""
        response = GetServicesResponse(root=[])
        assert response.root == []

    def test_get_services_response_single_service(self):
        """Test GetServicesResponse with single service"""
        service = ServiceElement(
            name="single-service",
            cluster="single-cluster",
            type="python-script",
            description="Single service",
            decorator={"type": "object"},
        )

        response = GetServicesResponse(root=[service])
        assert len(response.root) == 1
        assert response.root[0].name == "single-service"

    def test_get_services_response_multiple_services(self):
        """Test GetServicesResponse with multiple services"""
        services = [
            ServiceElement(
                name=f"service-{i}",
                cluster=f"cluster-{i}",
                type="python-script",
                description=f"Test service {i}",
                decorator={"id": i},
            )
            for i in range(5)
        ]

        response = GetServicesResponse(root=services)
        assert len(response.root) == 5

        for i, service in enumerate(response.root):
            assert service.name == f"service-{i}"

    def test_get_services_response_mixed_types(self):
        """Test GetServicesResponse with services of different types"""
        services = [
            ServiceElement(
                name="ansible-service",
                cluster="cluster-1",
                type="ansible-playbook",
                description="Ansible service",
                decorator={"playbook": "test.yml"},
            ),
            ServiceElement(
                name="python-service",
                cluster="cluster-2",
                type="python-script",
                description="Python service",
                decorator={"script": "test.py"},
            ),
            ServiceElement(
                name="terraform-service",
                cluster="cluster-3",
                type="opentofu-plan",
                description="Terraform service",
                decorator={"plan": "main.tf"},
            ),
        ]

        response = GetServicesResponse(root=services)
        types = [service.type for service in response.root]
        assert "ansible-playbook" in types
        assert "python-script" in types
        assert "opentofu-plan" in types

    def test_get_services_response_serialization(self):
        """Test GetServicesResponse serialization"""
        service = ServiceElement(
            name="serialize-test",
            cluster="serialize-cluster",
            type="python-script",
            description="Serialization test",
            decorator={"version": "1.0"},
        )

        response = GetServicesResponse(root=[service])
        serialized = response.model_dump()

        # GetServicesResponse is a RootModel, so it serializes directly as a list
        assert isinstance(serialized, list)
        assert len(serialized) == 1
        assert serialized[0]["name"] == "serialize-test"

    def test_get_services_response_invalid_service_data(self):
        """Test GetServicesResponse with invalid service data"""
        with pytest.raises(ValidationError):
            GetServicesResponse(
                root=[
                    {
                        "name": "test",
                        "cluster": "test",
                        "type": "python-script",
                        "description": "test",
                        # Missing decorator field
                    }
                ]
            )

    def test_get_services_response_iteration(self):
        """Test that GetServicesResponse can be iterated"""
        services = [
            ServiceElement(
                name=f"iter-{i}",
                cluster=f"cluster-{i}",
                type="python-script",
                description=f"Iterator test {i}",
                decorator={"index": i},
            )
            for i in range(3)
        ]

        response = GetServicesResponse(root=services)

        # Test direct access
        assert len(response.root) == 3

        # Test iteration
        names = [service.name for service in response.root]
        assert names == ["iter-0", "iter-1", "iter-2"]


class TestGatewayElement:
    """Test cases for GatewayElement model"""

    def test_gateway_element_valid_creation(self):
        """Test creating GatewayElement with valid data"""
        element = GatewayElement(
            name="test-gateway",
            cluster="test-cluster",
            description="Test gateway for unit testing",
            status="connected",
            enabled=True,
        )

        assert element.name == "test-gateway"
        assert element.cluster == "test-cluster"
        assert element.description == "Test gateway for unit testing"
        assert element.status == "connected"
        assert element.enabled is True

    @pytest.mark.parametrize(
        "status", ["connected", "disconnected", "connecting", "error", "unknown"]
    )
    def test_gateway_element_valid_statuses(self, status):
        """Test GatewayElement with various status values"""
        element = GatewayElement(
            name="gateway",
            cluster="cluster",
            description="description",
            status=status,
            enabled=True,
        )
        assert element.status == status

    @pytest.mark.parametrize("enabled", [True, False])
    def test_gateway_element_enabled_states(self, enabled):
        """Test GatewayElement with enabled/disabled states"""
        element = GatewayElement(
            name="gateway",
            cluster="cluster",
            description="description",
            status="connected",
            enabled=enabled,
        )
        assert element.enabled is enabled

    def test_gateway_element_missing_required_fields(self):
        """Test GatewayElement with missing required fields"""
        with pytest.raises(ValidationError) as exc_info:
            GatewayElement()

        errors = exc_info.value.errors()
        required_fields = {"name", "cluster", "description", "status", "enabled"}
        missing_fields = {
            error["loc"][0] for error in errors if error["type"] == "missing"
        }

        assert required_fields == missing_fields

    def test_gateway_element_serialization(self):
        """Test GatewayElement serialization to dict"""
        element = GatewayElement(
            name="serialize-gateway",
            cluster="serialize-cluster",
            description="Serialization test",
            status="disconnected",
            enabled=False,
        )

        expected_dict = {
            "name": "serialize-gateway",
            "cluster": "serialize-cluster",
            "description": "Serialization test",
            "status": "disconnected",
            "enabled": False,
        }

        assert element.model_dump() == expected_dict

    def test_gateway_element_field_validation(self):
        """Test GatewayElement field type validation"""
        # Test non-boolean enabled with invalid value
        with pytest.raises(ValidationError):
            GatewayElement(
                name="gateway",
                cluster="cluster",
                description="description",
                status="connected",
                enabled="invalid_boolean",  # Should be boolean
            )

    def test_gateway_element_unicode_support(self):
        """Test GatewayElement with Unicode characters"""
        element = GatewayElement(
            name="测试网关",
            cluster="тест-кластер",
            description="Gateway de test avec émojis 🌐",
            status="подключено",
            enabled=True,
        )

        assert element.name == "测试网关"
        assert element.cluster == "тест-кластер"
        assert element.description == "Gateway de test avec émojis 🌐"
        assert element.status == "подключено"


class TestGetGatewaysResponse:
    """Test cases for GetGatewaysResponse model"""

    def test_get_gateways_response_empty_list(self):
        """Test GetGatewaysResponse with empty gateway list"""
        response = GetGatewaysResponse(root=[])
        assert response.root == []

    def test_get_gateways_response_single_gateway(self):
        """Test GetGatewaysResponse with single gateway"""
        gateway = GatewayElement(
            name="single-gateway",
            cluster="single-cluster",
            description="Single gateway",
            status="connected",
            enabled=True,
        )

        response = GetGatewaysResponse(root=[gateway])
        assert len(response.root) == 1
        assert response.root[0].name == "single-gateway"

    def test_get_gateways_response_multiple_gateways(self):
        """Test GetGatewaysResponse with multiple gateways"""
        gateways = [
            GatewayElement(
                name=f"gateway-{i}",
                cluster=f"cluster-{i}",
                description=f"Test gateway {i}",
                status="connected",
                enabled=i % 2 == 0,  # Alternate enabled/disabled
            )
            for i in range(5)
        ]

        response = GetGatewaysResponse(root=gateways)
        assert len(response.root) == 5

        for i, gateway in enumerate(response.root):
            assert gateway.name == f"gateway-{i}"

    def test_get_gateways_response_mixed_statuses(self):
        """Test GetGatewaysResponse with gateways in different statuses"""
        gateways = [
            GatewayElement(
                name="connected-gateway",
                cluster="cluster-1",
                description="Connected gateway",
                status="connected",
                enabled=True,
            ),
            GatewayElement(
                name="disconnected-gateway",
                cluster="cluster-2",
                description="Disconnected gateway",
                status="disconnected",
                enabled=False,
            ),
            GatewayElement(
                name="error-gateway",
                cluster="cluster-3",
                description="Error gateway",
                status="error",
                enabled=True,
            ),
        ]

        response = GetGatewaysResponse(root=gateways)
        statuses = [gateway.status for gateway in response.root]
        assert "connected" in statuses
        assert "disconnected" in statuses
        assert "error" in statuses

    def test_get_gateways_response_serialization(self):
        """Test GetGatewaysResponse serialization"""
        gateway = GatewayElement(
            name="serialize-test",
            cluster="serialize-cluster",
            description="Serialization test",
            status="connected",
            enabled=True,
        )

        response = GetGatewaysResponse(root=[gateway])
        serialized = response.model_dump()

        # GetGatewaysResponse is a RootModel, so it serializes directly as a list
        assert isinstance(serialized, list)
        assert len(serialized) == 1
        assert serialized[0]["name"] == "serialize-test"


class TestRunServiceResponse:
    """Test cases for RunServiceResponse model"""

    def test_run_service_response_valid_creation(self):
        """Test creating RunServiceResponse with valid data"""
        response = RunServiceResponse(
            stdout="Hello, World!",
            stderr="",
            return_code=0,
            start_time="2025-01-01T10:00:00Z",
            end_time="2025-01-01T10:00:05Z",
            elapsed_time=5.0,
        )

        assert response.stdout == "Hello, World!"
        assert response.stderr == ""
        assert response.return_code == 0
        assert response.start_time == "2025-01-01T10:00:00Z"
        assert response.end_time == "2025-01-01T10:00:05Z"
        assert response.elapsed_time == 5.0

    @pytest.mark.parametrize("return_code", [0, 1, 127, 255, -1])
    def test_run_service_response_return_codes(self, return_code):
        """Test RunServiceResponse with various return codes"""
        response = RunServiceResponse(
            stdout="output",
            stderr="error",
            return_code=return_code,
            start_time="2025-01-01T10:00:00Z",
            end_time="2025-01-01T10:00:01Z",
            elapsed_time=1.0,
        )
        assert response.return_code == return_code

    def test_run_service_response_success_scenario(self):
        """Test RunServiceResponse for successful execution"""
        response = RunServiceResponse(
            stdout="Task completed successfully\nResult: 42",
            stderr="",
            return_code=0,
            start_time="2025-01-01T12:00:00Z",
            end_time="2025-01-01T12:00:10Z",
            elapsed_time=10.5,
        )

        assert response.return_code == 0
        assert "successfully" in response.stdout
        assert response.stderr == ""
        assert response.elapsed_time > 0

    def test_run_service_response_error_scenario(self):
        """Test RunServiceResponse for failed execution"""
        response = RunServiceResponse(
            stdout="Processing started...",
            stderr="Error: Connection failed\nTimeout occurred",
            return_code=1,
            start_time="2025-01-01T12:00:00Z",
            end_time="2025-01-01T12:00:30Z",
            elapsed_time=30.0,
        )

        assert response.return_code != 0
        assert "Error" in response.stderr
        assert response.elapsed_time == 30.0

    def test_run_service_response_missing_required_fields(self):
        """Test RunServiceResponse with missing required fields"""
        with pytest.raises(ValidationError) as exc_info:
            RunServiceResponse()

        errors = exc_info.value.errors()
        required_fields = {"return_code", "start_time", "end_time", "elapsed_time"}
        missing_fields = {
            error["loc"][0] for error in errors if error["type"] == "missing"
        }

        assert required_fields == missing_fields

    def test_run_service_response_field_validation(self):
        """Test RunServiceResponse field type validation"""
        # Test invalid return_code type
        with pytest.raises(ValidationError):
            RunServiceResponse(
                stdout="output",
                stderr="error",
                return_code=None,  # Should be int
                start_time="2025-01-01T10:00:00Z",
                end_time="2025-01-01T10:00:01Z",
                elapsed_time=1.0,
            )

        # Test invalid elapsed_time type
        with pytest.raises(ValidationError):
            RunServiceResponse(
                stdout="output",
                stderr="error",
                return_code=0,
                start_time="2025-01-01T10:00:00Z",
                end_time="2025-01-01T10:00:01Z",
                elapsed_time=None,  # Should be float
            )

    def test_run_service_response_serialization(self):
        """Test RunServiceResponse serialization"""
        response = RunServiceResponse(
            stdout="Serialization test output",
            stderr="Warning: test mode",
            return_code=0,
            start_time="2025-01-01T14:00:00.000Z",
            end_time="2025-01-01T14:00:02.500Z",
            elapsed_time=2.5,
        )

        serialized = response.model_dump()
        expected = {
            "stdout": "Serialization test output",
            "stderr": "Warning: test mode",
            "return_code": 0,
            "start_time": "2025-01-01T14:00:00.000Z",
            "end_time": "2025-01-01T14:00:02.500Z",
            "elapsed_time": 2.5,
        }

        assert serialized == expected

    def test_run_service_response_unicode_output(self):
        """Test RunServiceResponse with Unicode characters in output"""
        response = RunServiceResponse(
            stdout="成功完成任务 ✅\nРезультат: успешно",
            stderr="Avertissement: mode de test 🧪",
            return_code=0,
            start_time="2025-01-01T10:00:00Z",
            end_time="2025-01-01T10:00:01Z",
            elapsed_time=1.0,
        )

        assert "成功完成任务 ✅" in response.stdout
        assert "Avertissement: mode de test 🧪" in response.stderr

    def test_run_service_response_large_output(self):
        """Test RunServiceResponse with large output"""
        large_stdout = "Line {}\n" * 10000
        large_stderr = "Error {}\n" * 1000

        response = RunServiceResponse(
            stdout=large_stdout.format(*range(10000)),
            stderr=large_stderr.format(*range(1000)),
            return_code=2,
            start_time="2025-01-01T10:00:00Z",
            end_time="2025-01-01T10:05:00Z",
            elapsed_time=300.0,
        )

        assert len(response.stdout) > 50000
        assert len(response.stderr) > 5000
        assert response.elapsed_time == 300.0

    def test_run_service_response_zero_elapsed_time(self):
        """Test RunServiceResponse with zero elapsed time"""
        response = RunServiceResponse(
            stdout="Instant execution",
            stderr="",
            return_code=0,
            start_time="2025-01-01T10:00:00Z",
            end_time="2025-01-01T10:00:00Z",
            elapsed_time=0.0,
        )

        assert response.elapsed_time == 0.0

    def test_run_service_response_negative_elapsed_time(self):
        """Test RunServiceResponse with negative elapsed time"""
        # This might occur due to clock adjustments or measurement errors
        response = RunServiceResponse(
            stdout="Time anomaly",
            stderr="Clock adjustment detected",
            return_code=0,
            start_time="2025-01-01T10:00:01Z",
            end_time="2025-01-01T10:00:00Z",
            elapsed_time=-1.0,
        )

        assert response.elapsed_time == -1.0


class TestModelInteroperability:
    """Test cases for model interoperability and edge cases"""

    def test_service_and_gateway_response_consistency(self):
        """Test that service and gateway responses have consistent structure"""
        service = ServiceElement(
            name="test-service",
            cluster="test-cluster",
            type="python-script",
            description="Test service",
            decorator={},
        )

        gateway = GatewayElement(
            name="test-gateway",
            cluster="test-cluster",
            description="Test gateway",
            status="connected",
            enabled=True,
        )

        services_response = GetServicesResponse(root=[service])
        gateways_response = GetGatewaysResponse(root=[gateway])

        # Both should serialize as lists
        assert isinstance(services_response.model_dump(), list)
        assert isinstance(gateways_response.model_dump(), list)

    def test_model_field_descriptions_exist(self):
        """Test that all models have proper field descriptions"""
        models_to_test = [ServiceElement, GatewayElement, RunServiceResponse]

        for model_class in models_to_test:
            schema = model_class.model_json_schema()
            properties = schema["properties"]

            for field_name, field_info in properties.items():
                assert "description" in field_info
                assert len(field_info["description"]) > 0

    def test_json_schema_generation(self):
        """Test JSON schema generation for all models"""
        models = [
            ServiceElement,
            GetServicesResponse,
            GatewayElement,
            GetGatewaysResponse,
            RunServiceResponse,
        ]

        for model_class in models:
            schema = model_class.model_json_schema()
            assert "type" in schema

            # RootModels have different schema structure
            if model_class in [GetServicesResponse, GetGatewaysResponse]:
                assert "items" in schema
            else:
                assert "properties" in schema

    def test_model_equality(self):
        """Test model equality behavior"""
        service1 = ServiceElement(
            name="test",
            cluster="test",
            type="python-script",
            description="test",
            decorator={},
        )
        service2 = ServiceElement(
            name="test",
            cluster="test",
            type="python-script",
            description="test",
            decorator={},
        )
        service3 = ServiceElement(
            name="different",
            cluster="test",
            type="python-script",
            description="test",
            decorator={},
        )

        assert service1 == service2
        assert service1 != service3


class TestModelValidationEdgeCases:
    """Test edge cases and validation scenarios"""

    def test_extremely_long_field_values(self):
        """Test models with extremely long field values"""
        long_string = "x" * 10000

        service = ServiceElement(
            name=long_string,
            cluster=long_string,
            type=long_string,
            description=long_string,
            decorator={"long_key": long_string},
        )

        assert len(service.name) == 10000
        assert len(service.cluster) == 10000

    def test_special_characters_in_fields(self):
        """Test models with special characters in fields"""
        special_chars = "!@#$%^&*()[]{}|;':\",./<>?"

        gateway = GatewayElement(
            name=special_chars,
            cluster=special_chars,
            description=special_chars,
            status=special_chars,
            enabled=True,
        )

        assert gateway.name == special_chars

    def test_empty_and_whitespace_strings(self):
        """Test models with empty and whitespace-only strings"""
        run_response = RunServiceResponse(
            stdout="",
            stderr="   ",
            return_code=0,
            start_time="\t",
            end_time="\n",
            elapsed_time=0.0,
        )

        assert run_response.stdout == ""
        assert run_response.stderr == "   "
        assert run_response.start_time == "\t"
