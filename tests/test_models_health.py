# Copyright (c) 2025 Itential, Inc
# GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later


from itential_mcp.models.health import (
    ServiceStatus,
    PlatformStatus,
    CpuTimes,
    CpuInfo,
    SystemInfo,
    MemoryUsage,
    CpuUsage,
    ServerVersions,
    ServerInfo,
    ConnectionInfo,
    LoggerConfig,
    ApplicationInfo,
    AdapterInfo,
    HealthResponse,
)


class TestServiceStatus:
    """Test cases for ServiceStatus model."""

    def test_service_status_creation(self):
        """Test creating a ServiceStatus with valid data."""
        service_status = ServiceStatus(service="redis", status="running")

        assert service_status.service == "redis"
        assert service_status.status == "running"

    def test_service_status_serialization(self):
        """Test ServiceStatus model serialization."""
        service_status = ServiceStatus(service="mongo", status="stopped")

        data = service_status.model_dump()
        expected = {"service": "mongo", "status": "stopped"}
        assert data == expected

    def test_service_status_from_dict(self):
        """Test creating ServiceStatus from dictionary."""
        data = {"service": "redis", "status": "running"}
        service_status = ServiceStatus(**data)

        assert service_status.service == "redis"
        assert service_status.status == "running"


class TestPlatformStatus:
    """Test cases for PlatformStatus model."""

    def test_platform_status_creation(self):
        """Test creating a PlatformStatus with valid data."""
        service_status = ServiceStatus(service="redis", status="running")
        platform_status = PlatformStatus(
            host="test.host",
            serverId="test-server-123",
            services=[service_status],
            timestamp=1757004595716,
            apps="running",
            adapters="running",
        )

        assert platform_status.host == "test.host"
        assert platform_status.server_id == "test-server-123"
        assert platform_status.server_name is None
        assert len(platform_status.services) == 1
        assert platform_status.timestamp == 1757004595716
        assert platform_status.apps == "running"
        assert platform_status.adapters == "running"

    def test_platform_status_with_alias(self):
        """Test PlatformStatus creation using API field names (camelCase)."""
        data = {
            "host": "test.host",
            "serverId": "test-server-123",
            "serverName": "Test Server",
            "services": [{"service": "redis", "status": "running"}],
            "timestamp": 1757004595716,
            "apps": "running",
            "adapters": "running",
        }

        platform_status = PlatformStatus(**data)
        assert platform_status.server_id == "test-server-123"
        assert platform_status.server_name == "Test Server"

    def test_platform_status_serialization_with_aliases(self):
        """Test PlatformStatus serialization with aliases (camelCase)."""
        service_status = ServiceStatus(service="redis", status="running")
        platform_status = PlatformStatus(
            host="test.host",
            serverId="test-server-123",
            serverName="Test Server",
            services=[service_status],
            timestamp=1757004595716,
            apps="running",
            adapters="running",
        )

        data = platform_status.model_dump(by_alias=True)
        assert "serverId" in data
        assert "serverName" in data
        assert data["serverId"] == "test-server-123"
        assert data["serverName"] == "Test Server"

    def test_platform_status_empty_services(self):
        """Test PlatformStatus with empty services list."""
        platform_status = PlatformStatus(
            host="test.host",
            serverId="test-server-123",
            timestamp=1757004595716,
            apps="running",
            adapters="running",
        )

        assert platform_status.services == []

    def test_platform_status_optional_server_name(self):
        """Test PlatformStatus with optional server_name field."""
        platform_status = PlatformStatus(
            host="test.host",
            serverId="test-server-123",
            timestamp=1757004595716,
            apps="running",
            adapters="running",
        )

        assert platform_status.server_name is None


class TestCpuTimes:
    """Test cases for CpuTimes model."""

    def test_cpu_times_creation(self):
        """Test creating CpuTimes with valid data."""
        cpu_times = CpuTimes(
            user=52081020, nice=26850, sys=18688410, idle=4564187990, irq=7986130
        )

        assert cpu_times.user == 52081020
        assert cpu_times.nice == 26850
        assert cpu_times.sys == 18688410
        assert cpu_times.idle == 4564187990
        assert cpu_times.irq == 7986130

    def test_cpu_times_serialization(self):
        """Test CpuTimes model serialization."""
        cpu_times = CpuTimes(user=100, nice=50, sys=75, idle=1000, irq=25)

        data = cpu_times.model_dump()
        expected = {"user": 100, "nice": 50, "sys": 75, "idle": 1000, "irq": 25}
        assert data == expected


class TestCpuInfo:
    """Test cases for CpuInfo model."""

    def test_cpu_info_creation(self):
        """Test creating CpuInfo with valid data."""
        cpu_times = CpuTimes(
            user=52081020, nice=26850, sys=18688410, idle=4564187990, irq=7986130
        )

        cpu_info = CpuInfo(
            model="Intel(R) Core(TM) i7-12700H CPU @ 2.30GHz",
            speed=4015,
            times=cpu_times,
        )

        assert cpu_info.model == "Intel(R) Core(TM) i7-12700H CPU @ 2.30GHz"
        assert cpu_info.speed == 4015
        assert cpu_info.times.user == 52081020

    def test_cpu_info_nested_serialization(self):
        """Test CpuInfo serialization with nested CpuTimes."""
        cpu_times = CpuTimes(user=100, nice=50, sys=75, idle=1000, irq=25)

        cpu_info = CpuInfo(model="Test CPU", speed=3000, times=cpu_times)

        data = cpu_info.model_dump()
        assert data["model"] == "Test CPU"
        assert data["speed"] == 3000
        assert "times" in data
        assert data["times"]["user"] == 100


