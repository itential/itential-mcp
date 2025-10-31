# Itential MCP Server User Guide

This comprehensive guide helps you get started with the Itential MCP (Model Context Protocol) server, from basic setup to advanced usage patterns. Whether you're a platform administrator, network engineer, or automation developer, this guide will help you leverage AI assistants to manage your Itential Platform effectively.

## Table of Contents

1. [Getting Started](#getting-started)
2. [Basic Usage](#basic-usage)
3. [Configuration](#configuration)
4. [Tool Categories & Use Cases](#tool-categories--use-cases)
5. [Role-Based Workflows](#role-based-workflows)
6. [Advanced Features](#advanced-features)
7. [Troubleshooting](#troubleshooting)
8. [Best Practices](#best-practices)

## Getting Started

### Prerequisites

Before you begin, ensure you have:

- **Python 3.10 or higher** installed on your system
- **Access to an Itential Platform instance** with valid credentials
- **An MCP-compatible AI client** (Claude Desktop, Continue.dev, etc.)

### Quick Installation

1. **Install the MCP server:**
   ```bash
   pip install itential-mcp
   ```

2. **Set up your credentials:**
   ```bash
   export ITENTIAL_MCP_PLATFORM_HOST="your-platform.example.com"
   export ITENTIAL_MCP_PLATFORM_USER="your-username"
   export ITENTIAL_MCP_PLATFORM_PASSWORD="your-password"
   ```

3. **Test the connection:**
   ```bash
   itential-mcp run --transport sse --host 0.0.0.0 --port 8000
   ```

4. **Configure your AI client** following the [integration guide](integration.md)

### Your First Interaction

Once connected, try these basic interactions with your AI assistant:

```
"Show me the health status of the Itential Platform"
"List all available workflows"
"Get information about device 'router-01'"
```

## Basic Usage

### Starting the Server

The MCP server supports multiple transport methods:

**Default (stdio transport) - for MCP clients:**
```bash
itential-mcp run
```

**Web-based (SSE transport) - for web interfaces:**
```bash
itential-mcp run --transport sse --host 0.0.0.0 --port 8000
```

**HTTP transport - for REST API access:**
```bash
itential-mcp run --transport http --host 0.0.0.0 --port 8000
```

### Essential Commands

| Command | Purpose | Example |
|---------|---------|---------|
| `itential-mcp run` | Start the server | Basic startup |
| `itential-mcp run --help` | Show all options | Get help |
| `itential-mcp --version` | Check version | Version info |

## Configuration

### Environment Variables

All configuration options can be set via environment variables with the `ITENTIAL_MCP_` prefix:

**Platform Connection:**
```bash
# Required
export ITENTIAL_MCP_PLATFORM_HOST="platform.example.com"
export ITENTIAL_MCP_PLATFORM_USER="automation-user"
export ITENTIAL_MCP_PLATFORM_PASSWORD="secure-password"

# Optional
export ITENTIAL_MCP_PLATFORM_PORT="443"
export ITENTIAL_MCP_PLATFORM_TIMEOUT="30"
export ITENTIAL_MCP_PLATFORM_DISABLE_TLS="false"
export ITENTIAL_MCP_PLATFORM_DISABLE_VERIFY="false"
```

**OAuth Authentication (Alternative):**
```bash
export ITENTIAL_MCP_PLATFORM_HOST="platform.example.com"
export ITENTIAL_MCP_PLATFORM_CLIENT_ID="your-client-id"
export ITENTIAL_MCP_PLATFORM_CLIENT_SECRET="your-client-secret"
```

**Server Options:**
```bash
export ITENTIAL_MCP_SERVER_TRANSPORT="sse"
export ITENTIAL_MCP_SERVER_HOST="0.0.0.0"
export ITENTIAL_MCP_SERVER_PORT="8000"
export ITENTIAL_MCP_SERVER_LOG_LEVEL="INFO"
```

### Configuration Files

Create a configuration file for complex setups:

```toml
# itential-mcp.conf
[server]
transport = "sse"
host = "0.0.0.0"
port = 8000
log_level = "INFO"
include_tags = ["system", "devices", "operations_manager"]
exclude_tags = ["experimental", "beta"]

[platform]
host = "platform.example.com"
port = 443
user = "automation-user"
password = "secure-password"
timeout = 30
disable_tls = false
disable_verify = false
```

Use with: `itential-mcp run --config itential-mcp.conf`

## Tool Categories & Use Cases

### System Management (`system` tag)

**Use Case:** Monitor platform health and system status

**Available Tools:**
- `get_health` - Check overall platform health

**Example Interactions:**
```
"Check the health status of the platform"
"Is the Itential Platform running properly?"
"Show me system health metrics"
```

### Device Management (`devices`, `configuration_manager` tags)

**Use Case:** Manage network devices, configurations, and compliance

**Available Tools:**
- `get_devices` - List all managed devices
- `get_device_configuration` - Retrieve device configurations
- `backup_device_configuration` - Backup device settings
- `apply_device_configuration` - Apply configurations to devices
- `create_device_group` - Create logical device groups
- `get_compliance_plans` - List compliance validation plans
- `run_compliance_plan` - Execute compliance checks

**Example Interactions:**
```
"Show me all devices managed by the platform"
"Backup the configuration for router-01"
"Create a device group for all core routers"
"Run compliance check on the datacenter devices"
"Apply the golden config template to switch-group-1"
```

### Workflow & Automation (`operations_manager`, `workflow_engine` tags)

**Use Case:** Execute workflows, monitor jobs, and track automation

**Available Tools:**
- `get_workflows` - List available workflows
- `start_workflow` - Execute a workflow
- `get_jobs` - List workflow jobs
- `describe_job` - Get detailed job information
- `get_job_metrics` - Performance metrics for jobs
- `get_task_metrics` - Task-level execution metrics

**Example Interactions:**
```
"Show me all available workflows"
"Start the device onboarding workflow for new-switch-01"
"What's the status of job 12345?"
"Show me performance metrics for the backup workflow"
"List all running jobs"
```

### Command Automation (`automation_studio` tag)

**Use Case:** Execute commands and templates across devices

**Available Tools:**
- `get_command_templates` - List command templates
- `describe_command_template` - Get template details
- `run_command_template` - Execute templates on devices
- `run_command` - Run single commands
- `render_template` - Process Jinja2/TextFSM templates

**Example Interactions:**
```
"List all command templates"
"Run the interface check template on core routers"
"Execute 'show version' on all switches"
"Render the BGP configuration template for router-01"
```

### Application & Adapter Management (`applications`, `adapters` tags)

**Use Case:** Manage platform components and integrations

**Available Tools:**
- `get_applications` - List platform applications
- `start_application`, `stop_application`, `restart_application` - Lifecycle management
- `get_adapters` - List platform adapters
- `start_adapter`, `stop_adapter`, `restart_adapter` - Adapter management

**Example Interactions:**
```
"Show me all running applications"
"Restart the Configuration Manager application"
"List all adapters and their status"
"Stop the Cisco IOS adapter for maintenance"
```

### External Services (`gateway_manager` tag)

**Use Case:** Execute external services like Ansible, Python scripts, OpenTofu

**Available Tools:**
- `get_services` - List available external services
- `get_gateways` - List gateway configurations
- `run_service` - Execute external services

**Example Interactions:**
```
"List all available external services"
"Run the Ansible playbook for server provisioning"
"Execute the Python script for network validation"
```

### Lifecycle Management (`lifecycle_manager` tag)

**Use Case:** Manage stateful resources and their lifecycle workflows

**Available Tools:**
- `get_resources` - List resource definitions
- `describe_resource` - Get resource details
- `create_resource` - Define new resource types
- `get_instances` - List resource instances
- `describe_instance` - Get instance details
- `run_action` - Execute lifecycle actions

**Example Interactions:**
```
"Show me all resource types"
"Create a new network service resource"
"List all VPN service instances"
"Run the provision action on service instance 123"
```

## Role-Based Workflows

### Platform Administrator

**Recommended Tags:** `system`, `adapters`, `applications`, `integrations`

**Common Workflows:**
1. **Health Monitoring:** Regular platform health checks
2. **Component Management:** Start/stop/restart applications and adapters
3. **Integration Setup:** Configure external system integrations
4. **Troubleshooting:** Diagnose and resolve platform issues

**Example Session:**
```
"Check platform health"
→ "All systems are running normally"

"List all applications and their status"
→ Shows application status table

"Restart the Configuration Manager application"
→ "Application restarted successfully"
```

### Network Engineer

**Recommended Tags:** `devices`, `configuration_manager`, `automation_studio`

**Common Workflows:**
1. **Device Management:** Inventory and configuration management
2. **Compliance Checking:** Validate device configurations
3. **Configuration Deployment:** Apply golden configs and templates
4. **Troubleshooting:** Execute diagnostic commands

**Example Session:**
```
"Show me all core routers and their configuration status"
→ Lists devices with config details

"Run compliance check on the datacenter switches"
→ Executes compliance plan and shows results

"Apply the security hardening template to all edge routers"
→ Deploys configuration template
```

### Automation Developer

**Recommended Tags:** `operations_manager`, `workflow_engine`, `lifecycle_manager`, `gateway_manager`

**Common Workflows:**
1. **Workflow Development:** Create and test automation workflows
2. **Performance Analysis:** Monitor job and task metrics
3. **Resource Modeling:** Define lifecycle-managed resources
4. **External Integration:** Configure gateway services

**Example Session:**
```
"Show me performance metrics for the device onboarding workflow"
→ Displays execution time, success rate, etc.

"Create a new network service resource type"
→ Defines resource schema and lifecycle actions

"List all available external services"
→ Shows Ansible playbooks, Python scripts, etc.
```

### Platform Operator

**Recommended Tags:** `operations_manager`, `devices`, `configuration_manager`

**Common Workflows:**
1. **Daily Operations:** Execute routine automation jobs
2. **Monitoring:** Track job status and results
3. **Device Operations:** Basic device management tasks
4. **Reporting:** Generate compliance and configuration reports

**Example Session:**
```
"Start the daily backup workflow"
→ Initiates backup job

"Show me the status of all running jobs"
→ Lists active jobs with progress

"Get the compliance report for PCI devices"
→ Shows compliance status and violations
```

## Advanced Features

### Tool Filtering

Control available functionality using tag-based filtering:

```bash
# Include only specific tool categories
itential-mcp run --include-tags "system,devices,operations_manager"

# Exclude experimental features
itential-mcp run --exclude-tags "experimental,beta"

# Combine inclusion and exclusion
itential-mcp run --include-tags "system,devices" --exclude-tags "lifecycle_manager"
```

### Container Deployment

Deploy using Docker for production environments:

```bash
# Pull from registry
docker pull ghcr.io/itential/itential-mcp:latest

# Run with environment variables
docker run -p 8000:8000 \
  --env ITENTIAL_MCP_SERVER_TRANSPORT=sse \
  --env ITENTIAL_MCP_SERVER_HOST=0.0.0.0 \
  --env ITENTIAL_MCP_PLATFORM_HOST=platform.example.com \
  --env ITENTIAL_MCP_PLATFORM_USER=service-account \
  --env ITENTIAL_MCP_PLATFORM_PASSWORD=secure-password \
  ghcr.io/itential/itential-mcp:latest
```

### Authentication Methods

The server supports multiple authentication methods:

**Basic Authentication (Default):**
```bash
export ITENTIAL_MCP_PLATFORM_USER="username"
export ITENTIAL_MCP_PLATFORM_PASSWORD="password"
```

**OAuth 2.0:**
```bash
export ITENTIAL_MCP_PLATFORM_CLIENT_ID="client-id"
export ITENTIAL_MCP_PLATFORM_CLIENT_SECRET="client-secret"
```

### Custom Tool Development

Extend functionality by creating custom tools:

1. Create a Python file in `src/itential_mcp/tools/`
2. Define async functions with Context parameter
3. Tools are auto-discovered on startup

See the [custom tools guide](custom-tools.md) for detailed instructions.

## Troubleshooting

### Common Issues and Solutions

#### Connection Problems

**Issue:** "Connection refused" or timeout errors
**Solutions:**
- Verify `ITENTIAL_MCP_PLATFORM_HOST` is correct
- Check network connectivity and firewall rules
- Confirm platform is running and accessible
- Try disabling TLS for testing: `--platform-disable-tls`

#### Authentication Failures

**Issue:** "401 Unauthorized" or "403 Forbidden"
**Solutions:**
- Verify username/password are correct
- Check if account is locked or expired
- Ensure user has necessary permissions
- Try OAuth if basic auth fails

#### Tool Not Available

**Issue:** AI assistant says "Tool not found"
**Solutions:**
- Check tool tag filtering configuration
- Verify tool is not excluded by `--exclude-tags`
- Review available tools with `get_workflows` or similar
- Check if experimental tools need inclusion

#### Performance Issues

**Issue:** Slow response times or timeouts
**Solutions:**
- Increase timeout: `--platform-timeout 60`
- Check platform performance and load
- Monitor network latency
- Use specific tool tags to reduce overhead

#### SSL Certificate Errors

**Issue:** SSL verification failures
**Solutions:**
- For testing: `--platform-disable-verify`
- Install proper certificates in production
- Check certificate expiration dates
- Verify certificate chain is complete

### Debug Mode

Enable detailed logging for troubleshooting:

```bash
itential-mcp run --log-level DEBUG
```

Or in configuration:
```bash
export ITENTIAL_MCP_SERVER_LOG_LEVEL="DEBUG"
```

### Testing Connectivity

Test your configuration before integrating with AI clients:

```bash
# Test basic connectivity
curl -k https://your-platform.example.com/health

# Test with MCP server
itential-mcp run --transport sse --host localhost --port 8001 &
curl http://localhost:8001/mcp
```

## Best Practices

### Security

1. **Use Service Accounts:** Create dedicated accounts for MCP integration
2. **Apply Principle of Least Privilege:** Use tag filtering to limit tool access
3. **Secure Credentials:** Use environment variables or secure configuration files
4. **Enable TLS:** Always use HTTPS in production environments
5. **Regular Rotation:** Rotate passwords and API keys regularly

### Performance

1. **Tool Filtering:** Use specific tags to reduce tool discovery overhead
2. **Connection Pooling:** Reuse connections when possible
3. **Timeout Tuning:** Adjust timeouts based on network and platform performance
4. **Monitoring:** Track job metrics and platform health regularly

### Reliability

1. **Error Handling:** Implement retry logic for transient failures
2. **Health Checks:** Monitor platform connectivity regularly
3. **Backup Procedures:** Ensure configuration backups are automated
4. **Documentation:** Document custom workflows and procedures

### Integration

1. **Role-Based Access:** Configure different tool sets for different user roles
2. **Environment Separation:** Use different configurations for dev/test/prod
3. **Version Control:** Track configuration changes and tool updates
4. **Testing:** Validate configurations before production deployment

### AI Assistant Usage

1. **Clear Instructions:** Provide specific, actionable requests
2. **Context Awareness:** Understand which tools are available to your assistant
3. **Verification:** Always verify critical operations before execution
4. **Documentation:** Keep records of important automation workflows

## Next Steps

- **Explore Integration Options:** Review the [integration guide](integration.md) for your AI client
- **Learn About Tools:** Browse the [tools reference](tools.md) for complete capabilities
- **Understand Tagging:** Read the [tagging guide](tags.md) for advanced filtering
- **Set Up Workflows:** Check the [workflow execution guide](exposing-workflows.md)
- **Custom Development:** Learn about [creating custom tools](custom-tools.md)

## Support and Resources

- **Documentation:** Complete guides in the `docs/` directory
- **Examples:** Configuration examples for different use cases
- **Community:** Contribute to the project on GitHub
- **Issues:** Report problems and request features via GitHub issues

---

*This guide provides a comprehensive overview of the Itential MCP server. For specific technical details, refer to the individual documentation files linked throughout this guide.*