<div align="left">

[![PyPI version](https://badge.fury.io/py/ipsdk.svg)](https://badge.fury.io/py/ipsdk)
[![Python Version](https://img.shields.io/badge/python-3.10%2B-blue)](https://www.python.org/downloads/)
[![License: GPL v3](https://img.shields.io/badge/License-GPLv3-blue.svg)](https://www.gnu.org/licenses/gpl-3.0)
[![Build Status](https://img.shields.io/badge/build-passing-brightgreen.svg)](https://github.com/itential/itential-mcp)
[![Coverage](https://img.shields.io/badge/coverage-95%25-green)](https://github.com/itential/ipsdk)

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
- **Advanced Tool Selection**: Filter and control available tools using flexible tagging system
- **Multiple Transport Methods**: stdio, SSE, and HTTP transports for different deployment scenarios
- **Dynamic Tool Discovery**: Automatically discovers and registers tools without code modifications
- **Flexible Authentication**: Supports both basic authentication and OAuth 2.0 for Itential Platform
- **Comprehensive Configuration**: CLI parameters, environment variables, or configuration files

### **Network Automation**
- **Device Management**: Configure, backup, and monitor network devices
- **Command Execution**: Run commands and templates across device groups
- **Compliance Management**: Automated compliance checking and reporting
- **Golden Configuration**: Template-based configuration management

### **Workflow & Orchestration**
- **Workflow Execution**: Trigger and monitor automation workflows
- **Operations Management**: Job tracking and lifecycle management
- **Lifecycle Manager**: CRUD operations for stateful products with state tracking
- **Service Integration**: Connect with external systems and APIs

### **Platform Operations**
- **Health Monitoring**: Real-time platform and component health metrics
- **Resource Management**: Adapter and application lifecycle control
- **Gateway Services**: External service management and orchestration

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

### Build Container Image
Build and run as a container:

```bash
# Build the container image
make container

# Run the container with environment variables
docker run -p 8000:8000 \
  --env ITENTIAL_MCP_SERVER_TRANSPORT=sse \
  --env ITENTIAL_MCP_SERVER_HOST=0.0.0.0 \
  --env ITENTIAL_MCP_SERVER_PORT=8000 \
  --env ITENTIAL_MCP_PLATFORM_HOST=URL \
  --env ITENTIAL_MCP_PLATFORM_CLIENT_ID=CLIENT_ID \
  --env ITENTIAL_MCP_PLATFORM_CLIENT_SECRET=CLIENT_SECRET \
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
 | `--host`         | Host address to listen on                         | localhost         |
 | `--port`         | Port to listen on                                 | 8000              |
 | `--path`         | The streamable HTTP path to use                   | /mcp              |
 | `--log-level`    | Log level (DEBUG, INFO, WARNING, ERROR, CRITICAL) | INFO              |
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
# Include only system and device management tools
itential-mcp run --include-tags "system,configuration_manager,devices"

# Exclude experimental and beta tools (default behavior)
itential-mcp run --exclude-tags "experimental,beta,lifecycle_manager"
```

### **Available Tag Groups**

| Tag Group | Description | Use Case |
|-----------|-------------|----------|
| `system` | Platform health and monitoring | Platform administrators |
| `configuration_manager` | Device and compliance management | Network engineers |
| `devices` | Device-specific operations | NOC teams |
| `operations_manager` | Workflow and job management | Automation developers |
| `adapters` | Adapter lifecycle management | Integration specialists |
| `applications` | Application lifecycle management | Application owners |
| `automation_studio` | Command templates and automation | Network operators |
| `gateway_manager` | External service management | System integrators |
| `integrations` | External system integrations | API developers |
| `lifecycle_manager` | Stateful product CRUD operations and state tracking | Product managers |
| `workflow_engine` | Workflow execution metrics | Performance analysts |

### **Role-Based Configurations**

The following role-based configurations provide tailored tool access based on specific job functions and responsibilities:

**Platform SRE:**
*Use Cases: Platform & application administration, Adapter management, Integration management, Troubleshooting, Platform overall health and functionality*

```bash
itential-mcp run --include-tags "system,adapters,applications,integrations"
```

*Available Tools: get_health, restart_application, start_application, stop_application, create_integration_model, get_job_metrics, get_task_metrics, restart_adapter, start_adapter, stop_adapter, get_task_metrics_for_app, get_task_metrics_for_task, get_task_metrics_for_workflow*

**Platform Builder:**
*Use Cases: Asset development, Asset promotion, Workflow metrics analysis, Resource lifecycle management*

```bash
itential-mcp run --include-tags "operations_manager,automation_studio,configuration_manager,workflow_engine,lifecycle_manager"
```

*Available Tools: create_resource, get_workflows, describe_command_template, run_command_template, run_command, render_template, create_device_group, get_resources, describe_resource, get_instances, backup_device_configuration, apply_device_configuration, get_compliance_plans, run_compliance_plan, get_adapters, get_applications, get_integration_models, get_job_metrics, get_job_metrics_for_workflow, get_task_metrics, get_task_metrics_for_workflow, get_task_metrics_for_app, get_task_metrics_for_task, describe_instance, run_action*

**Automation Developer:**
*Use Cases: Asset development, Asset promotion, External service management*

```bash
itential-mcp run --include-tags "operations_manager,gateway_manager"
```

*Available Tools: create_resource, get_services, get_gateways, run_service*

**Platform Operator:**
*Use Cases: Execute jobs, Run compliance, Consume data*

```bash
itential-mcp run --include-tags "operations_manager,devices,configuration_manager,automation_studio"
```

*Available Tools: get_workflows, start_workflow, get_jobs, describe_job, get_devices, get_device_configuration, get_device_groups, get_command_templates, run_command_template, describe_compliance_report*

## 📚 Documentation & Integration

### **Complete Tool Reference**
The entire list of available tools can be found in the [tools documentation](docs/tools.md) along with detailed tag associations.

### **Client Integration Guides**
- [MCP Client Integration](docs/integration.md) - Configure Claude, Continue.dev, and other MCP clients
- [Configuration Examples](docs/mcp.conf.example) - Complete configuration file reference
- [Tagging System](docs/tags.md) - Advanced tagging and filtering guide
- [Workflow Execution](docs/exposing-workflows.md) - Running automation workflows

### **Example Prompts**
- [Claude Desktop Prompt](docs/claude-example.prompt) - Optimized prompt for Claude integration
- [GPT Integration Prompt](docs/gpt-example.prompt) - Optimized prompt for GPT integration

## 💡 Available Tools
The entire list of available tools can be found in the [tools](docs/tools.md)
file along with the tag groups associated with those tools.

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
