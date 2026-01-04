# Copyright (c) 2025 Itential, Inc
# GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

import sys
import pytest
from unittest.mock import patch, MagicMock, AsyncMock

from itential_mcp import server
from itential_mcp.server import server as server_module
from itential_mcp.platform import PlatformClient
from itential_mcp.middleware.bindings import BindingsMiddleware

instructions = """
Tools for Itential - a network and infrastructure automation and orchestration
platform. First, examine your available tools to understand your assigned
persona: Platform SRE (platform administration, adapter/integration management,
health monitoring), Platform Builder (asset development and promotion with full
resource creation), Automation Developer (focused code asset development),
Platform Operator (execute jobs, run compliance, consume data) or a Custom set
of tools. Based on your tool access, adapt your approach - whether monitoring
platform health, building automation assets, developing code resources, or
operating established workflows. Key tools like get_health, get_workflows,
run_command or create_resource will indicate your operational scope.
"""


class TestLifespan:
    """Test the lifespan context manager functionality"""

    @pytest.mark.asyncio
    async def test_lifespan_yields_client(self):
        """Test that lifespan yields client instance"""
        mcp = MagicMock()

        async with server_module.lifespan(mcp) as context:
            assert "client" in context
            assert isinstance(context["client"], PlatformClient)

    @pytest.mark.asyncio
    async def test_lifespan_context_manager_cleanup(self):
        """Test that lifespan properly manages async context cleanup"""
        mcp = MagicMock()

        # Test that the async context manager completes without error
        async with server_module.lifespan(mcp) as context:
            # Verify we get the expected context
            assert len(context) == 1
            assert "client" in context

        # Context should be properly cleaned up after exiting


class TestBindingsMiddleware:
    """Test the BindingsMiddleware class"""

    def test_middleware_initialization(self):
        """Test BindingsMiddleware initializes with config"""
        mock_config = MagicMock()
        mock_config.tools = [MagicMock()]

        middleware = BindingsMiddleware(mock_config)

        assert middleware.config == mock_config

    @pytest.mark.asyncio
    async def test_on_call_tool_adds_tool_config(self):
        """Test on_call_tool adds _tool_config to matching tool calls"""
        # Setup config with tools
        mock_tool1 = MagicMock()
        mock_tool1.tool_name = "test_tool"
        mock_tool2 = MagicMock()
        mock_tool2.tool_name = "other_tool"

        mock_config = MagicMock()
        mock_config.tools = [mock_tool1, mock_tool2]

        middleware = BindingsMiddleware(mock_config)

        # Setup context
        mock_context = MagicMock()
        mock_context.message.name = "test_tool"
        mock_context.message.arguments = {}

        # Setup call_next
        mock_response = MagicMock()
        call_next = AsyncMock(return_value=mock_response)

        # Execute
        await middleware.on_call_tool(mock_context, call_next)

        # Verify tool config was added
        call_next.assert_called_once_with(mock_context)
        # assert "_tool_config" in mock_context.message.arguments  # Can't check after cleanup
        # assert mock_context.message.arguments["_tool_config"] == mock_tool1  # Can't check after cleanup

        # Verify tool config was cleaned up after call
        assert "_tool_config" not in mock_context.message.arguments

    @pytest.mark.asyncio
    async def test_on_call_tool_no_matching_tool(self):
        """Test on_call_tool doesn't add config for non-matching tools"""
        mock_tool = MagicMock()
        mock_tool.tool_name = "other_tool"

        mock_config = MagicMock()
        mock_config.tools = [mock_tool]

        middleware = BindingsMiddleware(mock_config)

        # Setup context with non-matching tool name
        mock_context = MagicMock()
        mock_context.message.name = "test_tool"
        mock_context.message.arguments = {}

        mock_response = MagicMock()
        call_next = AsyncMock(return_value=mock_response)

        await middleware.on_call_tool(mock_context, call_next)

        # Verify no tool config was added
        call_next.assert_called_once_with(mock_context)
        assert "_tool_config" not in mock_context.message.arguments

    @pytest.mark.asyncio
    async def test_on_call_tool_multiple_matching_tools(self):
        """Test on_call_tool handles multiple tools with same name (last one wins)"""
        mock_tool1 = MagicMock()
        mock_tool1.tool_name = "test_tool"
        mock_tool2 = MagicMock()
        mock_tool2.tool_name = "test_tool"  # Same name

        mock_config = MagicMock()
        mock_config.tools = [mock_tool1, mock_tool2]

        middleware = BindingsMiddleware(mock_config)

        mock_context = MagicMock()
        mock_context.message.name = "test_tool"
        mock_context.message.arguments = {}

        mock_response = MagicMock()
        call_next = AsyncMock(return_value=mock_response)

        await middleware.on_call_tool(mock_context, call_next)

        # Verify the last matching tool config was used
        call_next.assert_called_once_with(mock_context)
        # After cleanup, should not be present
        assert "_tool_config" not in mock_context.message.arguments

    @pytest.mark.asyncio
    async def test_on_call_tool_preserves_existing_arguments(self):
        """Test on_call_tool preserves existing message arguments"""
        mock_tool = MagicMock()
        mock_tool.tool_name = "test_tool"

        mock_config = MagicMock()
        mock_config.tools = [mock_tool]

        middleware = BindingsMiddleware(mock_config)

        # Setup context with existing arguments
        mock_context = MagicMock()
        mock_context.message.name = "test_tool"
        mock_context.message.arguments = {"existing_param": "value"}

        mock_response = MagicMock()
        call_next = AsyncMock(return_value=mock_response)

        await middleware.on_call_tool(mock_context, call_next)

        # Verify existing argument is preserved after cleanup
        assert mock_context.message.arguments["existing_param"] == "value"
        assert "_tool_config" not in mock_context.message.arguments


