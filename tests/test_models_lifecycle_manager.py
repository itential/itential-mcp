# Copyright (c) 2025 Itential, Inc
# GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)

import pytest
from pydantic import ValidationError

from itential_mcp.models.lifecycle_manager import (
    GetResourcesElement,
    GetResourcesResponse,
    CreateResourceResponse,
    Action,
    DescribeResourceResponse,
    LastAction,
    GetInstancesElement,
    GetInstancesResponse,
    DescribeInstanceResponse,
    RunActionResponse,
)


class TestGetResourcesElement:
    """Test the GetResourcesElement model"""

    def test_get_resources_element_basic(self):
        """Test basic GetResourcesElement creation"""
        element = GetResourcesElement(
            name="test-resource",
            description="A test resource"
        )
        
        assert element.name == "test-resource"
        assert element.description == "A test resource"

    def test_get_resources_element_name_only(self):
        """Test GetResourcesElement with name only"""
        element = GetResourcesElement(name="test-resource")
        
        assert element.name == "test-resource"
        assert element.description is None

    def test_get_resources_element_none_description(self):
        """Test GetResourcesElement with explicit None description"""
        element = GetResourcesElement(
            name="test-resource",
            description=None
        )
        
        assert element.name == "test-resource"
        assert element.description is None

    def test_get_resources_element_empty_description(self):
        """Test GetResourcesElement with empty string description"""
        element = GetResourcesElement(
            name="test-resource",
            description=""
        )
        
        assert element.name == "test-resource"
        assert element.description == ""

    def test_get_resources_element_name_required(self):
        """Test that name is required"""
        with pytest.raises(ValidationError) as exc_info:
            GetResourcesElement(description="Missing name")
        
        assert "name" in str(exc_info.value)
        assert "Field required" in str(exc_info.value)

    def test_get_resources_element_serialization(self):
        """Test model serialization"""
        element = GetResourcesElement(
            name="test-resource",
            description="A test resource"
        )
        
        data = element.model_dump()
        assert data == {
            "name": "test-resource",
            "description": "A test resource"
        }

    def test_get_resources_element_json_serialization(self):
        """Test JSON serialization"""
        element = GetResourcesElement(
            name="test-resource",
            description="A test resource"
        )
        
        json_str = element.model_dump_json()
        assert '"name":"test-resource"' in json_str
        assert '"description":"A test resource"' in json_str


class TestGetResourcesResponse:
    """Test the GetResourcesResponse model"""

    def test_get_resources_response_empty(self):
        """Test empty GetResourcesResponse"""
        response = GetResourcesResponse(root=[])
        
        assert response.root == []
        assert len(response.root) == 0

    def test_get_resources_response_with_elements(self):
        """Test GetResourcesResponse with elements"""
        elements = [
            GetResourcesElement(name="resource1", description="First resource"),
            GetResourcesElement(name="resource2", description="Second resource"),
        ]
        
        response = GetResourcesResponse(root=elements)
        
        assert len(response.root) == 2
        assert response.root[0].name == "resource1"
        assert response.root[1].name == "resource2"

    def test_get_resources_response_default_factory(self):
        """Test GetResourcesResponse default factory"""
        response = GetResourcesResponse()
        
        assert response.root == []
        assert isinstance(response.root, list)

    def test_get_resources_response_iteration(self):
        """Test that GetResourcesResponse can be iterated"""
        elements = [
            GetResourcesElement(name="resource1"),
            GetResourcesElement(name="resource2"),
        ]
        
        response = GetResourcesResponse(root=elements)
        
        names = [element.name for element in response.root]
        assert names == ["resource1", "resource2"]


class TestCreateResourceResponse:
    """Test the CreateResourceResponse model"""

    def test_create_resource_response_instantiation(self):
        """Test CreateResourceResponse can be instantiated"""
        response = CreateResourceResponse()
        
        assert isinstance(response, CreateResourceResponse)

    def test_create_resource_response_is_base_model(self):
        """Test CreateResourceResponse inherits from BaseModel"""
        response = CreateResourceResponse()
        
        # Should have BaseModel methods
        assert hasattr(response, 'model_dump')
        assert hasattr(response, 'model_validate')

    def test_create_resource_response_serialization(self):
        """Test CreateResourceResponse serialization"""
        response = CreateResourceResponse()
        
        data = response.model_dump()
        assert isinstance(data, dict)


