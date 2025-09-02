# Copyright (c) 2025 Itential, Inc
# GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)

import pytest
from unittest.mock import AsyncMock, MagicMock

from itential_mcp.services.transformations import Service


class TestTransformationsService:
    """Test cases for the transformations Service class"""

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
        assert service.name == "transformations"

    @pytest.mark.asyncio
    async def test_describe_transformation_success(self, service, mock_client):
        """Test successful transformation description retrieval"""
        transformation_id = "transformation-123"
        expected_transformation = {
            "_id": transformation_id,
            "name": "Test Transformation",
            "description": "A test transformation",
            "version": "1.0.0",
            "type": "JSONtoJSON",
            "input": {"type": "object"},
            "output": {"type": "object"},
            "map": {"field1": "field2"}
        }

        # Mock response data
        mock_response = MagicMock()
        mock_response.json.return_value = expected_transformation
        mock_client.get.return_value = mock_response

        result = await service.describe_transformation(transformation_id)

        # Verify client was called with correct endpoint
        mock_client.get.assert_called_once_with(f"/transformations/{transformation_id}")

        # Verify result
        assert result == expected_transformation
        assert result["_id"] == transformation_id
        assert result["name"] == "Test Transformation"
        assert result["type"] == "JSONtoJSON"

    @pytest.mark.asyncio
    async def test_describe_transformation_client_error(self, service, mock_client):
        """Test transformation description with client error"""
        transformation_id = "test-transformation"
        mock_client.get.side_effect = Exception("API Error")

        with pytest.raises(Exception, match="API Error"):
            await service.describe_transformation(transformation_id)

        mock_client.get.assert_called_once_with(f"/transformations/{transformation_id}")

    @pytest.mark.asyncio
    async def test_describe_transformation_json_error(self, service, mock_client):
        """Test transformation description with JSON decode error"""
        transformation_id = "test-transformation"
        mock_response = MagicMock()
        mock_response.json.side_effect = ValueError("Invalid JSON")
        mock_client.get.return_value = mock_response

        with pytest.raises(ValueError, match="Invalid JSON"):
            await service.describe_transformation(transformation_id)

    @pytest.mark.asyncio
    async def test_describe_transformation_empty_id(self, service, mock_client):
        """Test transformation description with empty ID"""
        transformation_id = ""
        expected_transformation = {"_id": "", "name": "Empty ID Transformation"}

        mock_response = MagicMock()
        mock_response.json.return_value = expected_transformation
        mock_client.get.return_value = mock_response

        result = await service.describe_transformation(transformation_id)

        # Should handle empty ID (endpoint will be /transformations/)
        mock_client.get.assert_called_with("/transformations/")
        assert result == expected_transformation

    @pytest.mark.asyncio
    async def test_describe_transformation_unicode_id(self, service, mock_client):
        """Test transformation description with Unicode ID"""
        transformation_id = "转换-123"
        expected_transformation = {
            "_id": transformation_id,
            "name": "Unicode Test Transformation",
            "description": "测试转换"
        }

        mock_response = MagicMock()
        mock_response.json.return_value = expected_transformation
        mock_client.get.return_value = mock_response

        result = await service.describe_transformation(transformation_id)

        # Verify Unicode ID was handled correctly in URL
        mock_client.get.assert_called_with(f"/transformations/{transformation_id}")
        assert result == expected_transformation

    @pytest.mark.asyncio
    async def test_describe_transformation_special_characters(self, service, mock_client):
        """Test transformation description with special characters in ID"""
        transformation_id = "transformation-123_test@domain.com"
        expected_transformation = {
            "_id": transformation_id,
            "name": "Special Chars Transformation"
        }

        mock_response = MagicMock()
        mock_response.json.return_value = expected_transformation
        mock_client.get.return_value = mock_response

        result = await service.describe_transformation(transformation_id)

        # Verify special characters were handled correctly in URL
        mock_client.get.assert_called_with(f"/transformations/{transformation_id}")
        assert result == expected_transformation

    @pytest.mark.asyncio
    async def test_describe_transformation_with_slashes(self, service, mock_client):
        """Test transformation description with forward slashes in ID"""
        transformation_id = "namespace/transformation-123"
        expected_transformation = {
            "_id": transformation_id,
            "name": "Namespaced Transformation"
        }

        mock_response = MagicMock()
        mock_response.json.return_value = expected_transformation
        mock_client.get.return_value = mock_response

        result = await service.describe_transformation(transformation_id)

        # Should preserve slashes in the URL path
        mock_client.get.assert_called_with(f"/transformations/{transformation_id}")
        assert result == expected_transformation


