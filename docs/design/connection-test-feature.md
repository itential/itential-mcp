# Design Spec: Connection Test Feature

**Issue:** [#299](https://github.com/itential/itential-mcp/issues/299)
**Status:** Draft
**Author:** Claude
**Created:** 2026-01-27
**Last Updated:** 2026-01-27

## Problem Statement

Currently, the connection to Itential Platform is only established when a tool is invoked. If the connection is misconfigured (invalid credentials, incorrect host, network issues, TLS problems, etc.), users don't discover the problem until they attempt to use a tool, resulting in a poor user experience and difficult troubleshooting.

Users need a way to:
1. Proactively validate their connection configuration
2. Diagnose connection issues before attempting to use tools
3. Ensure the server is properly configured during startup/deployment

## Goals

1. **CLI Command**: Add a `test-connection` command to validate platform connectivity
2. **Startup Validation**: Add optional connection testing during server startup
3. **Comprehensive Diagnostics**: Provide detailed feedback about connection failures
4. **Backward Compatibility**: Feature is opt-in and maintains current server behavior by default
5. **Fast Feedback**: Connection test should complete quickly (< 5 seconds in normal conditions)

## Non-Goals

1. Connection monitoring/health checks after startup (out of scope - see existing keepalive)
2. Automatic retry or connection recovery logic
3. Connection pooling changes
4. Performance testing or load testing capabilities
5. Testing individual tool availability (focus on platform connectivity only)

## User Stories

### Story 1: Initial Setup Validation
**As a** platform administrator
**I want to** test my connection configuration before starting the server
**So that** I can verify credentials and network settings are correct

```bash
$ itential-mcp test-connection
Testing connection to Itential Platform...
✓ Configuration loaded successfully
✓ DNS resolution: platform.example.com -> 192.168.1.100
✓ TCP connection established (192.168.1.100:3000)
✓ TLS handshake successful
✓ Authentication successful (OAuth)
✓ Platform health check passed
✓ API access verified

Connection test: SUCCESS
Platform version: 2024.1.0
Authenticated as: admin@example.com
Response time: 1.2s
```

### Story 2: Troubleshooting Connection Issues
**As a** developer
**I want to** see detailed error messages when connection fails
**So that** I can quickly identify and fix configuration problems

```bash
$ itential-mcp test-connection
Testing connection to Itential Platform...
✓ Configuration loaded successfully
✓ DNS resolution: platform.example.com -> 192.168.1.100
✓ TCP connection established (192.168.1.100:3000)
✗ TLS handshake failed

Error: TLS certificate verification failed
  Certificate: CN=platform.internal.com
  Expected: CN=platform.example.com
  Reason: Hostname mismatch

Suggestion: Either update ITENTIAL_MCP_PLATFORM_HOST to match certificate,
           or set ITENTIAL_MCP_PLATFORM_DISABLE_VERIFY=true (not recommended)

Connection test: FAILED
```

### Story 3: Deployment Validation
**As a** DevOps engineer
**I want to** validate connection during container/pod startup
**So that** Kubernetes health checks fail fast if misconfigured

```bash
$ itential-mcp run --test-connection-on-startup
[2026-01-27 10:30:00] INFO: Testing platform connection...
[2026-01-27 10:30:01] INFO: Connection test successful
[2026-01-27 10:30:01] INFO: Starting MCP server (transport=sse, port=8000)
```

### Story 4: CI/CD Pipeline Validation
**As a** CI/CD pipeline
**I want to** validate connection configuration in integration tests
**So that** deployment proceeds only with valid configuration

```bash
$ itential-mcp test-connection --format json --quiet
{
  "success": true,
  "duration_ms": 1234,
  "platform_version": "2024.1.0",
  "authenticated_user": "admin@example.com",
  "checks": {
    "config": "passed",
    "dns": "passed",
    "tcp": "passed",
    "tls": "passed",
    "auth": "passed",
    "health": "passed",
    "api_access": "passed"
  }
}
```

## Technical Design

### Architecture Overview

```
┌─────────────────────────────────────────────────────────────┐
│                    CLI Entry Point                          │
│                  (runtime/commands.py)                      │
└──────────────────────────┬──────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────┐
│              Connection Test Orchestrator                    │
│           (runtime/connection_test.py - NEW)                │
│  - Coordinates test sequence                                │
│  - Formats output (human/json)                              │
│  - Handles errors and suggestions                           │
└──────────────────────────┬──────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────┐
│              Connection Test Service                         │
│           (platform/connection_test.py - NEW)               │
│  - Performs individual checks                               │
│  - Returns detailed results                                 │
│  - Measures timing                                          │
└──────────────────────────┬──────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────┐
│                   Platform Client                            │
│              (platform/client.py - MODIFIED)                │
│  - Validates connection                                     │
│  - Exposes test methods                                     │
└─────────────────────────────────────────────────────────────┘
```

### Component Details

#### 1. CLI Command: `test-connection`

**Location:** `src/itential_mcp/runtime/commands.py`

```python
async def test_connection(
    *,
    config_file: str | None = None,
    format: str = "human",  # human, json
    verbose: bool = False,
    timeout: int = 30,
) -> int:
    """Test connection to Itential Platform.

    Returns:
        int: Exit code (0=success, 1=failure)
    """
```

**Arguments:**
- `--config`: Path to configuration file
- `--format`: Output format (human, json)
- `--verbose`: Show detailed diagnostic information
- `--timeout`: Maximum time for test (default: 30s)
- `--quiet`: Suppress progress messages (JSON output only)

#### 2. Server Startup Option

**Configuration:**
```python
# src/itential_mcp/config/models.py
@dataclass
class ServerConfig:
    # ... existing fields ...
    test_connection_on_startup: bool = False  # NEW
    startup_test_timeout: int = 30  # NEW
```

**Environment Variables:**
```bash
ITENTIAL_MCP_SERVER_TEST_CONNECTION_ON_STARTUP=true|false
ITENTIAL_MCP_SERVER_STARTUP_TEST_TIMEOUT=30
```

**Server Initialization:**
```python
# src/itential_mcp/server/server.py
async def run(self):
    if self.config.server.test_connection_on_startup:
        await self._test_connection_on_startup()
    # ... continue with normal startup
```

#### 3. Connection Test Service

**Location:** `src/itential_mcp/platform/connection_test.py` (NEW)

```python
from dataclasses import dataclass
from enum import Enum

class CheckStatus(str, Enum):
    PASSED = "passed"
    FAILED = "failed"
    SKIPPED = "skipped"
    WARNING = "warning"

@dataclass
class CheckResult:
    name: str
    status: CheckStatus
    message: str
    duration_ms: float
    details: dict[str, Any] | None = None
    suggestion: str | None = None

@dataclass
class ConnectionTestResult:
    success: bool
    duration_ms: float
    checks: list[CheckResult]
    platform_version: str | None = None
    authenticated_user: str | None = None
    error: str | None = None

class ConnectionTestService:
    """Performs connection validation checks."""

    def __init__(self, config: Config):
        self.config = config

    async def run_all_checks(
        self,
        timeout: int = 30
    ) -> ConnectionTestResult:
        """Run all connection checks."""

    async def check_configuration(self) -> CheckResult:
        """Validate configuration is loaded and valid."""

    async def check_dns_resolution(self) -> CheckResult:
        """Verify hostname resolves."""

    async def check_tcp_connection(self) -> CheckResult:
        """Verify TCP connection can be established."""

    async def check_tls_handshake(self) -> CheckResult:
        """Verify TLS handshake (if enabled)."""

    async def check_authentication(self) -> CheckResult:
        """Verify authentication succeeds."""

    async def check_platform_health(self) -> CheckResult:
        """Verify platform health endpoint responds."""

    async def check_api_access(self) -> CheckResult:
        """Verify API access with simple query."""
```

#### 4. Output Formatting

**Human-Readable Format:**
```
Testing connection to Itential Platform...
✓ Configuration loaded successfully
✓ DNS resolution: platform.example.com -> 192.168.1.100
✓ TCP connection established (192.168.1.100:3000)
✓ TLS handshake successful
✓ Authentication successful (OAuth)
✓ Platform health check passed
✓ API access verified

Connection test: SUCCESS
Platform version: 2024.1.0
Authenticated as: admin@example.com
Response time: 1.2s
```

**JSON Format:**
```json
{
  "success": true,
  "duration_ms": 1234,
  "platform_version": "2024.1.0",
  "authenticated_user": "admin@example.com",
  "checks": [
    {
      "name": "configuration",
      "status": "passed",
      "message": "Configuration loaded successfully",
      "duration_ms": 12
    },
    {
      "name": "dns",
      "status": "passed",
      "message": "platform.example.com -> 192.168.1.100",
      "duration_ms": 45,
      "details": {
        "hostname": "platform.example.com",
        "ip_address": "192.168.1.100"
      }
    },
    {
      "name": "tcp",
      "status": "passed",
      "message": "TCP connection established",
      "duration_ms": 123
    },
    {
      "name": "tls",
      "status": "passed",
      "message": "TLS handshake successful",
      "duration_ms": 234,
      "details": {
        "protocol": "TLSv1.3",
        "cipher": "TLS_AES_256_GCM_SHA384"
      }
    },
    {
      "name": "authentication",
      "status": "passed",
      "message": "Authentication successful (OAuth)",
      "duration_ms": 456
    },
    {
      "name": "health",
      "status": "passed",
      "message": "Platform health check passed",
      "duration_ms": 234
    },
    {
      "name": "api_access",
      "status": "passed",
      "message": "API access verified",
      "duration_ms": 130
    }
  ]
}
```

### Test Sequence

The connection test performs checks in this order (fail-fast approach):

1. **Configuration Validation**
   - Verify config is loaded
   - Check required fields present
   - Validate field values

2. **DNS Resolution**
   - Resolve hostname to IP address
   - Report IP address
   - Fail if hostname doesn't resolve

3. **TCP Connection**
   - Establish TCP connection to host:port
   - Measure connection time
   - Fail if connection refused/timeout

4. **TLS Handshake** (if TLS enabled)
   - Perform TLS handshake
   - Verify certificate (if verify enabled)
   - Report TLS version and cipher
   - Fail on certificate errors (with helpful suggestions)

5. **Authentication**
   - Attempt authentication with configured method
   - Report auth method and user
   - Fail on auth errors (invalid credentials, expired tokens, etc.)

6. **Platform Health Check**
   - Call `/health` or equivalent endpoint
   - Verify platform is responding
   - Report platform version if available

7. **API Access Verification**
   - Make a simple API call (e.g., list adapters with limit=1)
   - Verify API access is working
   - Fail if API returns errors

### Error Handling & Suggestions

For common errors, provide actionable suggestions:

| Error | Suggestion |
|-------|-----------|
| DNS resolution failed | Check hostname spelling, verify DNS configuration, ensure network connectivity |
| Connection refused | Verify platform is running, check host:port configuration, check firewall rules |
| Connection timeout | Check network connectivity, verify host is reachable, increase timeout if needed |
| TLS certificate verification failed | Update hostname to match certificate, or disable verification (not recommended for production) |
| Invalid credentials | Verify username/password, check OAuth configuration, ensure user exists |
| Unauthorized | Check user has required permissions, verify API access is enabled |
| Platform health check failed | Platform may be starting up, check platform logs, verify platform is healthy |

## Implementation Plan

### Phase 1: Core Functionality (Minimal Viable Feature)
- [ ] Create `ConnectionTestService` with basic checks
- [ ] Add `test-connection` CLI command
- [ ] Implement human-readable output format
- [ ] Add basic error messages
- [ ] Unit tests for connection test service

### Phase 2: Enhanced Diagnostics
- [ ] Add JSON output format
- [ ] Implement detailed check results
- [ ] Add error suggestions
- [ ] Add verbose mode
- [ ] Integration tests

### Phase 3: Startup Integration
- [ ] Add `test_connection_on_startup` config option
- [ ] Integrate with server startup flow
- [ ] Add startup test timeout handling
- [ ] Update documentation

### Phase 4: Advanced Features (Optional)
- [ ] Add `--check` flag to test specific checks only
- [ ] Add timing metrics for each check
- [ ] Add TLS certificate details output
- [ ] Add network diagnostic info (latency, bandwidth)

## File Changes

### New Files
```
src/itential_mcp/platform/connection_test.py    # Connection test service
src/itential_mcp/runtime/connection_test.py     # CLI orchestration
tests/test_connection_test.py                   # Unit tests
tests/test_runtime_connection_test.py           # CLI tests
docs/connection-testing.md                      # User documentation
docs/design/connection-test-feature.md          # This document
```

### Modified Files
```
src/itential_mcp/config/models.py               # Add ServerConfig fields
src/itential_mcp/defaults.py                    # Add default values
src/itential_mcp/runtime/commands.py            # Add test_connection command
src/itential_mcp/runtime/handlers.py            # Add command handler
src/itential_mcp/runtime/parser.py              # Add CLI arguments
src/itential_mcp/server/server.py               # Add startup test
docs/README.md                                  # Add quick reference
```

## Configuration Examples

### Command Line
```bash
# Basic test
itential-mcp test-connection

# With custom config
itential-mcp test-connection --config prod.conf

# JSON output for scripting
itential-mcp test-connection --format json --quiet

# Verbose diagnostics
itential-mcp test-connection --verbose

# Custom timeout
itential-mcp test-connection --timeout 60
```

### Environment Variables
```bash
# Enable startup test
ITENTIAL_MCP_SERVER_TEST_CONNECTION_ON_STARTUP=true

# Set startup test timeout
ITENTIAL_MCP_SERVER_STARTUP_TEST_TIMEOUT=30
```

### Configuration File
```toml
[server]
test_connection_on_startup = true
startup_test_timeout = 30
```

### Docker/Kubernetes
```yaml
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
      initialDelaySeconds: 35  # Account for connection test
      periodSeconds: 10
```

## Testing Strategy

### Unit Tests
```python
# tests/test_connection_test.py

@pytest.mark.asyncio
async def test_check_configuration_success():
    """Test configuration check passes with valid config."""

@pytest.mark.asyncio
async def test_check_configuration_failure():
    """Test configuration check fails with invalid config."""

@pytest.mark.asyncio
async def test_check_dns_resolution_success():
    """Test DNS resolution succeeds."""

@pytest.mark.asyncio
async def test_check_authentication_oauth_success():
    """Test OAuth authentication succeeds."""

@pytest.mark.asyncio
async def test_run_all_checks_fail_fast():
    """Test that checks stop on first failure."""
```

### Integration Tests
```python
# tests/test_runtime_connection_test.py

@pytest.mark.asyncio
async def test_test_connection_command_success(mock_platform):
    """Test test-connection command with successful connection."""

@pytest.mark.asyncio
async def test_test_connection_command_failure(mock_platform):
    """Test test-connection command with connection failure."""

@pytest.mark.asyncio
async def test_test_connection_json_output(mock_platform):
    """Test JSON output format."""
```

### Manual Testing Scenarios
1. Valid configuration with working platform
2. Invalid hostname (DNS failure)
3. Wrong port (connection refused)
4. TLS certificate mismatch
5. Invalid credentials
6. Platform down (health check failure)
7. Network timeout
8. OAuth configuration issues

## Performance Considerations

### Timing Targets
- **Fast Path** (all checks pass): < 2 seconds
- **DNS Resolution**: < 100ms
- **TCP Connection**: < 500ms
- **TLS Handshake**: < 500ms
- **Authentication**: < 1000ms (depends on auth method)
- **Health Check**: < 500ms
- **API Access**: < 500ms

### Timeout Handling
- Default timeout: 30 seconds
- Configurable per check
- Fail fast on first error
- Overall timeout prevents hung tests

### Resource Usage
- Single connection (no pooling needed)
- Minimal memory footprint
- No persistent connections
- Clean resource cleanup

## Security Considerations

1. **Credential Exposure**
   - Don't log credentials in error messages
   - Filter sensitive data from verbose output
   - JSON output should not include passwords/tokens

2. **TLS Validation**
   - Warn if certificate verification is disabled
   - Report certificate details in verbose mode
   - Suggest proper certificate configuration

3. **Authentication**
   - Support all existing auth methods
   - Don't expose token values in output
   - Handle expired tokens gracefully

## Backward Compatibility

### Breaking Changes
None - feature is entirely opt-in

### Migration Path
Not applicable - new feature with no existing users

### Deprecations
None

### Default Behavior
- `test_connection_on_startup` defaults to `false`
- Maintains current server behavior by default
- Users must explicitly enable startup testing

## Documentation Updates

### User Documentation
1. **docs/connection-testing.md** (NEW)
   - Overview of connection testing feature
   - CLI command usage examples
   - Startup testing configuration
   - Troubleshooting guide with common errors
   - JSON output schema

2. **docs/README.md** (UPDATE)
   - Add `test-connection` to command reference
   - Add quick start example

3. **docs/troubleshooting.md** (UPDATE or NEW - see #301)
   - Add section on connection testing
   - Reference connection test command

### Developer Documentation
1. **AGENTS.md** (UPDATE)
   - Document new modules
   - Add architecture diagram
   - Explain test sequence

2. **CHANGELOG.md** (UPDATE)
   - Add feature to unreleased section

## Success Metrics

### Qualitative
- Users can diagnose connection issues faster
- Deployment failures are caught earlier
- Support burden reduced (self-service diagnostics)

### Quantitative
- Connection test completes in < 2s (success case)
- Connection test completes in < 5s (failure case with timeout)
- Test coverage > 95% for new code
- Zero regression in existing functionality

## Open Questions

1. **Should we add a `--fix` option to auto-correct common issues?**
   - Pro: Better UX, faster resolution
   - Con: Security risk, complexity, limited use cases
   - **Decision:** Not in initial implementation, consider for future

2. **Should we test individual tool availability?**
   - Pro: More comprehensive validation
   - Con: Slow, complexity, tools are dynamic
   - **Decision:** Out of scope - focus on platform connectivity only

3. **Should we cache successful connection tests?**
   - Pro: Faster repeated tests
   - Con: Cache invalidation complexity, false positives
   - **Decision:** No caching - tests should always be fresh

4. **Should startup test failure prevent server start?**
   - Pro: Fail fast, prevents broken deployments
   - Con: Could block legitimate use cases (temporary outages)
   - **Decision:** Yes, fail fast - users can disable if needed

5. **Should we add continuous connection monitoring?**
   - Pro: Detect issues during operation
   - Con: Complexity, overlaps with keepalive, out of scope
   - **Decision:** Out of scope for this feature (keepalive handles this)

## Future Enhancements

### Near-term (Next Release)
- Add `--check` flag to run specific checks only
- Add timing metrics to human output
- Add color output for better readability

### Long-term (Future Releases)
- Connection monitoring dashboard/metrics
- Automated remediation suggestions
- Performance benchmarking mode
- Certificate expiration warnings
- Network latency measurements

## References

- Issue: https://github.com/itential/itential-mcp/issues/299
- Related: Issue #301 (Troubleshooting guide)
- Existing keepalive implementation: `src/itential_mcp/server/keepalive.py`
- Platform health endpoints: `src/itential_mcp/server/routes.py`
- Configuration system: `src/itential_mcp/config/`

## Appendix A: Error Message Examples

### DNS Resolution Failure
```
✗ DNS resolution failed

Error: Could not resolve hostname 'platform.example.com'

Suggestion:
  1. Check hostname spelling in configuration
  2. Verify DNS server is reachable
  3. Try using IP address directly for testing

Configuration:
  ITENTIAL_MCP_PLATFORM_HOST=platform.example.com
```

### TLS Certificate Mismatch
```
✗ TLS handshake failed

Error: Certificate hostname mismatch
  Certificate CN: platform.internal.com
  Expected hostname: platform.example.com

Suggestion:
  1. Update ITENTIAL_MCP_PLATFORM_HOST to 'platform.internal.com'
  2. Or obtain certificate for 'platform.example.com'
  3. Or disable verification (not recommended):
     ITENTIAL_MCP_PLATFORM_DISABLE_VERIFY=true
```

### Authentication Failure
```
✗ Authentication failed

Error: Invalid credentials (401 Unauthorized)

Suggestion:
  1. Verify username and password are correct
  2. Check user exists in Itential Platform
  3. Ensure user has API access permissions
  4. For OAuth, verify issuer and token configuration

Configuration:
  ITENTIAL_MCP_AUTH_TYPE=oauth
  ITENTIAL_MCP_AUTH_ISSUER=https://auth.example.com
  ITENTIAL_MCP_PLATFORM_USER=admin
```

## Appendix B: JSON Schema

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "type": "object",
  "required": ["success", "duration_ms", "checks"],
  "properties": {
    "success": {
      "type": "boolean",
      "description": "Overall test result"
    },
    "duration_ms": {
      "type": "number",
      "description": "Total test duration in milliseconds"
    },
    "platform_version": {
      "type": "string",
      "description": "Itential Platform version (if available)"
    },
    "authenticated_user": {
      "type": "string",
      "description": "Authenticated username (if auth succeeded)"
    },
    "error": {
      "type": "string",
      "description": "Error message if test failed"
    },
    "checks": {
      "type": "array",
      "items": {
        "type": "object",
        "required": ["name", "status", "message", "duration_ms"],
        "properties": {
          "name": {
            "type": "string",
            "enum": ["configuration", "dns", "tcp", "tls", "authentication", "health", "api_access"]
          },
          "status": {
            "type": "string",
            "enum": ["passed", "failed", "skipped", "warning"]
          },
          "message": {
            "type": "string",
            "description": "Human-readable result message"
          },
          "duration_ms": {
            "type": "number",
            "description": "Check duration in milliseconds"
          },
          "details": {
            "type": "object",
            "description": "Additional check-specific details"
          },
          "suggestion": {
            "type": "string",
            "description": "Actionable suggestion if check failed"
          }
        }
      }
    }
  }
}
```
