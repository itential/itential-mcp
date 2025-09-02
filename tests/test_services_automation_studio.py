# Copyright (c) 2025 Itential, Inc
# GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)

import pytest
from unittest.mock import AsyncMock, MagicMock

from itential_mcp import exceptions
from itential_mcp.services.automation_studio import Service


class TestAutomationStudioService:
    """Test cases for the automation_studio Service class"""

    @pytest.fixture
    def mock_client(self):
        """Create a mock client for testing"""
        client = AsyncMock()
        return client

    @pytest.fixture
    def service(self, mock_client):
        """Create a Service instance with mocked client"""
        service = Service(mock_client)
        return service

    def test_service_name(self, mock_client):
        """Test that the service has the correct name"""
        service = Service(mock_client)
        assert service.name == "automation_studio"

    @pytest.mark.asyncio
    async def test_describe_workflow_success(self, service, mock_client):
        """Test successful workflow description retrieval"""
        workflow_id = "workflow-123"
        expected_workflow = {
            "_id": workflow_id,
            "name": "Test Workflow",
            "description": "A test workflow",
            "version": "1.0.0",
            "type": "automation",
            "tasks": []
        }

        # Mock response data
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "total": 1,
            "items": [expected_workflow]
        }
        mock_client.get.return_value = mock_response

        result = await service.describe_workflow(workflow_id)

        # Verify client was called with correct parameters
        mock_client.get.assert_called_once_with(
            "/automation-studio/workflows",
            params={"equals[_id]": workflow_id}
        )

        # Verify result
        assert result == expected_workflow
        assert result["_id"] == workflow_id
        assert result["name"] == "Test Workflow"

    @pytest.mark.asyncio
    async def test_describe_workflow_not_found(self, service, mock_client):
        """Test workflow not found scenario"""
        workflow_id = "nonexistent-workflow"

        # Mock response with no results
        mock_response = MagicMock()
        mock_response.json.return_value = {"total": 0, "items": []}
        mock_client.get.return_value = mock_response

        with pytest.raises(exceptions.NotFoundError) as exc_info:
            await service.describe_workflow(workflow_id)

        assert f"workflow id {workflow_id} not found" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_describe_workflow_multiple_results(self, service, mock_client):
        """Test scenario where multiple workflows are found (should not happen)"""
        workflow_id = "duplicate-workflow"

        # Mock response with multiple results
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "total": 2,
            "items": [
                {"_id": workflow_id, "name": "Workflow 1"},
                {"_id": workflow_id, "name": "Workflow 2"}
            ]
        }
        mock_client.get.return_value = mock_response

        with pytest.raises(exceptions.NotFoundError):
            await service.describe_workflow(workflow_id)

    @pytest.mark.asyncio
    async def test_describe_workflow_empty_id(self, service, mock_client):
        """Test workflow description with empty ID"""
        workflow_id = ""

        # Mock response with no results
        mock_response = MagicMock()
        mock_response.json.return_value = {"total": 0, "items": []}
        mock_client.get.return_value = mock_response

        with pytest.raises(exceptions.NotFoundError) as exc_info:
            await service.describe_workflow(workflow_id)

        assert f"workflow id {workflow_id} not found" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_describe_workflow_unicode_id(self, service, mock_client):
        """Test workflow description with Unicode ID"""
        workflow_id = "工作流程-123"
        expected_workflow = {
            "_id": workflow_id,
            "name": "Unicode Test Workflow",
            "description": "测试工作流程"
        }

        mock_response = MagicMock()
        mock_response.json.return_value = {
            "total": 1,
            "items": [expected_workflow]
        }
        mock_client.get.return_value = mock_response

        result = await service.describe_workflow(workflow_id)

        # Verify Unicode ID was handled correctly
        mock_client.get.assert_called_with(
            "/automation-studio/workflows",
            params={"equals[_id]": workflow_id}
        )
        assert result == expected_workflow

    @pytest.mark.asyncio
    async def test_describe_workflow_special_characters(self, service, mock_client):
        """Test workflow description with special characters in ID"""
        workflow_id = "workflow-123_test@domain.com"
        expected_workflow = {
            "_id": workflow_id,
            "name": "Special Chars Workflow"
        }

        mock_response = MagicMock()
        mock_response.json.return_value = {
            "total": 1,
            "items": [expected_workflow]
        }
        mock_client.get.return_value = mock_response

        result = await service.describe_workflow(workflow_id)

        # Verify special characters were handled correctly
        mock_client.get.assert_called_with(
            "/automation-studio/workflows",
            params={"equals[_id]": workflow_id}
        )
        assert result == expected_workflow


