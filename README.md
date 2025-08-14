<div align="left">

[![License: GPL v3](https://img.shields.io/badge/License-GPLv3-blue.svg)](https://www.gnu.org/licenses/gpl-3.0)
[![Python Version](https://img.shields.io/badge/python-3.10%2B-blue)](https://www.python.org/downloads/)
[![Build Status](https://img.shields.io/badge/build-passing-brightgreen.svg)](https://github.com/itential/itential-mcp)
[![Code Style](https://img.shields.io/badge/code%20style-ruff-black)](https://github.com/charliermarsh/ruff)

</div>

# 🔌 Itential - MCP Server
A Model Context Protocol _(MCP)_ server that provides tools for connecting LLMs to Itential Platform. Enable AI assistants to manage network automations, orchestrate workflows, and monitor platform health.

## 📒 Features
- **Multiple Transport Methods**: Choose between stdio (default) or SSE transport for MCP server
- **Dynamic Tool Loading**: Automatically discovers and registers tools without modifying core code
- **Flexible Authentication**: Supports both basic authentication and OAuth for Itential Platform
- **Configurable**: Set options via command line parameters or environment variables
- **Containerized**: Run as a Docker container with configurable environment
- **Extensible**: Easy to add new tools without deep knowledge of the code base

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

## 📝 Basic Usage
Start the MCP server with default settings _(stdio transport)_:

```bash
itential-mcp --transport --host 0.0.0.0 --port 8000
```

Start with SSE transport:

```bash
itential-mcp --transport sse --host 0.0.0.0 --port 8000
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
itential-mcp  # Will use the environment variables
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


## 💡 Available Tools
The entire list of availablle tools can be found in the [tools](docs/tools.md)
file along with the tag groups assoicated with those tools.

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
