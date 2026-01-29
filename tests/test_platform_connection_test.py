# Copyright (c) 2025 Itential, Inc
# GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

"""Tests for connection test service."""

from __future__ import annotations

import asyncio
import socket
import ssl
from unittest.mock import AsyncMock, Mock, PropertyMock, patch

import pytest

from itential_mcp.config.models import Config
from itential_mcp.core.exceptions import AuthenticationException
from itential_mcp.platform.connection_test import (
    CheckResult,
    CheckStatus,
    ConnectionTestService,
)


@pytest.fixture
def mock_config():
    """Create mock configuration."""
    config = Mock(spec=Config)
    config.platform = Mock()
    config.platform.host = "platform.example.com"
    config.platform.port = 3000
    config.platform.disable_tls = False
    config.platform.disable_verify = False
    config.platform.user = "admin"
    config.platform.password = "password"
    config.platform.client_id = None
    config.platform.client_secret = None
    config.auth = Mock()
    config.auth.type = "oauth"
    return config


@pytest.fixture
def service(mock_config):
    """Create connection test service instance."""
    return ConnectionTestService(mock_config)


# Port Detection Tests


def test_get_actual_port_with_tls_enabled(mock_config):
    """Test port detection returns 443 when TLS is enabled and port is 0."""
    mock_config.platform.port = 0
    mock_config.platform.disable_tls = False
    service = ConnectionTestService(mock_config)

    assert service._port == 443


def test_get_actual_port_with_tls_disabled(mock_config):
    """Test port detection returns 80 when TLS is disabled and port is 0."""
    mock_config.platform.port = 0
    mock_config.platform.disable_tls = True
    service = ConnectionTestService(mock_config)

    assert service._port == 80


def test_get_actual_port_with_custom_port(mock_config):
    """Test port detection returns custom port when specified."""
    mock_config.platform.port = 8443
    service = ConnectionTestService(mock_config)

    assert service._port == 8443


# Authentication Type Detection Tests


def test_get_platform_auth_type_oauth(mock_config):
    """Test auth type detection identifies OAuth."""
    mock_config.platform.client_id = "client123"
    mock_config.platform.client_secret = "secret456"
    mock_config.platform.user = None
    mock_config.platform.password = None
    service = ConnectionTestService(mock_config)

    assert service._auth_type == "oauth"


def test_get_platform_auth_type_basic(mock_config):
    """Test auth type detection identifies basic auth."""
    mock_config.platform.client_id = None
    mock_config.platform.client_secret = None
    mock_config.platform.user = "admin"
    mock_config.platform.password = "password"
    service = ConnectionTestService(mock_config)

    assert service._auth_type == "basic"


def test_get_platform_auth_type_none(mock_config):
    """Test auth type detection identifies no auth."""
    mock_config.platform.client_id = None
    mock_config.platform.client_secret = None
    mock_config.platform.user = None
    mock_config.platform.password = None
    service = ConnectionTestService(mock_config)

    assert service._auth_type == "none"


# Configuration Tests


@pytest.mark.asyncio
async def test_check_configuration_success(service):
    """Test configuration check passes with valid config."""
    result = await service.check_configuration()

    assert result.name == "configuration"
    assert result.status == CheckStatus.PASSED
    assert "successfully" in result.message.lower()
    assert result.details is not None
    assert result.details["platform_host"] == "platform.example.com"
    assert result.details["platform_port"] == 3000
    assert result.details["auth_type"] == "basic"


@pytest.mark.asyncio
async def test_check_configuration_missing_host(mock_config):
    """Test configuration check fails with missing host."""
    mock_config.platform.host = None
    service = ConnectionTestService(mock_config)

    result = await service.check_configuration()

    assert result.status == CheckStatus.FAILED
    assert "host not configured" in result.message.lower()
    assert result.suggestion is not None
    assert "ITENTIAL_MCP_PLATFORM_HOST" in result.suggestion


