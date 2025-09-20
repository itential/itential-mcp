# Copyright (c) 2025 Itential, Inc
# GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)

"""Default configuration values for Itential MCP Server.

This module defines default values for all configuration parameters used
by the Itential MCP Server. These defaults are used when no explicit
configuration is provided via environment variables, command line arguments,
or configuration files.

The configuration is organized into two main sections:
- Server configuration: Controls MCP server behavior and network settings
- Platform configuration: Controls connection to Itential Platform

All configuration values follow the naming convention ITENTIAL_MCP_<section>_<parameter>.
"""

# Server Configuration Defaults
ITENTIAL_MCP_SERVER_TRANSPORT = "stdio"  # MCP transport protocol: stdio, sse, or http
ITENTIAL_MCP_SERVER_HOST = "127.0.0.1"  # Server host address for network transports
ITENTIAL_MCP_SERVER_PORT = 8000  # Server port for network transports
ITENTIAL_MCP_SERVER_PATH = "/mcp"  # URI path for HTTP-based transports
ITENTIAL_MCP_SERVER_LOG_LEVEL = "INFO"  # Logging verbosity level
ITENTIAL_MCP_SERVER_INCLUDE_TAGS = None  # Tool tags to include (None = include all)
ITENTIAL_MCP_SERVER_EXCLUDE_TAGS = "experimental,beta"  # Tool tags to exclude
ITENTIAL_MCP_SERVER_TOOLS_PATH = None  # Custom path to load additional tools from

# Platform Configuration Defaults
ITENTIAL_MCP_PLATFORM_HOST = "localhost"  # Itential Platform server hostname
ITENTIAL_MCP_PLATFORM_PORT = 0  # Platform server port (0 = use default for protocol)
ITENTIAL_MCP_PLATFORM_DISABLE_TLS = False  # Disable TLS/SSL encryption
ITENTIAL_MCP_PLATFORM_DISABLE_VERIFY = False  # Disable SSL certificate verification
ITENTIAL_MCP_PLATFORM_USER = "admin"  # Username for basic authentication
ITENTIAL_MCP_PLATFORM_PASSWORD = "admin"  # Password for basic authentication
ITENTIAL_MCP_PLATFORM_CLIENT_ID = None  # OAuth client ID (None = use basic auth)
ITENTIAL_MCP_PLATFORM_CLIENT_SECRET = None  # OAuth client secret
ITENTIAL_MCP_PLATFORM_TIMEOUT = 30  # Request timeout in seconds