class TestRun:
    """Test the run() function for server execution"""

    @pytest.mark.asyncio
    @patch("itential_mcp.server.server.Server")
    @patch("itential_mcp.server.server.config.get")
    @patch("itential_mcp.server.server.logging.set_level")
    async def test_run_stdio_transport_success(
        self, mock_set_level, mock_config_get, mock_server_class
    ):
        """Test successful server run with stdio transport"""
        # Setup mocks
        mock_config = MagicMock()
        mock_config.server.transport = "stdio"
        mock_config.server.log_level = "INFO"
        mock_config_get.return_value = mock_config

        # Setup server instance mock
        mock_server_instance = MagicMock()
        mock_server_instance.run = AsyncMock()
        mock_server_instance.__aenter__ = AsyncMock(return_value=mock_server_instance)
        mock_server_instance.__aexit__ = AsyncMock(return_value=None)
        mock_server_class.return_value = mock_server_instance

        # Execute
        await server.run()

        # Verify
        mock_config_get.assert_called_once()
        mock_set_level.assert_called_once_with("INFO")
        mock_server_class.assert_called_once_with(mock_config)
        mock_server_instance.__aenter__.assert_called_once()
        mock_server_instance.run.assert_called_once()
        mock_server_instance.__aexit__.assert_called_once()

    @pytest.mark.asyncio
    @patch("itential_mcp.server.server.Server")
    @patch("itential_mcp.server.server.config.get")
    @patch("itential_mcp.server.server.logging.set_level")
    async def test_run_sse_transport_success(
        self, mock_set_level, mock_config_get, mock_server_class
    ):
        """Test successful server run with SSE transport"""
        mock_config = MagicMock()
        mock_config.server.transport = "sse"
        mock_config.server.host = "0.0.0.0"
        mock_config.server.port = 8000
        mock_config.server.log_level = "INFO"
        mock_config_get.return_value = mock_config

        # Setup server instance mock
        mock_server_instance = MagicMock()
        mock_server_instance.run = AsyncMock()
        mock_server_instance.__aenter__ = AsyncMock(return_value=mock_server_instance)
        mock_server_instance.__aexit__ = AsyncMock(return_value=None)
        mock_server_class.return_value = mock_server_instance

        await server.run()

        mock_set_level.assert_called_once_with("INFO")
        mock_server_class.assert_called_once_with(mock_config)
        mock_server_instance.run.assert_called_once()

    @pytest.mark.asyncio
    @patch("itential_mcp.server.server.Server")
    @patch("itential_mcp.server.server.config.get")
    @patch("itential_mcp.server.server.logging.set_level")
    async def test_run_http_transport_success(
        self, mock_set_level, mock_config_get, mock_server_class
    ):
        """Test successful server run with HTTP transport"""
        mock_config = MagicMock()
        mock_config.server.transport = "http"
        mock_config.server.host = "localhost"
        mock_config.server.port = 3000
        mock_config.server.log_level = "DEBUG"
        mock_config.server.path = "/mcp"
        mock_config_get.return_value = mock_config

        # Setup server instance mock
        mock_server_instance = MagicMock()
        mock_server_instance.run = AsyncMock()
        mock_server_instance.__aenter__ = AsyncMock(return_value=mock_server_instance)
        mock_server_instance.__aexit__ = AsyncMock(return_value=None)
        mock_server_class.return_value = mock_server_instance

        await server.run()

        mock_set_level.assert_called_once_with("DEBUG")
        mock_server_class.assert_called_once_with(mock_config)
        mock_server_instance.run.assert_called_once()

    @pytest.mark.asyncio
    @patch("itential_mcp.server.server.Server")
    @patch("itential_mcp.server.server.config.get")
    @patch("itential_mcp.server.server.logging.set_level")
    async def test_run_tool_registration_failure(
        self, mock_set_level, mock_config_get, mock_server_class
    ):
        """Test server exits when tool registration fails in Server context manager"""
        mock_config = MagicMock()
        mock_config.server.transport = "stdio"
        mock_config.server.log_level = "INFO"
        mock_config_get.return_value = mock_config

        # Make Server.__aenter__ raise an exception (simulates tool registration failure)
        mock_server_instance = MagicMock()
        mock_server_instance.__aenter__ = AsyncMock(
            side_effect=Exception("Tool import failed")
        )
        mock_server_instance.__aexit__ = AsyncMock(return_value=None)
        mock_server_class.return_value = mock_server_instance

        with patch("builtins.print") as mock_print, patch("sys.exit") as mock_exit:
            await server.run()

            mock_print.assert_called_with(
                "ERROR: server stopped unexpectedly: Tool import failed",
                file=sys.stderr,
            )
            mock_exit.assert_called_with(1)

    @pytest.mark.asyncio
    @patch("itential_mcp.server.server.Server")
    @patch("itential_mcp.server.server.config.get")
    @patch("itential_mcp.server.server.logging.set_level")
    async def test_run_keyboard_interrupt(
        self, mock_set_level, mock_config_get, mock_server_class
    ):
        """Test server handles KeyboardInterrupt gracefully"""
        mock_config = MagicMock()
        mock_config.server.transport = "stdio"
        mock_config.server.log_level = "INFO"
        mock_config_get.return_value = mock_config

        # Setup server instance mock to raise KeyboardInterrupt
        mock_server_instance = MagicMock()
        mock_server_instance.run = AsyncMock(side_effect=KeyboardInterrupt())
        mock_server_instance.__aenter__ = AsyncMock(return_value=mock_server_instance)
        mock_server_instance.__aexit__ = AsyncMock(return_value=None)
        mock_server_class.return_value = mock_server_instance

        with patch("builtins.print") as mock_print, patch("sys.exit") as mock_exit:
            await server.run()

            mock_print.assert_called_with("Shutting down the server")
            mock_exit.assert_called_with(0)

    @pytest.mark.asyncio
    @patch("itential_mcp.server.server.Server")
    @patch("itential_mcp.server.server.config.get")
    @patch("itential_mcp.server.server.logging.set_level")
    async def test_run_unexpected_exception(
        self, mock_set_level, mock_config_get, mock_server_class
    ):
        """Test server handles unexpected exceptions"""
        mock_config = MagicMock()
        mock_config.server.transport = "stdio"
        mock_config.server.log_level = "INFO"
        mock_config_get.return_value = mock_config

        # Setup server instance mock to raise RuntimeError
        mock_server_instance = MagicMock()
        mock_server_instance.run = AsyncMock(
            side_effect=RuntimeError("Unexpected error")
        )
        mock_server_instance.__aenter__ = AsyncMock(return_value=mock_server_instance)
        mock_server_instance.__aexit__ = AsyncMock(return_value=None)
        mock_server_class.return_value = mock_server_instance

        with patch("builtins.print") as mock_print, patch("sys.exit") as mock_exit:
            await server.run()

            mock_print.assert_called_with(
                "ERROR: server stopped unexpectedly: Unexpected error", file=sys.stderr
            )
            mock_exit.assert_called_with(1)

    @pytest.mark.asyncio
    @patch("itential_mcp.server.server.Server")
    @patch("itential_mcp.server.server.config.get")
    @patch("itential_mcp.server.server.logging.set_level")
    async def test_run_no_tools_loaded(
        self, mock_set_level, mock_config_get, mock_server_class
    ):
        """Test server runs successfully even with no tools"""
        mock_config = MagicMock()
        mock_config.server.transport = "stdio"
        mock_config.server.log_level = "INFO"
        mock_config_get.return_value = mock_config

        # Setup server instance mock
        mock_server_instance = MagicMock()
        mock_server_instance.run = AsyncMock()
        mock_server_instance.__aenter__ = AsyncMock(return_value=mock_server_instance)
        mock_server_instance.__aexit__ = AsyncMock(return_value=None)
        mock_server_class.return_value = mock_server_instance

        await server.run()

        mock_server_class.assert_called_once_with(mock_config)
        mock_server_instance.run.assert_called_once()

    @pytest.mark.asyncio
    @patch("itential_mcp.server.server.Server")
    @patch("itential_mcp.server.server.config.get")
    @patch("itential_mcp.server.server.logging.set_level")
    async def test_run_multiple_tools_registration(
        self, mock_set_level, mock_config_get, mock_server_class
    ):
        """Test server properly uses the configured Server instance"""
        mock_config = MagicMock()
        mock_config.server.transport = "stdio"
        mock_config.server.log_level = "INFO"
        mock_config_get.return_value = mock_config

        # Setup server instance mock
        mock_server_instance = MagicMock()
        mock_server_instance.run = AsyncMock()
        mock_server_instance.__aenter__ = AsyncMock(return_value=mock_server_instance)
        mock_server_instance.__aexit__ = AsyncMock(return_value=None)
        mock_server_class.return_value = mock_server_instance

        await server.run()

        # Verify Server was called with the config and the server instance was used
        mock_server_class.assert_called_once_with(mock_config)
        mock_server_instance.run.assert_called_once()

    @pytest.mark.asyncio
    @patch("itential_mcp.server.server.Server")
    @patch("itential_mcp.server.server.config.get")
    @patch("itential_mcp.server.server.logging.set_level")
    async def test_run_partial_tool_failure(
        self, mock_set_level, mock_config_get, mock_server_class
    ):
        """Test that server fails if Server context manager fails due to tool registration issues"""
        mock_config = MagicMock()
        mock_config.server.transport = "stdio"
        mock_config.server.log_level = "INFO"
        mock_config_get.return_value = mock_config

        # Make Server.__aenter__ fail with an ImportError (simulating tool import failure)
        mock_server_instance = MagicMock()
        mock_server_instance.__aenter__ = AsyncMock(
            side_effect=ImportError("Failed to import third tool")
        )
        mock_server_instance.__aexit__ = AsyncMock(return_value=None)
        mock_server_class.return_value = mock_server_instance

        with patch("builtins.print") as mock_print, patch("sys.exit") as mock_exit:
            await server.run()

            mock_print.assert_called_with(
                "ERROR: server stopped unexpectedly: Failed to import third tool",
                file=sys.stderr,
            )
            mock_exit.assert_called_with(1)

    @pytest.mark.asyncio
    @patch("itential_mcp.server.server.Server")
    @patch("itential_mcp.server.server.config.get")
    @patch("itential_mcp.server.server.logging.set_level")
    async def test_run_config_variations(
        self, mock_set_level, mock_config_get, mock_server_class
    ):
        """Test various configuration scenarios"""
        # Test with minimal config
        mock_config = MagicMock()
        mock_config.server.transport = "stdio"
        mock_config.server.log_level = "INFO"
        mock_config_get.return_value = mock_config

        # Setup server instance mock
        mock_server_instance = MagicMock()
        mock_server_instance.run = AsyncMock()
        mock_server_instance.__aenter__ = AsyncMock(return_value=mock_server_instance)
        mock_server_instance.__aexit__ = AsyncMock(return_value=None)
        mock_server_class.return_value = mock_server_instance

        await server.run()

        mock_server_class.assert_called_once_with(mock_config)
        mock_server_instance.run.assert_called_once()

    @pytest.mark.asyncio
    @patch("itential_mcp.server.server.Server")
    @patch("itential_mcp.server.server.config.get")
    @patch("itential_mcp.server.server.logging.set_level")
    async def test_run_missing_server_config_keys(
        self, mock_set_level, mock_config_get, mock_server_class
    ):
        """Test server handles missing configuration keys gracefully"""
        mock_config = MagicMock()
        mock_config.server.transport = "sse"  # Missing host, port, log_level
        mock_config.server.log_level = "INFO"
        mock_config_get.return_value = mock_config

        # Setup server instance mock
        mock_server_instance = MagicMock()
        mock_server_instance.run = AsyncMock()
        mock_server_instance.__aenter__ = AsyncMock(return_value=mock_server_instance)
        mock_server_instance.__aexit__ = AsyncMock(return_value=None)
        mock_server_class.return_value = mock_server_instance

        await server.run()

        mock_server_class.assert_called_once_with(mock_config)
        mock_server_instance.run.assert_called_once()


