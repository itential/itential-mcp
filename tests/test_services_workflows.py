# Copyright (c) 2025 Itential, Inc
# GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)

import pytest
from unittest.mock import AsyncMock, MagicMock
from typing import Mapping

from itential_mcp.services.workflows import Service as WorkflowsService
from itential_mcp.services import ServiceBase
from itential_mcp import exceptions
from ipsdk.platform import AsyncPlatform


class TestWorkflowsServiceStructure:
    """Test the basic structure and inheritance of WorkflowsService"""
    
    @pytest.fixture
    def mock_client(self):
        """Create a mock AsyncPlatform client"""
        return AsyncMock(spec=AsyncPlatform)
    
    def test_workflows_service_inherits_from_servicebase(self):
        """Test that WorkflowsService inherits from ServiceBase"""
        assert issubclass(WorkflowsService, ServiceBase)
    
    def test_workflows_service_instantiation(self, mock_client):
        """Test that WorkflowsService can be instantiated"""
        service = WorkflowsService(mock_client)
        
        assert isinstance(service, WorkflowsService)
        assert isinstance(service, ServiceBase)
        assert service.client is mock_client
        assert service.name == "workflows"
    
    def test_workflows_service_has_correct_name(self, mock_client):
        """Test that WorkflowsService has the correct service name"""
        service = WorkflowsService(mock_client)
        assert service.name == "workflows"
        assert hasattr(WorkflowsService, 'name')
        assert WorkflowsService.name == "workflows"
    
    def test_workflows_service_implements_describe_method(self):
        """Test that WorkflowsService implements the abstract describe method"""
        assert hasattr(WorkflowsService, 'describe')
        assert callable(getattr(WorkflowsService, 'describe'))
        
        # Verify it's not abstract anymore (overridden from ServiceBase)
        assert not getattr(WorkflowsService.describe, '__isabstractmethod__', False)
    
    def test_workflows_service_docstring_exists(self):
        """Test that WorkflowsService has comprehensive documentation"""
        assert WorkflowsService.__doc__ is not None
        assert len(WorkflowsService.__doc__.strip()) > 0
        
        docstring = WorkflowsService.__doc__
        assert "Automation Studio workflows" in docstring
        assert "Itential Platform" in docstring
        assert "Args:" in docstring
        assert "Attributes:" in docstring
    
    def test_describe_method_docstring(self):
        """Test that the describe method has proper documentation"""
        assert WorkflowsService.describe.__doc__ is not None
        assert len(WorkflowsService.describe.__doc__.strip()) > 0
        
        docstring = WorkflowsService.describe.__doc__
        assert "workflow_id" in docstring
        assert "Args:" in docstring
        assert "Returns:" in docstring
        assert "Raises:" in docstring
        assert "NotFoundError" in docstring


