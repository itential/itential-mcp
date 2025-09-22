# Copyright (c) 2025 Itential, Inc
# GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)

import os
import configparser
import re

from functools import lru_cache, partial
from pathlib import Path

from typing import Literal, List, Callable

from pydantic import Field, field_validator
from pydantic.dataclasses import dataclass

from . import env
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
    cluster: str = Field(
        description="The cluster where the Gateway service resides"
    )


@dataclass(frozen=True)
class Config(object):
    server_transport: Literal["stdio", "sse", "http"] = Field(
        description="The MCP server transport to use",
        default_factory=default_factory(
            env.getstr,
            "ITENTIAL_MCP_SERVER_TRANSPORT",
        ),
        json_schema_extra=options(
            "--transport",
            choices=("stdio", "sse", "http"),
            metavar="<value>"
        ),
    )

    server_host: str = Field(
        description="Address to listen for connections on",
        default_factory=default_factory(
            env.getstr,
            "ITENTIAL_MCP_SERVER_HOST",
        ),
        json_schema_extra=options(
            "--host",
            metavar="<host>"
        ),
    )

    server_port: int = Field(
        description="Port to listen for connections on",
        default_factory=default_factory(
            env.getint,
            "ITENTIAL_MCP_SERVER_PORT",
        ),
        json_schema_extra=options(
            "--port",
            metavar="<port>",
            type=int
        ),
    )

    server_path: str = Field(
        description="URI path used to accept requests from",
        default_factory=default_factory(
            env.getstr,
            "ITENTIAL_MCP_SERVER_PATH"
        ),
        json_schema_extra=options(
            "--path",
            metavar="<path>"
        ),
    )

    server_log_level: Literal["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"] = Field(
        description="Logging level for verbose output",
        default_factory=default_factory(
            env.getstr,
            "ITENTIAL_MCP_SERVER_LOG_LEVEL"
        ),
        json_schema_extra=options(
            "--log-level",
            metavar="<level>"
        ),
    )

    server_include_tags: str | None = Field(
        description="Include tools that match at least on tag",
        default_factory=default_factory(
            env.getstr,
            "ITENTIAL_MCP_SERVER_INCLUDE_TAGS"
        ),
        json_schema_extra=options(
            "--include-tags",
            metavar="<tags>"
        ),
    )

    server_exclude_tags: str | None = Field(
        description="Exclude any tool that matches one of these tags",
        default_factory=default_factory(
            env.getstr,
            "ITENTIAL_MCP_SERVER_EXCLUDE_TAGS",
        ),
        json_schema_extra=options(
            "--exclude-tags",
            metavar="<tags>"
        ),
    )

    server_tools_path: str | None = Field(
        description="Custom path to load tools from",
        default_factory=default_factory(
            env.getstr,
            "ITENTIAL_MCP_SERVER_TOOLS_PATH"
        ),
        json_schema_extra=options(
            "--tools-path",
            metavar="<path>",
        )
    )

    platform_host: str = Field(
        description="The host addres of the Itential Platform server",
        default_factory=default_factory(
            env.getstr,
            "ITENTIAL_MCP_PLATFORM_HOST",
        ),
        json_schema_extra=options(
            "--platform-host",
            metavar="<host>"
        ),
    )

    platform_port: int = Field(
        description="The port to use when connecting to Itential Platform",
        default_factory=default_factory(
            env.getint,
            "ITENTIAL_MCP_PLATFORM_PORT"
        ),
        json_schema_extra=options(
            "--platform-port",
            type=int,
            metavar="<port>",
        ),
    )

    platform_disable_tls: bool = Field(
        description="Disable using TLS to connect to the server",
        default_factory=default_factory(
            env.getbool,
            "ITENTIAL_MCP_PLATFORM_DISABLE_TLS"
        ),
        json_schema_extra=options(
            "--platform-disable-tls",
            action="store_true"
        ),
    )

    platform_disable_verify: bool = Field(
        description="Disable certificate verification",
        default_factory=default_factory(
            env.getbool,
            "ITENTIAL_MCP_PLATFORM_DISABLE_VERIFY"
        ),
        json_schema_extra=options(
            "--platform-disable-verify",
            action="store_true"
        ),
    )

    platform_user: str = Field(
        description="Username to use when authenticating to the server",
        default_factory=default_factory(
            env.getstr,
            "ITENTIAL_MCP_PLATFORM_USER"
        ),
        json_schema_extra=options(
            "--platform-user",
            metavar="<user>"
        ),
    )

    platform_password: str = Field(
        description="Password to use when authenticating to the server",
        default_factory=default_factory(
            env.getstr,
            "ITENTIAL_MCP_PLATFORM_PASSWORD"
        ),
        json_schema_extra=options(
            "--platform-password",
            metavar="<password>"
        ),
    )

    platform_client_id: str | None = Field(
        description="Client ID to use when authenticating using OAuth",
        default_factory=default_factory(
            env.getstr,
            "ITENTIAL_MCP_PLATFORM_CLIENT_ID"
        ),
        json_schema_extra=options(
            "--platform-client-id",
            metavar="<client_id>"
        ),
    )

    platform_client_secret: str | None = Field(
        description="Client secret to use when authenticating using OAuth",
        default_factory=default_factory(
            env.getstr,
            "ITENTIAL_MCP_PLATFORM_CLIENT_SECRET"
        ),
        json_schema_extra=options(
            "--platform-client-secret",
            metavar="<client_secret>"
        ),
    )

    platform_timeout: int = Field(
        description="Sets the timeout in seconds when communciating with the server",
        default_factory=default_factory(
            env.getint,
            "ITENTIAL_MCP_PLATFORM_TIMEOUT"
        ),
        json_schema_extra=options(
            "--platform-timeout",
            metavar="<secs>"
        ),
    )

    tools: List[Tool] = Field(
        description="List of Itential Platform assets to be exposed as tools",
        default_factory=list,
    )

    @property
    def server(self) -> dict:
        """Get server configuration as a dictionary.

        Returns:
            dict: Server configuration parameters including transport, host, port,
                path, log level, and tag filtering settings.
        """
        return {
            "transport": self.server_transport,
            "host": self.server_host,
            "port": self.server_port,
            "path": self.server_path,
            "tools_path": self.server_tools_path,
            "log_level": self.server_log_level,
            "include_tags": self._coerce_to_set(self.server_include_tags) if self.server_include_tags else None,
            "exclude_tags": self._coerce_to_set(self.server_exclude_tags) if self.server_exclude_tags else None,
        }

    @property
    def platform(self) -> dict:
        """Get platform configuration as a dictionary.

        Returns:
            dict: Platform configuration parameters including connection settings,
                authentication credentials, and timeout values.
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
        """
        items = set()
        for ele in value.split(","):
            items.add(ele.strip())
        return items


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
