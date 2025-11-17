# Itential MCP Server Documentation

The Itential MCP (Model Context Protocol) server enables AI assistants to interact directly with your Itential Platform for powerful network automation and management capabilities.

## Quick Start

New to the MCP server? Start here:

1. **[User Guide](user-guide.md)** - Installation, setup, and basic usage
2. **[Integration Guide](integration.md)** - Connect your AI client (Claude Desktop, Continue.dev, etc.)
3. **[Tools Reference](tools.md)** - Explore 50+ available automation tools

## Documentation Sections

### Getting Started

- **[User Guide](user-guide.md)** - Complete installation and usage guide
- **[Integration Guide](integration.md)** - Connect AI clients (Claude Desktop, Continue.dev)
- **[TLS Configuration](tls.md)** - Enable secure connections

### Configuration & Security

- **[Configuration Reference](mcp.conf.example)** - Complete configuration file with all options
- **[Status Endpoints](status-endpoints.md)** - Health monitoring for production deployments
- **[JWT Authentication](jwt-authentication.md)** - JWT token authentication setup
- **[OAuth Authentication](oauth-authentication.md)** - OAuth 2.0 with Google, Azure, Auth0, GitHub, Okta

### Tools & Features

- **[Tools Reference](tools.md)** - All 50+ tools organized by category
- **[Tagging System](tags.md)** - Filter tools by role and functionality
- **[Workflow Execution](exposing-workflows.md)** - Execute and monitor Itential workflows
- **[TOON Response Format](toon.md)** - LLM-optimized serialization with 30-60% token reduction

### Advanced Usage

- **[Custom Tools Development](custom-tools.md)** - Create and integrate custom MCP tools
- **[AI Assistant Configurations](ai-assistant-configs.md)** - Optimize AI client configurations  
- **[Bindings](bindings.md)** - Python SDK and API client patterns

## By User Role

### 👨‍💼 Platform Administrators
System health, component management, platform operations
- **Tools:** `system`, `adapters`, `applications`, `integrations`
- **Focus:** [Status monitoring](status-endpoints.md), [system tools](tools.md#system-management-tools)

### 👨‍💻 Network Engineers  
Device management, configurations, compliance, network automation
- **Tools:** `devices`, `configuration_manager`, `automation_studio`
- **Focus:** [Device tools](tools.md#device-management-tools), [workflows](exposing-workflows.md)

### 🔧 Automation Developers
Workflow building, performance analysis, platform extension
- **Tools:** `operations_manager`, `workflow_engine`, `lifecycle_manager`
- **Focus:** [Custom tools](custom-tools.md), [workflow engine](tools.md#workflow-engine-tools)

### 🎯 Platform Operators
Daily operations, job monitoring, report generation
- **Tools:** `operations_manager`, `devices`, `configuration_manager`
- **Focus:** [Operations tools](tools.md#operations-management-tools), [basic config](integration.md)

## By Tool Category

| Category | Tags | Description |
|----------|------|-------------|
| **System Management** | `system`, `adapters`, `applications` | Platform health and monitoring |
| **Device Management** | `devices`, `configuration_manager` | Network device operations |
| **Workflow Operations** | `operations_manager`, `workflow_engine` | Automation and job management |
| **Command Execution** | `automation_studio` | Template and command automation |
| **External Services** | `gateway_manager`, `integrations` | Gateway and integration management |
| **Lifecycle Management** | `lifecycle_manager` | Resource state and lifecycle workflows |

See [Tools Reference](tools.md) for complete details on each category.

## Quick Reference

### Installation & Basic Usage
```bash
# Install
pip install itential-mcp

# Start server (stdio mode for AI clients)
itential-mcp

# Start with web interface
itential-mcp --transport sse --host 0.0.0.0 --port 8000

# Role-specific tools
itential-mcp --include-tags "system,devices"
```

### Environment Variables
```bash
# Platform connection
ITENTIAL_MCP_PLATFORM_HOST="platform.example.com"
ITENTIAL_MCP_PLATFORM_USER="username"
ITENTIAL_MCP_PLATFORM_PASSWORD="password"
```

### Example AI Prompts
- "Show me the health status of the platform"
- "List all available workflows"
- "Get configuration for router-01"  
- "Run compliance check on datacenter devices"
- "Start the device backup workflow"

## Example Configurations

### Claude Desktop - Basic Setup
```json
{
  "mcpServers": {
    "itential": {
      "command": "itential-mcp",
      "env": {
        "ITENTIAL_MCP_PLATFORM_HOST": "platform.example.com",
        "ITENTIAL_MCP_PLATFORM_USER": "mcp-user",
        "ITENTIAL_MCP_PLATFORM_PASSWORD": "secure-password"
      }
    }
  }
}
```

### Claude Desktop - Network Engineer Role
```json
{
  "mcpServers": {
    "itential-netops": {
      "command": "itential-mcp", 
      "args": ["--include-tags", "devices,configuration_manager,automation_studio"],
      "env": {
        "ITENTIAL_MCP_PLATFORM_HOST": "platform.example.com",
        "ITENTIAL_MCP_PLATFORM_USER": "netops-user",
        "ITENTIAL_MCP_PLATFORM_PASSWORD": "netops-password"
      }
    }
  }
}
```

## Getting Help

- **[Troubleshooting](user-guide.md#troubleshooting)** - Common issues and solutions
- **[Debug Mode](integration.md#debug-mode)** - Diagnostic tools and logging
- **GitHub Issues** - Report bugs and request features

### Quick Diagnostics
```bash
# Test connection
curl -k https://your-platform.example.com/health

# Debug mode  
itential-mcp --log-level DEBUG

# Test specific tools
itential-mcp --include-tags "system" --transport sse --port 8001
```

## External Resources

- **[Itential Platform](https://www.itential.com/)** - Official Itential website
- **[Model Context Protocol](https://spec.modelcontextprotocol.io/)** - MCP specification
- **[FastMCP Framework](https://fastmcp.com)** - MCP server development framework

---

**Ready to get started?** Begin with the [User Guide](user-guide.md) for installation and setup, then configure your AI client using the [Integration Guide](integration.md).