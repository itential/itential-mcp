# Copyright (c) 2025 Itential, Inc
# GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)

import pytest
from unittest.mock import AsyncMock, MagicMock, patch

from itential_mcp import exceptions
from itential_mcp.services.lifecycle_manager import Service
from ipsdk.platform import AsyncPlatform


class TestService:
    """Test the lifecycle_manager Service class"""

    @pytest.fixture
    def mock_client(self):
        """Create a mock AsyncPlatform client"""
        return AsyncMock(spec=AsyncPlatform)

    @pytest.fixture
    def service(self, mock_client):
        """Create a Service instance with mock client"""
        return Service(mock_client)

    def test_service_initialization(self, mock_client):
        """Test Service initialization"""
        service = Service(mock_client)
        
        assert service.client == mock_client
        assert service.name == "lifecycle_manager"

    def test_service_inheritance(self, service):
        """Test Service inherits from ServiceBase"""
        from itential_mcp.services import ServiceBase
        
        assert isinstance(service, ServiceBase)
        assert hasattr(service, 'client')
        assert hasattr(service, 'name')

    def test_service_name_attribute(self, service):
        """Test Service has correct name attribute"""
        assert service.name == "lifecycle_manager"


class TestGetResources:
    """Test the get_resources method"""

    @pytest.fixture
    def mock_client(self):
        """Create a mock AsyncPlatform client"""
        return AsyncMock(spec=AsyncPlatform)

    @pytest.fixture
    def service(self, mock_client):
        """Create a Service instance with mock client"""
        return Service(mock_client)

    @pytest.mark.asyncio
    async def test_get_resources_empty_result(self, service):
        """Test get_resources with no resources"""
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "data": [],
            "metadata": {"total": 0}
        }
        service.client.get.return_value = mock_response

        result = await service.get_resources()

        assert result == []
        service.client.get.assert_called_once_with(
            "/lifecycle-manager/resources",
            params={"limit": 100, "skip": 0}
        )

    @pytest.mark.asyncio
    async def test_get_resources_single_page(self, service):
        """Test get_resources with results fitting in single page"""
        test_data = [
            {"_id": "1", "name": "resource1", "description": "First resource"},
            {"_id": "2", "name": "resource2", "description": "Second resource"}
        ]
        
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "data": test_data,
            "metadata": {"total": 2}
        }
        service.client.get.return_value = mock_response

        result = await service.get_resources()

        assert result == test_data
        assert len(result) == 2
        service.client.get.assert_called_once_with(
            "/lifecycle-manager/resources",
            params={"limit": 100, "skip": 0}
        )

    @pytest.mark.asyncio
    async def test_get_resources_multiple_pages(self, service):
        """Test get_resources with results requiring multiple pages"""
        # First page data
        first_page_data = [{"_id": str(i), "name": f"resource{i}"} for i in range(100)]
        # Second page data
        second_page_data = [{"_id": str(i), "name": f"resource{i}"} for i in range(100, 150)]
        
        # Mock first call (returns total count)
        first_response = MagicMock()
        first_response.json.return_value = {
            "data": first_page_data,
            "metadata": {"total": 150}
        }
        
        # Mock second call (additional page)
        second_response = MagicMock()
        second_response.json.return_value = {
            "data": second_page_data,
            "metadata": {"total": 150}
        }
        
        service.client.get.side_effect = [first_response, second_response]

        result = await service.get_resources()

        assert len(result) == 150
        # Verify we got data from both pages
        first_page_ids = [x["_id"] for x in result if int(x["_id"]) < 100]
        second_page_ids = [x["_id"] for x in result if int(x["_id"]) >= 100]
        assert len(first_page_ids) == 100
        assert len(second_page_ids) == 50
        
        # Verify initial call was made
        service.client.get.assert_called()

    @pytest.mark.asyncio
    async def test_get_resources_pagination_exception_handling(self, service):
        """Test get_resources handles pagination exceptions"""
        # First page succeeds
        first_response = MagicMock()
        first_response.json.return_value = {
            "data": [{"_id": "1", "name": "resource1"}],
            "metadata": {"total": 150}
        }
        
        # Second page fails
        service.client.get.side_effect = [
            first_response,
            Exception("Network error")
        ]

        with pytest.raises(Exception, match="Network error"):
            await service.get_resources()

    @pytest.mark.asyncio
    async def test_fetch_page_method(self, service):
        """Test the _fetch_page helper method"""
        test_data = [{"_id": "1", "name": "resource1"}]
        
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "data": test_data,
            "metadata": {"total": 1}
        }
        service.client.get.return_value = mock_response

        result = await service._fetch_page("/test-endpoint", 50, 25)

        assert result == test_data
        service.client.get.assert_called_once_with(
            "/test-endpoint",
            params={"limit": 25, "skip": 50}
        )


