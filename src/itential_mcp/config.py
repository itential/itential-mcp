# Copyright (c) 2025 Itential, Inc
# GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)

import os
import configparser
import re

from functools import lru_cache
from pathlib import Path

from typing import Literal, List
from dataclasses import fields

from pydantic import Field, field_validator
from pydantic.dataclasses import dataclass

from . import env


def options(*args, **kwargs) -> dict:
    """
    Utility function to add extra parameters to fields

    This function will add extra parameters to to a Field in the Config
    class.  Specifically it handles adding the necessary keys to support
    generating the CLI options from the configuration.  This unifies the
    parameter descriptions and default values for consistency.

    Args:
        *args: Positional arguments to be added to the CLI command line option
        **kwargs: Optional arguments to be added to the CLI command line option

    Returns:
        dict: A Python dict object to be added to the Field function
            signature

    Raises:
        None
    """
    return {
        "x-itential-mcp-cli-enabled": True,
        "x-itential-mcp-arguments": args,
        "x-itential-mcp-options": kwargs
    }


def validate_tool_name(tool_name: str) -> str:
    """
    Validate that a tool name follows the required naming convention.

    Tool names must start with a letter and only contain letters, numbers,
    and underscores. This ensures compatibility with Python function naming
    and prevents injection attacks.

    Args:
        tool_name (str): The tool name to validate

    Returns:
        str: The validated tool name

    Raises:
        ValueError: If the tool name does not match the required pattern
    """
    if not tool_name:
        raise ValueError("Tool name cannot be empty")
    
    pattern = r'^[a-zA-Z][a-zA-Z0-9_]*$'
    if not re.match(pattern, tool_name):
        raise ValueError(
            f"Tool name '{tool_name}' is invalid. Tool names must start with a letter "
            "and only contain letters, numbers, and underscores."
        )
    
    return tool_name


@dataclass(frozen=True)
class Tool(object):

    name: str = Field(
        description = "The name of the asset in Itential Platform",
    )

    tool_name: str = Field(
        description = "The tool name that is exposed"
    )

    type: Literal["endpoint"] = Field(
        description = "The tool type"
    )

    description: str = Field(
        description = "Description of this tool",
        default = None
    )

    tags: str = Field(
        description = "List of comma separated tags applied to this tool",
        default = None
    )

    @field_validator('tool_name')
    @classmethod
    def validate_tool_name_field(cls, v: str) -> str:
        """
        Validate tool_name field using the validate_tool_name function.

        Args:
            v (str): The tool_name value to validate

        Returns:
            str: The validated tool_name

        Raises:
            ValueError: If the tool_name is invalid
        """
        return validate_tool_name(v)


@dataclass(frozen=True)
class EndpointTool(Tool):

    automation: str = Field(
        description = "The name of the automation the trigger is associated with"
    )


