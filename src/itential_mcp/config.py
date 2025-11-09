# Copyright (c) 2025 Itential, Inc
# GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)

import os
import configparser
import re

from functools import lru_cache, partial
from pathlib import Path

from typing import Literal, List, Callable, Any

from pydantic import Field, field_validator
from pydantic.dataclasses import dataclass

from .core import env
from . import defaults


def options(*args, **kwargs) -> dict:
    """Utility function to add extra parameters to fields.

    This function will add extra parameters to a Field in the Config
    class. Specifically it handles adding the necessary keys to support
    generating the CLI options from the configuration. This unifies the
    parameter descriptions and default values for consistency.

    Args:
        *args: Positional arguments to be added to the CLI command line option.
        **kwargs: Optional arguments to be added to the CLI command line option.

    Returns:
        dict: A Python dict object to be added to the Field function signature.
    """
    return {
        "x-itential-mcp-cli-enabled": True,
        "x-itential-mcp-arguments": args,
        "x-itential-mcp-options": kwargs,
    }


def validate_tool_name(tool_name: str) -> str:
    """Validate that a tool name follows the required naming convention.

    Tool names must start with a letter and only contain letters, numbers,
    and underscores. This ensures compatibility with Python function naming
    and prevents injection attacks.

    Args:
        tool_name: The tool name to validate.

    Returns:
        The validated tool name.

    Raises:
        ValueError: If the tool name does not match the required pattern.
    """
    if not tool_name:
        raise ValueError("Tool name cannot be empty")

    pattern = r"^[a-zA-Z][a-zA-Z0-9_]*$"
    if not re.match(pattern, tool_name):
        raise ValueError(
            f"Tool name '{tool_name}' is invalid. Tool names must start with a letter "
            "and only contain letters, numbers, and underscores."
        )

    return tool_name


def default_factory(f, key) -> Callable:
    return partial(f, key, getattr(defaults, key))


@dataclass(frozen=True)
class Tool(object):
    name: str = Field(
        description="The name of the asset in Itential Platform",
    )

    tool_name: str = Field(description="The tool name that is exposed")

    type: Literal["endpoint", "service"] = Field(description="The tool type")

    description: str = Field(description="Description of this tool", default=None)

    tags: str = Field(
        description="List of comma separated tags applied to this tool", default=None
    )

    @field_validator("tool_name")
    @classmethod
    def validate_tool_name_field(cls, v: str) -> str:
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
    automation: str = Field(
        description="The name of the automation the trigger is associated with"
    )


@dataclass(frozen=True)
class ServiceTool(Tool):
    cluster: str = Field(description="The cluster where the Gateway service resides")