class TestTransformationTypes:
    """Test different types of transformation responses"""

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
    async def test_describe_jsonjson_transformation(self, service, mock_client):
        """Test JSONtoJSON transformation description"""
        transformation_id = "json-transformation"
        expected_transformation = {
            "_id": transformation_id,
            "name": "JSON to JSON Transformation",
            "type": "JSONtoJSON",
            "input": {"type": "object", "properties": {"input_field": {"type": "string"}}},
            "output": {"type": "object", "properties": {"output_field": {"type": "string"}}},
            "map": {"output_field": "input_field"},
            "hardcodedValues": {},
            "conditional": {}
        }

        mock_response = MagicMock()
        mock_response.json.return_value = expected_transformation
        mock_client.get.return_value = mock_response

        result = await service.describe_transformation(transformation_id)

        assert result["type"] == "JSONtoJSON"
        assert "map" in result
        assert "input" in result
        assert "output" in result

    @pytest.mark.asyncio
    async def test_describe_template_transformation(self, service, mock_client):
        """Test template-based transformation description"""
        transformation_id = "template-transformation"
        expected_transformation = {
            "_id": transformation_id,
            "name": "Template Transformation",
            "type": "template",
            "template": "Hello {{ name }}, your ID is {{ id }}",
            "input": {"type": "object", "properties": {"name": {"type": "string"}, "id": {"type": "string"}}},
            "output": {"type": "string"}
        }

        mock_response = MagicMock()
        mock_response.json.return_value = expected_transformation
        mock_client.get.return_value = mock_response

        result = await service.describe_transformation(transformation_id)

        assert result["type"] == "template"
        assert "template" in result
        assert "Hello {{ name }}" in result["template"]

    @pytest.mark.asyncio
    async def test_describe_javascript_transformation(self, service, mock_client):
        """Test JavaScript-based transformation description"""
        transformation_id = "js-transformation"
        expected_transformation = {
            "_id": transformation_id,
            "name": "JavaScript Transformation",
            "type": "javascript",
            "script": "return input.toUpperCase();",
            "input": {"type": "string"},
            "output": {"type": "string"}
        }

        mock_response = MagicMock()
        mock_response.json.return_value = expected_transformation
        mock_client.get.return_value = mock_response

        result = await service.describe_transformation(transformation_id)

        assert result["type"] == "javascript"
        assert "script" in result
        assert "toUpperCase" in result["script"]


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

        # Check describe_transformation signature
        describe_sig = inspect.signature(service.describe_transformation)
        assert 'transformation_id' in describe_sig.parameters

        # Verify parameter type annotation
        transformation_id_param = describe_sig.parameters['transformation_id']
        assert transformation_id_param.annotation is str

    @pytest.mark.asyncio
    async def test_all_methods_are_async(self, service):
        """Test that all public methods are async"""
        import inspect

        # Get all public methods (not starting with _)
        public_methods = [
            method for method in dir(service)
            if not method.startswith('_') and callable(getattr(service, method))
        ]

        for method_name in ['describe_transformation']:
            if method_name in public_methods:
                method = getattr(service, method_name)
                assert inspect.iscoroutinefunction(method)

    @pytest.mark.asyncio
    async def test_describe_transformation_return_type(self, service, mock_client):
        """Test that describe_transformation returns a mapping"""
        from collections.abc import Mapping

        transformation_id = "test-transformation"
        expected_transformation = {"_id": transformation_id, "name": "Test"}

        mock_response = MagicMock()
        mock_response.json.return_value = expected_transformation
        mock_client.get.return_value = mock_response

        result = await service.describe_transformation(transformation_id)

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
            await service.describe_transformation("test-transformation")

    @pytest.mark.asyncio
    async def test_http_404_error(self, service, mock_client):
        """Test handling of HTTP 404 errors (transformation not found)"""
        http_error = Exception("404 Not Found")
        http_error.status_code = 404
        mock_client.get.side_effect = http_error

        with pytest.raises(Exception):
            await service.describe_transformation("nonexistent-transformation")

    @pytest.mark.asyncio
    async def test_malformed_json_response(self, service, mock_client):
        """Test handling of malformed JSON responses"""
        mock_response = MagicMock()
        mock_response.json.side_effect = ValueError("Invalid JSON")
        mock_client.get.return_value = mock_response

        with pytest.raises(ValueError, match="Invalid JSON"):
            await service.describe_transformation("test-transformation")

    @pytest.mark.asyncio
    async def test_response_none_handling(self, service, mock_client):
        """Test handling when client returns None response"""
        mock_client.get.return_value = None

        with pytest.raises(AttributeError):
            await service.describe_transformation("test-transformation")

    @pytest.mark.asyncio
    async def test_network_timeout_error(self, service, mock_client):
        """Test handling of network timeout errors"""
        import asyncio
        mock_client.get.side_effect = asyncio.TimeoutError("Request timed out")

        with pytest.raises(asyncio.TimeoutError):
            await service.describe_transformation("test-transformation")


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
    async def test_very_long_transformation_id(self, service, mock_client):
        """Test handling of very long transformation IDs"""
        long_id = "a" * 1000  # Very long ID
        expected_transformation = {"_id": long_id, "name": "Long ID Transformation"}

        mock_response = MagicMock()
        mock_response.json.return_value = expected_transformation
        mock_client.get.return_value = mock_response

        result = await service.describe_transformation(long_id)

        # Should handle long IDs without issues
        assert result["_id"] == long_id
        mock_client.get.assert_called_with(f"/transformations/{long_id}")

    @pytest.mark.asyncio
    async def test_transformation_with_complex_data(self, service, mock_client):
        """Test transformation with complex nested data structures"""
        transformation_id = "complex-transformation"
        complex_transformation = {
            "_id": transformation_id,
            "name": "Complex Transformation",
            "type": "JSONtoJSON",
            "input": {
                "type": "object",
                "properties": {
                    "nested": {
                        "type": "object",
                        "properties": {
                            "deep": {
                                "type": "object",
                                "properties": {
                                    "value": {"type": "string"}
                                }
                            }
                        }
                    }
                }
            },
            "map": {
                "output.result": "nested.deep.value"
            },
            "conditionals": [
                {
                    "condition": "nested.deep.value !== null",
                    "map": {"status": "processed"}
                }
            ]
        }

        mock_response = MagicMock()
        mock_response.json.return_value = complex_transformation
        mock_client.get.return_value = mock_response

        result = await service.describe_transformation(transformation_id)

        # Should preserve complex data structures
        assert result == complex_transformation
        assert result["input"]["properties"]["nested"]["properties"]["deep"]["properties"]["value"]["type"] == "string"
        assert result["map"]["output.result"] == "nested.deep.value"

    @pytest.mark.asyncio
    async def test_transformation_with_null_values(self, service, mock_client):
        """Test transformation with null/None values"""
        transformation_id = "null-transformation"
        transformation_with_nulls = {
            "_id": transformation_id,
            "name": "Transformation with Nulls",
            "description": None,
            "template": None,
            "script": None,
            "tags": []
        }

        mock_response = MagicMock()
        mock_response.json.return_value = transformation_with_nulls
        mock_client.get.return_value = mock_response

        result = await service.describe_transformation(transformation_id)

        # Should preserve null values
        assert result == transformation_with_nulls
        assert result["description"] is None
        assert result["template"] is None
        assert result["script"] is None

    @pytest.mark.asyncio
    async def test_transformation_id_with_url_encoding_chars(self, service, mock_client):
        """Test transformation ID with characters that need URL encoding"""
        transformation_id = "transformation with spaces & special chars!"
        expected_transformation = {"_id": transformation_id, "name": "URL Encoded Transformation"}

        mock_response = MagicMock()
        mock_response.json.return_value = expected_transformation
        mock_client.get.return_value = mock_response

        result = await service.describe_transformation(transformation_id)

        # Should handle URL encoding characters correctly
        assert result == expected_transformation
        mock_client.get.assert_called_with(f"/transformations/{transformation_id}")

    @pytest.mark.asyncio
    async def test_empty_transformation_response(self, service, mock_client):
        """Test handling of empty transformation response"""
        transformation_id = "empty-transformation"
        empty_transformation = {}

        mock_response = MagicMock()
        mock_response.json.return_value = empty_transformation
        mock_client.get.return_value = mock_response

        result = await service.describe_transformation(transformation_id)

        # Should handle empty response
        assert result == empty_transformation


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

    def test_describe_transformation_has_docstring(self, service):
        """Test that describe_transformation method has proper documentation"""
        assert service.describe_transformation.__doc__ is not None
        assert len(service.describe_transformation.__doc__.strip()) > 0

    def test_docstring_contains_args_section(self, service):
        """Test that describe_transformation docstring contains Args section"""
        docstring = service.describe_transformation.__doc__
        assert "Args:" in docstring

    def test_docstring_contains_returns_section(self, service):
        """Test that describe_transformation docstring contains Returns section"""
        docstring = service.describe_transformation.__doc__
        assert "Returns:" in docstring

    def test_docstring_contains_raises_section(self, service):
        """Test that describe_transformation docstring contains Raises section"""
        docstring = service.describe_transformation.__doc__
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
        """Test that describe_transformation makes only one API call"""
        transformation_id = "performance-test"
        expected_transformation = {"_id": transformation_id, "name": "Performance Test"}

        mock_response = MagicMock()
        mock_response.json.return_value = expected_transformation
        mock_client.get.return_value = mock_response

        await service.describe_transformation(transformation_id)

        # Should make exactly one API call
        assert mock_client.get.call_count == 1

    @pytest.mark.asyncio
    async def test_concurrent_describe_calls(self, service, mock_client):
        """Test concurrent describe_transformation calls"""
        import asyncio

        transformation_ids = ["transformation-1", "transformation-2", "transformation-3"]
        
        call_count = [0]
        def create_response(*args, **kwargs):
            call_count[0] += 1
            transformation_id = f"transformation-{call_count[0]}"
            response = MagicMock()
            response.json.return_value = {
                "_id": transformation_id, 
                "name": f"Transformation {call_count[0]}"
            }
            return response

        mock_client.get.side_effect = create_response

        # Run concurrent describe operations
        tasks = [
            service.describe_transformation(transformation_id)
            for transformation_id in transformation_ids
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

    @pytest.mark.asyncio
    async def test_large_transformation_response(self, service, mock_client):
        """Test handling of large transformation responses"""
        transformation_id = "large-transformation"
        
        # Create a large transformation with many fields
        large_transformation = {
            "_id": transformation_id,
            "name": "Large Transformation",
            "type": "JSONtoJSON",
            "input": {"type": "object", "properties": {}},
            "output": {"type": "object", "properties": {}},
            "map": {},
            "hardcodedValues": {},
            "conditionals": []
        }
        
        # Add many properties to simulate large response
        for i in range(1000):
            large_transformation["input"]["properties"][f"field_{i}"] = {"type": "string"}
            large_transformation["output"]["properties"][f"out_field_{i}"] = {"type": "string"}
            large_transformation["map"][f"out_field_{i}"] = f"field_{i}"

        mock_response = MagicMock()
        mock_response.json.return_value = large_transformation
        mock_client.get.return_value = mock_response

        result = await service.describe_transformation(transformation_id)

        # Should handle large response without issues
        assert result == large_transformation
        assert len(result["input"]["properties"]) == 1000
        assert len(result["map"]) == 1000