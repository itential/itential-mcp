# Copyright (c) 2025 Itential, Inc
# GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

"""Configuration data models for Itential MCP Server.

This module defines immutable dataclasses that represent the configuration
structure for the Itential MCP Server. The models are organized hierarchically
to provide clear separation of concerns between different configuration domains.
"""

from __future__ import annotations

from typing import Literal, Any

from pydantic import Field, field_validator
from pydantic.dataclasses import dataclass

from ..core import env
from .. import defaults
from .validators import validate_tool_name, validate_port, validate_host


def _create_field_with_env(
    env_key: str,
    description: str,
    env_getter: callable = env.getstr,
    **extra_kwargs: dict[str, Any],
) -> Field:
    """Create a Field with environment variable default factory.

    Args:
        env_key: Environment variable name to use for default value.
        description: Field description for documentation.
        env_getter: Function to get and transform environment value.
        **extra_kwargs: Additional keyword arguments passed to Field.

    Returns:
        Field: Pydantic Field with environment variable default.

    Raises:
        None.
    """
    from functools import partial

    return Field(
        description=description,
        default_factory=partial(env_getter, env_key, getattr(defaults, env_key)),
        **extra_kwargs,
    )


@dataclass(frozen=True)
class Tool:
    """Base configuration for a tool exposed by the MCP server.

    This represents the common configuration for any tool type that can be
    exposed to AI agents through the MCP protocol.
    """

    name: str = Field(description="The name of the asset in Itential Platform")
    tool_name: str = Field(description="The tool name that is exposed")
    type: Literal["endpoint", "service"] = Field(description="The tool type")
    description: str | None = Field(
        description="Description of this tool", default=None
    )
    tags: str | None = Field(
        description="List of comma separated tags applied to this tool", default=None
    )

    @field_validator("tool_name")
    @classmethod
    def _validate_tool_name_field(cls, v: str) -> str:
        """Validate tool_name field using the validate_tool_name function.

        Args:
            v: The tool_name value to validate.

        Returns:
            The validated tool_name.

        Raises:
            ValueError: If the tool_name is invalid.
        """
        return validate_tool_name(v)


@dataclass(frozen=True)
class EndpointTool(Tool):
    """Configuration for an endpoint-based tool.

    Endpoint tools execute workflows through Itential Platform automation triggers.
    """

    automation: str = Field(
        description="The name of the automation the trigger is associated with"
    )


@dataclass(frozen=True)
class ServiceTool(Tool):
    """Configuration for a service-based tool.

    Service tools interact with Itential Gateway services in a specific cluster.
    """

    cluster: str = Field(description="The cluster where the Gateway service resides")


