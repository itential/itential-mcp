# Copyright (c) 2025 Itential, Inc
# GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)

import pytest
from abc import ABC
from unittest.mock import AsyncMock, MagicMock
from typing import Any

from itential_mcp.services import ServiceBase
from ipsdk.platform import AsyncPlatform


class TestServiceBase:
    """Test the ServiceBase abstract class"""
    
    def test_servicebase_is_abstract_class(self):
        """Test that ServiceBase is an abstract class"""
        assert issubclass(ServiceBase, ABC)
        assert hasattr(ServiceBase, '__abstractmethods__')
        assert 'describe' in ServiceBase.__abstractmethods__
    
    def test_cannot_instantiate_servicebase_directly(self):
        """Test that ServiceBase cannot be instantiated directly due to abstract method"""
        mock_client = AsyncMock(spec=AsyncPlatform)
        
        with pytest.raises(TypeError) as exc_info:
            ServiceBase(mock_client)
        
        assert "Can't instantiate abstract class" in str(exc_info.value)
        assert "describe" in str(exc_info.value)
    
    def test_servicebase_inheritance_and_interface(self):
        """Test that ServiceBase has the correct interface"""
        # Verify it's an ABC
        assert issubclass(ServiceBase, ABC)
        
        # Verify it has the correct abstract method
        assert hasattr(ServiceBase, 'describe')
        assert ServiceBase.describe.__isabstractmethod__
        
        # Verify __init__ method exists and is not abstract
        assert hasattr(ServiceBase, '__init__')
        assert not getattr(ServiceBase.__init__, '__isabstractmethod__', False)
    
    def test_describe_method_signature(self):
        """Test that the describe method has correct signature"""
        import inspect
        
        describe_signature = inspect.signature(ServiceBase.describe)
        parameters = list(describe_signature.parameters.keys())
        
        # Should have self, *args, **kwargs
        assert 'self' in parameters
        assert any(param.kind == inspect.Parameter.VAR_POSITIONAL for param in describe_signature.parameters.values())
        assert any(param.kind == inspect.Parameter.VAR_KEYWORD for param in describe_signature.parameters.values())
        
        # Return annotation should be Any | None
        return_annotation = describe_signature.return_annotation
        assert return_annotation is not inspect.Signature.empty
    
    def test_servicebase_docstring_exists(self):
        """Test that ServiceBase has comprehensive documentation"""
        assert ServiceBase.__doc__ is not None
        assert len(ServiceBase.__doc__.strip()) > 0
        
        # Check that key concepts are documented
        docstring = ServiceBase.__doc__
        assert "Abstract base class" in docstring
        assert "Itential Platform" in docstring
        assert "service implementations" in docstring
        assert "Args:" in docstring
        assert "Attributes:" in docstring
    
    def test_describe_method_docstring(self):
        """Test that the describe method has proper documentation"""
        assert ServiceBase.describe.__doc__ is not None
        assert len(ServiceBase.describe.__doc__.strip()) > 0
        
        docstring = ServiceBase.describe.__doc__
        assert "Abstract method" in docstring
        assert "Args:" in docstring
        assert "Returns:" in docstring
        assert "*args" in docstring
        assert "**kwargs" in docstring


class ConcreteService(ServiceBase):
    """Concrete implementation of ServiceBase for testing"""
    
    def __init__(self, client: AsyncPlatform):
        super().__init__(client)
        self.name = "test_service"
    
    async def describe(self, *args, **kwargs) -> Any | None:
        """Test implementation of describe method"""
        return {"service": "test", "args": args, "kwargs": kwargs}


class ConcreteServiceWithReturnNone(ServiceBase):
    """Concrete implementation that returns None from describe"""
    
    async def describe(self, *args, **kwargs) -> Any | None:
        """Implementation that returns None"""
        return None


class ConcreteServiceWithComplexReturn(ServiceBase):
    """Concrete implementation that returns complex data structures"""
    
    async def describe(self, resource_id: str, include_details: bool = False) -> dict:
        """Implementation that returns complex data"""
        result = {"id": resource_id, "type": "complex_service"}
        if include_details:
            result["details"] = {"created": "2025-01-01", "status": "active"}
        return result