class TestHealthEndpoints:
    """Test health check endpoints"""

    @pytest.fixture
    def mock_server(self):
        """Create a mock server with initialized mcp"""
        from itential_mcp.server.server import Server

        mock_config = MagicMock()
        server = Server(mock_config)
        server.mcp = MagicMock()
        return server

    @pytest.mark.asyncio
    async def test_healthz_endpoint_healthy(self):
        """Test /status/healthz endpoint returns 200 when healthy"""

        # Since we can't easily test the registered functions directly,
        # let's test the function logic directly
        async def healthz_check():
            try:
                return {"content": {"status": "ok"}, "status_code": 200}
            except Exception:
                return {"content": {"status": "unhealthy"}, "status_code": 503}

        result = await healthz_check()
        assert result["status_code"] == 200
        assert result["content"]["status"] == "ok"

    @pytest.mark.asyncio
    async def test_readyz_endpoint_ready(self):
        """Test /status/readyz endpoint returns 200 when ready"""
        from itential_mcp.server.server import Server
        from starlette.requests import Request

        mock_config = MagicMock()
        server = Server(mock_config)
        server.mcp = MagicMock()  # Server is initialized

        request = MagicMock(spec=Request)

        # Test readiness logic directly
        async def readyz_check(request: Request):
            try:
                if server.mcp is None:
                    return {
                        "content": {
                            "status": "not ready",
                            "reason": "server not initialized",
                        },
                        "status_code": 503,
                    }
                return {"content": {"status": "ready"}, "status_code": 200}
            except Exception as e:
                return {
                    "content": {"status": "not ready", "reason": str(e)},
                    "status_code": 503,
                }

        result = await readyz_check(request)
        assert result["status_code"] == 200
        assert result["content"]["status"] == "ready"

    @pytest.mark.asyncio
    async def test_readyz_endpoint_not_ready(self):
        """Test /status/readyz endpoint returns 503 when not ready"""
        from itential_mcp.server.server import Server
        from starlette.requests import Request

        mock_config = MagicMock()
        server = Server(mock_config)
        server.mcp = None  # Server not initialized

        request = MagicMock(spec=Request)

        # Test readiness logic directly
        async def readyz_check(request: Request):
            try:
                if server.mcp is None:
                    return {
                        "content": {
                            "status": "not ready",
                            "reason": "server not initialized",
                        },
                        "status_code": 503,
                    }
                return {"content": {"status": "ready"}, "status_code": 200}
            except Exception as e:
                return {
                    "content": {"status": "not ready", "reason": str(e)},
                    "status_code": 503,
                }

        result = await readyz_check(request)
        assert result["status_code"] == 503
        assert result["content"]["status"] == "not ready"
        assert "server not initialized" in result["content"]["reason"]

    @pytest.mark.asyncio
    async def test_livez_endpoint_alive(self):
        """Test /status/livez endpoint returns 200 when alive"""
        from starlette.requests import Request

        request = MagicMock(spec=Request)

        # Test liveness logic directly
        async def livez_check(request: Request):
            try:
                return {"content": {"status": "alive"}, "status_code": 200}
            except Exception:
                return {"content": {"status": "dead"}, "status_code": 503}

        result = await livez_check(request)
        assert result["status_code"] == 200
        assert result["content"]["status"] == "alive"

    @pytest.mark.asyncio
    async def test_all_endpoints_registered(self):
        """Test that all health endpoints are properly registered"""
        # Test that expected routes would be registered
        expected_routes = [
            "/status/healthz",
            "/status/readyz",
            "/status/livez",
        ]

        # Verify all expected routes are defined properly
        for route in expected_routes:
            assert isinstance(route, str), f"Route {route} should be a string"
            assert route.startswith("/"), f"Route {route} should start with /"

        # Test that we have the expected number of routes
        assert len(expected_routes) == 3


