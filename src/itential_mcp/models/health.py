# Copyright (c) 2025 Itential, Inc
# GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import annotations

import inspect
from typing import Annotated, Literal

from pydantic import BaseModel, Field, field_validator


class ServiceStatus(BaseModel):
    """
    Represents the status of an individual service within the platform.

    This model contains information about core platform services like
    Redis and MongoDB, including their operational state.
    """

    service: Annotated[
        str,
        Field(
            description=inspect.cleandoc(
                """
                The name of the service (e.g., 'redis', 'mongo')
                """
            )
        ),
    ]

    status: Annotated[
        str,
        Field(
            description=inspect.cleandoc(
                """
                The current status of the service (e.g., 'running', 'stopped')
                """
            )
        ),
    ]


class PlatformStatus(BaseModel):
    """
    Represents the overall platform status information.

    This model contains high-level platform information including host details,
    service statuses, and overall system health indicators.
    """

    host: Annotated[
        str,
        Field(
            description=inspect.cleandoc(
                """
                The hostname of the platform instance
                """
            )
        ),
    ]

    server_id: Annotated[
        str,
        Field(
            alias="serverId",
            description=inspect.cleandoc(
                """
                Unique server identifier for the platform instance
                """
            ),
        ),
    ]

    server_name: Annotated[
        str | None,
        Field(
            alias="serverName",
            description=inspect.cleandoc(
                """
                Optional server name for the platform instance
                """
            ),
            default=None,
        ),
    ]

    services: Annotated[
        list[ServiceStatus],
        Field(
            description=inspect.cleandoc(
                """
                List of core platform services and their current status
                """
            ),
            default_factory=list,
        ),
    ]

    timestamp: Annotated[
        int,
        Field(
            description=inspect.cleandoc(
                """
                Unix timestamp when the status was collected
                """
            )
        ),
    ]

    apps: Annotated[
        str,
        Field(
            description=inspect.cleandoc(
                """
                Overall status of applications (e.g., 'running', 'degraded')
                """
            )
        ),
    ]

    adapters: Annotated[
        str,
        Field(
            description=inspect.cleandoc(
                """
                Overall status of adapters (e.g., 'running', 'degraded')
                """
            )
        ),
    ]


class CpuTimes(BaseModel):
    """
    Represents CPU time statistics for a CPU core.

    This model contains detailed timing information about how CPU cycles
    are being utilized across different execution contexts.
    """

    user: Annotated[
        int,
        Field(
            description=inspect.cleandoc(
                """
                CPU time spent in user mode (microseconds)
                """
            )
        ),
    ]

    nice: Annotated[
        int,
        Field(
            description=inspect.cleandoc(
                """
                CPU time spent on low priority processes (microseconds)
                """
            )
        ),
    ]

    sys: Annotated[
        int,
        Field(
            description=inspect.cleandoc(
                """
                CPU time spent in system mode (microseconds)
                """
            )
        ),
    ]

    idle: Annotated[
        int,
        Field(
            description=inspect.cleandoc(
                """
                CPU time spent idle (microseconds)
                """
            )
        ),
    ]

    irq: Annotated[
        int,
        Field(
            description=inspect.cleandoc(
                """
                CPU time spent servicing interrupts (microseconds)
                """
            )
        ),
    ]


class CpuInfo(BaseModel):
    """
    Represents information about a CPU core.

    This model contains details about individual CPU cores including
    model information, current speed, and time utilization statistics.
    """

    model: Annotated[
        str,
        Field(
            description=inspect.cleandoc(
                """
                CPU model name and specifications
                """
            )
        ),
    ]

    speed: Annotated[
        int,
        Field(
            description=inspect.cleandoc(
                """
                Current CPU speed in MHz
                """
            )
        ),
    ]

    times: Annotated[
        CpuTimes,
        Field(
            description=inspect.cleandoc(
                """
                CPU time statistics for this core
                """
            )
        ),
    ]


