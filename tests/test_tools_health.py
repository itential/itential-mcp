# Copyright (c) 2025 Itential, Inc
# GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

import pytest
from unittest.mock import AsyncMock, MagicMock

from itential_mcp.tools.health import get_health
from itential_mcp.models.health import HealthResponse
from fastmcp import Context


class TestHealthTool:
    """Test cases for the health tool functions."""

    def setup_method(self):
        """Set up test fixtures before each test method."""
        self.mock_context = AsyncMock(spec=Context)
        self.mock_context.info = AsyncMock()

        # Create mock client with health service
        self.mock_client = MagicMock()
        self.mock_health_service = MagicMock()

        # Set up async methods on health service
        self.mock_health_service.get_status_health = AsyncMock()
        self.mock_health_service.get_system_health = AsyncMock()
        self.mock_health_service.get_server_health = AsyncMock()
        self.mock_health_service.get_applications_health = AsyncMock()
        self.mock_health_service.get_adapters_health = AsyncMock()

        # Attach health service to client
        self.mock_client.health = self.mock_health_service

        # Set up context to return the mock client
        self.mock_context.request_context.lifespan_context.get.return_value = (
            self.mock_client
        )

    def create_mock_health_data(self):
        """Create comprehensive mock health data for testing."""
        return {
            "status_data": {
                "host": "test.platform",
                "serverId": "test-server-123",
                "serverName": None,
                "services": [{"service": "redis", "status": "running"}],
                "timestamp": 1757004595716,
                "apps": "running",
                "adapters": "running",
            },
            "system_data": {
                "arch": "x64",
                "release": "6.13.12-100.fc40.x86_64",
                "uptime": 4668812.41,
                "freemem": 53953363968,
                "totalmem": 67111694336,
                "loadavg": [0.15, 0.22, 0.25],
                "cpus": [
                    {
                        "model": "Intel(R) Core(TM) i7-12700H CPU @ 2.30GHz",
                        "speed": 4015,
                        "times": {
                            "user": 52081020,
                            "nice": 26850,
                            "sys": 18688410,
                            "idle": 4564187990,
                            "irq": 7986130,
                        },
                    }
                ],
            },
            "server_data": {
                "version": "15.8.10-2023.2.44",
                "release": "2023.2.9",
                "arch": "x64",
                "platform": "linux",
                "versions": {
                    "node": "20.3.0",
                    "acorn": "8.8.2",
                    "ada": "2.5.0",
                    "ares": "1.19.1",
                    "base64": "0.5.0",
                    "brotli": "1.0.9",
                    "cjs_module_lexer": "1.2.2",
                    "cldr": "43.0",
                    "icu": "73.1",
                    "llhttp": "8.1.0",
                    "modules": "115",
                    "napi": "9",
                    "nghttp2": "1.53.0",
                    "nghttp3": "0.7.0",
                    "ngtcp2": "0.8.1",
                    "openssl": "3.0.8+quic",
                    "simdutf": "3.2.12",
                    "tz": "2023c",
                    "undici": "5.22.1",
                    "unicode": "15.0",
                    "uv": "1.45.0",
                    "uvwasi": "0.0.18",
                    "v8": "11.3.244.8-node.9",
                    "zlib": "1.2.13.1-motley",
                },
                "memoryUsage": {
                    "rss": 469671936,
                    "heapTotal": 158703616,
                    "heapUsed": 147501584,
                    "external": 50291978,
                    "arrayBuffers": 46521129,
                },
                "cpuUsage": {"user": 3815108692, "system": 621631048},
                "uptime": 2083622.963931177,
                "pid": 1,
                "dependencies": {"@itential/service": "3.1.12"},
            },
            "applications_data": {
                "results": [
                    {
                        "id": "TestApp",
                        "package_id": "@itential/test-app",
                        "version": "1.0.0",
                        "type": "Application",
                        "description": "Test application",
                        "routePrefix": "test-app",
                        "state": "RUNNING",
                        "connection": None,
                        "uptime": 1000.0,
                        "memoryUsage": {
                            "rss": 100000000,
                            "heapTotal": 50000000,
                            "heapUsed": 40000000,
                            "external": 5000000,
                            "arrayBuffers": 4000000,
                        },
                        "cpuUsage": {"user": 1000000, "system": 500000},
                        "pid": 123,
                        "logger": {
                            "console": "info",
                            "file": "info",
                            "syslog": "warning",
                        },
                        "timestamp": 1757004595716,
                        "prevUptime": 999.0,
                    }
                ]
            },
            "adapters_data": {
                "results": [
                    {
                        "id": "TestAdapter",
                        "package_id": "@itential/test-adapter",
                        "version": "1.0.0",
                        "type": "Adapter",
                        "description": "Test adapter",
                        "routePrefix": "test-adapter",
                        "state": "RUNNING",
                        "connection": {"state": "ONLINE"},
                        "uptime": 2000.0,
                        "memoryUsage": {
                            "rss": 150000000,
                            "heapTotal": 70000000,
                            "heapUsed": 60000000,
                            "external": 8000000,
                            "arrayBuffers": 7000000,
                        },
                        "cpuUsage": {"user": 2000000, "system": 1000000},
                        "pid": 456,
                        "logger": {
                            "console": "info",
                            "file": "info",
                            "syslog": "warning",
                        },
                        "timestamp": 1757004595716,
                        "prevUptime": 1999.0,
                    }
                ]
            },
        }

    @pytest.mark.asyncio
    async def test_get_health_success(self):
        """Test get_health returns comprehensive health data successfully."""
        # Set up mock data
        mock_data = self.create_mock_health_data()

        # Configure service method returns
        self.mock_health_service.get_status_health.return_value = mock_data[
            "status_data"
        ]
        self.mock_health_service.get_system_health.return_value = mock_data[
            "system_data"
        ]
        self.mock_health_service.get_server_health.return_value = mock_data[
            "server_data"
        ]
        self.mock_health_service.get_applications_health.return_value = mock_data[
            "applications_data"
        ]
        self.mock_health_service.get_adapters_health.return_value = mock_data[
            "adapters_data"
        ]

        # Call the function
        result = await get_health(self.mock_context)

        # Verify context info was called
        self.mock_context.info.assert_called_once_with("inside get_health(...)")

        # Verify all service methods were called
        self.mock_health_service.get_status_health.assert_called_once()
        self.mock_health_service.get_system_health.assert_called_once()
        self.mock_health_service.get_server_health.assert_called_once()
        self.mock_health_service.get_applications_health.assert_called_once()
        self.mock_health_service.get_adapters_health.assert_called_once()

        # Verify result is a HealthResponse
        assert isinstance(result, HealthResponse)

        # Verify the data structure
        assert result.status.host == "test.platform"
        assert result.status.server_id == "test-server-123"
        assert result.system.arch == "x64"
        assert result.server.version == "15.8.10-2023.2.44"
        assert len(result.applications) == 1
        assert len(result.adapters) == 1
        assert result.applications[0].id == "TestApp"
        assert result.adapters[0].id == "TestAdapter"

    @pytest.mark.asyncio
    async def test_get_health_empty_applications_and_adapters(self):
        """Test get_health with empty applications and adapters lists."""
        # Set up mock data with empty lists
        mock_data = self.create_mock_health_data()
        mock_data["applications_data"] = {"results": []}
        mock_data["adapters_data"] = {"results": []}

        # Configure service method returns
        self.mock_health_service.get_status_health.return_value = mock_data[
            "status_data"
        ]
        self.mock_health_service.get_system_health.return_value = mock_data[
            "system_data"
        ]
        self.mock_health_service.get_server_health.return_value = mock_data[
            "server_data"
        ]
        self.mock_health_service.get_applications_health.return_value = mock_data[
            "applications_data"
        ]
        self.mock_health_service.get_adapters_health.return_value = mock_data[
            "adapters_data"
        ]

        # Call the function
        result = await get_health(self.mock_context)

        # Verify result
        assert isinstance(result, HealthResponse)
        assert len(result.applications) == 0
        assert len(result.adapters) == 0
        assert result.status.host == "test.platform"

    @pytest.mark.asyncio
    async def test_get_health_multiple_applications_and_adapters(self):
        """Test get_health with multiple applications and adapters."""
        # Set up mock data with multiple items
        mock_data = self.create_mock_health_data()

        # Add second application
        second_app = {
            "id": "TestApp2",
            "package_id": "@itential/test-app2",
            "version": "2.0.0",
            "type": "Application",
            "description": "Second test application",
            "routePrefix": "test-app2",
            "state": "STOPPED",
            "connection": None,
            "uptime": 500.0,
            "memoryUsage": {
                "rss": 80000000,
                "heapTotal": 40000000,
                "heapUsed": 30000000,
                "external": 4000000,
                "arrayBuffers": 3000000,
            },
            "cpuUsage": {"user": 800000, "system": 400000},
            "pid": 124,
            "logger": {"console": "debug", "file": "debug", "syslog": "info"},
            "timestamp": 1757004595716,
            "prevUptime": 499.0,
        }
        mock_data["applications_data"]["results"].append(second_app)

        # Add second adapter
        second_adapter = {
            "id": "TestAdapter2",
            "package_id": "@itential/test-adapter2",
            "version": "2.0.0",
            "type": "Adapter",
            "description": "Second test adapter",
            "routePrefix": "test-adapter2",
            "state": "RUNNING",
            "connection": {"state": "OFFLINE"},
            "uptime": 1500.0,
            "memoryUsage": {
                "rss": 120000000,
                "heapTotal": 60000000,
                "heapUsed": 50000000,
                "external": 6000000,
                "arrayBuffers": 5000000,
            },
            "cpuUsage": {"user": 1500000, "system": 750000},
            "pid": 457,
            "logger": {"console": "debug", "file": "debug", "syslog": "info"},
            "timestamp": 1757004595716,
            "prevUptime": 1499.0,
        }
        mock_data["adapters_data"]["results"].append(second_adapter)

        # Configure service method returns
        self.mock_health_service.get_status_health.return_value = mock_data[
            "status_data"
        ]
        self.mock_health_service.get_system_health.return_value = mock_data[
            "system_data"
        ]
        self.mock_health_service.get_server_health.return_value = mock_data[
            "server_data"
        ]
        self.mock_health_service.get_applications_health.return_value = mock_data[
            "applications_data"
        ]
        self.mock_health_service.get_adapters_health.return_value = mock_data[
            "adapters_data"
        ]

        # Call the function
        result = await get_health(self.mock_context)

        # Verify result
        assert isinstance(result, HealthResponse)
        assert len(result.applications) == 2
        assert len(result.adapters) == 2

        # Verify first items
        assert result.applications[0].id == "TestApp"
        assert result.adapters[0].id == "TestAdapter"

        # Verify second items
        assert result.applications[1].id == "TestApp2"
        assert result.applications[1].state == "STOPPED"
        assert result.adapters[1].id == "TestAdapter2"
        assert result.adapters[1].connection.state == "OFFLINE"

    @pytest.mark.asyncio
    async def test_get_health_parallel_execution(self):
        """Test that get_health executes API calls in parallel."""
        # Set up mock data
        mock_data = self.create_mock_health_data()

        # Configure service method returns normally
        self.mock_health_service.get_status_health.return_value = mock_data[
            "status_data"
        ]
        self.mock_health_service.get_system_health.return_value = mock_data[
            "system_data"
        ]
        self.mock_health_service.get_server_health.return_value = mock_data[
            "server_data"
        ]
        self.mock_health_service.get_applications_health.return_value = mock_data[
            "applications_data"
        ]
        self.mock_health_service.get_adapters_health.return_value = mock_data[
            "adapters_data"
        ]

        # Call the function
        result = await get_health(self.mock_context)

        # Verify result
        assert isinstance(result, HealthResponse)

        # Verify all service methods were called exactly once
        # This verifies that asyncio.gather was used with all methods
        self.mock_health_service.get_status_health.assert_called_once()
        self.mock_health_service.get_system_health.assert_called_once()
        self.mock_health_service.get_server_health.assert_called_once()
        self.mock_health_service.get_applications_health.assert_called_once()
        self.mock_health_service.get_adapters_health.assert_called_once()

        # Verify data structure integrity (parallel execution preserved data)
        assert result.status.host == "test.platform"
        assert result.system.arch == "x64"
        assert result.server.version == "15.8.10-2023.2.44"

    @pytest.mark.asyncio
    async def test_get_health_handles_service_errors(self):
        """Test get_health handles service errors appropriately."""
        # Configure one service to raise an error
        self.mock_health_service.get_status_health.side_effect = Exception(
            "Status service error"
        )

        # Since asyncio.gather is called with return_exceptions=False, it should raise
        with pytest.raises(Exception, match="Status service error"):
            await get_health(self.mock_context)

        # Verify context info was called before error
        self.mock_context.info.assert_called_once_with("inside get_health(...)")

    @pytest.mark.asyncio
    async def test_get_health_context_setup(self):
        """Test get_health properly sets up context and client access."""
        # Set up mock data
        mock_data = self.create_mock_health_data()

        # Configure service method returns
        self.mock_health_service.get_status_health.return_value = mock_data[
            "status_data"
        ]
        self.mock_health_service.get_system_health.return_value = mock_data[
            "system_data"
        ]
        self.mock_health_service.get_server_health.return_value = mock_data[
            "server_data"
        ]
        self.mock_health_service.get_applications_health.return_value = mock_data[
            "applications_data"
        ]
        self.mock_health_service.get_adapters_health.return_value = mock_data[
            "adapters_data"
        ]

        # Call the function
        result = await get_health(self.mock_context)

        # Verify client access
        self.mock_context.request_context.lifespan_context.get.assert_called_once_with(
            "client"
        )

        # Verify result
        assert isinstance(result, HealthResponse)

    @pytest.mark.asyncio
    async def test_get_health_with_complex_system_data(self):
        """Test get_health with complex system information."""
        # Set up mock data with complex system info
        mock_data = self.create_mock_health_data()

        # Add multiple CPUs
        mock_data["system_data"]["cpus"] = [
            {
                "model": "Intel(R) Core(TM) i7-12700H CPU @ 2.30GHz",
                "speed": 4015,
                "times": {
                    "user": 52081020,
                    "nice": 26850,
                    "sys": 18688410,
                    "idle": 4564187990,
                    "irq": 7986130,
                },
            },
            {
                "model": "Intel(R) Core(TM) i7-12700H CPU @ 2.30GHz",
                "speed": 4015,
                "times": {
                    "user": 52081021,
                    "nice": 26851,
                    "sys": 18688411,
                    "idle": 4564187991,
                    "irq": 7986131,
                },
            },
        ]

        # Configure service method returns
        self.mock_health_service.get_status_health.return_value = mock_data[
            "status_data"
        ]
        self.mock_health_service.get_system_health.return_value = mock_data[
            "system_data"
        ]
        self.mock_health_service.get_server_health.return_value = mock_data[
            "server_data"
        ]
        self.mock_health_service.get_applications_health.return_value = mock_data[
            "applications_data"
        ]
        self.mock_health_service.get_adapters_health.return_value = mock_data[
            "adapters_data"
        ]

        # Call the function
        result = await get_health(self.mock_context)

        # Verify result
        assert isinstance(result, HealthResponse)
        assert len(result.system.cpus) == 2
        assert (
            result.system.cpus[0].model == "Intel(R) Core(TM) i7-12700H CPU @ 2.30GHz"
        )
        assert result.system.cpus[1].speed == 4015

    @pytest.mark.asyncio
    async def test_get_health_with_comprehensive_server_versions(self):
        """Test get_health with comprehensive server version information."""
        # Set up mock data with all server versions
        mock_data = self.create_mock_health_data()

        # Configure service method returns
        self.mock_health_service.get_status_health.return_value = mock_data[
            "status_data"
        ]
        self.mock_health_service.get_system_health.return_value = mock_data[
            "system_data"
        ]
        self.mock_health_service.get_server_health.return_value = mock_data[
            "server_data"
        ]
        self.mock_health_service.get_applications_health.return_value = mock_data[
            "applications_data"
        ]
        self.mock_health_service.get_adapters_health.return_value = mock_data[
            "adapters_data"
        ]

        # Call the function
        result = await get_health(self.mock_context)

        # Verify result
        assert isinstance(result, HealthResponse)

        # Check server versions are properly mapped
        server_versions = result.server.versions
        assert server_versions.node == "20.3.0"
        assert server_versions.acorn == "8.8.2"
        assert server_versions.openssl == "3.0.8+quic"
        assert server_versions.v8 == "11.3.244.8-node.9"

    @pytest.mark.asyncio
    async def test_get_health_data_structure_integrity(self):
        """Test that get_health maintains data structure integrity."""
        # Set up mock data
        mock_data = self.create_mock_health_data()

        # Configure service method returns
        self.mock_health_service.get_status_health.return_value = mock_data[
            "status_data"
        ]
        self.mock_health_service.get_system_health.return_value = mock_data[
            "system_data"
        ]
        self.mock_health_service.get_server_health.return_value = mock_data[
            "server_data"
        ]
        self.mock_health_service.get_applications_health.return_value = mock_data[
            "applications_data"
        ]
        self.mock_health_service.get_adapters_health.return_value = mock_data[
            "adapters_data"
        ]

        # Call the function
        result = await get_health(self.mock_context)

        # Verify the complete data structure
        assert isinstance(result, HealthResponse)

        # Verify status section
        assert result.status.host == "test.platform"
        assert result.status.server_id == "test-server-123"
        assert len(result.status.services) == 1
        assert result.status.services[0].service == "redis"

        # Verify system section
        assert result.system.arch == "x64"
        assert result.system.free_mem == 53953363968
        assert result.system.total_mem == 67111694336
        assert len(result.system.load_avg) == 3

        # Verify server section
        assert result.server.version == "15.8.10-2023.2.44"
        assert result.server.memory_usage.rss == 469671936
        assert result.server.cpu_usage.user == 3815108692

        # Verify applications section
        assert len(result.applications) == 1
        assert result.applications[0].route_prefix == "test-app"
        assert result.applications[0].memory_usage.heap_total == 50000000

        # Verify adapters section
        assert len(result.adapters) == 1
        assert result.adapters[0].route_prefix == "test-adapter"
        assert result.adapters[0].connection.state == "ONLINE"

    @pytest.mark.asyncio
    async def test_get_health_field_aliases_handling(self):
        """Test that get_health properly handles field aliases from API responses."""
        # Set up mock data
        mock_data = self.create_mock_health_data()

        # Configure service method returns
        self.mock_health_service.get_status_health.return_value = mock_data[
            "status_data"
        ]
        self.mock_health_service.get_system_health.return_value = mock_data[
            "system_data"
        ]
        self.mock_health_service.get_server_health.return_value = mock_data[
            "server_data"
        ]
        self.mock_health_service.get_applications_health.return_value = mock_data[
            "applications_data"
        ]
        self.mock_health_service.get_adapters_health.return_value = mock_data[
            "adapters_data"
        ]

        # Call the function
        result = await get_health(self.mock_context)

        # Verify that camelCase API fields are properly mapped to snake_case model fields

        # Status fields
        assert hasattr(result.status, "server_id")  # serverId -> server_id
        assert result.status.server_id == "test-server-123"

        # System fields
        assert hasattr(result.system, "free_mem")  # freemem -> free_mem
        assert hasattr(result.system, "total_mem")  # totalmem -> total_mem
        assert hasattr(result.system, "load_avg")  # loadavg -> load_avg
        assert result.system.free_mem == 53953363968

        # Server fields
        assert hasattr(
            result.server.memory_usage, "heap_total"
        )  # heapTotal -> heap_total
        assert hasattr(result.server.memory_usage, "heap_used")  # heapUsed -> heap_used
        assert hasattr(
            result.server.memory_usage, "array_buffers"
        )  # arrayBuffers -> array_buffers
        assert result.server.memory_usage.heap_total == 158703616

        # Application fields
        assert hasattr(
            result.applications[0], "route_prefix"
        )  # routePrefix -> route_prefix
        assert hasattr(
            result.applications[0], "prev_uptime"
        )  # prevUptime -> prev_uptime
        assert result.applications[0].route_prefix == "test-app"

        # Adapter fields
        assert hasattr(
            result.adapters[0], "route_prefix"
        )  # routePrefix -> route_prefix
        assert hasattr(result.adapters[0], "prev_uptime")  # prevUptime -> prev_uptime
        assert result.adapters[0].route_prefix == "test-adapter"

    def test_get_health_function_signature(self):
        """Test get_health function has correct signature."""
        import inspect
        from typing import get_type_hints

        # Check function signature
        sig = inspect.signature(get_health)
        params = list(sig.parameters.keys())
        assert params == ["ctx"]

        # Check parameter type
        param = sig.parameters["ctx"]
        assert param.annotation is not inspect.Parameter.empty

        # Check return type
        type_hints = get_type_hints(get_health)
        assert type_hints.get("return") == HealthResponse

    def test_get_health_docstring(self):
        """Test get_health function has proper docstring."""
        docstring = get_health.__doc__
        assert docstring is not None
        assert "comprehensive health information" in docstring.lower()
        assert "parallel" in docstring.lower()
        assert "Args:" in docstring
        assert "Returns:" in docstring
        assert "HealthResponse" in docstring
        assert "Raises:" in docstring

    def test_get_health_module_tags(self):
        """Test health tool module has correct tags."""
        from itential_mcp.tools import health

        assert hasattr(health, "__tags__")
        assert health.__tags__ == ("health",)

    @pytest.mark.asyncio
    async def test_get_health_minimal_data(self):
        """Test get_health with minimal valid data."""
        # Create minimal mock data
        minimal_data = {
            "status_data": {
                "host": "minimal.host",
                "serverId": "minimal-123",
                "services": [],
                "timestamp": 0,
                "apps": "unknown",
                "adapters": "unknown",
            },
            "system_data": {
                "arch": "x64",
                "release": "Unknown",
                "uptime": 0.0,
                "freemem": 0,
                "totalmem": 1000000,
                "loadavg": [0.0, 0.0, 0.0],
                "cpus": [],
            },
            "server_data": {
                "version": "0.0.0",
                "release": "0.0.0",
                "arch": "x64",
                "platform": "unknown",
                "versions": {
                    "node": "0.0.0",
                    "acorn": "0.0.0",
                    "ada": "0.0.0",
                    "ares": "0.0.0",
                    "base64": "0.0.0",
                    "brotli": "0.0.0",
                    "cjs_module_lexer": "0.0.0",
                    "cldr": "0.0",
                    "icu": "0.0",
                    "llhttp": "0.0.0",
                    "modules": "0",
                    "napi": "0",
                    "nghttp2": "0.0.0",
                    "nghttp3": "0.0.0",
                    "ngtcp2": "0.0.0",
                    "openssl": "0.0.0",
                    "simdutf": "0.0.0",
                    "tz": "0000a",
                    "undici": "0.0.0",
                    "unicode": "0.0",
                    "uv": "0.0.0",
                    "uvwasi": "0.0.0",
                    "v8": "0.0.0",
                    "zlib": "0.0.0",
                },
                "memoryUsage": {
                    "rss": 0,
                    "heapTotal": 0,
                    "heapUsed": 0,
                    "external": 0,
                    "arrayBuffers": 0,
                },
                "cpuUsage": {"user": 0, "system": 0},
                "uptime": 0.0,
                "pid": 1,
                "dependencies": {},
            },
            "applications_data": {"results": []},
            "adapters_data": {"results": []},
        }

        # Configure service method returns
        self.mock_health_service.get_status_health.return_value = minimal_data[
            "status_data"
        ]
        self.mock_health_service.get_system_health.return_value = minimal_data[
            "system_data"
        ]
        self.mock_health_service.get_server_health.return_value = minimal_data[
            "server_data"
        ]
        self.mock_health_service.get_applications_health.return_value = minimal_data[
            "applications_data"
        ]
        self.mock_health_service.get_adapters_health.return_value = minimal_data[
            "adapters_data"
        ]

        # Call the function
        result = await get_health(self.mock_context)

        # Verify result
        assert isinstance(result, HealthResponse)
        assert result.status.host == "minimal.host"
        assert result.system.arch == "x64"
        assert result.server.version == "0.0.0"
        assert len(result.applications) == 0
        assert len(result.adapters) == 0