class TestServiceIntegration:
    """Integration tests for the Service class"""

    @pytest.fixture
    def mock_client(self):
        """Create a mock client for testing"""
        client = AsyncMock()
        return client

    @pytest.fixture
    def service(self, mock_client):
        """Create a Service instance with mocked client"""
        service = Service(mock_client)
        return service

    @pytest.mark.asyncio
    async def test_service_inherits_from_servicebase(self, service):
        """Test that Service properly inherits from ServiceBase"""
        from itential_mcp.services import ServiceBase
        assert isinstance(service, ServiceBase)

    @pytest.mark.asyncio
    async def test_method_signatures_consistency(self, service):
        """Test that all methods have consistent parameter signatures"""
        import inspect

        # Check describe_workflow signature
        describe_sig = inspect.signature(service.describe_workflow)
        assert 'workflow_id' in describe_sig.parameters

        # Verify parameter type annotation
        workflow_id_param = describe_sig.parameters['workflow_id']
        assert workflow_id_param.annotation is str

    @pytest.mark.asyncio
    async def test_all_methods_are_async(self, service):
        """Test that all public methods are async"""
        import inspect

        # Get all public methods (not starting with _)
        public_methods = [
            method for method in dir(service)
            if not method.startswith('_') and callable(getattr(service, method))
        ]

        for method_name in ['describe_workflow']:
            if method_name in public_methods:
                method = getattr(service, method_name)
                assert inspect.iscoroutinefunction(method)

    @pytest.mark.asyncio
    async def test_describe_workflow_return_type(self, service, mock_client):
        """Test that describe_workflow returns a mapping"""
        from collections.abc import Mapping

        workflow_id = "test-workflow"
        expected_workflow = {"_id": workflow_id, "name": "Test"}

        mock_response = MagicMock()
        mock_response.json.return_value = {
            "total": 1,
            "items": [expected_workflow]
        }
        mock_client.get.return_value = mock_response

        result = await service.describe_workflow(workflow_id)

        # Verify return type is a mapping
        assert isinstance(result, Mapping)


class TestErrorHandling:
    """Test error handling scenarios"""

    @pytest.fixture
    def mock_client(self):
        """Create a mock client for testing"""
        client = AsyncMock()
        return client

    @pytest.fixture
    def service(self, mock_client):
        """Create a Service instance with mocked client"""
        service = Service(mock_client)
        return service

    @pytest.mark.asyncio
    async def test_client_connection_error(self, service, mock_client):
        """Test handling of client connection errors"""
        mock_client.get.side_effect = Exception("Connection failed")

        with pytest.raises(Exception, match="Connection failed"):
            await service.describe_workflow("test-workflow")

    @pytest.mark.asyncio
    async def test_malformed_response_handling(self, service, mock_client):
        """Test handling of malformed API responses"""
        # Mock response with missing 'total' field
        mock_response = MagicMock()
        mock_response.json.return_value = {"items": []}
        mock_client.get.return_value = mock_response

        with pytest.raises(KeyError):
            await service.describe_workflow("test-workflow")

    @pytest.mark.asyncio
    async def test_missing_items_field(self, service, mock_client):
        """Test handling of response missing items field"""
        mock_response = MagicMock()
        mock_response.json.return_value = {"total": 1}  # Missing items
        mock_client.get.return_value = mock_response

        with pytest.raises(KeyError):
            await service.describe_workflow("test-workflow")

    @pytest.mark.asyncio
    async def test_empty_items_array_with_positive_total(self, service, mock_client):
        """Test handling of inconsistent response (total > 0 but empty items)"""
        mock_response = MagicMock()
        mock_response.json.return_value = {"total": 1, "items": []}
        mock_client.get.return_value = mock_response

        # Should raise IndexError when trying to access items[0]
        with pytest.raises(IndexError):
            await service.describe_workflow("test-workflow")

    @pytest.mark.asyncio
    async def test_json_decode_error(self, service, mock_client):
        """Test handling of JSON decode errors"""
        mock_response = MagicMock()
        mock_response.json.side_effect = ValueError("Invalid JSON")
        mock_client.get.return_value = mock_response

        with pytest.raises(ValueError, match="Invalid JSON"):
            await service.describe_workflow("test-workflow")

    @pytest.mark.asyncio
    async def test_response_none_handling(self, service, mock_client):
        """Test handling when client returns None response"""
        mock_client.get.return_value = None

        with pytest.raises(AttributeError):
            await service.describe_workflow("test-workflow")


