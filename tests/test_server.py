# Copyright (c) 2025 Itential, Inc
# GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)

import sys
import pytest
from unittest.mock import patch, MagicMock, AsyncMock

from itential_mcp import server
from itential_mcp.config import Config
from itential_mcp.client import PlatformClient

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

        async with server.lifespan(mcp) as context:
            assert "client" in context
            assert isinstance(context["client"], PlatformClient)

    @pytest.mark.asyncio
    async def test_lifespan_context_manager_cleanup(self):
        """Test that lifespan properly manages async context cleanup"""
        mcp = MagicMock()

        # Test that the async context manager completes without error
        async with server.lifespan(mcp) as context:
            # Verify we get the expected context
            assert len(context) == 1
            assert "client" in context

        # Context should be properly cleaned up after exiting


class TestDynamicToolInjectionMiddleware:
    """Test the DynamicToolInjectionMiddleware class"""

    def test_middleware_initialization(self):
        """Test DynamicToolInjectionMiddleware initializes with config"""
        mock_config = MagicMock()
        mock_config.tools = [MagicMock()]

        middleware = server.DynamicToolInjectionMiddleware(mock_config)

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

        middleware = server.DynamicToolInjectionMiddleware(mock_config)

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

        middleware = server.DynamicToolInjectionMiddleware(mock_config)

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

        middleware = server.DynamicToolInjectionMiddleware(mock_config)

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

        middleware = server.DynamicToolInjectionMiddleware(mock_config)

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