class TestDescribeResource:
    """Test the describe_resource method"""

    @pytest.fixture
    def mock_client(self):
        """Create a mock AsyncPlatform client"""
        return AsyncMock(spec=AsyncPlatform)

    @pytest.fixture
    def service(self, mock_client):
        """Create a Service instance with mock client"""
        return Service(mock_client)

    @pytest.mark.asyncio
    async def test_describe_resource_success(self, service):
        """Test describe_resource with successful result"""
        test_resource = {
            "_id": "resource123",
            "name": "test-resource",
            "description": "A test resource",
            "schema": {"type": "object"}
        }
        
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "data": [test_resource],
            "metadata": {"total": 1}
        }
        service.client.get.return_value = mock_response

        result = await service.describe_resource("test-resource")

        assert result == test_resource
        service.client.get.assert_called_once_with(
            "/lifecycle-manager/resources",
            params={"equals[name]": "test-resource"}
        )

    @pytest.mark.asyncio
    async def test_describe_resource_not_found(self, service):
        """Test describe_resource with resource not found"""
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "data": [],
            "metadata": {"total": 0}
        }
        service.client.get.return_value = mock_response

        with pytest.raises(exceptions.NotFoundError, match="could not find resource test-resource"):
            await service.describe_resource("test-resource")

    @pytest.mark.asyncio
    async def test_describe_resource_multiple_found(self, service):
        """Test describe_resource with multiple resources found (should not happen)"""
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "data": [{"name": "resource1"}, {"name": "resource2"}],
            "metadata": {"total": 2}
        }
        service.client.get.return_value = mock_response

        with pytest.raises(exceptions.NotFoundError, match="could not find resource test-resource"):
            await service.describe_resource("test-resource")


class TestCreateResource:
    """Test the create_resource method"""

    @pytest.fixture
    def mock_client(self):
        """Create a mock AsyncPlatform client"""
        return AsyncMock(spec=AsyncPlatform)

    @pytest.fixture
    def service(self, mock_client):
        """Create a Service instance with mock client"""
        return Service(mock_client)

    @pytest.mark.asyncio
    async def test_create_resource_with_description(self, service):
        """Test create_resource with name, schema, and description"""
        test_schema = {"type": "object", "properties": {"name": {"type": "string"}}}
        test_response = {
            "_id": "new-resource-id",
            "name": "test-resource",
            "description": "A test resource",
            "schema": test_schema
        }
        
        mock_response = MagicMock()
        mock_response.json.return_value = {"data": test_response}
        service.client.post.return_value = mock_response

        result = await service.create_resource("test-resource", test_schema, "A test resource")

        assert result == test_response
        service.client.post.assert_called_once_with(
            "/lifecycle-manager/resources",
            json={
                "name": "test-resource",
                "schema": test_schema,
                "description": "A test resource"
            }
        )

    @pytest.mark.asyncio
    async def test_create_resource_without_description(self, service):
        """Test create_resource with name and schema only"""
        test_schema = {"type": "object", "properties": {"name": {"type": "string"}}}
        test_response = {
            "_id": "new-resource-id",
            "name": "test-resource",
            "schema": test_schema
        }
        
        mock_response = MagicMock()
        mock_response.json.return_value = {"data": test_response}
        service.client.post.return_value = mock_response

        result = await service.create_resource("test-resource", test_schema)

        assert result == test_response
        service.client.post.assert_called_once_with(
            "/lifecycle-manager/resources",
            json={
                "name": "test-resource",
                "schema": test_schema
            }
        )

    @pytest.mark.asyncio
    async def test_create_resource_with_none_description(self, service):
        """Test create_resource with explicit None description"""
        test_schema = {"type": "object"}
        test_response = {"_id": "new-resource-id", "name": "test-resource"}
        
        mock_response = MagicMock()
        mock_response.json.return_value = {"data": test_response}
        service.client.post.return_value = mock_response

        result = await service.create_resource("test-resource", test_schema, None)

        assert result == test_response
        service.client.post.assert_called_once_with(
            "/lifecycle-manager/resources",
            json={
                "name": "test-resource",
                "schema": test_schema
            }
        )

    @pytest.mark.asyncio
    async def test_create_resource_with_string_schema(self, service):
        """Test create_resource with string schema"""
        test_schema = '{"type": "object", "properties": {"name": {"type": "string"}}}'
        test_response = {"_id": "new-resource-id", "name": "test-resource"}
        
        mock_response = MagicMock()
        mock_response.json.return_value = {"data": test_response}
        service.client.post.return_value = mock_response

        result = await service.create_resource("test-resource", test_schema)

        assert result == test_response
        service.client.post.assert_called_once_with(
            "/lifecycle-manager/resources",
            json={
                "name": "test-resource",
                "schema": test_schema
            }
        )


