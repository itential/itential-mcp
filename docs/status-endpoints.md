# Status Endpoints Documentation

This document provides comprehensive documentation for the Kubernetes-standard health check endpoints available in the Itential MCP (Model Context Protocol) server. These endpoints are essential for operators managing containerized deployments and monitoring the health status of the MCP server in production environments.

## Overview

The Itential MCP server implements three distinct health check endpoints that conform to Kubernetes health monitoring standards and best practices. These endpoints serve different purposes in the container orchestration lifecycle and provide operators with granular visibility into various aspects of server health and readiness.

### Purpose and Design Philosophy

The health check endpoints are designed following the principle of separation of concerns:

- **Health Check (`/status/healthz`)**: Validates basic server functionality and internal process health
- **Readiness Check (`/status/readyz`)**: Verifies external dependencies and readiness to serve traffic
- **Liveness Check (`/status/livez`)**: Confirms the process is alive and responsive to prevent unnecessary restarts

These endpoints enable sophisticated orchestration strategies including:
- **Progressive Traffic Routing**: Only ready instances receive traffic
- **Intelligent Recovery**: Distinguish between temporary issues (readiness) and fatal problems (liveness)
- **Deployment Safety**: Ensure new instances are fully operational before receiving production traffic
- **Monitoring Integration**: Provide standardized health metrics for observability platforms

### Transport Requirements and Availability

The status endpoints are exclusively available when the MCP server is configured with HTTP-based transport protocols. This design choice ensures that health checks can be performed independently of the MCP communication protocol.

**Supported Transports:**
- **Server-Sent Events (SSE)**: Real-time bidirectional communication with HTTP foundation
- **Streamable HTTP**: Request-response based HTTP communication

**Unsupported Transport:**
- **Standard I/O (stdio)**: Direct process communication without HTTP layer

The HTTP-based requirement enables integration with standard monitoring tools, load balancers, and orchestration platforms that expect HTTP health check endpoints.

## Endpoints

### GET /status/healthz

**Purpose**: General health check endpoint for basic server operational status  
**Use Case**: Fundamental health monitoring to verify server process functionality  
**Kubernetes Usage**: Primary health monitoring, startup probes, and general wellness checks  
**Performance Characteristics**: Minimal latency, no external dependencies, safe for high-frequency polling

#### Detailed Description

The `/status/healthz` endpoint serves as the foundational health check for the Itential MCP server. This endpoint is designed to be lightweight and fast, focusing exclusively on internal server health without performing any external validation or dependency checks. It represents the most basic level of health verification and is suitable for scenarios where you need to confirm the server process is operational and capable of handling HTTP requests.

This endpoint is particularly valuable during:
- **Container Startup**: Verifying the server has initialized successfully
- **Load Balancer Registration**: Confirming the instance is ready for basic health checks
- **Monitoring Dashboards**: Providing a simple up/down status indicator
- **Debugging**: Quick verification that the HTTP layer is functional

#### Response Format and Status Codes

**Success Response (HTTP 200)**
```json
{
  "status": "ok"
}
```

The success response indicates:
- The MCP server process is running normally
- The HTTP request handling subsystem is functional
- Basic internal components are operational
- The server can accept and process HTTP requests

**Failure Response (HTTP 503 Service Unavailable)**
```json
{
  "status": "unhealthy"
}
```

The failure response indicates:
- Critical internal errors are preventing normal operation
- The server is experiencing internal processing failures
- HTTP request handling may be compromised
- Immediate investigation is recommended

#### Implementation Behavior and Logic

The healthz endpoint implements the following behavior patterns:

1. **Exception Handling**: All internal exceptions are caught and result in HTTP 503 responses
2. **No External Calls**: Deliberately avoids any network calls or external dependency validation
3. **Immediate Response**: Returns immediately without waiting for background processes
4. **Thread Safety**: Designed to be safely called concurrently from multiple monitoring sources
5. **Resource Efficiency**: Minimal CPU and memory footprint per check

#### Technical Implementation Details

The endpoint is implemented in the `get_healthz` function located in `src/itential_mcp/server/routes.py:10-27`. The implementation strategy focuses on:

- **Minimal Logic**: Simple try-catch wrapper around basic response generation
- **Fast Execution**: No database queries, file system access, or network operations
- **Consistent Format**: Standardized JSON response structure across all scenarios
- **Error Isolation**: Failures in the health check don't impact other server operations

#### Monitoring and Alerting Considerations

When implementing monitoring and alerting for the healthz endpoint, consider:

**Frequency Recommendations:**
- **High-Frequency Monitoring**: Every 5-15 seconds for critical systems
- **Load Balancer Health Checks**: Every 10-30 seconds depending on pool size
- **Uptime Monitoring**: Every 30-60 seconds for external monitoring services

**Alert Thresholds:**
- **Immediate Alert**: Single failure may indicate critical issues
- **Escalation**: Multiple consecutive failures suggest systemic problems
- **Recovery Notification**: Return to healthy status after failures

**Integration Examples:**
- **Prometheus**: Configure as a basic up/down metric
- **Nagios/Icinga**: Use for service availability checks
- **Cloud Load Balancers**: Primary health check endpoint

---

### GET /status/readyz

**Purpose**: Readiness probe endpoint for external dependency validation  
**Use Case**: Comprehensive readiness verification including platform connectivity  
**Kubernetes Usage**: Readiness probe for service mesh traffic routing and load balancer management  
**Performance Characteristics**: Moderate latency due to external validation, includes timeout handling

#### Detailed Description

The `/status/readyz` endpoint provides comprehensive readiness validation for the Itential MCP server, extending beyond basic process health to verify external dependencies and overall system readiness. This endpoint is crucial for production deployments where the server must be capable of successfully communicating with the Itential Platform before receiving client traffic.

Unlike the basic health check, the readiness endpoint performs active validation of the most critical external dependency: connectivity to the Itential Platform. This validation ensures that the MCP server can fulfill its primary function of facilitating communication between AI agents and the Itential Platform.

#### Key Operational Scenarios