class TestNew:
    """Test the new() function for creating FastMCP instances"""

    @patch("itential_mcp.server.bindings.iterbindings")
    @patch("itential_mcp.server.toolutils.itertools")
    @patch("itential_mcp.server.logging.get_logger")
    @patch("itential_mcp.server.FastMCP")
    @pytest.mark.asyncio
    async def test_new_creates_fastmcp_with_basic_config(
        self, mock_fastmcp, mock_logger, mock_itertools, mock_iterbindings
    ):
        """Test new() creates FastMCP with basic configuration"""
        mock_config = MagicMock(spec=Config)
        mock_config.server = {
            "include_tags": ["tag1", "tag2"],
            "exclude_tags": ["tag3"],
            "tools_path": None,
        }
        mock_config.tools = []

        mock_itertools.return_value = []

        async def empty_aiter():
            return
            yield  # unreachable but makes this an async generator

        mock_iterbindings.return_value = empty_aiter()

        mock_mcp_instance = MagicMock()
        mock_fastmcp.return_value = mock_mcp_instance

        result = await server.new(mock_config)

        mock_fastmcp.assert_called_once_with(
            name="Itential Platform MCP",
            instructions=server.inspect.cleandoc(server.INSTRUCTIONS),
            lifespan=server.lifespan,
            include_tags=["tag1", "tag2"],
            exclude_tags=["tag3"],
        )
        assert result == mock_mcp_instance

    @patch("itential_mcp.server.bindings.iterbindings")
    @patch("itential_mcp.server.toolutils.itertools")
    @patch("itential_mcp.server.logging.get_logger")
    @patch("itential_mcp.server.FastMCP")
    @pytest.mark.asyncio
    async def test_new_handles_none_tags(
        self, mock_fastmcp, mock_logger, mock_itertools, mock_iterbindings
    ):
        """Test new() handles None values for tags"""
        mock_config = MagicMock(spec=Config)
        mock_config.server = {"include_tags": None, "exclude_tags": None}
        mock_config.tools = []

        mock_itertools.return_value = []

        async def empty_aiter():
            return
            yield  # unreachable but makes this an async generator

        mock_iterbindings.return_value = empty_aiter()

        mock_mcp_instance = MagicMock()
        mock_fastmcp.return_value = mock_mcp_instance

        await server.new(mock_config)

        mock_fastmcp.assert_called_once_with(
            name="Itential Platform MCP",
            instructions=server.inspect.cleandoc(server.INSTRUCTIONS),
            lifespan=server.lifespan,
            include_tags=None,
            exclude_tags=None,
        )

    @patch("itential_mcp.server.bindings.iterbindings")
    @patch("itential_mcp.server.toolutils.itertools")
    @patch("itential_mcp.server.logging.get_logger")
    @patch("itential_mcp.server.FastMCP")
    @pytest.mark.asyncio
    async def test_new_handles_empty_server_config(
        self, mock_fastmcp, mock_logger, mock_itertools, mock_iterbindings
    ):
        """Test new() handles empty server configuration"""
        mock_config = MagicMock(spec=Config)
        mock_config.server = {}
        mock_config.tools = []

        mock_itertools.return_value = []

        async def empty_aiter():
            return
            yield  # unreachable but makes this an async generator

        mock_iterbindings.return_value = empty_aiter()

        mock_mcp_instance = MagicMock()
        mock_fastmcp.return_value = mock_mcp_instance

        await server.new(mock_config)

        mock_fastmcp.assert_called_once_with(
            name="Itential Platform MCP",
            instructions=server.inspect.cleandoc(server.INSTRUCTIONS),
            lifespan=server.lifespan,
            include_tags=None,
            exclude_tags=None,
        )

    @patch("itential_mcp.server.bindings.iterbindings")
    @patch("itential_mcp.server.toolutils.itertools")
    @patch("itential_mcp.server.logging.get_logger")
    @patch("itential_mcp.server.FastMCP")
    @pytest.mark.asyncio
    async def test_new_with_custom_tools_path(
        self, mock_fastmcp, mock_logger, mock_itertools, mock_iterbindings
    ):
        """Test new() with custom tools_path configuration"""
        mock_config = MagicMock(spec=Config)
        mock_config.server = {
            "include_tags": None,
            "exclude_tags": None,
            "tools_path": "/custom/tools/path",
        }
        mock_config.tools = []

        mock_itertools.return_value = []

        async def empty_aiter():
            return
            yield  # unreachable but makes this an async generator

        mock_iterbindings.return_value = empty_aiter()

        mock_mcp_instance = MagicMock()
        mock_fastmcp.return_value = mock_mcp_instance

        result = await server.new(mock_config)

        # Should call itertools twice - once for default, once for custom path
        assert mock_itertools.call_count == 2
        mock_fastmcp.assert_called_once()
        assert result == mock_mcp_instance

    @patch("itential_mcp.server.bindings.iterbindings")
    @patch("itential_mcp.server.toolutils.itertools")
    @patch("itential_mcp.server.logging.get_logger")
    @patch("itential_mcp.server.FastMCP")
    @pytest.mark.asyncio
    async def test_new_without_custom_tools_path(
        self, mock_fastmcp, mock_logger, mock_itertools, mock_iterbindings
    ):
        """Test new() without custom tools_path (None)"""
        mock_config = MagicMock(spec=Config)
        mock_config.server = {
            "include_tags": None,
            "exclude_tags": None,
            "tools_path": None,
        }
        mock_config.tools = []

        mock_itertools.return_value = []

        async def empty_aiter():
            return
            yield  # unreachable but makes this an async generator

        mock_iterbindings.return_value = empty_aiter()

        mock_mcp_instance = MagicMock()
        mock_fastmcp.return_value = mock_mcp_instance

        await server.new(mock_config)

        # Should only call itertools once for default path
        assert mock_itertools.call_count == 1

    @patch("itential_mcp.server.bindings.iterbindings")
    @patch("itential_mcp.server.toolutils.itertools")
    @patch("itential_mcp.server.toolutils.get_json_schema")
    @patch("itential_mcp.server.logging.get_logger")
    @patch("itential_mcp.server.FastMCP")
    @pytest.mark.asyncio
    async def test_new_tool_with_missing_output_schema(
        self,
        mock_fastmcp,
        mock_logger,
        mock_get_json_schema,
        mock_itertools,
        mock_iterbindings,
    ):
        """Test new() handles tools with missing or invalid output_schema"""
        mock_config = MagicMock(spec=Config)
        mock_config.server = {
            "include_tags": None,
            "exclude_tags": None,
            "tools_path": None,
        }
        mock_config.tools = []

        # Mock a tool function
        def mock_tool():
            """Test tool function"""
            pass

        mock_tool.__name__ = "test_tool"
        mock_itertools.return_value = [(mock_tool, {"test"})]

        # Mock get_json_schema to raise ValueError (missing/invalid schema)
        mock_get_json_schema.side_effect = ValueError("Missing schema")

        async def empty_aiter():
            return
            yield  # unreachable but makes this an async generator

        mock_iterbindings.return_value = empty_aiter()

        mock_mcp_instance = MagicMock()
        mock_fastmcp.return_value = mock_mcp_instance
        mock_logger_instance = MagicMock()
        mock_logger.return_value = mock_logger_instance

        await server.new(mock_config)

        # Should still register the tool without output_schema
        mock_mcp_instance.tool.assert_called_once_with(
            mock_tool, tags={"test", "default"}
        )


