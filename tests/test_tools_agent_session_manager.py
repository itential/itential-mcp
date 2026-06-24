# Copyright (c) 2025 Itential, Inc
# GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

import inspect

import pytest
from unittest.mock import AsyncMock, MagicMock, patch

from fastmcp import Context

from itential_mcp.tools import agent_session_manager
from itential_mcp.models.agent_session_manager import (
    GetSessionsResponse,
    DescribeSessionResponse,
)


def _make_context(agent_session_manager_mock=None):
    """Build a mock Context wired up with a client holding the given service mock."""
    context = AsyncMock(spec=Context)
    context.info = AsyncMock()
    context.warning = AsyncMock()

    mock_client = MagicMock()
    if agent_session_manager_mock is not None:
        mock_client.agent_session_manager = agent_session_manager_mock

    context.request_context = MagicMock()
    context.request_context.lifespan_context = MagicMock()
    context.request_context.lifespan_context.get.return_value = mock_client

    return context


class TestModule:
    """Test the agent_session_manager tools module"""

    def test_module_has_tags(self):
        """Test module has __tags__ attribute"""
        assert hasattr(agent_session_manager, "__tags__")

    def test_module_tags_value(self):
        """Test module __tags__ has correct value"""
        assert agent_session_manager.__tags__ == ("agent_session_manager",)

    def test_module_functions_exist(self):
        """Test all expected public functions are present in the module"""
        expected = ["get_sessions", "describe_session"]
        for func_name in expected:
            assert hasattr(agent_session_manager, func_name), (
                f"missing function: {func_name}"
            )
            assert callable(getattr(agent_session_manager, func_name))

    def test_functions_are_async(self):
        """Test that all public tool functions are async coroutines"""
        functions = [
            agent_session_manager.get_sessions,
            agent_session_manager.describe_session,
        ]
        for func in functions:
            assert inspect.iscoroutinefunction(func), (
                f"{func.__name__} must be an async def"
            )