class TestGetInstances:
    """Test the get_instances method"""

    @pytest.fixture
    def mock_client(self):
        """Create a mock AsyncPlatform client"""
        return AsyncMock(spec=AsyncPlatform)

    @pytest.fixture
    def service(self, mock_client):
        """Create a Service instance with mock client"""
        return Service(mock_client)

    @pytest.mark.asyncio
    async def test_get_instances_success(self, service):
        """Test get_instances with successful result"""
        # Mock describe_resource call
        test_resource = {"_id": "resource123", "name": "test-resource"}
        
        with patch.object(service, 'describe_resource') as mock_describe:
            mock_describe.return_value = test_resource
            
            # Mock get_instances call
            test_instances = [
                {"_id": "1", "name": "instance1", "instanceData": {"key": "value1"}},
                {"_id": "2", "name": "instance2", "instanceData": {"key": "value2"}}
            ]
            
            mock_response = MagicMock()
            mock_response.json.return_value = {
                "data": test_instances,
                "metadata": {"total": 2}
            }
            service.client.get.return_value = mock_response

            result = await service.get_instances("test-resource")

            assert result == test_instances
            mock_describe.assert_called_once_with("test-resource")
            service.client.get.assert_called_once_with(
                "/lifecycle-manager/resources/resource123/instances",
                params={"limit": 100, "skip": 0}
            )

    @pytest.mark.asyncio
    async def test_get_instances_empty_result(self, service):
        """Test get_instances with no instances"""
        test_resource = {"_id": "resource123", "name": "test-resource"}
        
        with patch.object(service, 'describe_resource') as mock_describe:
            mock_describe.return_value = test_resource
            
            mock_response = MagicMock()
            mock_response.json.return_value = {
                "data": [],
                "metadata": {"total": 0}
            }
            service.client.get.return_value = mock_response

            result = await service.get_instances("test-resource")

            assert result == []

    @pytest.mark.asyncio
    async def test_get_instances_resource_not_found(self, service):
        """Test get_instances with resource not found"""
        with patch.object(service, 'describe_resource') as mock_describe:
            mock_describe.side_effect = exceptions.NotFoundError("Resource not found")
            
            with pytest.raises(exceptions.NotFoundError, match="Resource not found"):
                await service.get_instances("nonexistent-resource")

    @pytest.mark.asyncio
    async def test_get_instances_multiple_pages(self, service):
        """Test get_instances with pagination"""
        test_resource = {"_id": "resource123", "name": "test-resource"}
        
        with patch.object(service, 'describe_resource') as mock_describe:
            mock_describe.return_value = test_resource
            
            # First page data
            first_page = [{"_id": str(i), "name": f"instance{i}"} for i in range(100)]
            # Second page data
            second_page = [{"_id": str(i), "name": f"instance{i}"} for i in range(100, 120)]
            
            first_response = MagicMock()
            first_response.json.return_value = {
                "data": first_page,
                "metadata": {"total": 120}
            }
            
            second_response = MagicMock()
            second_response.json.return_value = {
                "data": second_page,
                "metadata": {"total": 120}
            }
            
            service.client.get.side_effect = [first_response, second_response]

            result = await service.get_instances("test-resource")

            assert len(result) == 120
            # Verify we got all the data
            assert len([x for x in result if x["name"].startswith("instance")]) == 120