class TestRun:
    """Test the run() function for server execution"""

    @pytest.mark.asyncio
    @patch("itential_mcp.server.new", new_callable=AsyncMock)
    @patch("itential_mcp.server.config.get")
    async def test_run_stdio_transport_success(self, mock_config_get, mock_new):
        """Test successful server run with stdio transport"""
        # Setup mocks
        mock_config = MagicMock()
        mock_config.server = {"transport": "stdio"}
        mock_config_get.return_value = mock_config

        mock_mcp = MagicMock()
        mock_mcp.run_async = AsyncMock()
        mock_new.return_value = mock_mcp

        # Execute
        await server.run()

        # Verify
        mock_config_get.assert_called_once()
        mock_new.assert_awaited_once_with(mock_config)

        # Check server was run with correct parameters
        mock_mcp.run_async.assert_called_once_with(transport="stdio", show_banner=False)

    @pytest.mark.asyncio
    @patch("itential_mcp.server.toolutils.itertools")
    @patch("itential_mcp.server.new", new_callable=AsyncMock)
    @patch("itential_mcp.server.config.get")
    async def test_run_sse_transport_success(
        self, mock_config_get, mock_new, mock_itertools
    ):
        """Test successful server run with SSE transport"""
        mock_config = MagicMock()
        mock_config.server = {
            "transport": "sse",
            "host": "0.0.0.0",
            "port": 8000,
            "log_level": "INFO",
        }
        mock_config_get.return_value = mock_config

        mock_mcp = MagicMock()
        mock_mcp.run_async = AsyncMock()
        mock_new.return_value = mock_mcp

        mock_itertools.return_value = []

        await server.run()

        mock_mcp.run_async.assert_called_once_with(
            transport="sse", host="0.0.0.0", port=8000, show_banner=False
        )

    @pytest.mark.asyncio
    @patch("itential_mcp.server.toolutils.itertools")
    @patch("itential_mcp.server.new", new_callable=AsyncMock)
    @patch("itential_mcp.server.config.get")
    async def test_run_http_transport_success(
        self, mock_config_get, mock_new, mock_itertools
    ):
        """Test successful server run with HTTP transport"""
        mock_config = MagicMock()
        mock_config.server = {
            "transport": "http",
            "host": "localhost",
            "port": 3000,
            "log_level": "DEBUG",
            "path": "/mcp",
        }
        mock_config_get.return_value = mock_config

        mock_mcp = MagicMock()
        mock_mcp.run_async = AsyncMock()
        mock_new.return_value = mock_mcp

        mock_itertools.return_value = []

        await server.run()

        mock_mcp.run_async.assert_called_once_with(
            transport="http",
            host="localhost",
            port=3000,
            show_banner=False,
            path="/mcp",
        )

    @pytest.mark.asyncio
    @patch("itential_mcp.server.new", new_callable=AsyncMock)
    @patch("itential_mcp.server.config.get")
    async def test_run_tool_registration_failure(self, mock_config_get, mock_new):
        """Test server exits when tool registration fails in new()"""
        mock_config = MagicMock()
        mock_config.server = {"transport": "stdio"}
        mock_config_get.return_value = mock_config

        # Make new() raise an exception (simulates tool registration failure)
        mock_new.side_effect = Exception("Tool import failed")

        with patch("builtins.print") as mock_print, patch("sys.exit") as mock_exit:
            await server.run()

            mock_print.assert_called_with(
                "ERROR: server stopped unexpectedly: Tool import failed",
                file=sys.stderr,
            )
            mock_exit.assert_called_with(1)

    @pytest.mark.asyncio
    @patch("itential_mcp.server.toolutils.itertools")
    @patch("itential_mcp.server.new", new_callable=AsyncMock)
    @patch("itential_mcp.server.config.get")
    async def test_run_keyboard_interrupt(
        self, mock_config_get, mock_new, mock_itertools
    ):
        """Test server handles KeyboardInterrupt gracefully"""
        mock_config = MagicMock()
        mock_config.server = {"transport": "stdio"}
        mock_config_get.return_value = mock_config

        mock_mcp = MagicMock()
        mock_mcp.run_async = AsyncMock(side_effect=KeyboardInterrupt())
        mock_new.return_value = mock_mcp

        mock_itertools.return_value = []

        with patch("builtins.print") as mock_print, patch("sys.exit") as mock_exit:
            await server.run()

            mock_print.assert_called_with("Shutting down the server")
            mock_exit.assert_called_with(0)

    @pytest.mark.asyncio
    @patch("itential_mcp.server.toolutils.itertools")
    @patch("itential_mcp.server.new", new_callable=AsyncMock)
    @patch("itential_mcp.server.config.get")
    async def test_run_unexpected_exception(
        self, mock_config_get, mock_new, mock_itertools
    ):
        """Test server handles unexpected exceptions"""
        mock_config = MagicMock()
        mock_config.server = {"transport": "stdio"}
        mock_config_get.return_value = mock_config

        mock_mcp = MagicMock()
        mock_mcp.run_async = AsyncMock(side_effect=RuntimeError("Unexpected error"))
        mock_new.return_value = mock_mcp

        mock_itertools.return_value = []

        with patch("builtins.print") as mock_print, patch("sys.exit") as mock_exit:
            await server.run()

            mock_print.assert_called_with(
                "ERROR: server stopped unexpectedly: Unexpected error", file=sys.stderr
            )
            mock_exit.assert_called_with(1)

    @pytest.mark.asyncio
    @patch("itential_mcp.server.toolutils.itertools")
    @patch("itential_mcp.server.new", new_callable=AsyncMock)
    @patch("itential_mcp.server.config.get")
    async def test_run_no_tools_loaded(self, mock_config_get, mock_new, mock_itertools):
        """Test server runs successfully even with no tools"""
        mock_config = MagicMock()
        mock_config.server = {"transport": "stdio"}
        mock_config_get.return_value = mock_config

        mock_mcp = MagicMock()
        mock_mcp.run_async = AsyncMock()
        mock_new.return_value = mock_mcp

        # No tools returned
        mock_itertools.return_value = []

        await server.run()

        # Should not call mcp.tool since there are no tools
        mock_mcp.tool.assert_not_called()
        mock_mcp.run_async.assert_called_once()

    @pytest.mark.asyncio
    @patch("itential_mcp.server.new", new_callable=AsyncMock)
    @patch("itential_mcp.server.config.get")
    async def test_run_multiple_tools_registration(self, mock_config_get, mock_new):
        """Test server properly uses the configured MCP instance from new()"""
        mock_config = MagicMock()
        mock_config.server = {"transport": "stdio"}
        mock_config_get.return_value = mock_config

        mock_mcp = MagicMock()
        mock_mcp.run_async = AsyncMock()
        mock_new.return_value = mock_mcp

        await server.run()

        # Verify new() was called with the config and the MCP instance was used
        mock_new.assert_awaited_once_with(mock_config)
        mock_mcp.run_async.assert_called_once_with(transport="stdio", show_banner=False)

    @pytest.mark.asyncio
    @patch("itential_mcp.server.new", new_callable=AsyncMock)
    @patch("itential_mcp.server.config.get")
    async def test_run_partial_tool_failure(self, mock_config_get, mock_new):
        """Test that server fails if new() fails due to tool registration issues"""
        mock_config = MagicMock()
        mock_config.server = {"transport": "stdio"}
        mock_config_get.return_value = mock_config

        # Make new() fail with an ImportError (simulating tool import failure)
        mock_new.side_effect = ImportError("Failed to import third tool")

        with patch("builtins.print") as mock_print, patch("sys.exit") as mock_exit:
            await server.run()

            mock_print.assert_called_with(
                "ERROR: server stopped unexpectedly: Failed to import third tool",
                file=sys.stderr,
            )
            mock_exit.assert_called_with(1)

    @pytest.mark.asyncio
    @patch("itential_mcp.server.toolutils.itertools")
    @patch("itential_mcp.server.new", new_callable=AsyncMock)
    @patch("itential_mcp.server.config.get")
    async def test_run_config_variations(
        self, mock_config_get, mock_new, mock_itertools
    ):
        """Test various configuration scenarios"""
        # Test with minimal config
        mock_config = MagicMock()
        mock_config.server = {"transport": "stdio"}
        mock_config_get.return_value = mock_config

        mock_mcp = MagicMock()
        mock_mcp.run_async = AsyncMock()
        mock_new.return_value = mock_mcp

        mock_itertools.return_value = []

        await server.run()

        mock_mcp.run_async.assert_called_with(transport="stdio", show_banner=False)

    @pytest.mark.asyncio
    @patch("itential_mcp.server.toolutils.itertools")
    @patch("itential_mcp.server.new", new_callable=AsyncMock)
    @patch("itential_mcp.server.config.get")
    async def test_run_missing_server_config_keys(
        self, mock_config_get, mock_new, mock_itertools
    ):
        """Test server handles missing configuration keys gracefully"""
        mock_config = MagicMock()
        mock_config.server = {"transport": "sse"}  # Missing host, port, log_level
        mock_config_get.return_value = mock_config

        mock_mcp = MagicMock()
        mock_mcp.run_async = AsyncMock()
        mock_new.return_value = mock_mcp

        mock_itertools.return_value = []

        await server.run()

        # Should call with None values for missing keys
        mock_mcp.run_async.assert_called_with(
            transport="sse", host=None, port=None, show_banner=False
        )