class TestWorkflowsServiceDescribeMethodSuccess:
    """Test successful operations of the describe method"""
    
    @pytest.fixture
    def mock_client(self):
        """Create a mock AsyncPlatform client"""
        return AsyncMock(spec=AsyncPlatform)
    
    @pytest.fixture
    def sample_workflow_response(self):
        """Sample successful response from API"""
        return {
            "total": 1,
            "items": [
                {
                    "_id": "workflow-123",
                    "name": "Network Configuration Workflow",
                    "description": "Configures network devices",
                    "type": "automation",
                    "version": "1.0.0",
                    "status": "enabled",
                    "tasks": [
                        {"id": "task1", "name": "Backup Config", "type": "backup"},
                        {"id": "task2", "name": "Apply Config", "type": "configure"}
                    ],
                    "created": "2025-01-01T00:00:00Z",
                    "modified": "2025-01-02T00:00:00Z"
                }
            ]
        }
    
    @pytest.mark.asyncio
    async def test_describe_workflow_success(self, mock_client, sample_workflow_response):
        """Test successful workflow retrieval"""
        # Setup mock response
        mock_response = MagicMock()
        mock_response.json.return_value = sample_workflow_response
        mock_client.get.return_value = mock_response
        
        service = WorkflowsService(mock_client)
        result = await service.describe("workflow-123")
        
        # Verify API call was made correctly
        mock_client.get.assert_called_once_with(
            "/automation-studio/workflows",
            params={"equals[_id]": "workflow-123"}
        )
        
        # Verify result
        expected_workflow = sample_workflow_response["items"][0]
        assert result == expected_workflow
        assert result["_id"] == "workflow-123"
        assert result["name"] == "Network Configuration Workflow"
        assert result["type"] == "automation"
    
    @pytest.mark.asyncio
    async def test_describe_workflow_with_complex_data(self, mock_client):
        """Test workflow retrieval with complex nested data structures"""
        complex_response = {
            "total": 1,
            "items": [
                {
                    "_id": "complex-workflow-456",
                    "name": "Complex Workflow",
                    "metadata": {
                        "tags": ["production", "critical"],
                        "owner": "network-team",
                        "environment": "production"
                    },
                    "schema": {
                        "type": "object",
                        "properties": {
                            "device_list": {"type": "array"},
                            "config_template": {"type": "string"}
                        },
                        "required": ["device_list"]
                    },
                    "variables": {
                        "default_timeout": 300,
                        "retry_count": 3,
                        "enable_logging": True
                    }
                }
            ]
        }
        
        mock_response = MagicMock()
        mock_response.json.return_value = complex_response
        mock_client.get.return_value = mock_response
        
        service = WorkflowsService(mock_client)
        result = await service.describe("complex-workflow-456")
        
        # Verify complex nested data is preserved
        assert result["metadata"]["tags"] == ["production", "critical"]
        assert result["schema"]["properties"]["device_list"]["type"] == "array"
        assert result["variables"]["default_timeout"] == 300
        assert result["variables"]["enable_logging"] is True
    
    @pytest.mark.asyncio
    async def test_describe_workflow_return_type(self, mock_client, sample_workflow_response):
        """Test that describe method returns correct type"""
        mock_response = MagicMock()
        mock_response.json.return_value = sample_workflow_response
        mock_client.get.return_value = mock_response
        
        service = WorkflowsService(mock_client)
        result = await service.describe("workflow-123")
        
        assert isinstance(result, dict)
        assert isinstance(result, Mapping)
        
        # Verify it contains expected workflow fields
        assert "_id" in result
        assert "name" in result
        assert isinstance(result["_id"], str)
        assert isinstance(result["name"], str)
    
    @pytest.mark.asyncio
    async def test_describe_workflow_with_different_workflow_ids(self, mock_client):
        """Test describe method with various workflow ID formats"""
        test_ids = [
            "simple-id",
            "workflow-with-dashes-123",
            "workflowWithCamelCase456",
            "workflow_with_underscores_789",
            "65f1a2b3c4d5e6f7g8h9i0j1",  # ObjectId-like format
            "uuid-12345678-1234-1234-1234-123456789012"
        ]
        
        service = WorkflowsService(mock_client)
        
        for workflow_id in test_ids:
            # Setup mock response for each ID
            mock_response = MagicMock()
            mock_response.json.return_value = {
                "total": 1,
                "items": [{"_id": workflow_id, "name": f"Workflow {workflow_id}"}]
            }
            mock_client.get.return_value = mock_response
            
            result = await service.describe(workflow_id)
            
            # Verify correct API call
            mock_client.get.assert_called_with(
                "/automation-studio/workflows",
                params={"equals[_id]": workflow_id}
            )
            
            # Verify result
            assert result["_id"] == workflow_id
            assert result["name"] == f"Workflow {workflow_id}"