class TestConcreteServiceImplementations:
    """Test concrete implementations of ServiceBase"""
    
    @pytest.fixture
    def mock_client(self):
        """Create a mock AsyncPlatform client"""
        return AsyncMock(spec=AsyncPlatform)
    
    def test_concrete_service_instantiation(self, mock_client):
        """Test that concrete service can be instantiated"""
        service = ConcreteService(mock_client)
        
        assert isinstance(service, ServiceBase)
        assert isinstance(service, ConcreteService)
        assert service.client is mock_client
        assert service.name == "test_service"
    
    @pytest.mark.asyncio
    async def test_concrete_service_describe_method(self, mock_client):
        """Test that concrete service describe method works correctly"""
        service = ConcreteService(mock_client)
        
        # Test with no arguments
        result = await service.describe()
        expected = {"service": "test", "args": (), "kwargs": {}}
        assert result == expected
        
        # Test with positional arguments
        result = await service.describe("arg1", "arg2")
        expected = {"service": "test", "args": ("arg1", "arg2"), "kwargs": {}}
        assert result == expected
        
        # Test with keyword arguments
        result = await service.describe(key1="value1", key2="value2")
        expected = {"service": "test", "args": (), "kwargs": {"key1": "value1", "key2": "value2"}}
        assert result == expected
        
        # Test with both positional and keyword arguments
        result = await service.describe("arg1", key1="value1")
        expected = {"service": "test", "args": ("arg1",), "kwargs": {"key1": "value1"}}
        assert result == expected
    
    @pytest.mark.asyncio
    async def test_concrete_service_returning_none(self, mock_client):
        """Test concrete service that returns None from describe"""
        service = ConcreteServiceWithReturnNone(mock_client)
        
        result = await service.describe("test")
        assert result is None
    
    @pytest.mark.asyncio
    async def test_concrete_service_with_complex_return(self, mock_client):
        """Test concrete service with complex return types"""
        service = ConcreteServiceWithComplexReturn(mock_client)
        
        # Test without details
        result = await service.describe("test-123")
        expected = {"id": "test-123", "type": "complex_service"}
        assert result == expected
        
        # Test with details
        result = await service.describe("test-456", include_details=True)
        expected = {
            "id": "test-456",
            "type": "complex_service",
            "details": {"created": "2025-01-01", "status": "active"}
        }
        assert result == expected
    
    def test_multiple_concrete_services_with_same_client(self, mock_client):
        """Test that multiple concrete services can share the same client"""
        service1 = ConcreteService(mock_client)
        service2 = ConcreteServiceWithReturnNone(mock_client)
        service3 = ConcreteServiceWithComplexReturn(mock_client)
        
        assert service1.client is mock_client
        assert service2.client is mock_client
        assert service3.client is mock_client
        
        # Verify they are different instances
        assert service1 is not service2
        assert service2 is not service3
        assert service1 is not service3
    
    def test_concrete_service_client_attribute_immutable(self, mock_client):
        """Test that client attribute can be modified but doesn't affect other instances"""
        service1 = ConcreteService(mock_client)
        service2 = ConcreteService(mock_client)
        
        # Initially both should have the same client
        assert service1.client is mock_client
        assert service2.client is mock_client
        
        # Modify one service's client
        new_mock_client = AsyncMock(spec=AsyncPlatform)
        service1.client = new_mock_client
        
        # service1 should have new client, service2 should still have original
        assert service1.client is new_mock_client
        assert service2.client is mock_client


class PartiallyImplementedService(ServiceBase):
    """Service that doesn't implement describe method (should fail)"""
    
    def __init__(self, client: AsyncPlatform):
        super().__init__(client)


