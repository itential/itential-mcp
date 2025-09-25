# AI Assistant Configuration Guide

This guide provides configuration examples for integrating the Itential MCP server with various AI assistants. Choose the configuration style that matches your AI assistant and preferred connection method.

## Prerequisites

<details>
<summary><strong>UV Package Manager (Required for STDIO)</strong></summary>

All STDIO configurations require [UV](https://pypi.org/project/uv/), a fast Python package installer and resolver. UV must be installed on your system before configuring STDIO transport.

**Install UV:**
```bash
# macOS/Linux
curl -LsSf https://astral.sh/uv/install.sh | sh

# Windows (PowerShell)
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"

# Via pip
pip install uv
```

**Verify installation:**
```bash
uv --version
```
</details>

## Configuration Styles

<details>
<summary><strong>Claude Desktop</strong></summary>

Compatible with Claude Desktop and many other desktop applications like Cline, AnythingLLM and more.

### STDIO Configuration
```json
"itential-mcp": {
    "autoApprove": [],
    "disabled": false,
    "timeout": 60,
    "command": "uv",
    "args": [
        "--directory",
        "/path/to/your/itential-mcp",
        "run",
        "itential-mcp",
        "run",
        "--config",
        "/path/to/your/itential-mcp.conf"
    ],
    "type": "stdio"
}
```

### HTTP Configuration
```json
"itential-mcp": {
    "type": "streamable",
    "url": "http://localhost:8000/mcp"
}
```

**Note:** HTTP configuration requires the MCP server to be running separately in HTTP mode.

</details>

<details>
<summary><strong>Claude Code (CLI)</strong></summary>

Command-line interface for Claude with MCP server integration.

### STDIO Setup
```bash
claude mcp add itential-mcp -- uv --directory /path/to/your/itential-mcp run itential-mcp run --config /path/to/your/itential-mcp.conf
```

### HTTP Setup
```bash
claude mcp add --transport http itential-mcp http://localhost:8000/mcp
```

**Note:** Ensure the MCP server is running on the specified port for HTTP transport.

</details>

<details>
<summary><strong>Codex</strong></summary>

Configuration format for Codex-based AI assistants.

### STDIO Configuration
```toml
[mcp_servers.itential_mcp]
command = "uv"
args = [
    "--directory",
    "/path/to/your/itential-mcp",
    "run",
    "itential-mcp",
    "run",
    "--config",
    "/path/to/your/itential-mcp.conf"
]
timeout = 60
disabled = false
autoApprove = []
```

### HTTP Configuration
```
❌ HTTP transport is not supported in Codex
```

**Note:** Codex only supports STDIO transport method.

</details>

## Path Placeholders

When configuring your setup, replace the following placeholders with your actual paths:

- `/path/to/your/itential-mcp` - Directory containing your Itential MCP installation
- `/path/to/your/itential-mcp.conf` - Full path to your MCP configuration file
- `http://localhost:8000/mcp` - Your MCP server URL (adjust host/port as needed)

## Common Configuration Parameters

| Parameter | Description | Default | Required |
|-----------|-------------|---------|----------|
| `timeout` | Connection timeout in seconds | 60 | No |
| `disabled` | Whether the server is disabled | false | No |
| `autoApprove` | List of auto-approved tools | [] | No |

---

## Frequently Asked Questions

<details>
<summary><strong>How do I find my MCP installation directory?</strong></summary>

The installation directory depends on how you installed the MCP server:

- **Git clone**: The directory where you cloned the repository
- **Package manager**: Use your package manager's info command to locate the installation
- **Manual installation**: The directory where you extracted/installed the files

Example paths:
- `/Users/username/itential-mcp` (macOS)
- `/home/username/itential-mcp` (Linux)  
- `C:\Users\username\itential-mcp` (Windows)

</details>

<details>
<summary><strong>Do I need to install anything before setting up STDIO?</strong></summary>

Yes, STDIO configurations require **UV** (a fast Python package installer) to be installed on your system. UV is used to run the MCP server process.

**Install UV using one of these methods:**
```bash
# macOS/Linux
curl -LsSf https://astral.sh/uv/install.sh | sh

# Windows (PowerShell)  
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"

# Via pip (if you have Python installed)
pip install uv
```

After installation, verify it works:
```bash
uv --version
```

**Note:** HTTP configurations don't require UV since they connect to an already-running server.

</details>

<details>
<summary><strong>Where should I place the configuration file?</strong></summary>

The `itential-mcp.conf` file can be placed anywhere accessible to your system. Common locations:

- Same directory as the MCP installation
- User's home directory
- Dedicated config directory (e.g., `~/.config/itential/`)

Ensure the path in your configuration matches the actual file location.

</details>

<details>
<summary><strong>What's the difference between STDIO and HTTP transport?</strong></summary>

**STDIO Transport:**
- Direct process communication
- Lower latency
- More secure (no network exposure)
- Requires the AI assistant to manage the MCP server process

**HTTP Transport:**
- Network-based communication
- Allows remote connections
- Requires manually running the MCP server
- More flexible for distributed setups

Choose STDIO for local setups and HTTP for remote or service-based deployments.

</details>

<details>
<summary><strong>How do I start the MCP server for HTTP mode?</strong></summary>

To run the MCP server in HTTP mode:

```bash
cd /path/to/your/itential-mcp
uv run itential-mcp run --config /path/to/your/itential-mcp.conf
```

</details>

<details>
<summary><strong>My AI assistant can't find the MCP server. What should I check?</strong></summary>

Common troubleshooting steps:

1. **Verify paths**: Ensure all file paths in your configuration exist and are accessible
2. **Check permissions**: Make sure the AI assistant has read/execute permissions for the MCP directory
3. **Test manually**: Try running the MCP server command manually to verify it works
4. **Review logs**: Check your AI assistant's logs for specific error messages
5. **Validate config**: Ensure your configuration file syntax is correct for your AI assistant

</details>

<details>
<summary><strong>Can I run multiple MCP servers simultaneously?</strong></summary>

Yes, you can configure multiple MCP servers with different names and configurations. Each server should have:

- A unique name/identifier
- Different ports (if using HTTP transport)
- Separate configuration files (if needed)

Example for multiple servers:
```json
"itential-mcp-prod": {
    "type": "stdio",
    "command": "uv",
    "args": ["--directory", "/path/to/prod/itential-mcp", "run", "itential-mcp", "run", "--config", "/path/to/prod.conf"]
},
"itential-mcp-dev": {
    "type": "stdio", 
    "command": "uv",
    "args": ["--directory", "/path/to/dev/itential-mcp", "run", "itential-mcp", "run", "--config", "/path/to/dev.conf"]
}
```

</details>
