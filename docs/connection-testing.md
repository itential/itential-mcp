# Connection Testing

Test connectivity to Itential Platform before starting the server or troubleshoot connection issues with the built-in connection test tool.

## Overview

The `test` command performs a comprehensive series of checks to validate connectivity to the Itential Platform. It helps identify configuration issues, network problems, authentication failures, and other connectivity problems before they affect your MCP server operation.

## Usage

### Basic Test

Test connection with default settings:

```bash
itential-mcp test
```

### Verbose Output

Show detailed diagnostic information:

```bash
itential-mcp test --verbose
```

### JSON Output

Output results in JSON format for automation:

```bash
itential-mcp test --format json
```

### Custom Configuration

Use a custom configuration file:

```bash
itential-mcp test --config /path/to/config.toml
```

### Custom Timeout

Set a custom timeout (default: 30 seconds):

```bash
itential-mcp test --timeout 60
```

### Quiet Mode

Suppress progress messages (JSON output only):

```bash
itential-mcp test --format json --quiet
```

## Connection Checks

The test performs 7 comprehensive checks in sequence:

1. **Configuration** - Validates configuration is loaded and complete
2. **DNS Resolution** - Verifies hostname resolves to IP address
3. **TCP Connection** - Confirms TCP connection can be established
4. **TLS Handshake** - Validates TLS/SSL handshake (if TLS enabled)
5. **Authentication** - Verifies authentication credentials work
6. **Platform Health** - Checks platform health endpoint responds
7. **API Access** - Confirms API access with a simple query

The test uses **fail-fast behavior** - it stops at the first failure to help you focus on the immediate issue.

## Output Formats

### Human-Readable Output

Default format with colored output and clear status indicators:

```
✓ Configuration loaded successfully
✓ platform.example.com -> 192.168.1.100
✓ TCP connection established (platform.example.com:3000)
✓ TLS handshake successful
✓ Authentication successful (oauth)
✓ Platform health check passed
✓ API access verified

────────────────────────────────────────────────────────────

✓ Connection test: SUCCESS

  Platform version: 2024.1.0
  Authenticated as: admin
  Total duration: 1.23s
```

### JSON Output

Structured output suitable for automation and CI/CD:

```json
{
  "success": true,
  "duration_ms": 1234.56,
  "timestamp": "2026-01-27T12:34:56Z",
  "checks": [
    {
      "name": "configuration",
      "status": "passed",
      "message": "Configuration loaded successfully",
      "duration_ms": 12.34,
      "details": {
        "platform_host": "platform.example.com",
        "platform_port": 3000,
        "auth_type": "oauth",
        "tls_enabled": true
      }
    }
  ],
  "platform_version": "2024.1.0",
  "authenticated_user": "admin",
  "summary": {
    "total_checks": 7,
    "passed": 7,
    "failed": 0,
    "skipped": 0,
    "warnings": 0
  }
}
```

## Exit Codes

The command returns standard exit codes:

- **0** - All checks passed successfully
- **1** - One or more checks failed

This makes it suitable for use in scripts and CI/CD pipelines:

```bash
if itential-mcp test; then
    echo "Connection successful"
    itential-mcp run
else
    echo "Connection failed"
    exit 1
fi
```

## Startup Testing

You can configure the server to test the platform connection during startup. This ensures the server only starts if it can successfully connect to the platform.

### Configuration

#### Environment Variables

```bash
export ITENTIAL_MCP_SERVER_TEST_CONNECTION_ON_STARTUP=true
export ITENTIAL_MCP_SERVER_STARTUP_TEST_TIMEOUT=30
```

#### Configuration File

```toml
[server]
test_connection_on_startup = true
startup_test_timeout = 30
```

### Behavior

When startup testing is enabled:

1. Server loads configuration
2. Connection test runs automatically
3. If test succeeds, server starts normally
4. If test fails, server exits with error

This provides **fail-fast behavior** - the server won't start if it can't connect to the platform, making misconfigurations immediately apparent.

### Docker/Kubernetes

When using containers, enable startup testing to validate configuration:

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
    - name: ITENTIAL_MCP_PLATFORM_HOST
      value: "platform.itential.svc.cluster.local"
    livenessProbe:
      httpGet:
        path: /status/livez
        port: 8000
      initialDelaySeconds: 35  # Account for connection test + startup
      periodSeconds: 10
    readinessProbe:
      httpGet:
        path: /status/readyz
        port: 8000
      initialDelaySeconds: 35
      periodSeconds: 5
```

## Troubleshooting

### DNS Resolution Failure

**Error:**
```
✗ Could not resolve hostname 'platform.example.com'
```

**Suggestions:**
1. Check hostname spelling
2. Verify DNS server is reachable
3. Try using IP address directly for testing

**Fix:**
```bash
# Test DNS resolution manually
nslookup platform.example.com

# Or use IP address
export ITENTIAL_MCP_PLATFORM_HOST=192.168.1.100
```

### TCP Connection Refused

**Error:**
```
✗ Connection refused to platform.example.com:3000
```

**Suggestions:**
1. Verify platform is running
2. Check port number is correct
3. Verify platform is listening on this address

**Fix:**
```bash
# Check if platform is listening
netstat -an | grep 3000