class TestGetSessionsTool:
    """Test the get_sessions tool function"""

    @pytest.mark.asyncio
    async def test_get_sessions_returns_response_with_elements(self):
        """Test get_sessions returns a populated GetSessionsResponse"""
        mock_service = AsyncMock()
        mock_service.get_sessions.return_value = [
            {
                "session_id": "sess-001",
                "agent_name": "network-agent",
                "status": "COMPLETE",
                "started_at": "2025-06-01T10:00:00Z",
                "end_time": "2025-06-01T10:01:00Z",
                "duration_ms": 60000,
            }
        ]
        ctx = _make_context(mock_service)

        result = await agent_session_manager.get_sessions(ctx, None)

        assert isinstance(result, GetSessionsResponse)
        assert len(result.root) == 1
        assert result.root[0].session_id == "sess-001"
        assert result.root[0].agent_name == "network-agent"
        assert result.root[0].status == "COMPLETE"
        assert result.root[0].duration_ms == 60000

    @pytest.mark.asyncio
    async def test_get_sessions_empty_returns_empty_response(self):
        """Test get_sessions with no sessions returns an empty response"""
        mock_service = AsyncMock()
        mock_service.get_sessions.return_value = []
        ctx = _make_context(mock_service)

        result = await agent_session_manager.get_sessions(ctx, None)

        assert isinstance(result, GetSessionsResponse)
        assert len(result.root) == 0

    @pytest.mark.asyncio
    async def test_get_sessions_passes_agent_name_filter(self):
        """Test get_sessions passes agent_name through to the service"""
        mock_service = AsyncMock()
        mock_service.get_sessions.return_value = []
        ctx = _make_context(mock_service)

        await agent_session_manager.get_sessions(ctx, agent_name="my-agent")

        mock_service.get_sessions.assert_called_once_with("my-agent")

    @pytest.mark.asyncio
    async def test_get_sessions_epoch_started_at_converted(self):
        """Test get_sessions converts epoch integer started_at to ISO 8601"""
        mock_service = AsyncMock()
        mock_service.get_sessions.return_value = [
            {
                "session_id": "sess-001",
                "agent_name": None,
                "status": "COMPLETE",
                "started_at": 1748779200000,
                "end_time": None,
                "duration_ms": None,
            }
        ]
        ctx = _make_context(mock_service)

        with patch(
            "itential_mcp.tools.agent_session_manager.timeutils.epoch_to_timestamp"
        ) as mock_ts:
            mock_ts.return_value = "2025-06-01T12:00:00Z"

            result = await agent_session_manager.get_sessions(ctx, None)

        mock_ts.assert_called_with(1748779200000)
        assert result.root[0].started_at == "2025-06-01T12:00:00Z"

    @pytest.mark.asyncio
    async def test_get_sessions_epoch_end_time_converted(self):
        """Test get_sessions converts epoch integer end_time to ISO 8601"""
        mock_service = AsyncMock()
        mock_service.get_sessions.return_value = [
            {
                "session_id": "sess-001",
                "agent_name": None,
                "status": "COMPLETE",
                "started_at": None,
                "end_time": 1748779260000,
                "duration_ms": None,
            }
        ]
        ctx = _make_context(mock_service)

        with patch(
            "itential_mcp.tools.agent_session_manager.timeutils.epoch_to_timestamp"
        ) as mock_ts:
            mock_ts.return_value = "2025-06-01T12:01:00Z"

            result = await agent_session_manager.get_sessions(ctx, None)

        mock_ts.assert_called_with(1748779260000)
        assert result.root[0].end_time == "2025-06-01T12:01:00Z"

    @pytest.mark.asyncio
    async def test_get_sessions_string_timestamps_not_converted(self):
        """Test get_sessions leaves string timestamps untouched"""
        mock_service = AsyncMock()
        mock_service.get_sessions.return_value = [
            {
                "session_id": "sess-001",
                "agent_name": None,
                "status": "COMPLETE",
                "started_at": "2025-06-01T10:00:00Z",
                "end_time": "2025-06-01T10:01:00Z",
                "duration_ms": 60000,
            }
        ]
        ctx = _make_context(mock_service)

        with patch(
            "itential_mcp.tools.agent_session_manager.timeutils.epoch_to_timestamp"
        ) as mock_ts:
            result = await agent_session_manager.get_sessions(ctx, None)

        mock_ts.assert_not_called()
        assert result.root[0].started_at == "2025-06-01T10:00:00Z"
        assert result.root[0].end_time == "2025-06-01T10:01:00Z"


