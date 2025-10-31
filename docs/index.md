# Itential MCP Server Documentation

Welcome to the comprehensive documentation for the Itential MCP (Model Context Protocol) server. This documentation will help you integrate AI assistants with your Itential Platform for powerful network automation and management capabilities.

## 📖 Documentation Overview

This documentation is organized into several categories to help you find the information you need quickly:

### 🚀 Getting Started

Perfect for new users who want to get up and running quickly.

- **[User Guide](user-guide.md)** - Comprehensive guide from installation to advanced usage
  - Installation and setup
  - Basic usage patterns
  - Configuration options
  - Role-based workflows
  - Troubleshooting and best practices

- **[Integration Guide](integration.md)** - Connect your AI clients to the MCP server
  - MCP client configuration
  - Claude Desktop, Continue.dev, and generic client setup
  - Authentication methods
  - Security considerations

### 🔧 Configuration & Setup

Detailed configuration guides for different deployment scenarios.

- **[Configuration File Example](mcp.conf.example)** - Complete configuration file reference
  - All available options
  - Environment variable mappings
  - Example configurations for different environments

- **[JWT Authentication](jwt-authentication.md)** - OAuth 2.0 and JWT authentication setup
  - OAuth configuration
  - Token management
  - Security best practices

### 🛠️ Tools & Features

Understand what the MCP server can do for you.

- **[Tools Reference](tools.md)** - Complete list of available tools
  - All 50+ available tools organized by category
  - Tool descriptions and capabilities
  - Tag associations for filtering

- **[Tagging System](tags.md)** - Advanced tool filtering and selection
  - Available tag categories
  - Tool filtering strategies
  - Role-based access control

- **[Workflow Execution](exposing-workflows.md)** - Execute Itential workflows via MCP
  - Workflow discovery and execution
  - Job monitoring and metrics
  - Workflow exposure as APIs

### 🎯 Advanced Usage

For power users and developers who want to extend functionality.

- **[Custom Tools Development](custom-tools.md)** - Create your own MCP tools
  - Tool development patterns
  - Integration with Itential APIs
  - Best practices and examples

- **[AI Assistant Configurations](ai-assistant-configs.md)** - Optimize your AI assistant setup
  - Client-specific optimizations
  - Prompt engineering for Itential workflows
  - Performance tuning

- **[Bindings](bindings.md)** - Language bindings and SDK integration
  - Python SDK usage
  - API client configuration
  - Development patterns

## 🎭 By User Role

Choose your role to see the most relevant documentation:

### Platform Administrators
Focus on system health, component management, and platform operations.