@pytest.mark.asyncio
async def test_check_configuration_missing_auth_type(mock_config):
    """Test configuration check fails with missing auth type."""
    mock_config.auth.type = None
    service = ConnectionTestService(mock_config)

    result = await service.check_configuration()

    assert result.status == CheckStatus.FAILED
    assert "authentication type not configured" in result.message.lower()
    assert result.suggestion is not None


@pytest.mark.asyncio
async def test_check_configuration_exception():
    """Test configuration check handles generic exceptions."""
    # Create a config that will raise an exception during validation
    mock_config = Mock(spec=Config)
    mock_config.platform = Mock()
    mock_config.platform.host = "platform.example.com"
    mock_config.platform.port = 3000
    mock_config.platform.disable_tls = False
    mock_config.platform.disable_verify = False
    mock_config.platform.user = "admin"
    mock_config.platform.password = "password"
    mock_config.platform.client_id = None
    mock_config.platform.client_secret = None
    mock_config.auth = Mock()

    # Make auth.type raise an exception when accessed in a way that's not in __init__
    type(mock_config.auth).type = PropertyMock(side_effect=Exception("Config error"))

    service = ConnectionTestService(mock_config)
    result = await service.check_configuration()

    assert result.status == CheckStatus.FAILED
    assert "configuration error" in result.message.lower()
    assert result.error is not None


# DNS Tests


@pytest.mark.asyncio
async def test_check_dns_resolution_success(service):
    """Test DNS resolution succeeds."""
    with patch("socket.gethostbyname", return_value="192.168.1.100"):
        result = await service.check_dns_resolution()

    assert result.status == CheckStatus.PASSED
    assert "192.168.1.100" in result.message
    assert result.details["ip_address"] == "192.168.1.100"
    assert result.details["hostname"] == "platform.example.com"


@pytest.mark.asyncio
async def test_check_dns_resolution_failure(service):
    """Test DNS resolution fails gracefully."""
    with patch("socket.gethostbyname", side_effect=socket.gaierror):
        result = await service.check_dns_resolution()

    assert result.status == CheckStatus.FAILED
    assert "resolve" in result.message.lower()
    assert result.suggestion is not None
    assert "DNS server" in result.suggestion


@pytest.mark.asyncio
async def test_check_dns_resolution_generic_exception(service):
    """Test DNS resolution handles generic exceptions."""
    with patch("socket.gethostbyname", side_effect=Exception("Unexpected DNS error")):
        result = await service.check_dns_resolution()

    assert result.status == CheckStatus.FAILED
    assert "dns resolution error" in result.message.lower()
    assert result.error is not None


# TCP Tests


@pytest.mark.asyncio
async def test_check_tcp_connection_success(service):
    """Test TCP connection succeeds."""
    mock_sock = Mock()
    mock_sock.close = Mock()

    async def mock_connect(*args):
        pass

    with patch("socket.socket", return_value=mock_sock):
        with patch.object(
            asyncio.get_event_loop(), "run_in_executor", side_effect=mock_connect
        ):
            result = await service.check_tcp_connection()

    assert result.status == CheckStatus.PASSED
    assert "established" in result.message.lower()
    assert result.details["host"] == "platform.example.com"
    assert result.details["port"] == 3000
    mock_sock.close.assert_called_once()


@pytest.mark.asyncio
async def test_check_tcp_connection_refused(service):
    """Test TCP connection handles connection refused."""
    mock_sock = Mock()

    async def mock_connect_refused(*args):
        raise ConnectionRefusedError()

    with patch("socket.socket", return_value=mock_sock):
        with patch.object(
            asyncio.get_event_loop(),
            "run_in_executor",
            side_effect=mock_connect_refused,
        ):
            result = await service.check_tcp_connection()

    assert result.status == CheckStatus.FAILED
    assert "refused" in result.message.lower()
    assert result.suggestion is not None
    assert "platform is running" in result.suggestion.lower()


@pytest.mark.asyncio
async def test_check_tcp_connection_timeout(service):
    """Test TCP connection handles timeout."""
    mock_sock = Mock()

    async def mock_timeout(*args):
        raise socket.timeout()

    with patch("socket.socket", return_value=mock_sock):
        with patch.object(
            asyncio.get_event_loop(), "run_in_executor", side_effect=mock_timeout
        ):
            result = await service.check_tcp_connection()

    assert result.status == CheckStatus.FAILED
    assert "timeout" in result.message.lower()
    assert result.suggestion is not None


