# Copyright (c) 2025 Itential, Inc
# GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)

import pytest
import pathlib
import tempfile
import textwrap
from unittest.mock import AsyncMock, patch, MagicMock

from itential_mcp.client import PlatformClient


@pytest.fixture
def mock_config():
    """Mock configuration for testing"""
    return MagicMock(platform={"url": "https://test.example.com", "token": "test-token"})


@pytest.fixture
def mock_ipsdk_client():
    """Mock ipsdk AsyncPlatform client"""
    return AsyncMock()


@pytest.fixture
def patched_platform_factory(mock_ipsdk_client):
    """Patch ipsdk.platform_factory to return mock client"""
    with patch("itential_mcp.client.ipsdk.platform_factory") as factory_mock:
        factory_mock.return_value = mock_ipsdk_client
        yield factory_mock


@pytest.fixture
def patched_config_get(mock_config):
    """Patch config.get() to return mock config"""
    with patch("itential_mcp.client.config.get") as config_mock:
        config_mock.return_value = mock_config
        yield config_mock


def test_init_client(patched_platform_factory, patched_config_get, mock_config, mock_ipsdk_client):
    """Test that PlatformClient properly initializes the ipsdk client"""
    client = PlatformClient()
    
    # Verify config was retrieved
    patched_config_get.assert_called_once()
    
    # Verify platform_factory was called with correct parameters
    patched_platform_factory.assert_called_once_with(want_async=True, **mock_config.platform)
    
    # Verify client attribute is set correctly
    assert client.client is mock_ipsdk_client


def test_init_plugins_no_services_directory(patched_platform_factory, patched_config_get):
    """Test that _init_plugins handles missing services directory gracefully"""
    with patch("pathlib.Path.exists") as exists_mock:
        exists_mock.return_value = False
        
        client = PlatformClient()
        
        # Should complete without error when services directory doesn't exist
        assert client.client is not None


def test_init_plugins_loads_valid_services(patched_platform_factory, patched_config_get, mock_ipsdk_client):
    """Test that _init_plugins properly loads valid service modules"""
    
    # Create a temporary directory structure for testing
    with tempfile.TemporaryDirectory() as temp_dir:
        services_dir = pathlib.Path(temp_dir) / "services"
        services_dir.mkdir()
        
        # Create a valid service module
        test_service_file = services_dir / "test_service.py"
        test_service_file.write_text(textwrap.dedent("""
            class Service:
                def __init__(self, client):
                    self.client = client
                    self.name = "test_service"
        """))
        
        # Create an invalid service module (no Service class)
        invalid_service_file = services_dir / "invalid_service.py"
        invalid_service_file.write_text("# No Service class here")
        
        # Create a private module (should be ignored)
        private_service_file = services_dir / "_private_service.py"
        private_service_file.write_text("""
            class Service:
                def __init__(self, client):
                    self.name = "_private_service"
        """)
        
        with patch("itential_mcp.client.pathlib.Path.resolve") as resolve_mock:
            # Make resolve() return our temp directory structure
            resolve_mock.return_value.parent = pathlib.Path(temp_dir)
            
            client = PlatformClient()
            
            # Should have loaded the valid service
            assert hasattr(client, "test_service")
            assert client.test_service.name == "test_service"
            assert client.test_service.client is mock_ipsdk_client
            
            # Should not have loaded invalid or private services
            assert not hasattr(client, "invalid_service")
            assert not hasattr(client, "_private_service")


def test_init_plugins_handles_import_errors(patched_platform_factory, patched_config_get):
    """Test that _init_plugins gracefully handles modules with import errors"""
    
    with tempfile.TemporaryDirectory() as temp_dir:
        services_dir = pathlib.Path(temp_dir) / "services"
        services_dir.mkdir()
        
        # Create a service module with syntax error
        broken_service_file = services_dir / "broken_service.py"
        broken_service_file.write_text("import nonexistent_module\nclass Service: pass")
        
        with patch("itential_mcp.client.pathlib.Path.resolve") as resolve_mock:
            resolve_mock.return_value.parent = pathlib.Path(temp_dir)
            
            # Should complete without raising exception
            client = PlatformClient()
            assert not hasattr(client, "broken_service")


def test_init_plugins_handles_missing_service_class(patched_platform_factory, patched_config_get):
    """Test that _init_plugins handles modules without Service class"""
    
    with tempfile.TemporaryDirectory() as temp_dir:
        services_dir = pathlib.Path(temp_dir) / "services"
        services_dir.mkdir()
        
        # Create a module without Service class
        no_service_file = services_dir / "no_service.py"
        no_service_file.write_text("def some_function(): pass")
        
        with patch("itential_mcp.client.pathlib.Path.resolve") as resolve_mock:
            resolve_mock.return_value.parent = pathlib.Path(temp_dir)
            
            client = PlatformClient()
            assert not hasattr(client, "no_service")


def test_init_plugins_handles_service_instantiation_error(patched_platform_factory, patched_config_get, mock_ipsdk_client):
    """Test that _init_plugins handles errors during service instantiation"""
    
    with tempfile.TemporaryDirectory() as temp_dir:
        services_dir = pathlib.Path(temp_dir) / "services"
        services_dir.mkdir()
        
        # Create a service that raises an error during instantiation
        error_service_file = services_dir / "error_service.py"
        error_service_file.write_text(textwrap.dedent("""
            class Service:
                def __init__(self, client):
                    raise ValueError("Intentional error for testing")
        """))
        
        with patch("itential_mcp.client.pathlib.Path.resolve") as resolve_mock:
            resolve_mock.return_value.parent = pathlib.Path(temp_dir)
            
            # Should complete without raising exception
            client = PlatformClient()
            assert not hasattr(client, "error_service")

