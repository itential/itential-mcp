# Copyright (c) 2025 Itential, Inc
# GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

import pytest
from unittest.mock import AsyncMock, MagicMock, patch

from pydantic import BaseModel

from itential_mcp.bindings.endpoint import _get_trigger, start_workflow, new
from itential_mcp.platform import PlatformClient
from itential_mcp.core import exceptions
from fastmcp import Context


class MockResponse(BaseModel):
    """Mock response model for testing."""

    data: dict


@pytest.fixture
def mock_platform_client():
    """Mock PlatformClient for testing."""
    client_mock = AsyncMock(spec=PlatformClient)
    client_mock.client = AsyncMock()
    return client_mock


@pytest.fixture
def mock_endpoint_tool():
    """Mock EndpointTool configuration for testing."""
    tool = MagicMock()
    tool.automation = "test-automation"
    tool.name = "test-trigger"
    return tool


@pytest.fixture
def mock_context():
    """Mock FastMCP Context for testing."""
    context = MagicMock(spec=Context)
    context.request_context.lifespan_context.get.return_value = AsyncMock(
        spec=PlatformClient
    )
    return context


@pytest.fixture
def mock_automation_response():
    """Mock response for automation API call."""
    return {
        "metadata": {"total": 1},
        "data": [{"_id": "automation-123", "name": "test-automation"}],
    }


@pytest.fixture
def mock_triggers_response():
    """Mock response for triggers API call."""
    return {
        "data": [
            {
                "name": "test-trigger",
                "routeName": "test-route",
                "description": "Test trigger",
                "schema": {"type": "object"},
            },
            {
                "name": "other-trigger",
                "routeName": "other-route",
                "description": "Other trigger",
                "schema": {"type": "object"},
            },
        ]
    }


@pytest.fixture
def mock_trigger_data():
    """Mock trigger data for testing."""
    return {
        "name": "test-trigger",
        "routeName": "test-route",
        "description": "Test trigger description",
        "schema": {"type": "object", "properties": {"param": {"type": "string"}}},
    }


class TestGetTrigger:
    """Test cases for _get_trigger function."""

    @pytest.mark.asyncio
    async def test_get_trigger_success(
        self,
        mock_platform_client,
        mock_endpoint_tool,
        mock_automation_response,
        mock_triggers_response,
    ):
        """Test successful trigger retrieval."""
        # Setup
        mock_platform_client.client.get.side_effect = [
            # First call for automation
            MagicMock(json=lambda: mock_automation_response),
            # Second call for triggers
            MagicMock(json=lambda: mock_triggers_response),
        ]

        # Execute
        result = await _get_trigger(mock_platform_client, mock_endpoint_tool)

        # Verify
        assert result == mock_triggers_response["data"][0]
        assert mock_platform_client.client.get.call_count == 2

        # Verify first call (automation lookup)
        mock_platform_client.client.get.assert_any_call(
            "/operations-manager/automations",
            params={"equals": "test-automation", "equalsField": "name"},
        )

        # Verify second call (triggers lookup)
        mock_platform_client.client.get.assert_any_call(
            "/operations-manager/triggers",
            params={"equals": "automation-123", "equalsField": "actionId"},
        )

    @pytest.mark.asyncio
    async def test_get_trigger_automation_not_found(
        self, mock_platform_client, mock_endpoint_tool
    ):
        """Test _get_trigger raises NotFoundError when automation is not found."""
        # Setup - automation not found
        automation_response = {"metadata": {"total": 0}, "data": []}
        mock_platform_client.client.get.return_value = MagicMock(
            json=lambda: automation_response
        )

        # Execute and verify
        with pytest.raises(
            exceptions.NotFoundError,
            match="automation test-automation could not be found",
        ):
            await _get_trigger(mock_platform_client, mock_endpoint_tool)

        # Verify only one call was made (automation lookup)
        assert mock_platform_client.client.get.call_count == 1

    @pytest.mark.asyncio
    async def test_get_trigger_multiple_automations_found(
        self, mock_platform_client, mock_endpoint_tool
    ):
        """Test _get_trigger with multiple automations - uses first match, then fails on trigger lookup."""
        # Setup - multiple automations found, but empty triggers response
        automation_response = {
            "metadata": {"total": 2},
            "data": [
                {"_id": "automation-123", "name": "test-automation"},
                {"_id": "automation-456", "name": "test-automation"},
            ],
        }
        triggers_response = {"data": []}

        # Mock responses in order: automation lookup succeeds, trigger lookup returns empty
        mock_platform_client.client.get.side_effect = [
            MagicMock(json=lambda: automation_response),
            MagicMock(json=lambda: triggers_response),
        ]

        # Execute and verify - should fail when trigger is not found
        with pytest.raises(
            exceptions.NotFoundError,
            match="trigger test-trigger could not be found",
        ):
            await _get_trigger(mock_platform_client, mock_endpoint_tool)

    @pytest.mark.asyncio
    async def test_get_trigger_trigger_not_found(
        self, mock_platform_client, mock_endpoint_tool, mock_automation_response
    ):
        """Test _get_trigger raises NotFoundError when trigger is not found."""
        # Setup
        triggers_response = {
            "data": [{"name": "other-trigger", "routeName": "other-route"}]
        }
        mock_platform_client.client.get.side_effect = [
            MagicMock(json=lambda: mock_automation_response),
            MagicMock(json=lambda: triggers_response),
        ]

        # Execute and verify
        with pytest.raises(
            exceptions.NotFoundError, match="trigger test-trigger could not be found"
        ):
            await _get_trigger(mock_platform_client, mock_endpoint_tool)

    @pytest.mark.asyncio
    async def test_get_trigger_empty_triggers(
        self, mock_platform_client, mock_endpoint_tool, mock_automation_response
    ):
        """Test _get_trigger raises NotFoundError when no triggers are returned."""
        # Setup
        triggers_response = {"data": []}
        mock_platform_client.client.get.side_effect = [
            MagicMock(json=lambda: mock_automation_response),
            MagicMock(json=lambda: triggers_response),
        ]

        # Execute and verify
        with pytest.raises(
            exceptions.NotFoundError, match="trigger test-trigger could not be found"
        ):
            await _get_trigger(mock_platform_client, mock_endpoint_tool)