class TestSystemInfo:
    """Test cases for SystemInfo model."""

    def test_system_info_creation(self):
        """Test creating SystemInfo with valid data."""
        cpu_times = CpuTimes(user=100, nice=50, sys=75, idle=1000, irq=25)
        cpu_info = CpuInfo(model="Test CPU", speed=3000, times=cpu_times)

        system_info = SystemInfo(
            arch="x64",
            release="6.13.12-100.fc40.x86_64",
            uptime=4668812.41,
            freemem=53953363968,
            totalmem=67111694336,
            loadavg=[0.15, 0.22, 0.25],
            cpus=[cpu_info],
        )

        assert system_info.arch == "x64"
        assert system_info.release == "6.13.12-100.fc40.x86_64"
        assert system_info.uptime == 4668812.41
        assert system_info.free_mem == 53953363968
        assert system_info.total_mem == 67111694336
        assert system_info.load_avg == [0.15, 0.22, 0.25]
        assert len(system_info.cpus) == 1

    def test_system_info_with_aliases(self):
        """Test SystemInfo creation using API field names (camelCase)."""
        data = {
            "arch": "x64",
            "release": "6.13.12-100.fc40.x86_64",
            "uptime": 4668812.41,
            "freemem": 53953363968,
            "totalmem": 67111694336,
            "loadavg": [0.15, 0.22, 0.25],
            "cpus": [
                {
                    "model": "Test CPU",
                    "speed": 3000,
                    "times": {
                        "user": 100,
                        "nice": 50,
                        "sys": 75,
                        "idle": 1000,
                        "irq": 25,
                    },
                }
            ],
        }

        system_info = SystemInfo(**data)
        assert system_info.free_mem == 53953363968
        assert system_info.total_mem == 67111694336
        assert system_info.load_avg == [0.15, 0.22, 0.25]

    def test_system_info_serialization_with_aliases(self):
        """Test SystemInfo serialization with aliases (camelCase)."""
        cpu_times = CpuTimes(user=100, nice=50, sys=75, idle=1000, irq=25)
        cpu_info = CpuInfo(model="Test CPU", speed=3000, times=cpu_times)

        system_info = SystemInfo(
            arch="x64",
            release="6.13.12-100.fc40.x86_64",
            uptime=4668812.41,
            freemem=53953363968,
            totalmem=67111694336,
            loadavg=[0.15, 0.22, 0.25],
            cpus=[cpu_info],
        )

        data = system_info.model_dump(by_alias=True)
        assert "freemem" in data
        assert "totalmem" in data
        assert "loadavg" in data
        assert data["freemem"] == 53953363968

    def test_system_info_empty_cpus(self):
        """Test SystemInfo with empty CPU list."""
        system_info = SystemInfo(
            arch="x64",
            release="6.13.12-100.fc40.x86_64",
            uptime=4668812.41,
            freemem=53953363968,
            totalmem=67111694336,
            loadavg=[0.15, 0.22, 0.25],
        )

        assert system_info.cpus == []


class TestMemoryUsage:
    """Test cases for MemoryUsage model."""

    def test_memory_usage_creation(self):
        """Test creating MemoryUsage with valid data."""
        memory_usage = MemoryUsage(
            rss=469671936,
            heapTotal=158703616,
            heapUsed=147501584,
            external=50291978,
            arrayBuffers=46521129,
        )

        assert memory_usage.rss == 469671936
        assert memory_usage.heap_total == 158703616
        assert memory_usage.heap_used == 147501584
        assert memory_usage.external == 50291978
        assert memory_usage.array_buffers == 46521129

    def test_memory_usage_with_aliases(self):
        """Test MemoryUsage creation using API field names (camelCase)."""
        data = {
            "rss": 469671936,
            "heapTotal": 158703616,
            "heapUsed": 147501584,
            "external": 50291978,
            "arrayBuffers": 46521129,
        }

        memory_usage = MemoryUsage(**data)
        assert memory_usage.heap_total == 158703616
        assert memory_usage.heap_used == 147501584
        assert memory_usage.array_buffers == 46521129

    def test_memory_usage_serialization_with_aliases(self):
        """Test MemoryUsage serialization with aliases (camelCase)."""
        memory_usage = MemoryUsage(
            rss=469671936,
            heapTotal=158703616,
            heapUsed=147501584,
            external=50291978,
            arrayBuffers=46521129,
        )

        data = memory_usage.model_dump(by_alias=True)
        assert "heapTotal" in data
        assert "heapUsed" in data
        assert "arrayBuffers" in data
        assert data["heapTotal"] == 158703616


class TestCpuUsage:
    """Test cases for CpuUsage model."""

    def test_cpu_usage_creation(self):
        """Test creating CpuUsage with valid data."""
        cpu_usage = CpuUsage(user=3815108692, system=621631048)

        assert cpu_usage.user == 3815108692
        assert cpu_usage.system == 621631048

    def test_cpu_usage_serialization(self):
        """Test CpuUsage model serialization."""
        cpu_usage = CpuUsage(user=1000000, system=500000)

        data = cpu_usage.model_dump()
        expected = {"user": 1000000, "system": 500000}
        assert data == expected


