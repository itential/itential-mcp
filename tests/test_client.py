# Copyright (c) 2025 Itential, Inc
# GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

import pytest
import pathlib
import tempfile
import textwrap
from unittest.mock import AsyncMock, patch, MagicMock

from itential_mcp.platform import PlatformClient


@pytest.fixture
def mock_config():
    """Mock configuration for testing"""
    from itential_mcp.config.models import PlatformConfig

    config = MagicMock()
    # Create a real PlatformConfig so platform_to_dict works
    config.platform = PlatformConfig(
        host="test.example.com",
        port=443,
        disable_tls=False,
        disable_verify=False,
        user="admin",
        password="admin",
        client_id=None,
        client_secret=None,
        timeout=30,
        ttl=0,
    )
    return config


@pytest.fixture
def mock_config_with_disable_verify():
    """Mock configuration with TLS verification disabled"""
    from itential_mcp.config.models import PlatformConfig

    config = MagicMock()
    config.platform = PlatformConfig(
        host="test.example.com",
        port=443,
        disable_tls=False,
        disable_verify=True,
        user="admin",
        password="admin",
        client_id=None,
        client_secret=None,
        timeout=30,
        ttl=0,
    )
    return config


@pytest.fixture
def mock_config_with_disable_tls():
    """Mock configuration with TLS completely disabled"""
    from itential_mcp.config.models import PlatformConfig

    config = MagicMock()
    config.platform = PlatformConfig(
        host="test.example.com",
        port=443,
        disable_tls=True,
        disable_verify=False,
        user="admin",
        password="admin",
        client_id=None,
        client_secret=None,
        timeout=30,
        ttl=0,
    )
    return config


@pytest.fixture
def mock_ipsdk_client():
    """Mock ipsdk AsyncPlatform client"""
    return AsyncMock()


@pytest.fixture
def patched_platform_factory(mock_ipsdk_client):
    """Patch ipsdk.platform_factory to return mock client"""
    with patch("itential_mcp.platform.client.ipsdk.platform_factory") as factory_mock:
        factory_mock.return_value = mock_ipsdk_client
        yield factory_mock


@pytest.fixture
def patched_config_get(mock_config):
    """Patch config.get() to return mock config"""
    with patch("itential_mcp.platform.client.config.get") as config_mock:
        config_mock.return_value = mock_config
        yield config_mock


def test_init_client(
    patched_platform_factory, patched_config_get, mock_config, mock_ipsdk_client
):
    """Test that PlatformClient properly initializes the ipsdk client"""
    from itential_mcp.config.converters import platform_to_dict

    client = PlatformClient()

    # Verify config was retrieved (called twice: once in __init__ for timeout, once in _init_client)
    assert patched_config_get.call_count == 2

    # Verify platform_factory was called with platform config dict
    expected_platform_dict = platform_to_dict(mock_config.platform)
    patched_platform_factory.assert_called_once_with(
        want_async=True, **expected_platform_dict
    )

    # Verify client attribute is set correctly
    assert client.client is mock_ipsdk_client

    # Verify timeout was set
    assert client.timeout == mock_config.platform.timeout


def test_init_plugins_no_services_directory(
    patched_platform_factory, patched_config_get
):
    """Test that _init_plugins handles missing services directory gracefully"""
    with patch("pathlib.Path.exists") as exists_mock:
        exists_mock.return_value = False

        client = PlatformClient()

        # Should complete without error when services directory doesn't exist
        assert client.client is not None


def test_init_plugins_loads_valid_services(
    patched_platform_factory, patched_config_get, mock_ipsdk_client
):
    """Test that _init_plugins properly loads valid service modules"""

    # Create a temporary directory structure for testing
    with tempfile.TemporaryDirectory() as temp_dir:
        services_dir = pathlib.Path(temp_dir) / "services"
        services_dir.mkdir()

        # Create a valid service module
        test_service_file = services_dir / "test_service.py"
        test_service_file.write_text(
            textwrap.dedent("""
            class Service:
                def __init__(self, client):
                    self.client = client
                    self.name = "test_service"
        """)
        )

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

        with patch("itential_mcp.platform.client.pathlib.Path.resolve") as resolve_mock:
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