class TestAction:
    """Test the Action model"""

    def test_action_basic(self):
        """Test basic Action creation"""
        action = Action(
            name="create_vlan",
            type="create",
            input_schema={"type": "object", "properties": {"vlan_id": {"type": "integer"}}}
        )
        
        assert action.name == "create_vlan"
        assert action.type == "create"
        assert action.input_schema == {"type": "object", "properties": {"vlan_id": {"type": "integer"}}}

    def test_action_all_types(self):
        """Test Action with all valid types"""
        for action_type in ["create", "update", "delete"]:
            action = Action(
                name=f"{action_type}_action",
                type=action_type,
                input_schema={"type": "object"}
            )
            assert action.type == action_type

    def test_action_invalid_type(self):
        """Test Action with invalid type"""
        with pytest.raises(ValidationError) as exc_info:
            Action(
                name="invalid_action",
                type="invalid_type",
                input_schema={"type": "object"}
            )
        
        assert "invalid_type" in str(exc_info.value)

    def test_action_complex_schema(self):
        """Test Action with complex schema"""
        complex_schema = {
            "type": "object",
            "properties": {
                "name": {"type": "string"},
                "config": {
                    "type": "object",
                    "properties": {
                        "vlan_id": {"type": "integer"},
                        "description": {"type": "string"}
                    }
                }
            },
            "required": ["name"]
        }
        
        action = Action(
            name="complex_action",
            type="create",
            input_schema=complex_schema
        )
        
        assert action.input_schema == complex_schema

    def test_action_required_fields(self):
        """Test Action with missing required fields"""
        # Test missing name
        try:
            Action(type="create", input_schema={"type": "object"})  # Missing name
            assert False, "Should have raised ValidationError"
        except ValidationError as e:
            assert "name" in str(e)
        
        # Test missing type  
        try:
            Action(name="test", input_schema={"type": "object"})  # Missing type
            assert False, "Should have raised ValidationError"
        except ValidationError as e:
            assert "type" in str(e)
        
        # Test missing input_schema
        try:
            Action(name="test", type="create")  # Missing input_schema
            assert False, "Should have raised ValidationError"
        except ValidationError as e:
            assert "input_schema" in str(e)


class TestDescribeResourceResponse:
    """Test the DescribeResourceResponse model"""

    def test_describe_resource_response_basic(self):
        """Test basic DescribeResourceResponse creation"""
        actions = [
            Action(name="create", type="create", input_schema={"type": "object"}),
            Action(name="delete", type="delete", input_schema={"type": "object"}),
        ]
        
        response = DescribeResourceResponse(
            name="test-resource",
            description="A test resource",
            actions=actions
        )
        
        assert response.name == "test-resource"
        assert response.description == "A test resource"
        assert len(response.actions) == 2
        assert response.actions[0].name == "create"
        assert response.actions[1].name == "delete"

    def test_describe_resource_response_no_actions(self):
        """Test DescribeResourceResponse with no actions"""
        response = DescribeResourceResponse(
            name="test-resource",
            description="A test resource"
        )
        
        assert response.name == "test-resource"
        assert response.description == "A test resource"
        assert response.actions == []

    def test_describe_resource_response_none_description(self):
        """Test DescribeResourceResponse with None description"""
        response = DescribeResourceResponse(
            name="test-resource"
        )
        
        assert response.name == "test-resource"
        assert response.description is None
        assert response.actions == []