@pytest.mark.asyncio
async def test_check_tcp_connection_generic_exception(service):
    """Test TCP connection handles generic exceptions."""
    mock_sock = Mock()

    async def mock_error(*args):
        raise Exception("Unexpected network error")

    with patch("socket.socket", return_value=mock_sock):
        with patch.object(
            asyncio.get_event_loop(), "run_in_executor", side_effect=mock_error
        ):
            result = await service.check_tcp_connection()

    assert result.status == CheckStatus.FAILED
    assert "tcp connection error" in result.message.lower()
    assert result.error is not None


# TLS Tests


@pytest.mark.asyncio
async def test_check_tls_handshake_skipped_when_disabled(mock_config):
    """Test TLS check skipped when TLS disabled."""
    mock_config.platform.disable_tls = True
    service = ConnectionTestService(mock_config)

    result = await service.check_tls_handshake()

    assert result.status == CheckStatus.SKIPPED
    assert "disabled" in result.message.lower()


@pytest.mark.asyncio
async def test_check_tls_handshake_success(service):
    """Test TLS handshake succeeds."""
    mock_ssl_socket = Mock()
    mock_ssl_socket.cipher.return_value = ("TLS_AES_256_GCM_SHA384", "TLSv1.3", 256)
    mock_ssl_socket.version.return_value = "TLSv1.3"
    mock_ssl_socket.__enter__ = Mock(return_value=mock_ssl_socket)
    mock_ssl_socket.__exit__ = Mock(return_value=False)

    mock_socket = Mock()
    mock_socket.__enter__ = Mock(return_value=mock_socket)
    mock_socket.__exit__ = Mock(return_value=False)

    mock_context = Mock()
    mock_context.wrap_socket.return_value = mock_ssl_socket

    with (
        patch("ssl.create_default_context", return_value=mock_context),
        patch("socket.create_connection", return_value=mock_socket),
    ):
        result = await service.check_tls_handshake()

    assert result.status == CheckStatus.PASSED
    assert "successful" in result.message.lower()
    assert result.details["protocol"] == "TLSv1.3"


@pytest.mark.asyncio
async def test_check_tls_handshake_cert_verification_error(service):
    """Test TLS handshake handles certificate verification error."""
    with patch(
        "ssl.create_default_context",
        side_effect=ssl.SSLCertVerificationError("cert verify failed"),
    ):
        result = await service.check_tls_handshake()

    assert result.status == CheckStatus.FAILED
    assert "certificate verification failed" in result.message.lower()
    assert result.suggestion is not None
    assert "DISABLE_VERIFY" in result.suggestion


@pytest.mark.asyncio
async def test_check_tls_handshake_with_verify_disabled(mock_config):
    """Test TLS handshake with certificate verification disabled."""
    mock_config.platform.disable_verify = True
    service = ConnectionTestService(mock_config)

    mock_ssl_socket = Mock()
    mock_ssl_socket.cipher.return_value = ("TLS_AES_256_GCM_SHA384", "TLSv1.3", 256)
    mock_ssl_socket.version.return_value = "TLSv1.3"
    mock_ssl_socket.__enter__ = Mock(return_value=mock_ssl_socket)
    mock_ssl_socket.__exit__ = Mock(return_value=False)

    mock_socket = Mock()
    mock_socket.__enter__ = Mock(return_value=mock_socket)
    mock_socket.__exit__ = Mock(return_value=False)

    mock_context = Mock()
    mock_context.wrap_socket.return_value = mock_ssl_socket

    with (
        patch("ssl.create_default_context", return_value=mock_context),
        patch("socket.create_connection", return_value=mock_socket),
    ):
        result = await service.check_tls_handshake()

    assert result.status == CheckStatus.PASSED
    assert "successful" in result.message.lower()
    # Verify that certificate verification was disabled
    assert mock_context.check_hostname is False
    assert mock_context.verify_mode == ssl.CERT_NONE


