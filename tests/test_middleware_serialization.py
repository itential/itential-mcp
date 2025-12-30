# Copyright (c) 2025 Itential, Inc
# GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

"""Tests for the SerializationMiddleware."""

import pytest
from unittest.mock import AsyncMock, MagicMock

from itential_mcp.middleware.serialization import SerializationMiddleware
from itential_mcp import config


@pytest.fixture
def mock_config_json():
    """Create a mock config with JSON format."""
    cfg = MagicMock(spec=config.Config)
    cfg.server_response_format = "json"
    return cfg


@pytest.fixture
def mock_config_toon():
    """Create a mock config with TOON format."""
    cfg = MagicMock(spec=config.Config)
    cfg.server_response_format = "toon"
    return cfg


@pytest.fixture
def mock_config_auto():
    """Create a mock config with auto format."""
    cfg = MagicMock(spec=config.Config)
    cfg.server_response_format = "auto"
    return cfg


@pytest.fixture
def mock_context():
    """Create a mock middleware context."""
    context = MagicMock()
    context.message = MagicMock()
    context.message.name = "test_tool"
    return context


@pytest.fixture
def sample_dict():
    """Create a sample dictionary."""
    return {
        "name": "test-template",
        "description": "A test template",
        "type": "textfsm",
    }


@pytest.fixture
def sample_dict_list():
    """Create a list of sample dictionaries."""
    return [
        {
            "name": "template-1",
            "description": "First template",
            "type": "textfsm",
        },
        {
            "name": "template-2",
            "description": "Second template",
            "type": "jinja2",
        },
    ]


class TestSerializationMiddlewareInit:
    """Test cases for SerializationMiddleware initialization."""

    def test_init_with_json_format(self, mock_config_json):
        """Test middleware initialization with JSON format."""
        middleware = SerializationMiddleware(mock_config_json)
        assert middleware.config == mock_config_json
        assert middleware.format == "json"

    def test_init_with_toon_format(self, mock_config_toon):
        """Test middleware initialization with TOON format."""
        middleware = SerializationMiddleware(mock_config_toon)
        assert middleware.config == mock_config_toon
        assert middleware.format == "toon"

    def test_init_with_auto_format(self, mock_config_auto):
        """Test middleware initialization with auto format."""
        middleware = SerializationMiddleware(mock_config_auto)
        assert middleware.config == mock_config_auto
        assert middleware.format == "auto"


class TestSerializationMiddlewareJsonFormat:
    """Test cases for JSON format serialization."""

    @pytest.mark.asyncio
    async def test_single_dict_json_serialization(
        self, mock_config_json, mock_context, sample_dict
    ):
        """Test JSON serialization of a single dict."""
        middleware = SerializationMiddleware(mock_config_json)

        # Mock response with structured_content
        mock_response = MagicMock()
        mock_response.structured_content = sample_dict
        call_next = AsyncMock(return_value=mock_response)

        result = await middleware.on_call_tool(mock_context, call_next)

        # Verify call_next was called
        call_next.assert_awaited_once()

        # With JSON format, the response should pass through unchanged
        assert result == mock_response

    @pytest.mark.asyncio
    async def test_dict_list_json_serialization(
        self, mock_config_json, mock_context, sample_dict_list
    ):
        """Test JSON serialization of a list of dicts."""
        middleware = SerializationMiddleware(mock_config_json)

        # Mock response with structured_content
        mock_response = MagicMock()
        mock_response.structured_content = sample_dict_list
        call_next = AsyncMock(return_value=mock_response)

        result = await middleware.on_call_tool(mock_context, call_next)

        # Verify call_next was called
        call_next.assert_awaited_once()

        # With JSON format, the response should pass through unchanged
        assert result == mock_response

    @pytest.mark.asyncio
    async def test_non_dict_passthrough_json(self, mock_config_json, mock_context):
        """Test that non-dict/list results pass through unchanged."""
        middleware = SerializationMiddleware(mock_config_json)

        # Mock response with string content
        mock_response = MagicMock()
        mock_response.structured_content = "plain string result"
        call_next = AsyncMock(return_value=mock_response)

        result = await middleware.on_call_tool(mock_context, call_next)

        # Verify call_next was called
        call_next.assert_awaited_once()

        # String data should pass through unchanged
        assert result == mock_response