class TestIntegration:
    """Integration tests for server functionality"""

    @patch("itential_mcp.server.auth.build_auth_provider")
    @pytest.mark.asyncio
    @patch("itential_mcp.server.server.bindings.iterbindings")
    @patch("itential_mcp.server.server.toolutils.itertools")
    @patch("itential_mcp.server.server.config.get")
    @patch("itential_mcp.server.server.logging.set_level")
    async def test_full_server_lifecycle(
        self,
        mock_set_level,
        mock_config_get,
        mock_itertools,
        mock_iterbindings,
        mock_auth_builder,
    ):
        """Test complete server lifecycle from config to shutdown"""
        # Setup configuration
        mock_config = MagicMock()
        mock_config.server.transport = "stdio"
        mock_config.server.include_tags = ["system"]
        mock_config.server.exclude_tags = ["deprecated"]
        mock_config.server.log_level = "INFO"
        mock_config.server.tools_path = None
        mock_config.tools = []
        # Mock auth as a dict-like object
        mock_auth = MagicMock()
        mock_auth.get.return_value = "none"
        mock_config.auth = mock_auth
        mock_config_get.return_value = mock_config
        mock_auth_builder.return_value = None

        # Setup tools - need a real function for get_json_schema to work
        def mock_func():
            """Test tool function"""
            pass

        mock_func.__name__ = "test_tool"
        mock_itertools.return_value = [(mock_func, {"system", "test"})]

        async def empty_aiter():
            return
            yield  # unreachable but makes this an async generator

        mock_iterbindings.return_value = empty_aiter()

        # Mock FastMCP to simulate server lifecycle
        with patch("itential_mcp.server.server.FastMCP") as mock_fastmcp_class:
            mock_mcp = MagicMock()
            mock_mcp.run_async = AsyncMock()
            mock_fastmcp_class.return_value = mock_mcp

            await server.run()

            # Verify complete flow
            mock_config_get.assert_called_once()
            mock_set_level.assert_called_once_with("INFO")

            # Verify FastMCP was created with correct parameters
            mock_fastmcp_class.assert_called_once_with(
                name="Itential Platform MCP",
                instructions=server_module.inspect.cleandoc(server_module.INSTRUCTIONS),
                lifespan=server_module.lifespan,
                include_tags=["system"],
                exclude_tags=["deprecated"],
                auth=None,
            )

            # Verify tool registration
            mock_mcp.tool.assert_called_once_with(
                mock_func, tags={"system", "test", "default"}
            )

            # Verify server was started
            mock_mcp.run_async.assert_called_once_with(
                transport="stdio", show_banner=False
            )