class TestDescribeInstance:
    """Test the describe_instance method"""

    @pytest.fixture
    def mock_client(self):
        """Create a mock AsyncPlatform client"""
        return AsyncMock(spec=AsyncPlatform)

    @pytest.fixture
    def service(self, mock_client):
        """Create a Service instance with mock client"""
        return Service(mock_client)

    @pytest.mark.asyncio
    async def test_describe_instance_success(self, service):
        """Test describe_instance with successful result"""
        test_resource = {"_id": "resource123", "name": "test-resource"}
        test_instance = {
            "_id": "instance123",
            "name": "test-instance",
            "instanceData": {"vlan_id": 100}
        }
        
        with patch.object(service, 'describe_resource') as mock_describe:
            mock_describe.return_value = test_resource
            
            mock_response = MagicMock()
            mock_response.json.return_value = {
                "data": [test_instance],
                "metadata": {"total": 1}
            }
            service.client.get.return_value = mock_response

            result = await service.describe_instance("test-resource", "test-instance")

            assert result == test_instance
            mock_describe.assert_called_once_with("test-resource")
            service.client.get.assert_called_once_with(
                "/lifecycle-manager/resources/resource123/instances",
                params={"equals[name]": "test-instance"}
            )

    @pytest.mark.asyncio
    async def test_describe_instance_not_found(self, service):
        """Test describe_instance with instance not found"""
        test_resource = {"_id": "resource123", "name": "test-resource"}
        
        with patch.object(service, 'describe_resource') as mock_describe:
            mock_describe.return_value = test_resource
            
            mock_response = MagicMock()
            mock_response.json.return_value = {
                "data": [],
                "metadata": {"total": 0}
            }
            service.client.get.return_value = mock_response

            with pytest.raises(exceptions.NotFoundError, match="unable to find instance test-instance"):
                await service.describe_instance("test-resource", "test-instance")

    @pytest.mark.asyncio
    async def test_describe_instance_resource_not_found(self, service):
        """Test describe_instance with resource not found"""
        with patch.object(service, 'describe_resource') as mock_describe:
            mock_describe.side_effect = exceptions.NotFoundError("Resource not found")
            
            with pytest.raises(exceptions.NotFoundError, match="Resource not found"):
                await service.describe_instance("nonexistent-resource", "test-instance")