def test_init_plugins_handles_import_errors(
    patched_platform_factory, patched_config_get
):
    """Test that _init_plugins gracefully handles modules with import errors"""

    with tempfile.TemporaryDirectory() as temp_dir:
        services_dir = pathlib.Path(temp_dir) / "services"
        services_dir.mkdir()

        # Create a service module with syntax error
        broken_service_file = services_dir / "broken_service.py"
        broken_service_file.write_text("import nonexistent_module\nclass Service: pass")

        with patch("itential_mcp.platform.client.pathlib.Path.resolve") as resolve_mock:
            resolve_mock.return_value.parent = pathlib.Path(temp_dir)

            # Should complete without raising exception
            client = PlatformClient()
            assert not hasattr(client, "broken_service")


def test_init_plugins_handles_missing_service_class(
    patched_platform_factory, patched_config_get
):
    """Test that _init_plugins handles modules without Service class"""

    with tempfile.TemporaryDirectory() as temp_dir:
        services_dir = pathlib.Path(temp_dir) / "services"
        services_dir.mkdir()

        # Create a module without Service class
        no_service_file = services_dir / "no_service.py"
        no_service_file.write_text("def some_function(): pass")

        with patch("itential_mcp.platform.client.pathlib.Path.resolve") as resolve_mock:
            resolve_mock.return_value.parent = pathlib.Path(temp_dir)

            client = PlatformClient()
            assert not hasattr(client, "no_service")


def test_init_plugins_handles_service_instantiation_error(
    patched_platform_factory, patched_config_get, mock_ipsdk_client
):
    """Test that _init_plugins handles errors during service instantiation"""

    with tempfile.TemporaryDirectory() as temp_dir:
        services_dir = pathlib.Path(temp_dir) / "services"
        services_dir.mkdir()

        # Create a service that raises an error during instantiation
        error_service_file = services_dir / "error_service.py"
        error_service_file.write_text(
            textwrap.dedent("""
            class Service:
                def __init__(self, client):
                    raise ValueError("Intentional error for testing")
        """)
        )

        with patch("itential_mcp.platform.client.pathlib.Path.resolve") as resolve_mock:
            resolve_mock.return_value.parent = pathlib.Path(temp_dir)

            # Should complete without raising exception
            client = PlatformClient()
            assert not hasattr(client, "error_service")


def test_init_plugins_handles_none_spec(
    patched_platform_factory, patched_config_get, mock_ipsdk_client
):
    """Test that _init_plugins handles None module spec gracefully"""
    with tempfile.TemporaryDirectory() as temp_dir:
        services_dir = pathlib.Path(temp_dir) / "services"
        services_dir.mkdir()

        # Create a valid service file
        service_file = services_dir / "test_service.py"
        service_file.write_text(
            textwrap.dedent("""
            class Service:
                def __init__(self, client):
                    self.name = "test_service"
        """)
        )

        with patch("itential_mcp.platform.client.pathlib.Path.resolve") as resolve_mock:
            resolve_mock.return_value.parent = pathlib.Path(temp_dir)

            # Mock spec_from_file_location to return None
            with patch(
                "itential_mcp.platform.client.importlib.util.spec_from_file_location"
            ) as mock_spec:
                mock_spec.return_value = None

                with patch(
                    "itential_mcp.platform.client.logging.warning"
                ) as mock_warning:
                    client = PlatformClient()

                    # Should log warning and skip the service
                    assert not hasattr(client, "test_service")
                    assert mock_warning.call_count >= 1


def test_init_plugins_handles_none_loader(
    patched_platform_factory, patched_config_get, mock_ipsdk_client
):
    """Test that _init_plugins handles None loader in spec gracefully"""
    with tempfile.TemporaryDirectory() as temp_dir:
        services_dir = pathlib.Path(temp_dir) / "services"
        services_dir.mkdir()

        # Create a valid service file
        service_file = services_dir / "test_service.py"
        service_file.write_text(
            textwrap.dedent("""
            class Service:
                def __init__(self, client):
                    self.name = "test_service"
        """)
        )

        with patch("itential_mcp.platform.client.pathlib.Path.resolve") as resolve_mock:
            resolve_mock.return_value.parent = pathlib.Path(temp_dir)

            # Mock spec with None loader
            with patch(
                "itential_mcp.platform.client.importlib.util.spec_from_file_location"
            ) as mock_spec:
                mock_spec_obj = MagicMock()
                mock_spec_obj.loader = None
                mock_spec.return_value = mock_spec_obj

                with patch(
                    "itential_mcp.platform.client.logging.warning"
                ) as mock_warning:
                    client = PlatformClient()

                    # Should log warning and skip the service
                    assert not hasattr(client, "test_service")
                    assert mock_warning.call_count >= 1