class TestWorkflowsServiceDescribeMethodErrors:
    """Test error cases for the describe method"""
    
    @pytest.fixture
    def mock_client(self):
        """Create a mock AsyncPlatform client"""
        return AsyncMock(spec=AsyncPlatform)
    
    @pytest.mark.asyncio
    async def test_describe_workflow_not_found_zero_results(self, mock_client):
        """Test NotFoundError when no workflows match the ID"""
        # Setup mock response with zero results
        mock_response = MagicMock()
        mock_response.json.return_value = {"total": 0, "items": []}
        mock_client.get.return_value = mock_response
        
        service = WorkflowsService(mock_client)
        
        with pytest.raises(exceptions.NotFoundError) as exc_info:
            await service.describe("nonexistent-workflow")
        
        assert "workflow id nonexistent-workflow not found" in str(exc_info.value)
        
        # Verify API was called
        mock_client.get.assert_called_once_with(
            "/automation-studio/workflows",
            params={"equals[_id]": "nonexistent-workflow"}
        )
    
    @pytest.mark.asyncio
    async def test_describe_workflow_not_found_multiple_results(self, mock_client):
        """Test NotFoundError when multiple workflows match (should be impossible but tested)"""
        # Setup mock response with multiple results (edge case)
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "total": 2,
            "items": [
                {"_id": "workflow-123", "name": "Workflow 1"},
                {"_id": "workflow-123", "name": "Workflow 2"}  # Duplicate ID (edge case)
            ]
        }
        mock_client.get.return_value = mock_response
        
        service = WorkflowsService(mock_client)
        
        with pytest.raises(exceptions.NotFoundError) as exc_info:
            await service.describe("workflow-123")
        
        assert "workflow id workflow-123 not found" in str(exc_info.value)
    
    @pytest.mark.asyncio
    async def test_describe_workflow_empty_id(self, mock_client):
        """Test behavior with empty workflow ID"""
        mock_response = MagicMock()
        mock_response.json.return_value = {"total": 0, "items": []}
        mock_client.get.return_value = mock_response
        
        service = WorkflowsService(mock_client)
        
        with pytest.raises(exceptions.NotFoundError) as exc_info:
            await service.describe("")
        
        assert "workflow id  not found" in str(exc_info.value)
        
        # Verify API was called with empty string
        mock_client.get.assert_called_once_with(
            "/automation-studio/workflows",
            params={"equals[_id]": ""}
        )
    
    @pytest.mark.asyncio
    async def test_describe_workflow_client_error_propagation(self, mock_client):
        """Test that client errors are properly propagated"""
        # Setup mock to raise an exception
        mock_client.get.side_effect = ConnectionError("Network connection failed")
        
        service = WorkflowsService(mock_client)
        
        with pytest.raises(ConnectionError) as exc_info:
            await service.describe("workflow-123")
        
        assert "Network connection failed" in str(exc_info.value)
    
    @pytest.mark.asyncio
    async def test_describe_workflow_json_parse_error(self, mock_client):
        """Test behavior when API returns invalid JSON"""
        # Setup mock response that fails JSON parsing
        mock_response = MagicMock()
        mock_response.json.side_effect = ValueError("Invalid JSON")
        mock_client.get.return_value = mock_response
        
        service = WorkflowsService(mock_client)
        
        with pytest.raises(ValueError) as exc_info:
            await service.describe("workflow-123")
        
        assert "Invalid JSON" in str(exc_info.value)
    
    @pytest.mark.asyncio
    async def test_describe_workflow_missing_response_fields(self, mock_client):
        """Test behavior when API response is missing expected fields"""
        # Setup mock response missing 'total' field
        mock_response = MagicMock()
        mock_response.json.return_value = {"items": [{"_id": "workflow-123"}]}
        mock_client.get.return_value = mock_response
        
        service = WorkflowsService(mock_client)
        
        with pytest.raises(KeyError):
            await service.describe("workflow-123")
    
    @pytest.mark.asyncio
    async def test_describe_workflow_malformed_items_array(self, mock_client):
        """Test behavior when items array is malformed"""
        # Setup mock response with null items
        mock_response = MagicMock()
        mock_response.json.return_value = {"total": 1, "items": None}
        mock_client.get.return_value = mock_response
        
        service = WorkflowsService(mock_client)
        
        with pytest.raises(TypeError):
            await service.describe("workflow-123")


