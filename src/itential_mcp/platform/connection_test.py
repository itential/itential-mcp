# Copyright (c) 2025 Itential, Inc
# GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

"""Connection testing service for Itential Platform connectivity validation.

This module provides comprehensive connection testing capabilities to validate
connectivity to the Itential Platform. It performs a series of checks including
configuration validation, DNS resolution, TCP connectivity, TLS handshake,
authentication, platform health, and API access.
"""

from __future__ import annotations

import asyncio
import logging
import socket
import ssl
import time
from dataclasses import dataclass
from enum import Enum
from typing import Any

from ..config.models import Config
from ..core.exceptions import AuthenticationException


class CheckStatus(str, Enum):
    """Status of a connection check."""

    PASSED = "passed"
    FAILED = "failed"
    SKIPPED = "skipped"
    WARNING = "warning"


@dataclass
class CheckResult:
    """Result of a single connection check.

    Attributes:
        name: Name of the check that was performed.
        status: Status of the check (passed, failed, skipped, warning).
        message: Human-readable message describing the result.
        duration_ms: Time taken to perform the check in milliseconds.
        details: Additional structured information about the check.
        error: Exception that caused the check to fail, if any.
        suggestion: Actionable suggestion for resolving failures.
    """

    name: str
    status: CheckStatus
    message: str
    duration_ms: float
    details: dict[str, Any] | None = None
    error: Exception | None = None
    suggestion: str | None = None


@dataclass
class ConnectionTestResult:
    """Overall result of connection testing.

    Attributes:
        success: Whether all checks passed successfully.
        duration_ms: Total time taken for all checks in milliseconds.
        checks: List of individual check results.
        platform_version: Version of the Itential Platform, if available.
        authenticated_user: Username of the authenticated user, if available.
        error: Error message if the overall test failed.
    """

    success: bool
    duration_ms: float
    checks: list[CheckResult]
    platform_version: str | None = None
    authenticated_user: str | None = None
    error: str | None = None