@pytest.mark.asyncio
async def test_check_tls_handshake_generic_exception(service):
    """Test TLS handshake handles generic exceptions."""
    with patch(
        "ssl.create_default_context", side_effect=Exception("Unexpected SSL error")
    ):
        result = await service.check_tls_handshake()

    assert result.status == CheckStatus.FAILED
    assert "tls handshake error" in result.message.lower()
    assert result.error is not None


# Authentication Tests


@pytest.mark.asyncio
async def test_check_authentication_success(service):
    """Test authentication check succeeds."""
    mock_client = AsyncMock()
    mock_client.__aenter__.return_value = mock_client
    mock_client.__aexit__.return_value = None

    with patch(
        "itential_mcp.platform.client.PlatformClient",
        return_value=mock_client,
    ):
        result = await service.check_authentication()

    assert result.status == CheckStatus.PASSED
    assert "successful" in result.message.lower()
    assert result.details["auth_type"] == "basic"
    assert result.details["user"] == "admin"


@pytest.mark.asyncio
async def test_check_authentication_failure(service):
    """Test authentication check handles failure."""
    mock_client = AsyncMock()
    mock_client.__aenter__.side_effect = AuthenticationException("Invalid credentials")

    with patch(
        "itential_mcp.platform.client.PlatformClient",
        return_value=mock_client,
    ):
        result = await service.check_authentication()

    assert result.status == CheckStatus.FAILED
    assert "authentication failed" in result.message.lower()
    assert result.suggestion is not None
    assert "username and password" in result.suggestion.lower()


@pytest.mark.asyncio
async def test_check_authentication_generic_exception(service):
    """Test authentication check handles generic exceptions."""
    mock_client = AsyncMock()
    mock_client.__aenter__.side_effect = Exception("Unexpected auth error")

    with patch(
        "itential_mcp.platform.client.PlatformClient",
        return_value=mock_client,
    ):
        result = await service.check_authentication()

    assert result.status == CheckStatus.FAILED
    assert "authentication error" in result.message.lower()
    assert result.error is not None


# Health Tests


@pytest.mark.asyncio
async def test_check_platform_health_success(service):
    """Test platform health check succeeds."""
    mock_client = AsyncMock()
    mock_client.__aenter__.return_value = mock_client
    mock_client.__aexit__.return_value = None
    mock_client.health = AsyncMock()
    mock_client.health.get_status_health = AsyncMock(
        return_value={"status": "healthy", "platform": {"version": "2024.1.0"}}
    )

    with patch(
        "itential_mcp.platform.client.PlatformClient",
        return_value=mock_client,
    ):
        result = await service.check_platform_health()

    assert result.status == CheckStatus.PASSED
    assert "passed" in result.message.lower()
    assert result.details["platform_version"] == "2024.1.0"
    assert result.details["status"] == "healthy"


@pytest.mark.asyncio
async def test_check_platform_health_failure(service):
    """Test platform health check handles failure."""
    mock_client = AsyncMock()
    mock_client.__aenter__.return_value = mock_client
    mock_client.__aexit__.return_value = None
    mock_client.health = AsyncMock()
    mock_client.health.get_status_health = AsyncMock(side_effect=Exception("API error"))

    with patch(
        "itential_mcp.platform.client.PlatformClient",
        return_value=mock_client,
    ):
        result = await service.check_platform_health()

    assert result.status == CheckStatus.FAILED
    assert "failed" in result.message.lower()
    assert result.suggestion is not None


@pytest.mark.asyncio
async def test_check_platform_health_generic_exception(service):
    """Test platform health check handles generic exceptions."""
    mock_client = AsyncMock()
    mock_client.__aenter__.side_effect = Exception("Unexpected health error")

    with patch(
        "itential_mcp.platform.client.PlatformClient",
        return_value=mock_client,
    ):
        result = await service.check_platform_health()

    assert result.status == CheckStatus.FAILED
    assert "platform health check failed" in result.message.lower()
    assert result.error is not None


# API Access Tests