This endpoint is essential for:
- **Traffic Management**: Kubernetes uses this to control Service endpoint inclusion
- **Load Balancer Configuration**: Ensures only functional instances receive requests  
- **Deployment Validation**: Confirms new deployments can communicate with dependencies
- **Auto-scaling Events**: Validates new instances before adding to the active pool
- **Maintenance Windows**: Gracefully removes instances from traffic during updates
- **Dependency Recovery**: Automatically restores traffic when dependencies recover

#### Response Format and Comprehensive Status Information

**Ready State Response (HTTP 200)**
```json
{
  "status": "ready"
}
```

The ready response confirms:
- The MCP server internal processes are fully operational
- Network connectivity to the Itential Platform is established and functional
- Authentication credentials (if configured) are valid and accepted
- The server can successfully execute platform API calls
- All critical dependencies are available and responsive

**Not Ready State Response (HTTP 503 Service Unavailable)**
```json
{
  "status": "not ready",
  "reason": "Connection failed"
}
```

Common failure scenarios and their reason messages:
- **Network Connectivity**: `"Connection failed"`, `"Connection timeout"`  
- **Authentication Issues**: `"Authentication failed"`, `"Invalid credentials"`
- **Platform Unavailable**: `"Platform service unavailable"`, `"HTTP 503 from platform"`
- **Configuration Errors**: `"Invalid platform URL"`, `"Missing configuration"`
- **SSL/TLS Issues**: `"SSL verification failed"`, `"Certificate validation error"`

#### Implementation Behavior and External Dependency Validation

The readyz endpoint implements sophisticated dependency checking:

1. **Platform Connectivity Test**: Makes an actual HTTP request to the Itential Platform `/whoami` endpoint
2. **Authentication Validation**: Verifies that configured credentials are accepted by the platform
3. **Timeout Management**: Implements reasonable timeouts to prevent hanging health checks
4. **Error Classification**: Distinguishes between temporary and persistent failure conditions
5. **Resource Cleanup**: Properly closes connections and releases resources after checks
6. **Concurrent Safety**: Handles multiple simultaneous readiness checks without resource conflicts

#### Technical Implementation Deep Dive

The endpoint is implemented in the `get_readyz` function located in `src/itential_mcp/server/routes.py:30-54`. Key implementation aspects include:

**Connection Management:**
- Uses the `PlatformClient` class as an async context manager
- Automatically handles connection pooling and resource cleanup
- Implements proper timeout handling for network operations

**Error Handling Strategy:**
- Catches all exception types including network, authentication, and configuration errors
- Provides detailed error messages in the response for debugging purposes
- Maintains consistent JSON response format across all failure scenarios

**Dependency Validation Logic:**
```python
async with PlatformClient() as client_instance:
    await client_instance.get("/whoami")
```

This validation approach:
- Tests the complete authentication and communication pipeline
- Verifies network connectivity and SSL certificate validation
- Confirms the platform is accepting requests and responding correctly
- Exercises the same code path that actual MCP operations will use

#### Monitoring and Operational Considerations

**Recommended Check Frequencies:**
- **Kubernetes Readiness Probes**: Every 10-15 seconds with 2-3 failure threshold
- **Load Balancer Health Checks**: Every 15-30 seconds depending on traffic patterns
- **Service Mesh Configuration**: Every 10-20 seconds for rapid failover
- **Manual Monitoring**: Every 30-60 seconds for operational dashboards

**Failure Response Strategies:**
- **Immediate Traffic Removal**: Single failure should remove instance from load balancer pool
- **Retry Logic**: Allow 2-3 consecutive failures before marking as persistently unhealthy  
- **Recovery Validation**: Require 2-3 consecutive successes before restoring traffic
- **Alerting Integration**: Notify operations team of persistent readiness failures

**Performance Considerations:**
- **Network Latency**: Check duration depends on platform response time (typically 100-500ms)
- **Concurrent Limits**: Multiple health checkers may create connection pressure
- **Timeout Configuration**: Balance between quick failure detection and false positives
- **Resource Usage**: Each check consumes network connection and memory resources

#### Troubleshooting Readiness Failures

Common failure patterns and resolution strategies:

**Network Connectivity Issues:**
- Verify DNS resolution for platform hostname
- Check firewall rules and security group configurations
- Validate network routing and proxy configurations
- Test direct connectivity using curl or similar tools

**Authentication Failures:**
- Verify API credentials are correctly configured
- Check credential expiration and rotation requirements  
- Validate OAuth token refresh mechanisms (if applicable)
- Confirm platform user permissions and access rights

**Platform-Side Issues:**
- Monitor Itential Platform health and availability
- Check platform logs for authentication or processing errors
- Verify platform version compatibility with MCP server
- Validate platform configuration and service status

**Configuration Problems:**
- Review MCP server configuration file syntax and values
- Verify environment variable settings and precedence
- Check for configuration file permission and access issues
- Validate platform URL format and accessibility

---

### GET /status/livez

**Purpose**: Liveness probe endpoint for process vitality assessment  
**Use Case**: Critical process health monitoring to detect deadlocks, hangs, and fatal errors  
**Kubernetes Usage**: Liveness probe for pod restart decisions and recovery automation  
**Performance Characteristics**: Ultra-low latency, immediate response, no external dependencies

#### Detailed Description

The `/status/livez` endpoint serves as the definitive liveness indicator for the Itential MCP server process. This endpoint is specifically designed to answer the fundamental question: "Is the server process alive and capable of responding to requests?" Unlike readiness checks that verify external dependencies, liveness checks focus exclusively on the internal health and responsiveness of the server process itself.

The liveness endpoint plays a crucial role in Kubernetes' self-healing capabilities. When this endpoint fails consistently, it signals that the container process has entered an unrecoverable state and should be terminated and restarted. This mechanism protects against various failure modes including deadlocks, memory leaks, infinite loops, and other conditions that render a process non-functional while still technically running.

#### Critical Operational Functions

The liveness endpoint enables several important operational capabilities:

- **Deadlock Detection**: Identifies when the server becomes unresponsive due to threading issues
- **Memory Exhaustion Recovery**: Triggers restart when out-of-memory conditions make the process unusable
- **Infinite Loop Protection**: Detects when the server enters infinite processing loops
- **Corruption Recovery**: Restarts processes that have entered corrupted internal states
- **Resource Leak Mitigation**: Prevents accumulation of leaked resources through periodic restarts
- **Graceful Failure Handling**: Ensures consistent availability through automated recovery

#### Response Format and Process State Indicators

**Alive State Response (HTTP 200)**
```json
{
  "status": "alive"
}
```

The alive response definitively indicates:
- The main server process thread is running and responsive
- HTTP request processing pipeline is functional and accepting connections
- Critical server subsystems are operational and not deadlocked
- Memory and resource allocation systems are functioning normally
- The server can process requests without hanging or blocking indefinitely

**Dead State Response (HTTP 503 Service Unavailable)**
```json
{
  "status": "dead"
}
```

The dead response suggests critical process health issues:
- Severe internal errors that prevent normal HTTP response processing
- Critical subsystem failures that compromise server functionality
- Resource exhaustion conditions that prevent request handling
- Internal state corruption requiring process restart for recovery
- Threading or concurrency issues that have rendered the process non-functional

#### Implementation Philosophy and Design Principles

The livez endpoint adheres to specific design principles that differentiate it from other health checks:

1. **Absolute Minimalism**: Implements the smallest possible code path to generate a response
2. **No External Dependencies**: Avoids any network calls, database queries, or file system operations
3. **Immediate Execution**: Returns responses without waiting for background processes or operations
4. **Exception Isolation**: Designed so that failures don't cascade to other system components
5. **Resource Conservation**: Minimal memory allocation and CPU usage per check
6. **Thread Safety**: Safe for concurrent execution from multiple monitoring sources

#### Technical Implementation Analysis

The endpoint is implemented in the `get_livez` function located in `src/itential_mcp/server/routes.py:57-74`. The implementation strategy emphasizes:

**Minimal Code Path:**
```python
try:
    return JSONResponse(content={"status": "alive"}, status_code=200)
except Exception:
    return JSONResponse(content={"status": "dead"}, status_code=503)
```

This approach ensures:
- **Rapid Response Generation**: Minimal processing time between request and response
- **Exception Safety**: Any failure in response generation triggers the dead state
- **Consistent Behavior**: Predictable response format regardless of server state
- **Resource Efficiency**: No memory allocation beyond the basic response object

#### Monitoring Strategy and Operational Patterns

**Recommended Monitoring Frequencies:**
- **Kubernetes Liveness Probes**: Every 10-30 seconds with 3-5 failure threshold
- **Container Orchestration**: Every 15-45 seconds depending on restart tolerance
- **Process Monitoring**: Every 30-60 seconds for system administration
- **Health Dashboards**: Every 60-120 seconds for operational visibility

**Failure Threshold Configuration:**
- **Conservative Approach**: 3-5 consecutive failures before restart (reduces false positives)
- **Aggressive Approach**: 1-2 consecutive failures for rapid recovery (may cause restart loops)
- **Balanced Configuration**: 3 failures over 60-90 seconds (recommended for most deployments)

**Restart and Recovery Patterns:**
- **Graceful Termination**: Allow existing requests to complete before restart
- **Health Check Suspension**: Temporarily disable readiness checks during restart
- **Startup Delay**: Configure appropriate startup probe timing for initialization
- **Circuit Breaker Integration**: Coordinate with upstream circuit breakers during restarts

#### Advanced Operational Scenarios

**False Positive Mitigation:**
The liveness endpoint is designed to minimize false positives, but operators should be aware of scenarios that might trigger unnecessary restarts:
- **High Load Conditions**: Extreme request volume might delay response generation
- **Resource Contention**: CPU or memory pressure could slow response times
- **Network Issues**: Load balancer or proxy timeouts might simulate liveness failures
- **Container Resource Limits**: CPU throttling or memory limits might impact responsiveness

**Integration with Monitoring Systems:**
- **Prometheus Integration**: Export liveness status as a binary metric (up/down)
- **Alerting Configuration**: Immediate alerts on liveness failures due to restart implications  
- **Dashboard Visualization**: Simple status indicators with historical availability trends
- **Log Correlation**: Associate liveness failures with application logs and system metrics

**Troubleshooting Liveness Failures:**
When liveness checks fail consistently, investigate:
- **Resource Utilization**: Check CPU, memory, and I/O usage patterns
- **Thread Analysis**: Look for deadlocks or thread pool exhaustion
- **Error Logs**: Review application logs for exceptions or error patterns
- **System Health**: Examine host-level metrics and resource availability
- **Network Connectivity**: Verify local networking and load balancer configuration

#### Relationship to Other Health Endpoints

Understanding the interaction between all three health endpoints is crucial for effective monitoring:

**Failure Correlation Patterns:**
- **All Endpoints Failing**: Indicates complete server failure requiring restart
- **Only Readiness Failing**: Suggests external dependency issues, not process problems
- **Only Liveness Failing**: Indicates severe process corruption requiring immediate restart
- **Intermittent Failures**: May suggest resource contention or transient issues

**Orchestration Decision Matrix:**
- **Healthy + Ready + Alive**: Normal operation, accept traffic
- **Healthy + Not Ready + Alive**: Remove from load balancer, investigate dependencies
- **Healthy + Ready + Dead**: Contradictory state, prioritize liveness failure investigation
- **Unhealthy + Not Ready + Dead**: Complete failure, immediate restart required

## Comprehensive Usage Examples and Integration Patterns

### Command Line Testing and Validation

#### Basic cURL Commands