def test_init_plugins_handles_missing_name_attribute(
    patched_platform_factory, patched_config_get, mock_ipsdk_client
):
    """Test that _init_plugins handles services without name attribute"""
    with tempfile.TemporaryDirectory() as temp_dir:
        services_dir = pathlib.Path(temp_dir) / "services"
        services_dir.mkdir()

        # Create a service without name attribute
        service_file = services_dir / "no_name_service.py"
        service_file.write_text(
            textwrap.dedent("""
            class Service:
                def __init__(self, client):
                    self.client = client
                    # No name attribute
        """)
        )

        with patch("itential_mcp.platform.client.pathlib.Path.resolve") as resolve_mock:
            resolve_mock.return_value.parent = pathlib.Path(temp_dir)

            with patch("itential_mcp.platform.client.logging.warning") as mock_warning:
                client = PlatformClient()

                # Should log warning and skip the service
                assert not hasattr(client, "no_name_service")
                warning_calls = [call[0][0] for call in mock_warning.call_args_list]
                assert any(
                    "has no name attribute" in str(call) for call in warning_calls
                )


def test_init_plugins_handles_empty_name(
    patched_platform_factory, patched_config_get, mock_ipsdk_client
):
    """Test that _init_plugins handles services with empty name"""
    with tempfile.TemporaryDirectory() as temp_dir:
        services_dir = pathlib.Path(temp_dir) / "services"
        services_dir.mkdir()

        # Create a service with empty name
        service_file = services_dir / "empty_name_service.py"
        service_file.write_text(
            textwrap.dedent("""
            class Service:
                def __init__(self, client):
                    self.client = client
                    self.name = ""
        """)
        )

        with patch("itential_mcp.platform.client.pathlib.Path.resolve") as resolve_mock:
            resolve_mock.return_value.parent = pathlib.Path(temp_dir)

            with patch("itential_mcp.platform.client.logging.warning") as mock_warning:
                _ = PlatformClient()  # Constructor triggers plugin loading

                # Should log warning and skip the service
                warning_calls = [call[0][0] for call in mock_warning.call_args_list]
                assert any("has invalid name" in str(call) for call in warning_calls)


def test_init_plugins_handles_non_string_name(
    patched_platform_factory, patched_config_get, mock_ipsdk_client
):
    """Test that _init_plugins handles services with non-string name"""
    with tempfile.TemporaryDirectory() as temp_dir:
        services_dir = pathlib.Path(temp_dir) / "services"
        services_dir.mkdir()

        # Create a service with non-string name
        service_file = services_dir / "bad_name_service.py"
        service_file.write_text(
            textwrap.dedent("""
            class Service:
                def __init__(self, client):
                    self.client = client
                    self.name = 123  # Non-string name
        """)
        )

        with patch("itential_mcp.platform.client.pathlib.Path.resolve") as resolve_mock:
            resolve_mock.return_value.parent = pathlib.Path(temp_dir)

            with patch("itential_mcp.platform.client.logging.warning") as mock_warning:
                _ = PlatformClient()  # Constructor triggers plugin loading

                # Should log warning and skip the service
                warning_calls = [call[0][0] for call in mock_warning.call_args_list]
                assert any("has invalid name" in str(call) for call in warning_calls)