@pytest.mark.asyncio
async def test_check_api_access_success(service):
    """Test API access check succeeds."""
    mock_platform_client = AsyncMock()
    mock_platform_client.__aenter__.return_value = mock_platform_client
    mock_platform_client.__aexit__.return_value = None

    # Mock the underlying ipsdk client
    mock_ipsdk_client = AsyncMock()
    mock_response = Mock()
    mock_response.json.return_value = {"total": 5, "results": [{"id": "adapter1"}]}
    mock_ipsdk_client.get = AsyncMock(return_value=mock_response)
    mock_platform_client.client = mock_ipsdk_client

    with patch(
        "itential_mcp.platform.client.PlatformClient",
        return_value=mock_platform_client,
    ):
        result = await service.check_api_access()

    assert result.status == CheckStatus.PASSED
    assert "verified" in result.message.lower()
    assert result.details["api_call"] == "GET /health/adapters?limit=1"
    assert result.details["total_adapters"] == 5


@pytest.mark.asyncio
async def test_check_api_access_failure(service):
    """Test API access check handles failure."""
    mock_platform_client = AsyncMock()
    mock_platform_client.__aenter__.return_value = mock_platform_client
    mock_platform_client.__aexit__.return_value = None

    # Mock the underlying ipsdk client to raise an exception
    mock_ipsdk_client = AsyncMock()
    mock_ipsdk_client.get = AsyncMock(side_effect=Exception("Permission denied"))
    mock_platform_client.client = mock_ipsdk_client

    with patch(
        "itential_mcp.platform.client.PlatformClient",
        return_value=mock_platform_client,
    ):
        result = await service.check_api_access()

    assert result.status == CheckStatus.FAILED
    assert "failed" in result.message.lower()
    assert result.suggestion is not None


@pytest.mark.asyncio
async def test_check_api_access_generic_exception(service):
    """Test API access check handles generic exceptions."""
    mock_platform_client = AsyncMock()
    mock_platform_client.__aenter__.side_effect = Exception("Unexpected API error")

    with patch(
        "itential_mcp.platform.client.PlatformClient",
        return_value=mock_platform_client,
    ):
        result = await service.check_api_access()

    assert result.status == CheckStatus.FAILED
    assert "api access verification failed" in result.message.lower()
    assert result.error is not None


# Overall Test Runner


@pytest.mark.asyncio
async def test_run_all_checks_success(service):
    """Test running all checks successfully."""
    # Mock all checks to succeed
    mock_checks = [
        CheckResult(
            name="configuration",
            status=CheckStatus.PASSED,
            message="OK",
            duration_ms=10,
        ),
        CheckResult(
            name="dns", status=CheckStatus.PASSED, message="OK", duration_ms=10
        ),
        CheckResult(
            name="tcp", status=CheckStatus.PASSED, message="OK", duration_ms=10
        ),
        CheckResult(
            name="tls", status=CheckStatus.PASSED, message="OK", duration_ms=10
        ),
        CheckResult(
            name="authentication",
            status=CheckStatus.PASSED,
            message="OK",
            duration_ms=10,
            details={"user": "admin"},
        ),
        CheckResult(
            name="health",
            status=CheckStatus.PASSED,
            message="OK",
            duration_ms=10,
            details={"platform_version": "2024.1.0"},
        ),
        CheckResult(
            name="api_access", status=CheckStatus.PASSED, message="OK", duration_ms=10
        ),
    ]

    with (
        patch.object(service, "check_configuration", return_value=mock_checks[0]),
        patch.object(service, "check_dns_resolution", return_value=mock_checks[1]),
        patch.object(service, "check_tcp_connection", return_value=mock_checks[2]),
        patch.object(service, "check_tls_handshake", return_value=mock_checks[3]),
        patch.object(service, "check_authentication", return_value=mock_checks[4]),
        patch.object(service, "check_platform_health", return_value=mock_checks[5]),
        patch.object(service, "check_api_access", return_value=mock_checks[6]),
    ):
        result = await service.run_all_checks()

    assert result.success is True
    assert len(result.checks) == 7
    assert result.platform_version == "2024.1.0"
    assert result.authenticated_user == "admin"
    assert result.error is None


