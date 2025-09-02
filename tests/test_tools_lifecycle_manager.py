# Copyright (c) 2025 Itential, Inc
# GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)

import pytest
import json
from unittest.mock import AsyncMock, patch

from fastmcp import Context

from itential_mcp import exceptions
from itential_mcp import errors
from itential_mcp.tools import lifecycle_manager
from itential_mcp.models.lifecycle_manager import (
    GetResourcesResponse,
    CreateResourceResponse,
    DescribeResourceResponse,
    GetInstancesResponse,
    DescribeInstanceResponse,
    RunActionResponse,
    LastAction
)


class TestModule:
    """Test the lifecycle_manager tools module"""

    def test_module_tags(self):
        """Test module has correct tags"""
        assert hasattr(lifecycle_manager, '__tags__')
        assert lifecycle_manager.__tags__ == ("lifecycle_manager",)

    def test_module_functions_exist(self):
        """Test all expected functions exist in the module"""
        expected_functions = [
            'get_resources',
            'create_resource',
            'describe_resource',
            'get_instances',
            'describe_instance',
            'run_action'
        ]
        
        for func_name in expected_functions:
            assert hasattr(lifecycle_manager, func_name)
            assert callable(getattr(lifecycle_manager, func_name))

    def test_functions_are_async(self):
        """Test that all functions are async"""
        import inspect
        
        async_functions = [
            lifecycle_manager.get_resources,
            lifecycle_manager.create_resource,
            lifecycle_manager.describe_resource,
            lifecycle_manager.get_instances,
            lifecycle_manager.describe_instance,
            lifecycle_manager.run_action
        ]
        
        for func in async_functions:
            assert inspect.iscoroutinefunction(func)


class TestGetResources:
    """Test the get_resources function"""

    @pytest.fixture
    def mock_context(self):
        """Create a mock FastMCP context"""
        context = AsyncMock(spec=Context)
        context.info = AsyncMock()
        
        # Mock the nested structure
        mock_client = AsyncMock()
        mock_lifecycle_manager = AsyncMock()
        mock_client.lifecycle_manager = mock_lifecycle_manager
        
        context.request_context.lifespan_context.get.return_value = mock_client
        
        return context

    @pytest.mark.asyncio
    async def test_get_resources_success(self, mock_context):
        """Test get_resources with successful response"""
        # Mock service response
        mock_service_data = [
            {"_id": "1", "name": "resource1", "description": "First resource"},
            {"_id": "2", "name": "resource2", "description": "Second resource"}
        ]
        
        mock_client = mock_context.request_context.lifespan_context.get.return_value
        mock_client.lifecycle_manager.get_resources.return_value = mock_service_data

        result = await lifecycle_manager.get_resources(mock_context)

        # Verify result is correct type
        assert isinstance(result, GetResourcesResponse)
        assert len(result.root) == 2
        
        # Verify elements
        assert result.root[0].name == "resource1"
        assert result.root[0].description == "First resource"
        assert result.root[1].name == "resource2"
        assert result.root[1].description == "Second resource"
        
        # Verify service calls
        mock_context.info.assert_called_once_with("inside get_resources(...)")
        mock_client.lifecycle_manager.get_resources.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_resources_empty_response(self, mock_context):
        """Test get_resources with empty response"""
        mock_client = mock_context.request_context.lifespan_context.get.return_value
        mock_client.lifecycle_manager.get_resources.return_value = []

        result = await lifecycle_manager.get_resources(mock_context)

        assert isinstance(result, GetResourcesResponse)
        assert len(result.root) == 0
        assert result.root == []

    @pytest.mark.asyncio
    async def test_get_resources_missing_description(self, mock_context):
        """Test get_resources with missing description field"""
        mock_service_data = [
            {"_id": "1", "name": "resource1"},  # Missing description
            {"_id": "2", "name": "resource2", "description": None}  # Explicit None
        ]
        
        mock_client = mock_context.request_context.lifespan_context.get.return_value
        mock_client.lifecycle_manager.get_resources.return_value = mock_service_data

        result = await lifecycle_manager.get_resources(mock_context)

        assert isinstance(result, GetResourcesResponse)
        assert len(result.root) == 2
        assert result.root[0].name == "resource1"
        assert result.root[0].description is None
        assert result.root[1].name == "resource2"
        assert result.root[1].description is None

    @pytest.mark.asyncio
    async def test_get_resources_service_exception(self, mock_context):
        """Test get_resources when service raises exception"""
        mock_client = mock_context.request_context.lifespan_context.get.return_value
        mock_client.lifecycle_manager.get_resources.side_effect = Exception("Service error")

        with pytest.raises(Exception, match="Service error"):
            await lifecycle_manager.get_resources(mock_context)


