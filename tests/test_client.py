# Copyright (c) 2025 Itential, Inc
# GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

import pytest
import pathlib
import tempfile
import textwrap
from unittest.mock import AsyncMock, patch, MagicMock

import ipsdk

from itential_mcp.platform import PlatformClient
from itential_mcp.platform.client import _ErrorFormattingClient, _format_error_message
from ipsdk.http import HTTPMethod


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
            # Services receive the error-formatting wrapper, not the raw
            # ipsdk client, so that HTTP errors surface response bodies.
            assert isinstance(client.test_service.client, _ErrorFormattingClient)
            assert client.test_service.client._client is mock_ipsdk_client

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
        HTTPMethod.GET, "/test", {"key": "value"}, {"data": "test"}
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
        HTTPMethod.GET, "/api/test", {"filter": "active"}, None
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
        HTTPMethod.GET, "/api/test", None, None
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
        HTTPMethod.POST, "/api/create", {"validate": "true"}, {"name": "test"}
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
        HTTPMethod.POST, "/api/action", None, None
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
        HTTPMethod.PUT, "/api/update/123", None, {"status": "active"}
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
        HTTPMethod.PUT, "/api/update/123", {"force": "true"}, {"name": "updated"}
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
        HTTPMethod.DELETE, "/api/delete/123", {"cascade": "true"}, None
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
        HTTPMethod.DELETE, "/api/delete/123", None, None
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
async def test_send_request_includes_response_body(
    patched_platform_factory, patched_config_get, mock_ipsdk_client
):
    """Test that send_request includes the upstream response body text in
    the raised ItentialMcpException message when the underlying exception
    carries a `.response` attribute."""
    from itential_mcp.core.exceptions import ItentialMcpException

    mock_response = MagicMock()
    mock_response.text = '{"error": "invalid device_type"}'

    error = Exception("400 Bad Request")
    error.response = mock_response

    mock_ipsdk_client._send_request = AsyncMock(side_effect=error)

    client = PlatformClient()

    with pytest.raises(ItentialMcpException) as exc_info:
        await client.send_request(method="POST", path="/test")

    message = str(exc_info.value)
    assert "400 Bad Request" in message
    assert '{"error": "invalid device_type"}' in message


@pytest.mark.asyncio
async def test_send_request_truncates_long_response_body(
    patched_platform_factory, patched_config_get, mock_ipsdk_client
):
    """Test that an overly long response body is truncated to
    MAX_ERROR_BODY_LENGTH characters and suffixed with a truncation marker."""
    from itential_mcp.core.exceptions import ItentialMcpException
    from itential_mcp.platform.client import MAX_ERROR_BODY_LENGTH

    long_body = "x" * (MAX_ERROR_BODY_LENGTH + 500)

    mock_response = MagicMock()
    mock_response.text = long_body

    error = Exception("500 Server Error")
    error.response = mock_response

    mock_ipsdk_client._send_request = AsyncMock(side_effect=error)

    client = PlatformClient()

    with pytest.raises(ItentialMcpException) as exc_info:
        await client.send_request(method="GET", path="/test")

    message = str(exc_info.value)
    assert "... (truncated)" in message
    # Ensure the body portion embedded in the message was capped
    truncated_segment = message.split("response: ")[1]
    assert truncated_segment.startswith("x" * MAX_ERROR_BODY_LENGTH)
    assert truncated_segment == f"{'x' * MAX_ERROR_BODY_LENGTH}... (truncated)"


@pytest.mark.asyncio
async def test_send_request_without_response_falls_back_to_str(
    patched_platform_factory, patched_config_get, mock_ipsdk_client
):
    """Regression guard: when the underlying exception has no `.response`
    attribute (or it is None), send_request should still raise an
    ItentialMcpException with the plain string of the original exception,
    matching the pre-existing behavior."""
    from itential_mcp.core.exceptions import ItentialMcpException

    mock_ipsdk_client._send_request = AsyncMock(
        side_effect=Exception("Connection failed")
    )

    client = PlatformClient()

    with pytest.raises(ItentialMcpException) as exc_info:
        await client.send_request(method="GET", path="/test")

    message = str(exc_info.value)
    assert message == "Connection failed"
    assert "response:" not in message


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


def test_format_error_message_module_level_includes_response_body():
    """Test that the module-level _format_error_message helper includes the
    upstream response body when the exception carries a `.response`."""
    mock_response = MagicMock()
    mock_response.text = '{"error": "invalid device_type"}'

    error = Exception("400 Bad Request")
    error.response = mock_response

    message = _format_error_message(error)

    assert "400 Bad Request" in message
    assert '{"error": "invalid device_type"}' in message