def test_init_plugins_handles_invalid_identifier_name(
    patched_platform_factory, patched_config_get, mock_ipsdk_client
):
    """Test that _init_plugins handles services with invalid Python identifier as name"""
    with tempfile.TemporaryDirectory() as temp_dir:
        services_dir = pathlib.Path(temp_dir) / "services"
        services_dir.mkdir()

        # Create a service with invalid identifier name
        service_file = services_dir / "invalid_id_service.py"
        service_file.write_text(
            textwrap.dedent("""
            class Service:
                def __init__(self, client):
                    self.client = client
                    self.name = "123-invalid-name"  # Not a valid identifier
        """)
        )

        with patch("itential_mcp.platform.client.pathlib.Path.resolve") as resolve_mock:
            resolve_mock.return_value.parent = pathlib.Path(temp_dir)

            with patch("itential_mcp.platform.client.logging.warning") as mock_warning:
                _ = PlatformClient()  # Constructor triggers plugin loading

                # Should log warning and skip the service
                warning_calls = [call[0][0] for call in mock_warning.call_args_list]
                assert any(
                    "is not a valid Python identifier" in str(call)
                    for call in warning_calls
                )


def test_init_plugins_handles_attribute_error(
    patched_platform_factory, patched_config_get, mock_ipsdk_client
):
    """Test that _init_plugins handles AttributeError during service loading"""
    with tempfile.TemporaryDirectory() as temp_dir:
        services_dir = pathlib.Path(temp_dir) / "services"
        services_dir.mkdir()

        # Create a service that will raise AttributeError when accessed
        service_file = services_dir / "attr_error_service.py"
        service_file.write_text(
            textwrap.dedent("""
            class Service:
                def __init__(self, client):
                    self.client = client
                    # Access nonexistent attribute to trigger AttributeError
                    _ = self.nonexistent_attribute
        """)
        )

        with patch("itential_mcp.platform.client.pathlib.Path.resolve") as resolve_mock:
            resolve_mock.return_value.parent = pathlib.Path(temp_dir)

            with patch("itential_mcp.platform.client.logging.warning") as mock_warning:
                client = PlatformClient()

                # Should log warning and continue
                assert not hasattr(client, "attr_error_service")
                warning_calls = [call[0][0] for call in mock_warning.call_args_list]
                assert any("has attribute error" in str(call) for call in warning_calls)


def test_init_plugins_import_error_with_debug_logging(
    patched_platform_factory, patched_config_get, mock_ipsdk_client
):
    """Test that _init_plugins logs import errors with traceback when DEBUG logging enabled"""
    with tempfile.TemporaryDirectory() as temp_dir:
        services_dir = pathlib.Path(temp_dir) / "services"
        services_dir.mkdir()

        # Create a service with import error
        service_file = services_dir / "import_error_service.py"
        service_file.write_text("import nonexistent_module\nclass Service: pass")

        with patch("itential_mcp.platform.client.pathlib.Path.resolve") as resolve_mock:
            resolve_mock.return_value.parent = pathlib.Path(temp_dir)

            # Mock logger to enable DEBUG level
            mock_logger = MagicMock()
            mock_logger.isEnabledFor.return_value = True

            with patch(
                "itential_mcp.platform.client.logging.get_logger"
            ) as mock_get_logger:
                mock_get_logger.return_value = mock_logger

                _ = PlatformClient()  # Constructor triggers plugin loading

                # Verify that warning was called with exc_info=True for debug logging
                assert mock_logger.warning.called


def test_init_plugins_attribute_error_with_debug_logging(
    patched_platform_factory, patched_config_get, mock_ipsdk_client
):
    """Test that _init_plugins logs attribute errors with traceback when DEBUG logging enabled"""
    with tempfile.TemporaryDirectory() as temp_dir:
        services_dir = pathlib.Path(temp_dir) / "services"
        services_dir.mkdir()

        # Create a service that raises AttributeError
        service_file = services_dir / "attr_error_service.py"
        service_file.write_text(
            textwrap.dedent("""
            class Service:
                def __init__(self, client):
                    _ = self.nonexistent
        """)
        )

        with patch("itential_mcp.platform.client.pathlib.Path.resolve") as resolve_mock:
            resolve_mock.return_value.parent = pathlib.Path(temp_dir)

            # Mock logger to enable DEBUG level
            mock_logger = MagicMock()
            mock_logger.isEnabledFor.return_value = True

            with patch(
                "itential_mcp.platform.client.logging.get_logger"
            ) as mock_get_logger:
                mock_get_logger.return_value = mock_logger

                _ = PlatformClient()  # Constructor triggers plugin loading

                # Verify that warning was called with exc_info=True for debug logging
                assert mock_logger.warning.called