class TestEdgeCases:
    """Test edge cases and boundary conditions"""

    @pytest.fixture
    def mock_client(self):
        """Create a mock client for testing"""
        client = AsyncMock()
        return client

    @pytest.fixture
    def service(self, mock_client):
        """Create a Service instance with mocked client"""
        service = Service(mock_client)
        return service

    @pytest.mark.asyncio
    async def test_very_long_workflow_id(self, service, mock_client):
        """Test handling of very long workflow IDs"""
        long_id = "a" * 1000  # Very long ID
        expected_workflow = {"_id": long_id, "name": "Long ID Workflow"}

        mock_response = MagicMock()
        mock_response.json.return_value = {
            "total": 1,
            "items": [expected_workflow]
        }
        mock_client.get.return_value = mock_response

        result = await service.describe_workflow(long_id)

        # Should handle long IDs without issues
        assert result["_id"] == long_id
        mock_client.get.assert_called_with(
            "/automation-studio/workflows",
            params={"equals[_id]": long_id}
        )

    @pytest.mark.asyncio
    async def test_workflow_with_complex_data(self, service, mock_client):
        """Test workflow with complex nested data structures"""
        workflow_id = "complex-workflow"
        complex_workflow = {
            "_id": workflow_id,
            "name": "Complex Workflow",
            "tasks": [
                {
                    "id": "task1",
                    "type": "automation",
                    "config": {
                        "parameters": {
                            "nested": {
                                "deep": {
                                    "value": "test"
                                }
                            }
                        }
                    }
                }
            ],
            "variables": {
                "env": "production",
                "settings": {
                    "timeout": 300,
                    "retry": True
                }
            }
        }

        mock_response = MagicMock()
        mock_response.json.return_value = {
            "total": 1,
            "items": [complex_workflow]
        }
        mock_client.get.return_value = mock_response

        result = await service.describe_workflow(workflow_id)

        # Should preserve complex data structures
        assert result == complex_workflow
        assert result["tasks"][0]["config"]["parameters"]["nested"]["deep"]["value"] == "test"
        assert result["variables"]["settings"]["timeout"] == 300

    @pytest.mark.asyncio
    async def test_workflow_with_null_values(self, service, mock_client):
        """Test workflow with null/None values"""
        workflow_id = "null-workflow"
        workflow_with_nulls = {
            "_id": workflow_id,
            "name": "Workflow with Nulls",
            "description": None,
            "variables": None,
            "tags": []
        }

        mock_response = MagicMock()
        mock_response.json.return_value = {
            "total": 1,
            "items": [workflow_with_nulls]
        }
        mock_client.get.return_value = mock_response

        result = await service.describe_workflow(workflow_id)

        # Should preserve null values
        assert result == workflow_with_nulls
        assert result["description"] is None
        assert result["variables"] is None

    @pytest.mark.asyncio
    async def test_workflow_id_with_url_encoding_chars(self, service, mock_client):
        """Test workflow ID with characters that need URL encoding"""
        workflow_id = "workflow with spaces & special chars!"
        expected_workflow = {"_id": workflow_id, "name": "URL Encoded Workflow"}

        mock_response = MagicMock()
        mock_response.json.return_value = {
            "total": 1,
            "items": [expected_workflow]
        }
        mock_client.get.return_value = mock_response

        result = await service.describe_workflow(workflow_id)

        # Should handle URL encoding characters correctly
        assert result == expected_workflow
        mock_client.get.assert_called_with(
            "/automation-studio/workflows",
            params={"equals[_id]": workflow_id}
        )