class SystemInfo(BaseModel):
    """
    Represents system-level hardware and OS information.

    This model contains comprehensive system information including
    architecture, memory, load averages, and CPU details.
    """

    arch: Annotated[
        str,
        Field(
            description=inspect.cleandoc(
                """
                System architecture (e.g., 'x64', 'arm64')
                """
            )
        ),
    ]

    release: Annotated[
        str,
        Field(
            description=inspect.cleandoc(
                """
                Operating system release version
                """
            )
        ),
    ]

    uptime: Annotated[
        float,
        Field(
            description=inspect.cleandoc(
                """
                System uptime in seconds
                """
            )
        ),
    ]

    free_mem: Annotated[
        int,
        Field(
            alias="freemem",
            description=inspect.cleandoc(
                """
                Free system memory in bytes
                """
            ),
        ),
    ]

    total_mem: Annotated[
        int,
        Field(
            alias="totalmem",
            description=inspect.cleandoc(
                """
                Total system memory in bytes
                """
            ),
        ),
    ]

    load_avg: Annotated[
        list[float],
        Field(
            alias="loadavg",
            description=inspect.cleandoc(
                """
                System load averages for 1, 5, and 15 minutes
                """
            ),
        ),
    ]

    cpus: Annotated[
        list[CpuInfo],
        Field(
            description=inspect.cleandoc(
                """
                Information about each CPU core
                """
            ),
            default_factory=list,
        ),
    ]


class MemoryUsage(BaseModel):
    """
    Represents memory usage statistics for a process.

    This model contains detailed memory utilization information including
    heap usage, external memory, and array buffers.
    """

    rss: Annotated[
        int,
        Field(
            description=inspect.cleandoc(
                """
                Resident Set Size - physical memory currently used by the process in bytes
                """
            )
        ),
    ]

    heap_total: Annotated[
        int,
        Field(
            alias="heapTotal",
            description=inspect.cleandoc(
                """
                Total heap memory allocated in bytes
                """
            ),
        ),
    ]

    heap_used: Annotated[
        int,
        Field(
            alias="heapUsed",
            description=inspect.cleandoc(
                """
                Heap memory currently used in bytes
                """
            ),
        ),
    ]

    external: Annotated[
        int,
        Field(
            description=inspect.cleandoc(
                """
                External memory used by C++ objects bound to JavaScript objects in bytes
                """
            )
        ),
    ]

    array_buffers: Annotated[
        int,
        Field(
            alias="arrayBuffers",
            description=inspect.cleandoc(
                """
                Memory allocated for ArrayBuffers and SharedArrayBuffers in bytes
                """
            ),
        ),
    ]


class CpuUsage(BaseModel):
    """
    Represents CPU usage statistics for a process.

    This model contains CPU time utilization information for both
    user and system execution contexts.
    """

    user: Annotated[
        int,
        Field(
            description=inspect.cleandoc(
                """
                CPU time spent in user mode by the process in microseconds
                """
            )
        ),
    ]

    system: Annotated[
        int,
        Field(
            description=inspect.cleandoc(
                """
                CPU time spent in system mode by the process in microseconds
                """
            )
        ),
    ]


