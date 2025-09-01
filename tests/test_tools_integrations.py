# Copyright (c) 2025 Itential, Inc
# GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)

import pytest
from unittest.mock import AsyncMock, Mock, patch

from fastmcp import Context

from itential_mcp import exceptions
from itential_mcp.tools import integrations
from itential_mcp.models.integrations import (
    GetIntegrationModelsResponse,
    GetIntegrationModelsElement,
    CreateIntegrationModelResponse
)


class TestGetIntegrationModels:
    """Test cases for the get_integration_models tool function."""

    @pytest.fixture
    def mock_context(self):
        """Create a mock FastMCP Context for testing."""
        context = Mock(spec=Context)
        context.info = AsyncMock()
        
        # Mock the lifespan context
        mock_client = Mock()
        mock_client.integrations = Mock()
        mock_client.integrations.get_integration_models = AsyncMock()
        
        context.request_context = Mock()
        context.request_context.lifespan_context = Mock()
        context.request_context.lifespan_context.get = Mock(return_value=mock_client)
        
        return context

    @pytest.mark.asyncio
    async def test_get_integration_models_success(self, mock_context):
        """Test successful retrieval of integration models."""
        # Mock the client response
        mock_response = {
            "integrationModels": [
                {
                    "versionId": "test-api:1.0.0",
                    "properties": {"version": "1.0.0"},
                    "description": "Test API"
                },
                {
                    "versionId": "another-api:2.1.0",
                    "properties": {"version": "2.1.0"},
                    "description": "Another API"
                }
            ]
        }
        
        client = mock_context.request_context.lifespan_context.get.return_value
        client.integrations.get_integration_models.return_value = mock_response
        
        result = await integrations.get_integration_models(mock_context)
        
        # Verify context.info was called
        mock_context.info.assert_called_once_with("inside get_integration_models(...)")
        
        # Verify client was retrieved and method called
        mock_context.request_context.lifespan_context.get.assert_called_once_with("client")
        client.integrations.get_integration_models.assert_called_once()
        
        # Verify the result is properly transformed
        expected_result = GetIntegrationModelsResponse(root=[
            GetIntegrationModelsElement(
                id="test-api:1.0.0",
                title="test-api",
                version="1.0.0",
                description="Test API"
            ),
            GetIntegrationModelsElement(
                id="another-api:2.1.0",
                title="another-api", 
                version="2.1.0",
                description="Another API"
            )
        ])
        
        assert result == expected_result

    @pytest.mark.asyncio
    async def test_get_integration_models_empty_response(self, mock_context):
        """Test get_integration_models with empty response."""
        mock_response = {"integrationModels": []}
        
        client = mock_context.request_context.lifespan_context.get.return_value
        client.integrations.get_integration_models.return_value = mock_response
        
        result = await integrations.get_integration_models(mock_context)
        
        assert result == GetIntegrationModelsResponse(root=[])

    @pytest.mark.asyncio
    async def test_get_integration_models_missing_description(self, mock_context):
        """Test get_integration_models handles missing description field."""
        mock_response = {
            "integrationModels": [
                {
                    "versionId": "test-api:1.0.0",
                    "properties": {"version": "1.0.0"}
                    # No description field
                }
            ]
        }
        
        client = mock_context.request_context.lifespan_context.get.return_value
        client.integrations.get_integration_models.return_value = mock_response
        
        result = await integrations.get_integration_models(mock_context)
        
        expected_result = GetIntegrationModelsResponse(root=[
            GetIntegrationModelsElement(
                id="test-api:1.0.0",
                title="test-api",
                version="1.0.0",
                description=None
            )
        ])
        
        assert result == expected_result

    @pytest.mark.asyncio
    async def test_get_integration_models_complex_version_id(self, mock_context):
        """Test get_integration_models handles complex version IDs with multiple colons."""
        mock_response = {
            "integrationModels": [
                {
                    "versionId": "namespace:api-name:1.0.0:beta",
                    "properties": {"version": "1.0.0"},
                    "description": "Complex API"
                }
            ]
        }
        
        client = mock_context.request_context.lifespan_context.get.return_value
        client.integrations.get_integration_models.return_value = mock_response
        
        result = await integrations.get_integration_models(mock_context)
        
        expected_result = GetIntegrationModelsResponse(root=[
            GetIntegrationModelsElement(
                id="namespace:api-name:1.0.0:beta",
                title="namespace",  # Only takes first part before ':'
                version="1.0.0",
                description="Complex API"
            )
        ])
        
        assert result == expected_result

    @pytest.mark.asyncio
    async def test_get_integration_models_client_error(self, mock_context):
        """Test get_integration_models handles client errors."""
        client = mock_context.request_context.lifespan_context.get.return_value
        client.integrations.get_integration_models.side_effect = Exception("Connection failed")
        
        with pytest.raises(Exception) as exc_info:
            await integrations.get_integration_models(mock_context)
        
        assert "Connection failed" in str(exc_info.value)