class TestCreateResource:
    """Test the create_resource function"""

    @pytest.fixture
    def mock_context(self):
        """Create a mock FastMCP context"""
        context = AsyncMock(spec=Context)
        context.info = AsyncMock()
        
        mock_client = AsyncMock()
        mock_lifecycle_manager = AsyncMock()
        mock_client.lifecycle_manager = mock_lifecycle_manager
        
        context.request_context.lifespan_context.get.return_value = mock_client
        
        return context

    @pytest.mark.asyncio
    async def test_create_resource_success(self, mock_context):
        """Test create_resource with successful creation"""
        test_schema = {"type": "object", "properties": {"name": {"type": "string"}}}
        
        mock_client = mock_context.request_context.lifespan_context.get.return_value
        mock_client.lifecycle_manager.describe_resource.side_effect = exceptions.NotFoundError("Not found")
        mock_client.lifecycle_manager.create_resource.return_value = {"_id": "new-id"}

        result = await lifecycle_manager.create_resource(
            mock_context, 
            "test-resource", 
            test_schema, 
            "Test description"
        )

        assert isinstance(result, CreateResourceResponse)
        mock_context.info.assert_called_once_with("inside create_resource(...)")
        mock_client.lifecycle_manager.describe_resource.assert_called_once_with("test-resource")
        mock_client.lifecycle_manager.create_resource.assert_called_once_with(
            "test-resource", test_schema, "Test description"
        )

    @pytest.mark.asyncio
    async def test_create_resource_already_exists(self, mock_context):
        """Test create_resource when resource already exists"""
        test_schema = {"type": "object"}
        existing_resource = {"_id": "existing-id", "name": "test-resource"}
        
        mock_client = mock_context.request_context.lifespan_context.get.return_value
        mock_client.lifecycle_manager.describe_resource.return_value = existing_resource

        with patch.object(errors, 'resource_already_exists') as mock_error:
            mock_error.return_value = {"error": "Already exists"}
            
            result = await lifecycle_manager.create_resource(
                mock_context, 
                "test-resource", 
                test_schema,
                None  # description
            )

            assert result == {"error": "Already exists"}
            mock_error.assert_called_once_with("resource test-resource already exists")
            mock_client.lifecycle_manager.create_resource.assert_not_called()

    @pytest.mark.asyncio
    async def test_create_resource_no_description(self, mock_context):
        """Test create_resource without description"""
        test_schema = {"type": "object"}
        
        mock_client = mock_context.request_context.lifespan_context.get.return_value
        mock_client.lifecycle_manager.describe_resource.side_effect = exceptions.NotFoundError("Not found")
        mock_client.lifecycle_manager.create_resource.return_value = {"_id": "new-id"}

        result = await lifecycle_manager.create_resource(
            mock_context, 
            "test-resource", 
            test_schema,
            None  # description
        )

        assert isinstance(result, CreateResourceResponse)
        mock_client.lifecycle_manager.create_resource.assert_called_once_with(
            "test-resource", test_schema, None
        )