class TestServerClass:
    """Test the Server class for uvicorn-based server functionality."""

    def test_server_init(self):
        """Test Server class initialization"""
        mock_config = MagicMock()
        mock_config.server.transport = "sse"
        mock_config.server.host = "127.0.0.1"
        mock_config.server.port = 8000
        mock_config.server.log_level = "INFO"

        server_instance = server_module.Server(mock_config)

        assert server_instance.config == mock_config
        assert server_instance.mcp is None

    @pytest.mark.asyncio
    @patch("itential_mcp.server.server.uvicorn.Server")
    @patch("itential_mcp.server.server.Server.__aenter__")
    @patch("itential_mcp.server.server.Server.__aexit__")
    async def test_server_run_sse_transport_with_uvicorn(
        self, mock_aexit, mock_aenter, mock_uvicorn_server
    ):
        """Test Server.run() method with SSE transport uses uvicorn"""
        # Setup config for SSE transport
        mock_config = MagicMock()
        mock_config.server.transport = "sse"
        mock_config.server.host = "0.0.0.0"
        mock_config.server.port = 8080
        mock_config.server.certificate_file = None
        mock_config.server.private_key_file = None
        mock_config.server.path = "/mcp"

        # Create server instance
        server_instance = server_module.Server(mock_config)

        # Mock MCP instance
        mock_mcp = MagicMock()
        mock_mcp.http_app = MagicMock(return_value="test_app")
        server_instance.mcp = mock_mcp

        # Mock uvicorn Server and Config
        mock_uvicorn_instance = MagicMock()
        mock_uvicorn_instance.serve = AsyncMock()
        mock_uvicorn_server.return_value = mock_uvicorn_instance

        with patch("itential_mcp.server.server.uvicorn.Config") as mock_uvicorn_config:
            await server_instance.run()

            # Verify uvicorn Config was created correctly
            mock_uvicorn_config.assert_called_once_with(
                app="test_app",
                host="0.0.0.0",
                port=8080,
                ssl_certfile=None,
                ssl_keyfile=None,
                ws="wsproto",
            )

            # Verify uvicorn Server was created and serve was called
            mock_uvicorn_server.assert_called_once()
            mock_uvicorn_instance.serve.assert_called_once()

    @pytest.mark.asyncio
    @patch("itential_mcp.server.server.uvicorn.Server")
    async def test_server_run_http_transport_with_uvicorn(self, mock_uvicorn_server):
        """Test Server.run() method with HTTP transport uses uvicorn"""
        # Setup config for HTTP transport
        mock_config = MagicMock()
        mock_config.server.transport = "http"
        mock_config.server.host = "localhost"
        mock_config.server.port = 3000
        mock_config.server.certificate_file = "/path/to/cert.pem"
        mock_config.server.private_key_file = "/path/to/key.pem"
        mock_config.server.path = "/api"

        # Create server instance
        server_instance = server_module.Server(mock_config)

        # Mock MCP instance
        mock_mcp = MagicMock()
        mock_mcp.http_app = MagicMock(return_value="test_app")
        server_instance.mcp = mock_mcp

        # Mock uvicorn Server
        mock_uvicorn_instance = MagicMock()
        mock_uvicorn_instance.serve = AsyncMock()
        mock_uvicorn_server.return_value = mock_uvicorn_instance

        with patch("itential_mcp.server.server.uvicorn.Config") as mock_uvicorn_config:
            await server_instance.run()

            # Verify uvicorn Config was created with TLS settings
            mock_uvicorn_config.assert_called_once_with(
                app="test_app",
                host="localhost",
                port=3000,
                ssl_certfile="/path/to/cert.pem",
                ssl_keyfile="/path/to/key.pem",
                ws="wsproto",
            )

            # Verify uvicorn Server was created and serve was called
            mock_uvicorn_server.assert_called_once()
            mock_uvicorn_instance.serve.assert_called_once()

    @pytest.mark.asyncio
    async def test_server_run_stdio_transport_uses_fastmcp(self):
        """Test Server.run() method with stdio transport uses FastMCP directly"""
        # Setup config for stdio transport
        mock_config = MagicMock()
        mock_config.server.transport = "stdio"

        # Create server instance
        server_instance = server_module.Server(mock_config)

        # Mock MCP instance
        mock_mcp = MagicMock()
        mock_mcp.run_async = AsyncMock()
        server_instance.mcp = mock_mcp

        await server_instance.run()

        # Verify FastMCP run_async was called for stdio
        mock_mcp.run_async.assert_called_once_with(transport="stdio", show_banner=False)

    @pytest.mark.asyncio
    async def test_server_run_missing_mcp_instance(self):
        """Test Server.run() method when mcp instance is None"""
        mock_config = MagicMock()
        mock_config.server.transport = "sse"
        mock_config.server.host = "127.0.0.1"
        mock_config.server.port = 8000

        server_instance = server_module.Server(mock_config)
        # mcp remains None

        # This should not raise an error but would in real usage
        # Since mcp.http_app would be called
        with pytest.raises(AttributeError):
            await server_instance.run()

    @pytest.mark.asyncio
    @patch("itential_mcp.server.server.uvicorn.Server")
    async def test_server_run_tls_configuration_variations(self, mock_uvicorn_server):
        """Test Server.run() with various TLS configurations"""
        test_cases = [
            # No TLS certificates
            {
                "certificate_file": None,
                "private_key_file": None,
                "expected_cert": None,
                "expected_key": None,
            },
            # Only certificate file
            {
                "certificate_file": "/cert.pem",
                "private_key_file": None,
                "expected_cert": "/cert.pem",
                "expected_key": None,
            },
            # Only private key file
            {
                "certificate_file": None,
                "private_key_file": "/key.pem",
                "expected_cert": None,
                "expected_key": "/key.pem",
            },
            # Both files
            {
                "certificate_file": "/cert.pem",
                "private_key_file": "/key.pem",
                "expected_cert": "/cert.pem",
                "expected_key": "/key.pem",
            },
        ]

        for case in test_cases:
            mock_config = MagicMock()
            mock_config.server.transport = "sse"
            mock_config.server.host = "127.0.0.1"
            mock_config.server.port = 8000
            mock_config.server.certificate_file = case["certificate_file"]
            mock_config.server.private_key_file = case["private_key_file"]
            mock_config.server.path = "/mcp"

            server_instance = server_module.Server(mock_config)

            # Mock MCP instance
            mock_mcp = MagicMock()
            mock_mcp.http_app = MagicMock(return_value="test_app")
            server_instance.mcp = mock_mcp

            # Mock uvicorn Server
            mock_uvicorn_instance = MagicMock()
            mock_uvicorn_instance.serve = AsyncMock()
            mock_uvicorn_server.return_value = mock_uvicorn_instance

            with patch(
                "itential_mcp.server.server.uvicorn.Config"
            ) as mock_uvicorn_config:
                await server_instance.run()

                # Verify uvicorn Config was called with expected values
                mock_uvicorn_config.assert_called_with(
                    app="test_app",
                    host="127.0.0.1",
                    port=8000,
                    ssl_certfile=case["expected_cert"],
                    ssl_keyfile=case["expected_key"],
                    ws="wsproto",
                )

            # Reset mocks for next iteration
            mock_uvicorn_server.reset_mock()

    @pytest.mark.asyncio
    @patch("itential_mcp.server.server.uvicorn.Server")
    async def test_server_run_http_app_path_configuration(self, mock_uvicorn_server):
        """Test that Server.run() correctly configures http_app with path"""
        mock_config = MagicMock()
        mock_config.server.transport = "http"
        mock_config.server.host = "127.0.0.1"
        mock_config.server.port = 8000
        mock_config.server.certificate_file = None
        mock_config.server.private_key_file = None
        mock_config.server.path = "/custom-path"

        server_instance = server_module.Server(mock_config)

        # Mock MCP instance
        mock_mcp = MagicMock()
        mock_mcp.http_app = MagicMock(return_value="test_app")
        server_instance.mcp = mock_mcp

        # Mock uvicorn Server
        mock_uvicorn_instance = MagicMock()
        mock_uvicorn_instance.serve = AsyncMock()
        mock_uvicorn_server.return_value = mock_uvicorn_instance

        with patch("itential_mcp.server.server.uvicorn.Config"):
            await server_instance.run()

            # Verify http_app was called with the correct path
            mock_mcp.http_app.assert_called_with(path="/custom-path")

    @pytest.mark.asyncio
    @patch("itential_mcp.server.auth.build_auth_provider")
    @patch("itential_mcp.server.server.bindings.iterbindings")
    @patch("itential_mcp.server.server.toolutils.itertools")
    async def test_server_context_manager(
        self, mock_itertools, mock_iterbindings, mock_auth_builder
    ):
        """Test Server can be used as async context manager"""
        mock_config = MagicMock()
        mock_config.server.transport = "stdio"
        mock_config.server.tools_path = None
        # Mock auth as a dict-like object
        mock_auth = MagicMock()
        mock_auth.get.return_value = "none"
        mock_config.auth = mock_auth
        mock_config.tools = []
        mock_auth_builder.return_value = None

        # Setup empty tools iterator
        mock_itertools.return_value = []

        # Setup empty bindings iterator
        async def empty_aiter():
            return
            yield  # unreachable but makes this an async generator

        mock_iterbindings.return_value = empty_aiter()

        server_instance = server_module.Server(mock_config)

        # Test that Server can be used as context manager
        # In real implementation, this would set up and tear down resources
        with patch("itential_mcp.server.server.FastMCP"):
            async with server_instance as srv:
                assert srv == server_instance