class TestCreateIntegrationModel:
    """Test cases for the create_integration_model tool function."""

    @pytest.fixture
    def mock_context(self):
        """Create a mock FastMCP Context for testing."""
        context = Mock(spec=Context)
        context.info = AsyncMock()
        
        # Mock the lifespan context
        mock_client = Mock()
        mock_client.integrations = Mock()
        mock_client.integrations.create_integration_model = AsyncMock()
        
        context.request_context = Mock()
        context.request_context.lifespan_context = Mock()
        context.request_context.lifespan_context.get = Mock(return_value=mock_client)
        
        return context

    @pytest.fixture
    def valid_openapi_model(self):
        """Create a valid OpenAPI model for testing."""
        return {
            "info": {
                "title": "test-api",
                "version": "1.0.0",
                "description": "Test API"
            },
            "paths": {
                "/test": {
                    "get": {
                        "summary": "Test endpoint"
                    }
                }
            },
            "components": {
                "schemas": {
                    "TestModel": {
                        "type": "object",
                        "properties": {
                            "id": {"type": "string"}
                        }
                    }
                }
            }
        }

    @pytest.mark.asyncio
    async def test_create_integration_model_success(self, mock_context, valid_openapi_model):
        """Test successful creation of integration model."""
        # Mock get_integration_models to return empty list
        with patch.object(integrations, 'get_integration_models') as mock_get:
            mock_get.return_value = GetIntegrationModelsResponse(root=[])
            
            # Mock client response
            mock_response = {
                "status": "CREATED",
                "message": "Integration model created successfully"
            }
            
            client = mock_context.request_context.lifespan_context.get.return_value
            client.integrations.create_integration_model.return_value = mock_response
            
            result = await integrations.create_integration_model(mock_context, valid_openapi_model)
            
            # Verify context.info was called
            mock_context.info.assert_called_once_with("inside create_integration_model(...)")
            
            # Verify get_integration_models was called to check for duplicates
            mock_get.assert_called_once_with(mock_context)
            
            # Verify client was retrieved and method called
            mock_context.request_context.lifespan_context.get.assert_called_once_with("client")
            client.integrations.create_integration_model.assert_called_once_with(valid_openapi_model)
            
            # Verify the result
            expected_result = CreateIntegrationModelResponse(
                status="CREATED",
                message="Integration model created successfully"
            )
            
            assert result == expected_result

    @pytest.mark.asyncio
    async def test_create_integration_model_already_exists(self, mock_context, valid_openapi_model):
        """Test creation fails when model already exists."""
        # Mock get_integration_models to return existing model with same id
        existing_models = GetIntegrationModelsResponse(root=[
            GetIntegrationModelsElement(
                id="test-api:1.0.0",
                title="test-api",
                version="1.0.0",
                description="Existing API"
            )
        ])
        
        with patch.object(integrations, 'get_integration_models') as mock_get:
            mock_get.return_value = existing_models
            
            with pytest.raises(exceptions.AlreadyExistsError) as exc_info:
                await integrations.create_integration_model(mock_context, valid_openapi_model)
            
            assert "model test-api:1.0.0 already exists" in str(exc_info.value)
            
            # Verify get_integration_models was called
            mock_get.assert_called_once_with(mock_context)
            
            # Verify client creation method was NOT called
            client = mock_context.request_context.lifespan_context.get.return_value
            client.integrations.create_integration_model.assert_not_called()

    @pytest.mark.asyncio
    async def test_create_integration_model_different_version_allowed(self, mock_context):
        """Test creation succeeds when same title but different version exists."""
        model = {
            "info": {
                "title": "test-api",
                "version": "2.0.0"  # Different version
            },
            "paths": {}
        }
        
        # Mock get_integration_models to return existing model with same title, different version
        existing_models = GetIntegrationModelsResponse(root=[
            GetIntegrationModelsElement(
                id="test-api:1.0.0",  # Same title, different version
                title="test-api",
                version="1.0.0",
                description="Existing API v1"
            )
        ])
        
        with patch.object(integrations, 'get_integration_models') as mock_get:
            mock_get.return_value = existing_models
            
            # Mock client response
            mock_response = {
                "status": "CREATED",
                "message": "Integration model created successfully"
            }
            
            client = mock_context.request_context.lifespan_context.get.return_value
            client.integrations.create_integration_model.return_value = mock_response
            
            result = await integrations.create_integration_model(mock_context, model)
            
            # Should succeed since version is different
            expected_result = CreateIntegrationModelResponse(
                status="CREATED",
                message="Integration model created successfully"
            )
            assert result == expected_result
            
            # Verify client method was called
            client.integrations.create_integration_model.assert_called_once_with(model)

    @pytest.mark.asyncio
    async def test_create_integration_model_missing_info_title(self, mock_context):
        """Test creation fails with missing title in info block."""
        model = {
            "info": {
                "version": "1.0.0"
                # Missing title
            },
            "paths": {}
        }
        
        with pytest.raises(KeyError):
            await integrations.create_integration_model(mock_context, model)

    @pytest.mark.asyncio 
    async def test_create_integration_model_missing_info_version(self, mock_context):
        """Test creation fails with missing version in info block."""
        model = {
            "info": {
                "title": "test-api"
                # Missing version
            },
            "paths": {}
        }
        
        with pytest.raises(KeyError):
            await integrations.create_integration_model(mock_context, model)

    @pytest.mark.asyncio
    async def test_create_integration_model_missing_info_block(self, mock_context):
        """Test creation fails with missing info block."""
        model = {
            # Missing info block
            "paths": {}
        }
        
        with pytest.raises(KeyError):
            await integrations.create_integration_model(mock_context, model)

    @pytest.mark.asyncio
    async def test_create_integration_model_client_error(self, mock_context, valid_openapi_model):
        """Test create_integration_model handles client errors."""
        with patch.object(integrations, 'get_integration_models') as mock_get:
            mock_get.return_value = GetIntegrationModelsResponse(root=[])
            
            client = mock_context.request_context.lifespan_context.get.return_value
            client.integrations.create_integration_model.side_effect = Exception("Creation failed")
            
            with pytest.raises(Exception) as exc_info:
                await integrations.create_integration_model(mock_context, valid_openapi_model)
            
            assert "Creation failed" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_create_integration_model_get_models_error(self, mock_context, valid_openapi_model):
        """Test create_integration_model handles errors from get_integration_models."""
        with patch.object(integrations, 'get_integration_models') as mock_get:
            mock_get.side_effect = Exception("Failed to get models")
            
            with pytest.raises(Exception) as exc_info:
                await integrations.create_integration_model(mock_context, valid_openapi_model)
            
            assert "Failed to get models" in str(exc_info.value)