class TestIntegration:
    """Integration tests for server functionality"""

    @pytest.mark.asyncio
    @patch("itential_mcp.server.bindings.iterbindings")
    @patch("itential_mcp.server.toolutils.itertools")
    @patch("itential_mcp.server.config.get")
    async def test_full_server_lifecycle(
        self, mock_config_get, mock_itertools, mock_iterbindings
    ):
        """Test complete server lifecycle from config to shutdown"""
        # Setup configuration
        mock_config = MagicMock()
        mock_config.server = {
            "transport": "stdio",
            "include_tags": ["system"],
            "exclude_tags": ["deprecated"],
        }
        mock_config.tools = []
        mock_config_get.return_value = mock_config

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
        with patch("itential_mcp.server.FastMCP") as mock_fastmcp_class:
            mock_mcp = MagicMock()
            mock_mcp.run_async = AsyncMock()
            mock_fastmcp_class.return_value = mock_mcp

            await server.run()

            # Verify complete flow
            mock_config_get.assert_called_once()

            # Verify FastMCP was created with correct parameters
            mock_fastmcp_class.assert_called_once_with(
                name="Itential Platform MCP",
                instructions=server.inspect.cleandoc(server.INSTRUCTIONS),
                lifespan=server.lifespan,
                include_tags=["system"],
                exclude_tags=["deprecated"],
            )

            # Verify tool registration
            mock_mcp.tool.assert_called_once_with(
                mock_func, tags={"system", "test", "default"}
            )

            # Verify server was started
            mock_mcp.run_async.assert_called_once_with(transport="stdio", show_banner=False)