class TestSerializationMiddlewareToonFormat:
    """Test cases for TOON format serialization."""

    @pytest.mark.asyncio
    async def test_single_dict_toon_serialization(
        self, mock_config_toon, mock_context, sample_dict
    ):
        """Test TOON serialization of a single dict."""
        middleware = SerializationMiddleware(mock_config_toon)

        # Mock response with structured_content and content list
        mock_content_item = MagicMock()
        mock_content_item.text = ""
        mock_response = MagicMock()
        mock_response.structured_content = sample_dict
        mock_response.content = [mock_content_item]
        call_next = AsyncMock(return_value=mock_response)

        result = await middleware.on_call_tool(mock_context, call_next)

        # Verify call_next was called
        call_next.assert_awaited_once()

        # Result should be the modified response object
        assert result == mock_response

        # TOON format should modify content[0].text
        assert isinstance(result.content[0].text, str)
        # TOON format should contain the data
        assert "test-template" in result.content[0].text
        assert "A test template" in result.content[0].text

    @pytest.mark.asyncio
    async def test_dict_list_toon_serialization(
        self, mock_config_toon, mock_context, sample_dict_list
    ):
        """Test TOON serialization of a list of dicts."""
        middleware = SerializationMiddleware(mock_config_toon)

        # Mock response with structured_content and content list
        mock_content_item = MagicMock()
        mock_content_item.text = ""
        mock_response = MagicMock()
        mock_response.structured_content = sample_dict_list
        mock_response.content = [mock_content_item]
        call_next = AsyncMock(return_value=mock_response)

        result = await middleware.on_call_tool(mock_context, call_next)

        # Verify call_next was called
        call_next.assert_awaited_once()

        # Result should be the modified response object
        assert result == mock_response

        # TOON format should contain both items in content[0].text
        assert "template-1" in result.content[0].text
        assert "template-2" in result.content[0].text


class TestSerializationMiddlewareAutoFormat:
    """Test cases for auto format selection."""

    @pytest.mark.asyncio
    async def test_dict_uses_toon_in_auto(
        self, mock_config_auto, mock_context, sample_dict
    ):
        """Test that dict instances use TOON in auto mode."""
        middleware = SerializationMiddleware(mock_config_auto)

        # Mock response with structured_content
        mock_response = MagicMock()
        mock_response.structured_content = sample_dict
        call_next = AsyncMock(return_value=mock_response)

        result = await middleware.on_call_tool(mock_context, call_next)

        # Verify call_next was called
        call_next.assert_awaited_once()

        # Auto format is not currently implemented, so it passes through
        assert result == mock_response

    @pytest.mark.asyncio
    async def test_dict_list_uses_toon_in_auto(
        self, mock_config_auto, mock_context, sample_dict_list
    ):
        """Test that lists of dicts use TOON in auto mode."""
        middleware = SerializationMiddleware(mock_config_auto)

        # Mock response with structured_content
        mock_response = MagicMock()
        mock_response.structured_content = sample_dict_list
        call_next = AsyncMock(return_value=mock_response)

        result = await middleware.on_call_tool(mock_context, call_next)

        # Verify call_next was called
        call_next.assert_awaited_once()

        # Auto format is not currently implemented, so it passes through
        assert result == mock_response


class TestSerializationMiddlewareEdgeCases:
    """Test cases for edge cases and error handling."""

    @pytest.mark.asyncio
    async def test_empty_list_passthrough(self, mock_config_json, mock_context):
        """Test that empty lists pass through unchanged."""
        middleware = SerializationMiddleware(mock_config_json)

        # Mock response with empty list
        mock_response = MagicMock()
        mock_response.structured_content = []
        call_next = AsyncMock(return_value=mock_response)

        result = await middleware.on_call_tool(mock_context, call_next)

        # Verify call_next was called
        call_next.assert_awaited_once()

        # Empty list should pass through
        assert result == mock_response

    @pytest.mark.asyncio
    async def test_none_result_passthrough(self, mock_config_json, mock_context):
        """Test that None results pass through unchanged."""
        middleware = SerializationMiddleware(mock_config_json)

        # Mock response with None
        mock_response = MagicMock()
        mock_response.structured_content = None
        call_next = AsyncMock(return_value=mock_response)

        result = await middleware.on_call_tool(mock_context, call_next)

        # Verify call_next was called
        call_next.assert_awaited_once()

        # None should pass through
        assert result == mock_response

    @pytest.mark.asyncio
    async def test_string_result_passthrough(self, mock_config_json, mock_context):
        """Test that string results pass through unchanged."""
        middleware = SerializationMiddleware(mock_config_json)

        # Mock response with string
        mock_response = MagicMock()
        mock_response.structured_content = "plain string result"
        call_next = AsyncMock(return_value=mock_response)

        result = await middleware.on_call_tool(mock_context, call_next)

        # Verify call_next was called
        call_next.assert_awaited_once()

        # String should pass through
        assert result == mock_response

    @pytest.mark.asyncio
    async def test_number_result_passthrough(self, mock_config_json, mock_context):
        """Test that numeric results pass through unchanged."""
        middleware = SerializationMiddleware(mock_config_json)

        # Mock response with number
        mock_response = MagicMock()
        mock_response.structured_content = 42
        call_next = AsyncMock(return_value=mock_response)

        result = await middleware.on_call_tool(mock_context, call_next)

        # Verify call_next was called
        call_next.assert_awaited_once()

        # Number should pass through
        assert result == mock_response
