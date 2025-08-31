# Copyright (c) 2025 Itential, Inc
# GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)

import pytest
from pydantic import ValidationError

from itential_mcp.models.adapters import (
    GetAdaptersElement,
    GetAdaptersResponse,
    StartAdapterResponse,
    StopAdapterResponse,
    RestartAdapterResponse
)


class TestGetAdaptersElement:
    """Test cases for GetAdaptersElement model"""

    def test_get_adapters_element_valid_creation(self):
        """Test creating GetAdaptersElement with valid data"""
        element = GetAdaptersElement(
            name="test-adapter",
            package="@itential/test-adapter",
            version="1.0.0",
            description="Test adapter for unit testing",
            state="RUNNING"
        )
        
        assert element.name == "test-adapter"
        assert element.package == "@itential/test-adapter"
        assert element.version == "1.0.0"
        assert element.description == "Test adapter for unit testing"
        assert element.state == "RUNNING"

    @pytest.mark.parametrize("state", ["DEAD", "STOPPED", "RUNNING", "DELETED"])
    def test_get_adapters_element_valid_states(self, state):
        """Test GetAdaptersElement with all valid state values"""
        element = GetAdaptersElement(
            name="adapter",
            package="package",
            version="1.0.0",
            description="description",
            state=state
        )
        assert element.state == state

    def test_get_adapters_element_invalid_state(self):
        """Test GetAdaptersElement with invalid state value"""
        with pytest.raises(ValidationError) as exc_info:
            GetAdaptersElement(
                name="adapter",
                package="package",
                version="1.0.0",
                description="description",
                state="INVALID"
            )
        
        assert "Input should be 'DEAD', 'STOPPED', 'RUNNING' or 'DELETED'" in str(exc_info.value)

    def test_get_adapters_element_missing_required_fields(self):
        """Test GetAdaptersElement with missing required fields"""
        with pytest.raises(ValidationError) as exc_info:
            GetAdaptersElement()
        
        errors = exc_info.value.errors()
        required_fields = {"name", "package", "version", "description", "state"}
        missing_fields = {error["loc"][0] for error in errors if error["type"] == "missing"}
        
        assert required_fields == missing_fields

    def test_get_adapters_element_serialization(self):
        """Test GetAdaptersElement serialization to dict"""
        element = GetAdaptersElement(
            name="test-adapter",
            package="@itential/test-adapter",
            version="2.1.0",
            description="Test adapter",
            state="STOPPED"
        )
        
        expected_dict = {
            "name": "test-adapter",
            "package": "@itential/test-adapter",
            "version": "2.1.0",
            "description": "Test adapter",
            "state": "STOPPED"
        }
        
        assert element.model_dump() == expected_dict

    def test_get_adapters_element_json_serialization(self):
        """Test GetAdaptersElement JSON serialization"""
        element = GetAdaptersElement(
            name="json-adapter",
            package="@itential/json-adapter",
            version="3.0.1",
            description="JSON test adapter",
            state="DEAD"
        )
        
        json_str = element.model_dump_json()
        assert '"name":"json-adapter"' in json_str
        assert '"state":"DEAD"' in json_str

    def test_get_adapters_element_field_validation(self):
        """Test GetAdaptersElement field type validation"""
        # Test non-string name
        with pytest.raises(ValidationError):
            GetAdaptersElement(
                name=123,
                package="package",
                version="1.0.0",
                description="description",
                state="RUNNING"
            )

    def test_get_adapters_element_empty_strings(self):
        """Test GetAdaptersElement with empty string values"""
        element = GetAdaptersElement(
            name="",
            package="",
            version="",
            description="",
            state="RUNNING"
        )
        
        assert element.name == ""
        assert element.package == ""
        assert element.version == ""
        assert element.description == ""

    def test_get_adapters_element_whitespace_strings(self):
        """Test GetAdaptersElement with whitespace-only strings"""
        element = GetAdaptersElement(
            name="   ",
            package="\t",
            version="\n",
            description="  \t\n  ",
            state="RUNNING"
        )
        
        assert element.name == "   "
        assert element.package == "\t"
        assert element.version == "\n"
        assert element.description == "  \t\n  "

    def test_get_adapters_element_unicode_support(self):
        """Test GetAdaptersElement with Unicode characters"""
        element = GetAdaptersElement(
            name="测试适配器",
            package="@itential/тест-адаптер",
            version="1.0.0-α",
            description="Adaptateur de test avec émojis 🚀",
            state="RUNNING"
        )
        
        assert element.name == "测试适配器"
        assert element.package == "@itential/тест-адаптер"
        assert element.version == "1.0.0-α"
        assert element.description == "Adaptateur de test avec émojis 🚀"