class TestServiceDocumentation:
    """Test service documentation and metadata"""

    @pytest.fixture
    def mock_client(self):
        """Create a mock client for testing"""
        client = AsyncMock()
        return client

    @pytest.fixture
    def service(self, mock_client):
        """Create a Service instance with mocked client"""
        service = Service(mock_client)
        return service

    def test_service_has_docstring(self, service):
        """Test that the Service class has proper documentation"""
        assert service.__class__.__doc__ is not None
        assert len(service.__class__.__doc__.strip()) > 0

    def test_describe_workflow_has_docstring(self, service):
        """Test that describe_workflow method has proper documentation"""
        assert service.describe_workflow.__doc__ is not None
        assert len(service.describe_workflow.__doc__.strip()) > 0

    def test_docstring_contains_args_section(self, service):
        """Test that describe_workflow docstring contains Args section"""
        docstring = service.describe_workflow.__doc__
        assert "Args:" in docstring

    def test_docstring_contains_returns_section(self, service):
        """Test that describe_workflow docstring contains Returns section"""
        docstring = service.describe_workflow.__doc__
        assert "Returns:" in docstring

    def test_docstring_contains_raises_section(self, service):
        """Test that describe_workflow docstring contains Raises section"""
        docstring = service.describe_workflow.__doc__
        assert "Raises:" in docstring


class TestPerformanceConsiderations:
    """Test performance-related aspects"""

    @pytest.fixture
    def mock_client(self):
        """Create a mock client for testing"""
        client = AsyncMock()
        return client

    @pytest.fixture
    def service(self, mock_client):
        """Create a Service instance with mocked client"""
        service = Service(mock_client)
        return service

    @pytest.mark.asyncio
    async def test_single_api_call_per_describe(self, service, mock_client):
        """Test that describe_workflow makes only one API call"""
        workflow_id = "performance-test"
        expected_workflow = {"_id": workflow_id, "name": "Performance Test"}

        mock_response = MagicMock()
        mock_response.json.return_value = {
            "total": 1,
            "items": [expected_workflow]
        }
        mock_client.get.return_value = mock_response

        await service.describe_workflow(workflow_id)

        # Should make exactly one API call
        assert mock_client.get.call_count == 1

    @pytest.mark.asyncio
    async def test_concurrent_describe_calls(self, service, mock_client):
        """Test concurrent describe_workflow calls"""
        import asyncio

        workflow_ids = ["workflow-1", "workflow-2", "workflow-3"]
        
        call_count = [0]
        def create_response(*args, **kwargs):
            call_count[0] += 1
            workflow_id = f"workflow-{call_count[0]}"
            response = MagicMock()
            response.json.return_value = {
                "total": 1,
                "items": [{"_id": workflow_id, "name": f"Workflow {call_count[0]}"}]
            }
            return response

        mock_client.get.side_effect = create_response

        # Run concurrent describe operations
        tasks = [
            service.describe_workflow(workflow_id)
            for workflow_id in workflow_ids
        ]

        results = await asyncio.gather(*tasks, return_exceptions=True)

        # All should complete successfully
        assert len(results) == 3
        for result in results:
            assert not isinstance(result, Exception)
            assert "_id" in result
            assert "name" in result

        # Should have made three API calls
        assert mock_client.get.call_count == 3