class TestDescribeResource:
    """Test the describe_resource function"""

    @pytest.fixture
    def mock_context(self):
        """Create a mock FastMCP context"""
        context = AsyncMock(spec=Context)
        context.info = AsyncMock()
        
        mock_client = AsyncMock()
        mock_lifecycle_manager = AsyncMock()
        mock_transformations = AsyncMock()
        mock_automation_studio = AsyncMock()
        
        mock_client.lifecycle_manager = mock_lifecycle_manager
        mock_client.transformations = mock_transformations
        mock_client.automation_studio = mock_automation_studio
        
        context.request_context.lifespan_context.get.return_value = mock_client
        
        return context

    @pytest.mark.asyncio
    async def test_describe_resource_success(self, mock_context):
        """Test describe_resource with successful response"""
        mock_resource_data = {
            "_id": "resource123",
            "name": "test-resource",
            "description": "A test resource",
            "schema": {"type": "object"},
            "actions": [
                {
                    "_id": "action1",
                    "name": "create",
                    "type": "create",
                    "preWorkflowJst": None,
                    "workflow": None
                }
            ]
        }
        
        mock_client = mock_context.request_context.lifespan_context.get.return_value
        mock_client.lifecycle_manager.describe_resource.return_value = mock_resource_data

        result = await lifecycle_manager.describe_resource(mock_context, "test-resource")

        assert isinstance(result, DescribeResourceResponse)
        assert result.name == "test-resource"
        assert result.description == "A test resource"
        assert len(result.actions) == 1
        assert result.actions[0].name == "create"
        assert result.actions[0].type == "create"
        assert result.actions[0].input_schema == {"type": "object"}

    @pytest.mark.asyncio
    async def test_describe_resource_not_found(self, mock_context):
        """Test describe_resource when resource not found"""
        mock_client = mock_context.request_context.lifespan_context.get.return_value
        mock_client.lifecycle_manager.describe_resource.side_effect = exceptions.NotFoundError("Not found")

        with patch.object(errors, 'resource_not_found') as mock_error:
            mock_error.return_value = {"error": "Resource not found"}
            
            result = await lifecycle_manager.describe_resource(mock_context, "nonexistent")

            assert result == {"error": "Resource not found"}
            mock_error.assert_called_once_with("resource nonexistent not found on the server")

    @pytest.mark.asyncio
    async def test_describe_resource_with_transformation(self, mock_context):
        """Test describe_resource with preWorkflowJst transformation"""
        mock_resource_data = {
            "_id": "resource123",
            "name": "test-resource",
            "description": "A test resource",
            "schema": {"type": "object"},
            "actions": [
                {
                    "_id": "action1",
                    "name": "create",
                    "type": "create",
                    "preWorkflowJst": "transformation123",
                    "workflow": None
                }
            ]
        }
        
        mock_transformation_data = {
            "incoming": {"type": "object", "properties": {"custom": {"type": "string"}}}
        }
        
        mock_client = mock_context.request_context.lifespan_context.get.return_value
        mock_client.lifecycle_manager.describe_resource.return_value = mock_resource_data
        mock_client.transformations.describe_transformation.return_value = mock_transformation_data

        result = await lifecycle_manager.describe_resource(mock_context, "test-resource")

        assert isinstance(result, DescribeResourceResponse)
        assert result.actions[0].input_schema == mock_transformation_data["incoming"]
        mock_client.transformations.describe_transformation.assert_called_once_with("transformation123")

    @pytest.mark.asyncio
    async def test_describe_resource_with_workflow(self, mock_context):
        """Test describe_resource with workflow"""
        mock_resource_data = {
            "_id": "resource123",
            "name": "test-resource",
            "description": "A test resource",
            "schema": {"type": "object"},
            "actions": [
                {
                    "_id": "action1",
                    "name": "create",
                    "type": "create",
                    "preWorkflowJst": None,
                    "workflow": "workflow123"
                }
            ]
        }
        
        mock_workflow_data = {
            "inputSchema": {"type": "object", "properties": {"workflow_input": {"type": "string"}}}
        }
        
        mock_client = mock_context.request_context.lifespan_context.get.return_value
        mock_client.lifecycle_manager.describe_resource.return_value = mock_resource_data
        mock_client.automation_studio.describe_workflow.return_value = mock_workflow_data

        result = await lifecycle_manager.describe_resource(mock_context, "test-resource")

        assert isinstance(result, DescribeResourceResponse)
        assert result.actions[0].input_schema == mock_workflow_data["inputSchema"]
        mock_client.automation_studio.describe_workflow.assert_called_once_with("workflow123")

    @pytest.mark.asyncio
    async def test_describe_resource_transformation_not_found(self, mock_context):
        """Test describe_resource when transformation is not found"""
        mock_resource_data = {
            "_id": "resource123",
            "name": "test-resource",
            "description": "A test resource",
            "schema": {"type": "object"},
            "actions": [
                {
                    "_id": "action1",
                    "name": "create",
                    "type": "create",
                    "preWorkflowJst": "missing-transformation",
                    "workflow": None
                }
            ]
        }
        
        mock_client = mock_context.request_context.lifespan_context.get.return_value
        mock_client.lifecycle_manager.describe_resource.return_value = mock_resource_data
        mock_client.transformations.describe_transformation.side_effect = exceptions.NotFoundError("Transformation not found")

        with patch.object(errors, 'resource_not_found') as mock_error:
            mock_error.return_value = {"error": "Transformation not found"}
            
            result = await lifecycle_manager.describe_resource(mock_context, "test-resource")

            assert result == {"error": "Transformation not found"}