class TestWorkflowsServiceIntegration:
    """Integration tests for WorkflowsService"""
    
    @pytest.fixture
    def mock_client(self):
        """Create a comprehensive mock AsyncPlatform client"""
        client = AsyncMock(spec=AsyncPlatform)
        client.get = AsyncMock()
        return client
    
    @pytest.mark.asyncio
    async def test_workflows_service_in_service_registry(self, mock_client):
        """Test WorkflowsService in a service registry pattern"""
        from itential_mcp.services import ServiceBase
        
        class ServiceRegistry:
            def __init__(self):
                self.services = {}
            
            def register(self, service: ServiceBase):
                if not isinstance(service, ServiceBase):
                    raise TypeError("Service must inherit from ServiceBase")
                self.services[service.name] = service
            
            def get(self, name: str) -> ServiceBase:
                return self.services.get(name)
        
        registry = ServiceRegistry()
        workflows_service = WorkflowsService(mock_client)
        
        # Register the service
        registry.register(workflows_service)
        
        # Verify registration
        assert registry.get("workflows") is workflows_service
        assert isinstance(registry.get("workflows"), WorkflowsService)
        assert isinstance(registry.get("workflows"), ServiceBase)
    
    @pytest.mark.asyncio
    async def test_workflows_service_with_realistic_api_response(self, mock_client):
        """Test with realistic Itential Platform API response"""
        realistic_response = {
            "total": 1,
            "items": [
                {
                    "_id": "65f1a2b3c4d5e6f7g8h9i0j1",
                    "name": "Device Configuration Workflow",
                    "description": "Automated device configuration workflow for network devices",
                    "type": "automation",
                    "version": "2.1.0",
                    "status": "enabled",
                    "created": "2025-01-15T10:30:00.000Z",
                    "createdBy": "admin@company.com",
                    "lastModified": "2025-01-20T14:22:15.123Z",
                    "lastModifiedBy": "network-engineer@company.com",
                    "tags": ["network", "configuration", "automation"],
                    "project": "network-automation-project",
                    "namespace": "global",
                    "schema": {
                        "type": "object",
                        "properties": {
                            "deviceList": {
                                "type": "array",
                                "description": "List of devices to configure"
                            },
                            "configTemplate": {
                                "type": "string",
                                "description": "Configuration template to apply"
                            },
                            "dryRun": {
                                "type": "boolean",
                                "default": False,
                                "description": "Whether to run in dry-run mode"
                            }
                        },
                        "required": ["deviceList", "configTemplate"]
                    },
                    "tasks": [
                        {
                            "taskId": "start",
                            "name": "Start Workflow",
                            "type": "operation",
                            "app": "WorkflowEngine"
                        },
                        {
                            "taskId": "backup-configs",
                            "name": "Backup Current Configurations",
                            "type": "operation",
                            "app": "ConfigurationManager"
                        },
                        {
                            "taskId": "apply-configs",
                            "name": "Apply New Configurations",
                            "type": "operation",
                            "app": "ConfigurationManager"
                        },
                        {
                            "taskId": "verify-configs",
                            "name": "Verify Configuration Changes",
                            "type": "operation",
                            "app": "ValidationService"
                        }
                    ],
                    "variables": {
                        "timeout": 300,
                        "retryAttempts": 3,
                        "enableLogging": True,
                        "notificationEmail": "network-team@company.com"
                    }
                }
            ]
        }
        
        mock_response = MagicMock()
        mock_response.json.return_value = realistic_response
        mock_client.get.return_value = mock_response
        
        service = WorkflowsService(mock_client)
        result = await service.describe("65f1a2b3c4d5e6f7g8h9i0j1")
        
        # Verify all complex data structures are preserved
        workflow = result
        assert workflow["name"] == "Device Configuration Workflow"
        assert workflow["version"] == "2.1.0"
        assert len(workflow["tags"]) == 3
        assert "network" in workflow["tags"]
        
        # Verify schema structure
        assert workflow["schema"]["type"] == "object"
        assert "deviceList" in workflow["schema"]["properties"]
        assert workflow["schema"]["properties"]["dryRun"]["default"] is False
        
        # Verify tasks array
        assert len(workflow["tasks"]) == 4
        assert workflow["tasks"][0]["taskId"] == "start"
        assert workflow["tasks"][-1]["name"] == "Verify Configuration Changes"
        
        # Verify variables
        assert workflow["variables"]["timeout"] == 300
        assert workflow["variables"]["enableLogging"] is True
    
    def test_workflows_service_multiple_instances_independence(self, mock_client):
        """Test that multiple WorkflowsService instances are independent"""
        service1 = WorkflowsService(mock_client)
        service2 = WorkflowsService(mock_client)
        
        # Verify they are different instances
        assert service1 is not service2
        
        # Verify they share the same client
        assert service1.client is mock_client
        assert service2.client is mock_client
        
        # Verify they have the same name
        assert service1.name == service2.name == "workflows"
        
        # Modify one instance
        service1.custom_attribute = "test"
        
        # Verify the other instance is unaffected
        assert not hasattr(service2, 'custom_attribute')
    
    @pytest.mark.asyncio
    async def test_workflows_service_concurrent_requests(self, mock_client):
        """Test handling of concurrent workflow describe requests"""
        import asyncio
        
        # Setup different mock responses for different workflow IDs
        def mock_get_side_effect(*args, **kwargs):
            workflow_id = kwargs["params"]["equals[_id]"]
            mock_response = MagicMock()
            mock_response.json.return_value = {
                "total": 1,
                "items": [{"_id": workflow_id, "name": f"Workflow {workflow_id}"}]
            }
            return mock_response
        
        mock_client.get.side_effect = mock_get_side_effect
        
        service = WorkflowsService(mock_client)
        
        # Make concurrent requests
        workflow_ids = ["workflow-1", "workflow-2", "workflow-3"]
        tasks = [service.describe(wf_id) for wf_id in workflow_ids]
        
        results = await asyncio.gather(*tasks)
        
        # Verify all requests completed successfully
        assert len(results) == 3
        for i, result in enumerate(results):
            expected_id = workflow_ids[i]
            assert result["_id"] == expected_id
            assert result["name"] == f"Workflow {expected_id}"
        
        # Verify all API calls were made
        assert mock_client.get.call_count == 3


