# Copyright (c) 2025 Itential, Inc
# GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

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
ITENTIAL_MCP_SERVER_CERTIFICATE_FILE = (
    ""  # Path to certificate file to use for TLS connections
)
ITENTIAL_MCP_SERVER_PRIVATE_KEY_FILE = (
    ""  # Path to private key file to use for TLS connections
)
ITENTIAL_MCP_SERVER_PATH = "/mcp"  # URI path for HTTP-based transports
ITENTIAL_MCP_SERVER_LOG_LEVEL = "NONE"  # Logging verbosity level
ITENTIAL_MCP_SERVER_INCLUDE_TAGS = None  # Tool tags to include (None = include all)
ITENTIAL_MCP_SERVER_EXCLUDE_TAGS = "experimental,beta"  # Tool tags to exclude
ITENTIAL_MCP_SERVER_TOOLS_PATH = None  # Custom path to load additional tools from
ITENTIAL_MCP_SERVER_KEEPALIVE_INTERVAL = (
    300  # Keepalive interval in seconds (0 = disabled)
)
ITENTIAL_MCP_SERVER_RESPONSE_FORMAT = (
    "json"  # Response serialization format: json, toon, or auto
)
ITENTIAL_MCP_SERVER_AUTH_TYPE = "none"  # Authentication provider type
ITENTIAL_MCP_SERVER_AUTH_JWKS_URI = None  # JWKS URI for JWT validation
ITENTIAL_MCP_SERVER_AUTH_PUBLIC_KEY = (
    None  # Static public key or shared secret for JWT validation
)
ITENTIAL_MCP_SERVER_AUTH_ISSUER = None  # Expected JWT issuer
ITENTIAL_MCP_SERVER_AUTH_AUDIENCE = None  # Expected JWT audience(s)
ITENTIAL_MCP_SERVER_AUTH_ALGORITHM = None  # Expected JWT signing algorithm
ITENTIAL_MCP_SERVER_AUTH_REQUIRED_SCOPES = (
    None  # Comma separated list of required scopes
)

# OAuth Configuration Defaults
ITENTIAL_MCP_SERVER_AUTH_OAUTH_CLIENT_ID = None  # OAuth client ID for authentication
ITENTIAL_MCP_SERVER_AUTH_OAUTH_CLIENT_SECRET = (
    None  # OAuth client secret for authentication
)
ITENTIAL_MCP_SERVER_AUTH_OAUTH_AUTHORIZATION_URL = (
    None  # OAuth authorization endpoint URL
)
ITENTIAL_MCP_SERVER_AUTH_OAUTH_TOKEN_URL = None  # OAuth token endpoint URL
ITENTIAL_MCP_SERVER_AUTH_OAUTH_USERINFO_URL = None  # OAuth userinfo endpoint URL
ITENTIAL_MCP_SERVER_AUTH_OAUTH_SCOPES = None  # OAuth scopes to request
ITENTIAL_MCP_SERVER_AUTH_OAUTH_REDIRECT_URI = None  # OAuth redirect URI for callback
ITENTIAL_MCP_SERVER_AUTH_OAUTH_PROVIDER_TYPE = (
    None  # OAuth provider type for predefined configurations
)

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
ITENTIAL_MCP_PLATFORM_TTL = 0  # Authentication TTL in seconds (0 = disabled)