class TestStartWorkflow:
    """Test cases for start_workflow function."""

    @patch("itential_mcp.bindings.endpoint._get_trigger")
    @patch("itential_mcp.bindings.endpoint.operations_manager.start_workflow")
    @pytest.mark.asyncio
    async def test_start_workflow_success(
        self, mock_ops_start_workflow, mock_get_trigger, mock_context, mock_trigger_data
    ):
        """Test successful workflow start."""
        # Setup
        mock_tool_config = MagicMock()
        mock_data = {"param": "value"}
        mock_get_trigger.return_value = mock_trigger_data
        mock_ops_start_workflow.return_value = MockResponse(data={"job_id": "job-123"})

        # Execute
        result = await start_workflow(mock_context, mock_tool_config, mock_data)

        # Verify
        mock_get_trigger.assert_called_once_with(
            mock_context.request_context.lifespan_context.get.return_value,
            mock_tool_config,
        )
        mock_ops_start_workflow.assert_called_once_with(
            mock_context, route_name="test-route", data=mock_data
        )
        assert result == MockResponse(data={"job_id": "job-123"})

    @patch("itential_mcp.bindings.endpoint._get_trigger")
    @patch("itential_mcp.bindings.endpoint.operations_manager.start_workflow")
    @pytest.mark.asyncio
    async def test_start_workflow_no_data(
        self, mock_ops_start_workflow, mock_get_trigger, mock_context, mock_trigger_data
    ):
        """Test workflow start without input data."""
        # Setup
        mock_tool_config = MagicMock()
        mock_get_trigger.return_value = mock_trigger_data
        mock_ops_start_workflow.return_value = MockResponse(data={"job_id": "job-456"})

        # Execute
        result = await start_workflow(mock_context, mock_tool_config, None)

        # Verify
        mock_ops_start_workflow.assert_called_once_with(
            mock_context, route_name="test-route", data=None
        )
        assert result == MockResponse(data={"job_id": "job-456"})

    @patch("itential_mcp.bindings.endpoint._get_trigger")
    @pytest.mark.asyncio
    async def test_start_workflow_trigger_not_found(
        self, mock_get_trigger, mock_context
    ):
        """Test start_workflow propagates NotFoundError from _get_trigger."""
        # Setup
        mock_tool_config = MagicMock()
        mock_get_trigger.side_effect = exceptions.NotFoundError("trigger not found")

        # Execute and verify
        with pytest.raises(exceptions.NotFoundError, match="trigger not found"):
            await start_workflow(mock_context, mock_tool_config, {})

    @patch("itential_mcp.bindings.endpoint._get_trigger")
    @patch("itential_mcp.bindings.endpoint.operations_manager.start_workflow")
    @pytest.mark.asyncio
    async def test_start_workflow_operations_manager_error(
        self, mock_ops_start_workflow, mock_get_trigger, mock_context, mock_trigger_data
    ):
        """Test start_workflow propagates errors from operations_manager."""
        # Setup
        mock_tool_config = MagicMock()
        mock_get_trigger.return_value = mock_trigger_data
        mock_ops_start_workflow.side_effect = Exception("Workflow execution failed")

        # Execute and verify
        with pytest.raises(Exception, match="Workflow execution failed"):
            await start_workflow(mock_context, mock_tool_config, {})