class TestGetInstances:
    """Test the get_instances function"""

    @pytest.fixture
    def mock_context(self):
        """Create a mock FastMCP context"""
        context = AsyncMock(spec=Context)
        context.info = AsyncMock()
        
        mock_client = AsyncMock()
        mock_lifecycle_manager = AsyncMock()
        mock_client.lifecycle_manager = mock_lifecycle_manager
        
        context.request_context.lifespan_context.get.return_value = mock_client
        
        return context

    @pytest.mark.asyncio
    async def test_get_instances_success(self, mock_context):
        """Test get_instances with successful response"""
        mock_instances_data = [
            {
                "name": "instance1",
                "description": "First instance",
                "instanceData": {"vlan_id": 100},
                "lastAction": {
                    "name": "create",
                    "type": "create",
                    "status": "complete"
                }
            },
            {
                "name": "instance2",
                "description": "Second instance",
                "instanceData": {"vlan_id": 200},
                "lastAction": {
                    "name": "update",
                    "type": "update",
                    "status": "running"
                }
            }
        ]
        
        mock_client = mock_context.request_context.lifespan_context.get.return_value
        mock_client.lifecycle_manager.get_instances.return_value = mock_instances_data

        result = await lifecycle_manager.get_instances(mock_context, "test-resource")

        assert isinstance(result, GetInstancesResponse)
        assert len(result.root) == 2
        
        # Check first instance
        assert result.root[0].name == "instance1"
        assert result.root[0].description == "First instance"
        assert result.root[0].instance_data == {"vlan_id": 100}
        assert result.root[0].last_action.name == "create"
        assert result.root[0].last_action.type == "create"
        assert result.root[0].last_action.status == "complete"
        
        # Check second instance
        assert result.root[1].name == "instance2"
        assert result.root[1].last_action.status == "running"
        
        mock_client.lifecycle_manager.get_instances.assert_called_once_with("test-resource")

    @pytest.mark.asyncio
    async def test_get_instances_empty_response(self, mock_context):
        """Test get_instances with empty response"""
        mock_client = mock_context.request_context.lifespan_context.get.return_value
        mock_client.lifecycle_manager.get_instances.return_value = []

        result = await lifecycle_manager.get_instances(mock_context, "test-resource")

        assert isinstance(result, GetInstancesResponse)
        assert len(result.root) == 0
        assert result.root == []

    @pytest.mark.asyncio
    async def test_get_instances_missing_description(self, mock_context):
        """Test get_instances with missing description field"""
        mock_instances_data = [
            {
                "name": "instance1",
                # Missing description
                "instanceData": {"vlan_id": 100},
                "lastAction": {
                    "name": "create",
                    "type": "create",
                    "status": "complete"
                }
            }
        ]
        
        mock_client = mock_context.request_context.lifespan_context.get.return_value
        mock_client.lifecycle_manager.get_instances.return_value = mock_instances_data

        result = await lifecycle_manager.get_instances(mock_context, "test-resource")

        assert isinstance(result, GetInstancesResponse)
        assert len(result.root) == 1
        assert result.root[0].name == "instance1"
        assert result.root[0].description is None