```bash
# Basic health check with verbose output
curl -v -X GET http://localhost:8000/status/healthz

# Readiness check with timing information
curl -w "@curl-format.txt" -X GET http://localhost:8000/status/readyz

# Liveness check with JSON pretty-printing
curl -X GET http://localhost:8000/status/livez | jq '.'

# All endpoints with response codes and timing
curl -w "HTTP Status: %{http_code}, Time: %{time_total}s\n" \
     -X GET http://localhost:8000/status/healthz

curl -w "HTTP Status: %{http_code}, Time: %{time_total}s\n" \
     -X GET http://localhost:8000/status/readyz

curl -w "HTTP Status: %{http_code}, Time: %{time_total}s\n" \
     -X GET http://localhost:8000/status/livez
```

#### Advanced Testing Scripts

```bash
#!/bin/bash
# comprehensive-health-check.sh - Complete status endpoint validation

MCP_HOST="${MCP_HOST:-localhost}"
MCP_PORT="${MCP_PORT:-8000}"
BASE_URL="http://${MCP_HOST}:${MCP_PORT}"

echo "=== Itential MCP Server Health Check ==="
echo "Target: ${BASE_URL}"
echo "Timestamp: $(date -Iseconds)"
echo

# Function to check endpoint with detailed output
check_endpoint() {
    local endpoint=$1
    local expected_status=$2
    local description=$3
    
    echo "Testing ${endpoint} (${description})"
    echo "----------------------------------------"
    
    response=$(curl -s -w "HTTPSTATUS:%{http_code};TIME:%{time_total}" \
                   "${BASE_URL}${endpoint}")
    
    http_code=$(echo "$response" | grep -o "HTTPSTATUS:[0-9]*" | cut -d: -f2)
    time_total=$(echo "$response" | grep -o "TIME:[0-9.]*" | cut -d: -f2)
    body=$(echo "$response" | sed -E 's/HTTPSTATUS:[0-9]*;TIME:[0-9.]*$//')
    
    echo "HTTP Status: ${http_code}"
    echo "Response Time: ${time_total}s"
    echo "Response Body: ${body}"
    
    if [ "$http_code" = "$expected_status" ]; then
        echo "✓ PASS: Endpoint returned expected status"
    else
        echo "✗ FAIL: Expected ${expected_status}, got ${http_code}"
    fi
    
    echo
}

# Test all endpoints
check_endpoint "/status/healthz" "200" "Basic Health Check"
check_endpoint "/status/readyz" "200" "Readiness Check" 
check_endpoint "/status/livez" "200" "Liveness Check"

echo "=== Health Check Complete ==="
```

### Production Kubernetes Configurations

#### Comprehensive Pod Configuration with All Probe Types

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: itential-mcp-server
  labels:
    app: itential-mcp
    version: "1.0"
    component: mcp-server
spec:
  containers:
  - name: itential-mcp
    image: itential/mcp-server:latest
    ports:
    - name: http
      containerPort: 8000
      protocol: TCP
    
    # Environment configuration
    env:
    - name: ITENTIAL_MCP_SERVER_TRANSPORT
      value: "sse"
    - name: ITENTIAL_MCP_SERVER_HOST  
      value: "0.0.0.0"
    - name: ITENTIAL_MCP_SERVER_PORT
      value: "8000"
    - name: ITENTIAL_MCP_SERVER_LOG_LEVEL
      value: "INFO"
    
    # Resource limits and requests
    resources:
      requests:
        memory: "256Mi"
        cpu: "250m"
      limits:
        memory: "512Mi"
        cpu: "500m"
    
    # Startup probe - ensures container initializes properly
    startupProbe:
      httpGet:
        path: /status/healthz
        port: http
        scheme: HTTP
      initialDelaySeconds: 10    # Wait 10s after container starts
      periodSeconds: 5           # Check every 5 seconds
      timeoutSeconds: 3          # 3 second timeout per check
      failureThreshold: 6        # Allow up to 30s for startup (6 * 5s)
      successThreshold: 1        # One success means ready
    
    # Liveness probe - determines when to restart container
    livenessProbe:
      httpGet:
        path: /status/livez
        port: http
        scheme: HTTP
      initialDelaySeconds: 30    # Start checking 30s after container starts
      periodSeconds: 30          # Check every 30 seconds
      timeoutSeconds: 5          # 5 second timeout per check
      failureThreshold: 3        # 3 consecutive failures trigger restart
      successThreshold: 1        # One success means alive
    
    # Readiness probe - determines when to send traffic
    readinessProbe:
      httpGet:
        path: /status/readyz
        port: http
        scheme: HTTP
      initialDelaySeconds: 5     # Start checking 5s after container starts
      periodSeconds: 10          # Check every 10 seconds
      timeoutSeconds: 8          # 8 second timeout (allows for platform calls)
      failureThreshold: 2        # 2 consecutive failures remove from service
      successThreshold: 1        # One success means ready
    
    # Security context
    securityContext:
      runAsNonRoot: true
      runAsUser: 1000
      allowPrivilegeEscalation: false
      readOnlyRootFilesystem: true
      capabilities:
        drop:
        - ALL

  restartPolicy: Always
  terminationGracePeriodSeconds: 30
```

#### Production Deployment with Service and Ingress

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: itential-mcp-deployment
  labels:
    app: itential-mcp
spec:
  replicas: 3
  selector:
    matchLabels:
      app: itential-mcp
  strategy:
    type: RollingUpdate
    rollingUpdate:
      maxSurge: 1
      maxUnavailable: 0  # Ensure zero-downtime deployments
  template:
    metadata:
      labels:
        app: itential-mcp
    spec:
      containers:
      - name: itential-mcp
        image: itential/mcp-server:latest
        ports:
        - containerPort: 8000
          name: http
        
        # Health check configuration
        startupProbe:
          httpGet:
            path: /status/healthz
            port: http
          initialDelaySeconds: 15
          periodSeconds: 5
          failureThreshold: 12  # 60 seconds total startup time
        
        livenessProbe:
          httpGet:
            path: /status/livez
            port: http
          initialDelaySeconds: 30
          periodSeconds: 30
          failureThreshold: 3
        
        readinessProbe:
          httpGet:
            path: /status/readyz
            port: http
          initialDelaySeconds: 10
          periodSeconds: 10
          failureThreshold: 2
        
        resources:
          requests:
            memory: "512Mi"
            cpu: "500m"
          limits:
            memory: "1Gi"
            cpu: "1000m"

---
apiVersion: v1
kind: Service
metadata:
  name: itential-mcp-service
  labels:
    app: itential-mcp
spec:
  type: ClusterIP
  ports:
  - port: 80
    targetPort: 8000
    protocol: TCP
    name: http
  selector:
    app: itential-mcp

---
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: itential-mcp-ingress
  annotations:
    nginx.ingress.kubernetes.io/rewrite-target: /
    nginx.ingress.kubernetes.io/proxy-connect-timeout: "10"
    nginx.ingress.kubernetes.io/proxy-send-timeout: "60"
    nginx.ingress.kubernetes.io/proxy-read-timeout: "60"
    nginx.ingress.kubernetes.io/healthcheck-path: "/status/healthz"
spec:
  rules:
  - host: mcp.company.com
    http:
      paths:
      - path: /
        pathType: Prefix
        backend:
          service:
            name: itential-mcp-service
            port:
              number: 80
```