def test_format_error_message_module_level_truncates_long_body():
    """Test that the module-level _format_error_message helper truncates an
    overly long response body."""
    from itential_mcp.platform.client import MAX_ERROR_BODY_LENGTH

    long_body = "x" * (MAX_ERROR_BODY_LENGTH + 500)

    mock_response = MagicMock()
    mock_response.text = long_body

    error = Exception("500 Server Error")
    error.response = mock_response

    message = _format_error_message(error)

    assert "... (truncated)" in message
    truncated_segment = message.split("response: ")[1]
    assert truncated_segment == f"{'x' * MAX_ERROR_BODY_LENGTH}... (truncated)"


def test_format_error_message_module_level_without_response_falls_back():
    """Test that the module-level _format_error_message helper falls back to
    str(exc) when there is no `.response` attribute."""
    error = Exception("Connection failed")

    message = _format_error_message(error)

    assert message == "Connection failed"
    assert "response:" not in message


def _make_http_status_error(body_text: str, message: str = "400 Bad Request"):
    """Build a real ipsdk.exceptions.HTTPStatusError with a mock response body."""
    mock_response = MagicMock()
    mock_response.text = body_text

    httpx_exc = MagicMock()
    httpx_exc.args = (message,)
    httpx_exc.response = mock_response
    httpx_exc.request = MagicMock()

    return ipsdk.exceptions.HTTPStatusError(httpx_exc)


@pytest.mark.asyncio
async def test_error_formatting_client_get_returns_raw_response_on_success():
    """Test that _ErrorFormattingClient.get returns the raw response object
    unchanged (same identity) on success."""
    raw_client = AsyncMock()
    sentinel_response = MagicMock()
    raw_client.get = AsyncMock(return_value=sentinel_response)

    wrapper = _ErrorFormattingClient(raw_client)
    result = await wrapper.get("/path", params={"a": 1})

    raw_client.get.assert_called_once_with("/path", params={"a": 1})
    assert result is sentinel_response


@pytest.mark.asyncio
async def test_error_formatting_client_post_returns_raw_response_on_success():
    """Test that _ErrorFormattingClient.post returns the raw response object
    unchanged (same identity) on success."""
    raw_client = AsyncMock()
    sentinel_response = MagicMock()
    raw_client.post = AsyncMock(return_value=sentinel_response)

    wrapper = _ErrorFormattingClient(raw_client)
    result = await wrapper.post("/path", params={"a": 1}, json={"b": 2})

    raw_client.post.assert_called_once_with("/path", params={"a": 1}, json={"b": 2})
    assert result is sentinel_response


@pytest.mark.asyncio
async def test_error_formatting_client_put_returns_raw_response_on_success():
    """Test that _ErrorFormattingClient.put returns the raw response object
    unchanged (same identity) on success."""
    raw_client = AsyncMock()
    sentinel_response = MagicMock()
    raw_client.put = AsyncMock(return_value=sentinel_response)

    wrapper = _ErrorFormattingClient(raw_client)
    result = await wrapper.put("/path", json={"b": 2})

    raw_client.put.assert_called_once_with("/path", params=None, json={"b": 2})
    assert result is sentinel_response


@pytest.mark.asyncio
async def test_error_formatting_client_delete_returns_raw_response_on_success():
    """Test that _ErrorFormattingClient.delete returns the raw response object
    unchanged (same identity) on success."""
    raw_client = AsyncMock()
    sentinel_response = MagicMock()
    raw_client.delete = AsyncMock(return_value=sentinel_response)

    wrapper = _ErrorFormattingClient(raw_client)
    result = await wrapper.delete("/path")

    raw_client.delete.assert_called_once_with("/path", params=None)
    assert result is sentinel_response


@pytest.mark.asyncio
async def test_error_formatting_client_get_reformats_http_status_error():
    """Test that _ErrorFormattingClient.get reformats HTTPStatusError to
    include the upstream response body."""
    from itential_mcp.core.exceptions import ItentialMcpException

    raw_client = AsyncMock()
    raw_client.get = AsyncMock(
        side_effect=_make_http_status_error('{"error": "not found"}', "404 Not Found")
    )

    wrapper = _ErrorFormattingClient(raw_client)

    with pytest.raises(ItentialMcpException) as exc_info:
        await wrapper.get("/missing")

    message = str(exc_info.value)
    assert "404 Not Found" in message
    assert '{"error": "not found"}' in message