**Recommended Reading:**
1. [User Guide - Platform Administrator Section](user-guide.md#platform-administrator)
2. [Tools Reference - System & Applications](tools.md#system-management-tools)
3. [Integration Guide - Security](integration.md#security-considerations)

**Key Tools:** `system`, `adapters`, `applications`, `integrations`

### Network Engineers  
Manage devices, configurations, compliance, and network automation.

**Recommended Reading:**
1. [User Guide - Network Engineer Section](user-guide.md#network-engineer)
2. [Tools Reference - Device & Configuration Management](tools.md#device-management-tools)
3. [Workflow Execution Guide](exposing-workflows.md)

**Key Tools:** `devices`, `configuration_manager`, `automation_studio`

### Automation Developers
Build workflows, analyze performance, and extend platform capabilities.

**Recommended Reading:**
1. [User Guide - Automation Developer Section](user-guide.md#automation-developer)
2. [Custom Tools Development](custom-tools.md)
3. [Workflow Engine Reference](tools.md#workflow-engine-tools)

**Key Tools:** `operations_manager`, `workflow_engine`, `lifecycle_manager`, `gateway_manager`

### Platform Operators
Execute daily operations, monitor jobs, and generate reports.

**Recommended Reading:**
1. [User Guide - Platform Operator Section](user-guide.md#platform-operator)
2. [Tools Reference - Operations Management](tools.md#operations-management-tools)
3. [Integration Guide - Basic Configuration](integration.md#basic-configuration)

**Key Tools:** `operations_manager`, `devices`, `configuration_manager`

## 🏷️ By Tool Category

Find documentation organized by the type of work you want to accomplish:

### System Management
Monitor platform health and manage system components.
- Tools: [System Tools](tools.md#system-management-tools)
- Tags: `system`, `adapters`, `applications`

### Device & Network Management  
Manage network devices, configurations, and compliance.
- Tools: [Device Tools](tools.md#device-management-tools)
- Tags: `devices`, `configuration_manager`

### Workflow & Automation
Execute workflows and track automation jobs.
- Tools: [Workflow Tools](tools.md#workflow-management-tools) 
- Tags: `operations_manager`, `workflow_engine`

### Command Execution
Run commands and templates across your infrastructure.
- Tools: [Command Tools](tools.md#command-execution-tools)
- Tags: `automation_studio`

### External Integrations
Connect with external services and systems.
- Tools: [Integration Tools](tools.md#integration-tools)
- Tags: `gateway_manager`, `integrations`

### Lifecycle Management
Manage stateful resources and their lifecycle workflows.
- Tools: [Lifecycle Tools](tools.md#lifecycle-management-tools)
- Tags: `lifecycle_manager`

## 🔍 Quick Reference

### Essential Commands

```bash
# Install the server
pip install itential-mcp

# Basic startup
itential-mcp run

# Web interface startup  
itential-mcp run --transport sse --host 0.0.0.0 --port 8000

# Role-specific configurations
itential-mcp run --include-tags "system,devices"
```

### Key Environment Variables

```bash
# Platform connection
ITENTIAL_MCP_PLATFORM_HOST="platform.example.com"
ITENTIAL_MCP_PLATFORM_USER="username"  
ITENTIAL_MCP_PLATFORM_PASSWORD="password"

# Server options
ITENTIAL_MCP_SERVER_TRANSPORT="sse"
ITENTIAL_MCP_SERVER_LOG_LEVEL="INFO"
```

### Common AI Assistant Requests

```text
"Show me the health status of the platform"
"List all available workflows"  
"Get configuration for router-01"
"Run compliance check on datacenter devices"
"Start the device backup workflow"
"Show me performance metrics for recent jobs"
```

## 📊 Tool Categories Overview

| Category | Tools Count | Primary Use Case |
|----------|-------------|------------------|
| **System Management** | 5+ | Platform health and monitoring |
| **Device Management** | 10+ | Network device operations |
| **Workflow Operations** | 15+ | Automation and job management |
| **Command Execution** | 8+ | Template and command automation |
| **External Services** | 5+ | Gateway and integration management |
| **Lifecycle Management** | 10+ | Resource state and lifecycle workflows |
| **Applications/Adapters** | 8+ | Component lifecycle management |

## 🔗 External Resources

### Official Links
- **Itential Platform**: [https://www.itential.com/](https://www.itential.com/)
- **Model Context Protocol**: [https://spec.modelcontextprotocol.io/](https://spec.modelcontextprotocol.io/)
- **Python SDK (ipsdk)**: Integration library for Itential Platform

### AI Client Resources  
- **Claude Desktop**: MCP client configuration
- **Continue.dev**: Development-focused AI assistant
- **Generic MCP Clients**: Standard MCP integration patterns

### Development Resources
- **FastMCP Framework**: MCP server development framework
- **Pydantic**: Data validation and serialization
- **AsyncIO**: Asynchronous programming patterns

## 📋 Example Configurations

### Basic Configuration (Claude Desktop)
```json
{
  "mcpServers": {
    "itential-platform": {
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

### Role-Based Configuration
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

## 🆘 Getting Help

### Troubleshooting
- **[User Guide - Troubleshooting](user-guide.md#troubleshooting)** - Common issues and solutions
- **[Integration Guide - Debug Mode](integration.md#debug-mode)** - Diagnostic tools and logging

### Support Channels
- **GitHub Issues**: Report bugs and request features
- **Documentation**: Comprehensive guides and references
- **Community**: Contribute to the project development

### Quick Diagnostics

```bash
# Test connection
curl -k https://your-platform.example.com/health

# Debug mode
itential-mcp run --log-level DEBUG

# Check available tools
itential-mcp run --include-tags "system" --transport sse --port 8001
```

## 🚀 Next Steps

1. **Start with the [User Guide](user-guide.md)** for comprehensive setup instructions
2. **Configure your AI client** using the [Integration Guide](integration.md)  
3. **Explore available tools** in the [Tools Reference](tools.md)
4. **Optimize for your role** using the role-based documentation sections
5. **Extend functionality** with [Custom Tools](custom-tools.md) if needed

---

*Welcome to the powerful world of AI-assisted network automation with Itential MCP server. Choose your starting point above and begin transforming how you manage your network infrastructure.*