class TestWorkflowsServiceEdgeCases:
    """Test edge cases and boundary conditions"""
    
    @pytest.fixture
    def mock_client(self):
        """Create a mock AsyncPlatform client"""
        return AsyncMock(spec=AsyncPlatform)
    
    @pytest.mark.asyncio
    async def test_describe_with_special_characters_in_id(self, mock_client):
        """Test describe method with special characters in workflow ID"""
        special_id = "workflow@#$%^&*()_+-=[]{}|;:,.<>?/~`"
        
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "total": 1,
            "items": [{"_id": special_id, "name": "Special Workflow"}]
        }
        mock_client.get.return_value = mock_response
        
        service = WorkflowsService(mock_client)
        result = await service.describe(special_id)
        
        # Verify the special ID was handled correctly
        mock_client.get.assert_called_once_with(
            "/automation-studio/workflows",
            params={"equals[_id]": special_id}
        )
        assert result["_id"] == special_id
    
    @pytest.mark.asyncio
    async def test_describe_with_unicode_workflow_id(self, mock_client):
        """Test describe method with Unicode characters in workflow ID"""
        unicode_id = "workflow-测试-🚀-أتمتة"
        
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "total": 1,
            "items": [{"_id": unicode_id, "name": "Unicode Workflow", "description": "测试工作流程"}]
        }
        mock_client.get.return_value = mock_response
        
        service = WorkflowsService(mock_client)
        result = await service.describe(unicode_id)
        
        assert result["_id"] == unicode_id
        assert result["description"] == "测试工作流程"
    
    @pytest.mark.asyncio
    async def test_describe_with_very_long_workflow_id(self, mock_client):
        """Test describe method with very long workflow ID"""
        long_id = "workflow-" + "a" * 1000  # 1000+ character ID
        
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "total": 1,
            "items": [{"_id": long_id, "name": "Long ID Workflow"}]
        }
        mock_client.get.return_value = mock_response
        
        service = WorkflowsService(mock_client)
        result = await service.describe(long_id)
        
        assert result["_id"] == long_id
        assert len(result["_id"]) > 1000
    
    @pytest.mark.asyncio
    async def test_describe_method_signature_compliance(self, mock_client):
        """Test that describe method signature matches ServiceBase contract"""
        service = WorkflowsService(mock_client)
        
        # Test method can be called with positional arguments (as per ServiceBase contract)
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "total": 1,
            "items": [{"_id": "test-workflow", "name": "Test"}]
        }
        mock_client.get.return_value = mock_response
        
        # Should work with positional argument
        result = await service.describe("test-workflow")
        assert result["_id"] == "test-workflow"
        
        # Should also work with keyword argument
        mock_client.get.reset_mock()
        result = await service.describe(workflow_id="test-workflow-2")
        mock_client.get.assert_called_once_with(
            "/automation-studio/workflows",
            params={"equals[_id]": "test-workflow-2"}
        )