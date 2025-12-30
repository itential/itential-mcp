# Copyright (c) 2025 Itential, Inc
# GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

import pytest
from unittest.mock import AsyncMock, MagicMock

from itential_mcp.platform.services.health import Service


class TestHealthService:
    """Test cases for the Health Service class."""

    def setup_method(self):
        """Set up test fixtures before each test method."""
        self.mock_client = AsyncMock()
        self.health_service = Service(self.mock_client)

    def test_service_name(self):
        """Test that the service has the correct name."""
        assert self.health_service.name == "health"

    def test_service_initialization(self):
        """Test service initialization with client."""
        assert self.health_service.client == self.mock_client

    @pytest.mark.asyncio
    async def test_get_status_health_success(self):
        """Test get_status_health returns status data successfully."""
        expected_data = {
            "results": {
                "host": "test.platform",
                "serverId": "test-server-123",
                "services": [{"service": "redis", "status": "running"}],
                "timestamp": 1757004595716,
                "apps": "running",
                "adapters": "running",
            }
        }

        mock_response = MagicMock()
        mock_response.json.return_value = expected_data
        self.mock_client.get.return_value = mock_response

        result = await self.health_service.get_status_health()

        self.mock_client.get.assert_called_once_with("/health/status")
        assert result == expected_data

    @pytest.mark.asyncio
    async def test_get_system_health_success(self):
        """Test get_system_health returns system data successfully."""
        expected_data = {
            "results": {
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
            }
        }

        mock_response = MagicMock()
        mock_response.json.return_value = expected_data
        self.mock_client.get.return_value = mock_response

        result = await self.health_service.get_system_health()

        self.mock_client.get.assert_called_once_with("/health/system")
        assert result == expected_data

    @pytest.mark.asyncio
    async def test_get_server_health_success(self):
        """Test get_server_health returns server data successfully."""
        expected_data = {
            "results": {
                "version": "15.8.10-2023.2.44",
                "release": "2023.2.9",
                "arch": "x64",
                "platform": "linux",
                "versions": {
                    "node": "20.3.0",
                    "acorn": "8.8.2",
                    "ada": "2.5.0",
                    "v8": "11.3.244.8-node.9",
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
            }
        }

        mock_response = MagicMock()
        mock_response.json.return_value = expected_data
        self.mock_client.get.return_value = mock_response

        result = await self.health_service.get_server_health()

        self.mock_client.get.assert_called_once_with("/health/server")
        assert result == expected_data

    @pytest.mark.asyncio
    async def test_get_applications_health_success(self):
        """Test get_applications_health returns applications data successfully."""
        expected_data = {
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
                    "logger": {"console": "info", "file": "info", "syslog": "warning"},
                    "timestamp": 1757004595716,
                    "prevUptime": 999.0,
                }
            ]
        }

        mock_response = MagicMock()
        mock_response.json.return_value = expected_data
        self.mock_client.get.return_value = mock_response

        result = await self.health_service.get_applications_health()

        self.mock_client.get.assert_called_once_with("/health/applications")
        assert result == expected_data

    @pytest.mark.asyncio
    async def test_get_adapters_health_success(self):
        """Test get_adapters_health returns adapters data successfully."""
        expected_data = {
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
                    "logger": {"console": "info", "file": "info", "syslog": "warning"},
                    "timestamp": 1757004595716,
                    "prevUptime": 1999.0,
                }
            ]
        }

        mock_response = MagicMock()
        mock_response.json.return_value = expected_data
        self.mock_client.get.return_value = mock_response

        result = await self.health_service.get_adapters_health()

        self.mock_client.get.assert_called_once_with("/health/adapters")
        assert result == expected_data

    @pytest.mark.asyncio
    async def test_get_status_health_with_empty_services(self):
        """Test get_status_health with empty services list."""
        expected_data = {
            "results": {
                "host": "test.platform",
                "serverId": "test-server-123",
                "services": [],
                "timestamp": 1757004595716,
                "apps": "running",
                "adapters": "running",
            }
        }

        mock_response = MagicMock()
        mock_response.json.return_value = expected_data
        self.mock_client.get.return_value = mock_response

        result = await self.health_service.get_status_health()

        self.mock_client.get.assert_called_once_with("/health/status")
        assert result == expected_data
        assert result["results"]["services"] == []

    @pytest.mark.asyncio
    async def test_get_system_health_multiple_cpus(self):
        """Test get_system_health with multiple CPU cores."""
        expected_data = {
            "results": {
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
                ],
            }
        }

        mock_response = MagicMock()
        mock_response.json.return_value = expected_data
        self.mock_client.get.return_value = mock_response

        result = await self.health_service.get_system_health()

        self.mock_client.get.assert_called_once_with("/health/system")
        assert result == expected_data
        assert len(result["results"]["cpus"]) == 2

    @pytest.mark.asyncio
    async def test_get_applications_health_empty_list(self):
        """Test get_applications_health with empty applications list."""
        expected_data = {"results": []}

        mock_response = MagicMock()
        mock_response.json.return_value = expected_data
        self.mock_client.get.return_value = mock_response

        result = await self.health_service.get_applications_health()

        self.mock_client.get.assert_called_once_with("/health/applications")
        assert result == expected_data
        assert result["results"] == []

    @pytest.mark.asyncio
    async def test_get_adapters_health_empty_list(self):
        """Test get_adapters_health with empty adapters list."""
        expected_data = {"results": []}

        mock_response = MagicMock()
        mock_response.json.return_value = expected_data
        self.mock_client.get.return_value = mock_response

        result = await self.health_service.get_adapters_health()

        self.mock_client.get.assert_called_once_with("/health/adapters")
        assert result == expected_data
        assert result["results"] == []

    @pytest.mark.asyncio
    async def test_get_applications_health_multiple_apps(self):
        """Test get_applications_health with multiple applications."""
        expected_data = {
            "results": [
                {
                    "id": "App1",
                    "package_id": "@itential/app1",
                    "version": "1.0.0",
                    "type": "Application",
                    "description": "First application",
                    "routePrefix": "app1",
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
                    "logger": {"console": "info", "file": "info", "syslog": "warning"},
                    "timestamp": 1757004595716,
                    "prevUptime": 999.0,
                },
                {
                    "id": "App2",
                    "package_id": "@itential/app2",
                    "version": "2.0.0",
                    "type": "Application",
                    "description": "Second application",
                    "routePrefix": "app2",
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
                },
            ]
        }

        mock_response = MagicMock()
        mock_response.json.return_value = expected_data
        self.mock_client.get.return_value = mock_response

        result = await self.health_service.get_applications_health()

        self.mock_client.get.assert_called_once_with("/health/applications")
        assert result == expected_data
        assert len(result["results"]) == 2
        assert result["results"][0]["state"] == "RUNNING"
        assert result["results"][1]["state"] == "STOPPED"

    @pytest.mark.asyncio
    async def test_get_adapters_health_multiple_adapters(self):
        """Test get_adapters_health with multiple adapters."""
        expected_data = {
            "results": [
                {
                    "id": "Adapter1",
                    "package_id": "@itential/adapter1",
                    "version": "1.0.0",
                    "type": "Adapter",
                    "description": "First adapter",
                    "routePrefix": "adapter1",
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
                    "logger": {"console": "info", "file": "info", "syslog": "warning"},
                    "timestamp": 1757004595716,
                    "prevUptime": 1999.0,
                },
                {
                    "id": "Adapter2",
                    "package_id": "@itential/adapter2",
                    "version": "2.0.0",
                    "type": "Adapter",
                    "description": "Second adapter",
                    "routePrefix": "adapter2",
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
                },
            ]
        }

        mock_response = MagicMock()
        mock_response.json.return_value = expected_data
        self.mock_client.get.return_value = mock_response

        result = await self.health_service.get_adapters_health()

        self.mock_client.get.assert_called_once_with("/health/adapters")
        assert result == expected_data
        assert len(result["results"]) == 2
        assert result["results"][0]["connection"]["state"] == "ONLINE"
        assert result["results"][1]["connection"]["state"] == "OFFLINE"

    @pytest.mark.asyncio
    async def test_get_server_health_minimal_dependencies(self):
        """Test get_server_health with minimal dependencies."""
        expected_data = {
            "results": {
                "version": "15.8.10-2023.2.44",
                "release": "2023.2.9",
                "arch": "x64",
                "platform": "linux",
                "versions": {
                    "node": "20.3.0",
                    "acorn": "8.8.2",
                    "ada": "2.5.0",
                    "v8": "11.3.244.8-node.9",
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
                "dependencies": {},
            }
        }

        mock_response = MagicMock()
        mock_response.json.return_value = expected_data
        self.mock_client.get.return_value = mock_response

        result = await self.health_service.get_server_health()

        self.mock_client.get.assert_called_once_with("/health/server")
        assert result == expected_data
        assert result["results"]["dependencies"] == {}

    @pytest.mark.asyncio
    async def test_get_status_health_error_handling(self):
        """Test get_status_health handles client errors appropriately."""
        self.mock_client.get.side_effect = Exception("Network error")

        with pytest.raises(Exception, match="Network error"):
            await self.health_service.get_status_health()

        self.mock_client.get.assert_called_once_with("/health/status")

    @pytest.mark.asyncio
    async def test_get_system_health_error_handling(self):
        """Test get_system_health handles client errors appropriately."""
        self.mock_client.get.side_effect = Exception("Network error")

        with pytest.raises(Exception, match="Network error"):
            await self.health_service.get_system_health()

        self.mock_client.get.assert_called_once_with("/health/system")

    @pytest.mark.asyncio
    async def test_get_server_health_error_handling(self):
        """Test get_server_health handles client errors appropriately."""
        self.mock_client.get.side_effect = Exception("Network error")

        with pytest.raises(Exception, match="Network error"):
            await self.health_service.get_server_health()

        self.mock_client.get.assert_called_once_with("/health/server")

    @pytest.mark.asyncio
    async def test_get_applications_health_error_handling(self):
        """Test get_applications_health handles client errors appropriately."""
        self.mock_client.get.side_effect = Exception("Network error")

        with pytest.raises(Exception, match="Network error"):
            await self.health_service.get_applications_health()

        self.mock_client.get.assert_called_once_with("/health/applications")

    @pytest.mark.asyncio
    async def test_get_adapters_health_error_handling(self):
        """Test get_adapters_health handles client errors appropriately."""
        self.mock_client.get.side_effect = Exception("Network error")

        with pytest.raises(Exception, match="Network error"):
            await self.health_service.get_adapters_health()

        self.mock_client.get.assert_called_once_with("/health/adapters")

    @pytest.mark.asyncio
    async def test_all_methods_return_json_data(self):
        """Test that all service methods return JSON data from response."""
        test_data = {"results": {"test": "data"}}

        mock_response = MagicMock()
        mock_response.json.return_value = test_data
        self.mock_client.get.return_value = mock_response

        # Test each method
        methods_and_endpoints = [
            (self.health_service.get_status_health, "/health/status"),
            (self.health_service.get_system_health, "/health/system"),
            (self.health_service.get_server_health, "/health/server"),
            (self.health_service.get_applications_health, "/health/applications"),
            (self.health_service.get_adapters_health, "/health/adapters"),
        ]

        for method, endpoint in methods_and_endpoints:
            # Reset mock
            self.mock_client.reset_mock()
            mock_response.reset_mock()

            result = await method()

            self.mock_client.get.assert_called_once_with(endpoint)
            mock_response.json.assert_called_once()
            assert result == test_data

    @pytest.mark.asyncio
    async def test_service_inherits_from_service_base(self):
        """Test that Service class correctly inherits from ServiceBase."""
        from itential_mcp.platform.services import ServiceBase

        assert isinstance(self.health_service, ServiceBase)
        assert hasattr(self.health_service, "client")
        assert self.health_service.client == self.mock_client

    def test_service_class_attributes(self):
        """Test Service class has correct attributes."""
        assert hasattr(Service, "name")
        assert Service.name == "health"

    @pytest.mark.asyncio
    async def test_complex_status_data(self):
        """Test get_status_health with complex service status data."""
        expected_data = {
            "results": {
                "host": "production.itential.com",
                "serverId": "prod-server-abc123",
                "serverName": "Production Server",
                "services": [
                    {"service": "redis", "status": "running"},
                    {"service": "mongo", "status": "running"},
                    {"service": "rabbitmq", "status": "degraded"},
                    {"service": "elasticsearch", "status": "stopped"},
                ],
                "timestamp": 1757004595716,
                "apps": "degraded",
                "adapters": "running",
            }
        }

        mock_response = MagicMock()
        mock_response.json.return_value = expected_data
        self.mock_client.get.return_value = mock_response

        result = await self.health_service.get_status_health()

        self.mock_client.get.assert_called_once_with("/health/status")
        assert result == expected_data
        assert len(result["results"]["services"]) == 4
        assert result["results"]["apps"] == "degraded"

    @pytest.mark.asyncio
    async def test_system_health_edge_case_values(self):
        """Test get_system_health with edge case values."""
        expected_data = {
            "results": {
                "arch": "arm64",
                "release": "Ubuntu 22.04.3 LTS",
                "uptime": 0.0,  # Just started
                "freemem": 0,  # No free memory
                "totalmem": 8589934592,  # 8GB
                "loadavg": [0.0, 0.0, 0.0],  # No load
                "cpus": [],  # No CPU info available
            }
        }

        mock_response = MagicMock()
        mock_response.json.return_value = expected_data
        self.mock_client.get.return_value = mock_response

        result = await self.health_service.get_system_health()

        self.mock_client.get.assert_called_once_with("/health/system")
        assert result == expected_data
        assert result["results"]["freemem"] == 0
        assert result["results"]["cpus"] == []

    @pytest.mark.asyncio
    async def test_server_health_comprehensive_versions(self):
        """Test get_server_health with comprehensive version information."""
        expected_data = {
            "results": {
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
                "dependencies": {
                    "@itential/service": "3.1.12",
                    "@itential/automation-gateway": "4.2.1",
                    "@itential/app-workflow-manager": "2.5.3",
                },
            }
        }

        mock_response = MagicMock()
        mock_response.json.return_value = expected_data
        self.mock_client.get.return_value = mock_response

        result = await self.health_service.get_server_health()

        self.mock_client.get.assert_called_once_with("/health/server")
        assert result == expected_data
        assert len(result["results"]["versions"]) == 24
        assert len(result["results"]["dependencies"]) == 3