class ServerVersions(BaseModel):
    """
    Represents version information for Node.js and its dependencies.

    This model contains comprehensive version information about the Node.js
    runtime and all its core components and libraries.
    """

    node: Annotated[str, Field(description="Node.js version")]
    acorn: Annotated[str, Field(description="Acorn JavaScript parser version")]
    ada: Annotated[str, Field(description="Ada URL parser version")]
    ares: Annotated[str, Field(description="c-ares DNS resolver version")]
    base64: Annotated[
        str | None,
        Field(description="Base64 encoding library version", default=None),
    ]
    brotli: Annotated[str, Field(description="Brotli compression library version")]
    cjs_module_lexer: Annotated[
        str,
        Field(alias="cjs_module_lexer", description="CommonJS module lexer version"),
    ]
    cldr: Annotated[str, Field(description="Unicode CLDR data version")]
    icu: Annotated[str, Field(description="ICU internationalization library version")]
    llhttp: Annotated[str, Field(description="HTTP parser library version")]
    modules: Annotated[str, Field(description="Node.js ABI version")]
    napi: Annotated[str, Field(description="Node-API version")]
    nghttp2: Annotated[str, Field(description="HTTP/2 library version")]
    nghttp3: Annotated[
        str | None, Field(description="HTTP/3 library version", default=None)
    ]
    ngtcp2: Annotated[
        str | None, Field(description="QUIC library version", default=None)
    ]
    openssl: Annotated[str, Field(description="OpenSSL cryptographic library version")]
    simdutf: Annotated[str, Field(description="SIMD UTF validation library version")]
    tz: Annotated[str, Field(description="Timezone data version")]
    undici: Annotated[str, Field(description="HTTP client library version")]
    unicode: Annotated[str, Field(description="Unicode standard version")]
    uv: Annotated[str, Field(description="libuv asynchronous I/O library version")]
    uvwasi: Annotated[str, Field(description="WASI implementation version")]
    v8: Annotated[str, Field(description="V8 JavaScript engine version")]
    zlib: Annotated[str, Field(description="zlib compression library version")]


class ServerInfo(BaseModel):
    """
    Represents comprehensive server runtime information.

    This model contains detailed information about the Node.js server
    including versions, resource usage, dependencies, and runtime metrics.
    """

    version: Annotated[
        str,
        Field(
            description=inspect.cleandoc(
                """
                Itential Platform version
                """
            )
        ),
    ]

    release: Annotated[
        str,
        Field(
            description=inspect.cleandoc(
                """
                Itential Platform release version
                """
            )
        ),
    ]

    arch: Annotated[
        str,
        Field(
            description=inspect.cleandoc(
                """
                Server architecture (e.g., 'x64')
                """
            )
        ),
    ]

    platform: Annotated[
        str,
        Field(
            description=inspect.cleandoc(
                """
                Operating system platform (e.g., 'linux', 'win32')
                """
            )
        ),
    ]

    versions: Annotated[
        ServerVersions,
        Field(
            description=inspect.cleandoc(
                """
                Version information for Node.js and its dependencies
                """
            )
        ),
    ]

    memory_usage: Annotated[
        MemoryUsage,
        Field(
            alias="memoryUsage",
            description=inspect.cleandoc(
                """
                Memory usage statistics for the main server process
                """
            ),
        ),
    ]

    cpu_usage: Annotated[
        CpuUsage,
        Field(
            alias="cpuUsage",
            description=inspect.cleandoc(
                """
                CPU usage statistics for the main server process
                """
            ),
        ),
    ]

    uptime: Annotated[
        float,
        Field(
            description=inspect.cleandoc(
                """
                Server process uptime in seconds
                """
            )
        ),
    ]

    pid: Annotated[
        int,
        Field(
            description=inspect.cleandoc(
                """
                Process ID of the main server process
                """
            )
        ),
    ]

    dependencies: Annotated[
        dict[str, str],
        Field(
            description=inspect.cleandoc(
                """
                Dictionary of key Itential service dependencies and their versions
                """
            ),
            default_factory=dict,
        ),
    ]


class ConnectionInfo(BaseModel):
    """
    Represents connection status information for applications and adapters.

    This model contains information about network connections and
    their current operational state.
    """

    state: Annotated[
        str,
        Field(
            description=inspect.cleandoc(
                """
                Connection state (e.g., 'ONLINE', 'OFFLINE')
                """
            )
        ),
    ]