class ConnectionTestService:
    """Service for testing platform connectivity.

    This service performs a comprehensive series of checks to validate
    connectivity to the Itential Platform, including configuration validation,
    network connectivity, authentication, and API access.
    """

    def __init__(self, config: Config):
        """Initialize connection test service.

        Args:
            config: Application configuration.
        """
        self.config = config
        self._logger = logging.getLogger(__name__)

        # Determine actual port (0 means use default for protocol)
        self._port = self._get_actual_port()

        # Determine platform authentication type
        self._auth_type = self._get_platform_auth_type()

    def _get_actual_port(self) -> int:
        """Get the actual port to use for connections.

        Returns:
            int: The actual port number.
        """
        port = self.config.platform.port

        # Port 0 means use default for protocol
        if port == 0:
            if self.config.platform.disable_tls:
                return 80  # HTTP default
            else:
                return 443  # HTTPS default

        return port

    def _get_platform_auth_type(self) -> str:
        """Get the platform authentication type.

        Returns:
            str: The authentication type (basic, oauth, or none).
        """
        # Check if OAuth credentials are configured
        if self.config.platform.client_id and self.config.platform.client_secret:
            return "oauth"

        # Check if basic auth credentials are configured
        if self.config.platform.user and self.config.platform.password:
            return "basic"

        return "none"

    def _create_check_result(
        self,
        name: str,
        status: CheckStatus,
        message: str,
        duration_ms: float,
        details: dict[str, Any] | None = None,
        error: Exception | None = None,
        suggestion: str | None = None,
    ) -> CheckResult:
        """Create a CheckResult instance.

        Args:
            name: Name of the check.
            status: Status of the check.
            message: Human-readable message.
            duration_ms: Duration in milliseconds.
            details: Additional details.
            error: Exception that occurred.
            suggestion: Suggestion for resolving issues.

        Returns:
            CheckResult: The created check result.
        """
        return CheckResult(
            name=name,
            status=status,
            message=message,
            duration_ms=duration_ms,
            details=details,
            error=error,
            suggestion=suggestion,
        )

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
                    suggestion="Set ITENTIAL_MCP_PLATFORM_HOST environment variable",
                )

            # Validate auth configuration
            if not self.config.auth.type:
                return self._create_check_result(
                    name="configuration",
                    status=CheckStatus.FAILED,
                    message="Authentication type not configured",
                    duration_ms=(time.perf_counter() - start) * 1000,
                    suggestion="Set ITENTIAL_MCP_AUTH_TYPE environment variable",
                )

            return self._create_check_result(
                name="configuration",
                status=CheckStatus.PASSED,
                message="Configuration loaded successfully",
                duration_ms=(time.perf_counter() - start) * 1000,
                details={
                    "platform_host": self.config.platform.host,
                    "platform_port": self._port,
                    "auth_type": self._auth_type,
                    "tls_enabled": not self.config.platform.disable_tls,
                },
            )

        except Exception as e:
            return self._create_check_result(
                name="configuration",
                status=CheckStatus.FAILED,
                message=f"Configuration error: {e}",
                duration_ms=(time.perf_counter() - start) * 1000,
                error=e,
            )

    async def check_dns_resolution(self) -> CheckResult:
        """Verify hostname resolves to IP address.

        Returns:
            CheckResult: DNS resolution check result.
        """
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
                },
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
                ),
            )

        except Exception as e:
            return self._create_check_result(
                name="dns",
                status=CheckStatus.FAILED,
                message=f"DNS resolution error: {e}",
                duration_ms=(time.perf_counter() - start) * 1000,
                error=e,
            )

    async def check_tcp_connection(self) -> CheckResult:
        """Verify TCP connection can be established.

        Returns:
            CheckResult: TCP connection check result.
        """
        start = time.perf_counter()
        host = self.config.platform.host
        port = self._port

        try:
            # Attempt TCP connection with timeout
            loop = asyncio.get_event_loop()
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(5.0)

            await loop.run_in_executor(
                None,
                sock.connect,
                (host, port),
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
                },
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
                ),
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
                ),
            )

        except Exception as e:
            return self._create_check_result(
                name="tcp",
                status=CheckStatus.FAILED,
                message=f"TCP connection error: {e}",
                duration_ms=(time.perf_counter() - start) * 1000,
                error=e,
            )

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
                duration_ms=(time.perf_counter() - start) * 1000,
            )

        host = self.config.platform.host
        port = self._port

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
                        },
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
                ),
            )

        except Exception as e:
            return self._create_check_result(
                name="tls",
                status=CheckStatus.FAILED,
                message=f"TLS handshake error: {e}",
                duration_ms=(time.perf_counter() - start) * 1000,
                error=e,
            )

    async def check_authentication(self) -> CheckResult:
        """Verify authentication succeeds.

        Returns:
            CheckResult: Authentication check result.
        """
        from .client import PlatformClient

        start = time.perf_counter()

        try:
            # Create temporary client for auth test
            async with PlatformClient():
                # The mere fact that we can create the client and it doesn't
                # throw an auth error means auth is working

                user = getattr(self.config.platform, "user", None)

                return self._create_check_result(
                    name="authentication",
                    status=CheckStatus.PASSED,
                    message=f"Authentication successful ({self._auth_type})",
                    duration_ms=(time.perf_counter() - start) * 1000,
                    details={
                        "auth_type": self._auth_type,
                        "user": user,
                    },
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
                ),
            )

        except Exception as e:
            return self._create_check_result(
                name="authentication",
                status=CheckStatus.FAILED,
                message=f"Authentication error: {e}",
                duration_ms=(time.perf_counter() - start) * 1000,
                error=e,
            )

    async def check_platform_health(self) -> CheckResult:
        """Verify platform health endpoint responds.

        Returns:
            CheckResult: Platform health check result.
        """
        from .client import PlatformClient

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
                    },
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
                ),
            )

    async def check_api_access(self) -> CheckResult:
        """Verify API access with simple query.

        Returns:
            CheckResult: API access check result.
        """
        from .client import PlatformClient

        start = time.perf_counter()

        try:
            async with PlatformClient() as platform_client:
                # Make a simple API call that requires permissions
                # Use health/adapters endpoint with limit for minimal overhead
                # Use the underlying ipsdk client for the HTTP call
                res = await platform_client.client.get(
                    "/health/adapters", params={"limit": 1}
                )
                data = res.json()

                return self._create_check_result(
                    name="api_access",
                    status=CheckStatus.PASSED,
                    message="API access verified",
                    duration_ms=(time.perf_counter() - start) * 1000,
                    details={
                        "api_call": "GET /health/adapters?limit=1",
                        "total_adapters": data.get("total", 0),
                    },
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
                ),
            )

    async def run_all_checks(self, timeout: int = 30) -> ConnectionTestResult:
        """Run all connection checks in sequence.

        Args:
            timeout: Maximum time for all checks in seconds.

        Returns:
            ConnectionTestResult: Overall test results.
        """
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
                        timeout=timeout,
                    )
                    checks.append(result)

                    # Fail fast - stop on first failure
                    if result.status == CheckStatus.FAILED:
                        break

                except asyncio.TimeoutError:
                    checks.append(
                        CheckResult(
                            name=check_method.__name__.replace("check_", ""),
                            status=CheckStatus.FAILED,
                            message="Check timed out",
                            duration_ms=timeout * 1000,
                            suggestion="Increase timeout or check network latency",
                        )
                    )
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
                    if check.details:
                        platform_version = check.details.get("platform_version")
                if (
                    check.name == "authentication"
                    and check.status == CheckStatus.PASSED
                ):
                    if check.details:
                        authenticated_user = check.details.get("user")

            duration_ms = (time.perf_counter() - overall_start) * 1000

            return ConnectionTestResult(
                success=success,
                duration_ms=duration_ms,
                checks=checks,
                platform_version=platform_version,
                authenticated_user=authenticated_user,
                error=None if success else checks[-1].message,
            )

        except Exception as e:
            duration_ms = (time.perf_counter() - overall_start) * 1000
            self._logger.exception("Unexpected error during connection test")

            return ConnectionTestResult(
                success=False,
                duration_ms=duration_ms,
                checks=checks,
                error=f"Unexpected error: {e}",
            )
