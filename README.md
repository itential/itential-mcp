<div align="left">

[![PyPI version](https://badge.fury.io/py/itential-mcp.svg)](https://badge.fury.io/py/itential-mcp)
[![Python Version](https://img.shields.io/badge/python-3.10%2B-blue)](https://www.python.org/downloads/)
[![License: GPL v3](https://img.shields.io/badge/License-GPLv3-blue.svg)](https://www.gnu.org/licenses/gpl-3.0)
[![Build Status](https://img.shields.io/badge/build-passing-brightgreen.svg)](https://github.com/itential/itential-mcp)
[![Coverage](https://img.shields.io/badge/coverage-95%25-green)](https://github.com/itential/itential-mcp)

</div>

# 🔌 Itential - MCP Server

A Model Context Protocol _(MCP)_ server that provides comprehensive tools for connecting LLMs to Itential Platform. Enable AI assistants to manage network automations, orchestrate workflows, monitor platform health, and perform advanced network operations.

## 🎯 Who This Is For

### **Platform Engineers**
Manage infrastructure, monitor system health, configure devices, and orchestrate network operations through AI-powered automation.

### **Developers**
Build automation workflows, integrate with external systems, manage application lifecycles, and extend platform capabilities.

## 📒 Key Features

### **Core Capabilities**
- **56+ Automation Tools**: Comprehensive toolkit across 10 tag categories for all network automation needs
- **Advanced Tool Selection**: Filter and control available tools using flexible tagging system
- **Multiple Transport Methods**: stdio, SSE, and HTTP transports with optional TLS encryption
- **Dynamic Tool Discovery**: Automatically discovers and registers tools without code modifications
- **Flexible Authentication**: Supports basic auth, OAuth 2.0, JWT, and role-based access for Itential Platform
- **Comprehensive Configuration**: CLI parameters, environment variables, or configuration files
- **Role-Based Access**: Tailored tool configurations for Platform Administrators, Network Engineers, and Developers

### **Network Automation & Device Management**
- **Device Configuration**: Apply configurations, backup device settings, and retrieve current configurations
- **Command Execution**: Run single commands or command templates across multiple devices with rule validation
- **Device Groups**: Create and manage logical device collections for streamlined operations
- **Compliance Management**: Automated compliance plan execution and detailed reporting
- **Golden Configuration**: Hierarchical template-based configuration management with version control

### **Workflow & Orchestration**
- **Workflow Execution**: Start workflows via API endpoints and monitor execution status
- **Job Management**: Track workflow jobs with comprehensive status, metrics, and task details
- **Workflow Exposure**: Convert workflows into REST API endpoints for external consumption
- **Template Management**: Create, update, and execute Jinja2 and TextFSM templates
- **Performance Metrics**: Detailed job and task execution metrics for workflow optimization

### **Platform Operations & Monitoring**
- **Health Monitoring**: Real-time platform health including system resources, applications, and adapters
- **Component Lifecycle**: Start, stop, and restart applications and adapters with status monitoring
- **Integration Management**: Create and manage OpenAPI-based integration models
- **Gateway Services**: Execute external services (Ansible, Python scripts, OpenTofu) through Gateway Manager

### **Lifecycle & Resource Management**
- **Resource Models**: Define JSON Schema-based resource structures with lifecycle workflows
- **Instance Management**: Full CRUD operations on resource instances with state tracking
- **Action Execution**: Run lifecycle actions with comprehensive execution history
- **Data Validation**: Schema-based validation for resource data and action parameters

## 🔍 Requirements
- Python _3.10_ or higher
- Access to an [Itential Platform Instance](https://www.itential.com/)
- For _development_ - `uv` and `make`

### Tested Python Versions
This project is automatically tested against the following Python versions:
- Python 3.10
- Python 3.11
- Python 3.12
- Python 3.13

## 🔧 Installation
The `itential-mcp` application can be installed using either PyPI or it can be
run directly from source.

### PyPI Installation
To install it from PyPI, simply use `pip`:

```bash
pip install itential-mcp
```

### Local Development
The repository can also be clone the repository to your local environment to
work with the MCP server. The project uses `uv` and `make` so both tools
would need to be installed and available in your environment.

The following commands can be used to get started.

```bash
git clone https://github.com/itential/itential-mcp
cd itential-mcp
make build
```

For development, you can run the server directly using `uv`:

```bash
# Run with stdio transport (default)
uv run itential-mcp run

# Run with SSE transport
uv run itential-mcp run --transport sse --host 0.0.0.0 --port 8000

# Run with specific configuration
uv run itential-mcp run --include-tags "system,devices" --exclude-tags "experimental"
```

### Container Usage

#### Pull from GitHub Container Registry
Pull and run the latest release:

```bash
# Pull the latest image
docker pull ghcr.io/itential/itential-mcp:latest

# Run with SSE transport
docker run -p 8000:8000 \
  --env ITENTIAL_MCP_SERVER_TRANSPORT=sse \
  --env ITENTIAL_MCP_SERVER_HOST=0.0.0.0 \
  --env ITENTIAL_MCP_SERVER_PORT=8000 \
  --env ITENTIAL_MCP_PLATFORM_HOST=your-platform.example.com \
  --env ITENTIAL_MCP_PLATFORM_USER=your-username \
  --env ITENTIAL_MCP_PLATFORM_PASSWORD=your-password \
  ghcr.io/itential/itential-mcp:latest

# Or with OAuth authentication
docker run -p 8000:8000 \
  --env ITENTIAL_MCP_SERVER_TRANSPORT=sse \
  --env ITENTIAL_MCP_SERVER_HOST=0.0.0.0 \
  --env ITENTIAL_MCP_SERVER_PORT=8000 \
  --env ITENTIAL_MCP_PLATFORM_HOST=your-platform.example.com \
  --env ITENTIAL_MCP_PLATFORM_CLIENT_ID=CLIENT_ID \
  --env ITENTIAL_MCP_PLATFORM_CLIENT_SECRET=CLIENT_SECRET \
  ghcr.io/itential/itential-mcp:latest

# Run with stdio transport (for MCP clients)
docker run -i \
  --env ITENTIAL_MCP_PLATFORM_HOST=your-platform.example.com \
  --env ITENTIAL_MCP_PLATFORM_USER=your-username \
  --env ITENTIAL_MCP_PLATFORM_PASSWORD=your-password \
  ghcr.io/itential/itential-mcp:latest
```

#### Build Container Image Locally
Build and run from source:

```bash
# Build the container image
make container

# Run the locally built container
docker run -p 8000:8000 \
  --env ITENTIAL_MCP_SERVER_TRANSPORT=sse \
  --env ITENTIAL_MCP_SERVER_HOST=0.0.0.0 \
  --env ITENTIAL_MCP_SERVER_PORT=8000 \
  --env ITENTIAL_MCP_PLATFORM_HOST=your-platform.example.com \
  --env ITENTIAL_MCP_PLATFORM_USER=your-username \
  --env ITENTIAL_MCP_PLATFORM_PASSWORD=your-password \
  itential-mcp:devel
```

## 🚀 Quick Start

### **1. Install the Server**
```bash
pip install itential-mcp
```

### **2. Configure Platform Connection**
Set your Itential Platform credentials:

```bash
export ITENTIAL_MCP_PLATFORM_HOST="your-platform.example.com"
export ITENTIAL_MCP_PLATFORM_USER="your-username"
export ITENTIAL_MCP_PLATFORM_PASSWORD="your-password"
```

### **3. Start the Server**
```bash
# Basic stdio transport (default)
itential-mcp run

# Or with SSE transport for web clients
itential-mcp run --transport sse --host 0.0.0.0 --port 8000
```

### **4. Configure Your MCP Client**
Follow the [integration guide](docs/integration.md) to connect Claude, Continue.dev, or other MCP clients.

## 📝 Basic Usage
Start the MCP server with default settings _(stdio transport)_:

```bash
itential-mcp run
```

Start with SSE transport:

```bash
itential-mcp run --transport sse --host 0.0.0.0 --port 8000
```

### General Options

| Option     | Description             | Default |
|------------|-------------------------|---------|
| `--config` | Path to the config file | none    |

### Server Options

 | Option           | Description                                       | Default           |
 |------------------|---------------------------------------------------|-------------------|
 | `--transport`    | Transport protocol (stdio, sse, http)             | stdio             |
 | `--host`         | Host address to listen on                         | 127.0.0.1         |
 | `--port`         | Port to listen on                                 | 8000              |
 | `--path`         | The HTTP path to use                              | /mcp              |
 | `--log-level`    | Log level (DEBUG, INFO, WARNING, ERROR, CRITICAL, NONE) | NONE              |
 | `--include-tags` | Tags to include registered tools                  | none              |
 | `--exclude-tags` | Tags to exclude registered tools                  | experimental,beta |

### Platform Configuration

| Option                      | Description                         | Default   |
|-----------------------------|-------------------------------------|-----------|
| `--platform-host`           | Itential Platform hostname          | localhost |
| `--platform-port`           | Platform port (0 = auto-detect)     | 0         |
| `--platform-disable-tls`    | Disable TLS for platform connection | false     |
| `--platform-disable-verify` | Disable certificate verification    | false     |
| `--platform-timeout`        | Connection timeout                  | 30        |
| `--platform-user`           | Username for authentication         | admin     |
| `--platform-password`       | Password for authentication         | admin     |
| `--platform-client-id`      | OAuth client ID                     | none      |
| `--platform-client-secret`  | OAuth client secret                 | none      |

### Environment Variables

All command line options can also be set using environment variables prefixed with `ITENTIAL_MCP_SERVER_`. For example:

```bash
export ITENTIAL_MCP_SERVER_TRANSPORT=sse
export ITENTIAL_MCP_PLATFORM_HOST=platform.example.com
itential-mcp run  # Will use the environment variables
```

#### Security Considerations

**⚠️ Important Security Notice:**

The MCP server reads configuration from environment variables, which means it must run in a **trusted environment**. In shared or multi-tenant environments, ensure that:

1. **Environment Isolation**: The server runs in isolated containers or dedicated environments where users cannot set arbitrary environment variables
2. **Access Control**: Only authorized administrators can set `ITENTIAL_MCP_*` environment variables
3. **Dynamic Tool Configuration**: Environment variables with the pattern `ITENTIAL_MCP_TOOL_*` can define custom tool bindings. This is powerful but requires trust boundaries
4. **Credential Management**: Never expose credentials in shared environments. Use secret management systems (Kubernetes Secrets, HashiCorp Vault, etc.)

**Recommended Deployment Practices:**
- Use containerization (Docker, Kubernetes) to isolate environment variables
- Implement least-privilege access controls
- Rotate credentials regularly
- Enable TLS and certificate verification in production
- Use authentication (JWT, OAuth) for HTTP/SSE transports

For production deployments, see our [Security Best Practices](docs/security.md) guide.

### Configuration file

The server configuration can also be specified using a configuration file.  The
configuration file can be used to pass in all the configuration parameters.  To
use a configuration file, simply pass in the `--config <path>` command line
argument where `<path>` points to the configuration file to load.

The format and values for the configuration file are documented
[here](docs/mcp.conf.example)

When configuration options are specified in multiple places the following
precedence for determinting the value to be used will be honored from highest
to lowest:

1. Environment variable
2. Command line option
3. Configuration file
4. Default value


## 🎛️ Tool Selection & Tagging

The Itential MCP server provides powerful tool filtering capabilities through a comprehensive tagging system. This allows you to customize which tools are available based on your specific needs and security requirements.

### **Tag-Based Filtering**

Control tool availability using include and exclude tags:

```bash
# Include only health and device management tools  
itential-mcp run --include-tags "health,configuration_manager"

# Exclude experimental and beta tools (default behavior)
itential-mcp run --exclude-tags "experimental,beta,lifecycle_manager"
```

### **Available Tag Groups**

| Tag Group | Tool Count | Description | Use Case |
|-----------|------------|-------------|----------|
| `health` | 1 | Platform health and monitoring | Platform administrators |
| `configuration_manager` | 15 | Device, compliance, and config management | Network engineers |
| `operations_manager` | 5 | Workflow and job management | Automation developers |
| `automation_studio` | 8 | Command templates, projects, templates | Network operators |
| `lifecycle_manager` | 7 | Resource lifecycle and instance management | Product managers |
| `workflow_engine` | 6 | Workflow execution metrics | Performance analysts |
| `adapters` | 4 | Adapter lifecycle management | Integration specialists |
| `applications` | 4 | Application lifecycle management | Application owners |
| `gateway_manager` | 3 | External service management | System integrators |
| `integrations` | 3 | External system integrations | API developers |

### **Role-Based Configurations**

The following role-based configurations provide tailored tool access based on specific job functions and responsibilities:

**Platform Administrator:**
*System health monitoring, component management, platform operations*

```bash
itential-mcp run --include-tags "health,adapters,applications,integrations"
```

*Key Tools: Platform health monitoring, adapter/application lifecycle, integration management*

**Network Engineer:**
*Device management, configurations, compliance, network automation*

```bash
itential-mcp run --include-tags "configuration_manager,automation_studio"
```

*Key Tools: Device configuration, compliance plans, command templates, golden config management*

**Automation Developer:**
*Workflow building, performance analysis, platform extension*

```bash
itential-mcp run --include-tags "operations_manager,workflow_engine,lifecycle_manager,gateway_manager"
```

*Key Tools: Workflow execution, performance metrics, resource lifecycle, external service integration*

**Platform Operator:**
*Daily operations, job monitoring, report generation*

```bash
itential-mcp run --include-tags "operations_manager,configuration_manager"
```

*Key Tools: Workflow execution, job monitoring, device operations, compliance reporting*

## 📚 Documentation & Integration

### **Complete Tool Reference**
The entire list of available tools can be found in the [tools documentation](docs/tools.md) along with detailed tag associations.

### **Configuration & Security**
- [MCP Client Integration](docs/integration.md) - Configure Claude, Continue.dev, and other MCP clients
- [TLS Configuration](docs/tls.md) - Enable secure HTTPS connections with certificates
- [JWT Authentication](docs/jwt-authentication.md) - JWT token authentication setup
- [OAuth Authentication](docs/oauth-authentication.md) - OAuth 2.0 with multiple providers
- [Configuration Examples](docs/mcp.conf.example) - Complete configuration file reference
- [Status Endpoints](docs/status-endpoints.md) - Health monitoring for production deployments

### **Advanced Features**
- [Tagging System](docs/tags.md) - Advanced tool filtering and selection strategies
- [Workflow Execution](docs/exposing-workflows.md) - Execute and monitor Itential workflows
- [Custom Tools Development](docs/custom-tools.md) - Create and integrate custom MCP tools

### **Example Prompts**
- [Claude Desktop Prompt](docs/claude-example.prompt) - Optimized prompt for Claude integration
- [GPT Integration Prompt](docs/gpt-example.prompt) - Optimized prompt for GPT integration

## 🛠️ Adding new Tools
Adding a new tool is simple:

1. Create a new Python file in the `src/itential_mcp/tools/` directory or add a function to an existing file
2. Define an async function with a `Context` parameter annotation:

```python
from fastmcp import Context

async def my_new_tool(ctx: Context) -> dict:
    """
    Description of what the tool does

    Args:
        ctx (Context): The FastMCP Context object

    Returns:
        dict: The response data

    Raises:
        None
    """
    # Get the platform client
    client = ctx.request_context.lifespan_context.get("client")

    # Make API requests
    res = await client.get("/your/api/path")

    # Return JSON-serializable results
    return res.json()
```

Tools are automatically discovered and registered when the server starts.

### Running Tests
Run the test suite with:

```bash
make test
```

For test coverage information:

```bash
make coverage
```

## Contributing
Contributions are welcome! Please read our [Code of Conduct](CODE_OF_CONDUCT.md) before contributing.

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/my-feature`
3. Commit your changes: `git commit -am 'Add new feature'`
4. Push to the branch: `git push origin feature/my-feature`
5. Submit a pull request

Before submitting:
- Run `make premerge` to ensure tests pass and code style is correct
- Add documentation for new features
- Add tests for new functionality

## License
This project is licensed under the GNU General Public License v3.0 - see the [LICENSE](LICENSE) file for details.

Copyright (c) 2025 Itential, Inc