@pytest.mark.asyncio
async def test_context_manager_enter(
    patched_platform_factory, patched_config_get, mock_ipsdk_client
):
    """Test async context manager __aenter__ returns self"""
    client = PlatformClient()

    result = await client.__aenter__()

    assert result is client


@pytest.mark.asyncio
async def test_context_manager_exit_with_close(
    patched_platform_factory, patched_config_get, mock_ipsdk_client
):
    """Test async context manager __aexit__ calls close when available"""
    mock_ipsdk_client.close = AsyncMock()

    client = PlatformClient()
    await client.__aexit__(None, None, None)

    mock_ipsdk_client.close.assert_called_once()


@pytest.mark.asyncio
async def test_context_manager_exit_without_close(
    patched_platform_factory, patched_config_get
):
    """Test async context manager __aexit__ handles missing close method"""
    # Create a client without close method
    mock_client_no_close = AsyncMock(spec=[])  # Empty spec means no methods
    with patch("itential_mcp.platform.client.ipsdk.platform_factory") as factory_mock:
        factory_mock.return_value = mock_client_no_close

        client = PlatformClient()
        # Should complete without error when close() doesn't exist
        await client.__aexit__(None, None, None)


@pytest.mark.asyncio
async def test_context_manager_exit_with_exception(
    patched_platform_factory, patched_config_get, mock_ipsdk_client
):
    """Test async context manager __aexit__ with exception info"""
    mock_ipsdk_client.close = AsyncMock()

    client = PlatformClient()

    # Simulate exiting with exception
    try:
        raise ValueError("test exception")
    except ValueError:
        import sys

        await client.__aexit__(*sys.exc_info())

    # Should still call close even with exception
    mock_ipsdk_client.close.assert_called_once()


@pytest.mark.asyncio
async def test_context_manager_full_workflow(
    patched_platform_factory, patched_config_get, mock_ipsdk_client
):
    """Test full context manager workflow"""
    mock_ipsdk_client.close = AsyncMock()

    async with PlatformClient() as client:
        assert client is not None
        assert client.client is mock_ipsdk_client

    # Verify close was called
    mock_ipsdk_client.close.assert_called_once()


@pytest.mark.asyncio
async def test_make_response(
    patched_platform_factory, patched_config_get, mock_ipsdk_client
):
    """Test _make_response wraps ipsdk Response correctly"""
    from ipsdk.connection import Response as IpsdkResponse
    from itential_mcp.platform.response import Response

    mock_ipsdk_response = MagicMock(spec=IpsdkResponse)

    client = PlatformClient()
    result = await client._make_response(mock_ipsdk_response)

    assert isinstance(result, Response)
    assert result.response is mock_ipsdk_response


@pytest.mark.asyncio
async def test_send_request_success(
    patched_platform_factory, patched_config_get, mock_ipsdk_client
):
    """Test send_request makes correct call and wraps response"""
    from ipsdk.connection import Response as IpsdkResponse

    mock_ipsdk_response = MagicMock(spec=IpsdkResponse)
    mock_ipsdk_client._send_request = AsyncMock(return_value=mock_ipsdk_response)

    client = PlatformClient()
    result = await client.send_request(
        method="GET", path="/test", params={"key": "value"}, json={"data": "test"}
    )

    # Verify the underlying client method was called correctly
    mock_ipsdk_client._send_request.assert_called_once_with(
        "GET", "/test", {"key": "value"}, {"data": "test"}
    )

    # Verify response was wrapped
    assert result.response is mock_ipsdk_response


@pytest.mark.asyncio
async def test_send_request_error_handling(
    patched_platform_factory, patched_config_get, mock_ipsdk_client
):
    """Test send_request raises ItentialMcpException on error"""
    from itential_mcp.core.exceptions import ItentialMcpException

    mock_ipsdk_client._send_request = AsyncMock(
        side_effect=Exception("Connection failed")
    )

    client = PlatformClient()

    with pytest.raises(ItentialMcpException) as exc_info:
        await client.send_request(method="GET", path="/test")

    assert "Connection failed" in str(exc_info.value)