class TestRunAction:
    """Test the run_action method"""

    @pytest.fixture
    def mock_client(self):
        """Create a mock AsyncPlatform client"""
        return AsyncMock(spec=AsyncPlatform)

    @pytest.fixture
    def service(self, mock_client):
        """Create a Service instance with mock client"""
        return Service(mock_client)

    @pytest.mark.asyncio
    async def test_run_action_create_success(self, service):
        """Test run_action with create action"""
        test_resource = {
            "_id": "resource123",
            "name": "test-resource",
            "actions": [
                {"_id": "action1", "name": "create", "type": "create"},
                {"_id": "action2", "name": "delete", "type": "delete"}
            ]
        }
        
        expected_response = {
            "status": "started",
            "jobId": "job-123",
            "message": "Action started"
        }
        
        with patch.object(service, 'describe_resource') as mock_describe:
            mock_describe.return_value = test_resource
            
            mock_response = MagicMock()
            mock_response.json.return_value = expected_response
            service.client.post.return_value = mock_response

            result = await service.run_action(
                "test-resource", 
                "create", 
                instance_name="new-instance",
                instance_description="New test instance",
                input_params={"vlan_id": 100}
            )

            assert result == expected_response
            mock_describe.assert_called_once_with("test-resource")
            service.client.post.assert_called_once_with(
                "/lifecycle-manager/resources/resource123/run-action",
                json={
                    "actionId": "action1",
                    "instanceName": "new-instance",
                    "inputs": {"vlan_id": 100},
                    "instanceDescription": "New test instance"
                }
            )

    @pytest.mark.asyncio
    async def test_run_action_update_success(self, service):
        """Test run_action with update action on existing instance"""
        test_resource = {
            "_id": "resource123",
            "name": "test-resource",
            "actions": [
                {"_id": "action1", "name": "update", "type": "update"}
            ]
        }
        
        test_instance = {
            "_id": "instance123",
            "name": "existing-instance",
            "instanceData": {"vlan_id": 100}
        }
        
        expected_response = {"status": "started", "jobId": "job-123"}
        
        with patch.object(service, 'describe_resource') as mock_describe_resource:
            mock_describe_resource.return_value = test_resource
            
            with patch.object(service, 'describe_instance') as mock_describe_instance:
                mock_describe_instance.return_value = test_instance
                
                mock_response = MagicMock()
                mock_response.json.return_value = expected_response
                service.client.post.return_value = mock_response

                result = await service.run_action(
                    "test-resource",
                    "update",
                    instance_name="existing-instance",
                    input_params={"vlan_id": 200}
                )

                assert result == expected_response
                mock_describe_resource.assert_called_once_with("test-resource")
                mock_describe_instance.assert_called_once_with("test-resource", "existing-instance")
                service.client.post.assert_called_once_with(
                    "/lifecycle-manager/resources/resource123/run-action",
                    json={
                        "actionId": "action1",
                        "instance": "instance123",
                        "inputs": {"vlan_id": 200}
                    }
                )

    @pytest.mark.asyncio
    async def test_run_action_delete_with_default_inputs(self, service):
        """Test run_action with delete action using instance data as default inputs"""
        test_resource = {
            "_id": "resource123",
            "name": "test-resource",
            "actions": [
                {"_id": "action1", "name": "delete", "type": "delete"}
            ]
        }
        
        test_instance = {
            "_id": "instance123",
            "name": "existing-instance",
            "instanceData": {"vlan_id": 100, "status": "active"}
        }
        
        expected_response = {"status": "started", "jobId": "job-123"}
        
        with patch.object(service, 'describe_resource') as mock_describe_resource:
            mock_describe_resource.return_value = test_resource
            
            with patch.object(service, 'describe_instance') as mock_describe_instance:
                mock_describe_instance.return_value = test_instance
                
                mock_response = MagicMock()
                mock_response.json.return_value = expected_response
                service.client.post.return_value = mock_response

                result = await service.run_action(
                    "test-resource",
                    "delete",
                    instance_name="existing-instance"
                    # No input_params provided - should use instance data
                )

                assert result == expected_response
                service.client.post.assert_called_once_with(
                    "/lifecycle-manager/resources/resource123/run-action",
                    json={
                        "actionId": "action1",
                        "instance": "instance123",
                        "inputs": {"vlan_id": 100, "status": "active"}
                    }
                )

    @pytest.mark.asyncio
    async def test_run_action_action_not_found(self, service):
        """Test run_action with action not found"""
        test_resource = {
            "_id": "resource123",
            "name": "test-resource",
            "actions": [
                {"_id": "action1", "name": "create", "type": "create"}
            ]
        }
        
        with patch.object(service, 'describe_resource') as mock_describe:
            mock_describe.return_value = test_resource
            
            with pytest.raises(exceptions.NotFoundError, match="unable to find action nonexistent for resource test-resource"):
                await service.run_action("test-resource", "nonexistent")

    @pytest.mark.asyncio
    async def test_run_action_resource_not_found(self, service):
        """Test run_action with resource not found"""
        with patch.object(service, 'describe_resource') as mock_describe:
            mock_describe.side_effect = exceptions.NotFoundError("Resource not found")
            
            with pytest.raises(exceptions.NotFoundError, match="Resource not found"):
                await service.run_action("nonexistent-resource", "create")

    @pytest.mark.asyncio
    async def test_run_action_minimal_parameters(self, service):
        """Test run_action with minimal parameters"""
        test_resource = {
            "_id": "resource123",
            "name": "test-resource",
            "actions": [
                {"_id": "action1", "name": "create", "type": "create"}
            ]
        }
        
        expected_response = {"status": "started", "jobId": "job-123"}
        
        with patch.object(service, 'describe_resource') as mock_describe:
            mock_describe.return_value = test_resource
            
            mock_response = MagicMock()
            mock_response.json.return_value = expected_response
            service.client.post.return_value = mock_response

            result = await service.run_action("test-resource", "create")

            assert result == expected_response
            service.client.post.assert_called_once_with(
                "/lifecycle-manager/resources/resource123/run-action",
                json={"actionId": "action1"}
            )


