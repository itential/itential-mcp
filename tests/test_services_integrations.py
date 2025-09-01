# Copyright (c) 2025 Itential, Inc
# GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)

import pytest
from unittest.mock import AsyncMock, Mock

from itential_mcp import exceptions
from itential_mcp.services.integrations import Service
from itential_mcp.response import Response


class TestService:
    """Test cases for the integrations Service class."""
    
    @pytest.fixture
    def mock_client(self):
        """Create a mock client for testing."""
        client = Mock()
        client.get = AsyncMock()
        client.post = AsyncMock()
        client.put = AsyncMock()
        return client
    
    @pytest.fixture
    def service(self, mock_client):
        """Create a service instance with mock client."""
        service = Service(mock_client)
        return service

    def test_service_name(self, service):
        """Test that the service name is set correctly."""
        assert service.name == "integrations"

    def test_service_class_docstring(self):
        """Test that the Service class has proper docstring."""
        assert Service.__doc__ is not None
        assert "Integration models service" in Service.__doc__

    @pytest.mark.asyncio
    async def test_get_integration_models_success(self, service, mock_client):
        """Test successful retrieval of integration models."""
        expected_response = {
            "integrationModels": [
                {
                    "versionId": "test-model:1.0.0",
                    "properties": {"version": "1.0.0"},
                    "description": "Test model"
                }
            ]
        }
        
        mock_response = Mock(spec=Response)
        mock_response.json.return_value = expected_response
        mock_client.get.return_value = mock_response
        
        result = await service.get_integration_models()
        
        mock_client.get.assert_called_once_with("/integration-models")
        assert result == expected_response

    @pytest.mark.asyncio
    async def test_get_integration_models_empty_response(self, service, mock_client):
        """Test get_integration_models with empty response."""
        expected_response = {"integrationModels": []}
        
        mock_response = Mock(spec=Response)
        mock_response.json.return_value = expected_response
        mock_client.get.return_value = mock_response
        
        result = await service.get_integration_models()
        
        mock_client.get.assert_called_once_with("/integration-models")
        assert result == expected_response

    @pytest.mark.asyncio
    async def test_create_integration_model_success(self, service, mock_client):
        """Test successful creation of integration model."""
        model = {
            "info": {
                "title": "test-api",
                "version": "1.0.0"
            },
            "paths": {},
            "components": {}
        }
        
        expected_create_response = {
            "status": "CREATED",
            "message": "Model created successfully"
        }
        
        # Mock get_integration_models to return empty list (no existing models)
        get_models_response = {"integrationModels": []}
        get_mock_response = Mock(spec=Response)
        get_mock_response.json.return_value = get_models_response
        
        # Mock validation endpoint
        validation_mock_response = Mock(spec=Response)
        validation_mock_response.json.return_value = {"valid": True}
        
        # Mock creation endpoint
        create_mock_response = Mock(spec=Response)
        create_mock_response.json.return_value = expected_create_response
        
        mock_client.get.return_value = get_mock_response
        mock_client.put.return_value = validation_mock_response
        mock_client.post.return_value = create_mock_response
        
        result = await service.create_integration_model(model)
        
        # Verify all calls were made
        mock_client.get.assert_called_once_with("/integration-models")
        mock_client.put.assert_called_once_with(
            "/integration-models/validation",
            json={"model": model}
        )
        mock_client.post.assert_called_once_with(
            "/integration-models",
            json={"model": model}
        )
        
        assert result == expected_create_response

    @pytest.mark.asyncio
    async def test_create_integration_model_already_exists(self, service, mock_client):
        """Test creation fails when model already exists."""
        model = {
            "info": {
                "title": "existing-api",
                "version": "1.0.0"
            },
            "paths": {},
            "components": {}
        }
        
        # Mock get_integration_models to return existing model
        existing_models_response = {
            "integrationModels": [
                {
                    "versionId": "existing-api:1.0.0",
                    "properties": {"version": "1.0.0"}
                }
            ]
        }
        get_mock_response = Mock(spec=Response)
        get_mock_response.json.return_value = existing_models_response
        mock_client.get.return_value = get_mock_response
        
        with pytest.raises(exceptions.AlreadyExistsError) as exc_info:
            await service.create_integration_model(model)
        
        assert "model existing-api:1.0.0 already exists" in str(exc_info.value)
        mock_client.get.assert_called_once_with("/integration-models")
        # Validation and creation should not be called
        mock_client.put.assert_not_called()
        mock_client.post.assert_not_called()

    @pytest.mark.asyncio
    async def test_create_integration_model_with_different_version(self, service, mock_client):
        """Test creation succeeds when same title but different version exists."""
        model = {
            "info": {
                "title": "test-api",
                "version": "2.0.0"  # Different version
            },
            "paths": {},
            "components": {}
        }
        
        # Mock get_integration_models to return existing model with different version
        existing_models_response = {
            "integrationModels": [
                {
                    "versionId": "test-api:1.0.0",  # Same title, different version
                    "properties": {"version": "1.0.0"}
                }
            ]
        }
        get_mock_response = Mock(spec=Response)
        get_mock_response.json.return_value = existing_models_response
        
        expected_create_response = {
            "status": "CREATED",
            "message": "Model created successfully"
        }
        
        validation_mock_response = Mock(spec=Response)
        validation_mock_response.json.return_value = {"valid": True}
        
        create_mock_response = Mock(spec=Response)
        create_mock_response.json.return_value = expected_create_response
        
        mock_client.get.return_value = get_mock_response
        mock_client.put.return_value = validation_mock_response
        mock_client.post.return_value = create_mock_response
        
        result = await service.create_integration_model(model)
        
        # Verify all calls were made
        mock_client.get.assert_called_once_with("/integration-models")
        mock_client.put.assert_called_once_with(
            "/integration-models/validation",
            json={"model": model}
        )
        mock_client.post.assert_called_once_with(
            "/integration-models",
            json={"model": model}
        )
        
        assert result == expected_create_response

    @pytest.mark.asyncio
    async def test_create_integration_model_missing_info_title(self, service):
        """Test creation fails with missing title in info block."""
        model = {
            "info": {
                "version": "1.0.0"
                # Missing title
            },
            "paths": {},
            "components": {}
        }
        
        with pytest.raises(KeyError):
            await service.create_integration_model(model)

    @pytest.mark.asyncio
    async def test_create_integration_model_missing_info_version(self, service):
        """Test creation fails with missing version in info block."""
        model = {
            "info": {
                "title": "test-api"
                # Missing version
            },
            "paths": {},
            "components": {}
        }
        
        with pytest.raises(KeyError):
            await service.create_integration_model(model)

    @pytest.mark.asyncio
    async def test_create_integration_model_missing_info_block(self, service):
        """Test creation fails with missing info block."""
        model = {
            # Missing info block
            "paths": {},
            "components": {}
        }
        
        with pytest.raises(KeyError):
            await service.create_integration_model(model)


