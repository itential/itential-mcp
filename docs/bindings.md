# Tool Bindings Configuration

Tool bindings provide ways to dynamically expose Itential Platform automation capabilities as MCP tools through configuration files. This allows you to create custom tools that execute workflows or external services without writing code.

## Overview

**Endpoint tools** work by:
1. Reading tool definitions from configuration files
2. Looking up workflow endpoint triggers in Itential Platform
3. Creating dynamic MCP tools that execute those workflows
4. Automatically injecting tool configurations into function calls

**Service tools** work by:
1. Reading tool definitions from configuration files
2. Looking up services in Itential Platform Gateway Manager
3. Creating dynamic MCP tools that execute those services
4. Automatically injecting tool configurations and input parameters into service calls

## Configuration Methods

Both endpoint tools and service tools can be configured using two methods:
1. **Configuration files** - Using INI format files
2. **Environment variables** - Using environment variables with a specific naming pattern

Both methods can be used together, with environment variables taking precedence over file configurations for the same tool properties.

## Configuration File Format

Tools are defined in configuration files using INI format. Each tool is configured in a section with the prefix `tool:` followed by the tool name.

### Endpoint Tools

```ini
[tool:my-workflow-tool]
type = endpoint
name = my-trigger-name
automation = my-automation-name
description = Execute my custom workflow
tags = custom,workflow
```

#### Required Fields for Endpoint Tools

| Field | Description |
|-------|-------------|
| `type` | Must be set to `endpoint` for endpoint tools |
| `name` | The name of the trigger in Itential Platform |
| `automation` | The name of the automation containing the trigger |

### Service Tools

```ini
[tool:my-service-tool]
type = service
name = my-service-name
cluster = my-cluster-name
description = Execute my external service
tags = custom,service
```

#### Required Fields for Service Tools

| Field | Description |
|-------|-------------|
| `type` | Must be set to `service` for service tools |
| `name` | The name of the service in Itential Platform Gateway Manager |
| `cluster` | The name of the cluster containing the service |

### Optional Fields (Both Tool Types)

| Field | Description | Default |
|-------|-------------|---------|
| `description` | Description of the tool functionality | None |
| `tags` | Comma-separated list of additional tags | None |

## Environment Variable Configuration

As an alternative to configuration files, both endpoint and service tools can be configured using environment variables. This method is particularly useful for containerized deployments, CI/CD pipelines, and environments where managing configuration files is challenging.

### Environment Variable Format

Environment variables follow the pattern: `ITENTIAL_MCP_TOOL_<tool_name>_<property>=<value>`

Where:
- `<tool_name>` is the name of your tool (alphanumeric and underscores only)
- `<property>` is the configuration property (type, name, automation, cluster, etc.)
- `<value>` is the property value

### Endpoint Tool Example

```bash
# Define a provisioning tool via environment variables
export ITENTIAL_MCP_TOOL_PROVISION_DEVICE_TYPE=endpoint
export ITENTIAL_MCP_TOOL_PROVISION_DEVICE_NAME="Provision Network Device"
export ITENTIAL_MCP_TOOL_PROVISION_DEVICE_AUTOMATION="Device Management"
export ITENTIAL_MCP_TOOL_PROVISION_DEVICE_DESCRIPTION="Provision a new network device with standard configuration"
export ITENTIAL_MCP_TOOL_PROVISION_DEVICE_TAGS="provisioning,network,device"
```

This creates an endpoint tool equivalent to:
```ini
[tool:provision_device]
type = endpoint
name = Provision Network Device
automation = Device Management
description = Provision a new network device with standard configuration
tags = provisioning,network,device
```

### Service Tool Example

```bash
# Define a service tool via environment variables
export ITENTIAL_MCP_TOOL_RUN_PLAYBOOK_TYPE=service
export ITENTIAL_MCP_TOOL_RUN_PLAYBOOK_NAME="network-config-playbook"
export ITENTIAL_MCP_TOOL_RUN_PLAYBOOK_CLUSTER="ansible-cluster"
export ITENTIAL_MCP_TOOL_RUN_PLAYBOOK_DESCRIPTION="Execute Ansible playbook for network configuration"
export ITENTIAL_MCP_TOOL_RUN_PLAYBOOK_TAGS="ansible,configuration,service"
```