class LoggerConfig(BaseModel):
    """
    Represents logging configuration for applications and adapters.

    This model contains the current logging levels for different
    output destinations.
    """

    console: Annotated[
        str,
        Field(
            description=inspect.cleandoc(
                """
                Console logging level (e.g., 'info', 'debug', 'warning')
                """
            )
        ),
    ]

    file: Annotated[
        str,
        Field(
            description=inspect.cleandoc(
                """
                File logging level (e.g., 'info', 'debug', 'warning')
                """
            )
        ),
    ]

    syslog: Annotated[
        str | dict,
        Field(
            description=inspect.cleandoc(
                """
                Syslog logging level (e.g., 'info', 'debug', 'warning')
                """
            )
        ),
    ]

    @field_validator("syslog", mode="before")
    @classmethod
    def convert_empty_dict_to_string(cls, value):
        """Convert empty dict to empty string for syslog field.

        This validator normalizes the syslog field by converting empty
        dictionaries to empty strings for consistent data representation.

        Args:
            value: The value to validate, expected to be either a string or dict.

        Returns:
            str: Empty string if value is an empty dict, otherwise returns
                the original value unchanged.

        Raises:
            None
        """
        if isinstance(value, dict) and not value:
            return ""
        return value


class ApplicationInfo(BaseModel):
    """
    Represents detailed information about a running application.

    This model contains comprehensive application metadata including
    resource usage, operational state, and performance metrics.
    """

    id: Annotated[
        str,
        Field(
            description=inspect.cleandoc(
                """
                Unique application identifier
                """
            )
        ),
    ]

    package_id: Annotated[
        str,
        Field(
            alias="package_id",
            description=inspect.cleandoc(
                """
                NPM package identifier for the application
                """
            ),
        ),
    ]

    version: Annotated[
        str,
        Field(
            description=inspect.cleandoc(
                """
                Application version string
                """
            )
        ),
    ]

    type: Annotated[
        Literal["Application"],
        Field(
            description=inspect.cleandoc(
                """
                Type identifier for applications
                """
            )
        ),
    ]

    description: Annotated[
        str,
        Field(
            description=inspect.cleandoc(
                """
                Human-readable description of the application
                """
            )
        ),
    ]

    route_prefix: Annotated[
        str,
        Field(
            alias="routePrefix",
            description=inspect.cleandoc(
                """
                HTTP route prefix for the application API endpoints
                """
            ),
        ),
    ]

    state: Annotated[
        Literal["RUNNING", "STOPPED", "DEAD", "DELETED"],
        Field(
            description=inspect.cleandoc(
                """
                Current operational state of the application
                """
            )
        ),
    ]

    connection: Annotated[
        ConnectionInfo | None,
        Field(
            description=inspect.cleandoc(
                """
                Connection information (null for running applications)
                """
            ),
            default=None,
        ),
    ]

    uptime: Annotated[
        float,
        Field(
            description=inspect.cleandoc(
                """
                Application uptime in seconds
                """
            )
        ),
    ]

    memory_usage: Annotated[
        MemoryUsage,
        Field(
            alias="memoryUsage",
            description=inspect.cleandoc(
                """
                Current memory usage statistics for the application
                """
            ),
        ),
    ]

    cpu_usage: Annotated[
        CpuUsage,
        Field(
            alias="cpuUsage",
            description=inspect.cleandoc(
                """
                CPU usage statistics for the application
                """
            ),
        ),
    ]

    pid: Annotated[
        int,
        Field(
            description=inspect.cleandoc(
                """
                Process ID of the application
                """
            )
        ),
    ]

    logger: Annotated[
        LoggerConfig,
        Field(
            description=inspect.cleandoc(
                """
                Current logging configuration for the application
                """
            )
        ),
    ]

    timestamp: Annotated[
        int,
        Field(
            description=inspect.cleandoc(
                """
                Unix timestamp of the last status update
                """
            )
        ),
    ]

    prev_uptime: Annotated[
        float,
        Field(
            alias="prevUptime",
            description=inspect.cleandoc(
                """
                Previous uptime measurement in seconds
                """
            ),
        ),
    ]


