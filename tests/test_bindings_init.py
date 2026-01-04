# Copyright (c) 2025 Itential, Inc
# GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

import pytest
from unittest.mock import AsyncMock, MagicMock, patch

from itential_mcp.bindings import bind_to_tool, iterbindings
from itential_mcp.platform import PlatformClient


@pytest.fixture
def mock_platform_client():
    """Mock PlatformClient for testing."""
    platform_client = AsyncMock(spec=PlatformClient)
    platform_client.client = AsyncMock()

    # Mock the response structure for different API calls
    def mock_get(url, params=None):
        mock_response = MagicMock()  # Use MagicMock instead of AsyncMock for response

        if "/operations-manager/automations" in url:
            # Return automation data
            mock_response.json.return_value = {
                "metadata": {"total": 1},
                "data": [{"_id": "test-automation-id", "name": "test-automation"}],
            }
        elif "/operations-manager/triggers" in url:
            # Return trigger data
            mock_response.json.return_value = {
                "metadata": {"total": 1},
                "data": [
                    {
                        "_id": "test-trigger-id",
                        "name": "test-tool",
                        "description": "Test trigger description",
                        "schema": {"type": "object", "properties": {}},
                        "routeName": "test-route",
                    }
                ],
            }

        return mock_response

    platform_client.client.get.side_effect = mock_get

    return platform_client


@pytest.fixture
def mock_tool_config():
    """Mock tool configuration for testing."""
    tool = MagicMock()
    tool.type = "endpoint"
    tool.name = "test-tool"
    tool.tool_name = "test_tool_name"
    tool.automation = "test-automation"
    tool.tags = "tag1,tag2"
    return tool


@pytest.fixture
def mock_tool_config_no_tags():
    """Mock tool configuration without tags for testing."""
    tool = MagicMock()
    tool.type = "endpoint"
    tool.name = "test-tool"
    tool.tool_name = "test_tool_name"
    tool.automation = "test-automation"
    tool.tags = None
    return tool


@pytest.fixture
def mock_endpoint_module():
    """Mock endpoint module for testing."""
    module = MagicMock()
    mock_function = AsyncMock()
    mock_description = "Test function description"

    # The 'new' function is async and returns a tuple
    async def mock_new(*args):
        return (mock_function, mock_description)

    module.new = AsyncMock(side_effect=mock_new)
    return module


class TestBindToTool:
    """Test cases for bind_to_tool function."""

    @patch("itential_mcp.bindings._import_binding")
    @pytest.mark.asyncio
    async def test_bind_to_tool_success_with_tags(
        self,
        mock_import_binding,
        mock_tool_config,
        mock_platform_client,
        mock_endpoint_module,
    ):
        """Test successful tool binding with custom tags."""
        # Setup
        mock_import_binding.return_value = mock_endpoint_module

        # Execute
        fn, kwargs = await bind_to_tool(mock_tool_config, mock_platform_client)

        # Verify
        mock_endpoint_module.new.assert_called_once_with(
            mock_tool_config, mock_platform_client
        )
        # Since we're using AsyncMock with side_effect, we need to check the actual function returned
        assert callable(fn)
        assert kwargs["name"] == "test_tool_name"
        assert kwargs["exclude_args"] == ("_tool_config",)
        assert kwargs["tags"] == ["bindings", "test_tool_name", "tag1", "tag2"]

    @patch("itential_mcp.bindings._import_binding")
    @pytest.mark.asyncio
    async def test_bind_to_tool_success_without_tags(
        self,
        mock_import_binding,
        mock_tool_config_no_tags,
        mock_platform_client,
        mock_endpoint_module,
    ):
        """Test successful tool binding without custom tags."""
        # Setup
        mock_import_binding.return_value = mock_endpoint_module

        # Execute
        fn, kwargs = await bind_to_tool(mock_tool_config_no_tags, mock_platform_client)

        # Verify
        mock_endpoint_module.new.assert_called_once_with(
            mock_tool_config_no_tags, mock_platform_client
        )
        # Since we're using AsyncMock with side_effect, we need to check the actual function returned
        assert callable(fn)
        assert kwargs["name"] == "test_tool_name"
        assert kwargs["exclude_args"] == ("_tool_config",)
        assert kwargs["tags"] == ["bindings", "test_tool_name"]

    @patch("itential_mcp.bindings._import_binding")
    @pytest.mark.asyncio
    async def test_bind_to_tool_missing_type(
        self, mock_import_binding, mock_tool_config, mock_platform_client
    ):
        """Test bind_to_tool raises error when tool type module is not found."""
        # Setup
        mock_import_binding.side_effect = ImportError("Module not found")

        # Execute and verify
        with pytest.raises(ImportError):
            await bind_to_tool(mock_tool_config, mock_platform_client)

    @patch("itential_mcp.bindings._import_binding")
    @pytest.mark.asyncio
    async def test_bind_to_tool_missing_new_function(
        self, mock_import_binding, mock_tool_config, mock_platform_client
    ):
        """Test bind_to_tool raises AttributeError when module lacks 'new' function."""
        # Setup
        mock_module_without_new = MagicMock(spec=[])  # Module without 'new' attribute
        mock_import_binding.return_value = mock_module_without_new

        # Execute and verify
        with pytest.raises(AttributeError):
            await bind_to_tool(mock_tool_config, mock_platform_client)