class TestDescribeInstance:
    """Test the describe_instance function"""

    @pytest.fixture
    def mock_context(self):
        """Create a mock FastMCP context"""
        context = AsyncMock(spec=Context)
        context.info = AsyncMock()
        
        mock_client = AsyncMock()
        mock_lifecycle_manager = AsyncMock()
        mock_client.lifecycle_manager = mock_lifecycle_manager
        
        context.request_context.lifespan_context.get.return_value = mock_client
        
        return context

    @pytest.mark.asyncio
    async def test_describe_instance_success(self, mock_context):
        """Test describe_instance with successful response"""
        mock_instance_data = {
            "description": "Test instance",
            "instanceData": {"vlan_id": 100, "name": "test-vlan"},
            "lastAction": {
                "name": "create",
                "type": "create",
                "status": "complete"
            }
        }
        
        mock_client = mock_context.request_context.lifespan_context.get.return_value
        mock_client.lifecycle_manager.describe_instance.return_value = mock_instance_data

        result = await lifecycle_manager.describe_instance(
            mock_context, 
            "test-resource", 
            "test-instance"
        )

        assert isinstance(result, DescribeInstanceResponse)
        assert result.description == "Test instance"
        assert result.instance_data == {"vlan_id": 100, "name": "test-vlan"}
        assert result.last_action.name == "create"
        assert result.last_action.type == "create"
        assert result.last_action.status == "complete"
        
        mock_client.lifecycle_manager.describe_instance.assert_called_once_with(
            "test-resource", "test-instance"
        )

    @pytest.mark.asyncio
    async def test_describe_instance_missing_description(self, mock_context):
        """Test describe_instance with missing description field"""
        mock_instance_data = {
            # Missing description
            "instanceData": {"vlan_id": 100},
            "lastAction": {
                "name": "create",
                "type": "create",
                "status": "complete"
            }
        }
        
        mock_client = mock_context.request_context.lifespan_context.get.return_value
        mock_client.lifecycle_manager.describe_instance.return_value = mock_instance_data

        result = await lifecycle_manager.describe_instance(
            mock_context, 
            "test-resource", 
            "test-instance"
        )

        assert isinstance(result, DescribeInstanceResponse)
        assert result.description is None
        assert result.instance_data == {"vlan_id": 100}