class TestLastAction:
    """Test the LastAction model"""

    def test_last_action_basic(self):
        """Test basic LastAction creation"""
        action = LastAction(
            name="create_service",
            type="create",
            status="complete"
        )
        
        assert action.name == "create_service"
        assert action.type == "create"
        assert action.status == "complete"

    def test_last_action_all_types(self):
        """Test LastAction with all valid types"""
        for action_type in ["create", "update", "delete"]:
            action = LastAction(
                name=f"{action_type}_service",
                type=action_type,
                status="complete"
            )
            assert action.type == action_type

    def test_last_action_all_statuses(self):
        """Test LastAction with all valid statuses"""
        for status in ["running", "error", "complete", "canceled", "paused"]:
            action = LastAction(
                name="test_service",
                type="create",
                status=status
            )
            assert action.status == status

    def test_last_action_invalid_type(self):
        """Test LastAction with invalid type"""
        with pytest.raises(ValidationError):
            LastAction(
                name="test",
                type="invalid_type",
                status="complete"
            )

    def test_last_action_invalid_status(self):
        """Test LastAction with invalid status"""
        with pytest.raises(ValidationError):
            LastAction(
                name="test",
                type="create",
                status="invalid_status"
            )


class TestGetInstancesElement:
    """Test the GetInstancesElement model"""

    def test_get_instances_element_basic(self):
        """Test basic GetInstancesElement creation"""
        last_action = LastAction(
            name="create_service",
            type="create",
            status="complete"
        )
        
        element = GetInstancesElement(
            name="service-instance-1",
            description="First service instance",
            instance_data={"vlan_id": 100, "name": "test-vlan"},
            last_action=last_action
        )
        
        assert element.name == "service-instance-1"
        assert element.description == "First service instance"
        assert element.instance_data == {"vlan_id": 100, "name": "test-vlan"}
        assert element.last_action.name == "create_service"

    def test_get_instances_element_none_description(self):
        """Test GetInstancesElement with None description"""
        last_action = LastAction(
            name="create_service",
            type="create",
            status="complete"
        )
        
        element = GetInstancesElement(
            name="service-instance-1",
            description=None,
            instance_data={"vlan_id": 100},
            last_action=last_action
        )
        
        assert element.name == "service-instance-1"
        assert element.description is None

    def test_get_instances_element_complex_instance_data(self):
        """Test GetInstancesElement with complex instance data"""
        last_action = LastAction(
            name="create_service",
            type="create",
            status="complete"
        )
        
        complex_data = {
            "service": {
                "name": "test-service",
                "vlans": [100, 200, 300],
                "config": {
                    "enabled": True,
                    "description": "Test configuration"
                }
            }
        }
        
        element = GetInstancesElement(
            name="complex-instance",
            instance_data=complex_data,
            last_action=last_action
        )
        
        assert element.instance_data == complex_data


class TestGetInstancesResponse:
    """Test the GetInstancesResponse model"""

    def test_get_instances_response_empty(self):
        """Test empty GetInstancesResponse"""
        response = GetInstancesResponse(root=[])
        
        assert response.root == []
        assert len(response.root) == 0

    def test_get_instances_response_with_elements(self):
        """Test GetInstancesResponse with elements"""
        last_action = LastAction(
            name="create_service",
            type="create",
            status="complete"
        )
        
        elements = [
            GetInstancesElement(
                name="instance1",
                instance_data={"id": 1},
                last_action=last_action
            ),
            GetInstancesElement(
                name="instance2",
                instance_data={"id": 2},
                last_action=last_action
            ),
        ]
        
        response = GetInstancesResponse(root=elements)
        
        assert len(response.root) == 2
        assert response.root[0].name == "instance1"
        assert response.root[1].name == "instance2"


class TestDescribeInstanceResponse:
    """Test the DescribeInstanceResponse model"""

    def test_describe_instance_response_basic(self):
        """Test basic DescribeInstanceResponse creation"""
        last_action = LastAction(
            name="create_service",
            type="create",
            status="complete"
        )
        
        response = DescribeInstanceResponse(
            description="Test instance",
            instance_data={"vlan_id": 100},
            last_action=last_action
        )
        
        assert response.description == "Test instance"
        assert response.instance_data == {"vlan_id": 100}
        assert response.last_action.name == "create_service"

    def test_describe_instance_response_none_description(self):
        """Test DescribeInstanceResponse with None description"""
        last_action = LastAction(
            name="create_service",
            type="create",
            status="complete"
        )
        
        response = DescribeInstanceResponse(
            description=None,
            instance_data={"vlan_id": 100},
            last_action=last_action
        )
        
        assert response.description is None
        assert response.instance_data == {"vlan_id": 100}