@dataclass(frozen=True)
class Config(object):

    server_transport: Literal["stdio", "sse", "http"] = Field(
        description="The MCP server transport to use",
        default="stdio",
        json_schema_extra=options(
            "--transport",
            choices=("stdio", "sse", "http"),
            metavar="<value>"
        )
    )


    server_host: str = Field(
        description="Address to listen for connections on",
        default="127.0.0.1",
        json_schema_extra=options(
            "--host",
            metavar="<host>"
        )
    )

    server_port: int = Field(
        description="Port to listen for connections on",
        default=8000,
        json_schema_extra=options(
            "--port",
            metavar="<port>",
            type=int
        )
    )

    server_path: str = Field(
        description="URI path used to accept requests from",
        default="/mcp",
        json_schema_extra=options(
            "--path",
            metavar="<path>"
        )
    )

    server_log_level: Literal["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"] = Field(
        description="Logging level for verbose output",
        default="INFO",
        json_schema_extra=options(
            "--log-level",
            metavar="<level>"
        )
    )

    server_include_tags: str | None = Field(
        description="Include tools that match at least on tag",
        default=None,
        json_schema_extra=options(
            "--include-tags",
            metavar="<tags>"
        )
    )

    server_exclude_tags: str | None = Field(
        description="Exclude any tool that matches one of these tags",
        default="experimental,beta",
        json_schema_extra=options(
            "--exclude-tags",
            metavar="<tags>"
        )
    )

    platform_host: str = Field(
        description="The host addres of the Itential Platform server",
        default="localhost",
        json_schema_extra=options(
            "--platform-host",
            metavar="<host>"
        )
    )

    platform_port: int = Field(
        description="The port to use when connecting to Itential Platform",
        default=0,
        json_schema_extra=options(
            "--platform-port",
            type=int,
            metavar="<port>",
        )
    )

    platform_disable_tls: bool = Field(
        description="Disable using TLS to connect to the server",
        default=False,
        json_schema_extra=options(
            "--platform-disable-tls",
            action="store_true"
        )
    )

    platform_disable_verify: bool = Field(
        description="Disable certificate verification",
        default=False,
        json_schema_extra=options(
            "--platform-disable-verify",
            action="store_true"
        )
    )

    platform_user: str = Field(
        description="Username to use when authenticating to the server",
        default="admin",
        json_schema_extra=options(
            "--platform-user",
            metavar="<user>"
        )
    )

    platform_password: str = Field(
        description="Password to use when authenticating to the server",
        default="admin",
        json_schema_extra=options(
            "--platform-password",
            metavar="<password>"
        )
    )

    platform_client_id: str | None = Field(
        description="Client ID to use when authenticating using OAuth",
        default=None,
        json_schema_extra=options(
            "--platform-client-id",
            metavar="<client_id>"
        )
    )

    platform_client_secret: str | None = Field(
        description="Client secret to use when authenticating using OAuth",
        default=None,
        json_schema_extra=options(
            "--platform-client-secret",
            metavar="<client_secret>"

        )
    )

    platform_timeout: int = Field(
        description="Sets the timeout in seconds when communciating with the server",
        default=30,
        json_schema_extra=options(
            "--platform-timeout",
            metavar="<secs>"
        )
    )

    tools: List[Tool] = Field(
        description = "List of Itential Platform assets to be exposed as tools",
        default_factory = list
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
            "log_level": self.server_log_level,
            "include_tags": self._coerce_to_set(self.server_include_tags) if self.server_include_tags else None,
            "exclude_tags": self._coerce_to_set(self.server_exclude_tags) if self.server_exclude_tags else None
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
            "client_id": None if self.platform_client_id == "" else self.platform_client_id,
            "client_secret": None if self.platform_client_secret == "" else self.platform_client_secret,
            "timeout": self.platform_timeout
        }

    def _coerce_to_set(self, value) -> list:
        items = set()
        for ele in value.split(","):
            items.add(ele.strip())
        return items


@lru_cache(maxsize=None)
def get() -> Config:
    """
    Return the configuration instance

    This function will load the configuration and return an instance of
    Config.  This function is cached and is safe to call multiple times.
    The configuration is loaded only once and the cached Config instance
    is returned with every call.

    Args:
        None

    Returns:
        Conig: An instance of Config that represents the application
            configuration

    Raises:
        FileNotFoundError: If a configuration file is specified but not found
            this exception is raised
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

        for item in cf.sections():
            if item.startswith("tool:"):
                _, tool_name = item.split(":")

                t = {"tool_name": tool_name}

                for key, value in cf.items(item):
                    t[key] = value

                if t["type"] == "endpoint":
                    tools.append(EndpointTool(**t))
                else:
                    tools.append(Tool(**t))

            else:
                for key, value in cf.items(item):
                    key = f"{item}_{key}"
                    data[key] = value

        data["tools"] = tools

    for item in fields(Config):
        envkey = f"ITENTIAL_MCP_{item.name}".upper()
        if envkey in os.environ:
            value = ", ".join(os.environ[envkey].split(","))
            data[item.name] = value


    return Config(**data)