@dataclass(frozen=True)
class Config(object):
    server_transport: Literal["stdio", "sse", "http"] = Field(
        description="The MCP server transport to use",
        default_factory=default_factory(
            env.getstr,
            "ITENTIAL_MCP_SERVER_TRANSPORT",
        ),
        json_schema_extra=options(
            "--transport", choices=("stdio", "sse", "http"), metavar="<value>"
        ),
    )

    server_host: str = Field(
        description="Address to listen for connections on",
        default_factory=default_factory(
            env.getstr,
            "ITENTIAL_MCP_SERVER_HOST",
        ),
        json_schema_extra=options("--host", metavar="<host>"),
    )

    server_port: int = Field(
        description="Port to listen for connections on",
        default_factory=default_factory(
            env.getint,
            "ITENTIAL_MCP_SERVER_PORT",
        ),
        json_schema_extra=options("--port", metavar="<port>", type=int),
    )

    server_certificate_file: str = Field(
        description="Path to the certificate file to use for TLS connections",
        default_factory=default_factory(
            env.getstr,
            "ITENTIAL_MCP_SERVER_CERTIFICATE_FILE",
        ),
        json_schema_extra=options("--certificate-file", metavar="<path>"),
    )

    server_private_key_file: str = Field(
        description="path to the private key file to use for TLS connections",
        default_factory=default_factory(
            env.getstr,
            "ITENTIAL_MCP_SERVER_PRIVATE_KEY_FILE",
        ),
        json_schema_extra=options("--private-key-file", metavar="<path>"),
    )

    server_path: str = Field(
        description="URI path used to accept requests from",
        default_factory=default_factory(env.getstr, "ITENTIAL_MCP_SERVER_PATH"),
        json_schema_extra=options("--path", metavar="<path>"),
    )

    server_log_level: Literal[
        "DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL", "NONE"
    ] = Field(
        description="Logging level for verbose output",
        default_factory=default_factory(env.getstr, "ITENTIAL_MCP_SERVER_LOG_LEVEL"),
        json_schema_extra=options("--log-level", metavar="<level>"),
    )

    server_include_tags: str | None = Field(
        description="Include tools that match at least on tag",
        default_factory=default_factory(env.getstr, "ITENTIAL_MCP_SERVER_INCLUDE_TAGS"),
        json_schema_extra=options("--include-tags", metavar="<tags>"),
    )

    server_exclude_tags: str | None = Field(
        description="Exclude any tool that matches one of these tags",
        default_factory=default_factory(
            env.getstr,
            "ITENTIAL_MCP_SERVER_EXCLUDE_TAGS",
        ),
        json_schema_extra=options("--exclude-tags", metavar="<tags>"),
    )

    server_tools_path: str | None = Field(
        description="Custom path to load tools from",
        default_factory=default_factory(env.getstr, "ITENTIAL_MCP_SERVER_TOOLS_PATH"),
        json_schema_extra=options(
            "--tools-path",
            metavar="<path>",
        ),
    )

    server_keepalive_interval: int = Field(
        description="Keepalive interval in seconds to prevent session timeout (0 = disabled)",
        default_factory=default_factory(
            env.getint, "ITENTIAL_MCP_SERVER_KEEPALIVE_INTERVAL"
        ),
        json_schema_extra=options(
            "--keepalive-interval",
            metavar="<seconds>",
            type=int,
        ),
    )

    server_auth_type: Literal["none", "jwt", "oauth", "oauth_proxy"] = Field(
        description="Authentication provider type used to secure the MCP server",
        default_factory=default_factory(
            env.getstr,
            "ITENTIAL_MCP_SERVER_AUTH_TYPE",
        ),
        json_schema_extra=options(
            "--auth-type",
            choices=("none", "jwt", "oauth", "oauth_proxy"),
            metavar="<type>",
        ),
    )

    server_auth_jwks_uri: str | None = Field(
        description="JWKS URI used to dynamically fetch signing keys for JWT validation",
        default_factory=default_factory(
            env.getstr,
            "ITENTIAL_MCP_SERVER_AUTH_JWKS_URI",
        ),
        json_schema_extra=options(
            "--auth-jwks-uri",
            metavar="<url>",
        ),
    )

    server_auth_public_key: str | None = Field(
        description="Static PEM encoded public key or shared secret for JWT validation",
        default_factory=default_factory(
            env.getstr,
            "ITENTIAL_MCP_SERVER_AUTH_PUBLIC_KEY",
        ),
        json_schema_extra=options(
            "--auth-public-key",
            metavar="<value>",
        ),
    )

    server_auth_issuer: str | None = Field(
        description="Expected JWT issuer claim (iss)",
        default_factory=default_factory(
            env.getstr,
            "ITENTIAL_MCP_SERVER_AUTH_ISSUER",
        ),
        json_schema_extra=options(
            "--auth-issuer",
            metavar="<issuer>",
        ),
    )

    server_auth_audience: str | None = Field(
        description="Expected JWT audience claims (comma separated for multiple values)",
        default_factory=default_factory(
            env.getstr,
            "ITENTIAL_MCP_SERVER_AUTH_AUDIENCE",
        ),
        json_schema_extra=options(
            "--auth-audience",
            metavar="<audience>",
        ),
    )

    server_auth_algorithm: str | None = Field(
        description="Expected JWT signing algorithm (e.g., RS256, HS256)",
        default_factory=default_factory(
            env.getstr,
            "ITENTIAL_MCP_SERVER_AUTH_ALGORITHM",
        ),
        json_schema_extra=options(
            "--auth-algorithm",
            metavar="<algorithm>",
        ),
    )

    server_auth_required_scopes: str | None = Field(
        description="Comma separated list of scopes required on every JWT",
        default_factory=default_factory(
            env.getstr,
            "ITENTIAL_MCP_SERVER_AUTH_REQUIRED_SCOPES",
        ),
        json_schema_extra=options(
            "--auth-required-scopes",
            metavar="<scopes>",
        ),
    )

    server_auth_oauth_client_id: str | None = Field(
        description="OAuth client ID for authentication",
        default_factory=default_factory(
            env.getstr,
            "ITENTIAL_MCP_SERVER_AUTH_OAUTH_CLIENT_ID",
        ),
        json_schema_extra=options(
            "--auth-oauth-client-id",
            metavar="<client_id>",
        ),
    )

    server_auth_oauth_client_secret: str | None = Field(
        description="OAuth client secret for authentication",
        default_factory=default_factory(
            env.getstr,
            "ITENTIAL_MCP_SERVER_AUTH_OAUTH_CLIENT_SECRET",
        ),
        json_schema_extra=options(
            "--auth-oauth-client-secret",
            metavar="<client_secret>",
        ),
    )

    server_auth_oauth_authorization_url: str | None = Field(
        description="OAuth authorization endpoint URL",
        default_factory=default_factory(
            env.getstr,
            "ITENTIAL_MCP_SERVER_AUTH_OAUTH_AUTHORIZATION_URL",
        ),
        json_schema_extra=options(
            "--auth-oauth-authorization-url",
            metavar="<url>",
        ),
    )

    server_auth_oauth_token_url: str | None = Field(
        description="OAuth token endpoint URL",
        default_factory=default_factory(
            env.getstr,
            "ITENTIAL_MCP_SERVER_AUTH_OAUTH_TOKEN_URL",
        ),
        json_schema_extra=options(
            "--auth-oauth-token-url",
            metavar="<url>",
        ),
    )

    server_auth_oauth_userinfo_url: str | None = Field(
        description="OAuth userinfo endpoint URL",
        default_factory=default_factory(
            env.getstr,
            "ITENTIAL_MCP_SERVER_AUTH_OAUTH_USERINFO_URL",
        ),
        json_schema_extra=options(
            "--auth-oauth-userinfo-url",
            metavar="<url>",
        ),
    )

    server_auth_oauth_scopes: str | None = Field(
        description="OAuth scopes to request (space or comma separated)",
        default_factory=default_factory(
            env.getstr,
            "ITENTIAL_MCP_SERVER_AUTH_OAUTH_SCOPES",
        ),
        json_schema_extra=options(
            "--auth-oauth-scopes",
            metavar="<scopes>",
        ),
    )

    server_auth_oauth_redirect_uri: str | None = Field(
        description="OAuth redirect URI for callback",
        default_factory=default_factory(
            env.getstr,
            "ITENTIAL_MCP_SERVER_AUTH_OAUTH_REDIRECT_URI",
        ),
        json_schema_extra=options(
            "--auth-oauth-redirect-uri",
            metavar="<uri>",
        ),
    )

    server_auth_oauth_provider_type: (
        Literal["generic", "google", "azure", "auth0", "github", "okta"] | None
    ) = Field(
        description="OAuth provider type for predefined configurations",
        default_factory=default_factory(
            env.getstr,
            "ITENTIAL_MCP_SERVER_AUTH_OAUTH_PROVIDER_TYPE",
        ),
        json_schema_extra=options(
            "--auth-oauth-provider-type",
            choices=("generic", "google", "azure", "auth0", "github", "okta"),
            metavar="<type>",
        ),
    )

    platform_host: str = Field(
        description="The host addres of the Itential Platform server",
        default_factory=default_factory(
            env.getstr,
            "ITENTIAL_MCP_PLATFORM_HOST",
        ),
        json_schema_extra=options("--platform-host", metavar="<host>"),
    )

    platform_port: int = Field(
        description="The port to use when connecting to Itential Platform",
        default_factory=default_factory(env.getint, "ITENTIAL_MCP_PLATFORM_PORT"),
        json_schema_extra=options(
            "--platform-port",
            type=int,
            metavar="<port>",
        ),
    )

    platform_disable_tls: bool = Field(
        description="Disable using TLS to connect to the server",
        default_factory=default_factory(
            env.getbool, "ITENTIAL_MCP_PLATFORM_DISABLE_TLS"
        ),
        json_schema_extra=options("--platform-disable-tls", action="store_true"),
    )

    platform_disable_verify: bool = Field(
        description="Disable certificate verification",
        default_factory=default_factory(
            env.getbool, "ITENTIAL_MCP_PLATFORM_DISABLE_VERIFY"
        ),
        json_schema_extra=options("--platform-disable-verify", action="store_true"),
    )

    platform_user: str = Field(
        description="Username to use when authenticating to the server",
        default_factory=default_factory(env.getstr, "ITENTIAL_MCP_PLATFORM_USER"),
        json_schema_extra=options("--platform-user", metavar="<user>"),
    )

    platform_password: str = Field(
        description="Password to use when authenticating to the server",
        default_factory=default_factory(env.getstr, "ITENTIAL_MCP_PLATFORM_PASSWORD"),
        json_schema_extra=options("--platform-password", metavar="<password>"),
    )

    platform_client_id: str | None = Field(
        description="Client ID to use when authenticating using OAuth",
        default_factory=default_factory(env.getstr, "ITENTIAL_MCP_PLATFORM_CLIENT_ID"),
        json_schema_extra=options("--platform-client-id", metavar="<client_id>"),
    )

    platform_client_secret: str | None = Field(
        description="Client secret to use when authenticating using OAuth",
        default_factory=default_factory(
            env.getstr, "ITENTIAL_MCP_PLATFORM_CLIENT_SECRET"
        ),
        json_schema_extra=options(
            "--platform-client-secret", metavar="<client_secret>"
        ),
    )

    platform_timeout: int = Field(
        description="Sets the timeout in seconds when communciating with the server",
        default_factory=default_factory(env.getint, "ITENTIAL_MCP_PLATFORM_TIMEOUT"),
        json_schema_extra=options("--platform-timeout", metavar="<secs>"),
    )

    tools: List[Tool] = Field(
        description="List of Itential Platform assets to be exposed as tools",
        default_factory=list,
    )

    @property
    def server(self) -> dict:
        """Get server configuration as a dictionary.

        Args:
            None

        Returns:
            dict: Server configuration parameters including transport, host, port,
                path, log level, and tag filtering settings.

        Raises:
            None.
        """
        return {
            "transport": self.server_transport,
            "host": self.server_host,
            "port": self.server_port,
            "certificate_file": self.server_certificate_file
            if self.server_certificate_file
            else None,
            "private_key_file": self.server_private_key_file
            if self.server_private_key_file
            else None,
            "path": self.server_path,
            "tools_path": self.server_tools_path,
            "log_level": self.server_log_level,
            "keepalive_interval": self.server_keepalive_interval,
            "include_tags": self._coerce_to_set(self.server_include_tags)
            if self.server_include_tags
            else None,
            "exclude_tags": self._coerce_to_set(self.server_exclude_tags)
            if self.server_exclude_tags
            else None,
        }

    @property
    def auth(self) -> dict[str, Any]:
        """Get authentication configuration as a dictionary.

        Args:
            None

        Returns:
            dict[str, Any]: Authentication configuration including provider type and
                provider specific settings. Keys with no configured values are omitted.

        Raises:
            None.
        """
        auth_type = (self.server_auth_type or "none").strip().lower()

        audience: str | list[str] | None = None
        if self.server_auth_audience:
            values = self._coerce_to_list(self.server_auth_audience)
            if len(values) == 1:
                audience = values[0]
            elif values:
                audience = values

        required_scopes = (
            self._coerce_to_list(self.server_auth_required_scopes)
            if self.server_auth_required_scopes
            else None
        )

        # Handle OAuth scopes parsing
        oauth_scopes = None
        if self.server_auth_oauth_scopes:
            # Support both space and comma separated scopes
            scopes_str = self.server_auth_oauth_scopes.replace(",", " ")
            oauth_scopes = [s.strip() for s in scopes_str.split() if s.strip()]

        data: dict[str, Any] = {
            "type": auth_type,
            # JWT-specific fields
            "jwks_uri": self.server_auth_jwks_uri or None,
            "public_key": self.server_auth_public_key or None,
            "issuer": self.server_auth_issuer or None,
            "audience": audience,
            "algorithm": self.server_auth_algorithm or None,
            "required_scopes": required_scopes,
            # OAuth-specific fields
            "client_id": self.server_auth_oauth_client_id or None,
            "client_secret": self.server_auth_oauth_client_secret or None,
            "authorization_url": self.server_auth_oauth_authorization_url or None,
            "token_url": self.server_auth_oauth_token_url or None,
            "userinfo_url": self.server_auth_oauth_userinfo_url or None,
            "scopes": oauth_scopes,
            "redirect_uri": self.server_auth_oauth_redirect_uri or None,
            "provider_type": self.server_auth_oauth_provider_type or None,
        }

        return {k: v for k, v in data.items() if v not in (None, "", [])}

    @property
    def platform(self) -> dict:
        """Get platform configuration as a dictionary.

        Args:
            None

        Returns:
            dict: Platform configuration parameters including connection settings,
                authentication credentials, and timeout values.

        Raises:
            None.
        """
        return {
            "host": self.platform_host,
            "port": self.platform_port,
            "use_tls": not self.platform_disable_tls,
            "verify": not self.platform_disable_verify,
            "user": self.platform_user,
            "password": self.platform_password,
            "client_id": None
            if self.platform_client_id == ""
            else self.platform_client_id,
            "client_secret": None
            if self.platform_client_secret == ""
            else self.platform_client_secret,
            "timeout": self.platform_timeout,
        }

    def _coerce_to_set(self, value) -> list:
        """Convert comma-separated string to a set of trimmed strings.

        Args:
            value: Comma-separated string to convert.

        Returns:
            Set of trimmed string elements.

        Raises:
            None.
        """
        items = set()
        for ele in value.split(","):
            items.add(ele.strip())
        return items

    def _coerce_to_list(self, value: str) -> list[str]:
        """Convert comma-separated string to a list of trimmed values.

        Args:
            value (str): Comma separated string value to parse.

        Returns:
            list[str]: List of trimmed values, excluding empty entries.

        Raises:
            None.
        """
        return [item.strip() for item in value.split(",") if item.strip()]