class TestRunActionResponse:
    """Test the RunActionResponse model"""

    def test_run_action_response_basic(self):
        """Test basic RunActionResponse creation"""
        response = RunActionResponse(
            message="Action started successfully",
            start_time="2024-01-01T12:00:00Z",
            job_id="job-12345",
            status="running"
        )
        
        assert response.message == "Action started successfully"
        assert response.start_time == "2024-01-01T12:00:00Z"
        assert response.job_id == "job-12345"
        assert response.status == "running"

    def test_run_action_response_none_message(self):
        """Test RunActionResponse with None message"""
        response = RunActionResponse(
            message=None,
            start_time="2024-01-01T12:00:00Z",
            job_id="job-12345",
            status="running"
        )
        
        assert response.message is None
        assert response.start_time == "2024-01-01T12:00:00Z"
        assert response.job_id == "job-12345"
        assert response.status == "running"

    def test_run_action_response_required_fields(self):
        """Test RunActionResponse with missing required fields"""
        with pytest.raises(ValidationError):
            RunActionResponse(
                message="Test",
                job_id="job-12345",
                status="running"
                # Missing start_time
            )
        
        with pytest.raises(ValidationError):
            RunActionResponse(
                message="Test",
                start_time="2024-01-01T12:00:00Z",
                status="running"
                # Missing job_id
            )
        
        with pytest.raises(ValidationError):
            RunActionResponse(
                message="Test",
                start_time="2024-01-01T12:00:00Z",
                job_id="job-12345"
                # Missing status
            )


class TestModelIntegration:
    """Test model integration and real-world usage scenarios"""

    def test_full_workflow_models(self):
        """Test models working together in a realistic workflow"""
        # Create a resource element
        resource_element = GetResourcesElement(
            name="network-service",
            description="Network service resource"
        )
        
        # Create a resources response
        resources_response = GetResourcesResponse(root=[resource_element])
        
        # Create an action
        create_action = Action(
            name="provision",
            type="create",
            input_schema={"type": "object", "properties": {"vlan_id": {"type": "integer"}}}
        )
        
        # Create a describe resource response
        describe_response = DescribeResourceResponse(
            name="network-service",
            description="Network service resource",
            actions=[create_action]
        )
        
        # Create a last action
        last_action = LastAction(
            name="provision",
            type="create",
            status="complete"
        )
        
        # Create an instance element
        instance_element = GetInstancesElement(
            name="service-1",
            description="First service instance",
            instance_data={"vlan_id": 100, "status": "active"},
            last_action=last_action
        )
        
        # Create instances response
        instances_response = GetInstancesResponse(root=[instance_element])
        
        # Create describe instance response
        instance_response = DescribeInstanceResponse(
            description="First service instance",
            instance_data={"vlan_id": 100, "status": "active"},
            last_action=last_action
        )
        
        # Create run action response
        action_response = RunActionResponse(
            message="Service provisioned successfully",
            start_time="2024-01-01T12:00:00Z",
            job_id="job-12345",
            status="complete"
        )
        
        # Verify all models work together
        assert len(resources_response.root) == 1
        assert resources_response.root[0].name == "network-service"
        assert len(describe_response.actions) == 1
        assert describe_response.actions[0].name == "provision"
        assert len(instances_response.root) == 1
        assert instances_response.root[0].name == "service-1"
        assert instance_response.instance_data["vlan_id"] == 100
        assert action_response.job_id == "job-12345"

    def test_model_serialization_roundtrip(self):
        """Test that models can be serialized and deserialized"""
        # Create original model
        last_action = LastAction(
            name="test_action",
            type="create",
            status="complete"
        )
        
        element = GetInstancesElement(
            name="test-instance",
            description="Test instance",
            instance_data={"key": "value"},
            last_action=last_action
        )
        
        # Serialize to dict
        data = element.model_dump()
        
        # Deserialize back to model
        restored_element = GetInstancesElement.model_validate(data)
        
        # Verify they're equivalent
        assert restored_element.name == element.name
        assert restored_element.description == element.description
        assert restored_element.instance_data == element.instance_data
        assert restored_element.last_action.name == element.last_action.name
        assert restored_element.last_action.type == element.last_action.type
        assert restored_element.last_action.status == element.last_action.status