class TestIntegrationModelsIntegration:
    """Integration tests for the integrations tool functions."""

    def test_module_tags(self):
        """Test that the module has correct tags."""
        assert hasattr(integrations, '__tags__')
        assert integrations.__tags__ == ("integrations",)

    def test_function_signatures(self):
        """Test that functions have correct signatures."""
        import inspect
        
        # Test get_integration_models signature
        get_sig = inspect.signature(integrations.get_integration_models)
        assert len(get_sig.parameters) == 1
        assert 'ctx' in get_sig.parameters
        
        # Test create_integration_model signature
        create_sig = inspect.signature(integrations.create_integration_model)
        assert len(create_sig.parameters) == 2
        assert 'ctx' in create_sig.parameters
        assert 'model' in create_sig.parameters

    def test_function_annotations(self):
        """Test that functions have correct type annotations."""
        from typing import get_type_hints
        
        # Test get_integration_models annotations
        get_hints = get_type_hints(integrations.get_integration_models)
        assert 'return' in get_hints
        
        # Test create_integration_model annotations
        create_hints = get_type_hints(integrations.create_integration_model)
        assert 'return' in create_hints

    def test_function_docstrings(self):
        """Test that all functions have proper docstrings."""
        assert integrations.get_integration_models.__doc__ is not None
        assert integrations.create_integration_model.__doc__ is not None
        
        # Check docstring content
        get_doc = integrations.get_integration_models.__doc__
        assert "Get all integration models" in get_doc
        assert "Args:" in get_doc
        assert "Returns:" in get_doc
        
        create_doc = integrations.create_integration_model.__doc__
        assert "Create a new integration model" in create_doc
        assert "Args:" in create_doc
        assert "Returns:" in create_doc
        assert "Raises:" in create_doc

    def test_functions_are_async(self):
        """Test that all functions are async."""
        import inspect
        
        assert inspect.iscoroutinefunction(integrations.get_integration_models)
        assert inspect.iscoroutinefunction(integrations.create_integration_model)

    def test_pydantic_field_annotations(self):
        """Test that functions have proper Pydantic Field annotations."""
        import inspect
        
        # Test get_integration_models parameter annotation
        get_sig = inspect.signature(integrations.get_integration_models)
        ctx_param = get_sig.parameters['ctx']
        assert ctx_param.annotation is not None
        
        # Test create_integration_model parameter annotations
        create_sig = inspect.signature(integrations.create_integration_model)
        ctx_param = create_sig.parameters['ctx']
        model_param = create_sig.parameters['model']
        assert ctx_param.annotation is not None
        assert model_param.annotation is not None


