# Copyright (c) 2025 Itential, Inc
# GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

import json
import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from io import StringIO
from dataclasses import dataclass
from typing import Any

from itential_mcp.runtime import runner


@dataclass
class MockCallToolResult:
    """Mock version of CallToolResult for testing"""

    content: list[Any]
    structured_content: dict[str, Any] | None = None
    data: Any = None
    is_error: bool = False


class TestRun:
    """Test cases for the run function"""

    @pytest.mark.asyncio
    @patch("sys.stdout", new_callable=StringIO)
    @patch("itential_mcp.runtime.runner.Client")
    @patch("itential_mcp.runtime.runner.Server")
    @patch("itential_mcp.runtime.runner.config.get")
    async def test_run_basic_tool_no_params(
        self, mock_config_get, mock_server_class, mock_client_class, mock_stdout
    ):
        """Test running a tool without parameters"""
        # Setup mocks
        mock_config = MagicMock()
        mock_config_get.return_value = mock_config

        # Setup server instance mock
        mock_server_instance = MagicMock()
        mock_server_instance.mcp = MagicMock()
        mock_server_instance.__aenter__ = AsyncMock(return_value=mock_server_instance)
        mock_server_instance.__aexit__ = AsyncMock(return_value=None)
        mock_server_class.return_value = mock_server_instance

        mock_client = AsyncMock()
        mock_client.ping.return_value = True

        # Mock tool list response
        mock_tool = MagicMock()
        mock_tool.name = "test_tool"
        mock_tool.inputSchema = {
            "properties": {"param1": {"type": "string"}},
            "required": [],
        }

        mock_list_response = MagicMock()
        mock_list_response.tools = [mock_tool]
        mock_client.list_tools_mcp.return_value = mock_list_response

        # Mock tool execution response
        mock_result_content = MagicMock()
        mock_result_content.text = json.dumps({"result": "success"})
        mock_result = MockCallToolResult(content=[mock_result_content])
        mock_client.call_tool.return_value = mock_result

        mock_client_class.return_value.__aenter__.return_value = mock_client
        mock_client_class.return_value.__aexit__.return_value = None

        # Execute
        await runner.run("test_tool")

        # Verify
        mock_config_get.assert_called_once()
        mock_server_class.assert_called_once_with(mock_config)
        mock_client.ping.assert_called_once()
        mock_client.list_tools_mcp.assert_called_once()
        mock_client.call_tool.assert_called_once_with("test_tool", arguments=None)

        # Check stdout output
        output = mock_stdout.getvalue()
        assert '"result": "success"' in output

    @pytest.mark.asyncio
    @patch("sys.stdout", new_callable=StringIO)
    @patch("itential_mcp.runtime.runner.Client")
    @patch("itential_mcp.runtime.runner.Server")
    @patch("itential_mcp.runtime.runner.config.get")
    async def test_run_tool_with_params(
        self, mock_config_get, mock_server_class, mock_client_class, mock_stdout
    ):
        """Test running a tool with parameters"""
        # Setup mocks
        mock_config = MagicMock()
        mock_config_get.return_value = mock_config

        # Setup server instance mock
        mock_server_instance = MagicMock()
        mock_server_instance.mcp = MagicMock()
        mock_server_instance.__aenter__ = AsyncMock(return_value=mock_server_instance)
        mock_server_instance.__aexit__ = AsyncMock(return_value=None)
        mock_server_class.return_value = mock_server_instance

        mock_client = AsyncMock()
        mock_client.ping.return_value = True

        # Mock tool list response
        mock_tool = MagicMock()
        mock_tool.name = "test_tool"
        mock_tool.inputSchema = {
            "properties": {"param1": {"type": "string"}, "param2": {"type": "integer"}},
            "required": ["param1"],
        }

        mock_list_response = MagicMock()
        mock_list_response.tools = [mock_tool]
        mock_client.list_tools_mcp.return_value = mock_list_response

        # Mock tool execution response
        mock_result_content = MagicMock()
        mock_result_content.text = json.dumps(
            {"result": "success", "param1_value": "test"}
        )
        mock_result = MockCallToolResult(content=[mock_result_content])
        mock_client.call_tool.return_value = mock_result

        mock_client_class.return_value.__aenter__.return_value = mock_client
        mock_client_class.return_value.__aexit__.return_value = None

        # Execute with parameters
        params_json = '{"param1": "test", "param2": 42}'
        await runner.run("test_tool", params_json)

        # Verify
        expected_arguments = {"param1": "test", "param2": 42}
        mock_client.call_tool.assert_called_once_with(
            "test_tool", arguments=expected_arguments
        )

        # Check stdout output
        output = mock_stdout.getvalue()
        assert '"result": "success"' in output
        assert '"param1_value": "test"' in output

    @pytest.mark.asyncio
    @patch("itential_mcp.runtime.runner.Client")
    @patch("itential_mcp.runtime.runner.Server")
    @patch("itential_mcp.runtime.runner.config.get")
    async def test_run_server_ping_failure(
        self, mock_config_get, mock_server_class, mock_client_class
    ):
        """Test failure when server ping fails"""
        # Setup mocks
        mock_config = MagicMock()
        mock_config_get.return_value = mock_config

        # Setup server instance mock
        mock_server_instance = MagicMock()
        mock_server_instance.mcp = MagicMock()
        mock_server_instance.__aenter__ = AsyncMock(return_value=mock_server_instance)
        mock_server_instance.__aexit__ = AsyncMock(return_value=None)
        mock_server_class.return_value = mock_server_instance

        mock_client = AsyncMock()
        mock_client.ping.return_value = False

        mock_client_class.return_value.__aenter__.return_value = mock_client
        mock_client_class.return_value.__aexit__.return_value = None

        # Execute and verify exception
        with pytest.raises(ValueError, match="ERROR: cannot reach the server"):
            await runner.run("test_tool")

        mock_client.ping.assert_called_once()
        # Should not proceed to list tools
        mock_client.list_tools_mcp.assert_not_called()

    @pytest.mark.asyncio
    @patch("itential_mcp.runtime.runner.Client")
    @patch("itential_mcp.runtime.runner.Server")
    @patch("itential_mcp.runtime.runner.config.get")
    async def test_run_invalid_tool(
        self, mock_config_get, mock_server_class, mock_client_class
    ):
        """Test running an invalid/non-existent tool"""
        # Setup mocks
        mock_config = MagicMock()
        mock_config_get.return_value = mock_config

        # Setup server instance mock
        mock_server_instance = MagicMock()
        mock_server_instance.mcp = MagicMock()
        mock_server_instance.__aenter__ = AsyncMock(return_value=mock_server_instance)
        mock_server_instance.__aexit__ = AsyncMock(return_value=None)
        mock_server_class.return_value = mock_server_instance

        mock_client = AsyncMock()
        mock_client.ping.return_value = True

        # Mock tool list response with different tool
        mock_tool = MagicMock()
        mock_tool.name = "other_tool"
        mock_tool.inputSchema = {"properties": {}, "required": []}

        mock_list_response = MagicMock()
        mock_list_response.tools = [mock_tool]
        mock_client.list_tools_mcp.return_value = mock_list_response

        mock_client_class.return_value.__aenter__.return_value = mock_client
        mock_client_class.return_value.__aexit__.return_value = None

        # Execute and verify exception
        with pytest.raises(ValueError, match="invalid tool: nonexistent_tool"):
            await runner.run("nonexistent_tool")

        mock_client.list_tools_mcp.assert_called_once()
        # Should not proceed to call tool
        mock_client.call_tool.assert_not_called()

    @pytest.mark.asyncio
    @patch("itential_mcp.runtime.runner.Client")
    @patch("itential_mcp.runtime.runner.Server")
    @patch("itential_mcp.runtime.runner.config.get")
    async def test_run_missing_required_params(
        self, mock_config_get, mock_server_class, mock_client_class
    ):
        """Test running a tool with missing required parameters"""
        # Setup mocks
        mock_config = MagicMock()
        mock_config_get.return_value = mock_config

        # Setup server instance mock
        mock_server_instance = MagicMock()
        mock_server_instance.mcp = MagicMock()
        mock_server_instance.__aenter__ = AsyncMock(return_value=mock_server_instance)
        mock_server_instance.__aexit__ = AsyncMock(return_value=None)
        mock_server_class.return_value = mock_server_instance

        mock_client = AsyncMock()
        mock_client.ping.return_value = True

        # Mock tool list response with required parameters
        mock_tool = MagicMock()
        mock_tool.name = "test_tool"
        mock_tool.inputSchema = {
            "properties": {
                "required_param": {"type": "string"},
                "optional_param": {"type": "string"},
            },
            "required": ["required_param"],
        }

        mock_list_response = MagicMock()
        mock_list_response.tools = [mock_tool]
        mock_client.list_tools_mcp.return_value = mock_list_response

        mock_client_class.return_value.__aenter__.return_value = mock_client
        mock_client_class.return_value.__aexit__.return_value = None

        # Execute without required parameter and verify exception
        with pytest.raises(
            ValueError, match="missing required property: required_param"
        ):
            await runner.run("test_tool")

        # Execute with incomplete parameters and verify exception
        params_json = '{"optional_param": "test"}'
        with pytest.raises(
            ValueError, match="missing required property: required_param"
        ):
            await runner.run("test_tool", params_json)

        # Should not proceed to call tool
        mock_client.call_tool.assert_not_called()

    @pytest.mark.asyncio
    @patch("itential_mcp.runtime.runner.Client")
    @patch("itential_mcp.runtime.runner.Server")
    @patch("itential_mcp.runtime.runner.config.get")
    async def test_run_invalid_params(
        self, mock_config_get, mock_server_class, mock_client_class
    ):
        """Test running a tool with invalid parameters"""
        # Setup mocks
        mock_config = MagicMock()
        mock_config_get.return_value = mock_config

        # Setup server instance mock
        mock_server_instance = MagicMock()
        mock_server_instance.mcp = MagicMock()
        mock_server_instance.__aenter__ = AsyncMock(return_value=mock_server_instance)
        mock_server_instance.__aexit__ = AsyncMock(return_value=None)
        mock_server_class.return_value = mock_server_instance

        mock_client = AsyncMock()
        mock_client.ping.return_value = True

        # Mock tool list response
        mock_tool = MagicMock()
        mock_tool.name = "test_tool"
        mock_tool.inputSchema = {
            "properties": {"valid_param": {"type": "string"}},
            "required": [],
        }

        mock_list_response = MagicMock()
        mock_list_response.tools = [mock_tool]
        mock_client.list_tools_mcp.return_value = mock_list_response

        mock_client_class.return_value.__aenter__.return_value = mock_client
        mock_client_class.return_value.__aexit__.return_value = None

        # Execute with invalid parameter and verify exception
        params_json = '{"invalid_param": "test"}'
        with pytest.raises(ValueError, match="invalid argument: invalid_param"):
            await runner.run("test_tool", params_json)

        # Should not proceed to call tool
        mock_client.call_tool.assert_not_called()

    @pytest.mark.asyncio
    @patch("sys.stdout", new_callable=StringIO)
    @patch("itential_mcp.runtime.runner.Client")
    @patch("itential_mcp.runtime.runner.Server")
    @patch("itential_mcp.runtime.runner.config.get")
    async def test_run_tool_no_required_params(
        self, mock_config_get, mock_server_class, mock_client_class, mock_stdout
    ):
        """Test running a tool that has no required parameters in schema"""
        # Setup mocks
        mock_config = MagicMock()
        mock_config_get.return_value = mock_config

        # Setup server instance mock
        mock_server_instance = MagicMock()
        mock_server_instance.mcp = MagicMock()
        mock_server_instance.__aenter__ = AsyncMock(return_value=mock_server_instance)
        mock_server_instance.__aexit__ = AsyncMock(return_value=None)
        mock_server_class.return_value = mock_server_instance

        mock_client = AsyncMock()
        mock_client.ping.return_value = True

        # Mock tool list response with no required field (None)
        mock_tool = MagicMock()
        mock_tool.name = "test_tool"
        mock_tool.inputSchema = {
            "properties": {"optional_param": {"type": "string"}},
            "required": None,  # No required parameters
        }

        mock_list_response = MagicMock()
        mock_list_response.tools = [mock_tool]
        mock_client.list_tools_mcp.return_value = mock_list_response

        # Mock tool execution response
        mock_result_content = MagicMock()
        mock_result_content.text = json.dumps({"result": "success"})
        mock_result = MockCallToolResult(content=[mock_result_content])
        mock_client.call_tool.return_value = mock_result

        mock_client_class.return_value.__aenter__.return_value = mock_client
        mock_client_class.return_value.__aexit__.return_value = None

        # Execute
        await runner.run("test_tool")

        # Verify
        mock_client.call_tool.assert_called_once_with("test_tool", arguments=None)

        # Check stdout output
        output = mock_stdout.getvalue()
        assert '"result": "success"' in output

    @pytest.mark.asyncio
    @patch("sys.stdout", new_callable=StringIO)
    @patch("itential_mcp.runtime.runner.Client")
    @patch("itential_mcp.runtime.runner.Server")
    @patch("itential_mcp.runtime.runner.config.get")
    async def test_run_multiple_tools_available(
        self, mock_config_get, mock_server_class, mock_client_class, mock_stdout
    ):
        """Test running a specific tool when multiple tools are available"""
        # Setup mocks
        mock_config = MagicMock()
        mock_config_get.return_value = mock_config

        # Setup server instance mock
        mock_server_instance = MagicMock()
        mock_server_instance.mcp = MagicMock()
        mock_server_instance.__aenter__ = AsyncMock(return_value=mock_server_instance)
        mock_server_instance.__aexit__ = AsyncMock(return_value=None)
        mock_server_class.return_value = mock_server_instance

        mock_client = AsyncMock()
        mock_client.ping.return_value = True

        # Mock multiple tools
        mock_tool1 = MagicMock()
        mock_tool1.name = "tool1"
        mock_tool1.inputSchema = {"properties": {}, "required": []}

        mock_tool2 = MagicMock()
        mock_tool2.name = "tool2"
        mock_tool2.inputSchema = {
            "properties": {"param": {"type": "string"}},
            "required": [],
        }

        mock_list_response = MagicMock()
        mock_list_response.tools = [mock_tool1, mock_tool2]
        mock_client.list_tools_mcp.return_value = mock_list_response

        # Mock tool execution response
        mock_result_content = MagicMock()
        mock_result_content.text = json.dumps({"tool": "tool2", "result": "executed"})
        mock_result = MockCallToolResult(content=[mock_result_content])
        mock_client.call_tool.return_value = mock_result

        mock_client_class.return_value.__aenter__.return_value = mock_client
        mock_client_class.return_value.__aexit__.return_value = None

        # Execute tool2
        await runner.run("tool2")

        # Verify correct tool was called
        mock_client.call_tool.assert_called_once_with("tool2", arguments=None)

        # Check stdout output
        output = mock_stdout.getvalue()
        assert '"tool": "tool2"' in output

    @pytest.mark.asyncio
    @patch("itential_mcp.runtime.runner.Client")
    @patch("itential_mcp.runtime.runner.Server")
    @patch("itential_mcp.runtime.runner.config.get")
    async def test_run_invalid_json_params(
        self, mock_config_get, mock_server_class, mock_client_class
    ):
        """Test running a tool with invalid JSON parameters"""
        # Setup mocks
        mock_config = MagicMock()
        mock_config_get.return_value = mock_config

        # Setup server instance mock
        mock_server_instance = MagicMock()
        mock_server_instance.mcp = MagicMock()
        mock_server_instance.__aenter__ = AsyncMock(return_value=mock_server_instance)
        mock_server_instance.__aexit__ = AsyncMock(return_value=None)
        mock_server_class.return_value = mock_server_instance

        mock_client = AsyncMock()
        mock_client.ping.return_value = True

        # Mock tool list response
        mock_tool = MagicMock()
        mock_tool.name = "test_tool"
        mock_tool.inputSchema = {"properties": {}, "required": []}

        mock_list_response = MagicMock()
        mock_list_response.tools = [mock_tool]
        mock_client.list_tools_mcp.return_value = mock_list_response

        mock_client_class.return_value.__aenter__.return_value = mock_client
        mock_client_class.return_value.__aexit__.return_value = None

        # Execute with invalid JSON and verify exception
        invalid_json = '{"param": invalid}'
        with pytest.raises(json.JSONDecodeError):
            await runner.run("test_tool", invalid_json)

    @pytest.mark.asyncio
    @patch("sys.stdout", new_callable=StringIO)
    @patch("itential_mcp.runtime.runner.Client")
    @patch("itential_mcp.runtime.runner.Server")
    @patch("itential_mcp.runtime.runner.config.get")
    async def test_run_complex_result_formatting(
        self, mock_config_get, mock_server_class, mock_client_class, mock_stdout
    ):
        """Test that complex results are properly formatted in JSON output"""
        # Setup mocks
        mock_config = MagicMock()
        mock_config_get.return_value = mock_config

        # Setup server instance mock
        mock_server_instance = MagicMock()
        mock_server_instance.mcp = MagicMock()
        mock_server_instance.__aenter__ = AsyncMock(return_value=mock_server_instance)
        mock_server_instance.__aexit__ = AsyncMock(return_value=None)
        mock_server_class.return_value = mock_server_instance

        mock_client = AsyncMock()
        mock_client.ping.return_value = True

        # Mock tool list response
        mock_tool = MagicMock()
        mock_tool.name = "test_tool"
        mock_tool.inputSchema = {"properties": {}, "required": []}

        mock_list_response = MagicMock()
        mock_list_response.tools = [mock_tool]
        mock_client.list_tools_mcp.return_value = mock_list_response

        # Mock complex tool execution response
        complex_result = {
            "result": "success",
            "data": {
                "items": [{"id": 1, "name": "item1"}, {"id": 2, "name": "item2"}],
                "metadata": {"total": 2, "page": 1},
            },
        }
        mock_result_content = MagicMock()
        mock_result_content.text = json.dumps(complex_result)
        mock_result = MockCallToolResult(content=[mock_result_content])
        mock_client.call_tool.return_value = mock_result

        mock_client_class.return_value.__aenter__.return_value = mock_client
        mock_client_class.return_value.__aexit__.return_value = None

        # Execute
        await runner.run("test_tool")

        # Verify formatted output
        output = mock_stdout.getvalue()
        assert '"result": "success"' in output
        assert '"total": 2' in output
        assert '"name": "item1"' in output
        # Should have proper indentation (4 spaces)
        assert '    "result": "success"' in output