class TestIterBindings:
    """Test cases for iterbindings function."""

    @patch("itential_mcp.bindings.PlatformClient")
    @patch("itential_mcp.bindings.bind_to_tool")
    @pytest.mark.asyncio
    async def test_iterbindings_success(
        self, mock_bind_to_tool, mock_platform_client_class
    ):
        """Test successful iteration over tool bindings."""
        # Setup
        mock_config = MagicMock()
        tool1 = MagicMock()
        tool1.name = "tool1"
        tool2 = MagicMock()
        tool2.name = "tool2"
        mock_config.tools = [tool1, tool2]

        # Create mock that supports async context manager protocol
        mock_platform_client_instance = AsyncMock()
        mock_platform_client_instance.__aenter__.return_value = (
            mock_platform_client_instance
        )
        mock_platform_client_instance.__aexit__.return_value = None
        mock_platform_client_class.return_value = mock_platform_client_instance

        mock_bind_to_tool.side_effect = [
            (AsyncMock(), {"name": "tool1", "tags": "tag1"}),
            (AsyncMock(), {"name": "tool2", "tags": "tag2"}),
        ]

        # Execute
        results = []
        async for fn, kwargs in iterbindings(mock_config):
            results.append((fn, kwargs))

        # Verify
        assert len(results) == 2
        mock_platform_client_class.assert_called_once()

        # Verify context manager was used
        mock_platform_client_instance.__aenter__.assert_called_once()
        mock_platform_client_instance.__aexit__.assert_called_once()

        # Verify bind_to_tool was called for each tool
        assert mock_bind_to_tool.call_count == 2
        mock_bind_to_tool.assert_any_call(tool1, mock_platform_client_instance)
        mock_bind_to_tool.assert_any_call(tool2, mock_platform_client_instance)

        # Verify results
        assert results[0][1]["name"] == "tool1"
        assert results[1][1]["name"] == "tool2"

    @patch("itential_mcp.bindings.PlatformClient")
    @patch("itential_mcp.bindings.bind_to_tool")
    @pytest.mark.asyncio
    async def test_iterbindings_empty_tools(
        self, mock_bind_to_tool, mock_platform_client_class
    ):
        """Test iterbindings with empty tools list."""
        # Setup
        mock_config = MagicMock()
        mock_config.tools = []

        # Create mock that supports async context manager protocol
        mock_platform_client_instance = AsyncMock()
        mock_platform_client_instance.__aenter__.return_value = (
            mock_platform_client_instance
        )
        mock_platform_client_instance.__aexit__.return_value = None
        mock_platform_client_class.return_value = mock_platform_client_instance

        # Execute
        results = []
        async for fn, kwargs in iterbindings(mock_config):
            results.append((fn, kwargs))

        # Verify
        assert len(results) == 0
        mock_platform_client_class.assert_called_once()
        mock_bind_to_tool.assert_not_called()

    @patch("itential_mcp.bindings.PlatformClient")
    @patch("itential_mcp.bindings.bind_to_tool")
    @pytest.mark.asyncio
    async def test_iterbindings_bind_error_propagates(
        self, mock_bind_to_tool, mock_platform_client_class
    ):
        """Test that errors from bind_to_tool are properly propagated."""
        # Setup
        mock_config = MagicMock()
        tool1 = MagicMock()
        mock_config.tools = [tool1]

        mock_platform_client_instance = AsyncMock()
        mock_platform_client_class.return_value = mock_platform_client_instance

        mock_bind_to_tool.side_effect = AttributeError("Module has no 'new' function")

        # Execute and verify
        with pytest.raises(AttributeError, match="Module has no 'new' function"):
            async for fn, kwargs in iterbindings(mock_config):
                pass