class TestIntegrationModelsErrorScenarios:
    """Test error scenarios and edge cases for integrations tools."""

    @pytest.fixture
    def mock_context(self):
        """Create a mock FastMCP Context for error testing."""
        context = Mock(spec=Context)
        context.info = AsyncMock()
        
        # Mock the lifespan context
        mock_client = Mock()
        mock_client.integrations = Mock()
        
        context.request_context = Mock()
        context.request_context.lifespan_context = Mock()
        context.request_context.lifespan_context.get = Mock(return_value=mock_client)
        
        return context

    @pytest.mark.asyncio
    async def test_get_integration_models_malformed_response(self, mock_context):
        """Test get_integration_models handles malformed API responses."""
        # Missing integrationModels key
        mock_response = {"someOtherKey": []}
        
        client = mock_context.request_context.lifespan_context.get.return_value
        client.integrations.get_integration_models = AsyncMock(return_value=mock_response)
        
        with pytest.raises(KeyError):
            await integrations.get_integration_models(mock_context)

    @pytest.mark.asyncio
    async def test_get_integration_models_missing_version_id(self, mock_context):
        """Test get_integration_models handles missing versionId in response."""
        mock_response = {
            "integrationModels": [
                {
                    # Missing versionId
                    "properties": {"version": "1.0.0"},
                    "description": "Test API"
                }
            ]
        }
        
        client = mock_context.request_context.lifespan_context.get.return_value
        client.integrations.get_integration_models = AsyncMock(return_value=mock_response)
        
        with pytest.raises(KeyError):
            await integrations.get_integration_models(mock_context)

    @pytest.mark.asyncio
    async def test_get_integration_models_missing_properties(self, mock_context):
        """Test get_integration_models handles missing properties in response."""
        mock_response = {
            "integrationModels": [
                {
                    "versionId": "test-api:1.0.0",
                    # Missing properties
                    "description": "Test API"
                }
            ]
        }
        
        client = mock_context.request_context.lifespan_context.get.return_value
        client.integrations.get_integration_models = AsyncMock(return_value=mock_response)
        
        with pytest.raises(KeyError):
            await integrations.get_integration_models(mock_context)

    @pytest.mark.asyncio
    async def test_get_integration_models_missing_version_in_properties(self, mock_context):
        """Test get_integration_models handles missing version in properties."""
        mock_response = {
            "integrationModels": [
                {
                    "versionId": "test-api:1.0.0",
                    "properties": {
                        # Missing version
                        "someOtherProperty": "value"
                    },
                    "description": "Test API"
                }
            ]
        }
        
        client = mock_context.request_context.lifespan_context.get.return_value
        client.integrations.get_integration_models = AsyncMock(return_value=mock_response)
        
        with pytest.raises(KeyError):
            await integrations.get_integration_models(mock_context)

    @pytest.mark.asyncio
    async def test_create_integration_model_multiple_existing_models(self, mock_context):
        """Test create_integration_model correctly identifies duplicates among multiple models."""
        model = {
            "info": {
                "title": "duplicate-api",
                "version": "1.0.0"
            },
            "paths": {}
        }
        
        # Mock get_integration_models to return multiple models including duplicate
        existing_models = GetIntegrationModelsResponse(root=[
            GetIntegrationModelsElement(
                id="other-api:1.0.0",
                title="other-api", 
                version="1.0.0",
                description="Other API"
            ),
            GetIntegrationModelsElement(
                id="duplicate-api:1.0.0",  # This is the duplicate
                title="duplicate-api",
                version="1.0.0", 
                description="Duplicate API"
            ),
            GetIntegrationModelsElement(
                id="third-api:2.0.0",
                title="third-api",
                version="2.0.0",
                description="Third API"
            )
        ])
        
        with patch.object(integrations, 'get_integration_models') as mock_get:
            mock_get.return_value = existing_models
            
            with pytest.raises(exceptions.AlreadyExistsError) as exc_info:
                await integrations.create_integration_model(mock_context, model)
            
            assert "model duplicate-api:1.0.0 already exists" in str(exc_info.value)