class TestRunEdgeCases:
    """Test edge cases and error conditions"""

    @pytest.mark.asyncio
    @patch("itential_mcp.runtime.runner.Client")
    @patch("itential_mcp.runtime.runner.Server")
    @patch("itential_mcp.runtime.runner.config.get")
    async def test_run_empty_tool_list(
        self, mock_config_get, mock_server_class, mock_client_class
    ):
        """Test behavior when no tools are available"""
        # Setup mocks
        mock_config = MagicMock()
        mock_config_get.return_value = mock_config

        # Setup server instance mock
        mock_server_instance = MagicMock()
        mock_server_instance.mcp = MagicMock()
        mock_server_instance.__aenter__ = AsyncMock(return_value=mock_server_instance)
        mock_server_instance.__aexit__ = AsyncMock(return_value=None)
        mock_server_class.return_value = mock_server_instance

        mock_client = AsyncMock()
        mock_client.ping.return_value = True

        # Mock empty tool list response
        mock_list_response = MagicMock()
        mock_list_response.tools = []
        mock_client.list_tools_mcp.return_value = mock_list_response

        mock_client_class.return_value.__aenter__.return_value = mock_client
        mock_client_class.return_value.__aexit__.return_value = None

        # Execute and verify exception
        with pytest.raises(ValueError, match="invalid tool: any_tool"):
            await runner.run("any_tool")

    @pytest.mark.asyncio
    @patch("sys.stdout", new_callable=StringIO)
    @patch("itential_mcp.runtime.runner.Client")
    @patch("itential_mcp.runtime.runner.Server")
    @patch("itential_mcp.runtime.runner.config.get")
    async def test_run_empty_params_string(
        self, mock_config_get, mock_server_class, mock_client_class, mock_stdout
    ):
        """Test running a tool with empty parameters string"""
        # Setup mocks
        mock_config = MagicMock()
        mock_config_get.return_value = mock_config

        # Setup server instance mock
        mock_server_instance = MagicMock()
        mock_server_instance.mcp = MagicMock()
        mock_server_instance.__aenter__ = AsyncMock(return_value=mock_server_instance)
        mock_server_instance.__aexit__ = AsyncMock(return_value=None)
        mock_server_class.return_value = mock_server_instance

        mock_client = AsyncMock()
        mock_client.ping.return_value = True

        # Mock tool list response
        mock_tool = MagicMock()
        mock_tool.name = "test_tool"
        mock_tool.inputSchema = {"properties": {}, "required": []}

        mock_list_response = MagicMock()
        mock_list_response.tools = [mock_tool]
        mock_client.list_tools_mcp.return_value = mock_list_response

        # Mock tool execution response
        mock_result_content = MagicMock()
        mock_result_content.text = json.dumps({"result": "success"})
        mock_result = MockCallToolResult(content=[mock_result_content])
        mock_client.call_tool.return_value = mock_result

        mock_client_class.return_value.__aenter__.return_value = mock_client
        mock_client_class.return_value.__aexit__.return_value = None

        # Execute with empty string for params
        await runner.run("test_tool", "")

        # Should still work and pass None as arguments
        mock_client.call_tool.assert_called_once_with("test_tool", arguments=None)