class TestServiceIntegration:
    """Integration tests for the integrations Service class."""
    
    @pytest.fixture
    def service(self):
        """Create a service instance without mocking for integration tests."""
        mock_client = Mock()
        return Service(mock_client)
    
    def test_service_inheritance(self, service):
        """Test that Service properly inherits from ServiceBase."""
        from itential_mcp.services import ServiceBase
        assert isinstance(service, ServiceBase)
    
    def test_service_name_property(self, service):
        """Test that the service name property is accessible."""
        assert hasattr(service, 'name')
        assert service.name == "integrations"
    
    def test_service_methods_exist(self, service):
        """Test that all expected service methods exist."""
        assert hasattr(service, 'get_integration_models')
        assert hasattr(service, 'create_integration_model')
        assert callable(service.get_integration_models)
        assert callable(service.create_integration_model)
    
    def test_service_method_signatures(self, service):
        """Test that service methods have correct signatures."""
        import inspect
        
        # Test get_integration_models signature
        get_sig = inspect.signature(service.get_integration_models)
        assert len(get_sig.parameters) == 0  # Should only have 'self'
        
        # Test create_integration_model signature
        create_sig = inspect.signature(service.create_integration_model)
        assert len(create_sig.parameters) == 1  # Should have 'self' and 'model'
        assert 'model' in create_sig.parameters
    
    def test_service_docstrings_exist(self, service):
        """Test that all service methods have docstrings."""
        assert service.get_integration_models.__doc__ is not None
        assert service.create_integration_model.__doc__ is not None
        assert "Get all integration models" in service.get_integration_models.__doc__
        assert "Create a new integration model" in service.create_integration_model.__doc__


class TestServiceErrorHandling:
    """Test error handling scenarios for the integrations Service class."""
    
    @pytest.fixture
    def mock_client(self):
        """Create a mock client for error testing."""
        client = Mock()
        client.get = AsyncMock()
        client.post = AsyncMock()
        client.put = AsyncMock()
        return client
    
    @pytest.fixture
    def service(self, mock_client):
        """Create a service instance with mock client."""
        service = Service(mock_client)
        return service

    @pytest.mark.asyncio
    async def test_get_integration_models_client_error(self, service, mock_client):
        """Test get_integration_models handles client errors properly."""
        mock_client.get.side_effect = Exception("Connection failed")
        
        with pytest.raises(Exception) as exc_info:
            await service.get_integration_models()
        
        assert "Connection failed" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_create_integration_model_get_models_error(self, service, mock_client):
        """Test create_integration_model handles errors from get_integration_models."""
        model = {
            "info": {
                "title": "test-api",
                "version": "1.0.0"
            }
        }
        
        mock_client.get.side_effect = Exception("Failed to get existing models")
        
        with pytest.raises(Exception) as exc_info:
            await service.create_integration_model(model)
        
        assert "Failed to get existing models" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_create_integration_model_validation_error(self, service, mock_client):
        """Test create_integration_model handles validation errors."""
        model = {
            "info": {
                "title": "test-api",
                "version": "1.0.0"
            }
        }
        
        # Mock successful get_integration_models
        get_models_response = {"integrationModels": []}
        get_mock_response = Mock(spec=Response)
        get_mock_response.json.return_value = get_models_response
        mock_client.get.return_value = get_mock_response
        
        # Mock validation failure
        mock_client.put.side_effect = Exception("Validation failed")
        
        with pytest.raises(Exception) as exc_info:
            await service.create_integration_model(model)
        
        assert "Validation failed" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_create_integration_model_creation_error(self, service, mock_client):
        """Test create_integration_model handles creation errors."""
        model = {
            "info": {
                "title": "test-api",
                "version": "1.0.0"
            }
        }
        
        # Mock successful get_integration_models
        get_models_response = {"integrationModels": []}
        get_mock_response = Mock(spec=Response)
        get_mock_response.json.return_value = get_models_response
        mock_client.get.return_value = get_mock_response
        
        # Mock successful validation
        validation_mock_response = Mock(spec=Response)
        validation_mock_response.json.return_value = {"valid": True}
        mock_client.put.return_value = validation_mock_response
        
        # Mock creation failure
        mock_client.post.side_effect = Exception("Creation failed")
        
        with pytest.raises(Exception) as exc_info:
            await service.create_integration_model(model)
        
        assert "Creation failed" in str(exc_info.value)