# Troubleshooting Guide

This guide provides specific steps to diagnose and resolve common issues when the Itential MCP server isn't working as expected.

## Table of Contents

- [Quick Diagnostics](#quick-diagnostics)
- [Server Startup Issues](#server-startup-issues)
- [Connection & Network Problems](#connection--network-problems)
- [Authentication & Authorization](#authentication--authorization)
- [Configuration Problems](#configuration-problems)
- [Tool & Binding Issues](#tool--binding-issues)
- [Performance & Timeout Issues](#performance--timeout-issues)
- [SSL/TLS Errors](#ssltls-errors)
- [Container & Kubernetes Deployment](#container--kubernetes-deployment)
- [Logging & Debug Mode](#logging--debug-mode)
- [Getting Help](#getting-help)

## Quick Diagnostics

Start with these fast health checks to quickly identify the problem area.

### Health Check Endpoints

If your server is running with HTTP-based transport (SSE or HTTP), check the health endpoints:

```bash
# Check server health
curl http://localhost:8000/status/healthz

# Check if server is ready to accept requests
curl http://localhost:8000/status/readyz

# Check if server is alive
curl http://localhost:8000/status/livez
```

**Expected response:** `{"status": "ok"}` with HTTP 200 status code.

See [status-endpoints.md](status-endpoints.md) for detailed information about health check endpoints.

### Test Platform Connectivity

Use the built-in connection test command to validate your platform connection:

```bash
# Quick connection test
itential-mcp test

# Verbose output with detailed diagnostics
itential-mcp test --verbose

# Test with specific configuration
itential-mcp test --platform-host platform.example.com --platform-user admin
```

**What it checks:**
- Configuration validation
- DNS resolution
- TCP connection
- TLS handshake (if enabled)
- Authentication
- Platform health API
- Adapter API access

See [connection-testing.md](connection-testing.md) for detailed connection diagnostics.

### Enable Debug Logging

Enable debug logging to see detailed information about what's happening:

```bash
# Enable debug logging via environment variable
export ITENTIAL_MCP_SERVER_LOG_LEVEL=DEBUG
itential-mcp run

# Or pass as command-line argument
itential-mcp run --log-level DEBUG
```

### Quick Fixes Checklist

Before diving into detailed troubleshooting, try these common fixes:

- [ ] Verify platform is running and accessible
- [ ] Check credentials are correct
- [ ] Confirm firewall allows connections
- [ ] Verify TLS certificate is valid (if using HTTPS)
- [ ] Check port is not already in use
- [ ] Ensure configuration file syntax is valid
- [ ] Verify all required environment variables are set
- [ ] Test with `itential-mcp test --verbose`

## Server Startup Issues

### Server Won't Start

**Problem:** Server fails to start or exits immediately.

**Common Causes:**

1. **Configuration Loading Errors**

```bash
# Error message:
ERROR: server stopped unexpectedly: Configuration validation failed
```

**Solution:** Validate your configuration file syntax:

```bash
# Check configuration with test command
itential-mcp test --config /path/to/config.toml

# Enable debug logging to see configuration details
ITENTIAL_MCP_SERVER_LOG_LEVEL=DEBUG itential-mcp run --config /path/to/config.toml
```

2. **Auth Provider / Transport Mismatch**

```bash
# Error message:
ConfigurationException: Authentication provider OAuthProvider is not supported for transport 'stdio'.
OAuth providers require HTTP-based transports (sse or http).
```

**Solution:** Use HTTP-based transport (SSE or HTTP) with OAuth authentication:

```bash
# Change transport to sse
export ITENTIAL_MCP_SERVER_TRANSPORT=sse
export ITENTIAL_MCP_SERVER_HOST=0.0.0.0
export ITENTIAL_MCP_SERVER_PORT=8000

# Or use basic auth with stdio
export ITENTIAL_MCP_SERVER_AUTH_TYPE=none
```

See [oauth-authentication.md](oauth-authentication.md) and [jwt-authentication.md](jwt-authentication.md) for authentication configuration.

3. **Port Already in Use**

```bash
# Error message:
OSError: [Errno 98] Address already in use
```

**Solution:** Use a different port or stop the conflicting process:

```bash
# Use a different port
export ITENTIAL_MCP_SERVER_PORT=8001

# Or find and stop the process using the port
lsof -ti:8000 | xargs kill -9  # Linux/macOS
netstat -ano | findstr :8000    # Windows
```

4. **Missing Required Configuration**

```bash
# Error message:
ValidationException: Platform host is required
```

**Solution:** Set all required platform configuration:

```bash
export ITENTIAL_MCP_PLATFORM_HOST=platform.example.com
export ITENTIAL_MCP_PLATFORM_USER=admin
export ITENTIAL_MCP_PLATFORM_PASSWORD=your_password
```

**Verification:**

```bash
# Server should start without errors
itential-mcp run

# For HTTP transport, check health endpoint
curl http://localhost:8000/status/healthz
```

### Tool Loading Failures

**Problem:** Server starts but tools are not loaded or warnings appear in logs.

**Common Causes:**

1. **Tools Directory Not Found**

```bash
# Warning message:
WARNING: Tools directory not found: /custom/tools/path
```

**Solution:** Verify the tools path exists:

```bash
# Check if path exists
ls -la /custom/tools/path

# Or use default tools (don't set custom path)
unset ITENTIAL_MCP_SERVER_TOOLS_PATH
```

2. **Missing or Invalid Output Schema**

```bash
# Warning message:
WARNING: tool my_tool has a missing or invalid output_schema
```

**Solution:** This is a warning, not an error. The tool will still work but MCP clients won't have complete type information. To fix, add a proper return type annotation to the tool function.

3. **Dynamic Binding Errors**

```bash
# Error message:
ImportError: Dynamic binding failed for tool 'my_workflow'
```

**Solution:** Verify the workflow or service exists in the platform:

```bash
# Check workflow exists
itential-mcp call get_workflows

# Verify binding configuration
echo $ITENTIAL_MCP_TOOL_MY_WORKFLOW
```

**Verification:**

```bash
# List available tools
itential-mcp tools

# List tags
itential-mcp tags

# Enable debug logging to see tool loading details
ITENTIAL_MCP_SERVER_LOG_LEVEL=DEBUG itential-mcp run
```

### Import or Dependency Errors

**Problem:** Server fails to start with import errors.

```bash
# Error message:
ModuleNotFoundError: No module named 'fastmcp'
```

**Solution:** Verify installation and dependencies:

```bash
# Reinstall with all dependencies
pip install --upgrade itential-mcp

# Or with uv
uv pip install --upgrade itential-mcp

# Verify installation
itential-mcp version

# Check Python version (3.10-3.13 required)
python --version
```

## Connection & Network Problems

### Cannot Connect to Platform

**Problem:** Server starts but cannot connect to Itential Platform.

**Diagnosis:** Use the connection test command:

```bash
itential-mcp test --verbose --platform-host platform.example.com
```

**Common Causes:**

1. **DNS Resolution Failure**

```bash
# Check output for:
DNS Resolution: ✗ Failed
  Error: Name or service not known
```

**Solution:** Verify hostname is correct and resolvable:

```bash
# Test DNS resolution
nslookup platform.example.com
dig platform.example.com

# Try with IP address instead
export ITENTIAL_MCP_PLATFORM_HOST=192.168.1.100
itential-mcp test --verbose
```

2. **Network Connectivity Issues**

```bash
# Check output for:
TCP Connection: ✗ Failed
  Error: Connection refused
```

**Solution:** Verify network connectivity and firewall rules:

```bash
# Test TCP connection
telnet platform.example.com 443
nc -zv platform.example.com 443

# Check firewall allows outbound connections
# Verify network route to platform
traceroute platform.example.com
```

3. **Wrong Port Configuration**

```bash
# Check output for:
TCP Connection: ✗ Failed
  Connecting to: platform.example.com:80
```

**Solution:** Verify correct port configuration:

```bash
# For HTTPS (default with TLS enabled)
export ITENTIAL_MCP_PLATFORM_PORT=443  # or 0 for auto-detect

# For HTTP (TLS disabled)
export ITENTIAL_MCP_PLATFORM_PORT=80  # or 0 for auto-detect
export ITENTIAL_MCP_PLATFORM_DISABLE_TLS=true

# Test connection
itential-mcp test --verbose
```

**Detailed Diagnostics:** See [connection-testing.md](connection-testing.md) for comprehensive connection troubleshooting steps.

### Timeout Errors

**Problem:** Requests to platform time out.

```bash
# Error message:
TimeoutExceededError: Request to platform timed out after 30 seconds
```

**Solution:** Increase timeout configuration:

```bash
# Increase platform request timeout (default: 30 seconds)
export ITENTIAL_MCP_PLATFORM_TIMEOUT=60

# Test connection with longer timeout
itential-mcp test --timeout 60 --verbose
```

**Adjust Keepalive Interval:**

```bash
# Increase keepalive interval (default: 300 seconds)
# Lower values = more frequent keepalive pings
export ITENTIAL_MCP_SERVER_KEEPALIVE_INTERVAL=180

# Or disable keepalive
export ITENTIAL_MCP_SERVER_KEEPALIVE_INTERVAL=0
```

**Check Platform Health:**

```bash
# Verify platform is responsive
curl -k https://platform.example.com/health

# Check platform system status
itential-mcp call get_health
```

### Connection Refused

**Problem:** Platform refuses connection.

```bash
# Error message:
ConnectionException: Connection refused to platform.example.com:443
```

**Common Causes:**

1. **Platform Not Running**

**Solution:** Verify platform is running:

```bash
# Check platform status
systemctl status iap  # Linux with systemd
docker ps | grep itential  # Docker deployment
kubectl get pods -n itential  # Kubernetes deployment
```

2. **Wrong Host or Port**

**Solution:** Verify platform configuration:

```bash
# Check platform configuration
echo $ITENTIAL_MCP_PLATFORM_HOST
echo $ITENTIAL_MCP_PLATFORM_PORT

# Test with connection test
itential-mcp test --verbose
```

3. **Firewall Blocking**

**Solution:** Check firewall rules:

```bash
# Linux iptables
sudo iptables -L -n | grep <platform-ip>

# Check if port is accessible
telnet platform.example.com 443
```

## Authentication & Authorization

### Authentication Failures (401)

**Problem:** Server cannot authenticate with platform.

```bash
# Error message:
AuthenticationException: Authentication failed: Invalid credentials
```

**Diagnosis:**

```bash
# Test authentication with connection test
itential-mcp test --verbose

# Check auth section for details
Authentication: ✗ Failed
  Error: 401 Unauthorized
```

**Common Causes:**

1. **Invalid Credentials**

**Solution:** Verify username and password:

```bash
# Check credentials
echo $ITENTIAL_MCP_PLATFORM_USER
echo $ITENTIAL_MCP_PLATFORM_PASSWORD  # Be careful with this!

# Test with different credentials
export ITENTIAL_MCP_PLATFORM_USER=admin
export ITENTIAL_MCP_PLATFORM_PASSWORD=your_password
itential-mcp test --verbose
```

2. **OAuth Token Expired**

**Solution:** Clear token cache and re-authenticate:

```bash
# Token is automatically refreshed by ipsdk
# If issues persist, verify OAuth configuration
echo $ITENTIAL_MCP_PLATFORM_CLIENT_ID
echo $ITENTIAL_MCP_PLATFORM_CLIENT_SECRET
```

See [oauth-authentication.md](oauth-authentication.md) for OAuth configuration.

3. **JWT Validation Errors**

**Solution:** Verify JWT configuration:

```bash
# Check JWT settings
echo $ITENTIAL_MCP_SERVER_AUTH_JWKS_URI
echo $ITENTIAL_MCP_SERVER_AUTH_ISSUER
echo $ITENTIAL_MCP_SERVER_AUTH_AUDIENCE

# Test with debug logging
ITENTIAL_MCP_SERVER_LOG_LEVEL=DEBUG itential-mcp run
```

See [jwt-authentication.md](jwt-authentication.md) for JWT configuration.

### Authorization Failures (403)

**Problem:** Authentication succeeds but operations fail with permission errors.

```bash
# Error message:
AuthorizationException: Insufficient permissions to perform this operation
```

**Solution:** Verify user has required permissions in platform:

1. Check user role in Itential Platform
2. Verify user has access to required resources (workflows, adapters, etc.)
3. Check platform audit logs for permission denial details

**Check Required Scopes:**

```bash
# For OAuth with required scopes
echo $ITENTIAL_MCP_SERVER_AUTH_REQUIRED_SCOPES

# Example scopes
export ITENTIAL_MCP_SERVER_AUTH_REQUIRED_SCOPES="read:platform,write:workflows"
```

### Auth Provider Configuration

**Problem:** Authentication provider configuration is invalid.

**Common Causes:**

1. **JWT JWKS URI Invalid**

```bash
# Error message:
ConfigurationException: Failed to fetch JWKS from uri
```

**Solution:** Verify JWKS URI is accessible:

```bash
# Test JWKS URI
curl https://auth.example.com/.well-known/jwks.json

# Verify configuration
echo $ITENTIAL_MCP_SERVER_AUTH_JWKS_URI
```

2. **OAuth Redirect URI Missing**

```bash
# Error message:
ConfigurationException: OAuth redirect_uri is required for OAuth authentication
```

**Solution:** Set redirect URI:

```bash
export ITENTIAL_MCP_SERVER_AUTH_OAUTH_REDIRECT_URI=http://localhost:8000/auth/callback
```

3. **Auth Type / Transport Mismatch**

**Solution:** Ensure auth type is compatible with transport:

```bash
# OAuth requires HTTP-based transport
export ITENTIAL_MCP_SERVER_TRANSPORT=sse  # or http
export ITENTIAL_MCP_SERVER_AUTH_TYPE=oauth

# stdio transport should use no auth
export ITENTIAL_MCP_SERVER_TRANSPORT=stdio
export ITENTIAL_MCP_SERVER_AUTH_TYPE=none
```

## Configuration Problems

### Configuration Precedence

**Problem:** Configuration values are not being applied as expected.

**Understanding Precedence (highest to lowest):**

1. Environment variables (`ITENTIAL_MCP_*`)
2. Command-line arguments
3. Configuration file (--config)
4. Default values (src/itential_mcp/defaults.py)

**Solution:** Check configuration sources:

```bash
# Environment variables override config file
export ITENTIAL_MCP_SERVER_PORT=9000  # This takes precedence

# Even if config file has:
# [server]
# port = 8000

# Verify which value is used
itential-mcp run --log-level DEBUG  # Shows config loading details
```

**Best Practice:** Use environment variables for secrets, config file for static settings.

### Invalid Configuration Values

**Problem:** Configuration validation fails.

**Common Validation Errors:**

1. **Port Out of Range**

```bash
# Error message:
ValidationException: Port must be between 1 and 65535
```

**Solution:** Use valid port number:

```bash
export ITENTIAL_MCP_SERVER_PORT=8000  # Valid: 1-65535
```

2. **Invalid Host Format**

```bash
# Error message:
ValidationException: Invalid host format
```

**Solution:** Use valid hostname or IP address:

```bash
# Valid formats
export ITENTIAL_MCP_PLATFORM_HOST=platform.example.com
export ITENTIAL_MCP_PLATFORM_HOST=192.168.1.100
export ITENTIAL_MCP_PLATFORM_HOST=::1  # IPv6
```

3. **Tool Name Validation**

```bash
# Error message:
ValidationException: Tool name must contain only letters, numbers, and underscores
```

**Solution:** Use valid tool names:

```bash
# Valid: letters, numbers, underscores
export ITENTIAL_MCP_TOOL_MY_WORKFLOW='{"type":"endpoint","name":"valid_name",...}'

# Invalid: hyphens, spaces, special characters
# ITENTIAL_MCP_TOOL_MY-WORKFLOW  # Wrong!
```

### Missing Required Settings

**Problem:** Server fails to start due to missing required configuration.

```bash
# Error message:
ValidationException: Platform host is required
```

**Solution:** Set all required parameters:

```bash
# Minimum required for basic operation
export ITENTIAL_MCP_PLATFORM_HOST=platform.example.com
export ITENTIAL_MCP_PLATFORM_USER=admin
export ITENTIAL_MCP_PLATFORM_PASSWORD=your_password

# Verify configuration
itential-mcp test --verbose
```

**Required Settings by Transport:**

**stdio:**
```bash
ITENTIAL_MCP_PLATFORM_HOST=required
ITENTIAL_MCP_PLATFORM_USER=required (if not using OAuth)
ITENTIAL_MCP_PLATFORM_PASSWORD=required (if not using OAuth)
```

**sse/http:**
```bash
ITENTIAL_MCP_PLATFORM_HOST=required
ITENTIAL_MCP_PLATFORM_USER=required (if not using OAuth)
ITENTIAL_MCP_PLATFORM_PASSWORD=required (if not using OAuth)
ITENTIAL_MCP_SERVER_HOST=required
ITENTIAL_MCP_SERVER_PORT=required
```

See [user-guide.md](user-guide.md) for complete configuration reference.

## Tool & Binding Issues

### Tools Not Loading

**Problem:** Tools are not available or not appearing in tool list.

**Diagnosis:**

```bash
# List available tools
itential-mcp tools

# Check tool count
itential-mcp tools | wc -l
```

**Common Causes:**

1. **Tools Directory Path Incorrect**

```bash
# Error message:
WARNING: Tools directory not found: /path/to/tools
```

**Solution:** Verify tools path or use default:

```bash
# Use default tools (built-in)
unset ITENTIAL_MCP_SERVER_TOOLS_PATH

# Or specify correct custom path
export ITENTIAL_MCP_SERVER_TOOLS_PATH=/correct/path/to/tools
```

2. **Include/Exclude Tag Filtering**

**Solution:** Check tag filters:

```bash
# Show current tags
itential-mcp tags

# Clear tag filters to see all tools
unset ITENTIAL_MCP_SERVER_INCLUDE_TAGS
unset ITENTIAL_MCP_SERVER_EXCLUDE_TAGS

# Or adjust filters
export ITENTIAL_MCP_SERVER_EXCLUDE_TAGS=experimental  # Exclude only experimental
export ITENTIAL_MCP_SERVER_INCLUDE_TAGS=health,devices  # Include only specific tags
```

See [tags.md](tags.md) for detailed information about tool tagging.

3. **Tool Loading Failed**

**Solution:** Enable debug logging to see tool loading details:

```bash
ITENTIAL_MCP_SERVER_LOG_LEVEL=DEBUG itential-mcp run 2>&1 | grep "tool"
```

### Dynamic Binding Errors

**Problem:** Dynamic bindings for workflows or services fail to load.

**Common Causes:**

1. **Workflow or Endpoint Not Found**

```bash
# Error message:
ImportError: Workflow 'MyWorkflow' not found in platform
```

**Solution:** Verify workflow exists and name matches:

```bash
# List available workflows
itential-mcp call get_workflows

# Verify workflow name matches exactly (case-sensitive)
export ITENTIAL_MCP_TOOL_MY_WORKFLOW='{"type":"endpoint","name":"trigger_name","automation":"Exact Workflow Name"}'
```

2. **Service Binding Failures**

```bash
# Error message:
ImportError: Service 'ansible' not found in cluster 'default'
```

**Solution:** Verify service exists in gateway cluster:

```bash
# List available services
itential-mcp call get_services

# Verify service name and cluster
export ITENTIAL_MCP_TOOL_RUN_ANSIBLE='{"type":"service","name":"exact_service_name","cluster":"correct_cluster"}'
```

3. **Invalid JSON in Tool Configuration**

```bash
# Error message:
ValidationException: Invalid JSON in tool configuration
```

**Solution:** Validate JSON syntax:

```bash
# Use proper JSON formatting
export ITENTIAL_MCP_TOOL_MY_TOOL='{"type":"endpoint","name":"my_trigger","automation":"My Workflow"}'

# Common mistakes to avoid:
# - Missing quotes around strings
# - Single quotes instead of double quotes
# - Trailing commas
# - Unescaped special characters
```

### Tool Execution Errors

**Problem:** Tool calls fail during execution.

**Common Causes:**

1. **Resource Not Found**

```bash
# Error message:
NotFoundError: Adapter 'my_adapter' not found
```

**Solution:** Verify resource exists:

```bash
# List adapters
itential-mcp call get_adapters

# Check resource by ID
itential-mcp call get_adapter --params '{"adapter_id":"ServiceNow"}'
```

2. **Invalid Resource State**

```bash
# Error message:
InvalidStateError: Cannot start adapter 'my_adapter' in state 'running'
```

**Solution:** Check resource state before operation:

```bash
# Get adapter status
itential-mcp call get_adapter --params '{"adapter_id":"ServiceNow"}'

# Stop adapter before starting
itential-mcp call stop_adapter --params '{"adapter_id":"ServiceNow"}'
```

3. **Timeout During Execution**

```bash
# Error message:
TimeoutExceededError: Tool execution exceeded timeout of 30 seconds
```

**Solution:** Increase timeout or optimize operation:

```bash
# Increase platform timeout
export ITENTIAL_MCP_PLATFORM_TIMEOUT=60

# For long-running workflows, use async execution
itential-mcp call run_workflow --params '{"name":"MyWorkflow","async":true}'
```

## Performance & Timeout Issues

### Slow Response Times

**Problem:** Tools and operations take longer than expected.

**Diagnosis:**

```bash
# Enable timing middleware logging
ITENTIAL_MCP_SERVER_LOG_LEVEL=DEBUG itential-mcp run

# Look for timing information in logs:
# INFO: Tool 'get_health' completed in 2.5s
```

**Common Causes:**

1. **Platform Performance Degradation**

**Solution:** Check platform health:

```bash
# Get platform health
itential-mcp call get_health

# Check system resources
itential-mcp call get_system_info

# Review platform logs for performance issues
```

2. **Connection Pool Exhaustion**

**Solution:** Monitor connection usage and adjust keepalive:

```bash
# Reduce keepalive interval to maintain connections
export ITENTIAL_MCP_SERVER_KEEPALIVE_INTERVAL=180  # 3 minutes

# Or increase timeout for busy platforms
export ITENTIAL_MCP_PLATFORM_TIMEOUT=60
```

3. **Large Result Sets**

**Solution:** Use pagination or filtering:

```bash
# Use limit parameter
itential-mcp call get_workflows --params '{"limit":50}'

# Filter results
itential-mcp call get_adapters --params '{"filter":{"status":"running"}}'
```

### Request Timeouts

**Problem:** Requests consistently time out.

```bash
# Error message:
TimeoutExceededError: Request to platform timed out after 30 seconds
```

**Solution:** Adjust timeout configuration:

```bash
# Increase platform request timeout (default: 30s)
export ITENTIAL_MCP_PLATFORM_TIMEOUT=90

# Test with connection test
itential-mcp test --timeout 90 --verbose

# For specific long-running operations, use async execution:
itential-mcp call run_workflow --params '{"name":"LongWorkflow","async":true}'
```

**Check Platform Load:**

```bash
# Get platform health metrics
itential-mcp call get_health

# Check for errors
itential-mcp call get_errors --params '{"limit":10}'
```

### Keepalive Configuration

**Problem:** Sessions timeout frequently requiring re-authentication.

**Solution:** Adjust keepalive interval:

```bash
# Default: 300 seconds (5 minutes)
# Lower value = more frequent keepalive pings = more stable connection
export ITENTIAL_MCP_SERVER_KEEPALIVE_INTERVAL=180  # 3 minutes

# Very stable networks can use higher values
export ITENTIAL_MCP_SERVER_KEEPALIVE_INTERVAL=600  # 10 minutes

# Disable keepalive (not recommended for production)
export ITENTIAL_MCP_SERVER_KEEPALIVE_INTERVAL=0
```

**Monitor Keepalive:**

```bash
# Enable debug logging to see keepalive activity
ITENTIAL_MCP_SERVER_LOG_LEVEL=DEBUG itential-mcp run

# Look for messages like:
# DEBUG: Keepalive ping successful
# INFO: Stopping keepalive task
```

## SSL/TLS Errors

### Certificate Verification Failures

**Problem:** TLS certificate verification fails.

```bash
# Error message:
ConnectionException: SSL: CERTIFICATE_VERIFY_FAILED
```

**Common Causes:**

1. **Self-Signed Certificates**

**Solution (Development Only):** Disable certificate verification:

```bash
# WARNING: Only use in development/testing environments
export ITENTIAL_MCP_PLATFORM_DISABLE_VERIFY=true

# Test connection
itential-mcp test --verbose
```

**Solution (Production):** Install proper CA certificate:

```bash
# Add CA certificate to system trust store
# Linux (Debian/Ubuntu)
sudo cp ca-cert.crt /usr/local/share/ca-certificates/
sudo update-ca-certificates

# Linux (RHEL/CentOS)
sudo cp ca-cert.crt /etc/pki/ca-trust/source/anchors/
sudo update-ca-trust

# macOS
sudo security add-trusted-cert -d -r trustRoot -k /Library/Keychains/System.keychain ca-cert.crt
```

2. **Hostname Mismatch**

```bash
# Error message:
ConnectionException: SSL: CERTIFICATE_VERIFY_FAILED (certificate subject does not match hostname)
```

**Solution:** Use correct hostname that matches certificate:

```bash
# If certificate is for platform.example.com
export ITENTIAL_MCP_PLATFORM_HOST=platform.example.com

# Don't use IP address if certificate has hostname
# export ITENTIAL_MCP_PLATFORM_HOST=192.168.1.100  # Wrong!
```

See [tls.md](tls.md) for comprehensive TLS configuration guide.

### TLS Handshake Errors

**Problem:** TLS handshake fails.

```bash
# Error message:
ConnectionException: SSL handshake failed
```

**Common Causes:**

1. **Protocol Version Mismatch**

**Solution:** Check TLS version support:

```bash
# Test with openssl
openssl s_client -connect platform.example.com:443 -tls1_2
openssl s_client -connect platform.example.com:443 -tls1_3

# Python uses system TLS configuration
# Ensure platform supports TLS 1.2 or higher
```

2. **Cipher Suite Incompatibility**

**Solution:** Verify cipher suite support:

```bash
# Test cipher suites
nmap --script ssl-enum-ciphers -p 443 platform.example.com

# Update platform TLS configuration if needed
```

### Certificate Expired

**Problem:** TLS certificate has expired.

```bash
# Error message:
ConnectionException: SSL: CERTIFICATE_EXPIRED
```

**Solution:** Install updated certificate:

1. Obtain new certificate from certificate authority
2. Install on platform server
3. Restart platform services
4. Test connection:

```bash
# Verify certificate expiration
openssl s_client -connect platform.example.com:443 -servername platform.example.com | openssl x509 -noout -dates

# Test MCP connection
itential-mcp test --verbose
```

## Container & Kubernetes Deployment

### Container Won't Start

**Problem:** Container fails to start or exits immediately.

**Diagnosis:**

```bash
# Check container logs
docker logs itential-mcp

# Check container status
docker ps -a | grep itential-mcp

# Inspect container
docker inspect itential-mcp
```

**Common Causes:**

1. **Environment Variable Configuration**

**Solution:** Verify environment variables are set:

```bash
# Run with required environment variables
docker run -d \
  --name itential-mcp \
  -e ITENTIAL_MCP_SERVER_TRANSPORT=sse \
  -e ITENTIAL_MCP_SERVER_HOST=0.0.0.0 \
  -e ITENTIAL_MCP_SERVER_PORT=8000 \
  -e ITENTIAL_MCP_PLATFORM_HOST=platform.example.com \
  -e ITENTIAL_MCP_PLATFORM_USER=admin \
  -e ITENTIAL_MCP_PLATFORM_PASSWORD=your_password \
  -p 8000:8000 \
  itential-mcp:latest

# Check logs
docker logs itential-mcp
```

2. **Volume Mount Issues**

**Solution:** Verify volume mounts and permissions:

```bash
# Mount configuration file
docker run -d \
  --name itential-mcp \
  -v /path/to/config.toml:/app/config.toml:ro \
  -e ITENTIAL_MCP_CONFIG=/app/config.toml \
  -p 8000:8000 \
  itential-mcp:latest

# Check mount
docker exec itential-mcp ls -la /app/config.toml
```

### Health Probe Failures

**Problem:** Kubernetes readiness/liveness probes fail.

**Diagnosis:**

```bash
# Check pod status
kubectl get pods -n itential

# Describe pod
kubectl describe pod <pod-name> -n itential

# Check events
kubectl get events -n itential --sort-by='.lastTimestamp'
```

**Common Causes:**

1. **Readiness Probe Timing**

```yaml
# Adjust probe timing in deployment
readinessProbe:
  httpGet:
    path: /status/readyz
    port: 8000
  initialDelaySeconds: 10  # Increase if startup is slow
  periodSeconds: 5
  timeoutSeconds: 3
  successThreshold: 1
  failureThreshold: 3
```

2. **Liveness Probe Configuration**

```yaml
livenessProbe:
  httpGet:
    path: /status/livez
    port: 8000
  initialDelaySeconds: 30  # Give server time to start
  periodSeconds: 10
  timeoutSeconds: 5
  successThreshold: 1
  failureThreshold: 3
```

**Solution:** Test health endpoints manually:

```bash
# Port-forward to pod
kubectl port-forward <pod-name> 8000:8000 -n itential

# Test health endpoints
curl http://localhost:8000/status/healthz
curl http://localhost:8000/status/readyz
curl http://localhost:8000/status/livez
```

### Network Policies

**Problem:** Pod cannot connect to platform due to network policies.

**Solution:** Verify network policies allow connections:

```bash
# Check network policies
kubectl get networkpolicies -n itential

# Describe policy
kubectl describe networkpolicy <policy-name> -n itential
```

**Example Network Policy:**

```yaml
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: itential-mcp-egress
  namespace: itential
spec:
  podSelector:
    matchLabels:
      app: itential-mcp
  policyTypes:
  - Egress
  egress:
  - to:
    - podSelector:
        matchLabels:
          app: itential-platform
    ports:
    - protocol: TCP
      port: 443
```

**Test Connectivity:**

```bash
# Exec into pod
kubectl exec -it <pod-name> -n itential -- /bin/bash

# Test DNS
nslookup platform.example.com

# Test TCP connection
nc -zv platform.example.com 443

# Test MCP connection
itential-mcp test --verbose
```

## Logging & Debug Mode

### Enable Debug Logging

Enable detailed logging to troubleshoot issues:

```bash
# Via environment variable
export ITENTIAL_MCP_SERVER_LOG_LEVEL=DEBUG
itential-mcp run

# Via command-line argument
itential-mcp run --log-level DEBUG

# In configuration file
[server]
log_level = "DEBUG"
```

### Log Levels

Available log levels (in order of verbosity):

- `ERROR` - Only errors
- `WARNING` - Errors and warnings
- `INFO` - Normal operation information
- `DEBUG` - Detailed debugging information
- `NONE` - Disable logging (not recommended)

### Reading Logs Effectively

**Key Log Patterns:**

1. **Configuration Loading**

```
INFO: Loading configuration from environment
INFO: Platform configuration: host=platform.example.com port=443 tls=enabled
DEBUG: Server configuration: transport=stdio log_level=DEBUG
```

2. **Connection Issues**

```
ERROR: Failed to connect to platform: Connection refused
DEBUG: Attempting connection to platform.example.com:443
DEBUG: DNS resolved to: 192.168.1.100
ERROR: TCP connection failed after 3 attempts
```

3. **Authentication**

```
INFO: Authenticating with platform using basic auth
DEBUG: Using credentials for user: admin
ERROR: Authentication failed: 401 Unauthorized
```

4. **Tool Execution**

```
INFO: Executing tool: get_health
DEBUG: Tool parameters: {}
INFO: Tool 'get_health' completed in 1.2s
DEBUG: Tool result: {"status": "ok", ...}
```

5. **Keepalive Activity**

```
INFO: Starting keepalive task (interval: 300s)
DEBUG: Keepalive ping successful
INFO: Stopping keepalive task
```

### Sensitive Data Filtering

The server automatically filters sensitive data from logs:

- Passwords
- API keys
- OAuth tokens
- Client secrets

**Example:**

```
# Raw: password=secret123
# Logged: password=***
```

### Security Warnings

Pay attention to security warnings in logs:

```
WARNING: TLS certificate verification is disabled - this is insecure!
WARNING: Using HTTP without TLS - credentials will be sent in plaintext
WARNING: Sensitive configuration in environment variables
```

## Getting Help

### Before Asking for Help

Gather this information to help diagnose the issue:

1. **Version Information**

```bash
itential-mcp version
```

2. **Configuration (Sanitized)**

```bash
# List environment variables (remove passwords!)
env | grep ITENTIAL_MCP | sed 's/PASSWORD=.*/PASSWORD=***/'

# Or show configuration file (remove sensitive data)
cat config.toml | sed 's/password = .*/password = "***"/'
```

3. **Connection Test Output**

```bash
itential-mcp test --verbose --format json > connection-test.json
```

4. **Log Output (Sanitized)**

```bash
# Run with debug logging and capture output (remove sensitive data)
ITENTIAL_MCP_SERVER_LOG_LEVEL=DEBUG itential-mcp run 2>&1 | tee debug.log
# Review and sanitize debug.log before sharing
```

5. **Platform Information**

```bash
# Platform version
itential-mcp call get_health

# Error logs
itential-mcp call get_errors --params '{"limit":10}'
```

### Support Channels

- **GitHub Issues:** https://github.com/itential/itential-mcp/issues
- **Documentation:** https://github.com/itential/itential-mcp/tree/main/docs

### Filing a Bug Report

When filing a bug report, include:

1. **Description:** Clear description of the problem
2. **Steps to Reproduce:** Exact steps to reproduce the issue
3. **Expected Behavior:** What you expected to happen
4. **Actual Behavior:** What actually happened
5. **Version:** Output of `itential-mcp version`
6. **Configuration:** Sanitized configuration (remove passwords!)
7. **Logs:** Relevant log output (sanitized)
8. **Connection Test:** Output of `itential-mcp test --verbose` (if applicable)
9. **Environment:** OS, Python version, deployment method (Docker, Kubernetes, etc.)

### Related Documentation

- [User Guide](user-guide.md) - Installation and basic usage
- [Connection Testing](connection-testing.md) - Detailed connection diagnostics
- [TLS Configuration](tls.md) - TLS/SSL setup and troubleshooting
- [JWT Authentication](jwt-authentication.md) - JWT configuration
- [OAuth Authentication](oauth-authentication.md) - OAuth setup
- [Status Endpoints](status-endpoints.md) - Health check endpoints
- [Integration Guide](integration.md) - MCP client integration
- [Tools Reference](tools.md) - Available tools documentation
- [Tags](tags.md) - Tool tagging system