@pytest.mark.asyncio
async def test_run_all_checks_fails_fast(service):
    """Test that checks stop on first failure."""
    # Mock first check to succeed, second to fail
    config_check = CheckResult(
        name="configuration", status=CheckStatus.PASSED, message="OK", duration_ms=10
    )
    dns_check = CheckResult(
        name="dns",
        status=CheckStatus.FAILED,
        message="Failed",
        duration_ms=10,
        suggestion="Fix DNS",
    )

    with (
        patch.object(service, "check_configuration", return_value=config_check),
        patch.object(
            service, "check_dns_resolution", return_value=dns_check
        ) as mock_dns,
    ):
        result = await service.run_all_checks()

    assert result.success is False
    assert len(result.checks) == 2  # Only ran first two checks
    assert result.error == "Failed"
    mock_dns.assert_called_once()


@pytest.mark.asyncio
async def test_run_all_checks_timeout(service):
    """Test timeout handling."""

    async def slow_check():
        await asyncio.sleep(10)
        return CheckResult(
            name="slow", status=CheckStatus.PASSED, message="OK", duration_ms=10000
        )

    config_check = CheckResult(
        name="configuration", status=CheckStatus.PASSED, message="OK", duration_ms=10
    )

    with (
        patch.object(service, "check_configuration", return_value=config_check),
        patch.object(service, "check_dns_resolution", new=slow_check),
    ):
        result = await service.run_all_checks(timeout=1)

    assert result.success is False
    assert len(result.checks) == 2
    # The second check should have timed out
    assert result.checks[1].status == CheckStatus.FAILED
    assert "timed out" in result.checks[1].message.lower()


@pytest.mark.asyncio
async def test_run_all_checks_skips_tls_when_disabled(mock_config):
    """Test that TLS check is skipped when disabled."""
    mock_config.platform.disable_tls = True
    service = ConnectionTestService(mock_config)

    mock_checks = [
        CheckResult(
            name="configuration",
            status=CheckStatus.PASSED,
            message="OK",
            duration_ms=10,
        ),
        CheckResult(
            name="dns", status=CheckStatus.PASSED, message="OK", duration_ms=10
        ),
        CheckResult(
            name="tcp", status=CheckStatus.PASSED, message="OK", duration_ms=10
        ),
        CheckResult(
            name="tls",
            status=CheckStatus.SKIPPED,
            message="TLS disabled",
            duration_ms=0,
        ),
        CheckResult(
            name="authentication",
            status=CheckStatus.PASSED,
            message="OK",
            duration_ms=10,
        ),
        CheckResult(
            name="health", status=CheckStatus.PASSED, message="OK", duration_ms=10
        ),
        CheckResult(
            name="api_access", status=CheckStatus.PASSED, message="OK", duration_ms=10
        ),
    ]

    with (
        patch.object(service, "check_configuration", return_value=mock_checks[0]),
        patch.object(service, "check_dns_resolution", return_value=mock_checks[1]),
        patch.object(service, "check_tcp_connection", return_value=mock_checks[2]),
        patch.object(service, "check_tls_handshake", return_value=mock_checks[3]),
        patch.object(service, "check_authentication", return_value=mock_checks[4]),
        patch.object(service, "check_platform_health", return_value=mock_checks[5]),
        patch.object(service, "check_api_access", return_value=mock_checks[6]),
    ):
        result = await service.run_all_checks()

    assert result.success is True
    assert len(result.checks) == 7
    tls_check = next((c for c in result.checks if c.name == "tls"), None)
    assert tls_check is not None
    assert tls_check.status == CheckStatus.SKIPPED


@pytest.mark.asyncio
async def test_run_all_checks_handles_unexpected_error(service):
    """Test that unexpected errors are handled gracefully."""
    with patch.object(
        service, "check_configuration", side_effect=Exception("Unexpected error")
    ):
        result = await service.run_all_checks()

    assert result.success is False
    assert "Unexpected error" in result.error