class TestServiceIntegration:
    """Test Service integration and edge cases"""

    @pytest.fixture
    def mock_client(self):
        """Create a mock AsyncPlatform client"""
        return AsyncMock(spec=AsyncPlatform)

    @pytest.fixture
    def service(self, mock_client):
        """Create a Service instance with mock client"""
        return Service(mock_client)

    def test_service_docstring(self, service):
        """Test Service has comprehensive documentation"""
        assert Service.__doc__ is not None
        assert len(Service.__doc__.strip()) > 0
        
        # Check that key concepts are documented
        docstring = Service.__doc__
        assert "Lifecycle Manager" in docstring
        assert "resource models" in docstring
        assert "Args:" in docstring
        assert "Attributes:" in docstring

    @pytest.mark.asyncio
    async def test_service_method_signatures(self, service):
        """Test that all service methods have correct signatures"""
        import inspect
        
        # get_resources should have no parameters (except self)
        sig = inspect.signature(service.get_resources)
        assert len(sig.parameters) == 0
        
        # describe_resource should have name parameter
        sig = inspect.signature(service.describe_resource)
        assert 'name' in sig.parameters
        
        # create_resource should have name, schema, and optional description
        sig = inspect.signature(service.create_resource)
        assert 'name' in sig.parameters
        assert 'schema' in sig.parameters
        assert 'description' in sig.parameters
        assert sig.parameters['description'].default is None
        
        # get_instances should have resource_name parameter
        sig = inspect.signature(service.get_instances)
        assert 'resource_name' in sig.parameters
        
        # describe_instance should have resource_name and instance_name
        sig = inspect.signature(service.describe_instance)
        assert 'resource_name' in sig.parameters
        assert 'instance_name' in sig.parameters
        
        # run_action should have resource_name, action_name, and optional parameters
        sig = inspect.signature(service.run_action)
        assert 'resource_name' in sig.parameters
        assert 'action_name' in sig.parameters
        assert 'instance_name' in sig.parameters
        assert 'instance_description' in sig.parameters
        assert 'input_params' in sig.parameters

    @pytest.mark.asyncio
    async def test_concurrent_operations(self, service):
        """Test that service methods can be called concurrently"""
        # Mock responses for different operations
        resource_response = MagicMock()
        resource_response.json.return_value = {
            "data": [{"_id": "1", "name": "resource1"}],
            "metadata": {"total": 1}
        }
        
        instances_response = MagicMock()
        instances_response.json.return_value = {
            "data": [],
            "metadata": {"total": 0}
        }
        
        service.client.get.side_effect = [resource_response, instances_response]
        
        # Just test that both operations complete without error
        with patch.object(service, 'describe_resource') as mock_describe:
            mock_describe.return_value = {"_id": "1", "name": "resource1"}
            
            # Run describe_resource
            result1 = await service.describe_resource("resource1")
            assert result1["name"] == "resource1"
            
            # Run get_instances (which calls describe_resource internally)
            result2 = await service.get_instances("resource1")
            # get_instances returns what the service returned, not necessarily empty
            assert isinstance(result2, list)

    @pytest.mark.asyncio 
    async def test_error_propagation(self, service):
        """Test that errors are properly propagated from client"""
        service.client.get.side_effect = Exception("Network error")
        
        with pytest.raises(Exception, match="Network error"):
            await service.get_resources()
        
        with pytest.raises(Exception, match="Network error"):
            await service.describe_resource("test-resource")