This creates a service tool equivalent to:
```ini
[tool:run_playbook]
type = service
name = network-config-playbook
cluster = ansible-cluster
description = Execute Ansible playbook for network configuration
tags = ansible,configuration,service
```

### Multiple Tools Example

```bash
# Endpoint tool for provisioning
export ITENTIAL_MCP_TOOL_PROVISION_DEVICE_TYPE=endpoint
export ITENTIAL_MCP_TOOL_PROVISION_DEVICE_NAME="Provision Network Device"
export ITENTIAL_MCP_TOOL_PROVISION_DEVICE_AUTOMATION="Device Management"

# Endpoint tool for compliance
export ITENTIAL_MCP_TOOL_CHECK_COMPLIANCE_TYPE=endpoint
export ITENTIAL_MCP_TOOL_CHECK_COMPLIANCE_NAME="Security Compliance Check"
export ITENTIAL_MCP_TOOL_CHECK_COMPLIANCE_AUTOMATION="Compliance Automation"
export ITENTIAL_MCP_TOOL_CHECK_COMPLIANCE_TAGS="compliance,security,audit"

# Service tool for running scripts
export ITENTIAL_MCP_TOOL_RUN_SCRIPT_TYPE=service
export ITENTIAL_MCP_TOOL_RUN_SCRIPT_NAME="backup-script"
export ITENTIAL_MCP_TOOL_RUN_SCRIPT_CLUSTER="python-cluster"
export ITENTIAL_MCP_TOOL_RUN_SCRIPT_DESCRIPTION="Execute Python backup script"
export ITENTIAL_MCP_TOOL_RUN_SCRIPT_TAGS="backup,python,service"
```

### Docker Compose Example

```yaml
version: '3.8'
services:
  itential-mcp:
    image: itential/mcp-server
    environment:
      # Server configuration
      ITENTIAL_MCP_SERVER_TRANSPORT: sse
      ITENTIAL_MCP_SERVER_HOST: 0.0.0.0
      ITENTIAL_MCP_SERVER_PORT: 8000

      # Platform connection
      ITENTIAL_MCP_PLATFORM_HOST: platform.company.com
      ITENTIAL_MCP_PLATFORM_USER: service-account
      ITENTIAL_MCP_PLATFORM_PASSWORD: secret123

      # Endpoint tools
      ITENTIAL_MCP_TOOL_PROVISION_DEVICE_TYPE: endpoint
      ITENTIAL_MCP_TOOL_PROVISION_DEVICE_NAME: "Provision Network Device"
      ITENTIAL_MCP_TOOL_PROVISION_DEVICE_AUTOMATION: "Device Management"
      ITENTIAL_MCP_TOOL_PROVISION_DEVICE_DESCRIPTION: "Provision new network devices"

      ITENTIAL_MCP_TOOL_COMPLIANCE_CHECK_TYPE: endpoint
      ITENTIAL_MCP_TOOL_COMPLIANCE_CHECK_NAME: "Security Compliance Check"
      ITENTIAL_MCP_TOOL_COMPLIANCE_CHECK_AUTOMATION: "Compliance Automation"
      ITENTIAL_MCP_TOOL_COMPLIANCE_CHECK_TAGS: "compliance,security"

      # Service tools
      ITENTIAL_MCP_TOOL_RUN_PLAYBOOK_TYPE: service
      ITENTIAL_MCP_TOOL_RUN_PLAYBOOK_NAME: "network-config-playbook"
      ITENTIAL_MCP_TOOL_RUN_PLAYBOOK_CLUSTER: "ansible-cluster"
      ITENTIAL_MCP_TOOL_RUN_PLAYBOOK_DESCRIPTION: "Execute network configuration playbooks"
      ITENTIAL_MCP_TOOL_RUN_PLAYBOOK_TAGS: "ansible,automation,service"

      ITENTIAL_MCP_TOOL_BACKUP_SCRIPT_TYPE: service
      ITENTIAL_MCP_TOOL_BACKUP_SCRIPT_NAME: "device-backup"
      ITENTIAL_MCP_TOOL_BACKUP_SCRIPT_CLUSTER: "python-cluster"
      ITENTIAL_MCP_TOOL_BACKUP_SCRIPT_TAGS: "backup,python,service"
    ports:
      - "8000:8000"
```

### Kubernetes ConfigMap Example

