# Endpoint Tools Configuration

Endpoint tools provide a way to dynamically expose Itential Platform workflow triggers as MCP tools through configuration files. This allows you to create custom tools that execute specific workflows without writing code.

## Overview

Endpoint tools work by:
1. Reading tool definitions from configuration files
2. Looking up workflow triggers in Itential Platform
3. Creating dynamic MCP tools that execute those workflows
4. Automatically injecting tool configurations into function calls

## Configuration Methods

Endpoint tools can be configured using two methods:
1. **Configuration files** - Using INI format files
2. **Environment variables** - Using environment variables with a specific naming pattern

Both methods can be used together, with environment variables taking precedence over file configurations for the same tool properties.

## Configuration File Format

Endpoint tools are defined in configuration files using INI format. Each tool is configured in a section with the prefix `tool:` followed by the tool name.

### Basic Structure

```ini
[tool:my-workflow-tool]
type = endpoint
name = my-trigger-name
automation = my-automation-name
description = Execute my custom workflow
tags = custom,workflow
```

### Required Fields

| Field | Description |
|-------|-------------|
| `type` | Must be set to `endpoint` for endpoint tools |
| `name` | The name of the trigger in Itential Platform |
| `automation` | The name of the automation containing the trigger |

### Optional Fields

| Field | Description | Default |
|-------|-------------|---------|
| `description` | Description of the tool functionality | None |
| `tags` | Comma-separated list of additional tags | None |

## Environment Variable Configuration

As an alternative to configuration files, endpoint tools can be configured using environment variables. This method is particularly useful for containerized deployments, CI/CD pipelines, and environments where managing configuration files is challenging.

### Environment Variable Format

Environment variables follow the pattern: `ITENTIAL_MCP_TOOL_<tool_name>_<property>=<value>`

Where:
- `<tool_name>` is the name of your tool (alphanumeric and underscores only)
- `<property>` is the configuration property (type, name, automation, etc.)
- `<value>` is the property value

### Basic Example

```bash
# Define a provisioning tool via environment variables
export ITENTIAL_MCP_TOOL_PROVISION_DEVICE_TYPE=endpoint
export ITENTIAL_MCP_TOOL_PROVISION_DEVICE_NAME="Provision Network Device"
export ITENTIAL_MCP_TOOL_PROVISION_DEVICE_AUTOMATION="Device Management"
export ITENTIAL_MCP_TOOL_PROVISION_DEVICE_DESCRIPTION="Provision a new network device with standard configuration"
export ITENTIAL_MCP_TOOL_PROVISION_DEVICE_TAGS="provisioning,network,device"
```

This creates a tool equivalent to:
```ini
[tool:provision_device]
type = endpoint
name = Provision Network Device
automation = Device Management
description = Provision a new network device with standard configuration
tags = provisioning,network,device
```

### Multiple Tools Example

```bash
# Provisioning tool
export ITENTIAL_MCP_TOOL_PROVISION_DEVICE_TYPE=endpoint
export ITENTIAL_MCP_TOOL_PROVISION_DEVICE_NAME="Provision Network Device"
export ITENTIAL_MCP_TOOL_PROVISION_DEVICE_AUTOMATION="Device Management"

# Compliance tool
export ITENTIAL_MCP_TOOL_CHECK_COMPLIANCE_TYPE=endpoint
export ITENTIAL_MCP_TOOL_CHECK_COMPLIANCE_NAME="Security Compliance Check"
export ITENTIAL_MCP_TOOL_CHECK_COMPLIANCE_AUTOMATION="Compliance Automation"
export ITENTIAL_MCP_TOOL_CHECK_COMPLIANCE_TAGS="compliance,security,audit"

# Backup tool
export ITENTIAL_MCP_TOOL_BACKUP_CONFIG_TYPE=endpoint
export ITENTIAL_MCP_TOOL_BACKUP_CONFIG_NAME="Backup Device Configuration"
export ITENTIAL_MCP_TOOL_BACKUP_CONFIG_AUTOMATION="Backup Operations"
export ITENTIAL_MCP_TOOL_BACKUP_CONFIG_DESCRIPTION="Create backup of device configurations"
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
      ITENTIAL_MCP_TOOL_PROVISION_DEVICE_name: "Provision Network Device"
      ITENTIAL_MCP_TOOL_PROVISION_DEVICE_automation: "Device Management"
      ITENTIAL_MCP_TOOL_PROVISION_DEVICE_description: "Provision new network devices"

      ITENTIAL_MCP_TOOL_COMPLIANCE_CHECK_TYPE: endpoint
      ITENTIAL_MCP_TOOL_COMPLIANCE_CHECK_NAME: "Security Compliance Check"
      ITENTIAL_MCP_TOOL_COMPLIANCE_CHECK_AUTOMATION: "Compliance Automation"
      ITENTIAL_MCP_TOOL_COMPLIANCE_CHECK_TAGS: "compliance,security"
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
  # Tool configurations
  ITENTIAL_MCP_TOOL_PROVISION_DEVICE_TYPE: "endpoint"
  ITENTIAL_MCP_TOOL_PROVISION_DEVICE_name: "Provision Network Device"
  ITENTIAL_MCP_TOOL_PROVISION_DEVICE_automation: "Device Management"
  ITENTIAL_MCP_TOOL_PROVISION_DEVICE_description: "Provision new network devices"

  ITENTIAL_MCP_TOOL_BACKUP_CONFIG_TYPE: "endpoint"
  ITENTIAL_MCP_TOOL_BACKUP_CONFIG_NAME: "Backup Device Configuration"
  ITENTIAL_MCP_TOOL_BACKUP_CONFIG_AUTOMATION: "Backup Operations"

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
```

