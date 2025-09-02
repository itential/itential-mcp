# Itential MCP Server Integration Guide

This document explains how to integrate the Itential MCP (Model Context Protocol) server with MCP clients using JSON configuration files.

## Overview

The Itential MCP server provides network automation capabilities through the Model Context Protocol, enabling AI assistants and other MCP clients to interact with Itential Platform APIs. Integration is accomplished through JSON configuration files that define server connection details, authentication, and optional tool filtering.

## Basic Configuration

### MCP Client Configuration Format

Most MCP clients use a JSON configuration file to define available servers. Here's the basic structure:

```json
{
  "mcpServers": {
    "itential-platform": {
      "command": "itential-mcp",
      "env": {
        "ITENTIAL_MCP_SERVER_HOST": "your-itential-host.com",
        "ITENTIAL_MCP_SERVER_USERNAME": "your-username",
        "ITENTIAL_MCP_SERVER_PASSWORD": "your-password"
      }
    }
  }
}
```

### Advanced Configuration with Tool Filtering

You can filter available tools using tags to limit functionality:

```json
{
  "mcpServers": {
    "itential-platform": {
      "command": "itential-mcp",
      "args": [
        "--include-tags", "system,operations_manager,devices",
        "--exclude-tags", "lifecycle_manager"
      ],
      "env": {
        "ITENTIAL_MCP_SERVER_HOST": "https://itential.example.com",
        "ITENTIAL_MCP_SERVER_PORT": "443",
        "ITENTIAL_MCP_SERVER_USERNAME": "automation-user",
        "ITENTIAL_MCP_SERVER_PASSWORD": "secure-password",
        "ITENTIAL_MCP_SERVER_VERIFY_SSL": "true"
      }
    }
  }
}
```

## Configuration Parameters

### Required Environment Variables

| Variable | Description | Example |
|----------|-------------|---------|
| `ITENTIAL_MCP_SERVER_HOST` | Itential Platform hostname or IP | `itential.example.com` |
| `ITENTIAL_MCP_SERVER_USERNAME` | Username for authentication | `automation-user` |
| `ITENTIAL_MCP_SERVER_PASSWORD` | Password for authentication | `secure-password` |

### Optional Environment Variables

| Variable | Description | Default | Example |
|----------|-------------|---------|---------|
| `ITENTIAL_MCP_SERVER_PORT` | Itential Platform port | `443` | `8443` |
| `ITENTIAL_MCP_SERVER_PROTOCOL` | Protocol (http/https) | `https` | `http` |
| `ITENTIAL_MCP_SERVER_VERIFY_SSL` | SSL certificate verification | `true` | `false` |
| `ITENTIAL_MCP_SERVER_TIMEOUT` | Request timeout in seconds | `30` | `60` |

### Command Line Arguments

| Argument | Description | Example |
|----------|-------------|---------|
| `--include-tags` | Comma-separated list of tags to include | `--include-tags system,devices` |
| `--exclude-tags` | Comma-separated list of tags to exclude | `--exclude-tags lifecycle_manager` |
| `--transport` | Transport protocol (stdio/sse/http) | `--transport stdio` |
| `--host` | Host for SSE/HTTP transport | `--host 0.0.0.0` |
| `--port` | Port for SSE/HTTP transport | `--port 8000` |

## Client-Specific Integration Examples

### Claude Desktop Integration

Create or update `~/Library/Application Support/Claude/claude_desktop_config.json` (macOS) or the equivalent location on your platform:

```json
{
  "mcpServers": {
    "itential-platform": {
      "command": "itential-mcp",
      "env": {
        "ITENTIAL_MCP_SERVER_HOST": "your-itential-host.com",
        "ITENTIAL_MCP_SERVER_USERNAME": "your-username",
        "ITENTIAL_MCP_SERVER_PASSWORD": "your-password"
      }
    }
  }
}
```

### Continue.dev Integration

Add to your `continue` configuration:

```json
{
  "models": [
    {
      "model": "gpt-4",
      "provider": "openai",
      "mcpServers": [
        {
          "name": "itential-platform",
          "command": "itential-mcp",
          "env": {
            "ITENTIAL_MCP_SERVER_HOST": "itential.example.com",
            "ITENTIAL_MCP_SERVER_USERNAME": "automation-user",
            "ITENTIAL_MCP_SERVER_PASSWORD": "secure-password"
          }
        }
      ]
    }
  ]
}
```

### Generic MCP Client Integration

For any MCP-compatible client that supports server configuration:

```json
{
  "servers": [
    {
      "name": "itential-platform",
      "command": ["itential-mcp"],
      "transport": {
        "type": "stdio"
      },
      "environment": {
        "ITENTIAL_MCP_SERVER_HOST": "itential.example.com",
        "ITENTIAL_MCP_SERVER_USERNAME": "automation-user",
        "ITENTIAL_MCP_SERVER_PASSWORD": "secure-password"
      }
    }
  ]
}
```

## Role-Based Tool Filtering

Use tool tags to create role-specific configurations:

### Platform Administrator Configuration