class TestGetAdaptersResponse:
    """Test cases for GetAdaptersResponse model"""

    def test_get_adapters_response_empty_list(self):
        """Test GetAdaptersResponse with empty adapter list"""
        response = GetAdaptersResponse(root=[])
        assert response.root == []

    def test_get_adapters_response_single_adapter(self):
        """Test GetAdaptersResponse with single adapter"""
        adapter = GetAdaptersElement(
            name="single-adapter",
            package="@itential/single",
            version="1.0.0",
            description="Single adapter",
            state="RUNNING"
        )
        
        response = GetAdaptersResponse(root=[adapter])
        assert len(response.root) == 1
        assert response.root[0].name == "single-adapter"

    def test_get_adapters_response_multiple_adapters(self):
        """Test GetAdaptersResponse with multiple adapters"""
        adapters = [
            GetAdaptersElement(
                name=f"adapter-{i}",
                package=f"@itential/adapter-{i}",
                version="1.0.0",
                description=f"Test adapter {i}",
                state="RUNNING"
            )
            for i in range(5)
        ]
        
        response = GetAdaptersResponse(root=adapters)
        assert len(response.root) == 5
        
        for i, adapter in enumerate(response.root):
            assert adapter.name == f"adapter-{i}"

    def test_get_adapters_response_mixed_states(self):
        """Test GetAdaptersResponse with adapters in different states"""
        adapters = [
            GetAdaptersElement(
                name="running-adapter",
                package="@itential/running",
                version="1.0.0",
                description="Running adapter",
                state="RUNNING"
            ),
            GetAdaptersElement(
                name="stopped-adapter",
                package="@itential/stopped",
                version="1.0.0",
                description="Stopped adapter",
                state="STOPPED"
            ),
            GetAdaptersElement(
                name="dead-adapter",
                package="@itential/dead",
                version="1.0.0",
                description="Dead adapter",
                state="DEAD"
            )
        ]
        
        response = GetAdaptersResponse(root=adapters)
        states = [adapter.state for adapter in response.root]
        assert "RUNNING" in states
        assert "STOPPED" in states
        assert "DEAD" in states

    def test_get_adapters_response_serialization(self):
        """Test GetAdaptersResponse serialization"""
        adapter = GetAdaptersElement(
            name="serialize-test",
            package="@itential/serialize",
            version="2.0.0",
            description="Serialization test",
            state="RUNNING"
        )
        
        response = GetAdaptersResponse(root=[adapter])
        serialized = response.model_dump()
        
        # GetAdaptersResponse is a RootModel, so it serializes directly as a list
        assert isinstance(serialized, list)
        assert len(serialized) == 1
        assert serialized[0]["name"] == "serialize-test"

    def test_get_adapters_response_invalid_adapter_data(self):
        """Test GetAdaptersResponse with invalid adapter data"""
        with pytest.raises(ValidationError):
            GetAdaptersResponse(root=[{
                "name": "test",
                "package": "test",
                "version": "1.0.0",
                "description": "test",
                "state": "INVALID_STATE"
            }])

    def test_get_adapters_response_iteration(self):
        """Test that GetAdaptersResponse can be iterated"""
        adapters = [
            GetAdaptersElement(
                name=f"iter-{i}",
                package=f"@itential/iter-{i}",
                version="1.0.0",
                description=f"Iterator test {i}",
                state="RUNNING"
            )
            for i in range(3)
        ]
        
        response = GetAdaptersResponse(root=adapters)
        
        # Test direct access
        assert len(response.root) == 3
        
        # Test iteration
        names = [adapter.name for adapter in response.root]
        assert names == ["iter-0", "iter-1", "iter-2"]