class AdapterInfo(BaseModel):
    """
    Represents detailed information about a running adapter.

    This model contains comprehensive adapter metadata including
    resource usage, operational state, and connectivity information.
    """

    id: Annotated[
        str,
        Field(
            description=inspect.cleandoc(
                """
                Unique adapter identifier
                """
            )
        ),
    ]

    package_id: Annotated[
        str,
        Field(
            alias="package_id",
            description=inspect.cleandoc(
                """
                NPM package identifier for the adapter
                """
            ),
        ),
    ]

    version: Annotated[
        str,
        Field(
            description=inspect.cleandoc(
                """
                Adapter version string
                """
            )
        ),
    ]

    type: Annotated[
        Literal["Adapter"],
        Field(
            description=inspect.cleandoc(
                """
                Type identifier for adapters
                """
            )
        ),
    ]

    description: Annotated[
        str,
        Field(
            description=inspect.cleandoc(
                """
                Human-readable description of the adapter
                """
            )
        ),
    ]

    route_prefix: Annotated[
        str,
        Field(
            alias="routePrefix",
            description=inspect.cleandoc(
                """
                HTTP route prefix for the adapter API endpoints
                """
            ),
        ),
    ]

    state: Annotated[
        Literal["RUNNING", "STOPPED", "DEAD", "DELETED"],
        Field(
            description=inspect.cleandoc(
                """
                Current operational state of the adapter
                """
            )
        ),
    ]

    connection: Annotated[
        ConnectionInfo,
        Field(
            description=inspect.cleandoc(
                """
                Connection status information for the adapter
                """
            )
        ),
    ]

    uptime: Annotated[
        float,
        Field(
            description=inspect.cleandoc(
                """
                Adapter uptime in seconds
                """
            )
        ),
    ]

    memory_usage: Annotated[
        MemoryUsage,
        Field(
            alias="memoryUsage",
            description=inspect.cleandoc(
                """
                Current memory usage statistics for the adapter
                """
            ),
        ),
    ]

    cpu_usage: Annotated[
        CpuUsage,
        Field(
            alias="cpuUsage",
            description=inspect.cleandoc(
                """
                CPU usage statistics for the adapter
                """
            ),
        ),
    ]

    pid: Annotated[
        int,
        Field(
            description=inspect.cleandoc(
                """
                Process ID of the adapter
                """
            )
        ),
    ]

    logger: Annotated[
        LoggerConfig,
        Field(
            description=inspect.cleandoc(
                """
                Current logging configuration for the adapter
                """
            )
        ),
    ]

    timestamp: Annotated[
        int,
        Field(
            description=inspect.cleandoc(
                """
                Unix timestamp of the last status update
                """
            )
        ),
    ]

    prev_uptime: Annotated[
        float,
        Field(
            alias="prevUptime",
            description=inspect.cleandoc(
                """
                Previous uptime measurement in seconds
                """
            ),
        ),
    ]


class HealthResponse(BaseModel):
    """
    Comprehensive health information response from Itential Platform.

    This model represents the complete health status of an Itential Platform
    instance, including system metrics, application states, adapter status,
    and server performance information. It provides a holistic view of
    platform health for monitoring and troubleshooting purposes.
    """

    status: Annotated[
        PlatformStatus,
        Field(
            description=inspect.cleandoc(
                """
                Overall platform status including service states and health indicators
                """
            )
        ),
    ]

    system: Annotated[
        SystemInfo,
        Field(
            description=inspect.cleandoc(
                """
                System-level hardware and operating system information
                """
            )
        ),
    ]

    server: Annotated[
        ServerInfo,
        Field(
            description=inspect.cleandoc(
                """
                Node.js server runtime information and performance metrics
                """
            )
        ),
    ]

    applications: Annotated[
        list[ApplicationInfo],
        Field(
            description=inspect.cleandoc(
                """
                Complete list of applications with their current status and resource usage
                """
            ),
            default_factory=list,
        ),
    ]

    adapters: Annotated[
        list[AdapterInfo],
        Field(
            description=inspect.cleandoc(
                """
                Complete list of adapters with their current status and connectivity information
                """
            ),
            default_factory=list,
        ),
    ]