class TestServerVersions:
    """Test cases for ServerVersions model."""

    def test_server_versions_creation(self):
        """Test creating ServerVersions with valid data."""
        versions = ServerVersions(
            node="20.3.0",
            acorn="8.8.2",
            ada="2.5.0",
            ares="1.19.1",
            base64="0.5.0",
            brotli="1.0.9",
            cjs_module_lexer="1.2.2",
            cldr="43.0",
            icu="73.1",
            llhttp="8.1.0",
            modules="115",
            napi="9",
            nghttp2="1.53.0",
            nghttp3="0.7.0",
            ngtcp2="0.8.1",
            openssl="3.0.8+quic",
            simdutf="3.2.12",
            tz="2023c",
            undici="5.22.1",
            unicode="15.0",
            uv="1.45.0",
            uvwasi="0.0.18",
            v8="11.3.244.8-node.9",
            zlib="1.2.13.1-motley",
        )

        assert versions.node == "20.3.0"
        assert versions.acorn == "8.8.2"
        assert versions.openssl == "3.0.8+quic"
        assert versions.v8 == "11.3.244.8-node.9"

    def test_server_versions_serialization(self):
        """Test ServerVersions model serialization."""
        versions = ServerVersions(
            node="18.0.0",
            acorn="8.8.0",
            ada="1.0.0",
            ares="1.19.0",
            base64="0.5.0",
            brotli="1.0.0",
            cjs_module_lexer="1.2.0",
            cldr="43.0",
            icu="73.0",
            llhttp="8.1.0",
            modules="108",
            napi="8",
            nghttp2="1.53.0",
            nghttp3="0.7.0",
            ngtcp2="0.8.0",
            openssl="3.0.0",
            simdutf="3.2.0",
            tz="2023a",
            undici="5.22.0",
            unicode="15.0",
            uv="1.44.0",
            uvwasi="0.0.18",
            v8="10.2.154",
            zlib="1.2.13",
        )

        data = versions.model_dump()
        assert data["node"] == "18.0.0"
        assert data["openssl"] == "3.0.0"
        assert "cjs_module_lexer" in data


class TestServerInfo:
    """Test cases for ServerInfo model."""

    def test_server_info_creation(self):
        """Test creating ServerInfo with valid data."""
        memory_usage = MemoryUsage(
            rss=469671936,
            heapTotal=158703616,
            heapUsed=147501584,
            external=50291978,
            arrayBuffers=46521129,
        )

        cpu_usage = CpuUsage(user=3815108692, system=621631048)

        versions = ServerVersions(
            node="20.3.0",
            acorn="8.8.2",
            ada="2.5.0",
            ares="1.19.1",
            base64="0.5.0",
            brotli="1.0.9",
            cjs_module_lexer="1.2.2",
            cldr="43.0",
            icu="73.1",
            llhttp="8.1.0",
            modules="115",
            napi="9",
            nghttp2="1.53.0",
            nghttp3="0.7.0",
            ngtcp2="0.8.1",
            openssl="3.0.8+quic",
            simdutf="3.2.12",
            tz="2023c",
            undici="5.22.1",
            unicode="15.0",
            uv="1.45.0",
            uvwasi="0.0.18",
            v8="11.3.244.8-node.9",
            zlib="1.2.13.1-motley",
        )

        server_info = ServerInfo(
            version="15.8.10-2023.2.44",
            release="2023.2.9",
            arch="x64",
            platform="linux",
            versions=versions,
            memoryUsage=memory_usage,
            cpuUsage=cpu_usage,
            uptime=2083622.963931177,
            pid=1,
            dependencies={"@itential/service": "3.1.12"},
        )

        assert server_info.version == "15.8.10-2023.2.44"
        assert server_info.release == "2023.2.9"
        assert server_info.arch == "x64"
        assert server_info.platform == "linux"
        assert server_info.uptime == 2083622.963931177
        assert server_info.pid == 1
        assert server_info.dependencies["@itential/service"] == "3.1.12"

    def test_server_info_with_aliases(self):
        """Test ServerInfo creation using API field names (camelCase)."""
        data = {
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
        }

        server_info = ServerInfo(**data)
        assert server_info.memory_usage.heap_total == 158703616
        assert server_info.cpu_usage.user == 3815108692

    def test_server_info_empty_dependencies(self):
        """Test ServerInfo with empty dependencies."""
        memory_usage = MemoryUsage(
            rss=469671936,
            heapTotal=158703616,
            heapUsed=147501584,
            external=50291978,
            arrayBuffers=46521129,
        )

        cpu_usage = CpuUsage(user=3815108692, system=621631048)

        versions = ServerVersions(
            node="20.3.0",
            acorn="8.8.2",
            ada="2.5.0",
            ares="1.19.1",
            base64="0.5.0",
            brotli="1.0.9",
            cjs_module_lexer="1.2.2",
            cldr="43.0",
            icu="73.1",
            llhttp="8.1.0",
            modules="115",
            napi="9",
            nghttp2="1.53.0",
            nghttp3="0.7.0",
            ngtcp2="0.8.1",
            openssl="3.0.8+quic",
            simdutf="3.2.12",
            tz="2023c",
            undici="5.22.1",
            unicode="15.0",
            uv="1.45.0",
            uvwasi="0.0.18",
            v8="11.3.244.8-node.9",
            zlib="1.2.13.1-motley",
        )

        server_info = ServerInfo(
            version="15.8.10-2023.2.44",
            release="2023.2.9",
            arch="x64",
            platform="linux",
            versions=versions,
            memoryUsage=memory_usage,
            cpuUsage=cpu_usage,
            uptime=2083622.963931177,
            pid=1,
        )

        assert server_info.dependencies == {}