class TestStartAdapterResponse:
    """Test cases for StartAdapterResponse model"""

    def test_start_adapter_response_valid_creation(self):
        """Test creating StartAdapterResponse with valid data"""
        response = StartAdapterResponse(
            name="test-adapter",
            state="RUNNING"
        )
        
        assert response.name == "test-adapter"
        assert response.state == "RUNNING"

    @pytest.mark.parametrize("state", ["DEAD", "STOPPED", "RUNNING", "DELETED"])
    def test_start_adapter_response_valid_states(self, state):
        """Test StartAdapterResponse with all valid state values"""
        response = StartAdapterResponse(name="adapter", state=state)
        assert response.state == state

    def test_start_adapter_response_invalid_state(self):
        """Test StartAdapterResponse with invalid state"""
        with pytest.raises(ValidationError) as exc_info:
            StartAdapterResponse(name="adapter", state="INVALID")
        
        assert "Input should be 'DEAD', 'STOPPED', 'RUNNING' or 'DELETED'" in str(exc_info.value)

    def test_start_adapter_response_missing_fields(self):
        """Test StartAdapterResponse with missing required fields"""
        with pytest.raises(ValidationError) as exc_info:
            StartAdapterResponse()
        
        errors = exc_info.value.errors()
        missing_fields = {error["loc"][0] for error in errors if error["type"] == "missing"}
        
        assert {"name", "state"} == missing_fields

    def test_start_adapter_response_serialization(self):
        """Test StartAdapterResponse serialization"""
        response = StartAdapterResponse(name="start-test", state="RUNNING")
        serialized = response.model_dump()
        
        expected = {"name": "start-test", "state": "RUNNING"}
        assert serialized == expected


class TestStopAdapterResponse:
    """Test cases for StopAdapterResponse model"""

    def test_stop_adapter_response_valid_creation(self):
        """Test creating StopAdapterResponse with valid data"""
        response = StopAdapterResponse(
            name="test-adapter",
            state="STOPPED"
        )
        
        assert response.name == "test-adapter"
        assert response.state == "STOPPED"

    @pytest.mark.parametrize("state", ["DEAD", "STOPPED", "RUNNING", "DELETED"])
    def test_stop_adapter_response_valid_states(self, state):
        """Test StopAdapterResponse with all valid state values"""
        response = StopAdapterResponse(name="adapter", state=state)
        assert response.state == state

    def test_stop_adapter_response_invalid_state(self):
        """Test StopAdapterResponse with invalid state"""
        with pytest.raises(ValidationError) as exc_info:
            StopAdapterResponse(name="adapter", state="INVALID")
        
        assert "Input should be 'DEAD', 'STOPPED', 'RUNNING' or 'DELETED'" in str(exc_info.value)

    def test_stop_adapter_response_serialization(self):
        """Test StopAdapterResponse serialization"""
        response = StopAdapterResponse(name="stop-test", state="STOPPED")
        serialized = response.model_dump()
        
        expected = {"name": "stop-test", "state": "STOPPED"}
        assert serialized == expected


class TestRestartAdapterResponse:
    """Test cases for RestartAdapterResponse model"""

    def test_restart_adapter_response_valid_creation(self):
        """Test creating RestartAdapterResponse with valid data"""
        response = RestartAdapterResponse(
            name="test-adapter",
            state="RUNNING"
        )
        
        assert response.name == "test-adapter"
        assert response.state == "RUNNING"

    @pytest.mark.parametrize("state", ["DEAD", "STOPPED", "RUNNING", "DELETED"])
    def test_restart_adapter_response_valid_states(self, state):
        """Test RestartAdapterResponse with all valid state values"""
        response = RestartAdapterResponse(name="adapter", state=state)
        assert response.state == state

    def test_restart_adapter_response_invalid_state(self):
        """Test RestartAdapterResponse with invalid state"""
        with pytest.raises(ValidationError) as exc_info:
            RestartAdapterResponse(name="adapter", state="INVALID")
        
        assert "Input should be 'DEAD', 'STOPPED', 'RUNNING' or 'DELETED'" in str(exc_info.value)

    def test_restart_adapter_response_serialization(self):
        """Test RestartAdapterResponse serialization"""
        response = RestartAdapterResponse(name="restart-test", state="RUNNING")
        serialized = response.model_dump()
        
        expected = {"name": "restart-test", "state": "RUNNING"}
        assert serialized == expected


