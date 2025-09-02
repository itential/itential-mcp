# Copyright (c) 2025 Itential, Inc
# GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)

import os
import configparser

from functools import lru_cache
from pathlib import Path

from typing import Literal
from dataclasses import fields

from pydantic import Field
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

    def _coerce_to_set(self, value: str) -> set:
        """Convert a comma-separated string to a set of trimmed values.
        
        Args:
            value (str): A comma-separated string to convert to a set.
            
        Returns:
            set: A set containing the trimmed individual values.
            
        Raises:
            AttributeError: If value is None or not a string.
        """
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

        for item in cf.sections():
            for key, value in cf.items(item):
                key = f"{item}_{key}"
                data[key] = value

    for item in fields(Config):
        envkey = f"ITENTIAL_MCP_{item.name}".upper()
        if envkey in os.environ:
            value = ", ".join(os.environ[envkey].split(","))
            data[item.name] = value

    return Config(**data)
