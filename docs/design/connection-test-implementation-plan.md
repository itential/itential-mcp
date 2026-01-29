# Implementation Plan: Connection Test Feature

**Design Spec:** [connection-test-feature.md](connection-test-feature.md)
**Issue:** [#299](https://github.com/itential/itential-mcp/issues/299)
**Status:** Ready for Implementation
**Created:** 2026-01-27
**Last Updated:** 2026-01-27

## Overview

This document provides a detailed, phased implementation plan for the connection test feature. The implementation is broken into 4 phases, each building on the previous phase and delivering incremental value.

## Implementation Phases

| Phase | Focus | Deliverables | Effort |
|-------|-------|--------------|--------|
| 1 | Core Foundation | Connection test service, basic checks | 2-3 days |
| 2 | CLI Integration | test-connection command, human output | 1-2 days |
| 3 | Enhanced Output | JSON format, detailed diagnostics, suggestions | 1-2 days |
| 4 | Startup Integration | Startup testing, configuration options | 1 day |

**Total Estimated Effort:** 5-8 days

## Phase 1: Core Foundation

**Objective:** Build the core connection test service with basic connectivity checks.

**Success Criteria:**
- ✓ Connection test service can perform all 7 checks
- ✓ Each check returns structured results
- ✓ Fail-fast behavior works correctly
- ✓ Unit test coverage > 95%
- ✓ No regression in existing functionality

### Tasks

#### Task 1.1: Create Connection Test Service Module
**File:** `src/itential_mcp/platform/connection_test.py` (NEW)
**Estimated Time:** 4-6 hours

**Implementation Steps:**

1. Create the file with copyright header and module docstring
2. Define data models:
   ```python
   from dataclasses import dataclass
   from enum import Enum
   from typing import Any

   class CheckStatus(str, Enum):
       """Status of a connection check."""
       PASSED = "passed"
       FAILED = "failed"
       SKIPPED = "skipped"
       WARNING = "warning"

   @dataclass
   class CheckResult:
       """Result of a single connection check."""
       name: str
       status: CheckStatus
       message: str
       duration_ms: float
       details: dict[str, Any] | None = None
       error: Exception | None = None
       suggestion: str | None = None

   @dataclass
   class ConnectionTestResult:
       """Overall result of connection testing."""
       success: bool
       duration_ms: float
       checks: list[CheckResult]
       platform_version: str | None = None
       authenticated_user: str | None = None
       error: str | None = None
   ```

3. Create `ConnectionTestService` class skeleton:
   ```python
   class ConnectionTestService:
       """Service for testing platform connectivity."""

       def __init__(self, config: Config):
           """Initialize connection test service.

           Args:
               config: Application configuration.
           """
           self.config = config
           self._logger = logging.getLogger(__name__)
   ```

4. Implement utility methods:
   ```python
   def _measure_time(self, func):
       """Decorator to measure check execution time."""

   def _create_check_result(
       self,
       name: str,
       status: CheckStatus,
       message: str,
       duration_ms: float,
       **kwargs
   ) -> CheckResult:
       """Create a CheckResult instance."""
   ```

**Acceptance Criteria:**
- [ ] Module created with proper structure
- [ ] Data models defined with type hints
- [ ] Class skeleton implemented
- [ ] Code passes `make check`

---

#### Task 1.2: Implement Configuration Check
**File:** `src/itential_mcp/platform/connection_test.py`
**Estimated Time:** 1 hour

```python
async def check_configuration(self) -> CheckResult:
    """Validate configuration is loaded and valid.

    Returns:
        CheckResult: Configuration check result.
    """
    start = time.perf_counter()

    try:
        # Validate required fields
        if not self.config.platform.host:
            return self._create_check_result(
                name="configuration",
                status=CheckStatus.FAILED,
                message="Platform host not configured",
                duration_ms=(time.perf_counter() - start) * 1000,
                suggestion="Set ITENTIAL_MCP_PLATFORM_HOST environment variable"
            )

        # Validate auth configuration
        if not self.config.auth.type:
            return self._create_check_result(
                name="configuration",
                status=CheckStatus.FAILED,
                message="Authentication type not configured",
                duration_ms=(time.perf_counter() - start) * 1000,
                suggestion="Set ITENTIAL_MCP_AUTH_TYPE environment variable"
            )

        # Additional validation checks...

        return self._create_check_result(
            name="configuration",
            status=CheckStatus.PASSED,
            message="Configuration loaded successfully",
            duration_ms=(time.perf_counter() - start) * 1000,
            details={
                "platform_host": self.config.platform.host,
                "platform_port": self.config.platform.port,
                "auth_type": self.config.auth.type,
                "tls_enabled": not self.config.platform.disable_tls,
            }
        )

    except Exception as e:
        return self._create_check_result(
            name="configuration",
            status=CheckStatus.FAILED,
            message=f"Configuration error: {e}",
            duration_ms=(time.perf_counter() - start) * 1000,
            error=e
        )
```

**Acceptance Criteria:**
- [ ] Validates all required configuration fields
- [ ] Returns detailed configuration info
- [ ] Handles missing config gracefully
- [ ] Unit tests cover success and failure cases

---

#### Task 1.3: Implement DNS Resolution Check
**File:** `src/itential_mcp/platform/connection_test.py`
**Estimated Time:** 1 hour

```python
async def check_dns_resolution(self) -> CheckResult:
    """Verify hostname resolves to IP address.

    Returns:
        CheckResult: DNS resolution check result.
    """
    import socket

    start = time.perf_counter()
    hostname = self.config.platform.host

    try:
        # Attempt DNS resolution
        ip_address = socket.gethostbyname(hostname)

        return self._create_check_result(
            name="dns",
            status=CheckStatus.PASSED,
            message=f"{hostname} -> {ip_address}",
            duration_ms=(time.perf_counter() - start) * 1000,
            details={
                "hostname": hostname,
                "ip_address": ip_address,
            }
        )

    except socket.gaierror as e:
        return self._create_check_result(
            name="dns",
            status=CheckStatus.FAILED,
            message=f"Could not resolve hostname '{hostname}'",
            duration_ms=(time.perf_counter() - start) * 1000,
            error=e,
            suggestion=(
                f"1. Check hostname spelling: {hostname}\n"
                "2. Verify DNS server is reachable\n"
                "3. Try using IP address directly for testing"
            )
        )

    except Exception as e:
        return self._create_check_result(
            name="dns",
            status=CheckStatus.FAILED,
            message=f"DNS resolution error: {e}",
            duration_ms=(time.perf_counter() - start) * 1000,
            error=e
        )
```

**Acceptance Criteria:**
- [ ] Resolves hostname to IP address
- [ ] Handles resolution failures gracefully
- [ ] Provides helpful error suggestions
- [ ] Unit tests with mocked socket calls

---

#### Task 1.4: Implement TCP Connection Check
**File:** `src/itential_mcp/platform/connection_test.py`
**Estimated Time:** 1-2 hours

```python
async def check_tcp_connection(self) -> CheckResult:
    """Verify TCP connection can be established.

    Returns:
        CheckResult: TCP connection check result.
    """
    import socket
    import asyncio

    start = time.perf_counter()
    host = self.config.platform.host
    port = self.config.platform.port

    try:
        # Attempt TCP connection with timeout
        loop = asyncio.get_event_loop()
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(5.0)

        await loop.run_in_executor(
            None,
            sock.connect,
            (host, port)
        )

        sock.close()

        return self._create_check_result(
            name="tcp",
            status=CheckStatus.PASSED,
            message=f"TCP connection established ({host}:{port})",
            duration_ms=(time.perf_counter() - start) * 1000,
            details={
                "host": host,
                "port": port,
            }
        )

    except socket.timeout:
        return self._create_check_result(
            name="tcp",
            status=CheckStatus.FAILED,
            message=f"Connection timeout to {host}:{port}",
            duration_ms=(time.perf_counter() - start) * 1000,
            suggestion=(
                f"1. Verify platform is running at {host}:{port}\n"
                "2. Check network connectivity\n"
                "3. Verify firewall rules allow connection\n"
                "4. Increase timeout if network is slow"
            )
        )

    except ConnectionRefusedError:
        return self._create_check_result(
            name="tcp",
            status=CheckStatus.FAILED,
            message=f"Connection refused to {host}:{port}",
            duration_ms=(time.perf_counter() - start) * 1000,
            suggestion=(
                f"1. Verify platform is running at {host}:{port}\n"
                "2. Check port number is correct\n"
                "3. Verify platform is listening on this address"
            )
        )

    except Exception as e:
        return self._create_check_result(
            name="tcp",
            status=CheckStatus.FAILED,
            message=f"TCP connection error: {e}",
            duration_ms=(time.perf_counter() - start) * 1000,
            error=e
        )
```

**Acceptance Criteria:**
- [ ] Establishes TCP connection
- [ ] Handles timeout appropriately
- [ ] Handles connection refused
- [ ] Provides helpful suggestions
- [ ] Unit tests with mocked socket

---

#### Task 1.5: Implement TLS Handshake Check
**File:** `src/itential_mcp/platform/connection_test.py`
**Estimated Time:** 2-3 hours

```python
async def check_tls_handshake(self) -> CheckResult:
    """Verify TLS handshake succeeds (if TLS enabled).

    Returns:
        CheckResult: TLS handshake check result.
    """
    start = time.perf_counter()

    # Skip if TLS is disabled
    if self.config.platform.disable_tls:
        return self._create_check_result(
            name="tls",
            status=CheckStatus.SKIPPED,
            message="TLS disabled in configuration",
            duration_ms=(time.perf_counter() - start) * 1000
        )

    import ssl
    import socket

    host = self.config.platform.host
    port = self.config.platform.port

    try:
        # Create SSL context
        context = ssl.create_default_context()

        if self.config.platform.disable_verify:
            context.check_hostname = False
            context.verify_mode = ssl.CERT_NONE

        # Perform TLS handshake
        with socket.create_connection((host, port), timeout=5.0) as sock:
            with context.wrap_socket(sock, server_hostname=host) as ssock:
                cipher = ssock.cipher()
                version = ssock.version()

                return self._create_check_result(
                    name="tls",
                    status=CheckStatus.PASSED,
                    message="TLS handshake successful",
                    duration_ms=(time.perf_counter() - start) * 1000,
                    details={
                        "protocol": version,
                        "cipher": cipher[0] if cipher else None,
                    }
                )

    except ssl.SSLCertVerificationError as e:
        return self._create_check_result(
            name="tls",
            status=CheckStatus.FAILED,
            message="TLS certificate verification failed",
            duration_ms=(time.perf_counter() - start) * 1000,
            error=e,
            suggestion=(
                f"Certificate verification failed for {host}\n\n"
                "Options:\n"
                "1. Update hostname to match certificate CN\n"
                "2. Obtain valid certificate for this hostname\n"
                "3. Disable verification (not recommended):\n"
                "   ITENTIAL_MCP_PLATFORM_DISABLE_VERIFY=true"
            )
        )

    except Exception as e:
        return self._create_check_result(
            name="tls",
            status=CheckStatus.FAILED,
            message=f"TLS handshake error: {e}",
            duration_ms=(time.perf_counter() - start) * 1000,
            error=e
        )
```

**Acceptance Criteria:**
- [ ] Performs TLS handshake
- [ ] Reports TLS version and cipher
- [ ] Skips when TLS disabled
- [ ] Handles certificate errors gracefully
- [ ] Provides actionable suggestions
- [ ] Unit tests with mocked SSL

---

#### Task 1.6: Implement Authentication Check
**File:** `src/itential_mcp/platform/connection_test.py`
**Estimated Time:** 2-3 hours

```python
async def check_authentication(self) -> CheckResult:
    """Verify authentication succeeds.

    Returns:
        CheckResult: Authentication check result.
    """
    from itential_mcp.platform.client import PlatformClient
    from itential_mcp.core.exceptions import AuthenticationException

    start = time.perf_counter()

    try:
        # Create temporary client for auth test
        async with PlatformClient() as client:
            # Attempt to get current user info (validates auth)
            # This depends on ipsdk exposing user info endpoint
            # For now, we'll try a simple API call that requires auth

            # The mere fact that we can create the client and it doesn't
            # throw an auth error means auth is working

            auth_type = self.config.auth.type
            user = self.config.platform.user if hasattr(self.config.platform, "user") else None

            return self._create_check_result(
                name="authentication",
                status=CheckStatus.PASSED,
                message=f"Authentication successful ({auth_type})",
                duration_ms=(time.perf_counter() - start) * 1000,
                details={
                    "auth_type": auth_type,
                    "user": user,
                }
            )

    except AuthenticationException as e:
        return self._create_check_result(
            name="authentication",
            status=CheckStatus.FAILED,
            message="Authentication failed",
            duration_ms=(time.perf_counter() - start) * 1000,
            error=e,
            suggestion=(
                "Authentication failed. Please check:\n"
                "1. Username and password are correct\n"
                "2. User exists in Itential Platform\n"
                "3. User has API access permissions\n"
                "4. For OAuth, verify issuer and token configuration"
            )
        )

    except Exception as e:
        return self._create_check_result(
            name="authentication",
            status=CheckStatus.FAILED,
            message=f"Authentication error: {e}",
            duration_ms=(time.perf_counter() - start) * 1000,
            error=e
        )
```

**Acceptance Criteria:**
- [ ] Validates authentication
- [ ] Reports auth type and user
- [ ] Handles auth failures
- [ ] Provides helpful suggestions
- [ ] Unit tests with mocked client

---

#### Task 1.7: Implement Platform Health Check
**File:** `src/itential_mcp/platform/connection_test.py`
**Estimated Time:** 1 hour

```python
async def check_platform_health(self) -> CheckResult:
    """Verify platform health endpoint responds.

    Returns:
        CheckResult: Platform health check result.
    """
    from itential_mcp.platform.client import PlatformClient

    start = time.perf_counter()

    try:
        async with PlatformClient() as client:
            # Call health endpoint
            health = await client.health.get_status_health()

            platform_version = health.get("platform", {}).get("version")

            return self._create_check_result(
                name="health",
                status=CheckStatus.PASSED,
                message="Platform health check passed",
                duration_ms=(time.perf_counter() - start) * 1000,
                details={
                    "platform_version": platform_version,
                    "status": health.get("status"),
                }
            )

    except Exception as e:
        return self._create_check_result(
            name="health",
            status=CheckStatus.FAILED,
            message=f"Platform health check failed: {e}",
            duration_ms=(time.perf_counter() - start) * 1000,
            error=e,
            suggestion=(
                "Platform health check failed. Possible causes:\n"
                "1. Platform is starting up (wait and retry)\n"
                "2. Platform is experiencing issues (check logs)\n"
                "3. Health endpoint is not available"
            )
        )
```

**Acceptance Criteria:**
- [ ] Calls health endpoint
- [ ] Extracts platform version
- [ ] Handles health check failures
- [ ] Unit tests with mocked client

---

#### Task 1.8: Implement API Access Check
**File:** `src/itential_mcp/platform/connection_test.py`
**Estimated Time:** 1 hour

```python
async def check_api_access(self) -> CheckResult:
    """Verify API access with simple query.

    Returns:
        CheckResult: API access check result.
    """
    from itential_mcp.platform.client import PlatformClient

    start = time.perf_counter()

    try:
        async with PlatformClient() as client:
            # Make a simple API call that requires permissions
            # Use adapters list with limit=1 for minimal overhead
            adapters = await client.adapters.get_adapters(limit=1)

            return self._create_check_result(
                name="api_access",
                status=CheckStatus.PASSED,
                message="API access verified",
                duration_ms=(time.perf_counter() - start) * 1000,
                details={
                    "api_call": "GET /adapters?limit=1",
                    "response_count": len(adapters.get("results", [])),
                }
            )

    except Exception as e:
        return self._create_check_result(
            name="api_access",
            status=CheckStatus.FAILED,
            message=f"API access verification failed: {e}",
            duration_ms=(time.perf_counter() - start) * 1000,
            error=e,
            suggestion=(
                "API access verification failed. Possible causes:\n"
                "1. User lacks required permissions\n"
                "2. API endpoint is unavailable\n"
                "3. Request format is invalid"
            )
        )
```

**Acceptance Criteria:**
- [ ] Makes simple API call
- [ ] Verifies response is valid
- [ ] Handles API errors
- [ ] Unit tests with mocked client

---

#### Task 1.9: Implement Main Test Runner
**File:** `src/itential_mcp/platform/connection_test.py`
**Estimated Time:** 2 hours

```python
async def run_all_checks(self, timeout: int = 30) -> ConnectionTestResult:
    """Run all connection checks in sequence.

    Args:
        timeout: Maximum time for all checks in seconds.

    Returns:
        ConnectionTestResult: Overall test results.
    """
    import asyncio

    overall_start = time.perf_counter()
    checks: list[CheckResult] = []

    try:
        # Run checks in order, fail-fast on failures
        check_methods = [
            self.check_configuration,
            self.check_dns_resolution,
            self.check_tcp_connection,
            self.check_tls_handshake,
            self.check_authentication,
            self.check_platform_health,
            self.check_api_access,
        ]

        for check_method in check_methods:
            try:
                # Run with timeout
                result = await asyncio.wait_for(
                    check_method(),
                    timeout=timeout
                )
                checks.append(result)

                # Fail fast - stop on first failure
                if result.status == CheckStatus.FAILED:
                    break

            except asyncio.TimeoutError:
                checks.append(CheckResult(
                    name=check_method.__name__.replace("check_", ""),
                    status=CheckStatus.FAILED,
                    message="Check timed out",
                    duration_ms=timeout * 1000,
                    suggestion="Increase timeout or check network latency"
                ))
                break

        # Determine overall success
        success = all(
            check.status in (CheckStatus.PASSED, CheckStatus.SKIPPED)
            for check in checks
        )

        # Extract metadata from successful checks
        platform_version = None
        authenticated_user = None

        for check in checks:
            if check.name == "health" and check.status == CheckStatus.PASSED:
                platform_version = check.details.get("platform_version")
            if check.name == "authentication" and check.status == CheckStatus.PASSED:
                authenticated_user = check.details.get("user")

        duration_ms = (time.perf_counter() - overall_start) * 1000

        return ConnectionTestResult(
            success=success,
            duration_ms=duration_ms,
            checks=checks,
            platform_version=platform_version,
            authenticated_user=authenticated_user,
            error=None if success else checks[-1].message
        )

    except Exception as e:
        duration_ms = (time.perf_counter() - overall_start) * 1000
        self._logger.exception("Unexpected error during connection test")

        return ConnectionTestResult(
            success=False,
            duration_ms=duration_ms,
            checks=checks,
            error=f"Unexpected error: {e}"
        )
```

**Acceptance Criteria:**
- [ ] Runs all checks in sequence
- [ ] Implements fail-fast behavior
- [ ] Handles timeouts properly
- [ ] Extracts metadata from results
- [ ] Unit tests cover all code paths

---

#### Task 1.10: Write Unit Tests
**File:** `tests/test_platform_connection_test.py` (NEW)
**Estimated Time:** 4-6 hours

Create comprehensive unit tests for all functionality:

```python
import pytest
from unittest.mock import Mock, AsyncMock, patch
from itential_mcp.platform.connection_test import (
    ConnectionTestService,
    CheckStatus,
    CheckResult,
    ConnectionTestResult,
)
from itential_mcp.config.models import Config

@pytest.fixture
def mock_config():
    """Create mock configuration."""
    config = Mock(spec=Config)
    config.platform.host = "platform.example.com"
    config.platform.port = 3000
    config.platform.disable_tls = False
    config.platform.disable_verify = False
    config.auth.type = "oauth"
    config.platform.user = "admin"
    return config

@pytest.fixture
def service(mock_config):
    """Create connection test service instance."""
    return ConnectionTestService(mock_config)

# Configuration Tests
@pytest.mark.asyncio
async def test_check_configuration_success(service):
    """Test configuration check passes with valid config."""
    result = await service.check_configuration()

    assert result.name == "configuration"
    assert result.status == CheckStatus.PASSED
    assert "successfully" in result.message.lower()
    assert result.details is not None

@pytest.mark.asyncio
async def test_check_configuration_missing_host(mock_config):
    """Test configuration check fails with missing host."""
    mock_config.platform.host = None
    service = ConnectionTestService(mock_config)

    result = await service.check_configuration()

    assert result.status == CheckStatus.FAILED
    assert "host not configured" in result.message.lower()
    assert result.suggestion is not None

# DNS Tests
@pytest.mark.asyncio
async def test_check_dns_resolution_success(service):
    """Test DNS resolution succeeds."""
    with patch("socket.gethostbyname", return_value="192.168.1.100"):
        result = await service.check_dns_resolution()

    assert result.status == CheckStatus.PASSED
    assert "192.168.1.100" in result.message
    assert result.details["ip_address"] == "192.168.1.100"

@pytest.mark.asyncio
async def test_check_dns_resolution_failure(service):
    """Test DNS resolution fails gracefully."""
    import socket
    with patch("socket.gethostbyname", side_effect=socket.gaierror):
        result = await service.check_dns_resolution()

    assert result.status == CheckStatus.FAILED
    assert "resolve" in result.message.lower()
    assert result.suggestion is not None

# TCP Tests
@pytest.mark.asyncio
async def test_check_tcp_connection_success(service):
    """Test TCP connection succeeds."""
    mock_sock = Mock()
    with patch("socket.socket", return_value=mock_sock):
        result = await service.check_tcp_connection()

    assert result.status == CheckStatus.PASSED
    assert "established" in result.message.lower()
    mock_sock.close.assert_called_once()

@pytest.mark.asyncio
async def test_check_tcp_connection_refused(service):
    """Test TCP connection handles connection refused."""
    mock_sock = Mock()
    mock_sock.connect.side_effect = ConnectionRefusedError()

    with patch("socket.socket", return_value=mock_sock):
        result = await service.check_tcp_connection()

    assert result.status == CheckStatus.FAILED
    assert "refused" in result.message.lower()
    assert result.suggestion is not None

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
    # Mock SSL context and socket
    with patch("ssl.create_default_context"), \
         patch("socket.create_connection"):
        result = await service.check_tls_handshake()

    assert result.status == CheckStatus.PASSED
    assert "successful" in result.message.lower()

# Authentication Tests
@pytest.mark.asyncio
async def test_check_authentication_success(service):
    """Test authentication check succeeds."""
    mock_client = AsyncMock()

    with patch("itential_mcp.platform.client.PlatformClient", return_value=mock_client):
        result = await service.check_authentication()

    assert result.status == CheckStatus.PASSED
    assert "successful" in result.message.lower()

# Health Tests
@pytest.mark.asyncio
async def test_check_platform_health_success(service):
    """Test platform health check succeeds."""
    mock_client = AsyncMock()
    mock_client.health.get_status_health.return_value = {
        "status": "healthy",
        "platform": {"version": "2024.1.0"}
    }

    with patch("itential_mcp.platform.client.PlatformClient", return_value=mock_client):
        result = await service.check_platform_health()

    assert result.status == CheckStatus.PASSED
    assert result.details["platform_version"] == "2024.1.0"

# API Access Tests
@pytest.mark.asyncio
async def test_check_api_access_success(service):
    """Test API access check succeeds."""
    mock_client = AsyncMock()
    mock_client.adapters.get_adapters.return_value = {
        "results": [{"id": "adapter1"}]
    }

    with patch("itential_mcp.platform.client.PlatformClient", return_value=mock_client):
        result = await service.check_api_access()

    assert result.status == CheckStatus.PASSED
    assert "verified" in result.message.lower()

# Overall Test Runner
@pytest.mark.asyncio
async def test_run_all_checks_success(service):
    """Test running all checks successfully."""
    # Mock all checks to succeed
    with patch.object(service, "check_configuration", return_value=CheckResult(
        name="config", status=CheckStatus.PASSED, message="OK", duration_ms=10
    )), \
    patch.object(service, "check_dns_resolution", return_value=CheckResult(
        name="dns", status=CheckStatus.PASSED, message="OK", duration_ms=10
    )), \
    patch.object(service, "check_tcp_connection", return_value=CheckResult(
        name="tcp", status=CheckStatus.PASSED, message="OK", duration_ms=10
    )), \
    patch.object(service, "check_tls_handshake", return_value=CheckResult(
        name="tls", status=CheckStatus.PASSED, message="OK", duration_ms=10
    )), \
    patch.object(service, "check_authentication", return_value=CheckResult(
        name="auth", status=CheckStatus.PASSED, message="OK", duration_ms=10
    )), \
    patch.object(service, "check_platform_health", return_value=CheckResult(
        name="health", status=CheckStatus.PASSED, message="OK", duration_ms=10,
        details={"platform_version": "2024.1.0"}
    )), \
    patch.object(service, "check_api_access", return_value=CheckResult(
        name="api", status=CheckStatus.PASSED, message="OK", duration_ms=10
    )):
        result = await service.run_all_checks()

    assert result.success is True
    assert len(result.checks) == 7
    assert result.platform_version == "2024.1.0"

@pytest.mark.asyncio
async def test_run_all_checks_fails_fast(service):
    """Test that checks stop on first failure."""
    # Mock first check to succeed, second to fail
    with patch.object(service, "check_configuration", return_value=CheckResult(
        name="config", status=CheckStatus.PASSED, message="OK", duration_ms=10
    )), \
    patch.object(service, "check_dns_resolution", return_value=CheckResult(
        name="dns", status=CheckStatus.FAILED, message="Failed", duration_ms=10
    )) as mock_dns:
        result = await service.run_all_checks()

    assert result.success is False
    assert len(result.checks) == 2  # Only ran first two checks
    mock_dns.assert_called_once()

@pytest.mark.asyncio
async def test_run_all_checks_timeout(service):
    """Test timeout handling."""
    async def slow_check():
        await asyncio.sleep(100)
        return CheckResult(name="slow", status=CheckStatus.PASSED, message="OK", duration_ms=100000)

    with patch.object(service, "check_configuration", return_value=CheckResult(
        name="config", status=CheckStatus.PASSED, message="OK", duration_ms=10
    )), \
    patch.object(service, "check_dns_resolution", side_effect=slow_check):
        result = await service.run_all_checks(timeout=1)

    assert result.success is False
    assert any("timeout" in check.message.lower() for check in result.checks)
```

**Additional Test Files:**
- Test all error paths
- Test timeout behavior
- Test with different config combinations
- Test with different auth types

**Acceptance Criteria:**
- [ ] Test coverage > 95%
- [ ] All success paths tested
- [ ] All failure paths tested
- [ ] Edge cases covered
- [ ] Tests pass with `make test`

---

### Phase 1 Deliverables Checklist

- [ ] `src/itential_mcp/platform/connection_test.py` created with all checks
- [ ] All 7 checks implemented and working
- [ ] Unit tests written with >95% coverage
- [ ] All tests passing (`make test`)
- [ ] Code passes linting (`make check`)
- [ ] Code formatted (`make format`)
- [ ] Documentation comments complete
- [ ] Type hints on all functions
- [ ] No regression in existing tests

---

## Phase 2: CLI Integration

**Objective:** Add `test-connection` CLI command with human-readable output.

**Success Criteria:**
- ✓ CLI command works with basic output
- ✓ Exit codes correct (0=success, 1=failure)
- ✓ Human-readable output is clear and helpful
- ✓ Integration tests pass
- ✓ Documentation updated

### Tasks

#### Task 2.1: Add CLI Command Parser
**File:** `src/itential_mcp/runtime/parser.py`
**Estimated Time:** 1 hour

Add test-connection subcommand to argument parser:

```python
def _add_test_connection_parser(subparsers):
    """Add test-connection command parser.

    Args:
        subparsers: Subparser collection.
    """
    parser = subparsers.add_parser(
        "test-connection",
        help="Test connection to Itential Platform",
        description=(
            "Test connection to Itential Platform by performing a series of "
            "connectivity checks. Useful for validating configuration and "
            "troubleshooting connection issues."
        ),
    )

    parser.add_argument(
        "--config",
        type=str,
        help="Path to configuration file",
    )

    parser.add_argument(
        "--timeout",
        type=int,
        default=30,
        help="Maximum time for test in seconds (default: 30)",
    )

    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Show detailed diagnostic information",
    )

    parser.add_argument(
        "--format",
        type=str,
        choices=["human", "json"],
        default="human",
        help="Output format (default: human)",
    )

    parser.add_argument(
        "--quiet",
        action="store_true",
        help="Suppress progress messages (JSON output only)",
    )

    return parser
```

Update main parser creation:

```python
def parse_args(args: list[str] | None = None) -> argparse.Namespace:
    """Parse command-line arguments.

    Args:
        args: Arguments to parse (defaults to sys.argv).

    Returns:
        Parsed arguments namespace.
    """
    parser = argparse.ArgumentParser(...)
    subparsers = parser.add_subparsers(dest="command", required=True)

    # Existing parsers
    _add_run_parser(subparsers)
    _add_version_parser(subparsers)
    # ... other parsers ...

    # Add new parser
    _add_test_connection_parser(subparsers)

    return parser.parse_args(args)
```

**Acceptance Criteria:**
- [ ] Parser added with all arguments
- [ ] Help text is clear and useful
- [ ] Parser integrates with existing CLI
- [ ] Unit tests for parser

---

#### Task 2.2: Create CLI Command Handler
**File:** `src/itential_mcp/runtime/commands.py`
**Estimated Time:** 2-3 hours

```python
async def test_connection(
    *,
    config_file: str | None = None,
    format: str = "human",
    verbose: bool = False,
    timeout: int = 30,
    quiet: bool = False,
) -> int:
    """Test connection to Itential Platform.

    Args:
        config_file: Path to configuration file.
        format: Output format (human or json).
        verbose: Show detailed diagnostic information.
        timeout: Maximum time for test in seconds.
        quiet: Suppress progress messages.

    Returns:
        int: Exit code (0=success, 1=failure).
    """
    from itential_mcp import config
    from itential_mcp.platform.connection_test import ConnectionTestService
    from itential_mcp.cli.terminal import print_success, print_error, print_info
    import sys
    import json

    # Load configuration
    try:
        if config_file:
            os.environ["ITENTIAL_MCP_CONFIG_FILE"] = config_file

        cfg = config.get()
    except Exception as e:
        print_error(f"Failed to load configuration: {e}")
        return 1

    # Create service
    service = ConnectionTestService(cfg)

    # Run checks
    if not quiet and format == "human":
        print_info("Testing connection to Itential Platform...")
        print()

    try:
        result = await service.run_all_checks(timeout=timeout)
    except Exception as e:
        print_error(f"Connection test failed with unexpected error: {e}")
        return 1

    # Output results
    if format == "json":
        _output_json(result)
    else:
        _output_human(result, verbose=verbose)

    return 0 if result.success else 1


def _output_human(result: ConnectionTestResult, verbose: bool = False) -> None:
    """Output results in human-readable format.

    Args:
        result: Test results.
        verbose: Show detailed information.
    """
    from itential_mcp.cli.terminal import (
        print_success,
        print_error,
        print_info,
        Colors,
    )

    # Print check results
    for check in result.checks:
        if check.status == CheckStatus.PASSED:
            symbol = "✓"
            color = Colors.GREEN
        elif check.status == CheckStatus.FAILED:
            symbol = "✗"
            color = Colors.RED
        elif check.status == CheckStatus.SKIPPED:
            symbol = "○"
            color = Colors.YELLOW
        else:  # WARNING
            symbol = "⚠"
            color = Colors.YELLOW

        print(f"{color}{symbol}{Colors.RESET} {check.message}")

        # Show details in verbose mode
        if verbose and check.details:
            for key, value in check.details.items():
                print(f"  {key}: {value}")

        # Show suggestions for failures
        if check.status == CheckStatus.FAILED and check.suggestion:
            print()
            print(f"{Colors.YELLOW}Suggestion:{Colors.RESET}")
            for line in check.suggestion.split("\n"):
                print(f"  {line}")
            print()

    print()

    # Print summary
    if result.success:
        print_success("Connection test: SUCCESS")
        if result.platform_version:
            print(f"Platform version: {result.platform_version}")
        if result.authenticated_user:
            print(f"Authenticated as: {result.authenticated_user}")
        print(f"Response time: {result.duration_ms / 1000:.1f}s")
    else:
        print_error("Connection test: FAILED")
        if result.error:
            print(f"Error: {result.error}")


def _output_json(result: ConnectionTestResult) -> None:
    """Output results in JSON format.

    Args:
        result: Test results.
    """
    import json
    from dataclasses import asdict

    # Convert to dict
    data = {
        "success": result.success,
        "duration_ms": result.duration_ms,
        "checks": [
            {
                "name": check.name,
                "status": check.status,
                "message": check.message,
                "duration_ms": check.duration_ms,
                "details": check.details,
                "suggestion": check.suggestion,
            }
            for check in result.checks
        ],
    }

    if result.platform_version:
        data["platform_version"] = result.platform_version
    if result.authenticated_user:
        data["authenticated_user"] = result.authenticated_user
    if result.error:
        data["error"] = result.error

    print(json.dumps(data, indent=2))
```

**Acceptance Criteria:**
- [ ] Command executes successfully
- [ ] Human output is clear and colorful
- [ ] JSON output is valid
- [ ] Exit codes are correct
- [ ] Error handling works properly

---

#### Task 2.3: Register Command Handler
**File:** `src/itential_mcp/runtime/handlers.py`
**Estimated Time:** 30 minutes

```python
def get_command_handler(command: str):
    """Get handler function for command.

    Args:
        command: Command name.

    Returns:
        Handler function.

    Raises:
        ValueError: If command is not recognized.
    """
    from .commands import (
        run,
        version,
        list_tools,
        list_tags,
        call_tool,
        test_connection,  # NEW
    )

    handlers = {
        "run": run,
        "version": version,
        "tools": list_tools,
        "tags": list_tags,
        "call": call_tool,
        "test-connection": test_connection,  # NEW
    }

    handler = handlers.get(command)
    if not handler:
        raise ValueError(f"Unknown command: {command}")

    return handler
```

**Acceptance Criteria:**
- [ ] Handler registered
- [ ] Command dispatching works
- [ ] Unit tests updated

---

#### Task 2.4: Add Terminal Utilities (if needed)
**File:** `src/itential_mcp/cli/terminal.py`
**Estimated Time:** 1 hour

Add any missing terminal utility functions:

```python
class Colors:
    """ANSI color codes."""
    RED = "\033[91m"
    GREEN = "\033[92m"
    YELLOW = "\033[93m"
    BLUE = "\033[94m"
    RESET = "\033[0m"
    BOLD = "\033[1m"


def print_success(message: str) -> None:
    """Print success message in green."""
    print(f"{Colors.GREEN}{message}{Colors.RESET}")


def print_error(message: str) -> None:
    """Print error message in red."""
    print(f"{Colors.RED}{message}{Colors.RESET}")


def print_warning(message: str) -> None:
    """Print warning message in yellow."""
    print(f"{Colors.YELLOW}{message}{Colors.RESET}")


def print_info(message: str) -> None:
    """Print info message in blue."""
    print(f"{Colors.BLUE}{message}{Colors.RESET}")
```

**Acceptance Criteria:**
- [ ] Terminal utilities available
- [ ] Colors work in terminal
- [ ] Functions are reusable

---

#### Task 2.5: Write Integration Tests
**File:** `tests/test_runtime_test_connection.py` (NEW)
**Estimated Time:** 2-3 hours

```python
import pytest
from unittest.mock import Mock, AsyncMock, patch
from itential_mcp.runtime.commands import test_connection
from itential_mcp.platform.connection_test import (
    ConnectionTestResult,
    CheckResult,
    CheckStatus,
)

@pytest.mark.asyncio
async def test_test_connection_command_success():
    """Test test-connection command with successful connection."""
    mock_result = ConnectionTestResult(
        success=True,
        duration_ms=1234,
        checks=[
            CheckResult(
                name="config",
                status=CheckStatus.PASSED,
                message="OK",
                duration_ms=10
            )
        ],
        platform_version="2024.1.0",
        authenticated_user="admin",
    )

    with patch("itential_mcp.platform.connection_test.ConnectionTestService") as mock_service_class:
        mock_service = AsyncMock()
        mock_service.run_all_checks.return_value = mock_result
        mock_service_class.return_value = mock_service

        exit_code = await test_connection()

        assert exit_code == 0
        mock_service.run_all_checks.assert_called_once()

@pytest.mark.asyncio
async def test_test_connection_command_failure():
    """Test test-connection command with connection failure."""
    mock_result = ConnectionTestResult(
        success=False,
        duration_ms=1234,
        checks=[
            CheckResult(
                name="config",
                status=CheckStatus.FAILED,
                message="Failed",
                duration_ms=10,
                suggestion="Fix config"
            )
        ],
        error="Connection failed",
    )

    with patch("itential_mcp.platform.connection_test.ConnectionTestService") as mock_service_class:
        mock_service = AsyncMock()
        mock_service.run_all_checks.return_value = mock_result
        mock_service_class.return_value = mock_service

        exit_code = await test_connection()

        assert exit_code == 1

@pytest.mark.asyncio
async def test_test_connection_json_output(capsys):
    """Test JSON output format."""
    mock_result = ConnectionTestResult(
        success=True,
        duration_ms=1234,
        checks=[],
    )

    with patch("itential_mcp.platform.connection_test.ConnectionTestService") as mock_service_class:
        mock_service = AsyncMock()
        mock_service.run_all_checks.return_value = mock_result
        mock_service_class.return_value = mock_service

        exit_code = await test_connection(format="json")

        captured = capsys.readouterr()
        import json
        output = json.loads(captured.out)

        assert output["success"] is True
        assert output["duration_ms"] == 1234
        assert exit_code == 0
```

**Acceptance Criteria:**
- [ ] Integration tests pass
- [ ] CLI command works end-to-end
- [ ] Both output formats tested
- [ ] Exit codes validated

---

### Phase 2 Deliverables Checklist

- [ ] CLI command implemented and working
- [ ] Human-readable output looks good
- [ ] Exit codes correct
- [ ] Integration tests passing
- [ ] Can run `itential-mcp test-connection` successfully
- [ ] Help text is clear (`itential-mcp test-connection --help`)

---

## Phase 3: Enhanced Output

**Objective:** Add JSON output format and enhanced diagnostic information.

**Success Criteria:**
- ✓ JSON output is valid and complete
- ✓ Verbose mode shows detailed info
- ✓ Error messages include actionable suggestions
- ✓ Output is machine-parseable for CI/CD

### Tasks

#### Task 3.1: Enhance JSON Output
**File:** `src/itential_mcp/runtime/commands.py`
**Estimated Time:** 1 hour

The JSON output was already implemented in Phase 2, but now we'll enhance it:

```python
def _output_json(result: ConnectionTestResult) -> None:
    """Output results in JSON format.

    Args:
        result: Test results.
    """
    import json

    # Build comprehensive JSON output
    data = {
        "success": result.success,
        "duration_ms": round(result.duration_ms, 2),
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "checks": [],
    }

    # Add check results
    for check in result.checks:
        check_data = {
            "name": check.name,
            "status": check.status,
            "message": check.message,
            "duration_ms": round(check.duration_ms, 2),
        }

        if check.details:
            check_data["details"] = check.details

        if check.suggestion:
            check_data["suggestion"] = check.suggestion

        if check.error:
            check_data["error"] = {
                "type": type(check.error).__name__,
                "message": str(check.error),
            }

        data["checks"].append(check_data)

    # Add metadata
    if result.platform_version:
        data["platform_version"] = result.platform_version
    if result.authenticated_user:
        data["authenticated_user"] = result.authenticated_user
    if result.error:
        data["error"] = result.error

    # Add summary statistics
    data["summary"] = {
        "total_checks": len(result.checks),
        "passed": sum(1 for c in result.checks if c.status == CheckStatus.PASSED),
        "failed": sum(1 for c in result.checks if c.status == CheckStatus.FAILED),
        "skipped": sum(1 for c in result.checks if c.status == CheckStatus.SKIPPED),
        "warnings": sum(1 for c in result.checks if c.status == CheckStatus.WARNING),
    }

    print(json.dumps(data, indent=2))
```

**Acceptance Criteria:**
- [ ] JSON is valid and well-formatted
- [ ] All data included
- [ ] Timestamp added
- [ ] Summary statistics included
- [ ] Schema documented

---

#### Task 3.2: Add JSON Schema Documentation
**File:** `docs/connection-testing.md` (NEW)
**Estimated Time:** 1 hour

Create user documentation with JSON schema:

```markdown
# Connection Testing

## Overview

The `test-connection` command validates connectivity to Itential Platform...

## Usage

### Basic Test
\`\`\`bash
itential-mcp test-connection
\`\`\`

### JSON Output
\`\`\`bash
itential-mcp test-connection --format json
\`\`\`

### Verbose Output
\`\`\`bash
itential-mcp test-connection --verbose
\`\`\`

## JSON Output Schema

[Include schema from design spec]

## Examples

[Include examples from design spec]

## Troubleshooting

[Include common error scenarios and solutions]
```

**Acceptance Criteria:**
- [ ] Documentation complete
- [ ] Examples provided
- [ ] Schema documented
- [ ] Troubleshooting guide included

---

#### Task 3.3: Enhance Human Output
**File:** `src/itential_mcp/runtime/commands.py`
**Estimated Time:** 2 hours

Improve human-readable output with better formatting:

```python
def _output_human(result: ConnectionTestResult, verbose: bool = False) -> None:
    """Output results in human-readable format.

    Args:
        result: Test results.
        verbose: Show detailed information.
    """
    from itential_mcp.cli.terminal import (
        print_success,
        print_error,
        print_info,
        print_warning,
        Colors,
    )

    # Print header
    print()

    # Print check results with improved formatting
    for i, check in enumerate(result.checks, 1):
        # Status symbol and color
        if check.status == CheckStatus.PASSED:
            symbol = "✓"
            color = Colors.GREEN
        elif check.status == CheckStatus.FAILED:
            symbol = "✗"
            color = Colors.RED
        elif check.status == CheckStatus.SKIPPED:
            symbol = "○"
            color = Colors.YELLOW
        else:  # WARNING
            symbol = "⚠"
            color = Colors.YELLOW

        # Print check result
        print(f"{color}{symbol}{Colors.RESET} {check.message}")

        # Show timing in verbose mode
        if verbose:
            print(f"  {Colors.BLUE}Duration:{Colors.RESET} {check.duration_ms:.0f}ms")

        # Show details in verbose mode
        if verbose and check.details:
            print(f"  {Colors.BLUE}Details:{Colors.RESET}")
            for key, value in check.details.items():
                print(f"    • {key}: {value}")

        # Show error details in verbose mode
        if verbose and check.error:
            print(f"  {Colors.RED}Error:{Colors.RESET} {type(check.error).__name__}: {check.error}")

        # Show suggestions for failures
        if check.status == CheckStatus.FAILED and check.suggestion:
            print()
            print(f"  {Colors.YELLOW}💡 Suggestion:{Colors.RESET}")
            for line in check.suggestion.split("\n"):
                if line.strip():
                    print(f"     {line}")
            print()

    print()
    print("─" * 60)
    print()

    # Print summary
    if result.success:
        print(f"{Colors.GREEN}{Colors.BOLD}✓ Connection test: SUCCESS{Colors.RESET}")
        print()
        if result.platform_version:
            print(f"  Platform version: {Colors.BOLD}{result.platform_version}{Colors.RESET}")
        if result.authenticated_user:
            print(f"  Authenticated as: {Colors.BOLD}{result.authenticated_user}{Colors.RESET}")
        print(f"  Total duration: {Colors.BOLD}{result.duration_ms / 1000:.2f}s{Colors.RESET}")
    else:
        print(f"{Colors.RED}{Colors.BOLD}✗ Connection test: FAILED{Colors.RESET}")
        print()
        if result.error:
            print(f"  {Colors.RED}Error: {result.error}{Colors.RESET}")

    print()
```

**Acceptance Criteria:**
- [ ] Output is clear and well-formatted
- [ ] Colors enhance readability
- [ ] Verbose mode shows helpful details
- [ ] Error suggestions are prominent

---

#### Task 3.4: Add Progress Indicators
**File:** `src/itential_mcp/runtime/commands.py`
**Estimated Time:** 1-2 hours

Add real-time progress indicators (optional enhancement):

```python
async def test_connection(
    *,
    config_file: str | None = None,
    format: str = "human",
    verbose: bool = False,
    timeout: int = 30,
    quiet: bool = False,
) -> int:
    """Test connection to Itential Platform."""
    # ... existing code ...

    # Run checks with progress updates
    if not quiet and format == "human":
        print_info("Testing connection to Itential Platform...")
        print()

        # Show progress as checks run
        result = await _run_checks_with_progress(service, timeout)
    else:
        result = await service.run_all_checks(timeout=timeout)

    # ... rest of code ...


async def _run_checks_with_progress(
    service: ConnectionTestService,
    timeout: int
) -> ConnectionTestResult:
    """Run checks with live progress updates.

    Args:
        service: Connection test service.
        timeout: Timeout in seconds.

    Returns:
        Test results.
    """
    import sys
    from itential_mcp.cli.terminal import Colors

    check_names = [
        "Configuration",
        "DNS Resolution",
        "TCP Connection",
        "TLS Handshake",
        "Authentication",
        "Platform Health",
        "API Access",
    ]

    # Start checks
    start = time.perf_counter()
    checks = []

    for i, check_method in enumerate([
        service.check_configuration,
        service.check_dns_resolution,
        service.check_tcp_connection,
        service.check_tls_handshake,
        service.check_authentication,
        service.check_platform_health,
        service.check_api_access,
    ]):
        # Show progress
        sys.stdout.write(f"  [{i+1}/7] {check_names[i]}... ")
        sys.stdout.flush()

        # Run check
        check_result = await check_method()
        checks.append(check_result)

        # Show result
        if check_result.status == CheckStatus.PASSED:
            sys.stdout.write(f"{Colors.GREEN}✓{Colors.RESET}\n")
        elif check_result.status == CheckStatus.FAILED:
            sys.stdout.write(f"{Colors.RED}✗{Colors.RESET}\n")
            break  # Fail fast
        elif check_result.status == CheckStatus.SKIPPED:
            sys.stdout.write(f"{Colors.YELLOW}○{Colors.RESET}\n")
        else:
            sys.stdout.write(f"{Colors.YELLOW}⚠{Colors.RESET}\n")

        sys.stdout.flush()

    duration_ms = (time.perf_counter() - start) * 1000

    # Build result
    success = all(
        c.status in (CheckStatus.PASSED, CheckStatus.SKIPPED)
        for c in checks
    )

    # Extract metadata
    platform_version = None
    authenticated_user = None
    for check in checks:
        if check.name == "health" and check.details:
            platform_version = check.details.get("platform_version")
        if check.name == "authentication" and check.details:
            authenticated_user = check.details.get("user")

    return ConnectionTestResult(
        success=success,
        duration_ms=duration_ms,
        checks=checks,
        platform_version=platform_version,
        authenticated_user=authenticated_user,
        error=None if success else checks[-1].message
    )
```

**Acceptance Criteria:**
- [ ] Progress indicators work
- [ ] Real-time feedback provided
- [ ] Fail-fast behavior visible
- [ ] No progress in quiet mode

---

### Phase 3 Deliverables Checklist

- [ ] JSON output enhanced and complete
- [ ] JSON schema documented
- [ ] Human output improved with better formatting
- [ ] Verbose mode shows detailed info
- [ ] Progress indicators work (optional)
- [ ] Documentation updated
- [ ] Examples provided

---

## Phase 4: Startup Integration

**Objective:** Add optional connection testing during server startup.

**Success Criteria:**
- ✓ Startup testing works when enabled
- ✓ Server fails fast if connection test fails
- ✓ Configuration options documented
- ✓ Backward compatible (off by default)

### Tasks

#### Task 4.1: Add Configuration Options
**File:** `src/itential_mcp/config/models.py`
**Estimated Time:** 30 minutes

```python
@dataclass
class ServerConfig:
    """Server configuration."""

    # ... existing fields ...

    test_connection_on_startup: bool = False
    """Test platform connection during server startup."""

    startup_test_timeout: int = 30
    """Timeout for startup connection test in seconds."""
```

**File:** `src/itential_mcp/defaults.py`

```python
# Server defaults
ITENTIAL_MCP_SERVER_TEST_CONNECTION_ON_STARTUP = False
ITENTIAL_MCP_SERVER_STARTUP_TEST_TIMEOUT = 30
```

**Acceptance Criteria:**
- [ ] Config fields added
- [ ] Defaults defined
- [ ] Type hints correct
- [ ] Validation works

---

#### Task 4.2: Integrate with Server Startup
**File:** `src/itential_mcp/server/server.py`
**Estimated Time:** 2-3 hours

```python
class Server:
    """MCP server implementation."""

    # ... existing code ...

    async def _test_connection_on_startup(self) -> None:
        """Test platform connection during startup.

        Raises:
            ConnectionException: If connection test fails.
        """
        from itential_mcp.platform.connection_test import ConnectionTestService
        from itential_mcp.core.exceptions import ConnectionException

        logger = logging.getLogger(__name__)
        logger.info("Testing platform connection...")

        try:
            service = ConnectionTestService(self.config)
            result = await service.run_all_checks(
                timeout=self.config.server.startup_test_timeout
            )

            if result.success:
                logger.info("Connection test successful")
                if result.platform_version:
                    logger.info(f"Platform version: {result.platform_version}")
                if result.authenticated_user:
                    logger.info(f"Authenticated as: {result.authenticated_user}")
            else:
                logger.error("Connection test failed")
                for check in result.checks:
                    if check.status == CheckStatus.FAILED:
                        logger.error(f"  {check.name}: {check.message}")
                        if check.suggestion:
                            logger.info(f"  Suggestion: {check.suggestion}")

                raise ConnectionException(
                    f"Connection test failed: {result.error}",
                    details={
                        "checks": [
                            {
                                "name": c.name,
                                "status": c.status,
                                "message": c.message,
                            }
                            for c in result.checks
                        ]
                    }
                )

        except Exception as e:
            logger.exception("Connection test failed with unexpected error")
            raise ConnectionException(f"Connection test failed: {e}") from e

    async def run(self):
        """Run the MCP server.

        Raises:
            ConnectionException: If startup connection test fails.
        """
        # Test connection if enabled
        if self.config.server.test_connection_on_startup:
            await self._test_connection_on_startup()

        # Continue with normal startup
        logger.info(
            f"Starting MCP server (transport={self.config.server.transport}, "
            f"port={self.config.server.port})"
        )

        # ... existing startup code ...
```

**Acceptance Criteria:**
- [ ] Startup test runs when enabled
- [ ] Server fails fast on test failure
- [ ] Logging is clear and helpful
- [ ] Error messages are actionable

---

#### Task 4.3: Update Documentation
**File:** `docs/connection-testing.md`
**Estimated Time:** 1 hour

Add section on startup testing:

```markdown
## Startup Testing

You can configure the server to test the platform connection during startup.
This is useful for deployment validation and fail-fast behavior.

### Configuration

#### Environment Variables

\`\`\`bash
ITENTIAL_MCP_SERVER_TEST_CONNECTION_ON_STARTUP=true
ITENTIAL_MCP_SERVER_STARTUP_TEST_TIMEOUT=30
\`\`\`

#### Configuration File

\`\`\`toml
[server]
test_connection_on_startup = true
startup_test_timeout = 30
\`\`\`

### Docker/Kubernetes

When using containers, enable startup testing to fail fast if misconfigured:

\`\`\`yaml
apiVersion: v1
kind: Pod
metadata:
  name: itential-mcp
spec:
  containers:
  - name: itential-mcp
    image: itential-mcp:latest
    env:
    - name: ITENTIAL_MCP_SERVER_TEST_CONNECTION_ON_STARTUP
      value: "true"
    - name: ITENTIAL_MCP_SERVER_STARTUP_TEST_TIMEOUT
      value: "30"
    livenessProbe:
      httpGet:
        path: /status/livez
        port: 8000
      initialDelaySeconds: 35  # Account for connection test + startup
      periodSeconds: 10
\`\`\`

### Behavior

When startup testing is enabled:

1. Server loads configuration
2. Connection test runs automatically
3. If test succeeds, server starts normally
4. If test fails, server exits with error

This ensures the server only starts if it can connect to the platform.
```

**File:** `docs/README.md`

Add reference to connection testing:

```markdown
## Connection Testing

Test your platform connection before starting the server:

\`\`\`bash
itential-mcp test-connection
\`\`\`

See [Connection Testing](connection-testing.md) for details.
```

**Acceptance Criteria:**
- [ ] Startup testing documented
- [ ] Configuration examples provided
- [ ] Kubernetes example included
- [ ] Behavior explained clearly

---

#### Task 4.4: Write Integration Tests
**File:** `tests/test_server_startup_test.py` (NEW)
**Estimated Time:** 2 hours

```python
import pytest
from unittest.mock import Mock, AsyncMock, patch
from itential_mcp.server.server import Server
from itential_mcp.platform.connection_test import (
    ConnectionTestResult,
    CheckStatus,
)
from itential_mcp.core.exceptions import ConnectionException

@pytest.fixture
def mock_config():
    """Create mock configuration."""
    config = Mock()
    config.server.test_connection_on_startup = True
    config.server.startup_test_timeout = 30
    config.server.transport = "stdio"
    return config

@pytest.mark.asyncio
async def test_startup_test_success(mock_config):
    """Test successful startup connection test."""
    mock_result = ConnectionTestResult(
        success=True,
        duration_ms=1234,
        checks=[],
        platform_version="2024.1.0",
    )

    with patch("itential_mcp.platform.connection_test.ConnectionTestService") as mock_service_class, \
         patch.object(Server, "_Server__init_server__"), \
         patch.object(Server, "_Server__init_tools__"), \
         patch.object(Server, "_Server__init_bindings__"), \
         patch.object(Server, "_Server__init_routes__"):

        mock_service = AsyncMock()
        mock_service.run_all_checks.return_value = mock_result
        mock_service_class.return_value = mock_service

        server = Server(mock_config)

        # Should not raise
        await server._test_connection_on_startup()

        mock_service.run_all_checks.assert_called_once_with(timeout=30)

@pytest.mark.asyncio
async def test_startup_test_failure(mock_config):
    """Test failed startup connection test raises exception."""
    mock_result = ConnectionTestResult(
        success=False,
        duration_ms=1234,
        checks=[],
        error="Connection failed",
    )

    with patch("itential_mcp.platform.connection_test.ConnectionTestService") as mock_service_class, \
         patch.object(Server, "_Server__init_server__"), \
         patch.object(Server, "_Server__init_tools__"), \
         patch.object(Server, "_Server__init_bindings__"), \
         patch.object(Server, "_Server__init_routes__"):

        mock_service = AsyncMock()
        mock_service.run_all_checks.return_value = mock_result
        mock_service_class.return_value = mock_service

        server = Server(mock_config)

        # Should raise ConnectionException
        with pytest.raises(ConnectionException) as exc_info:
            await server._test_connection_on_startup()

        assert "Connection test failed" in str(exc_info.value)

@pytest.mark.asyncio
async def test_startup_test_disabled(mock_config):
    """Test startup test skipped when disabled."""
    mock_config.server.test_connection_on_startup = False

    with patch("itential_mcp.platform.connection_test.ConnectionTestService") as mock_service_class, \
         patch.object(Server, "_Server__init_server__"), \
         patch.object(Server, "_Server__init_tools__"), \
         patch.object(Server, "_Server__init_bindings__"), \
         patch.object(Server, "_Server__init_routes__"), \
         patch.object(Server, "run", new_callable=AsyncMock):

        server = Server(mock_config)

        # Service should not be created
        mock_service_class.assert_not_called()
```

**Acceptance Criteria:**
- [ ] Integration tests pass
- [ ] Success case tested
- [ ] Failure case tested
- [ ] Disabled case tested

---

### Phase 4 Deliverables Checklist

- [ ] Configuration options added
- [ ] Server startup integration complete
- [ ] Startup test works when enabled
- [ ] Server fails fast on connection failure
- [ ] Documentation updated
- [ ] Integration tests passing
- [ ] Backward compatible (off by default)

---

## Post-Implementation Tasks

### Task: Update CHANGELOG
**File:** `CHANGELOG.md`
**Estimated Time:** 30 minutes

Add entry for new feature:

```markdown
## [Unreleased]

### Added
- Connection test feature (#299)
  - New `test-connection` CLI command to validate platform connectivity
  - Performs 7 comprehensive connectivity checks (config, DNS, TCP, TLS, auth, health, API)
  - Supports human-readable and JSON output formats
  - Optional startup connection testing with `test_connection_on_startup` config option
  - Detailed error messages with actionable suggestions
  - Verbose mode for diagnostic information
```

---

### Task: Update User Documentation
**Files:** Various in `docs/`
**Estimated Time:** 1 hour

1. **README.md** - Add quick reference
2. **integration.md** - Add troubleshooting section
3. **connection-testing.md** - Complete user guide (created in Phase 3)

---

### Task: Run Full Test Suite
**Estimated Time:** 30 minutes

```bash
# Run all tests
make test

# Check coverage
make coverage

# Ensure >95% coverage for new code

# Run linting
make check

# Format code
make format

# Run premerge pipeline
make premerge
```

---

### Task: Manual Testing
**Estimated Time:** 2-3 hours

Test scenarios:

1. **Valid Connection**
   - Configure valid platform connection
   - Run `itential-mcp test-connection`
   - Verify all checks pass
   - Verify output is clear

2. **Invalid Hostname**
   - Set `ITENTIAL_MCP_PLATFORM_HOST=invalid.example.com`
   - Run test-connection
   - Verify DNS check fails with helpful message

3. **Wrong Port**
   - Set invalid port number
   - Verify TCP connection fails with suggestion

4. **TLS Certificate Mismatch**
   - Configure hostname that doesn't match certificate
   - Verify TLS check fails with clear suggestion

5. **Invalid Credentials**
   - Set wrong username/password
   - Verify auth check fails with helpful message

6. **JSON Output**
   - Run with `--format json`
   - Verify JSON is valid
   - Verify all fields present

7. **Verbose Output**
   - Run with `--verbose`
   - Verify detailed information shown

8. **Startup Testing**
   - Enable `test_connection_on_startup`
   - Start server with valid config
   - Verify server starts normally
   - Start server with invalid config
   - Verify server exits with error

9. **Timeout**
   - Simulate slow network
   - Run with `--timeout 5`
   - Verify timeout handling works

10. **Quiet Mode**
    - Run with `--quiet --format json`
    - Verify no progress messages

---

### Task: Create Pull Request
**Estimated Time:** 1 hour

1. Create feature branch: `git checkout -b feature/connection-test-299`
2. Commit changes in logical groups:
   - "feat: add connection test service (#299)"
   - "feat: add test-connection CLI command (#299)"
   - "feat: add JSON output and enhanced diagnostics (#299)"
   - "feat: add startup connection testing option (#299)"
   - "docs: add connection testing documentation (#299)"
3. Write comprehensive PR description:
   - Link to issue #299
   - Summarize changes
   - List new files
   - Note configuration changes
   - Include testing performed
   - Add examples
4. Request review

---

## Risk Management

### Risk 1: Platform Client Limitations
**Risk:** Platform client may not expose all needed functionality for tests
**Mitigation:**
- Phase 1 will reveal any limitations early
- Can add methods to platform client as needed
- Alternative: Use lower-level HTTP client for specific checks

### Risk 2: Test Timeouts
**Risk:** Connection tests may be slow on poor networks
**Mitigation:**
- Configurable timeout with sensible default (30s)
- Individual check timeouts
- Clear timeout messages with suggestions

### Risk 3: Authentication Complexity
**Risk:** Supporting all auth types (Basic, OAuth, JWT) in tests
**Mitigation:**
- Leverage existing platform client auth logic
- Test each auth type separately
- Document any limitations

### Risk 4: TLS Certificate Testing
**Risk:** TLS testing may be complex with various certificate configurations
**Mitigation:**
- Use Python's SSL library (well-tested)
- Skip TLS check when disabled
- Provide clear suggestions for cert issues
- Test with various cert configurations

### Risk 5: Breaking Changes
**Risk:** Changes to config/server might break existing functionality
**Mitigation:**
- Feature is opt-in (off by default)
- Comprehensive regression testing
- Backward compatibility guaranteed

---

## Success Metrics

### Code Quality
- [x] Test coverage > 95% for new code
- [x] All unit tests passing
- [x] All integration tests passing
- [x] Code passes linting (make check)
- [x] Code formatted (make format)
- [x] No regressions in existing tests

### Functionality
- [x] All 7 checks implemented and working
- [x] CLI command works correctly
- [x] Exit codes correct (0=success, 1=failure)
- [x] Human output is clear and helpful
- [x] JSON output is valid and complete
- [x] Startup testing works when enabled
- [x] Error messages are actionable

### Documentation
- [x] User documentation complete
- [x] JSON schema documented
- [x] Examples provided
- [x] Configuration options documented
- [x] CHANGELOG updated

### Performance
- [x] Successful test completes in < 2s
- [x] Failed test completes in < 5s
- [x] No performance regression in server startup

---

## Timeline Summary

| Phase | Duration | Start | End |
|-------|----------|-------|-----|
| Phase 1: Core Foundation | 2-3 days | Day 1 | Day 3 |
| Phase 2: CLI Integration | 1-2 days | Day 4 | Day 5 |
| Phase 3: Enhanced Output | 1-2 days | Day 6 | Day 7 |
| Phase 4: Startup Integration | 1 day | Day 8 | Day 8 |
| **Total** | **5-8 days** | **Day 1** | **Day 8** |

*Timeline assumes single developer, full-time work*

---

## Next Steps

1. **Review this implementation plan** - Ensure all stakeholders agree
2. **Create feature branch** - `feature/connection-test-299`
3. **Start Phase 1** - Begin with Task 1.1
4. **Regular check-ins** - Review progress after each phase
5. **Integration testing** - Test end-to-end after Phase 2
6. **Documentation review** - Review docs after Phase 3
7. **Final testing** - Complete manual test scenarios
8. **Create PR** - Submit for review when complete

---

## Questions for Stakeholders

1. **Should startup test failure be fatal?**
   - Current plan: Yes (server exits)
   - Alternative: Warn but continue

2. **Should we support partial check execution?**
   - E.g., `--check dns,tcp` to run only specific checks
   - Adds complexity but useful for debugging

3. **Should we add connection monitoring?**
   - Out of scope for this feature
   - Consider for future enhancement

4. **Should we cache successful test results?**
   - Current plan: No caching (always fresh)
   - Trade-off: Speed vs. accuracy

---

## Appendix: File Structure

```
src/itential_mcp/
├── platform/
│   └── connection_test.py          # NEW - Core test service
├── runtime/
│   ├── commands.py                 # MODIFIED - Add test_connection command
│   ├── handlers.py                 # MODIFIED - Register handler
│   └── parser.py                   # MODIFIED - Add CLI arguments
├── server/
│   └── server.py                   # MODIFIED - Add startup test
├── config/
│   ├── models.py                   # MODIFIED - Add config fields
│   └── defaults.py                 # MODIFIED - Add defaults
└── cli/
    └── terminal.py                 # MODIFIED - Add utilities (if needed)

tests/
├── test_platform_connection_test.py    # NEW - Unit tests
└── test_runtime_test_connection.py     # NEW - Integration tests

docs/
├── connection-testing.md           # NEW - User documentation
├── README.md                       # MODIFIED - Add reference
└── design/
    ├── connection-test-feature.md  # Design spec
    └── connection-test-implementation-plan.md  # This document
```

---

**End of Implementation Plan**