def _get_tools_from_env() -> dict:
    """Parse tool configuration from environment variables.

    Parses environment variables with the pattern ITENTIAL_MCP_TOOL_<tool_name>_<key>
    and returns a nested dictionary structure organized by tool name.

    Expected format: ITENTIAL_MCP_TOOL_<tool_name>_<key>=<value>

    Returns:
        Nested dictionary where keys are tool names and values are
        dictionaries of configuration key-value pairs for each tool.
        Example: {"my_tool": {"name": "value", "type": "endpoint"}}

    Raises:
        ValueError: If environment variable format is invalid or missing required parts.
    """
    tool_config = {}
    prefix = "ITENTIAL_MCP_TOOL_"

    # Filter and process environment variables in a single pass
    for env_key, env_value in os.environ.items():
        if not env_key.startswith(prefix):
            continue

        # Remove prefix and split remaining parts
        remaining = env_key[len(prefix) :]
        parts = remaining.split("_", 2)  # Split into at most 3 parts

        if len(parts) < 2:
            raise ValueError(
                f"Invalid tool environment variable format: {env_key}. "
                f"Expected format: {prefix}<tool_name>_<key>=<value>"
            )

        tool_name, config_key = parts[0], parts[1]

        if not tool_name or not config_key:
            raise ValueError(f"Tool name and config key cannot be empty in: {env_key}")

        # Initialize tool config if not exists
        if tool_name not in tool_config:
            tool_config[tool_name] = {}

        tool_config[tool_name][config_key] = env_value

    return tool_config