@pytest.mark.asyncio
async def test_get_method(
    patched_platform_factory, patched_config_get, mock_ipsdk_client
):
    """Test get method calls send_request with correct parameters"""
    from ipsdk.connection import Response as IpsdkResponse

    mock_ipsdk_response = MagicMock(spec=IpsdkResponse)
    mock_ipsdk_client._send_request = AsyncMock(return_value=mock_ipsdk_response)

    client = PlatformClient()
    result = await client.get("/api/test", params={"filter": "active"})

    mock_ipsdk_client._send_request.assert_called_once_with(
        "GET", "/api/test", {"filter": "active"}, None
    )
    assert result.response is mock_ipsdk_response


@pytest.mark.asyncio
async def test_get_method_no_params(
    patched_platform_factory, patched_config_get, mock_ipsdk_client
):
    """Test get method without query parameters"""
    from ipsdk.connection import Response as IpsdkResponse

    mock_ipsdk_response = MagicMock(spec=IpsdkResponse)
    mock_ipsdk_client._send_request = AsyncMock(return_value=mock_ipsdk_response)

    client = PlatformClient()
    result = await client.get("/api/test")

    mock_ipsdk_client._send_request.assert_called_once_with(
        "GET", "/api/test", None, None
    )
    assert result.response is mock_ipsdk_response


@pytest.mark.asyncio
async def test_post_method(
    patched_platform_factory, patched_config_get, mock_ipsdk_client
):
    """Test post method calls send_request with correct parameters"""
    from ipsdk.connection import Response as IpsdkResponse

    mock_ipsdk_response = MagicMock(spec=IpsdkResponse)
    mock_ipsdk_client._send_request = AsyncMock(return_value=mock_ipsdk_response)

    client = PlatformClient()
    result = await client.post(
        "/api/create", params={"validate": "true"}, json={"name": "test"}
    )

    mock_ipsdk_client._send_request.assert_called_once_with(
        "POST", "/api/create", {"validate": "true"}, {"name": "test"}
    )
    assert result.response is mock_ipsdk_response


@pytest.mark.asyncio
async def test_post_method_minimal(
    patched_platform_factory, patched_config_get, mock_ipsdk_client
):
    """Test post method with only path parameter"""
    from ipsdk.connection import Response as IpsdkResponse

    mock_ipsdk_response = MagicMock(spec=IpsdkResponse)
    mock_ipsdk_client._send_request = AsyncMock(return_value=mock_ipsdk_response)

    client = PlatformClient()
    result = await client.post("/api/action")

    mock_ipsdk_client._send_request.assert_called_once_with(
        "POST", "/api/action", None, None
    )
    assert result.response is mock_ipsdk_response


@pytest.mark.asyncio
async def test_put_method(
    patched_platform_factory, patched_config_get, mock_ipsdk_client
):
    """Test put method calls send_request with correct parameters"""
    from ipsdk.connection import Response as IpsdkResponse

    mock_ipsdk_response = MagicMock(spec=IpsdkResponse)
    mock_ipsdk_client._send_request = AsyncMock(return_value=mock_ipsdk_response)

    client = PlatformClient()
    result = await client.put("/api/update/123", json={"status": "active"})

    mock_ipsdk_client._send_request.assert_called_once_with(
        "PUT", "/api/update/123", None, {"status": "active"}
    )
    assert result.response is mock_ipsdk_response


@pytest.mark.asyncio
async def test_put_method_with_params(
    patched_platform_factory, patched_config_get, mock_ipsdk_client
):
    """Test put method with both params and json"""
    from ipsdk.connection import Response as IpsdkResponse

    mock_ipsdk_response = MagicMock(spec=IpsdkResponse)
    mock_ipsdk_client._send_request = AsyncMock(return_value=mock_ipsdk_response)

    client = PlatformClient()
    result = await client.put(
        "/api/update/123", params={"force": "true"}, json={"name": "updated"}
    )

    mock_ipsdk_client._send_request.assert_called_once_with(
        "PUT", "/api/update/123", {"force": "true"}, {"name": "updated"}
    )
    assert result.response is mock_ipsdk_response