class TestRunAction:
    """Test the run_action function"""

    @pytest.fixture
    def mock_context(self):
        """Create a mock FastMCP context"""
        context = AsyncMock(spec=Context)
        context.info = AsyncMock()
        
        mock_client = AsyncMock()
        mock_lifecycle_manager = AsyncMock()
        mock_client.lifecycle_manager = mock_lifecycle_manager
        
        context.request_context.lifespan_context.get.return_value = mock_client
        
        return context

    @pytest.mark.asyncio
    async def test_run_action_success(self, mock_context):
        """Test run_action with successful response"""
        mock_response_data = {
            "message": "Action completed successfully",
            "data": {
                "startTime": "2024-01-01T12:00:00Z",
                "jobId": "job-12345",
                "status": "complete"
            }
        }
        
        mock_client = mock_context.request_context.lifespan_context.get.return_value
        mock_client.lifecycle_manager.run_action.return_value = mock_response_data

        result = await lifecycle_manager.run_action(
            mock_context,
            "test-resource",
            "create",
            "test-instance",
            "Test instance description",
            {"vlan_id": 100}
        )

        assert isinstance(result, RunActionResponse)
        assert result.message == "Action completed successfully"
        assert result.start_time == "2024-01-01T12:00:00Z"
        assert result.job_id == "job-12345"
        assert result.status == "complete"
        
        mock_client.lifecycle_manager.run_action.assert_called_once_with(
            "test-resource", "create", "test-instance", "Test instance description", {"vlan_id": 100}
        )

    @pytest.mark.asyncio
    async def test_run_action_not_found_error(self, mock_context):
        """Test run_action with NotFoundError"""
        mock_client = mock_context.request_context.lifespan_context.get.return_value
        mock_client.lifecycle_manager.run_action.side_effect = exceptions.NotFoundError("Resource not found")

        with patch.object(errors, 'resource_not_found') as mock_error:
            mock_error.return_value = {"error": "Resource not found"}
            
            result = await lifecycle_manager.run_action(
                mock_context,
                "nonexistent-resource",
                "create",
                None,  # instance_name
                None,  # instance_description
                None   # input_params
            )

            assert result == {"error": "Resource not found"}
            mock_error.assert_called_once_with("Could not find a resource named nonexistent-resource")

    @pytest.mark.asyncio
    async def test_run_action_client_exception(self, mock_context):
        """Test run_action with ClientException"""
        client_error = exceptions.ClientException("Invalid request")
        client_error.message = "Invalid request"
        
        mock_client = mock_context.request_context.lifespan_context.get.return_value
        mock_client.lifecycle_manager.run_action.side_effect = client_error

        with patch.object(errors, 'bad_request') as mock_error:
            mock_error.return_value = {"error": "Bad request"}
            
            result = await lifecycle_manager.run_action(
                mock_context,
                "test-resource",
                "create",
                None,  # instance_name
                None,  # instance_description
                None   # input_params
            )

            assert result == {"error": "Bad request"}
            mock_error.assert_called_once_with("Invalid request")

    @pytest.mark.asyncio
    async def test_run_action_itential_mcp_exception(self, mock_context):
        """Test run_action with ItentialMcpException containing JSON"""
        json_error_message = json.dumps({"message": "Custom error message"})
        itential_error = exceptions.ItentialMcpException(json_error_message)
        itential_error.message = json_error_message
        
        mock_client = mock_context.request_context.lifespan_context.get.return_value
        mock_client.lifecycle_manager.run_action.side_effect = itential_error

        with patch.object(errors, 'bad_request') as mock_error:
            mock_error.return_value = {"error": "Custom error"}
            
            result = await lifecycle_manager.run_action(
                mock_context,
                "test-resource",
                "create",
                None,  # instance_name
                None,  # instance_description
                None   # input_params
            )

            assert result == {"error": "Custom error"}
            mock_error.assert_called_once_with("Custom error message")

    @pytest.mark.asyncio
    async def test_run_action_minimal_parameters(self, mock_context):
        """Test run_action with minimal parameters"""
        mock_response_data = {
            "data": {
                "startTime": "2024-01-01T12:00:00Z",
                "jobId": "job-12345",
                "status": "running"
            }
        }
        
        mock_client = mock_context.request_context.lifespan_context.get.return_value
        mock_client.lifecycle_manager.run_action.return_value = mock_response_data

        result = await lifecycle_manager.run_action(
            mock_context,
            "test-resource",
            "create",
            None,  # instance_name
            None,  # instance_description
            None   # input_params
        )

        assert isinstance(result, RunActionResponse)
        assert result.message is None
        assert result.start_time == "2024-01-01T12:00:00Z"
        assert result.job_id == "job-12345"
        assert result.status == "running"
        
        mock_client.lifecycle_manager.run_action.assert_called_once_with(
            "test-resource", "create", None, None, None
        )