class TestServiceBaseErrorCases:
    """Test error cases and edge conditions for ServiceBase"""
    
    @pytest.fixture
    def mock_client(self):
        """Create a mock AsyncPlatform client"""
        return AsyncMock(spec=AsyncPlatform)
    
    def test_partially_implemented_service_fails(self, mock_client):
        """Test that service without describe implementation cannot be instantiated"""
        with pytest.raises(TypeError) as exc_info:
            PartiallyImplementedService(mock_client)
        
        assert "Can't instantiate abstract class" in str(exc_info.value)
        assert "describe" in str(exc_info.value)
    
    def test_servicebase_with_none_client(self):
        """Test behavior when None is passed as client"""
        service = ConcreteService(None)
        assert service.client is None
    
    def test_servicebase_with_invalid_client_type(self):
        """Test behavior when non-AsyncPlatform object is passed as client"""
        invalid_client = "not a client"
        service = ConcreteService(invalid_client)
        assert service.client == "not a client"
        
        # Note: The class doesn't enforce type checking at runtime,
        # it relies on type hints for static analysis
    
    def test_servicebase_inheritance_chain(self, mock_client):
        """Test that inheritance chain works correctly"""
        service = ConcreteService(mock_client)
        
        # Check MRO (Method Resolution Order)
        mro = ConcreteService.__mro__
        assert ServiceBase in mro
        assert ABC in mro
        
        # Check isinstance relationships
        assert isinstance(service, ConcreteService)
        assert isinstance(service, ServiceBase)
        assert isinstance(service, ABC)


class TestServiceBaseIntegration:
    """Integration tests for ServiceBase with real-world scenarios"""
    
    @pytest.fixture
    def mock_platform_client(self):
        """Create a comprehensive mock of AsyncPlatform client"""
        client = AsyncMock(spec=AsyncPlatform)
        client.get = AsyncMock()
        client.post = AsyncMock()
        client.put = AsyncMock()
        client.delete = AsyncMock()
        return client
    
    @pytest.mark.asyncio
    async def test_service_using_client_methods(self, mock_platform_client):
        """Test service that actually uses the client for API calls"""
        
        class ApiService(ServiceBase):
            async def describe(self, resource_id: str) -> dict:
                """Get resource details from API"""
                response = await self.client.get(f"/api/resources/{resource_id}")
                return response.json()
        
        # Setup mock response
        mock_response = MagicMock()
        mock_response.json.return_value = {"id": "test-123", "name": "Test Resource"}
        mock_platform_client.get.return_value = mock_response
        
        service = ApiService(mock_platform_client)
        result = await service.describe("test-123")
        
        # Verify the client was called correctly
        mock_platform_client.get.assert_called_once_with("/api/resources/test-123")
        
        # Verify the result
        assert result == {"id": "test-123", "name": "Test Resource"}
    
    def test_service_registry_pattern(self, mock_platform_client):
        """Test using ServiceBase in a service registry pattern"""
        
        class ServiceRegistry:
            def __init__(self):
                self.services = {}
            
            def register(self, name: str, service: ServiceBase):
                if not isinstance(service, ServiceBase):
                    raise TypeError(f"Service must inherit from ServiceBase, got {type(service)}")
                self.services[name] = service
            
            def get(self, name: str) -> ServiceBase:
                return self.services.get(name)
        
        registry = ServiceRegistry()
        
        # Register valid services
        service1 = ConcreteService(mock_platform_client)
        service2 = ConcreteServiceWithReturnNone(mock_platform_client)
        
        registry.register("service1", service1)
        registry.register("service2", service2)
        
        # Verify registration
        assert registry.get("service1") is service1
        assert registry.get("service2") is service2
        
        # Test invalid registration
        with pytest.raises(TypeError) as exc_info:
            registry.register("invalid", "not a service")
        
        assert "Service must inherit from ServiceBase" in str(exc_info.value)
    
    @pytest.mark.asyncio
    async def test_service_composition(self, mock_platform_client):
        """Test composing multiple services together"""
        
        class CompositeService(ServiceBase):
            def __init__(self, client: AsyncPlatform, *sub_services: ServiceBase):
                super().__init__(client)
                self.sub_services = sub_services
            
            async def describe(self, *args, **kwargs) -> dict:
                """Aggregate results from multiple sub-services"""
                results = {}
                for i, service in enumerate(self.sub_services):
                    result = await service.describe(*args, **kwargs)
                    results[f"service_{i}"] = result
                return results
        
        # Create sub-services
        service1 = ConcreteService(mock_platform_client)
        service2 = ConcreteServiceWithReturnNone(mock_platform_client)
        
        # Create composite service
        composite = CompositeService(mock_platform_client, service1, service2)
        
        # Test the composite
        result = await composite.describe("test")
        
        expected = {
            "service_0": {"service": "test", "args": ("test",), "kwargs": {}},
            "service_1": None
        }
        assert result == expected