class TestConnectionInfo:
    """Test cases for ConnectionInfo model."""

    def test_connection_info_creation(self):
        """Test creating ConnectionInfo with valid data."""
        connection_info = ConnectionInfo(state="ONLINE")
        assert connection_info.state == "ONLINE"

    def test_connection_info_offline(self):
        """Test creating ConnectionInfo with offline state."""
        connection_info = ConnectionInfo(state="OFFLINE")
        assert connection_info.state == "OFFLINE"

    def test_connection_info_serialization(self):
        """Test ConnectionInfo model serialization."""
        connection_info = ConnectionInfo(state="ONLINE")
        data = connection_info.model_dump()
        assert data == {"state": "ONLINE"}


class TestLoggerConfig:
    """Test cases for LoggerConfig model."""

    def test_logger_config_creation(self):
        """Test creating LoggerConfig with valid data."""
        logger_config = LoggerConfig(console="info", file="debug", syslog="warning")

        assert logger_config.console == "info"
        assert logger_config.file == "debug"
        assert logger_config.syslog == "warning"

    def test_logger_config_serialization(self):
        """Test LoggerConfig model serialization."""
        logger_config = LoggerConfig(console="info", file="info", syslog="warning")

        data = logger_config.model_dump()
        expected = {"console": "info", "file": "info", "syslog": "warning"}
        assert data == expected