class TestNew:
    """Test cases for new function."""

    @patch("itential_mcp.bindings.endpoint._get_trigger")
    @pytest.mark.asyncio
    async def test_new_success(
        self,
        mock_get_trigger,
        mock_endpoint_tool,
        mock_platform_client,
        mock_trigger_data,
    ):
        """Test successful creation of bound workflow function."""
        # Setup
        mock_get_trigger.return_value = mock_trigger_data

        # Execute
        fn, description = await new(mock_endpoint_tool, mock_platform_client)

        # Verify
        mock_get_trigger.assert_called_once_with(
            mock_platform_client, mock_endpoint_tool
        )
        assert fn == start_workflow
        assert "Test trigger description" in description
        assert "Args:" in description
        assert "data (dict):" in description

    @patch("itential_mcp.bindings.endpoint._get_trigger")
    @pytest.mark.asyncio
    async def test_new_empty_description(
        self, mock_get_trigger, mock_endpoint_tool, mock_platform_client
    ):
        """Test new function with empty trigger description."""
        # Setup
        trigger_data = {
            "name": "test-trigger",
            "routeName": "test-route",
            "description": "",
            "schema": {"type": "object"},
        }
        mock_get_trigger.return_value = trigger_data

        # Execute
        fn, description = await new(mock_endpoint_tool, mock_platform_client)

        # Verify
        assert fn == start_workflow
        assert "Args:\ndata (dict):" in description

    @patch("itential_mcp.bindings.endpoint._get_trigger")
    @pytest.mark.asyncio
    async def test_new_none_description(
        self, mock_get_trigger, mock_endpoint_tool, mock_platform_client
    ):
        """Test new function with None trigger description."""
        # Setup
        trigger_data = {
            "name": "test-trigger",
            "routeName": "test-route",
            "description": None,
            "schema": {"type": "object"},
        }
        mock_get_trigger.return_value = trigger_data

        # Execute
        fn, description = await new(mock_endpoint_tool, mock_platform_client)

        # Verify
        assert fn == start_workflow
        assert "Args:\ndata (dict):" in description

    @patch("itential_mcp.bindings.endpoint._get_trigger")
    @pytest.mark.asyncio
    async def test_new_trigger_not_found(
        self, mock_get_trigger, mock_endpoint_tool, mock_platform_client
    ):
        """Test new function propagates NotFoundError from _get_trigger."""
        # Setup
        mock_get_trigger.side_effect = exceptions.NotFoundError("trigger not found")

        # Execute and verify
        with pytest.raises(exceptions.NotFoundError, match="trigger not found"):
            await new(mock_endpoint_tool, mock_platform_client)


class TestEndpointIntegration:
    """Integration tests for endpoint module."""

    @pytest.mark.asyncio
    async def test_full_endpoint_workflow(
        self, mock_platform_client, mock_endpoint_tool
    ):
        """Test complete endpoint workflow from trigger retrieval to function binding."""
        # Setup
        automation_response = {
            "metadata": {"total": 1},
            "data": [{"_id": "automation-123", "name": "test-automation"}],
        }
        triggers_response = {
            "data": [
                {
                    "name": "test-trigger",
                    "routeName": "test-workflow-route",
                    "description": "Complete test workflow",
                    "schema": {
                        "type": "object",
                        "properties": {"device": {"type": "string"}},
                    },
                }
            ]
        }

        # We need to provide enough responses for both calls to _get_trigger
        # (once in new() and once directly in test)
        mock_platform_client.client.get.side_effect = [
            MagicMock(json=lambda: automation_response),
            MagicMock(json=lambda: triggers_response),
            MagicMock(json=lambda: automation_response),
            MagicMock(json=lambda: triggers_response),
        ]

        # Execute
        fn, description = await new(mock_endpoint_tool, mock_platform_client)

        # Verify
        assert fn == start_workflow
        assert "Complete test workflow" in description
        assert "Args:" in description
        assert "data (dict):" in description
        assert "'type': 'object'" in description

        # Verify the trigger was retrieved correctly in a separate call
        trigger = await _get_trigger(mock_platform_client, mock_endpoint_tool)
        assert trigger["name"] == "test-trigger"
        assert trigger["routeName"] == "test-workflow-route"
        assert trigger["description"] == "Complete test workflow"

    @pytest.mark.asyncio
    async def test_endpoint_error_handling_chain(
        self, mock_platform_client, mock_endpoint_tool
    ):
        """Test that errors propagate correctly through the endpoint chain."""
        # Setup - simulate automation not found
        automation_response = {"metadata": {"total": 0}, "data": []}
        mock_platform_client.client.get.return_value = MagicMock(
            json=lambda: automation_response
        )

        # Test error propagation through _get_trigger
        with pytest.raises(exceptions.NotFoundError):
            await _get_trigger(mock_platform_client, mock_endpoint_tool)

        # Test error propagation through new function
        with pytest.raises(exceptions.NotFoundError):
            await new(mock_endpoint_tool, mock_platform_client)