## How It Works

### 1. Configuration Parsing

The MCP server reads the configuration file at startup and identifies all `tool:*` sections. For each section with `type = endpoint`, it creates an `EndpointTool` configuration object.

### 2. Dynamic Tool Registration

During server initialization, the bindings system:

1. Looks up the specified automation in Itential Platform
2. Finds the trigger by name within that automation
3. Retrieves the trigger's JSON schema for input validation
4. Creates a dynamic MCP tool function
5. Registers the tool with the MCP server

### 3. Tool Execution

When a client calls the endpoint tool:

1. The DynamicToolInjectionMiddleware injects the tool configuration
2. The endpoint binding retrieves the trigger details from Platform
3. The tool delegates to the operations manager to start the workflow
4. The workflow execution result is returned to the client

## Trigger Requirements

For endpoint tools to work properly, the Itential Platform automation must have:

1. **An automation** - A named automation containing the workflow logic
2. **A trigger** - A specific trigger within that automation with:
   - A unique name matching the `name` field in configuration
   - An associated JSON schema defining expected input parameters
   - A route name for API access

## Tags

Tags control tool visibility and can be used for filtering. Endpoint tools automatically get these tags:

- `dynamic` - Added to all dynamically created tools
- The tool's `name` value from configuration
- Any additional tags specified in the `tags` field

Example with tag filtering:
```ini
[server]
include_tags = provisioning,backup
exclude_tags = experimental

[tool:device-backup]
tags = backup,production
# This tool will be included

[tool:experimental-feature]
tags = experimental
# This tool will be excluded
```

## Error Handling

Common configuration errors and solutions:

### Automation Not Found
```
Error: automation 'My Automation' could not be found
```
**Solution**: Verify the automation name exactly matches what's in Itential Platform.

### Trigger Not Found
```
Error: trigger 'My Trigger' could not be found
```
**Solution**: Check that the trigger name matches exactly and exists within the specified automation.

### Invalid Configuration
```
Error: tool configuration missing required field 'automation'
```
**Solution**: Ensure all required fields are present in the tool configuration section.

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

Endpoint tools work alongside the standard MCP tools. You can mix and match:

```ini
[server]
# Include both standard operations tools and custom endpoint tools
include_tags = operations,dynamic,custom-workflows
exclude_tags = experimental

[tool:custom-provisioning]
type = endpoint
name = Custom Device Provisioning
automation = Network Provisioning
tags = custom-workflows
```

This configuration would provide access to:
- Standard operations manager tools (tagged with `operations`)
- Your custom endpoint tool (tagged with `dynamic` and `custom-workflows`)
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
# Test with get_workflows tool to verify connectivity
await get_workflows(ctx)
```

### Check Tool Registration
Look for log messages during startup:
```
INFO: Registering dynamic tool: provision_network_device
INFO: Tool tags: dynamic,Provision Network Device,provisioning,network
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
Endpoint tools use the same platform authentication as other MCP tools. Ensure your service account has appropriate permissions for the workflows being exposed.

## Access Control
Use MCP tag filtering to control which tools are exposed to specific clients or environments.

### Environment Variable Security
When using environment variables:
- Avoid storing sensitive information (passwords, API keys) directly in environment variables when possible
- Use secure secret management systems (Docker Secrets, Kubernetes Secrets, etc.)
- Be cautious with environment variable visibility in process lists and logs
- Consider using configuration files for sensitive data with appropriate file permissions