### Advanced Monitoring and Integration Configurations

#### Prometheus ServiceMonitor Configuration

```yaml
apiVersion: monitoring.coreos.com/v1
kind: ServiceMonitor
metadata:
  name: itential-mcp-health-monitor
  labels:
    app: itential-mcp
    monitoring: enabled
spec:
  selector:
    matchLabels:
      app: itential-mcp
  endpoints:
  - port: http
    path: /status/healthz
    interval: 30s
    timeout: 10s
    scheme: http
  - port: http
    path: /status/readyz
    interval: 30s
    timeout: 15s  # Longer timeout for readiness checks
    scheme: http
  - port: http
    path: /status/livez
    interval: 30s
    timeout: 10s
    scheme: http

---
# Prometheus rules for alerting
apiVersion: monitoring.coreos.com/v1
kind: PrometheusRule
metadata:
  name: itential-mcp-health-alerts
spec:
  groups:
  - name: itential-mcp.health
    rules:
    - alert: ItentialMCPDown
      expr: up{job="itential-mcp-health-monitor"} == 0
      for: 1m
      labels:
        severity: critical
      annotations:
        summary: "Itential MCP Server is down"
        description: "Itential MCP server {{ $labels.instance }} has been down for more than 1 minute"
    
    - alert: ItentialMCPNotReady
      expr: probe_success{job="itential-mcp-health-monitor", instance=~".*readyz.*"} == 0
      for: 2m
      labels:
        severity: warning
      annotations:
        summary: "Itential MCP Server not ready"
        description: "Itential MCP server {{ $labels.instance }} has not been ready for more than 2 minutes"
```

#### HAProxy Load Balancer Configuration

```haproxy
global
    daemon
    maxconn 4096
    log stdout local0 info

defaults
    mode http
    timeout connect 5000ms
    timeout client 50000ms
    timeout server 50000ms
    option httplog
    option dontlognull
    
    # Health check configuration
    option httpchk GET /status/readyz
    http-check expect status 200

frontend itential_mcp_frontend
    bind *:80
    default_backend itential_mcp_backend

backend itential_mcp_backend
    balance roundrobin
    
    # Health check every 10 seconds, 2 failures mark as down
    option httpchk GET /status/readyz
    http-check expect status 200
    
    # Server configurations with health checks
    server mcp1 10.0.1.10:8000 check inter 10s fall 2 rise 3
    server mcp2 10.0.1.11:8000 check inter 10s fall 2 rise 3  
    server mcp3 10.0.1.12:8000 check inter 10s fall 2 rise 3
    
    # Health check URI for load balancer status
    http-request set-header X-Forwarded-Proto https if { ssl_fc }
    
    # Custom health check endpoint for load balancer monitoring
    acl health_check path_beg /health
    http-request redirect location /status/healthz if health_check

# Statistics interface
listen stats
    bind *:8404
    stats enable
    stats uri /stats
    stats refresh 30s
    stats admin if TRUE
```

#### NGINX Reverse Proxy with Advanced Health Checking

```nginx
upstream itential_mcp_upstream {
    # Health check configuration
    server 10.0.1.10:8000 max_fails=2 fail_timeout=30s;
    server 10.0.1.11:8000 max_fails=2 fail_timeout=30s;
    server 10.0.1.12:8000 max_fails=2 fail_timeout=30s;
    
    # Load balancing method
    least_conn;
    
    # Keep alive connections
    keepalive 32;
}

# Health check location for external monitoring
server {
    listen 8080;
    server_name _;
    
    location /health {
        access_log off;
        proxy_pass http://itential_mcp_upstream/status/healthz;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_connect_timeout 5s;
        proxy_read_timeout 10s;
    }
    
    location /readiness {
        access_log off;
        proxy_pass http://itential_mcp_upstream/status/readyz;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_connect_timeout 5s;
        proxy_read_timeout 15s;  # Longer timeout for readiness
    }
}

# Main application server
server {
    listen 80;
    server_name mcp.company.com;
    
    # Main application proxy
    location / {
        proxy_pass http://itential_mcp_upstream;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        # Timeout configuration
        proxy_connect_timeout 10s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;
        
        # Health check header passthrough
        proxy_set_header Connection "";
        proxy_http_version 1.1;
    }
    
    # Direct health check access (optional)
    location ~ ^/status/(healthz|readyz|livez)$ {
        proxy_pass http://itential_mcp_upstream$request_uri;
        proxy_set_header Host $host;
        access_log off;
    }
}

## Transport Compatibility and Configuration

### Supported Transport Protocols

The status endpoints are exclusively available when the Itential MCP server is configured with HTTP-based transport protocols. This architectural decision ensures that health monitoring can be performed independently of the primary MCP communication channel.

#### Server-Sent Events (SSE) Transport

```bash
# Basic SSE configuration
itential-mcp --transport sse --host 0.0.0.0 --port 8000