```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: itential-mcp-config
data:
  # Endpoint tool configurations
  ITENTIAL_MCP_TOOL_PROVISION_DEVICE_TYPE: "endpoint"
  ITENTIAL_MCP_TOOL_PROVISION_DEVICE_NAME: "Provision Network Device"
  ITENTIAL_MCP_TOOL_PROVISION_DEVICE_AUTOMATION: "Device Management"
  ITENTIAL_MCP_TOOL_PROVISION_DEVICE_DESCRIPTION: "Provision new network devices"

  ITENTIAL_MCP_TOOL_BACKUP_CONFIG_TYPE: "endpoint"
  ITENTIAL_MCP_TOOL_BACKUP_CONFIG_NAME: "Backup Device Configuration"
  ITENTIAL_MCP_TOOL_BACKUP_CONFIG_AUTOMATION: "Backup Operations"

  # Service tool configurations
  ITENTIAL_MCP_TOOL_RUN_PLAYBOOK_TYPE: "service"
  ITENTIAL_MCP_TOOL_RUN_PLAYBOOK_NAME: "network-config-playbook"
  ITENTIAL_MCP_TOOL_RUN_PLAYBOOK_CLUSTER: "ansible-cluster"
  ITENTIAL_MCP_TOOL_RUN_PLAYBOOK_DESCRIPTION: "Execute network configuration playbooks"

  ITENTIAL_MCP_TOOL_PYTHON_SCRIPT_TYPE: "service"
  ITENTIAL_MCP_TOOL_PYTHON_SCRIPT_NAME: "device-backup"
  ITENTIAL_MCP_TOOL_PYTHON_SCRIPT_CLUSTER: "python-cluster"
  ITENTIAL_MCP_TOOL_PYTHON_SCRIPT_TAGS: "backup,python,service"

---
apiVersion: apps/v1
kind: Deployment
metadata:
  name: itential-mcp
spec:
  template:
    spec:
      containers:
      - name: mcp-server
        image: itential/mcp-server
        envFrom:
        - configMapRef:
            name: itential-mcp-config
```

### Environment Variable Validation

Environment variables are validated the same way as configuration file entries:

- **Tool names** must start with a letter and contain only letters, numbers, and underscores
- **Required fields** (type, name, automation) must be present
- **Invalid formats** will generate clear error messages

Example validation error:
```bash
export ITENTIAL_MCP_TOOL_123invalid_TYPE=endpoint
# Error: Tool name '123invalid' is invalid. Tool names must start with a letter and only contain letters, numbers, and underscores.

export ITENTIAL_MCP_TOOL_MYTOOL_INVALIDFORMAT=value
# Error: Invalid tool environment variable format: ITENTIAL_MCP_TOOL_mytool_invalidformat. Expected format: ITENTIAL_MCP_TOOL_<tool_name>_<key>=<value>
```

## Hybrid Configuration

You can combine both configuration methods. Environment variables will override file-based configurations for the same tool properties:

**config.ini:**
```ini
[tool:provision_device]
type = endpoint
name = Provision Network Device
automation = Device Management
description = Basic provisioning workflow
tags = provisioning
```

**Environment variables:**
```bash
# Override description and add tags
export ITENTIAL_MCP_TOOL_PROVISION_DEVICE_DESCRIPTION="Enhanced provisioning with validation and rollback"
export ITENTIAL_MCP_TOOL_PROVISION_DEVICE_TAGS="provisioning,network,validated"
```

**Result:** The tool will use the file configuration but with the description and tags from environment variables.

## Complete Example Configuration

```ini
# Server configuration
[server]
transport = sse
host = 0.0.0.0
port = 8000
log_level = INFO

# Platform connection
[platform]
host = my-platform.company.com
user = service-account
password = secret123

# Endpoint tool for device provisioning
[tool:provision-device]
type = endpoint
name = Provision Network Device
automation = Device Management
description = Provision a new network device with standard configuration
tags = provisioning,network,device

# Endpoint tool for compliance checking
[tool:check-compliance]
type = endpoint
name = Security Compliance Check
automation = Compliance Automation
description = Run security compliance checks across network devices
tags = compliance,security,audit

# Service tool for running Ansible playbooks
[tool:run-playbook]
type = service
name = network-config-playbook
cluster = ansible-cluster
description = Execute Ansible playbooks for network configuration
tags = ansible,automation,service

# Service tool for running Python scripts
[tool:backup-script]
type = service
name = device-backup-script
cluster = python-cluster
description = Execute Python script for device configuration backup
tags = backup,python,script,service
```