@dataclass(frozen=True)
class ServerConfig:
    """Server configuration for the MCP server.

    Controls MCP server behavior including transport, networking, logging,
    tool filtering, and authentication settings.
    """

    transport: Literal["stdio", "sse", "http"] = _create_field_with_env(
        "ITENTIAL_MCP_SERVER_TRANSPORT",
        "The MCP server transport to use",
        json_schema_extra={
            "x-itential-mcp-cli-enabled": True,
            "x-itential-mcp-arguments": ("--transport",),
            "x-itential-mcp-options": {
                "choices": ("stdio", "sse", "http"),
                "metavar": "<value>",
            },
        },
    )

    host: str = _create_field_with_env(
        "ITENTIAL_MCP_SERVER_HOST",
        "Address to listen for connections on",
        json_schema_extra={
            "x-itential-mcp-cli-enabled": True,
            "x-itential-mcp-arguments": ("--host",),
            "x-itential-mcp-options": {"metavar": "<host>"},
        },
    )

    port: int = _create_field_with_env(
        "ITENTIAL_MCP_SERVER_PORT",
        "Port to listen for connections on",
        env_getter=env.getint,
        json_schema_extra={
            "x-itential-mcp-cli-enabled": True,
            "x-itential-mcp-arguments": ("--port",),
            "x-itential-mcp-options": {"metavar": "<port>", "type": int},
        },
    )

    certificate_file: str = _create_field_with_env(
        "ITENTIAL_MCP_SERVER_CERTIFICATE_FILE",
        "Path to the certificate file to use for TLS connections",
        json_schema_extra={
            "x-itential-mcp-cli-enabled": True,
            "x-itential-mcp-arguments": ("--certificate-file",),
            "x-itential-mcp-options": {"metavar": "<path>"},
        },
    )

    private_key_file: str = _create_field_with_env(
        "ITENTIAL_MCP_SERVER_PRIVATE_KEY_FILE",
        "path to the private key file to use for TLS connections",
        json_schema_extra={
            "x-itential-mcp-cli-enabled": True,
            "x-itential-mcp-arguments": ("--private-key-file",),
            "x-itential-mcp-options": {"metavar": "<path>"},
        },
    )

    path: str = _create_field_with_env(
        "ITENTIAL_MCP_SERVER_PATH",
        "URI path used to accept requests from",
        json_schema_extra={
            "x-itential-mcp-cli-enabled": True,
            "x-itential-mcp-arguments": ("--path",),
            "x-itential-mcp-options": {"metavar": "<path>"},
        },
    )

    log_level: Literal["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL", "NONE"] = (
        _create_field_with_env(
            "ITENTIAL_MCP_SERVER_LOG_LEVEL",
            "Logging level for verbose output",
            json_schema_extra={
                "x-itential-mcp-cli-enabled": True,
                "x-itential-mcp-arguments": ("--log-level",),
                "x-itential-mcp-options": {"metavar": "<level>"},
            },
        )
    )

    include_tags: str | None = _create_field_with_env(
        "ITENTIAL_MCP_SERVER_INCLUDE_TAGS",
        "Include tools that match at least on tag",
        json_schema_extra={
            "x-itential-mcp-cli-enabled": True,
            "x-itential-mcp-arguments": ("--include-tags",),
            "x-itential-mcp-options": {"metavar": "<tags>"},
        },
    )

    exclude_tags: str | None = _create_field_with_env(
        "ITENTIAL_MCP_SERVER_EXCLUDE_TAGS",
        "Exclude any tool that matches one of these tags",
        json_schema_extra={
            "x-itential-mcp-cli-enabled": True,
            "x-itential-mcp-arguments": ("--exclude-tags",),
            "x-itential-mcp-options": {"metavar": "<tags>"},
        },
    )

    tools_path: str | None = _create_field_with_env(
        "ITENTIAL_MCP_SERVER_TOOLS_PATH",
        "Custom path to load tools from",
        json_schema_extra={
            "x-itential-mcp-cli-enabled": True,
            "x-itential-mcp-arguments": ("--tools-path",),
            "x-itential-mcp-options": {"metavar": "<path>"},
        },
    )

    keepalive_interval: int = _create_field_with_env(
        "ITENTIAL_MCP_SERVER_KEEPALIVE_INTERVAL",
        "Keepalive interval in seconds to prevent session timeout (0 = disabled)",
        env_getter=env.getint,
        json_schema_extra={
            "x-itential-mcp-cli-enabled": True,
            "x-itential-mcp-arguments": ("--keepalive-interval",),
            "x-itential-mcp-options": {"metavar": "<seconds>", "type": int},
        },
    )

    response_format: Literal["json", "toon"] = _create_field_with_env(
        "ITENTIAL_MCP_SERVER_RESPONSE_FORMAT",
        "Response serialization format (json, toon)",
        json_schema_extra={
            "x-itential-mcp-cli-enabled": True,
            "x-itential-mcp-arguments": ("--response-format",),
            "x-itential-mcp-options": {
                "choices": ("json", "toon"),
                "metavar": "<format>",
            },
        },
    )


