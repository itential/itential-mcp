# Endpoint Tools Configuration

Endpoint tools provide a way to dynamically expose Itential Platform workflow triggers as MCP tools through configuration files. This allows you to create custom tools that execute specific workflows without writing code.

## Overview

Endpoint tools work by:
1. Reading tool definitions from configuration files
2. Looking up workflow triggers in Itential Platform
3. Creating dynamic MCP tools that execute those workflows
4. Automatically injecting tool configurations into function calls

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
Use different configuration files for different environments:

```bash
# Development
itential-mcp --config dev-config.ini

# Production
itential-mcp --config prod-config.ini
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

## Security Considerations

### Authentication
Endpoint tools use the same platform authentication as other MCP tools. Ensure your service account has appropriate permissions for the workflows being exposed.

### Input Validation
The tool automatically uses the trigger's JSON schema for input validation. Make sure your Platform triggers have proper schema definitions.

### Access Control
Use MCP tag filtering to control which tools are exposed to specific clients or environments.