```json
{
  "mcpServers": {
    "itential-admin": {
      "command": "itential-mcp",
      "args": [
        "--include-tags", "system,adapters,applications"
      ],
      "env": {
        "ITENTIAL_MCP_SERVER_HOST": "itential.example.com",
        "ITENTIAL_MCP_SERVER_USERNAME": "admin-user",
        "ITENTIAL_MCP_SERVER_PASSWORD": "admin-password"
      }
    }
  }
}
```

### Network Operations Configuration

```json
{
  "mcpServers": {
    "itential-netops": {
      "command": "itential-mcp",
      "args": [
        "--include-tags", "devices,configuration_manager,automation_studio",
        "--exclude-tags", "adapters,applications"
      ],
      "env": {
        "ITENTIAL_MCP_SERVER_HOST": "itential.example.com",
        "ITENTIAL_MCP_SERVER_USERNAME": "netops-user",
        "ITENTIAL_MCP_SERVER_PASSWORD": "netops-password"
      }
    }
  }
}
```

### Automation Developer Configuration

```json
{
  "mcpServers": {
    "itential-developer": {
      "command": "itential-mcp",
      "args": [
        "--include-tags", "operations_manager,workflow_engine,lifecycle_manager",
        "--exclude-tags", "system,adapters"
      ],
      "env": {
        "ITENTIAL_MCP_SERVER_HOST": "itential.example.com",
        "ITENTIAL_MCP_SERVER_USERNAME": "dev-user",
        "ITENTIAL_MCP_SERVER_PASSWORD": "dev-password"
      }
    }
  }
}
```

## Security Considerations

### Authentication

The MCP server supports HTTP Basic Authentication. Ensure you use secure credentials:

- Create dedicated service accounts for MCP integration
- Use strong passwords or consider token-based authentication if supported
- Rotate credentials regularly

### Network Security

- Use HTTPS when possible (default behavior)
- Verify SSL certificates in production (`ITENTIAL_MCP_SERVER_VERIFY_SSL=true`)
- Consider network restrictions and firewall rules

### Access Control

- Use tool tag filtering to limit available functionality
- Create role-specific configurations with minimal required permissions
- Monitor MCP server usage through Itential Platform logs

## Environment Variable File

For development or testing, you can create a `.env` file:

```bash
# Itential Platform Connection
ITENTIAL_MCP_SERVER_HOST=itential-dev.example.com
ITENTIAL_MCP_SERVER_PORT=443
ITENTIAL_MCP_SERVER_PROTOCOL=https
ITENTIAL_MCP_SERVER_USERNAME=mcp-service-account
ITENTIAL_MCP_SERVER_PASSWORD=secure-dev-password
ITENTIAL_MCP_SERVER_VERIFY_SSL=true
ITENTIAL_MCP_SERVER_TIMEOUT=30
```

Then reference it in your MCP client configuration:

```json
{
  "mcpServers": {
    "itential-platform": {
      "command": "itential-mcp",
      "env": {
        "ITENTIAL_MCP_SERVER_HOST": "${ITENTIAL_MCP_SERVER_HOST}",
        "ITENTIAL_MCP_SERVER_USERNAME": "${ITENTIAL_MCP_SERVER_USERNAME}",
        "ITENTIAL_MCP_SERVER_PASSWORD": "${ITENTIAL_MCP_SERVER_PASSWORD}"
      }
    }
  }
}
```

## Troubleshooting

### Common Issues

1. **Connection Failed**: Verify host, port, and network connectivity
2. **Authentication Error**: Check username/password credentials
3. **SSL Certificate Error**: Set `ITENTIAL_MCP_SERVER_VERIFY_SSL=false` for testing or install proper certificates
4. **Tool Not Available**: Check tool tag filtering configuration
5. **Timeout Errors**: Increase `ITENTIAL_MCP_SERVER_TIMEOUT` value

### Debug Mode

Enable debug logging:

```json
{
  "mcpServers": {
    "itential-platform": {
      "command": "itential-mcp",
      "args": ["--debug"],
      "env": {
        "ITENTIAL_MCP_SERVER_HOST": "itential.example.com",
        "ITENTIAL_MCP_SERVER_USERNAME": "debug-user",
        "ITENTIAL_MCP_SERVER_PASSWORD": "debug-password"
      }
    }
  }
}
```

### Test Connection

Test the MCP server connection:

```bash
# Test basic connectivity
itential-mcp --test-connection

# Test with specific configuration
ITENTIAL_MCP_SERVER_HOST=itential.example.com \
ITENTIAL_MCP_SERVER_USERNAME=test-user \
ITENTIAL_MCP_SERVER_PASSWORD=test-password \
itential-mcp --test-connection
```

## Available Tool Tags

For reference, here are the available tool tags for filtering:

- `adapters` - Adapter lifecycle management
- `applications` - Application lifecycle management
- `automation_studio` - Command templates and automation
- `configuration_manager` - Configuration and compliance management
- `devices` - Device-specific operations
- `gateway_manager` - Gateway and external service management
- `integrations` - External system integrations
- `lifecycle_manager` - Resource lifecycle management
- `operations_manager` - Workflow and job management
- `system` - Platform health and monitoring
- `workflow_engine` - Workflow execution metrics

See the [Tools Reference](tools.md) for complete details on available tools and their capabilities.