## How It Works

### 1. Configuration Parsing

The MCP server reads the configuration file at startup and identifies all `tool:*` sections. For each section:
- `type = endpoint` creates an `EndpointTool` configuration object
- `type = service` creates a `ServiceTool` configuration object

### 2. Dynamic Tool Registration

During server initialization, the bindings system handles each tool type differently:

**For Endpoint Tools:**
1. Looks up the specified automation in Itential Platform
2. Finds the trigger by name within that automation
3. Retrieves the trigger's JSON schema for input validation
4. Creates a dynamic MCP tool function
5. Registers the tool with the MCP server

**For Service Tools:**
1. Looks up the specified service in Itential Platform Gateway Manager
2. Finds the service by name within the specified cluster
3. Retrieves the service's JSON schema (decorator) for input validation
4. Creates a dynamic MCP tool function
5. Registers the tool with the MCP server

## Requirements

### Endpoint Tool Requirements

For endpoint tools to work properly, the Itential Platform automation must have:

1. **An automation** - A named automation containing the workflow logic
2. **A trigger** - A specific trigger within that automation with:
   - A unique name matching the `name` field in configuration
   - An associated JSON schema defining expected input parameters
   - A route name for API access

### Service Tool Requirements

For service tools to work properly, the Itential Platform Gateway Manager must have:

1. **A cluster** - A named cluster containing the service
2. **A service** - A specific service within that cluster with:
   - A unique name matching the `name` field in configuration
   - A service type (ansible-playbook, python-script, opentofu-plan, etc.)
   - An associated JSON schema (decorator) defining expected input parameters
   - The service must be enabled and available for execution

## Tags

Tags control tool visibility and can be used for filtering. Both endpoint and service tools automatically get these tags:

- `bindings` - Added to all dynamically created tools
- The tool's `name` value from configuration
- Any additional tags specified in the `tags` field

Example with tag filtering:
```ini
[server]
include_tags = provisioning,backup,service
exclude_tags = experimental

[tool:device-backup]
type = endpoint
tags = backup,production
# This endpoint tool will be included

[tool:run-script]
type = service
tags = service,python
# This service tool will be included

[tool:experimental-feature]
type = endpoint
tags = experimental
# This tool will be excluded
```

## Error Handling

Common configuration errors and solutions:

### Endpoint Tool Errors

**Automation Not Found:**
```
Error: automation 'My Automation' could not be found
```
**Solution**: Verify the automation name exactly matches what's in Itential Platform.

**Trigger Not Found:**
```
Error: trigger 'My Trigger' could not be found
```
**Solution**: Check that the trigger name matches exactly and exists within the specified automation.

**Missing Automation Field:**
```
Error: tool configuration missing required field 'automation'
```
**Solution**: Ensure all required fields (type, name, automation) are present in the endpoint tool configuration.

### Service Tool Errors

**Cluster Not Found:**
```
Error: cluster 'My Cluster' could not be found
```
**Solution**: Verify the cluster name exactly matches what's configured in Itential Platform Gateway Manager.

**Service Not Found:**
```
Error: service 'My Service' could not be found in cluster 'My Cluster'
```
**Solution**: Check that the service name matches exactly and exists within the specified cluster.

**Missing Cluster Field:**
```
Error: tool configuration missing required field 'cluster'
```
**Solution**: Ensure all required fields (type, name, cluster) are present in the service tool configuration.

### General Configuration Errors

**Invalid Tool Type:**
```
Error: invalid tool type 'invalid-type'. Must be 'endpoint' or 'service'
```
**Solution**: Set the `type` field to either `endpoint` or `service`.

## Best Practices

### 1. Descriptive Naming
Use clear, descriptive names for tools and include context about what they do:

```ini
[tool:cisco-router-provisioning]
description = Provision new Cisco router with standard enterprise configuration
```

### 2. Consistent Tagging
Develop a consistent tagging strategy for easy filtering:

```ini
# By function
tags = provisioning,configuration,deployment

# By device type
tags = cisco,juniper,arista

# By environment
tags = production,staging,development
```

### 3. Environment-Specific Configurations
Use different approaches for different environments:

**Configuration Files:**
```bash
# Development
itential-mcp --config dev-config.ini

# Production
itential-mcp --config prod-config.ini
```

