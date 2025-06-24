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


@dataclass(frozen=True)
class Config(object):

    server_transport: Literal["stdio", "sse", "streamable-http"] = Field(default="stdio")
    server_host: str = Field(default="127.0.0.1")
    server_port: int = Field(default=0)
    server_path: str = Field(default="/mcp")
    server_log_level: Literal["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"] = Field(default="INFO")
    server_include_tags: str | None = Field(default=None)
    server_exclude_tags: str | None = Field(default="experimental,beta")

    platform_host: str = Field(default="localhost")
    platform_port: int = Field(default=0)
    platform_disable_tls: bool = Field(default=False)
    platform_disable_verify: bool = Field(default=False)
    platform_user: str = Field(default="admin")
    platform_password: str = Field(default="admin")
    platform_client_id: str | None = Field(default=None)
    platform_client_secret: str | None = Field(default=None)
    platform_timeout: int = Field(default=30)

    @property
    def server(self):
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
    def platform(self):
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