@pytest.mark.asyncio
async def test_error_formatting_client_post_reformats_http_status_error():
    """Test that _ErrorFormattingClient.post reformats HTTPStatusError to
    include the upstream response body."""
    from itential_mcp.core.exceptions import ItentialMcpException

    raw_client = AsyncMock()
    raw_client.post = AsyncMock(
        side_effect=_make_http_status_error(
            '{"error": "invalid device_type"}', "400 Bad Request"
        )
    )

    wrapper = _ErrorFormattingClient(raw_client)

    with pytest.raises(ItentialMcpException) as exc_info:
        await wrapper.post("/create", json={"foo": "bar"})

    message = str(exc_info.value)
    assert "400 Bad Request" in message
    assert '{"error": "invalid device_type"}' in message


@pytest.mark.asyncio
async def test_error_formatting_client_put_reformats_http_status_error():
    """Test that _ErrorFormattingClient.put reformats HTTPStatusError to
    include the upstream response body."""
    from itential_mcp.core.exceptions import ItentialMcpException

    raw_client = AsyncMock()
    raw_client.put = AsyncMock(
        side_effect=_make_http_status_error('{"error": "conflict"}', "409 Conflict")
    )

    wrapper = _ErrorFormattingClient(raw_client)

    with pytest.raises(ItentialMcpException):
        await wrapper.put("/update/1", json={"foo": "bar"})


@pytest.mark.asyncio
async def test_error_formatting_client_delete_reformats_http_status_error():
    """Test that _ErrorFormattingClient.delete reformats HTTPStatusError to
    include the upstream response body."""
    from itential_mcp.core.exceptions import ItentialMcpException

    raw_client = AsyncMock()
    raw_client.delete = AsyncMock(
        side_effect=_make_http_status_error('{"error": "forbidden"}', "403 Forbidden")
    )

    wrapper = _ErrorFormattingClient(raw_client)

    with pytest.raises(ItentialMcpException) as exc_info:
        await wrapper.delete("/resource/1")

    message = str(exc_info.value)
    assert "403 Forbidden" in message
    assert '{"error": "forbidden"}' in message


@pytest.mark.asyncio
async def test_error_formatting_client_propagates_non_http_status_exceptions():
    """Test that exceptions other than ipsdk.exceptions.HTTPStatusError are
    NOT caught or modified by _ErrorFormattingClient -- they propagate
    completely unchanged."""
    raw_client = AsyncMock()
    raw_client.get = AsyncMock(side_effect=ValueError("boom"))

    wrapper = _ErrorFormattingClient(raw_client)

    with pytest.raises(ValueError, match="boom"):
        await wrapper.get("/path")


@pytest.mark.asyncio
async def test_error_formatting_client_propagates_ipsdk_request_error():
    """Test that ipsdk.exceptions.RequestError (network-level errors) is not
    caught by _ErrorFormattingClient and propagates unchanged."""
    httpx_exc = MagicMock()
    httpx_exc.args = ("Connection refused",)
    httpx_exc.request = MagicMock()

    request_error = ipsdk.exceptions.RequestError(httpx_exc)

    raw_client = AsyncMock()
    raw_client.post = AsyncMock(side_effect=request_error)

    wrapper = _ErrorFormattingClient(raw_client)

    with pytest.raises(ipsdk.exceptions.RequestError):
        await wrapper.post("/path", json={})


def test_error_formatting_client_getattr_delegates_to_wrapped_client():
    """Test that __getattr__ forwards arbitrary attribute access to the
    wrapped raw client (needed so ServiceBase._paginate and similar helpers
    keep working)."""
    raw_client = MagicMock()
    raw_client.some_arbitrary_attribute = "sentinel-value"

    wrapper = _ErrorFormattingClient(raw_client)

    assert wrapper.some_arbitrary_attribute == "sentinel-value"


@pytest.mark.asyncio
async def test_real_service_surfaces_response_body_through_wrapper():
    """Load-bearing test: construct _ErrorFormattingClient around a mock raw
    ipsdk client whose `post` raises a real ipsdk.exceptions.HTTPStatusError
    with a response body, hand the wrapper to an actual
    operations_manager.Service instance, and call a real service method.

    This proves the fix reaches real tool call paths -- service plugins call
    get/post/put/delete directly on the raw ipsdk client, bypassing
    PlatformClient.send_request()/_format_error_message() entirely. Prior
    test coverage always used AsyncMock() clients directly, which bypassed
    the wrapper and gave false confidence.
    """
    from itential_mcp.core.exceptions import ItentialMcpException
    from itential_mcp.platform.services import operations_manager

    raw_client = AsyncMock()
    raw_client.post = AsyncMock(
        side_effect=_make_http_status_error(
            '{"error": "invalid input for workflow trigger"}',
            "400 Bad Request",
        )
    )

    wrapper = _ErrorFormattingClient(raw_client)
    service = operations_manager.Service(wrapper)

    with pytest.raises(ItentialMcpException) as exc_info:
        await service.start_workflow("my-workflow-route", {"device": "router1"})

    message = str(exc_info.value)
    assert "400 Bad Request" in message
    assert '{"error": "invalid input for workflow trigger"}' in message


