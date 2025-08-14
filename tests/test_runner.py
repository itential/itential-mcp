# Copyright (c) 2025 Itential, Inc
# GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)

import json
import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from io import StringIO
from dataclasses import dataclass
from typing import Any

from itential_mcp import runner


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
    @patch('sys.stdout', new_callable=StringIO)
    @patch('itential_mcp.runner.Client')
    @patch('itential_mcp.runner.server.new')
    @patch('itential_mcp.runner.config.get')
    async def test_run_basic_tool_no_params(self, mock_config_get, mock_server_new, mock_client_class, mock_stdout):
        """Test running a tool without parameters"""
        # Setup mocks
        mock_config = MagicMock()
        mock_config_get.return_value = mock_config
        
        mock_server = MagicMock()
        mock_server_new.return_value = mock_server
        
        mock_client = AsyncMock()
        mock_client.ping.return_value = True
        
        # Mock tool list response
        mock_tool = MagicMock()
        mock_tool.name = "test_tool"
        mock_tool.inputSchema = {
            "properties": {"param1": {"type": "string"}},
            "required": []
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
        mock_server_new.assert_called_once_with(mock_config)
        mock_client.ping.assert_called_once()
        mock_client.list_tools_mcp.assert_called_once()
        mock_client.call_tool.assert_called_once_with("test_tool", arguments=None)
        
        # Check stdout output
        output = mock_stdout.getvalue()
        assert '"result": "success"' in output

    @pytest.mark.asyncio
    @patch('sys.stdout', new_callable=StringIO)
    @patch('itential_mcp.runner.Client')
    @patch('itential_mcp.runner.server.new')
    @patch('itential_mcp.runner.config.get')
    async def test_run_tool_with_params(self, mock_config_get, mock_server_new, mock_client_class, mock_stdout):
        """Test running a tool with parameters"""
        # Setup mocks
        mock_config = MagicMock()
        mock_config_get.return_value = mock_config
        
        mock_server = MagicMock()
        mock_server_new.return_value = mock_server
        
        mock_client = AsyncMock()
        mock_client.ping.return_value = True
        
        # Mock tool list response
        mock_tool = MagicMock()
        mock_tool.name = "test_tool"
        mock_tool.inputSchema = {
            "properties": {
                "param1": {"type": "string"},
                "param2": {"type": "integer"}
            },
            "required": ["param1"]
        }
        
        mock_list_response = MagicMock()
        mock_list_response.tools = [mock_tool]
        mock_client.list_tools_mcp.return_value = mock_list_response
        
        # Mock tool execution response
        mock_result_content = MagicMock()
        mock_result_content.text = json.dumps({"result": "success", "param1_value": "test"})
        mock_result = MockCallToolResult(content=[mock_result_content])
        mock_client.call_tool.return_value = mock_result
        
        mock_client_class.return_value.__aenter__.return_value = mock_client
        mock_client_class.return_value.__aexit__.return_value = None
        
        # Execute with parameters
        params_json = '{"param1": "test", "param2": 42}'
        await runner.run("test_tool", params_json)
        
        # Verify
        expected_arguments = {"param1": "test", "param2": 42}
        mock_client.call_tool.assert_called_once_with("test_tool", arguments=expected_arguments)
        
        # Check stdout output
        output = mock_stdout.getvalue()
        assert '"result": "success"' in output
        assert '"param1_value": "test"' in output

    @pytest.mark.asyncio
    @patch('itential_mcp.runner.Client')
    @patch('itential_mcp.runner.server.new')
    @patch('itential_mcp.runner.config.get')
    async def test_run_server_ping_failure(self, mock_config_get, mock_server_new, mock_client_class):
        """Test failure when server ping fails"""
        # Setup mocks
        mock_config = MagicMock()
        mock_config_get.return_value = mock_config
        
        mock_server = MagicMock()
        mock_server_new.return_value = mock_server
        
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
    @patch('itential_mcp.runner.Client')
    @patch('itential_mcp.runner.server.new')
    @patch('itential_mcp.runner.config.get')
    async def test_run_invalid_tool(self, mock_config_get, mock_server_new, mock_client_class):
        """Test running an invalid/non-existent tool"""
        # Setup mocks
        mock_config = MagicMock()
        mock_config_get.return_value = mock_config
        
        mock_server = MagicMock()
        mock_server_new.return_value = mock_server
        
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
    @patch('itential_mcp.runner.Client')
    @patch('itential_mcp.runner.server.new')
    @patch('itential_mcp.runner.config.get')
    async def test_run_missing_required_params(self, mock_config_get, mock_server_new, mock_client_class):
        """Test running a tool with missing required parameters"""
        # Setup mocks
        mock_config = MagicMock()
        mock_config_get.return_value = mock_config
        
        mock_server = MagicMock()
        mock_server_new.return_value = mock_server
        
        mock_client = AsyncMock()
        mock_client.ping.return_value = True
        
        # Mock tool list response with required parameters
        mock_tool = MagicMock()
        mock_tool.name = "test_tool"
        mock_tool.inputSchema = {
            "properties": {
                "required_param": {"type": "string"},
                "optional_param": {"type": "string"}
            },
            "required": ["required_param"]
        }
        
        mock_list_response = MagicMock()
        mock_list_response.tools = [mock_tool]
        mock_client.list_tools_mcp.return_value = mock_list_response
        
        mock_client_class.return_value.__aenter__.return_value = mock_client
        mock_client_class.return_value.__aexit__.return_value = None
        
        # Execute without required parameter and verify exception
        with pytest.raises(ValueError, match="missing required property: required_param"):
            await runner.run("test_tool")
        
        # Execute with incomplete parameters and verify exception
        params_json = '{"optional_param": "test"}'
        with pytest.raises(ValueError, match="missing required property: required_param"):
            await runner.run("test_tool", params_json)
        
        # Should not proceed to call tool
        mock_client.call_tool.assert_not_called()

    @pytest.mark.asyncio
    @patch('itential_mcp.runner.Client')
    @patch('itential_mcp.runner.server.new')
    @patch('itential_mcp.runner.config.get')
    async def test_run_invalid_params(self, mock_config_get, mock_server_new, mock_client_class):
        """Test running a tool with invalid parameters"""
        # Setup mocks
        mock_config = MagicMock()
        mock_config_get.return_value = mock_config
        
        mock_server = MagicMock()
        mock_server_new.return_value = mock_server
        
        mock_client = AsyncMock()
        mock_client.ping.return_value = True
        
        # Mock tool list response
        mock_tool = MagicMock()
        mock_tool.name = "test_tool"
        mock_tool.inputSchema = {
            "properties": {
                "valid_param": {"type": "string"}
            },
            "required": []
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
    @patch('sys.stdout', new_callable=StringIO)
    @patch('itential_mcp.runner.Client')
    @patch('itential_mcp.runner.server.new')
    @patch('itential_mcp.runner.config.get')
    async def test_run_tool_no_required_params(self, mock_config_get, mock_server_new, mock_client_class, mock_stdout):
        """Test running a tool that has no required parameters in schema"""
        # Setup mocks
        mock_config = MagicMock()
        mock_config_get.return_value = mock_config
        
        mock_server = MagicMock()
        mock_server_new.return_value = mock_server
        
        mock_client = AsyncMock()
        mock_client.ping.return_value = True
        
        # Mock tool list response with no required field (None)
        mock_tool = MagicMock()
        mock_tool.name = "test_tool"
        mock_tool.inputSchema = {
            "properties": {"optional_param": {"type": "string"}},
            "required": None  # No required parameters
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
    @patch('sys.stdout', new_callable=StringIO)
    @patch('itential_mcp.runner.Client')
    @patch('itential_mcp.runner.server.new')
    @patch('itential_mcp.runner.config.get')
    async def test_run_multiple_tools_available(self, mock_config_get, mock_server_new, mock_client_class, mock_stdout):
        """Test running a specific tool when multiple tools are available"""
        # Setup mocks
        mock_config = MagicMock()
        mock_config_get.return_value = mock_config
        
        mock_server = MagicMock()
        mock_server_new.return_value = mock_server
        
        mock_client = AsyncMock()
        mock_client.ping.return_value = True
        
        # Mock multiple tools
        mock_tool1 = MagicMock()
        mock_tool1.name = "tool1"
        mock_tool1.inputSchema = {"properties": {}, "required": []}
        
        mock_tool2 = MagicMock()
        mock_tool2.name = "tool2"
        mock_tool2.inputSchema = {"properties": {"param": {"type": "string"}}, "required": []}
        
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
    @patch('itential_mcp.runner.Client')
    @patch('itential_mcp.runner.server.new')
    @patch('itential_mcp.runner.config.get')
    async def test_run_invalid_json_params(self, mock_config_get, mock_server_new, mock_client_class):
        """Test running a tool with invalid JSON parameters"""
        # Setup mocks
        mock_config = MagicMock()
        mock_config_get.return_value = mock_config
        
        mock_server = MagicMock()
        mock_server_new.return_value = mock_server
        
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
    @patch('sys.stdout', new_callable=StringIO)
    @patch('itential_mcp.runner.Client')
    @patch('itential_mcp.runner.server.new')
    @patch('itential_mcp.runner.config.get')
    async def test_run_complex_result_formatting(self, mock_config_get, mock_server_new, mock_client_class, mock_stdout):
        """Test that complex results are properly formatted in JSON output"""
        # Setup mocks
        mock_config = MagicMock()
        mock_config_get.return_value = mock_config
        
        mock_server = MagicMock()
        mock_server_new.return_value = mock_server
        
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
                "metadata": {
                    "total": 2,
                    "page": 1
                }
            }
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
    @patch('itential_mcp.runner.Client')
    @patch('itential_mcp.runner.server.new')
    @patch('itential_mcp.runner.config.get')
    async def test_run_empty_tool_list(self, mock_config_get, mock_server_new, mock_client_class):
        """Test behavior when no tools are available"""
        # Setup mocks
        mock_config = MagicMock()
        mock_config_get.return_value = mock_config
        
        mock_server = MagicMock()
        mock_server_new.return_value = mock_server
        
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
    @patch('sys.stdout', new_callable=StringIO)
    @patch('itential_mcp.runner.Client')
    @patch('itential_mcp.runner.server.new')
    @patch('itential_mcp.runner.config.get')
    async def test_run_empty_params_string(self, mock_config_get, mock_server_new, mock_client_class, mock_stdout):
        """Test running a tool with empty parameters string"""
        # Setup mocks
        mock_config = MagicMock()
        mock_config_get.return_value = mock_config
        
        mock_server = MagicMock()
        mock_server_new.return_value = mock_server
        
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
    @patch('sys.stdout', new_callable=StringIO)
    @patch('itential_mcp.runner.Client')
    @patch('itential_mcp.runner.server.new')
    @patch('itential_mcp.runner.config.get')
    async def test_run_full_workflow(self, mock_config_get, mock_server_new, mock_client_class, mock_stdout):
        """Test the complete workflow from start to finish"""
        # Setup mocks
        mock_config = MagicMock()
        mock_config_get.return_value = mock_config
        
        mock_server = MagicMock()
        mock_server_new.return_value = mock_server
        
        mock_client = AsyncMock()
        mock_client.ping.return_value = True
        
        # Mock realistic tool list response
        mock_tool = MagicMock()
        mock_tool.name = "get_user_info"
        mock_tool.inputSchema = {
            "properties": {
                "user_id": {"type": "string", "description": "User ID to retrieve"},
                "include_details": {"type": "boolean", "description": "Include detailed info"}
            },
            "required": ["user_id"]
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
                "details": {
                    "role": "admin",
                    "last_login": "2024-01-15T10:30:00Z"
                }
            },
            "status": "success"
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
        mock_server_new.assert_called_once_with(mock_config)
        mock_client.ping.assert_called_once()
        mock_client.list_tools_mcp.assert_called_once()
        
        expected_args = {"user_id": "12345", "include_details": True}
        mock_client.call_tool.assert_called_once_with("get_user_info", arguments=expected_args)
        
        # Verify output formatting
        output = mock_stdout.getvalue()
        assert '"user"' in output
        assert '"name": "John Doe"' in output
        assert '"status": "success"' in output
        assert '"role": "admin"' in output