class TestDescribeSessionTool:
    """Test the describe_session tool function"""

    @pytest.mark.asyncio
    async def test_describe_session_complete_with_output(self):
        """Test describe_session returns full detail including agent output"""
        mock_service = AsyncMock()
        mock_service.get_session.return_value = {
            "sessionId": "sess-001",
            "status": "COMPLETE",
            "agentSnapshot": {"name": "network-agent"},
            "startedAt": "2025-06-01T10:00:00Z",
            "endTime": "2025-06-01T10:01:00Z",
            "durationMs": 60000,
        }
        mock_service.get_session_messages.return_value = [
            {
                "type": "tool-call",
                "text": "calling get_device",
                "category": None,
                "timestamp": None,
            },
            {
                "type": "inference-succeeded",
                "text": "Device configured.",
                "category": "output",
                "timestamp": None,
            },
        ]
        ctx = _make_context(mock_service)

        result = await agent_session_manager.describe_session(ctx, "sess-001")

        assert isinstance(result, DescribeSessionResponse)
        assert result.session_id == "sess-001"
        assert result.agent_name == "network-agent"
        assert result.status == "COMPLETE"
        assert result.output == "Device configured."
        assert result.duration_ms == 60000
        assert len(result.messages) == 2

    @pytest.mark.asyncio
    async def test_describe_session_running_no_output(self):
        """Test describe_session for a running session returns output=None"""
        mock_service = AsyncMock()
        mock_service.get_session.return_value = {
            "sessionId": "sess-002",
            "status": "RUNNING",
            "agentSnapshot": {"name": "my-agent"},
        }
        mock_service.get_session_messages.return_value = [
            {
                "type": "tool-call",
                "text": "looking up data",
                "category": None,
                "timestamp": None,
            },
        ]
        ctx = _make_context(mock_service)

        result = await agent_session_manager.describe_session(ctx, "sess-002")

        assert result.status == "RUNNING"
        assert result.output is None
        assert len(result.messages) == 1

    @pytest.mark.asyncio
    async def test_describe_session_no_inference_succeeded_event(self):
        """Test describe_session output is None when no inference-succeeded message"""
        mock_service = AsyncMock()
        mock_service.get_session.return_value = {
            "sessionId": "sess-003",
            "status": "FAILED",
        }
        mock_service.get_session_messages.return_value = [
            {
                "type": "agent-error",
                "text": "something broke",
                "category": None,
                "timestamp": None,
            },
        ]
        ctx = _make_context(mock_service)

        result = await agent_session_manager.describe_session(ctx, "sess-003")

        assert result.output is None
        assert result.status == "FAILED"
        assert len(result.messages) == 1

    @pytest.mark.asyncio
    async def test_describe_session_inference_succeeded_null_text_not_output(self):
        """Test describe_session ignores inference-succeeded with None text for output"""
        mock_service = AsyncMock()
        mock_service.get_session.return_value = {
            "sessionId": "sess-004",
            "status": "COMPLETE",
        }
        mock_service.get_session_messages.return_value = [
            {
                "type": "inference-succeeded",
                "text": None,
                "category": None,
                "timestamp": None,
            },
        ]
        ctx = _make_context(mock_service)

        result = await agent_session_manager.describe_session(ctx, "sess-004")

        assert result.output is None

    @pytest.mark.asyncio
    async def test_describe_session_epoch_timestamps_on_session_converted(self):
        """Test describe_session converts epoch timestamps on the session record"""
        mock_service = AsyncMock()
        mock_service.get_session.return_value = {
            "sessionId": "sess-005",
            "status": "COMPLETE",
            "startedAt": 1748779200000,
            "endTime": 1748779260000,
        }
        mock_service.get_session_messages.return_value = []
        ctx = _make_context(mock_service)

        with patch(
            "itential_mcp.tools.agent_session_manager.timeutils.epoch_to_timestamp"
        ) as mock_ts:
            mock_ts.side_effect = lambda ms: f"ts({ms})"
            result = await agent_session_manager.describe_session(ctx, "sess-005")

        assert result.started_at == "ts(1748779200000)"
        assert result.end_time == "ts(1748779260000)"

    @pytest.mark.asyncio
    async def test_describe_session_epoch_timestamps_on_messages_converted(self):
        """Test describe_session converts epoch timestamps on message records"""
        mock_service = AsyncMock()
        mock_service.get_session.return_value = {
            "sessionId": "sess-006",
            "status": "COMPLETE",
        }
        mock_service.get_session_messages.return_value = [
            {
                "type": "tool-call",
                "text": "hi",
                "category": None,
                "timestamp": 1748779200000,
            },
        ]
        ctx = _make_context(mock_service)

        with patch(
            "itential_mcp.tools.agent_session_manager.timeutils.epoch_to_timestamp"
        ) as mock_ts:
            mock_ts.return_value = "2025-06-01T12:00:00Z"
            result = await agent_session_manager.describe_session(ctx, "sess-006")

        assert result.messages[0].timestamp == "2025-06-01T12:00:00Z"

    @pytest.mark.asyncio
    async def test_describe_session_no_agent_snapshot(self):
        """Test describe_session handles missing agentSnapshot gracefully"""
        mock_service = AsyncMock()
        mock_service.get_session.return_value = {
            "sessionId": "sess-007",
            "status": "COMPLETE",
        }
        mock_service.get_session_messages.return_value = []
        ctx = _make_context(mock_service)

        result = await agent_session_manager.describe_session(ctx, "sess-007")

        assert result.agent_name is None

    @pytest.mark.asyncio
    async def test_describe_session_client_error_propagates(self):
        """Test describe_session propagates errors from the service layer"""
        mock_service = AsyncMock()
        mock_service.get_session.side_effect = Exception("session not found")
        ctx = _make_context(mock_service)

        with pytest.raises(Exception, match="session not found"):
            await agent_session_manager.describe_session(ctx, "sess-missing")