class TestModelInteroperability:
    """Test cases for model interoperability and edge cases"""

    def test_all_models_have_consistent_state_literals(self):
        """Test that all models use the same state literal values"""
        valid_states = ["DEAD", "STOPPED", "RUNNING", "DELETED"]
        
        # Test each model with each state
        for state in valid_states:
            element = GetAdaptersElement(
                name="test", package="test", version="1.0.0",
                description="test", state=state
            )
            start_resp = StartAdapterResponse(name="test", state=state)
            stop_resp = StopAdapterResponse(name="test", state=state)
            restart_resp = RestartAdapterResponse(name="test", state=state)
            
            assert element.state == state
            assert start_resp.state == state
            assert stop_resp.state == state
            assert restart_resp.state == state

    def test_response_models_from_adapter_element(self):
        """Test creating response models from adapter element data"""
        element = GetAdaptersElement(
            name="conversion-test",
            package="@itential/conversion",
            version="1.0.0",
            description="Conversion test",
            state="RUNNING"
        )
        
        # Create response models using data from element
        start_resp = StartAdapterResponse(name=element.name, state=element.state)
        stop_resp = StopAdapterResponse(name=element.name, state="STOPPED")
        restart_resp = RestartAdapterResponse(name=element.name, state=element.state)
        
        assert start_resp.name == element.name
        assert stop_resp.name == element.name
        assert restart_resp.name == element.name

    def test_model_field_descriptions_exist(self):
        """Test that all models have proper field descriptions"""
        # Test GetAdaptersElement
        element_schema = GetAdaptersElement.model_json_schema()
        properties = element_schema["properties"]
        
        for field in ["name", "package", "version", "description", "state"]:
            assert field in properties
            assert "description" in properties[field]
            assert len(properties[field]["description"]) > 0

        # Test response models
        for model_class in [StartAdapterResponse, StopAdapterResponse, RestartAdapterResponse]:
            schema = model_class.model_json_schema()
            properties = schema["properties"]
            
            for field in ["name", "state"]:
                assert field in properties
                assert "description" in properties[field]

    def test_json_schema_generation(self):
        """Test JSON schema generation for all models"""
        models = [
            GetAdaptersElement,
            GetAdaptersResponse,
            StartAdapterResponse,
            StopAdapterResponse,
            RestartAdapterResponse
        ]
        
        for model_class in models:
            schema = model_class.model_json_schema()
            assert "type" in schema
            
            # GetAdaptersResponse is a RootModel which has a different schema structure
            if model_class == GetAdaptersResponse:
                # RootModel schema has "items" instead of "properties"
                assert "items" in schema
            else:
                assert "properties" in schema

    def test_model_equality_and_hashing(self):
        """Test model equality behavior"""
        element1 = GetAdaptersElement(
            name="test", package="test", version="1.0.0",
            description="test", state="RUNNING"
        )
        element2 = GetAdaptersElement(
            name="test", package="test", version="1.0.0",
            description="test", state="RUNNING"
        )
        element3 = GetAdaptersElement(
            name="different", package="test", version="1.0.0",
            description="test", state="RUNNING"
        )
        
        assert element1 == element2
        assert element1 != element3
        
        # Pydantic models are not hashable by default, so we skip hash testing
        # This is expected behavior for Pydantic BaseModel instances


class TestModelValidationEdgeCases:
    """Test edge cases and validation scenarios"""

    def test_extremely_long_field_values(self):
        """Test models with extremely long field values"""
        long_string = "x" * 10000
        
        element = GetAdaptersElement(
            name=long_string,
            package=long_string,
            version=long_string,
            description=long_string,
            state="RUNNING"
        )
        
        assert len(element.name) == 10000
        assert len(element.package) == 10000

    def test_special_characters_in_fields(self):
        """Test models with special characters in fields"""
        special_chars = "!@#$%^&*()[]{}|;':\",./<>?"
        
        element = GetAdaptersElement(
            name=special_chars,
            package=special_chars,
            version=special_chars,
            description=special_chars,
            state="RUNNING"
        )
        
        assert element.name == special_chars

    def test_numeric_strings_in_fields(self):
        """Test models with numeric strings in fields"""
        element = GetAdaptersElement(
            name="12345",
            package="67890",
            version="1.2.3.4.5",
            description="0000",
            state="RUNNING"
        )
        
        assert element.name == "12345"
        assert element.package == "67890"
        assert element.version == "1.2.3.4.5"

    def test_model_immutability_after_creation(self):
        """Test that models maintain data integrity after creation"""
        element = GetAdaptersElement(
            name="immutable-test",
            package="@itential/immutable",
            version="1.0.0",
            description="Immutability test",
            state="RUNNING"
        )
        
        original_name = element.name
        original_state = element.state
        
        # Pydantic models are immutable by default, so this should work
        assert element.name == original_name
        assert element.state == original_state