# Advanced SSE configuration with environment variables
export ITENTIAL_MCP_SERVER_TRANSPORT=sse
export ITENTIAL_MCP_SERVER_HOST=0.0.0.0
export ITENTIAL_MCP_SERVER_PORT=8000
export ITENTIAL_MCP_SERVER_LOG_LEVEL=INFO
itential-mcp

# Configuration file based setup
itential-mcp --config /etc/itential-mcp/config.yaml
```

**SSE Transport Characteristics:**
- **Real-time Communication**: Bidirectional communication with HTTP foundation
- **Web-compatible**: Suitable for browser-based clients and web applications
- **Event-driven**: Supports streaming responses and server-sent events
- **HTTP-based Health Checks**: Full support for all status endpoints
- **Load Balancer Friendly**: Standard HTTP endpoints work with all load balancers

#### Streamable HTTP Transport

```bash
# Basic HTTP configuration  
itential-mcp --transport http --host 0.0.0.0 --port 8000 --path /mcp

# Production HTTP configuration
itential-mcp \
  --transport http \
  --host 0.0.0.0 \
  --port 8000 \
  --path /api/mcp \
  --log-level INFO

# Docker container HTTP configuration
docker run -p 8000:8000 itential/mcp-server \
  itential-mcp --transport http --host 0.0.0.0 --port 8000
```

**HTTP Transport Characteristics:**
- **Request-Response Pattern**: Traditional HTTP request/response communication
- **RESTful Interface**: Standard HTTP methods and status codes
- **Path Configuration**: Customizable base path for API endpoints
- **Middleware Support**: Full HTTP middleware stack including authentication
- **Health Check Integration**: Native support for HTTP health monitoring patterns

#### Unsupported Transport Protocol

**Standard I/O (stdio) Transport**

```bash
# stdio transport - health endpoints NOT available
itential-mcp --transport stdio

# This configuration does not support HTTP-based health checks
# Status endpoints will not be accessible via HTTP requests
```

**Why stdio doesn't support health checks:**
- **Process Communication**: Direct process-to-process communication without HTTP layer
- **No HTTP Stack**: Lacks the necessary HTTP server infrastructure for endpoint routing
- **Monitoring Limitations**: External monitoring tools cannot access stdio-based processes via HTTP
- **Orchestration Challenges**: Container orchestration platforms cannot perform HTTP health checks

### Configuration Examples and Best Practices

#### Production SSE Configuration

```yaml
# config.yaml - Production SSE setup
server:
  transport: sse
  host: "0.0.0.0"
  port: 8000
  log_level: "INFO"
  
# Health check specific configurations
health:
  timeout: 30s
  platform_check_enabled: true
  concurrent_checks: true

# Platform connection settings
platform:
  url: "https://itential-platform.company.com"
  timeout: 15s
  retry_attempts: 3
  verify_ssl: true

# Authentication configuration
auth:
  type: "oauth"
  client_id: "${ITENTIAL_CLIENT_ID}"
  client_secret: "${ITENTIAL_CLIENT_SECRET}"
```

#### Enterprise HTTP Configuration

```yaml
# enterprise-config.yaml - Full production HTTP setup
server:
  transport: http
  host: "0.0.0.0" 
  port: 8000
  path: "/api/mcp"
  log_level: "INFO"
  
  # TLS configuration for HTTPS
  tls:
    enabled: true
    cert_file: "/etc/ssl/certs/mcp-server.crt"
    key_file: "/etc/ssl/private/mcp-server.key"
    
  # Security headers
  security:
    cors_enabled: true
    cors_origins: ["https://dashboard.company.com"]
    rate_limiting:
      enabled: true
      requests_per_minute: 1000

# Monitoring and observability
monitoring:
  metrics_enabled: true
  metrics_path: "/metrics"
  health_check_logging: false  # Don't log health checks
  trace_requests: true

# Advanced platform settings  
platform:
  url: "https://itential-platform.company.com"
  connection_pool_size: 20
  keep_alive: true
  timeout: 30s
  
  # High availability settings
  ha:
    enabled: true
    failover_urls:
      - "https://itential-platform-backup.company.com"
      - "https://itential-platform-dr.company.com"
    health_check_interval: 60s
```

#### Environment Variable Configuration Reference

```bash
# Core server settings
export ITENTIAL_MCP_SERVER_TRANSPORT=sse
export ITENTIAL_MCP_SERVER_HOST=0.0.0.0
export ITENTIAL_MCP_SERVER_PORT=8000
export ITENTIAL_MCP_SERVER_PATH=/api/mcp
export ITENTIAL_MCP_SERVER_LOG_LEVEL=INFO

# Platform connection settings
export ITENTIAL_PLATFORM_URL=https://itential-platform.company.com
export ITENTIAL_PLATFORM_USERNAME=mcp-service-account
export ITENTIAL_PLATFORM_PASSWORD=${PLATFORM_PASSWORD}
export ITENTIAL_PLATFORM_TIMEOUT=30

# Authentication settings (OAuth)
export ITENTIAL_MCP_AUTH_TYPE=oauth
export ITENTIAL_MCP_AUTH_CLIENT_ID=${OAUTH_CLIENT_ID}
export ITENTIAL_MCP_AUTH_CLIENT_SECRET=${OAUTH_CLIENT_SECRET}
export ITENTIAL_MCP_AUTH_TOKEN_URL=https://auth.company.com/oauth/token

# Health check specific settings
export ITENTIAL_MCP_HEALTH_TIMEOUT=15
export ITENTIAL_MCP_HEALTH_CONCURRENT_ENABLED=true
export ITENTIAL_MCP_HEALTH_PLATFORM_CHECK_ENABLED=true

# TLS/SSL settings (for HTTPS transport)
export ITENTIAL_MCP_TLS_ENABLED=true
export ITENTIAL_MCP_TLS_CERT_FILE=/etc/ssl/certs/mcp.crt
export ITENTIAL_MCP_TLS_KEY_FILE=/etc/ssl/private/mcp.key
export ITENTIAL_MCP_TLS_VERIFY_CLIENT=false
```

## Comprehensive Monitoring and Observability Integration

### Enterprise Prometheus Integration

#### Custom Metrics Export Configuration

```yaml
# prometheus-config.yaml - Custom metrics for health endpoints
global:
  scrape_interval: 15s
  evaluation_interval: 15s