@pytest.mark.asyncio
async def test_delete_method(
    patched_platform_factory, patched_config_get, mock_ipsdk_client
):
    """Test delete method calls send_request with correct parameters"""
    from ipsdk.connection import Response as IpsdkResponse

    mock_ipsdk_response = MagicMock(spec=IpsdkResponse)
    mock_ipsdk_client._send_request = AsyncMock(return_value=mock_ipsdk_response)

    client = PlatformClient()
    result = await client.delete("/api/delete/123", params={"cascade": "true"})

    mock_ipsdk_client._send_request.assert_called_once_with(
        "DELETE", "/api/delete/123", {"cascade": "true"}, None
    )
    assert result.response is mock_ipsdk_response


@pytest.mark.asyncio
async def test_delete_method_no_params(
    patched_platform_factory, patched_config_get, mock_ipsdk_client
):
    """Test delete method without query parameters"""
    from ipsdk.connection import Response as IpsdkResponse

    mock_ipsdk_response = MagicMock(spec=IpsdkResponse)
    mock_ipsdk_client._send_request = AsyncMock(return_value=mock_ipsdk_response)

    client = PlatformClient()
    result = await client.delete("/api/delete/123")

    mock_ipsdk_client._send_request.assert_called_once_with(
        "DELETE", "/api/delete/123", None, None
    )
    assert result.response is mock_ipsdk_response


@pytest.mark.asyncio
async def test_http_methods_error_propagation(
    patched_platform_factory, patched_config_get, mock_ipsdk_client
):
    """Test that all HTTP methods properly propagate exceptions"""
    from itential_mcp.core.exceptions import ItentialMcpException

    mock_ipsdk_client._send_request = AsyncMock(side_effect=Exception("Network error"))

    client = PlatformClient()

    # Test GET
    with pytest.raises(ItentialMcpException):
        await client.get("/test")

    # Test POST
    with pytest.raises(ItentialMcpException):
        await client.post("/test")

    # Test PUT
    with pytest.raises(ItentialMcpException):
        await client.put("/test")

    # Test DELETE
    with pytest.raises(ItentialMcpException):
        await client.delete("/test")


def test_init_client_with_disable_verify_warning(mock_config_with_disable_verify):
    """Test that initializing client with disable_verify logs a security warning"""
    with patch("itential_mcp.platform.client.config.get") as config_mock:
        config_mock.return_value = mock_config_with_disable_verify

        with patch("itential_mcp.platform.client.ipsdk.platform_factory"):
            with patch("itential_mcp.platform.client.logging.warning") as mock_warning:
                _ = PlatformClient()  # Constructor triggers TLS checks

                # Verify warning was logged
                assert mock_warning.call_count >= 1
                warning_calls = [call[0][0] for call in mock_warning.call_args_list]
                assert any(
                    "TLS certificate verification is DISABLED" in str(call)
                    for call in warning_calls
                )


def test_init_client_with_disable_tls_warning(mock_config_with_disable_tls):
    """Test that initializing client with disable_tls logs a security warning"""
    with patch("itential_mcp.platform.client.config.get") as config_mock:
        config_mock.return_value = mock_config_with_disable_tls

        with patch("itential_mcp.platform.client.ipsdk.platform_factory"):
            with patch("itential_mcp.platform.client.logging.warning") as mock_warning:
                _ = PlatformClient()  # Constructor triggers TLS checks

                # Verify warning was logged
                assert mock_warning.call_count >= 1
                warning_calls = [call[0][0] for call in mock_warning.call_args_list]
                assert any("TLS is DISABLED" in str(call) for call in warning_calls)


@pytest.mark.asyncio
async def test_send_request_timeout_error(
    patched_platform_factory, patched_config_get, mock_ipsdk_client
):
    """Test that send_request raises TimeoutExceededError on asyncio.TimeoutError"""
    from itential_mcp.core.exceptions import TimeoutExceededError
    import asyncio

    # Make _send_request hang indefinitely
    async def slow_request(*args, **kwargs):
        await asyncio.sleep(100)

    mock_ipsdk_client._send_request = slow_request

    client = PlatformClient()

    # Use a very short timeout to trigger the error
    with pytest.raises(TimeoutExceededError) as exc_info:
        await client.send_request(method="GET", path="/test", timeout=0.001)

    assert "timed out" in str(exc_info.value)