class TestFunctionSignatures:
    """Test function signatures and annotations"""

    def test_get_resources_signature(self):
        """Test get_resources function signature"""
        import inspect
        
        sig = inspect.signature(lifecycle_manager.get_resources)
        assert len(sig.parameters) == 1
        assert 'ctx' in sig.parameters
        
        # Check return type annotation
        assert sig.return_annotation == GetResourcesResponse

    def test_create_resource_signature(self):
        """Test create_resource function signature"""
        import inspect
        
        sig = inspect.signature(lifecycle_manager.create_resource)
        expected_params = ['ctx', 'name', 'schema', 'description']
        
        assert len(sig.parameters) == len(expected_params)
        for param in expected_params:
            assert param in sig.parameters
        
        # Check that description parameter exists and has Field annotation
        assert 'description' in sig.parameters
        
        # Check return type annotation
        assert sig.return_annotation == CreateResourceResponse

    def test_describe_resource_signature(self):
        """Test describe_resource function signature"""
        import inspect
        
        sig = inspect.signature(lifecycle_manager.describe_resource)
        assert len(sig.parameters) == 2
        assert 'ctx' in sig.parameters
        assert 'name' in sig.parameters
        
        # Check return type annotation
        assert sig.return_annotation == DescribeResourceResponse

    def test_get_instances_signature(self):
        """Test get_instances function signature"""
        import inspect
        
        sig = inspect.signature(lifecycle_manager.get_instances)
        assert len(sig.parameters) == 2
        assert 'ctx' in sig.parameters
        assert 'resource_name' in sig.parameters
        
        # Check return type annotation
        assert sig.return_annotation == GetInstancesResponse

    def test_describe_instance_signature(self):
        """Test describe_instance function signature"""
        import inspect
        
        sig = inspect.signature(lifecycle_manager.describe_instance)
        assert len(sig.parameters) == 3
        assert 'ctx' in sig.parameters
        assert 'resource_name' in sig.parameters
        assert 'instance_name' in sig.parameters
        
        # Check that instance_name parameter exists
        assert 'instance_name' in sig.parameters
        
        # Check return type annotation
        assert sig.return_annotation == DescribeInstanceResponse

    def test_run_action_signature(self):
        """Test run_action function signature"""
        import inspect
        
        sig = inspect.signature(lifecycle_manager.run_action)
        expected_params = ['ctx', 'resource_name', 'action_name', 'instance_name', 'instance_description', 'input_params']
        
        assert len(sig.parameters) == len(expected_params)
        for param in expected_params:
            assert param in sig.parameters
        
        # Check that optional parameters exist
        assert 'instance_name' in sig.parameters
        assert 'instance_description' in sig.parameters
        assert 'input_params' in sig.parameters
        
        # Check return type annotation
        assert sig.return_annotation == RunActionResponse


class TestDocstrings:
    """Test that all functions have proper docstrings"""

    def test_all_functions_have_docstrings(self):
        """Test that all functions have comprehensive docstrings"""
        functions = [
            lifecycle_manager.get_resources,
            lifecycle_manager.create_resource,
            lifecycle_manager.describe_resource,
            lifecycle_manager.get_instances,
            lifecycle_manager.describe_instance,
            lifecycle_manager.run_action
        ]
        
        for func in functions:
            assert func.__doc__ is not None
            assert len(func.__doc__.strip()) > 0
            
            # Check for required docstring sections
            docstring = func.__doc__
            assert "Args:" in docstring
            assert "Returns:" in docstring
            
            # Check that it mentions relevant concepts
            assert any(keyword in docstring for keyword in [
                "Lifecycle Manager", "lifecycle manager", "resource", "Itential Platform"
            ])

    def test_docstring_parameter_descriptions(self):
        """Test that docstrings describe parameters correctly"""
        # Test get_resources
        doc = lifecycle_manager.get_resources.__doc__
        assert "ctx (Context)" in doc
        
        # Test create_resource
        doc = lifecycle_manager.create_resource.__doc__
        assert "name (str)" in doc
        assert "schema (dict)" in doc
        assert "description (str | None)" in doc
        
        # Test run_action - should document optional parameters
        doc = lifecycle_manager.run_action.__doc__
        assert "resource_name (str)" in doc
        assert "action_name (str)" in doc
        assert "instance_name" in doc
        assert "input_params" in doc