class TestApplicationInfo:
    """Test cases for ApplicationInfo model."""

    def test_application_info_creation(self):
        """Test creating ApplicationInfo with valid data."""
        memory_usage = MemoryUsage(
            rss=100000000,
            heapTotal=50000000,
            heapUsed=40000000,
            external=5000000,
            arrayBuffers=4000000,
        )

        cpu_usage = CpuUsage(user=1000000, system=500000)

        logger_config = LoggerConfig(console="info", file="info", syslog="warning")

        app_info = ApplicationInfo(
            id="TestApp",
            package_id="@itential/test-app",
            version="1.0.0",
            type="Application",
            description="Test application",
            routePrefix="test-app",
            state="RUNNING",
            uptime=1000.0,
            memoryUsage=memory_usage,
            cpuUsage=cpu_usage,
            pid=123,
            logger=logger_config,
            timestamp=1757004595716,
            prevUptime=999.0,
        )

        assert app_info.id == "TestApp"
        assert app_info.package_id == "@itential/test-app"
        assert app_info.version == "1.0.0"
        assert app_info.type == "Application"
        assert app_info.state == "RUNNING"
        assert app_info.connection is None
        assert app_info.route_prefix == "test-app"

    def test_application_info_with_aliases(self):
        """Test ApplicationInfo creation using API field names (actual API format)."""
        data = {
            "id": "TestApp",
            "package_id": "@itential/test-app",  # API uses package_id, not packageId
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

        app_info = ApplicationInfo(**data)
        assert app_info.route_prefix == "test-app"
        assert app_info.memory_usage.heap_total == 50000000
        assert app_info.prev_uptime == 999.0

    def test_application_info_stopped_state(self):
        """Test ApplicationInfo with STOPPED state."""
        memory_usage = MemoryUsage(
            rss=100000000,
            heapTotal=50000000,
            heapUsed=40000000,
            external=5000000,
            arrayBuffers=4000000,
        )

        cpu_usage = CpuUsage(user=1000000, system=500000)

        logger_config = LoggerConfig(console="info", file="info", syslog="warning")

        app_info = ApplicationInfo(
            id="TestApp",
            package_id="@itential/test-app",
            version="1.0.0",
            type="Application",
            description="Test application",
            routePrefix="test-app",
            state="STOPPED",
            uptime=1000.0,
            memoryUsage=memory_usage,
            cpuUsage=cpu_usage,
            pid=123,
            logger=logger_config,
            timestamp=1757004595716,
            prevUptime=999.0,
        )

        assert app_info.state == "STOPPED"


class TestAdapterInfo:
    """Test cases for AdapterInfo model."""

    def test_adapter_info_creation(self):
        """Test creating AdapterInfo with valid data."""
        memory_usage = MemoryUsage(
            rss=150000000,
            heapTotal=70000000,
            heapUsed=60000000,
            external=8000000,
            arrayBuffers=7000000,
        )

        cpu_usage = CpuUsage(user=2000000, system=1000000)

        connection_info = ConnectionInfo(state="ONLINE")

        logger_config = LoggerConfig(console="info", file="info", syslog="warning")

        adapter_info = AdapterInfo(
            id="TestAdapter",
            package_id="@itential/test-adapter",
            version="1.0.0",
            type="Adapter",
            description="Test adapter",
            routePrefix="test-adapter",
            state="RUNNING",
            connection=connection_info,
            uptime=2000.0,
            memoryUsage=memory_usage,
            cpuUsage=cpu_usage,
            pid=456,
            logger=logger_config,
            timestamp=1757004595716,
            prevUptime=1999.0,
        )

        assert adapter_info.id == "TestAdapter"
        assert adapter_info.package_id == "@itential/test-adapter"
        assert adapter_info.version == "1.0.0"
        assert adapter_info.type == "Adapter"
        assert adapter_info.state == "RUNNING"
        assert adapter_info.connection.state == "ONLINE"
        assert adapter_info.route_prefix == "test-adapter"

    def test_adapter_info_with_aliases(self):
        """Test AdapterInfo creation using API field names (actual API format)."""
        data = {
            "id": "TestAdapter",
            "package_id": "@itential/test-adapter",  # API uses package_id, not packageId
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

        adapter_info = AdapterInfo(**data)
        assert adapter_info.route_prefix == "test-adapter"
        assert adapter_info.memory_usage.heap_total == 70000000
        assert adapter_info.prev_uptime == 1999.0

    def test_adapter_info_offline_connection(self):
        """Test AdapterInfo with offline connection."""
        memory_usage = MemoryUsage(
            rss=150000000,
            heapTotal=70000000,
            heapUsed=60000000,
            external=8000000,
            arrayBuffers=7000000,
        )

        cpu_usage = CpuUsage(user=2000000, system=1000000)

        connection_info = ConnectionInfo(state="OFFLINE")

        logger_config = LoggerConfig(console="info", file="info", syslog="warning")

        adapter_info = AdapterInfo(
            id="TestAdapter",
            package_id="@itential/test-adapter",
            version="1.0.0",
            type="Adapter",
            description="Test adapter",
            routePrefix="test-adapter",
            state="RUNNING",
            connection=connection_info,
            uptime=2000.0,
            memoryUsage=memory_usage,
            cpuUsage=cpu_usage,
            pid=456,
            logger=logger_config,
            timestamp=1757004595716,
            prevUptime=1999.0,
        )

        assert adapter_info.connection.state == "OFFLINE"

    def test_adapter_info_serialization_with_aliases(self):
        """Test AdapterInfo serialization with aliases (API format)."""
        memory_usage = MemoryUsage(
            rss=150000000,
            heapTotal=70000000,
            heapUsed=60000000,
            external=8000000,
            arrayBuffers=7000000,
        )

        cpu_usage = CpuUsage(user=2000000, system=1000000)

        connection_info = ConnectionInfo(state="ONLINE")

        logger_config = LoggerConfig(console="info", file="info", syslog="warning")

        adapter_info = AdapterInfo(
            id="TestAdapter",
            package_id="@itential/test-adapter",
            version="1.0.0",
            type="Adapter",
            description="Test adapter",
            routePrefix="test-adapter",
            state="RUNNING",
            connection=connection_info,
            uptime=2000.0,
            memoryUsage=memory_usage,
            cpuUsage=cpu_usage,
            pid=456,
            logger=logger_config,
            timestamp=1757004595716,
            prevUptime=1999.0,
        )

        # Test serialization with aliases (should match API format)
        data = adapter_info.model_dump(by_alias=True)
        assert "package_id" in data  # API uses package_id, not packageId
        assert "routePrefix" in data
        assert "memoryUsage" in data
        assert "cpuUsage" in data
        assert "prevUptime" in data
        assert data["routePrefix"] == "test-adapter"
        assert data["memoryUsage"]["heapTotal"] == 70000000
        assert data["prevUptime"] == 1999.0

    def test_application_info_serialization_with_aliases(self):
        """Test ApplicationInfo serialization with aliases (API format)."""
        memory_usage = MemoryUsage(
            rss=100000000,
            heapTotal=50000000,
            heapUsed=40000000,
            external=5000000,
            arrayBuffers=4000000,
        )

        cpu_usage = CpuUsage(user=1000000, system=500000)

        logger_config = LoggerConfig(console="info", file="info", syslog="warning")

        app_info = ApplicationInfo(
            id="TestApp",
            package_id="@itential/test-app",
            version="1.0.0",
            type="Application",
            description="Test application",
            routePrefix="test-app",
            state="RUNNING",
            uptime=1000.0,
            memoryUsage=memory_usage,
            cpuUsage=cpu_usage,
            pid=123,
            logger=logger_config,
            timestamp=1757004595716,
            prevUptime=999.0,
        )

        # Test serialization with aliases (should match API format)
        data = app_info.model_dump(by_alias=True)
        assert "package_id" in data  # API uses package_id, not packageId
        assert "routePrefix" in data
        assert "memoryUsage" in data
        assert "cpuUsage" in data
        assert "prevUptime" in data
        assert data["routePrefix"] == "test-app"
        assert data["memoryUsage"]["heapTotal"] == 50000000
        assert data["prevUptime"] == 999.0


class TestHealthResponse:
    """Test cases for HealthResponse model."""

    def test_health_response_creation(self):
        """Test creating HealthResponse with valid data."""
        service_status = ServiceStatus(service="redis", status="running")

        platform_status = PlatformStatus(
            host="test.platform",
            serverId="test-server-123",
            services=[service_status],
            timestamp=1757004595716,
            apps="running",
            adapters="running",
        )

        cpu_times = CpuTimes(user=100, nice=50, sys=75, idle=1000, irq=25)
        cpu_info = CpuInfo(model="Test CPU", speed=3000, times=cpu_times)

        system_info = SystemInfo(
            arch="x64",
            release="6.13.12-100.fc40.x86_64",
            uptime=4668812.41,
            freemem=53953363968,
            totalmem=67111694336,
            loadavg=[0.15, 0.22, 0.25],
            cpus=[cpu_info],
        )

        memory_usage = MemoryUsage(
            rss=469671936,
            heapTotal=158703616,
            heapUsed=147501584,
            external=50291978,
            arrayBuffers=46521129,
        )

        cpu_usage = CpuUsage(user=3815108692, system=621631048)

        versions = ServerVersions(
            node="20.3.0",
            acorn="8.8.2",
            ada="2.5.0",
            ares="1.19.1",
            base64="0.5.0",
            brotli="1.0.9",
            cjs_module_lexer="1.2.2",
            cldr="43.0",
            icu="73.1",
            llhttp="8.1.0",
            modules="115",
            napi="9",
            nghttp2="1.53.0",
            nghttp3="0.7.0",
            ngtcp2="0.8.1",
            openssl="3.0.8+quic",
            simdutf="3.2.12",
            tz="2023c",
            undici="5.22.1",
            unicode="15.0",
            uv="1.45.0",
            uvwasi="0.0.18",
            v8="11.3.244.8-node.9",
            zlib="1.2.13.1-motley",
        )

        server_info = ServerInfo(
            version="15.8.10-2023.2.44",
            release="2023.2.9",
            arch="x64",
            platform="linux",
            versions=versions,
            memoryUsage=memory_usage,
            cpuUsage=cpu_usage,
            uptime=2083622.963931177,
            pid=1,
            dependencies={"@itential/service": "3.1.12"},
        )

        health_response = HealthResponse(
            status=platform_status,
            system=system_info,
            server=server_info,
            applications=[],
            adapters=[],
        )

        assert health_response.status.host == "test.platform"
        assert health_response.system.arch == "x64"
        assert health_response.server.version == "15.8.10-2023.2.44"
        assert len(health_response.applications) == 0
        assert len(health_response.adapters) == 0

    def test_health_response_with_applications_and_adapters(self):
        """Test HealthResponse with applications and adapters."""
        service_status = ServiceStatus(service="redis", status="running")

        platform_status = PlatformStatus(
            host="test.platform",
            serverId="test-server-123",
            services=[service_status],
            timestamp=1757004595716,
            apps="running",
            adapters="running",
        )

        cpu_times = CpuTimes(user=100, nice=50, sys=75, idle=1000, irq=25)
        cpu_info = CpuInfo(model="Test CPU", speed=3000, times=cpu_times)

        system_info = SystemInfo(
            arch="x64",
            release="6.13.12-100.fc40.x86_64",
            uptime=4668812.41,
            freemem=53953363968,
            totalmem=67111694336,
            loadavg=[0.15, 0.22, 0.25],
            cpus=[cpu_info],
        )

        memory_usage = MemoryUsage(
            rss=469671936,
            heapTotal=158703616,
            heapUsed=147501584,
            external=50291978,
            arrayBuffers=46521129,
        )

        cpu_usage = CpuUsage(user=3815108692, system=621631048)

        versions = ServerVersions(
            node="20.3.0",
            acorn="8.8.2",
            ada="2.5.0",
            ares="1.19.1",
            base64="0.5.0",
            brotli="1.0.9",
            cjs_module_lexer="1.2.2",
            cldr="43.0",
            icu="73.1",
            llhttp="8.1.0",
            modules="115",
            napi="9",
            nghttp2="1.53.0",
            nghttp3="0.7.0",
            ngtcp2="0.8.1",
            openssl="3.0.8+quic",
            simdutf="3.2.12",
            tz="2023c",
            undici="5.22.1",
            unicode="15.0",
            uv="1.45.0",
            uvwasi="0.0.18",
            v8="11.3.244.8-node.9",
            zlib="1.2.13.1-motley",
        )

        server_info = ServerInfo(
            version="15.8.10-2023.2.44",
            release="2023.2.9",
            arch="x64",
            platform="linux",
            versions=versions,
            memoryUsage=memory_usage,
            cpuUsage=cpu_usage,
            uptime=2083622.963931177,
            pid=1,
            dependencies={"@itential/service": "3.1.12"},
        )

        # Create test application
        app_memory = MemoryUsage(
            rss=100000000,
            heapTotal=50000000,
            heapUsed=40000000,
            external=5000000,
            arrayBuffers=4000000,
        )

        app_cpu = CpuUsage(user=1000000, system=500000)

        app_logger = LoggerConfig(console="info", file="info", syslog="warning")

        application = ApplicationInfo(
            id="TestApp",
            package_id="@itential/test-app",
            version="1.0.0",
            type="Application",
            description="Test application",
            routePrefix="test-app",
            state="RUNNING",
            uptime=1000.0,
            memoryUsage=app_memory,
            cpuUsage=app_cpu,
            pid=123,
            logger=app_logger,
            timestamp=1757004595716,
            prevUptime=999.0,
        )

        # Create test adapter
        adapter_memory = MemoryUsage(
            rss=150000000,
            heapTotal=70000000,
            heapUsed=60000000,
            external=8000000,
            arrayBuffers=7000000,
        )

        adapter_cpu = CpuUsage(user=2000000, system=1000000)

        adapter_connection = ConnectionInfo(state="ONLINE")

        adapter_logger = LoggerConfig(console="info", file="info", syslog="warning")

        adapter = AdapterInfo(
            id="TestAdapter",
            package_id="@itential/test-adapter",
            version="1.0.0",
            type="Adapter",
            description="Test adapter",
            routePrefix="test-adapter",
            state="RUNNING",
            connection=adapter_connection,
            uptime=2000.0,
            memoryUsage=adapter_memory,
            cpuUsage=adapter_cpu,
            pid=456,
            logger=adapter_logger,
            timestamp=1757004595716,
            prevUptime=1999.0,
        )

        health_response = HealthResponse(
            status=platform_status,
            system=system_info,
            server=server_info,
            applications=[application],
            adapters=[adapter],
        )

        assert len(health_response.applications) == 1
        assert len(health_response.adapters) == 1
        assert health_response.applications[0].id == "TestApp"
        assert health_response.adapters[0].id == "TestAdapter"

    def test_health_response_empty_lists(self):
        """Test HealthResponse with empty applications and adapters lists."""
        service_status = ServiceStatus(service="redis", status="running")

        platform_status = PlatformStatus(
            host="test.platform",
            serverId="test-server-123",
            services=[service_status],
            timestamp=1757004595716,
            apps="running",
            adapters="running",
        )

        cpu_times = CpuTimes(user=100, nice=50, sys=75, idle=1000, irq=25)
        cpu_info = CpuInfo(model="Test CPU", speed=3000, times=cpu_times)

        system_info = SystemInfo(
            arch="x64",
            release="6.13.12-100.fc40.x86_64",
            uptime=4668812.41,
            freemem=53953363968,
            totalmem=67111694336,
            loadavg=[0.15, 0.22, 0.25],
            cpus=[cpu_info],
        )

        memory_usage = MemoryUsage(
            rss=469671936,
            heapTotal=158703616,
            heapUsed=147501584,
            external=50291978,
            arrayBuffers=46521129,
        )

        cpu_usage = CpuUsage(user=3815108692, system=621631048)

        versions = ServerVersions(
            node="20.3.0",
            acorn="8.8.2",
            ada="2.5.0",
            ares="1.19.1",
            base64="0.5.0",
            brotli="1.0.9",
            cjs_module_lexer="1.2.2",
            cldr="43.0",
            icu="73.1",
            llhttp="8.1.0",
            modules="115",
            napi="9",
            nghttp2="1.53.0",
            nghttp3="0.7.0",
            ngtcp2="0.8.1",
            openssl="3.0.8+quic",
            simdutf="3.2.12",
            tz="2023c",
            undici="5.22.1",
            unicode="15.0",
            uv="1.45.0",
            uvwasi="0.0.18",
            v8="11.3.244.8-node.9",
            zlib="1.2.13.1-motley",
        )

        server_info = ServerInfo(
            version="15.8.10-2023.2.44",
            release="2023.2.9",
            arch="x64",
            platform="linux",
            versions=versions,
            memoryUsage=memory_usage,
            cpuUsage=cpu_usage,
            uptime=2083622.963931177,
            pid=1,
            dependencies={"@itential/service": "3.1.12"},
        )

        health_response = HealthResponse(
            status=platform_status, system=system_info, server=server_info
        )

        assert health_response.applications == []
        assert health_response.adapters == []

    def test_health_response_comprehensive_serialization(self):
        """Test complete HealthResponse serialization with all components."""
        service_status = ServiceStatus(service="redis", status="running")

        platform_status = PlatformStatus(
            host="test.platform",
            serverId="test-server-123",
            services=[service_status],
            timestamp=1757004595716,
            apps="running",
            adapters="running",
        )

        cpu_times = CpuTimes(user=100, nice=50, sys=75, idle=1000, irq=25)
        cpu_info = CpuInfo(model="Test CPU", speed=3000, times=cpu_times)

        system_info = SystemInfo(
            arch="x64",
            release="6.13.12-100.fc40.x86_64",
            uptime=4668812.41,
            freemem=53953363968,
            totalmem=67111694336,
            loadavg=[0.15, 0.22, 0.25],
            cpus=[cpu_info],
        )

        memory_usage = MemoryUsage(
            rss=469671936,
            heapTotal=158703616,
            heapUsed=147501584,
            external=50291978,
            arrayBuffers=46521129,
        )

        cpu_usage = CpuUsage(user=3815108692, system=621631048)

        versions = ServerVersions(
            node="20.3.0",
            acorn="8.8.2",
            ada="2.5.0",
            ares="1.19.1",
            base64="0.5.0",
            brotli="1.0.9",
            cjs_module_lexer="1.2.2",
            cldr="43.0",
            icu="73.1",
            llhttp="8.1.0",
            modules="115",
            napi="9",
            nghttp2="1.53.0",
            nghttp3="0.7.0",
            ngtcp2="0.8.1",
            openssl="3.0.8+quic",
            simdutf="3.2.12",
            tz="2023c",
            undici="5.22.1",
            unicode="15.0",
            uv="1.45.0",
            uvwasi="0.0.18",
            v8="11.3.244.8-node.9",
            zlib="1.2.13.1-motley",
        )

        server_info = ServerInfo(
            version="15.8.10-2023.2.44",
            release="2023.2.9",
            arch="x64",
            platform="linux",
            versions=versions,
            memoryUsage=memory_usage,
            cpuUsage=cpu_usage,
            uptime=2083622.963931177,
            pid=1,
            dependencies={"@itential/service": "3.1.12"},
        )

        health_response = HealthResponse(
            status=platform_status,
            system=system_info,
            server=server_info,
            applications=[],
            adapters=[],
        )

        data = health_response.model_dump()
        assert "status" in data
        assert "system" in data
        assert "server" in data
        assert "applications" in data
        assert "adapters" in data

        # Test alias serialization
        alias_data = health_response.model_dump(by_alias=True)
        assert "serverId" in alias_data["status"]
        assert "freemem" in alias_data["system"]
        assert "memoryUsage" in alias_data["server"]

    def test_health_response_with_actual_api_data(self):
        """Test HealthResponse with partial actual API data structure."""
        # Simplified version of actual API response data
        api_data = {
            "status": {
                "host": "platform.devel",
                "serverId": "c0ecb6ba62d43b067c09a1c33488a7d41df592f6",
                "serverName": None,
                "services": [
                    {"service": "redis", "status": "running"},
                    {"service": "mongo", "status": "running"},
                ],
                "timestamp": 1757090849045,
                "apps": "degraded",
                "adapters": "running",
            },
            "system": {
                "arch": "x64",
                "release": "6.13.12-100.fc40.x86_64",
                "uptime": 4755065.68,
                "freemem": 53909569536,
                "totalmem": 67111694336,
                "loadavg": [0.0, 0.05, 0.15],
                "cpus": [
                    {
                        "model": "Intel(R) Core(TM) i7-10710U CPU @ 1.10GHz",
                        "speed": 3980,
                        "times": {
                            "user": 53001480,
                            "nice": 27070,
                            "sys": 19005460,
                            "idle": 4648595970,
                            "irq": 8128900,
                        },
                    }
                ],
            },
            "server": {
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
                    "rss": 490758144,
                    "heapTotal": 191733760,
                    "heapUsed": 155665376,
                    "external": 53745949,
                    "arrayBuffers": 49975100,
                },
                "cpuUsage": {"user": 3899743493, "system": 641198313},
                "uptime": 2169876.158544452,
                "pid": 1,
                "dependencies": {
                    "@itential/service": "3.1.12",
                    "@itential/network": "4.1.5",
                },
            },
            "applications": [
                {
                    "id": "AGManager",
                    "package_id": "@itential/app-ag_manager",
                    "version": "1.20.3-2023.2.1",
                    "type": "Application",
                    "description": "stand alone discovery",
                    "routePrefix": "ag-manager",
                    "state": "RUNNING",
                    "connection": None,
                    "uptime": 846338.466451258,
                    "memoryUsage": {
                        "rss": 181534720,
                        "heapTotal": 111050752,
                        "heapUsed": 107171864,
                        "external": 80144072,
                        "arrayBuffers": 77843804,
                    },
                    "cpuUsage": {"user": 289119808, "system": 125456921},
                    "pid": 715,
                    "logger": {"console": "info", "file": "info", "syslog": "warning"},
                    "timestamp": 1757090846633,
                    "prevUptime": 846333.466399005,
                }
            ],
            "adapters": [
                {
                    "id": "Gateway",
                    "package_id": "@itential/adapter-automation_gateway",
                    "version": "4.31.4-2023.2.1",
                    "type": "Adapter",
                    "description": "Itential Ansible Manager Adapter",
                    "routePrefix": "automationgateway",
                    "state": "RUNNING",
                    "connection": {"state": "ONLINE"},
                    "uptime": 846361.043660279,
                    "memoryUsage": {
                        "rss": 157736960,
                        "heapTotal": 83701760,
                        "heapUsed": 72719480,
                        "external": 95906058,
                        "arrayBuffers": 93589021,
                    },
                    "cpuUsage": {"user": 468600392, "system": 137284189},
                    "pid": 701,
                    "logger": {"console": "info", "file": "info", "syslog": "warning"},
                    "timestamp": 1757090848784,
                    "prevUptime": 846356.042837805,
                }
            ],
        }

        # Test that our models can parse actual API data
        health_response = HealthResponse(**api_data)

        # Verify parsing worked correctly with snake_case field access
        assert health_response.status.host == "platform.devel"
        assert (
            health_response.status.server_id
            == "c0ecb6ba62d43b067c09a1c33488a7d41df592f6"
        )
        assert health_response.system.arch == "x64"
        assert health_response.system.free_mem == 53909569536
        assert health_response.system.total_mem == 67111694336
        assert health_response.system.load_avg == [0.0, 0.05, 0.15]
        assert health_response.server.memory_usage.heap_total == 191733760
        assert health_response.server.cpu_usage.user == 3899743493
        assert len(health_response.applications) == 1
        assert len(health_response.adapters) == 1

        app = health_response.applications[0]
        assert app.package_id == "@itential/app-ag_manager"
        assert app.route_prefix == "ag-manager"
        assert app.memory_usage.heap_total == 111050752
        assert app.prev_uptime == 846333.466399005

        adapter = health_response.adapters[0]
        assert adapter.package_id == "@itential/adapter-automation_gateway"
        assert adapter.route_prefix == "automationgateway"
        assert adapter.memory_usage.heap_total == 83701760
        assert adapter.prev_uptime == 846356.042837805

        # Test that serialization with aliases produces API-compatible output
        serialized = health_response.model_dump(by_alias=True)
        assert "serverId" in serialized["status"]
        assert "freemem" in serialized["system"]
        assert "memoryUsage" in serialized["server"]
        assert serialized["applications"][0]["routePrefix"] == "ag-manager"
        assert serialized["adapters"][0]["routePrefix"] == "automationgateway"
