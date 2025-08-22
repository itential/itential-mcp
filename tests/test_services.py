# Copyright (c) 2025 Itential, Inc
# GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)

import pytest
from unittest.mock import AsyncMock

from itential_mcp.services import ServiceBase
from ipsdk.platform import AsyncPlatform


class TestServiceBase:
    """Test the ServiceBase class"""
    
    def test_servicebase_is_concrete_class(self):
        """Test that ServiceBase is a concrete class"""
        assert not hasattr(ServiceBase, '__abstractmethods__')
    
    def test_can_instantiate_servicebase_directly(self):
        """Test that ServiceBase can be instantiated directly"""
        mock_client = AsyncMock(spec=AsyncPlatform)
        
        service = ServiceBase(mock_client)
        assert service.client == mock_client
    
    def test_servicebase_inheritance_and_interface(self):
        """Test that ServiceBase has the correct interface"""
        # Verify __init__ method exists
        assert hasattr(ServiceBase, '__init__')
        
        # Test that it can be instantiated
        mock_client = AsyncMock(spec=AsyncPlatform)
        service = ServiceBase(mock_client)
        assert service.client == mock_client
    
    def test_servicebase_initialization(self):
        """Test that ServiceBase initializes correctly"""
        mock_client = AsyncMock(spec=AsyncPlatform)
        
        service = ServiceBase(mock_client)
        assert service.client == mock_client
    
    def test_servicebase_docstring_exists(self):
        """Test that ServiceBase has comprehensive documentation"""
        assert ServiceBase.__doc__ is not None
        assert len(ServiceBase.__doc__.strip()) > 0
        
        # Check that key concepts are documented
        docstring = ServiceBase.__doc__
        assert "Abstract base class" in docstring or "base class" in docstring
        assert "Itential Platform" in docstring
        assert "service implementations" in docstring
        assert "Args:" in docstring
        assert "Attributes:" in docstring


class ConcreteService(ServiceBase):
    """Concrete implementation of ServiceBase for testing"""
    
    def __init__(self, client: AsyncPlatform):
        super().__init__(client)
        self.name = "test_service"


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
    
    def test_servicebase_inheritance_chain(self, mock_client):
        """Test that inheritance chain works correctly"""
        ConcreteService(mock_client)
        
        # Check MRO (Method Resolution Order)
        mro = ConcreteService.__mro__
        assert ServiceBase in mro
        assert object in mro


class TestServiceBaseErrorCases:
    """Test error cases and edge conditions"""
    
    @pytest.fixture
    def mock_client(self):
        """Create a mock AsyncPlatform client"""
        return AsyncMock(spec=AsyncPlatform)
    
    def test_servicebase_with_none_client(self):
        """Test that ServiceBase handles None client gracefully"""
        service = ServiceBase(None)
        assert service.client is None
    
    def test_servicebase_client_assignment(self, mock_client):
        """Test that client is properly assigned during initialization"""
        service = ServiceBase(mock_client)
        assert service.client is mock_client
        
        # Test that client can be changed after initialization
        new_client = AsyncMock(spec=AsyncPlatform)
        service.client = new_client
        assert service.client is new_client