rule_files:
  - "itential_mcp_alerts.yml"

scrape_configs:
  # Health endpoint monitoring
  - job_name: 'itential-mcp-health-endpoints'
    static_configs:
      - targets: 
        - 'mcp-server-1.company.com:8000'
        - 'mcp-server-2.company.com:8000'  
        - 'mcp-server-3.company.com:8000'
    metrics_path: '/status/healthz'
    scrape_interval: 30s
    scrape_timeout: 10s
    scheme: https
    tls_config:
      insecure_skip_verify: false
    
  # Readiness endpoint monitoring with longer timeout
  - job_name: 'itential-mcp-readiness'
    static_configs:
      - targets:
        - 'mcp-server-1.company.com:8000'
        - 'mcp-server-2.company.com:8000'
        - 'mcp-server-3.company.com:8000'
    metrics_path: '/status/readyz'
    scrape_interval: 30s
    scrape_timeout: 15s  # Longer timeout for platform connectivity checks
    scheme: https
    
  # Liveness endpoint monitoring
  - job_name: 'itential-mcp-liveness'
    static_configs:
      - targets:
        - 'mcp-server-1.company.com:8000'
        - 'mcp-server-2.company.com:8000'
        - 'mcp-server-3.company.com:8000'
    metrics_path: '/status/livez'
    scrape_interval: 30s
    scrape_timeout: 10s
    scheme: https
```

#### Advanced Prometheus Rules and Alerting

```yaml
# itential_mcp_alerts.yml - Comprehensive alerting rules
groups:
  - name: itential-mcp-health
    interval: 30s
    rules:
      # Basic availability alerts
      - alert: ItentialMCPServerDown
        expr: up{job=~"itential-mcp-.*"} == 0
        for: 1m
        labels:
          severity: critical
          service: itential-mcp
          type: availability
        annotations:
          summary: "Itential MCP Server {{ $labels.instance }} is down"
          description: |
            The Itential MCP server at {{ $labels.instance }} has been unreachable 
            for more than 1 minute. This indicates a complete service failure.
            Immediate investigation required.
          runbook_url: "https://docs.company.com/runbooks/itential-mcp-down"
          dashboard_url: "https://grafana.company.com/d/itential-mcp"
      
      # Readiness-specific alerts  
      - alert: ItentialMCPServerNotReady
        expr: up{job="itential-mcp-readiness"} == 0
        for: 2m
        labels:
          severity: warning
          service: itential-mcp
          type: readiness
        annotations:
          summary: "Itential MCP Server {{ $labels.instance }} not ready"
          description: |
            The Itential MCP server at {{ $labels.instance }} has failed readiness 
            checks for more than 2 minutes. This typically indicates platform 
            connectivity issues. Traffic is being redirected away from this instance.
          runbook_url: "https://docs.company.com/runbooks/itential-mcp-not-ready"
      
      # Liveness-specific alerts
      - alert: ItentialMCPServerNotLive  
        expr: up{job="itential-mcp-liveness"} == 0
        for: 1m
        labels:
          severity: critical
          service: itential-mcp
          type: liveness
        annotations:
          summary: "Itential MCP Server {{ $labels.instance }} not responding to liveness checks"
          description: |
            The Itential MCP server at {{ $labels.instance }} has failed liveness 
            checks for more than 1 minute. The container should be restarted immediately 
            to prevent prolonged service degradation.
          runbook_url: "https://docs.company.com/runbooks/itential-mcp-not-live"
      
      # Multi-instance availability alerts
      - alert: ItentialMCPClusterDegraded
        expr: (count(up{job=~"itential-mcp-.*"} == 1) / count(up{job=~"itential-mcp-.*"})) < 0.67
        for: 5m
        labels:
          severity: warning
          service: itential-mcp
          type: cluster
        annotations:
          summary: "Itential MCP Cluster degraded - less than 67% instances available"
          description: |
            Less than 2/3 of Itential MCP server instances are currently available.
            Current availability: {{ $value | humanizePercentage }}
            This may indicate a systemic issue affecting multiple instances.
      
      # Response time monitoring (if available)
      - alert: ItentialMCPHighLatency
        expr: histogram_quantile(0.95, http_request_duration_seconds_bucket{job=~"itential-mcp-.*"}) > 2
        for: 5m  
        labels:
          severity: warning
          service: itential-mcp
          type: performance
        annotations:
          summary: "Itential MCP Server {{ $labels.instance }} experiencing high latency"
          description: |
            95th percentile response time for {{ $labels.instance }} is {{ $value }}s,
            which exceeds the 2 second threshold. This may indicate performance degradation.
```

#### Grafana Dashboard Integration

```json
{
  "dashboard": {
    "id": null,
    "title": "Itential MCP Server Health Dashboard",
    "tags": ["itential", "mcp", "health"],
    "timezone": "UTC",
    "panels": [
      {
        "title": "Service Availability Overview",
        "type": "stat",
        "targets": [
          {
            "expr": "up{job=~\"itential-mcp-.*\"}",
            "legendFormat": "{{ instance }}"
          }
        ],
        "fieldConfig": {
          "defaults": {
            "mappings": [
              { "options": { "0": { "text": "Down", "color": "red" } } },
              { "options": { "1": { "text": "Up", "color": "green" } } }
            ]
          }
        }
      },
      {
        "title": "Health Check Status Timeline",
        "type": "status-history", 
        "targets": [
          {
            "expr": "up{job=\"itential-mcp-health-endpoints\"}",
            "legendFormat": "Health - {{ instance }}"
          },
          {
            "expr": "up{job=\"itential-mcp-readiness\"}",
            "legendFormat": "Ready - {{ instance }}"
          },
          {
            "expr": "up{job=\"itential-mcp-liveness\"}",
            "legendFormat": "Live - {{ instance }}"
          }
        ]
      }
    ]
  }
}
```

### Advanced Load Balancer Health Check Configurations

#### AWS Application Load Balancer (ALB) Configuration

```yaml
# aws-alb-health-check.yaml
apiVersion: v1
kind: Service
metadata:
  name: itential-mcp-service
  annotations:
    service.beta.kubernetes.io/aws-load-balancer-type: "nlb"
    service.beta.kubernetes.io/aws-load-balancer-healthcheck-path: "/status/readyz"
    service.beta.kubernetes.io/aws-load-balancer-healthcheck-interval: "30"
    service.beta.kubernetes.io/aws-load-balancer-healthcheck-timeout: "10"
    service.beta.kubernetes.io/aws-load-balancer-healthcheck-healthy-threshold: "2"
    service.beta.kubernetes.io/aws-load-balancer-healthcheck-unhealthy-threshold: "3"
    service.beta.kubernetes.io/aws-load-balancer-healthcheck-protocol: "HTTP"
    service.beta.kubernetes.io/aws-load-balancer-healthcheck-port: "8000"