class TestIntegration:
    """Test integration scenarios and edge cases"""

    @pytest.fixture
    def mock_context(self):
        """Create a comprehensive mock FastMCP context"""
        context = AsyncMock(spec=Context)
        context.info = AsyncMock()
        
        mock_client = AsyncMock()
        mock_lifecycle_manager = AsyncMock()
        mock_transformations = AsyncMock()
        mock_automation_studio = AsyncMock()
        
        mock_client.lifecycle_manager = mock_lifecycle_manager
        mock_client.transformations = mock_transformations
        mock_client.automation_studio = mock_automation_studio
        
        context.request_context.lifespan_context.get.return_value = mock_client
        
        return context

    @pytest.mark.asyncio
    async def test_full_workflow_scenario(self, mock_context):
        """Test a full workflow from resource creation to action execution"""
        # Mock create resource
        mock_client = mock_context.request_context.lifespan_context.get.return_value
        
        # First call (for create_resource check) should fail, then succeed for describe_resource
        mock_resource = {
            "_id": "resource123",
            "name": "network-service",
            "description": "Network service resource",
            "schema": {"type": "object"},
            "actions": [
                {
                    "_id": "action1",
                    "name": "provision",
                    "type": "create",
                    "preWorkflowJst": None,
                    "workflow": None
                }
            ]
        }
        
        mock_client.lifecycle_manager.describe_resource.side_effect = [
            exceptions.NotFoundError("Not found"),  # First call fails (for create_resource)
            mock_resource  # Second call succeeds (for describe_resource)
        ]
        mock_client.lifecycle_manager.create_resource.return_value = {"_id": "new-resource"}
        
        # Create resource
        create_result = await lifecycle_manager.create_resource(
            mock_context, 
            "network-service", 
            {"type": "object", "properties": {"vlan_id": {"type": "integer"}}},
            "Network service resource"
        )
        assert isinstance(create_result, CreateResourceResponse)
        
        # Describe resource
        describe_result = await lifecycle_manager.describe_resource(mock_context, "network-service")
        assert isinstance(describe_result, DescribeResourceResponse)
        assert describe_result.name == "network-service"
        assert len(describe_result.actions) == 1
        
        # Mock run action
        mock_action_response = {
            "message": "Provisioning started",
            "data": {
                "startTime": "2024-01-01T12:00:00Z",
                "jobId": "job-12345",
                "status": "running"
            }
        }
        mock_client.lifecycle_manager.run_action.return_value = mock_action_response
        
        # Run action
        action_result = await lifecycle_manager.run_action(
            mock_context,
            "network-service",
            "provision",
            "service-1",
            "First service instance",
            {"vlan_id": 100}
        )
        assert isinstance(action_result, RunActionResponse)
        assert action_result.job_id == "job-12345"

    @pytest.mark.asyncio
    async def test_error_handling_consistency(self, mock_context):
        """Test that error handling is consistent across functions"""
        mock_client = mock_context.request_context.lifespan_context.get.return_value
        
        # Test NotFoundError handling in describe_resource
        mock_client.lifecycle_manager.describe_resource.side_effect = exceptions.NotFoundError("Not found")
        
        with patch.object(errors, 'resource_not_found', return_value={"error": "Not found"}):
            result = await lifecycle_manager.describe_resource(mock_context, "nonexistent")
            assert "error" in result
        
        # Test exception propagation in get_resources
        mock_client.lifecycle_manager.get_resources.side_effect = Exception("Service down")
        
        with pytest.raises(Exception, match="Service down"):
            await lifecycle_manager.get_resources(mock_context)

    @pytest.mark.asyncio
    async def test_context_usage(self, mock_context):
        """Test that context is used correctly in all functions"""
        # Mock service responses
        mock_client = mock_context.request_context.lifespan_context.get.return_value
        mock_client.lifecycle_manager.get_resources.return_value = []
        
        # Call function
        await lifecycle_manager.get_resources(mock_context)
        
        # Verify context methods were called
        mock_context.info.assert_called_with("inside get_resources(...)")
        mock_context.request_context.lifespan_context.get.assert_called_with("client")

    def test_model_imports(self):
        """Test that all required models are properly imported"""
        from itential_mcp.models.lifecycle_manager import (
            GetResourcesResponse,
            CreateResourceResponse,
            DescribeResourceResponse,
            GetInstancesResponse,
            DescribeInstanceResponse,
            RunActionResponse
        )
        
        # Verify models can be instantiated (basic smoke test)
        GetResourcesResponse()
        CreateResourceResponse()
        DescribeResourceResponse(name="test", actions=[])
        GetInstancesResponse()
        DescribeInstanceResponse(
            instance_data={}, 
            last_action=LastAction(name="test", type="create", status="complete")
        )
        RunActionResponse(
            start_time="2024-01-01T00:00:00Z",
            job_id="test",
            status="running"
        )