class TestRunIntegration:
    """Integration-style tests for the run function"""

    @pytest.mark.asyncio
    @patch("sys.stdout", new_callable=StringIO)
    @patch("itential_mcp.runtime.runner.Client")
    @patch("itential_mcp.runtime.runner.Server")
    @patch("itential_mcp.runtime.runner.config.get")
    async def test_run_full_workflow(
        self, mock_config_get, mock_server_class, mock_client_class, mock_stdout
    ):
        """Test the complete workflow from start to finish"""
        # Setup mocks
        mock_config = MagicMock()
        mock_config_get.return_value = mock_config

        # Setup server instance mock
        mock_server_instance = MagicMock()
        mock_server_instance.mcp = MagicMock()
        mock_server_instance.__aenter__ = AsyncMock(return_value=mock_server_instance)
        mock_server_instance.__aexit__ = AsyncMock(return_value=None)
        mock_server_class.return_value = mock_server_instance

        mock_client = AsyncMock()
        mock_client.ping.return_value = True

        # Mock realistic tool list response
        mock_tool = MagicMock()
        mock_tool.name = "get_user_info"
        mock_tool.inputSchema = {
            "properties": {
                "user_id": {"type": "string", "description": "User ID to retrieve"},
                "include_details": {
                    "type": "boolean",
                    "description": "Include detailed info",
                },
            },
            "required": ["user_id"],
        }

        mock_list_response = MagicMock()
        mock_list_response.tools = [mock_tool]
        mock_client.list_tools_mcp.return_value = mock_list_response

        # Mock realistic tool execution response
        mock_result_content = MagicMock()
        result_data = {
            "user": {
                "id": "12345",
                "name": "John Doe",
                "email": "john@example.com",
                "details": {"role": "admin", "last_login": "2024-01-15T10:30:00Z"},
            },
            "status": "success",
        }
        mock_result_content.text = json.dumps(result_data)
        mock_result = MockCallToolResult(content=[mock_result_content])
        mock_client.call_tool.return_value = mock_result

        mock_client_class.return_value.__aenter__.return_value = mock_client
        mock_client_class.return_value.__aexit__.return_value = None

        # Execute complete workflow
        params = '{"user_id": "12345", "include_details": true}'
        await runner.run("get_user_info", params)

        # Verify complete flow
        mock_config_get.assert_called_once()
        mock_server_class.assert_called_once_with(mock_config)
        mock_client.ping.assert_called_once()
        mock_client.list_tools_mcp.assert_called_once()

        expected_args = {"user_id": "12345", "include_details": True}
        mock_client.call_tool.assert_called_once_with(
            "get_user_info", arguments=expected_args
        )

        # Verify output formatting
        output = mock_stdout.getvalue()
        assert '"user"' in output
        assert '"name": "John Doe"' in output
        assert '"status": "success"' in output
        assert '"role": "admin"' in output