@dataclass(frozen=True)
class AuthConfig:
    """Authentication configuration for the MCP server.

    Supports multiple authentication providers including JWT, OAuth, and OAuth Proxy.
    """

    type: Literal["none", "jwt", "oauth", "oauth_proxy"] = _create_field_with_env(
        "ITENTIAL_MCP_SERVER_AUTH_TYPE",
        "Authentication provider type used to secure the MCP server",
        json_schema_extra={
            "x-itential-mcp-cli-enabled": True,
            "x-itential-mcp-arguments": ("--auth-type",),
            "x-itential-mcp-options": {
                "choices": ("none", "jwt", "oauth", "oauth_proxy"),
                "metavar": "<type>",
            },
        },
    )

    jwks_uri: str | None = _create_field_with_env(
        "ITENTIAL_MCP_SERVER_AUTH_JWKS_URI",
        "JWKS URI used to dynamically fetch signing keys for JWT validation",
        json_schema_extra={
            "x-itential-mcp-cli-enabled": True,
            "x-itential-mcp-arguments": ("--auth-jwks-uri",),
            "x-itential-mcp-options": {"metavar": "<url>"},
        },
    )

    public_key: str | None = _create_field_with_env(
        "ITENTIAL_MCP_SERVER_AUTH_PUBLIC_KEY",
        "Static PEM encoded public key or shared secret for JWT validation",
        json_schema_extra={
            "x-itential-mcp-cli-enabled": True,
            "x-itential-mcp-arguments": ("--auth-public-key",),
            "x-itential-mcp-options": {"metavar": "<value>"},
        },
    )

    issuer: str | None = _create_field_with_env(
        "ITENTIAL_MCP_SERVER_AUTH_ISSUER",
        "Expected JWT issuer claim (iss)",
        json_schema_extra={
            "x-itential-mcp-cli-enabled": True,
            "x-itential-mcp-arguments": ("--auth-issuer",),
            "x-itential-mcp-options": {"metavar": "<issuer>"},
        },
    )

    audience: str | None = _create_field_with_env(
        "ITENTIAL_MCP_SERVER_AUTH_AUDIENCE",
        "Expected JWT audience claims (comma separated for multiple values)",
        json_schema_extra={
            "x-itential-mcp-cli-enabled": True,
            "x-itential-mcp-arguments": ("--auth-audience",),
            "x-itential-mcp-options": {"metavar": "<audience>"},
        },
    )

    algorithm: str | None = _create_field_with_env(
        "ITENTIAL_MCP_SERVER_AUTH_ALGORITHM",
        "Expected JWT signing algorithm (e.g., RS256, HS256)",
        json_schema_extra={
            "x-itential-mcp-cli-enabled": True,
            "x-itential-mcp-arguments": ("--auth-algorithm",),
            "x-itential-mcp-options": {"metavar": "<algorithm>"},
        },
    )

    required_scopes: str | None = _create_field_with_env(
        "ITENTIAL_MCP_SERVER_AUTH_REQUIRED_SCOPES",
        "Comma separated list of scopes required on every JWT",
        json_schema_extra={
            "x-itential-mcp-cli-enabled": True,
            "x-itential-mcp-arguments": ("--auth-required-scopes",),
            "x-itential-mcp-options": {"metavar": "<scopes>"},
        },
    )

    oauth_client_id: str | None = _create_field_with_env(
        "ITENTIAL_MCP_SERVER_AUTH_OAUTH_CLIENT_ID",
        "OAuth client ID for authentication",
        json_schema_extra={
            "x-itential-mcp-cli-enabled": True,
            "x-itential-mcp-arguments": ("--auth-oauth-client-id",),
            "x-itential-mcp-options": {"metavar": "<client_id>"},
        },
    )

    oauth_client_secret: str | None = _create_field_with_env(
        "ITENTIAL_MCP_SERVER_AUTH_OAUTH_CLIENT_SECRET",
        "OAuth client secret for authentication",
        json_schema_extra={
            "x-itential-mcp-cli-enabled": True,
            "x-itential-mcp-arguments": ("--auth-oauth-client-secret",),
            "x-itential-mcp-options": {"metavar": "<client_secret>"},
        },
    )

    oauth_authorization_url: str | None = _create_field_with_env(
        "ITENTIAL_MCP_SERVER_AUTH_OAUTH_AUTHORIZATION_URL",
        "OAuth authorization endpoint URL",
        json_schema_extra={
            "x-itential-mcp-cli-enabled": True,
            "x-itential-mcp-arguments": ("--auth-oauth-authorization-url",),
            "x-itential-mcp-options": {"metavar": "<url>"},
        },
    )

    oauth_token_url: str | None = _create_field_with_env(
        "ITENTIAL_MCP_SERVER_AUTH_OAUTH_TOKEN_URL",
        "OAuth token endpoint URL",
        json_schema_extra={
            "x-itential-mcp-cli-enabled": True,
            "x-itential-mcp-arguments": ("--auth-oauth-token-url",),
            "x-itential-mcp-options": {"metavar": "<url>"},
        },
    )

    oauth_userinfo_url: str | None = _create_field_with_env(
        "ITENTIAL_MCP_SERVER_AUTH_OAUTH_USERINFO_URL",
        "OAuth userinfo endpoint URL",
        json_schema_extra={
            "x-itential-mcp-cli-enabled": True,
            "x-itential-mcp-arguments": ("--auth-oauth-userinfo-url",),
            "x-itential-mcp-options": {"metavar": "<url>"},
        },
    )

    oauth_scopes: str | None = _create_field_with_env(
        "ITENTIAL_MCP_SERVER_AUTH_OAUTH_SCOPES",
        "OAuth scopes to request (space or comma separated)",
        json_schema_extra={
            "x-itential-mcp-cli-enabled": True,
            "x-itential-mcp-arguments": ("--auth-oauth-scopes",),
            "x-itential-mcp-options": {"metavar": "<scopes>"},
        },
    )

    oauth_redirect_uri: str | None = _create_field_with_env(
        "ITENTIAL_MCP_SERVER_AUTH_OAUTH_REDIRECT_URI",
        "OAuth redirect URI for callback",
        json_schema_extra={
            "x-itential-mcp-cli-enabled": True,
            "x-itential-mcp-arguments": ("--auth-oauth-redirect-uri",),
            "x-itential-mcp-options": {"metavar": "<uri>"},
        },
    )

    oauth_provider_type: (
        Literal["generic", "google", "azure", "auth0", "github", "okta"] | None
    ) = _create_field_with_env(
        "ITENTIAL_MCP_SERVER_AUTH_OAUTH_PROVIDER_TYPE",
        "OAuth provider type for predefined configurations",
        json_schema_extra={
            "x-itential-mcp-cli-enabled": True,
            "x-itential-mcp-arguments": ("--auth-oauth-provider-type",),
            "x-itential-mcp-options": {
                "choices": ("generic", "google", "azure", "auth0", "github", "okta"),
                "metavar": "<type>",
            },
        },
    )