spec:
  type: LoadBalancer
  ports:
  - port: 80
    targetPort: 8000
    protocol: TCP
  selector:
    app: itential-mcp
```

#### Google Cloud Load Balancer Health Check

```yaml
# gcp-health-check.yaml
apiVersion: compute.googleapis.com/v1
kind: HealthCheck
metadata:
  name: itential-mcp-health-check
spec:
  httpHealthCheck:
    port: 8000
    requestPath: "/status/readyz"
    checkIntervalSec: 30
    timeoutSec: 15
    healthyThreshold: 2
    unhealthyThreshold: 3
  description: "Health check for Itential MCP servers"
```

#### F5 BIG-IP Health Monitor Configuration

```tcl
# F5 BIG-IP configuration for Itential MCP health monitoring
create ltm monitor http itential_mcp_health_monitor {
    defaults-from http
    destination "*:8000"
    send "GET /status/readyz HTTP/1.1\r\nHost: mcp.company.com\r\nConnection: close\r\n\r\n"
    recv "HTTP/1.1 200"
    interval 30
    timeout 15
    up-interval 10
}

create ltm monitor http itential_mcp_liveness_monitor {
    defaults-from http  
    destination "*:8000"
    send "GET /status/livez HTTP/1.1\r\nHost: mcp.company.com\r\nConnection: close\r\n\r\n"
    recv "HTTP/1.1 200"
    interval 60
    timeout 10
    up-interval 30
}

# Pool configuration with health monitoring
create ltm pool itential_mcp_pool {
    members {
        10.0.1.10:8000 { monitor itential_mcp_health_monitor }
        10.0.1.11:8000 { monitor itential_mcp_health_monitor }
        10.0.1.12:8000 { monitor itential_mcp_health_monitor }
    }
    load-balancing-mode least-connections-member
    slow-ramp-time 60
}
```

### Logging and Audit Integration

#### Centralized Logging Configuration

```yaml
# fluentd-health-logging.conf - Centralized health check logging
<source>
  @type http
  @id input_http
  port 9880
  bind 0.0.0.0
  body_size_limit 32m
  keepalive_timeout 10s
</source>

<filter itential.mcp.health.**>
  @type record_transformer
  <record>
    service "itential-mcp"
    environment "#{ENV['ENVIRONMENT']}"
    cluster "#{ENV['CLUSTER_NAME']}"
    timestamp ${Time.now.iso8601}
  </record>
</filter>

# Route health check logs to dedicated index
<match itential.mcp.health.status.**>
  @type elasticsearch
  host elasticsearch.company.com
  port 9200
  index_name itential-mcp-health-${+YYYY.MM.dd}
  type_name health_check
  
  # Custom mapping for health check data
  template_name itential_mcp_health
  template_file /etc/fluent/templates/mcp_health_template.json
  
  <buffer>
    @type file
    path /var/log/fluent/itential_mcp_health
    flush_mode interval
    flush_interval 30s
    chunk_limit_size 64m
    queue_limit_length 32
  </buffer>
</match>
```

#### Structured Health Check Logging

```json
{
  "timestamp": "2024-01-15T10:30:45Z",
  "service": "itential-mcp",
  "instance": "mcp-server-1.company.com:8000", 
  "endpoint": "/status/readyz",
  "status_code": 200,
  "response_time_ms": 245,
  "health_status": "ready",
  "platform_connectivity": "ok",
  "checks": {
    "platform_reachable": true,
    "authentication_valid": true,
    "response_time_acceptable": true
  },
  "metadata": {
    "cluster": "production",
    "environment": "prod",
    "version": "1.2.3",
    "request_id": "req_abc123"
  }
}
```

## Error Handling

All endpoints follow consistent error handling patterns:

1. **Successful Operations**: Return HTTP 200 with JSON status
2. **Failed Operations**: Return HTTP 503 with JSON error details
3. **Exception Handling**: All endpoints catch and handle exceptions gracefully
4. **Timeout Handling**: Platform connectivity checks include proper timeout handling

## Best Practices

1. **Frequency**: 
   - `healthz`: Can be checked frequently (every 5-10 seconds)
   - `readyz`: Moderate frequency (every 10-30 seconds) due to platform connectivity check
   - `livez`: Moderate frequency (every 10-30 seconds)

2. **Failure Thresholds**:
   - Set appropriate failure thresholds in Kubernetes probes
   - Allow for temporary network issues in readiness checks
   - Use startup probes for initial container readiness

3. **Monitoring**:
   - Monitor all three endpoints for comprehensive health coverage
   - Alert on consistent failures across multiple endpoints
   - Use readiness failures to investigate platform connectivity issues

## Implementation Details

The status endpoints are implemented in:
- **Routes**: `src/itential_mcp/server/routes.py`
- **Registration**: `src/itential_mcp/server/server.py:__init_routes__()`
- **Tests**: `tests/test_routes.py`

The endpoints leverage:
- **FastMCP**: For HTTP route registration and handling
- **PlatformClient**: For Itential Platform connectivity validation
- **Starlette**: For HTTP request/response handling