@lru_cache(maxsize=None)
def get() -> Config:
    """Return the configuration instance.

    This function will load the configuration and return an instance of
    Config. This function is cached and is safe to call multiple times.
    The configuration is loaded only once and the cached Config instance
    is returned with every call.

    Returns:
        An instance of Config that represents the application configuration.

    Raises:
        FileNotFoundError: If a configuration file is specified but not found.
    """
    conf_file = env.getstr("ITENTIAL_MCP_CONFIG")

    data = {}

    if conf_file is not None:
        path = Path(conf_file)
        if not path.is_file():
            raise FileNotFoundError(f"Config file not found: {path}")

        cf = configparser.ConfigParser()
        cf.read(conf_file)

        tools = []
        tool_config = _get_tools_from_env()

        for item in cf.sections():
            if item.startswith("tool:"):
                _, tool_name = item.split(":")

                t = {"tool_name": tool_name}

                for key, value in cf.items(item):
                    t[key] = value

                if tool_name in tool_config:
                    t.update(tool_config[tool_name])

                if t["type"] == "endpoint":
                    tools.append(EndpointTool(**t))
                else:
                    tools.append(Tool(**t))

            else:
                for key, value in cf.items(item):
                    key = f"{item}_{key}"
                    data[key] = value

        # Add any remaining environment tools not found in config file
        for tool_name, tool_data in tool_config.items():
            if not any(t.tool_name == tool_name for t in tools):
                tool_data["tool_name"] = tool_name
                if tool_data.get("type") == "endpoint":
                    tools.append(EndpointTool(**tool_data))
                else:
                    tools.append(Tool(**tool_data))

    else:
        # No config file, but check for environment variables
        tool_config = _get_tools_from_env()
        tools = []

        for tool_name, tool_data in tool_config.items():
            tool_data["tool_name"] = tool_name
            if tool_data.get("type") == "endpoint":
                tools.append(EndpointTool(**tool_data))
            else:
                tools.append(Tool(**tool_data))

    if tools:
        data["tools"] = tools

    return Config(**data)