@dataclass(frozen=True)
class PlatformConfig:
    """Platform configuration for connecting to Itential Platform.

    Controls connection settings, authentication, and communication parameters
    for the Itential Platform API client.
    """

    host: str = _create_field_with_env(
        "ITENTIAL_MCP_PLATFORM_HOST",
        "The host addres of the Itential Platform server",
        json_schema_extra={
            "x-itential-mcp-cli-enabled": True,
            "x-itential-mcp-arguments": ("--platform-host",),
            "x-itential-mcp-options": {"metavar": "<host>"},
        },
    )

    port: int = _create_field_with_env(
        "ITENTIAL_MCP_PLATFORM_PORT",
        "The port to use when connecting to Itential Platform",
        env_getter=env.getint,
        json_schema_extra={
            "x-itential-mcp-cli-enabled": True,
            "x-itential-mcp-arguments": ("--platform-port",),
            "x-itential-mcp-options": {"metavar": "<port>", "type": int},
        },
    )

    disable_tls: bool = _create_field_with_env(
        "ITENTIAL_MCP_PLATFORM_DISABLE_TLS",
        "Disable using TLS to connect to the server",
        env_getter=env.getbool,
        json_schema_extra={
            "x-itential-mcp-cli-enabled": True,
            "x-itential-mcp-arguments": ("--platform-disable-tls",),
            "x-itential-mcp-options": {"action": "store_true"},
        },
    )

    disable_verify: bool = _create_field_with_env(
        "ITENTIAL_MCP_PLATFORM_DISABLE_VERIFY",
        "Disable certificate verification",
        env_getter=env.getbool,
        json_schema_extra={
            "x-itential-mcp-cli-enabled": True,
            "x-itential-mcp-arguments": ("--platform-disable-verify",),
            "x-itential-mcp-options": {"action": "store_true"},
        },
    )

    user: str = _create_field_with_env(
        "ITENTIAL_MCP_PLATFORM_USER",
        "Username to use when authenticating to the server",
        json_schema_extra={
            "x-itential-mcp-cli-enabled": True,
            "x-itential-mcp-arguments": ("--platform-user",),
            "x-itential-mcp-options": {"metavar": "<user>"},
        },
    )

    password: str = _create_field_with_env(
        "ITENTIAL_MCP_PLATFORM_PASSWORD",
        "Password to use when authenticating to the server",
        json_schema_extra={
            "x-itential-mcp-cli-enabled": True,
            "x-itential-mcp-arguments": ("--platform-password",),
            "x-itential-mcp-options": {"metavar": "<password>"},
        },
    )

    client_id: str | None = _create_field_with_env(
        "ITENTIAL_MCP_PLATFORM_CLIENT_ID",
        "Client ID to use when authenticating using OAuth",
        json_schema_extra={
            "x-itential-mcp-cli-enabled": True,
            "x-itential-mcp-arguments": ("--platform-client-id",),
            "x-itential-mcp-options": {"metavar": "<client_id>"},
        },
    )

    client_secret: str | None = _create_field_with_env(
        "ITENTIAL_MCP_PLATFORM_CLIENT_SECRET",
        "Client secret to use when authenticating using OAuth",
        json_schema_extra={
            "x-itential-mcp-cli-enabled": True,
            "x-itential-mcp-arguments": ("--platform-client-secret",),
            "x-itential-mcp-options": {"metavar": "<client_secret>"},
        },
    )

    timeout: int = _create_field_with_env(
        "ITENTIAL_MCP_PLATFORM_TIMEOUT",
        "Sets the timeout in seconds when communciating with the server",
        env_getter=env.getint,
        json_schema_extra={
            "x-itential-mcp-cli-enabled": True,
            "x-itential-mcp-arguments": ("--platform-timeout",),
            "x-itential-mcp-options": {"metavar": "<secs>"},
        },
    )

    ttl: int = _create_field_with_env(
        "ITENTIAL_MCP_PLATFORM_TTL",
        "Authentication TTL in seconds before forcing reauthentication (0 = disabled)",
        env_getter=env.getint,
        json_schema_extra={
            "x-itential-mcp-cli-enabled": True,
            "x-itential-mcp-arguments": ("--platform-ttl",),
            "x-itential-mcp-options": {"metavar": "<secs>", "type": int},
        },
    )

    @field_validator("port")
    @classmethod
    def _validate_port(cls, v: int) -> int:
        """Validate that port is in the valid TCP port range.

        Args:
            v: The port number to validate.

        Returns:
            The validated port number.

        Raises:
            ValueError: If the port is not in the range 1-65535.
        """
        return validate_port(v)

    @field_validator("host")
    @classmethod
    def _validate_host(cls, v: str) -> str:
        """Validate that host is a valid hostname or IP address.

        Args:
            v: The host string to validate.

        Returns:
            The validated host string.

        Raises:
            ValueError: If the host is invalid.
        """
        return validate_host(v)


@dataclass(frozen=True)
class Config:
    """Complete configuration for the Itential MCP Server.

    This is the root configuration object that aggregates all configuration
    sections and provides convenient property accessors for downstream
    consumers.
    """

    server: ServerConfig
    auth: AuthConfig
    platform: PlatformConfig
    tools: list[Tool] = Field(
        description="List of Itential Platform assets to be exposed as tools",
        default_factory=list,
    )