class TestRunJSONParsing:
    """Test JSON parsing behavior in run function"""

    @pytest.mark.asyncio
    @patch("sys.stdout", new_callable=StringIO)
    @patch("itential_mcp.runtime.runner.Client")
    @patch("itential_mcp.runtime.runner.Server")
    @patch("itential_mcp.runtime.runner.config.get")
    async def test_run_valid_json_response(
        self, mock_config_get, mock_server_class, mock_client_class, mock_stdout
    ):
        """Test that valid JSON response is properly formatted"""
        # Setup mocks
        mock_config = MagicMock()
        mock_config_get.return_value = mock_config

        # Setup server instance mock
        mock_server_instance = MagicMock()
        mock_server_instance.mcp = MagicMock()
        mock_server_instance.__aenter__ = AsyncMock(return_value=mock_server_instance)
        mock_server_instance.__aexit__ = AsyncMock(return_value=None)
        mock_server_class.return_value = mock_server_instance

        mock_client = AsyncMock()
        mock_client.ping.return_value = True

        # Mock tool list response
        mock_tool = MagicMock()
        mock_tool.name = "test_tool"
        mock_tool.inputSchema = {"properties": {}, "required": []}

        mock_list_response = MagicMock()
        mock_list_response.tools = [mock_tool]
        mock_client.list_tools_mcp.return_value = mock_list_response

        # Mock tool execution response with valid JSON
        mock_result_content = MagicMock()
        mock_result_content.text = json.dumps({"status": "ok", "message": "Success"})
        mock_result = MockCallToolResult(content=[mock_result_content])
        mock_client.call_tool.return_value = mock_result

        mock_client_class.return_value.__aenter__.return_value = mock_client
        mock_client_class.return_value.__aexit__.return_value = None

        # Execute
        await runner.run("test_tool")

        # Verify JSON output is formatted with indentation
        output = mock_stdout.getvalue()
        assert '"status": "ok"' in output
        assert '"message": "Success"' in output
        # Should have proper indentation (4 spaces)
        assert '    "status": "ok"' in output

    @pytest.mark.asyncio
    @patch("sys.stdout", new_callable=StringIO)
    @patch("itential_mcp.runtime.runner.Client")
    @patch("itential_mcp.runtime.runner.Server")
    @patch("itential_mcp.runtime.runner.config.get")
    async def test_run_invalid_json_returns_plain_text(
        self, mock_config_get, mock_server_class, mock_client_class, mock_stdout
    ):
        """Test that invalid JSON response returns plain text without error"""
        # Setup mocks
        mock_config = MagicMock()
        mock_config_get.return_value = mock_config

        # Setup server instance mock
        mock_server_instance = MagicMock()
        mock_server_instance.mcp = MagicMock()
        mock_server_instance.__aenter__ = AsyncMock(return_value=mock_server_instance)
        mock_server_instance.__aexit__ = AsyncMock(return_value=None)
        mock_server_class.return_value = mock_server_instance

        mock_client = AsyncMock()
        mock_client.ping.return_value = True

        # Mock tool list response
        mock_tool = MagicMock()
        mock_tool.name = "test_tool"
        mock_tool.inputSchema = {"properties": {}, "required": []}

        mock_list_response = MagicMock()
        mock_list_response.tools = [mock_tool]
        mock_client.list_tools_mcp.return_value = mock_list_response

        # Mock tool execution response with plain text (not valid JSON)
        mock_result_content = MagicMock()
        plain_text_response = "This is a plain text response from the tool"
        mock_result_content.text = plain_text_response
        mock_result = MockCallToolResult(content=[mock_result_content])
        mock_client.call_tool.return_value = mock_result

        mock_client_class.return_value.__aenter__.return_value = mock_client
        mock_client_class.return_value.__aexit__.return_value = None

        # Execute - should not raise an exception
        await runner.run("test_tool")

        # Verify plain text is output without JSON formatting
        output = mock_stdout.getvalue()
        assert plain_text_response in output
        # Should not have JSON indentation markers
        assert "    " not in output or output.strip() == plain_text_response

    @pytest.mark.asyncio
    @patch("sys.stdout", new_callable=StringIO)
    @patch("itential_mcp.runtime.runner.Client")
    @patch("itential_mcp.runtime.runner.Server")
    @patch("itential_mcp.runtime.runner.config.get")
    async def test_run_malformed_json_returns_plain_text(
        self, mock_config_get, mock_server_class, mock_client_class, mock_stdout
    ):
        """Test that malformed JSON response returns plain text gracefully"""
        # Setup mocks
        mock_config = MagicMock()
        mock_config_get.return_value = mock_config

        # Setup server instance mock
        mock_server_instance = MagicMock()
        mock_server_instance.mcp = MagicMock()
        mock_server_instance.__aenter__ = AsyncMock(return_value=mock_server_instance)
        mock_server_instance.__aexit__ = AsyncMock(return_value=None)
        mock_server_class.return_value = mock_server_instance

        mock_client = AsyncMock()
        mock_client.ping.return_value = True

        # Mock tool list response
        mock_tool = MagicMock()
        mock_tool.name = "test_tool"
        mock_tool.inputSchema = {"properties": {}, "required": []}

        mock_list_response = MagicMock()
        mock_list_response.tools = [mock_tool]
        mock_client.list_tools_mcp.return_value = mock_list_response

        # Mock tool execution response with malformed JSON
        mock_result_content = MagicMock()
        malformed_json = '{"status": "ok", "data": incomplete'
        mock_result_content.text = malformed_json
        mock_result = MockCallToolResult(content=[mock_result_content])
        mock_client.call_tool.return_value = mock_result

        mock_client_class.return_value.__aenter__.return_value = mock_client
        mock_client_class.return_value.__aexit__.return_value = None

        # Execute - should not raise an exception
        await runner.run("test_tool")

        # Verify malformed JSON is output as plain text
        output = mock_stdout.getvalue()
        assert malformed_json in output

    @pytest.mark.asyncio
    @patch("sys.stdout", new_callable=StringIO)
    @patch("itential_mcp.runtime.runner.Client")
    @patch("itential_mcp.runtime.runner.Server")
    @patch("itential_mcp.runtime.runner.config.get")
    async def test_run_empty_string_response(
        self, mock_config_get, mock_server_class, mock_client_class, mock_stdout
    ):
        """Test that empty string response is handled gracefully"""
        # Setup mocks
        mock_config = MagicMock()
        mock_config_get.return_value = mock_config

        # Setup server instance mock
        mock_server_instance = MagicMock()
        mock_server_instance.mcp = MagicMock()
        mock_server_instance.__aenter__ = AsyncMock(return_value=mock_server_instance)
        mock_server_instance.__aexit__ = AsyncMock(return_value=None)
        mock_server_class.return_value = mock_server_instance

        mock_client = AsyncMock()
        mock_client.ping.return_value = True

        # Mock tool list response
        mock_tool = MagicMock()
        mock_tool.name = "test_tool"
        mock_tool.inputSchema = {"properties": {}, "required": []}

        mock_list_response = MagicMock()
        mock_list_response.tools = [mock_tool]
        mock_client.list_tools_mcp.return_value = mock_list_response

        # Mock tool execution response with empty string
        mock_result_content = MagicMock()
        mock_result_content.text = ""
        mock_result = MockCallToolResult(content=[mock_result_content])
        mock_client.call_tool.return_value = mock_result

        mock_client_class.return_value.__aenter__.return_value = mock_client
        mock_client_class.return_value.__aexit__.return_value = None

        # Execute - should not raise an exception
        await runner.run("test_tool")

        # Verify empty output
        output = mock_stdout.getvalue()
        # Should just have newlines (from print statement)
        assert output.strip() == ""

    @pytest.mark.asyncio
    @patch("sys.stdout", new_callable=StringIO)
    @patch("itential_mcp.runtime.runner.Client")
    @patch("itential_mcp.runtime.runner.Server")
    @patch("itential_mcp.runtime.runner.config.get")
    async def test_run_numeric_string_response(
        self, mock_config_get, mock_server_class, mock_client_class, mock_stdout
    ):
        """Test that numeric string response returns plain text"""
        # Setup mocks
        mock_config = MagicMock()
        mock_config_get.return_value = mock_config

        # Setup server instance mock
        mock_server_instance = MagicMock()
        mock_server_instance.mcp = MagicMock()
        mock_server_instance.__aenter__ = AsyncMock(return_value=mock_server_instance)
        mock_server_instance.__aexit__ = AsyncMock(return_value=None)
        mock_server_class.return_value = mock_server_instance

        mock_client = AsyncMock()
        mock_client.ping.return_value = True

        # Mock tool list response
        mock_tool = MagicMock()
        mock_tool.name = "test_tool"
        mock_tool.inputSchema = {"properties": {}, "required": []}

        mock_list_response = MagicMock()
        mock_list_response.tools = [mock_tool]
        mock_client.list_tools_mcp.return_value = mock_list_response

        # Mock tool execution response with just a number as string
        mock_result_content = MagicMock()
        mock_result_content.text = "42"
        mock_result = MockCallToolResult(content=[mock_result_content])
        mock_client.call_tool.return_value = mock_result

        mock_client_class.return_value.__aenter__.return_value = mock_client
        mock_client_class.return_value.__aexit__.return_value = None

        # Execute
        await runner.run("test_tool")

        # Verify numeric output is formatted as JSON (valid JSON primitive)
        output = mock_stdout.getvalue()
        assert "42" in output

    @pytest.mark.asyncio
    @patch("sys.stdout", new_callable=StringIO)
    @patch("itential_mcp.runtime.runner.Client")
    @patch("itential_mcp.runtime.runner.Server")
    @patch("itential_mcp.runtime.runner.config.get")
    async def test_run_html_response_returns_plain_text(
        self, mock_config_get, mock_server_class, mock_client_class, mock_stdout
    ):
        """Test that HTML response returns plain text without parsing error"""
        # Setup mocks
        mock_config = MagicMock()
        mock_config_get.return_value = mock_config

        # Setup server instance mock
        mock_server_instance = MagicMock()
        mock_server_instance.mcp = MagicMock()
        mock_server_instance.__aenter__ = AsyncMock(return_value=mock_server_instance)
        mock_server_instance.__aexit__ = AsyncMock(return_value=None)
        mock_server_class.return_value = mock_server_instance

        mock_client = AsyncMock()
        mock_client.ping.return_value = True

        # Mock tool list response
        mock_tool = MagicMock()
        mock_tool.name = "test_tool"
        mock_tool.inputSchema = {"properties": {}, "required": []}

        mock_list_response = MagicMock()
        mock_list_response.tools = [mock_tool]
        mock_client.list_tools_mcp.return_value = mock_list_response

        # Mock tool execution response with HTML
        mock_result_content = MagicMock()
        html_response = "<html><body><h1>Error</h1></body></html>"
        mock_result_content.text = html_response
        mock_result = MockCallToolResult(content=[mock_result_content])
        mock_client.call_tool.return_value = mock_result

        mock_client_class.return_value.__aenter__.return_value = mock_client
        mock_client_class.return_value.__aexit__.return_value = None

        # Execute - should not raise an exception
        await runner.run("test_tool")

        # Verify HTML is output as plain text
        output = mock_stdout.getvalue()
        assert html_response in output