# Or test connection manually
telnet platform.example.com 3000
```

### TLS Certificate Verification Failed

**Error:**
```
✗ TLS certificate verification failed
```

**Suggestions:**
1. Update hostname to match certificate CN
2. Obtain valid certificate for this hostname
3. Disable verification (not recommended):
   `ITENTIAL_MCP_PLATFORM_DISABLE_VERIFY=true`

**Fix:**
```bash
# Check certificate details
openssl s_client -connect platform.example.com:3000 -showcerts

# Disable verification for testing (not recommended for production)
export ITENTIAL_MCP_PLATFORM_DISABLE_VERIFY=true
```

### Authentication Failed

**Error:**
```
✗ Authentication failed
```

**Suggestions:**
1. Username and password are correct
2. User exists in Itential Platform
3. User has API access permissions
4. For OAuth, verify issuer and token configuration

**Fix:**
```bash
# Verify credentials
export ITENTIAL_MCP_PLATFORM_USER=admin
export ITENTIAL_MCP_PLATFORM_PASSWORD=correct_password

# Check auth type
export ITENTIAL_MCP_AUTH_TYPE=oauth  # or basic
```

### Platform Health Check Failed

**Error:**
```
✗ Platform health check failed
```

**Suggestions:**
1. Platform is starting up (wait and retry)
2. Platform is experiencing issues (check logs)
3. Health endpoint is not available

**Fix:**
```bash
# Check platform logs
# Wait a moment and retry

# Test health endpoint manually
curl https://platform.example.com:3000/health
```

### API Access Failed

**Error:**
```
✗ API access verification failed
```

**Suggestions:**
1. User lacks required permissions
2. API endpoint is unavailable
3. Request format is invalid

**Fix:**
```bash
# Verify user has appropriate RBAC permissions in Itential Platform
# Check platform documentation for required permissions
```

## Examples

### CI/CD Pipeline Integration

```yaml
# GitLab CI example
test_connection:
  stage: test
  script:
    - itential-mcp test --format json --quiet
  only:
    - main
    - develop

deploy:
  stage: deploy
  script:
    - itential-mcp test
    - docker build -t itential-mcp:latest .
    - docker push itential-mcp:latest
  needs:
    - test_connection
```

### Health Check Script

```bash
#!/bin/bash
# health-check.sh

# Run connection test
if itential-mcp test --format json --quiet > /tmp/connection-test.json; then
    # Extract platform version
    VERSION=$(jq -r '.platform_version' /tmp/connection-test.json)
    echo "Platform version: $VERSION"
    exit 0
else
    # Extract error message
    ERROR=$(jq -r '.error' /tmp/connection-test.json)
    echo "Connection failed: $ERROR"
    exit 1
fi
```

### Verbose Troubleshooting

```bash
# Run with maximum verbosity
itential-mcp test --verbose --timeout 60

# Output shows:
# - Detailed timing for each check
# - Configuration values
# - TLS protocol and cipher information
# - Full error stack traces
```

## Configuration Reference

### Command-Line Options

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `--config` | string | - | Path to configuration file |
| `--timeout` | int | 30 | Maximum time for test in seconds |
| `--verbose` | flag | false | Show detailed diagnostic information |
| `--format` | string | human | Output format (human or json) |
| `--quiet` | flag | false | Suppress progress messages |

### Environment Variables

| Variable | Type | Default | Description |
|----------|------|---------|-------------|
| `ITENTIAL_MCP_SERVER_TEST_CONNECTION_ON_STARTUP` | bool | false | Test connection during startup |
| `ITENTIAL_MCP_SERVER_STARTUP_TEST_TIMEOUT` | int | 30 | Startup test timeout in seconds |
| `ITENTIAL_MCP_PLATFORM_HOST` | string | localhost | Platform hostname |
| `ITENTIAL_MCP_PLATFORM_PORT` | int | 0 | Platform port (0 = auto: 443 for HTTPS, 80 for HTTP) |
| `ITENTIAL_MCP_PLATFORM_DISABLE_TLS` | bool | false | Disable TLS/HTTPS |

All standard platform configuration variables also apply (host, port, auth, etc.).

**Note:** When `ITENTIAL_MCP_PLATFORM_PORT` is set to `0` (default), the connection test will automatically use:
- Port **443** if TLS is enabled (default)
- Port **80** if TLS is disabled

To specify a custom port, set `ITENTIAL_MCP_PLATFORM_PORT` to the desired value:
```bash
export ITENTIAL_MCP_PLATFORM_PORT=3000
```

## Best Practices

1. **Run Before Deployment** - Test connectivity before deploying to production
2. **Enable Startup Testing** - Use in production to fail fast on misconfigurations
3. **Automate in CI/CD** - Include connection testing in your deployment pipeline
4. **Use JSON for Automation** - Parse JSON output in scripts for detailed diagnostics
5. **Monitor Exit Codes** - Check exit codes in scripts for proper error handling
6. **Increase Timeout for Slow Networks** - Adjust timeout for high-latency connections
7. **Use Verbose Mode for Troubleshooting** - Enable verbose output when debugging issues

## See Also

- [Integration Guide](integration.md) - Setting up MCP client integration
- [Configuration](configuration.md) - Complete configuration reference
- [Authentication](authentication.md) - Authentication methods and setup
- [TLS Configuration](tls.md) - TLS/SSL setup and troubleshooting