class TestBindingsIntegration:
    """Integration tests for bindings module."""

    @patch("itential_mcp.bindings._import_binding")
    @patch("itential_mcp.bindings.PlatformClient")
    @pytest.mark.asyncio
    async def test_full_binding_workflow(
        self, mock_platform_client_class, mock_import_binding
    ):
        """Test complete binding workflow from config to bound functions."""
        # Setup
        mock_endpoint_module = MagicMock()
        mock_function = AsyncMock()
        mock_description = "Test workflow function"

        # The 'new' function is async and returns a tuple
        async def mock_new(*args):
            return (mock_function, mock_description)

        mock_endpoint_module.new = AsyncMock(side_effect=mock_new)
        mock_import_binding.return_value = mock_endpoint_module

        # Create mock that supports async context manager protocol
        mock_platform_client_instance = AsyncMock()
        mock_platform_client_instance.client = AsyncMock()
        mock_platform_client_instance.__aenter__.return_value = (
            mock_platform_client_instance
        )
        mock_platform_client_instance.__aexit__.return_value = None

        # Mock the response structure for different API calls
        def mock_get(url, params=None):
            mock_response = (
                MagicMock()
            )  # Use MagicMock instead of AsyncMock for response

            if "/operations-manager/automations" in url:
                # Return automation data
                mock_response.json.return_value = {
                    "metadata": {"total": 1},
                    "data": [{"_id": "test-automation-id", "name": "test-automation"}],
                }
            elif "/operations-manager/triggers" in url:
                # Return trigger data
                mock_response.json.return_value = {
                    "metadata": {"total": 1},
                    "data": [
                        {
                            "_id": "test-trigger-id",
                            "name": "test-workflow",
                            "description": "Test workflow description",
                            "schema": {"type": "object", "properties": {}},
                            "routeName": "test-workflow-route",
                        }
                    ],
                }

            return mock_response

        mock_platform_client_instance.client.get.side_effect = mock_get
        mock_platform_client_class.return_value = mock_platform_client_instance

        # Create mock config with tools
        mock_config = MagicMock()
        tool = MagicMock()
        tool.type = "endpoint"
        tool.name = "test-workflow"
        tool.tool_name = "test_workflow"
        tool.automation = "test-automation"
        tool.tags = "workflow,automation"
        mock_config.tools = [tool]

        # Execute
        results = []
        async for fn, kwargs in iterbindings(mock_config):
            results.append((fn, kwargs))

        # Verify
        assert len(results) == 1
        bound_fn, bound_kwargs = results[0]

        # Since we're using AsyncMock with side_effect, we need to check the actual function returned
        assert callable(bound_fn)
        assert bound_kwargs["name"] == "test_workflow"
        assert bound_kwargs["exclude_args"] == ("_tool_config",)
        assert bound_kwargs["tags"] == [
            "bindings",
            "test_workflow",
            "workflow",
            "automation",
        ]

        # Verify the endpoint module was called correctly
        mock_endpoint_module.new.assert_called_once_with(
            tool, mock_platform_client_instance
        )