@pytest.mark.asyncio
async def test_init_plugins_wires_error_formatting_client_into_services(
    patched_platform_factory, patched_config_get, mock_ipsdk_client
):
    """Test that _init_plugins passes an _ErrorFormattingClient (not the raw
    ipsdk client) to service constructors, and that HTTP errors raised from
    calls made through a loaded service surface the response body."""
    from itential_mcp.core.exceptions import ItentialMcpException

    with tempfile.TemporaryDirectory() as temp_dir:
        services_dir = pathlib.Path(temp_dir) / "services"
        services_dir.mkdir()

        service_file = services_dir / "probe_service.py"
        service_file.write_text(
            textwrap.dedent("""
            class Service:
                def __init__(self, client):
                    self.client = client
                    self.name = "probe_service"

                async def do_get(self, path):
                    return await self.client.get(path)
        """)
        )

        with patch("itential_mcp.platform.client.pathlib.Path.resolve") as resolve_mock:
            resolve_mock.return_value.parent = pathlib.Path(temp_dir)

            client = PlatformClient()

            # The service should have been handed the wrapper, not the raw client
            assert isinstance(client.probe_service.client, _ErrorFormattingClient)
            assert client.probe_service.client._client is mock_ipsdk_client

            mock_ipsdk_client.get = AsyncMock(
                side_effect=_make_http_status_error('{"error": "gone"}', "410 Gone")
            )

            with pytest.raises(ItentialMcpException) as exc_info:
                await client.probe_service.do_get("/resource")

            message = str(exc_info.value)
            assert "410 Gone" in message
            assert '{"error": "gone"}' in message


@pytest.mark.asyncio
async def test_error_formatting_client_preserves_http_status():
    """The HTTP status code of an HTTPStatusError is kept on http_status so
    callers can branch on it (e.g. treat 404 as empty)."""
    from itential_mcp.core.exceptions import ItentialMcpException

    exc = _make_http_status_error("not found", "404 Not Found")
    exc.response.status_code = 404
    raw_client = AsyncMock()
    raw_client.get = AsyncMock(side_effect=exc)

    wrapper = _ErrorFormattingClient(raw_client)

    with pytest.raises(ItentialMcpException) as exc_info:
        await wrapper.get("/missing")

    assert exc_info.value.http_status == 404


@pytest.mark.asyncio
async def test_error_formatting_client_patch_returns_raw_response_on_success():
    """Test that _ErrorFormattingClient.patch returns the raw response object
    unchanged (same identity) on success."""
    raw_client = AsyncMock()
    sentinel_response = MagicMock()
    raw_client.patch = AsyncMock(return_value=sentinel_response)

    wrapper = _ErrorFormattingClient(raw_client)
    result = await wrapper.patch("/path", json={"b": 2})

    raw_client.patch.assert_called_once_with("/path", params=None, json={"b": 2})
    assert result is sentinel_response


@pytest.mark.asyncio
async def test_error_formatting_client_patch_preserves_http_status():
    """A PATCH HTTPStatusError is reformatted and keeps its status code."""
    from itential_mcp.core.exceptions import ItentialMcpException

    exc = _make_http_status_error('{"error": "must be pending"}', "409 Conflict")
    exc.response.status_code = 409
    raw_client = AsyncMock()
    raw_client.patch = AsyncMock(side_effect=exc)

    wrapper = _ErrorFormattingClient(raw_client)

    with pytest.raises(ItentialMcpException) as exc_info:
        await wrapper.patch("/resource/1", json={"a": 1})

    assert exc_info.value.http_status == 409
    assert "409 Conflict" in str(exc_info.value)
    assert '{"error": "must be pending"}' in str(exc_info.value)


@pytest.mark.asyncio
@pytest.mark.parametrize(
    ("verb", "kwargs", "status"),
    [
        ("post", {"json": {"a": 1}}, 400),
        ("put", {"json": {"a": 1}}, 409),
        ("delete", {}, 403),
    ],
)
async def test_error_formatting_client_write_verbs_preserve_http_status(
    verb, kwargs, status
):
    """post/put/delete keep the HTTP status code on the raised exception."""
    from itential_mcp.core.exceptions import ItentialMcpException

    exc = _make_http_status_error("boom", f"{status} Error")
    exc.response.status_code = status
    raw_client = AsyncMock()
    setattr(raw_client, verb, AsyncMock(side_effect=exc))

    wrapper = _ErrorFormattingClient(raw_client)

    with pytest.raises(ItentialMcpException) as exc_info:
        await getattr(wrapper, verb)("/resource", **kwargs)

    assert exc_info.value.http_status == status