**Environment Variables:**
```bash
# Development
export ITENTIAL_MCP_PLATFORM_HOST=dev-platform.company.com
export ITENTIAL_MCP_TOOL_DEBUG_WORKFLOW_TYPE=endpoint

# Production
export ITENTIAL_MCP_PLATFORM_HOST=prod-platform.company.com
export ITENTIAL_MCP_SERVER_EXCLUDE_TAGS=debug,experimental
```

### 4. Documentation
Always include meaningful descriptions that explain:
- What the tool does
- What parameters it expects
- What results it returns

## Integration with Existing Tools

Both endpoint tools and service tools work alongside the standard MCP tools. You can mix and match:

```ini
[server]
# Include standard operations tools, custom endpoint tools, and service tools
include_tags = operations,bindings,custom-workflows,services
exclude_tags = experimental

[tool:custom-provisioning]
type = endpoint
name = Custom Device Provisioning
automation = Network Provisioning
tags = custom-workflows

[tool:ansible-playbook]
type = service
name = network-config-playbook
cluster = ansible-cluster
tags = services,ansible
```

This configuration would provide access to:
- Standard operations manager tools (tagged with `operations`)
- Your custom endpoint tools (tagged with `bindings` and `custom-workflows`)
- Your custom service tools (tagged with `bindings` and `services`)
- All other default tools

## Troubleshooting

### Enable Debug Logging
```ini
[server]
log_level = DEBUG
```

### Verify Platform Connectivity
Test your platform connection settings using the standard tools first:
```python
# Test with get_workflows tool to verify endpoint connectivity
await get_workflows(ctx)

# Test with get_services tool to verify Gateway Manager connectivity
await get_services(ctx)
```

### Check Tool Registration
Look for log messages during startup:
```
INFO: Registering dynamic tool: provision_network_device
INFO: Tool tags: dynamic,Provision Network Device,provisioning,network

INFO: Registering dynamic tool: run_ansible_playbook
INFO: Tool tags: dynamic,network-config-playbook,ansible,service
```

### Debug Environment Variables
List all tool-related environment variables:
```bash
# List all Itential MCP tool environment variables
env | grep ITENTIAL_MCP_TOOL | sort

# Check specific tool configuration
env | grep ITENTIAL_MCP_TOOL_provision_device
```

### Validate Environment Variable Format
Common environment variable issues:

**Invalid tool name:**
```bash
# ❌ Invalid: starts with number
ITENTIAL_MCP_TOOL_123TOOL_TYPE=endpoint

# ✅ Valid: starts with letter
ITENTIAL_MCP_TOOL_TOOL123_TYPE=endpoint
```

**Missing components:**
```bash
# ❌ Invalid: missing property
ITENTIAL_MCP_TOOL_MYTOOL=endpoint

# ✅ Valid: includes property
ITENTIAL_MCP_TOOL_MYTOOL_TYPE=endpoint
```

**Empty values:**
```bash
# ❌ Invalid: empty tool name
ITENTIAL_MCP_TOOL__TYPE=endpoint

# ❌ Invalid: empty property
ITENTIAL_MCP_TOOL_MYTOOL_=endpoint

# ✅ Valid: empty value is allowed
ITENTIAL_MCP_TOOL_MYTOOL_DESCRIPTION=""
```

## Security Considerations

### Authentication
Both endpoint tools and service tools use the same platform authentication as other MCP tools:

- **Endpoint tools** require permissions to execute workflows and automations in Itential Platform
- **Service tools** require permissions to execute services through Itential Platform Gateway Manager

Ensure your service account has appropriate permissions for the workflows and services being exposed.

### Access Control
Use MCP tag filtering to control which tools are exposed to specific clients or environments.

### Service vs Endpoint Security
- **Endpoint tools** execute within the Itential Platform environment and follow its security model
- **Service tools** execute external services (Ansible, Python scripts, etc.) which may have different security implications
- Consider the trust level of external service execution when exposing service tools

### Environment Variable Security
When using environment variables:
- Avoid storing sensitive information (passwords, API keys) directly in environment variables when possible
- Use secure secret management systems (Docker Secrets, Kubernetes Secrets, etc.)
- Be cautious with environment variable visibility in process lists and logs
- Consider using configuration files for sensitive data with appropriate file permissions
