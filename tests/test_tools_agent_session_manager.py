# Copyright (c) 2025 Itential, Inc
# GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

import inspect
import typing

import pytest
from unittest.mock import AsyncMock, MagicMock, patch

from fastmcp import Context

from itential_mcp.core.exceptions import ValidationException
from itential_mcp.tools import agent_session_manager
from itential_mcp.models.agent_session_manager import (
    GetSessionsResponse,
    DescribeSessionResponse,
    GetAgentTokenUsageResponse,
    GetAgentSessionTokenUsageResponse,
    DescribeSessionTokenUsageResponse,
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
        expected = [
            "get_sessions",
            "describe_session",
            "get_agent_token_usage",
            "get_agent_session_token_usage",
            "describe_session_token_usage",
        ]
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
            agent_session_manager.get_agent_token_usage,
            agent_session_manager.get_agent_session_token_usage,
            agent_session_manager.describe_session_token_usage,
        ]
        for func in functions:
            assert inspect.iscoroutinefunction(func), (
                f"{func.__name__} must be an async def"
            )


def _raw_session(session_id="sess-001", **overrides):
    """Build a raw platform session item."""
    item = {
        "sessionId": session_id,
        "agentSnapshot": {"name": "network-agent"},
        "status": "COMPLETE",
        "startedAt": "2025-06-01T10:00:00Z",
        "endTime": "2025-06-01T10:01:00Z",
        "durationMs": 60000,
        "totalInputTokens": 12345,
        "totalOutputTokens": 678,
    }
    item.update(overrides)
    return item


class TestGetSessionsTool:
    """Test the get_sessions tool function"""

    @pytest.mark.asyncio
    async def test_get_sessions_returns_response_with_elements(self):
        """Test get_sessions returns a populated GetSessionsResponse"""
        mock_service = AsyncMock()
        mock_service.get_sessions_page.return_value = ([_raw_session()], 1)
        ctx = _make_context(mock_service)

        result = await agent_session_manager.get_sessions(ctx, None)

        assert isinstance(result, GetSessionsResponse)
        assert len(result.results) == 1
        element = result.results[0]
        assert element.session_id == "sess-001"
        assert element.agent_name == "network-agent"
        assert element.status == "COMPLETE"
        assert element.duration_ms == 60000
        assert element.total_input_tokens == 12345
        assert element.total_output_tokens == 678

    @pytest.mark.asyncio
    async def test_get_sessions_defaults(self):
        """Test default limit/skip are passed and reflected in the response"""
        mock_service = AsyncMock()
        mock_service.get_sessions_page.return_value = ([], 0)
        ctx = _make_context(mock_service)

        result = await agent_session_manager.get_sessions(ctx, None)

        mock_service.get_sessions_page.assert_called_once_with(limit=100, skip=0)
        assert result.results == []
        assert result.total == 0
        assert result.returned == 0
        assert result.limit == 100
        assert result.skip == 0
        assert result.has_more is False

    @pytest.mark.asyncio
    async def test_get_sessions_passes_limit_skip(self):
        """Test limit and skip are passed to the paged service call"""
        mock_service = AsyncMock()
        mock_service.get_sessions_page.return_value = ([], 0)
        ctx = _make_context(mock_service)

        await agent_session_manager.get_sessions(ctx, None, limit=25, skip=50)

        mock_service.get_sessions_page.assert_called_once_with(limit=25, skip=50)

    @pytest.mark.asyncio
    async def test_get_sessions_empty_page_has_more_false(self):
        """Test has_more is false when the platform returns an empty page even
        though skip + 0 < total"""
        mock_service = AsyncMock()
        mock_service.get_sessions_page.return_value = ([], 10)
        ctx = _make_context(mock_service)

        result = await agent_session_manager.get_sessions(ctx, None, skip=0)

        assert result.has_more is False
        assert result.total == 10

    @staticmethod
    def _norm(session_id, started_at, agent="my-agent"):
        return {
            "session_id": session_id,
            "agent_name": agent,
            "status": "COMPLETE",
            "started_at": started_at,
            "end_time": None,
            "duration_ms": None,
            "total_input_tokens": None,
            "total_output_tokens": None,
        }

    def _agent_ctx(self, count=5):
        mock_service = AsyncMock()
        # deliberately oldest-first to prove the tool sorts newest-first
        mock_service.get_sessions.return_value = [
            self._norm(f"s{i}", f"2025-06-0{i + 1}T00:00:00Z") for i in range(count)
        ]
        return mock_service, _make_context(mock_service)

    @pytest.mark.asyncio
    async def test_agent_name_uses_client_side_path(self):
        """Test agent_name calls the full-scan service, not the paged one"""
        mock_service, ctx = self._agent_ctx()

        await agent_session_manager.get_sessions(ctx, agent_name="my-agent")

        mock_service.get_sessions.assert_called_once_with("my-agent")
        mock_service.get_sessions_page.assert_not_called()

    @pytest.mark.asyncio
    async def test_agent_name_slices_newest_first(self):
        """Test results are sorted newest-first and sliced by skip/limit"""
        _, ctx = self._agent_ctx(5)

        result = await agent_session_manager.get_sessions(
            ctx, agent_name="my-agent", limit=2, skip=1
        )

        assert [e.session_id for e in result.results] == ["s3", "s2"]
        assert result.total == 5
        assert result.returned == 2
        assert result.limit == 2
        assert result.skip == 1
        assert result.has_more is True

    @pytest.mark.asyncio
    async def test_agent_name_last_page_has_more_false(self):
        """Test has_more is false when the slice reaches the filtered total"""
        _, ctx = self._agent_ctx(5)

        result = await agent_session_manager.get_sessions(
            ctx, agent_name="my-agent", limit=2, skip=3
        )

        assert [e.session_id for e in result.results] == ["s1", "s0"]
        assert result.total == 5
        assert result.has_more is False

    @pytest.mark.asyncio
    async def test_agent_name_skip_beyond_end(self):
        """Test skip beyond the filtered set yields an empty page"""
        _, ctx = self._agent_ctx(3)

        result = await agent_session_manager.get_sessions(
            ctx, agent_name="my-agent", limit=10, skip=50
        )

        assert result.results == []
        assert result.total == 3
        assert result.returned == 0
        assert result.has_more is False

    @pytest.mark.asyncio
    async def test_agent_name_no_matches(self):
        """Test no matching sessions yields an empty response"""
        mock_service = AsyncMock()
        mock_service.get_sessions.return_value = []
        ctx = _make_context(mock_service)

        result = await agent_session_manager.get_sessions(ctx, agent_name="nope")

        assert result.results == []
        assert result.total == 0
        assert result.has_more is False

    @pytest.mark.asyncio
    async def test_agent_name_epoch_sorted_and_converted(self):
        """Test epoch started_at values sort numerically and are converted"""
        mock_service = AsyncMock()
        mock_service.get_sessions.return_value = [
            self._norm("old", 1000),
            self._norm("new", 2000),
            self._norm("none", None),
        ]
        ctx = _make_context(mock_service)

        with patch(
            "itential_mcp.tools.agent_session_manager.timeutils.epoch_to_timestamp"
        ) as mock_ts:
            mock_ts.side_effect = lambda v: f"ts-{v}"
            result = await agent_session_manager.get_sessions(
                ctx, agent_name="my-agent"
            )

        assert [e.session_id for e in result.results] == ["new", "old", "none"]
        assert result.results[0].started_at == "ts-2000"

    @pytest.mark.asyncio
    async def test_get_sessions_has_more_true(self):
        """Test has_more is true when more sessions remain"""
        mock_service = AsyncMock()
        mock_service.get_sessions_page.return_value = (
            [_raw_session("a"), _raw_session("b")],
            10,
        )
        ctx = _make_context(mock_service)

        result = await agent_session_manager.get_sessions(ctx, None, limit=2, skip=4)

        assert result.total == 10
        assert result.returned == 2
        assert result.skip == 4
        assert result.limit == 2
        assert result.has_more is True

    @pytest.mark.asyncio
    async def test_get_sessions_has_more_false_on_last_page(self):
        """Test has_more is false when the page reaches the total"""
        mock_service = AsyncMock()
        mock_service.get_sessions_page.return_value = (
            [_raw_session("a"), _raw_session("b")],
            6,
        )
        ctx = _make_context(mock_service)

        result = await agent_session_manager.get_sessions(ctx, None, limit=2, skip=4)

        assert result.has_more is False

    @pytest.mark.asyncio
    async def test_get_sessions_drops_session_without_id(self):
        """Test rows with no sessionId are skipped, returned counts kept rows,
        and has_more is computed from the raw item count"""
        mock_service = AsyncMock()
        mock_service.get_sessions_page.return_value = (
            [_raw_session("a"), _raw_session(None), _raw_session("c")],
            10,
        )
        ctx = _make_context(mock_service)

        result = await agent_session_manager.get_sessions(ctx, None, limit=3)

        assert [e.session_id for e in result.results] == ["a", "c"]
        assert result.returned == 2
        assert result.returned < result.limit
        assert result.has_more is True

    @pytest.mark.asyncio
    async def test_get_sessions_has_more_uses_raw_count_when_row_dropped(self):
        """Test a dropped row does not make has_more true on the last page"""
        mock_service = AsyncMock()
        mock_service.get_sessions_page.return_value = (
            [_raw_session("a"), _raw_session(None)],
            2,
        )
        ctx = _make_context(mock_service)

        result = await agent_session_manager.get_sessions(ctx, None, limit=5)

        assert result.returned == 1
        assert result.has_more is False

    @pytest.mark.asyncio
    async def test_get_sessions_missing_token_fields_default_none(self):
        """Test get_sessions tolerates a payload without token fields"""
        mock_service = AsyncMock()
        item = _raw_session()
        del item["totalInputTokens"]
        del item["totalOutputTokens"]
        mock_service.get_sessions_page.return_value = ([item], 1)
        ctx = _make_context(mock_service)

        result = await agent_session_manager.get_sessions(ctx, None)

        assert result.results[0].total_input_tokens is None
        assert result.results[0].total_output_tokens is None

    @pytest.mark.asyncio
    async def test_get_sessions_missing_agent_snapshot(self):
        """Test get_sessions tolerates a missing agentSnapshot"""
        mock_service = AsyncMock()
        item = _raw_session()
        del item["agentSnapshot"]
        mock_service.get_sessions_page.return_value = ([item], 1)
        ctx = _make_context(mock_service)

        result = await agent_session_manager.get_sessions(ctx, None)

        assert result.results[0].agent_name is None

    @pytest.mark.asyncio
    async def test_get_sessions_epoch_timestamps_converted(self):
        """Test get_sessions converts epoch integer timestamps to ISO 8601"""
        mock_service = AsyncMock()
        mock_service.get_sessions_page.return_value = (
            [_raw_session(startedAt=1748779200000, endTime=1748779260000)],
            1,
        )
        ctx = _make_context(mock_service)

        with patch(
            "itential_mcp.tools.agent_session_manager.timeutils.epoch_to_timestamp"
        ) as mock_ts:
            mock_ts.side_effect = lambda v: f"ts-{v}"

            result = await agent_session_manager.get_sessions(ctx, None)

        assert result.results[0].started_at == "ts-1748779200000"
        assert result.results[0].end_time == "ts-1748779260000"

    @pytest.mark.asyncio
    async def test_get_sessions_string_timestamps_not_converted(self):
        """Test get_sessions leaves string timestamps untouched"""
        mock_service = AsyncMock()
        mock_service.get_sessions_page.return_value = ([_raw_session()], 1)
        ctx = _make_context(mock_service)

        with patch(
            "itential_mcp.tools.agent_session_manager.timeutils.epoch_to_timestamp"
        ) as mock_ts:
            result = await agent_session_manager.get_sessions(ctx, None)

        mock_ts.assert_not_called()
        assert result.results[0].started_at == "2025-06-01T10:00:00Z"
        assert result.results[0].end_time == "2025-06-01T10:01:00Z"

    @pytest.mark.parametrize("kwargs", [{"limit": 0}, {"limit": 101}, {"skip": -1}])
    def test_get_sessions_field_bounds(self, kwargs):
        """Test the limit/skip Field bounds reject out-of-range values"""
        from pydantic import TypeAdapter, ValidationError

        hints = typing.get_type_hints(
            agent_session_manager.get_sessions, include_extras=True
        )
        name, value = next(iter(kwargs.items()))
        adapter = TypeAdapter(hints[name])

        with pytest.raises(ValidationError):
            adapter.validate_python(value)

        # boundaries are accepted
        adapter.validate_python(1 if name == "limit" else 0)
        adapter.validate_python(100 if name == "limit" else 5)


class TestDescribeSessionTool:
    """Test the describe_session tool function"""

    @pytest.mark.asyncio
    async def test_describe_session_keeps_end_turn_reasoning_event(self):
        """Test describe_session keeps an AGENT_REASONING event with
        data.stopReason == 'end_turn' and maps its fields correctly"""
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
                "eventId": "evt-001",
                "sequenceNumber": 1,
                "timestamp": 1748779200000,
                "text": "Device configured.",
                "category": "AGENT_REASONING",
                "data": {"stopReason": "end_turn"},
            },
        ]
        ctx = _make_context(mock_service)

        with patch(
            "itential_mcp.tools.agent_session_manager.timeutils.epoch_to_timestamp"
        ) as mock_ts:
            mock_ts.return_value = "2025-06-01T10:00:00Z"
            result = await agent_session_manager.describe_session(ctx, "sess-001")

        assert isinstance(result, DescribeSessionResponse)
        assert result.session_id == "sess-001"
        assert result.agent_name == "network-agent"
        assert result.status == "COMPLETE"
        assert result.duration_ms == 60000
        assert len(result.reasoning_events) == 1

        event = result.reasoning_events[0]
        assert event.event_id == "evt-001"
        assert event.sequence_number == 1
        assert event.timestamp == "2025-06-01T10:00:00Z"
        assert event.text == "Device configured."
        mock_ts.assert_called_with(1748779200000)

    @pytest.mark.asyncio
    async def test_describe_session_drops_tool_use_stop_reason(self):
        """Test describe_session drops an AGENT_REASONING event whose
        data.stopReason is 'tool_use' (mid-turn, not yet final)"""
        mock_service = AsyncMock()
        mock_service.get_session.return_value = {
            "sessionId": "sess-002",
            "status": "RUNNING",
            "agentSnapshot": {"name": "my-agent"},
        }
        mock_service.get_session_messages.return_value = [
            {
                "eventId": "evt-010",
                "sequenceNumber": 1,
                "timestamp": None,
                "text": "thinking about which tool to call",
                "category": "AGENT_REASONING",
                "data": {"stopReason": "tool_use"},
            },
        ]
        ctx = _make_context(mock_service)

        result = await agent_session_manager.describe_session(ctx, "sess-002")

        assert result.status == "RUNNING"
        # No end_turn event exists, so output falls back to the last
        # AGENT_REASONING text while reasoning_events stays filtered.
        assert result.output == "thinking about which tool to call"
        assert len(result.reasoning_events) == 0

    @pytest.mark.asyncio
    async def test_describe_session_drops_empty_data_reasoning_event(self):
        """Test describe_session drops an AGENT_REASONING event with no
        data (no stopReason present at all)"""
        mock_service = AsyncMock()
        mock_service.get_session.return_value = {
            "sessionId": "sess-003",
            "status": "RUNNING",
        }
        mock_service.get_session_messages.return_value = [
            {
                "eventId": "evt-020",
                "sequenceNumber": 1,
                "timestamp": None,
                "text": "partial reasoning",
                "category": "AGENT_REASONING",
                "data": {},
            },
        ]
        ctx = _make_context(mock_service)

        result = await agent_session_manager.describe_session(ctx, "sess-003")

        assert result.output == "partial reasoning"
        assert len(result.reasoning_events) == 0

    @pytest.mark.asyncio
    async def test_describe_session_drops_tool_execution_event(self):
        """Test describe_session drops a tool-execution event (category
        does not match AGENT_REASONING)"""
        mock_service = AsyncMock()
        mock_service.get_session.return_value = {
            "sessionId": "sess-004",
            "status": "COMPLETE",
        }
        mock_service.get_session_messages.return_value = [
            {
                "eventId": "evt-030",
                "sequenceNumber": 1,
                "timestamp": None,
                "text": "calling get_device",
                "category": "TOOL_EXECUTION",
                "data": {"stopReason": "end_turn"},
            },
        ]
        ctx = _make_context(mock_service)

        result = await agent_session_manager.describe_session(ctx, "sess-004")

        assert result.output is None
        assert len(result.reasoning_events) == 0

    @pytest.mark.asyncio
    async def test_describe_session_drops_session_status_event(self):
        """Test describe_session drops a session-status event (category
        does not match AGENT_REASONING)"""
        mock_service = AsyncMock()
        mock_service.get_session.return_value = {
            "sessionId": "sess-005",
            "status": "FAILED",
        }
        mock_service.get_session_messages.return_value = [
            {
                "eventId": "evt-040",
                "sequenceNumber": 1,
                "timestamp": None,
                "text": "session failed",
                "category": "SESSION_STATUS",
                "data": None,
            },
        ]
        ctx = _make_context(mock_service)

        result = await agent_session_manager.describe_session(ctx, "sess-005")

        assert result.output is None
        assert result.status == "FAILED"
        assert len(result.reasoning_events) == 0

    @pytest.mark.asyncio
    async def test_describe_session_output_is_last_kept_event_text(self):
        """Test describe_session's output equals the last kept reasoning
        event's text, not the first"""
        mock_service = AsyncMock()
        mock_service.get_session.return_value = {
            "sessionId": "sess-006",
            "status": "COMPLETE",
        }
        mock_service.get_session_messages.return_value = [
            {
                "eventId": "evt-050",
                "sequenceNumber": 1,
                "timestamp": None,
                "text": "first turn output",
                "category": "AGENT_REASONING",
                "data": {"stopReason": "end_turn"},
            },
            {
                "eventId": "evt-051",
                "sequenceNumber": 2,
                "timestamp": None,
                "text": "calling a tool",
                "category": "TOOL_EXECUTION",
                "data": {"stopReason": "end_turn"},
            },
            {
                "eventId": "evt-052",
                "sequenceNumber": 3,
                "timestamp": None,
                "text": "final turn output",
                "category": "AGENT_REASONING",
                "data": {"stopReason": "end_turn"},
            },
        ]
        ctx = _make_context(mock_service)

        result = await agent_session_manager.describe_session(ctx, "sess-006")

        assert len(result.reasoning_events) == 2
        assert result.output == "final turn output"

    @staticmethod
    def _mixed_service():
        mock_service = AsyncMock()
        mock_service.get_session.return_value = {
            "sessionId": "sess-mix",
            "status": "COMPLETE",
        }
        mock_service.get_session_messages.return_value = [
            {
                "eventId": "e1",
                "sequenceNumber": 1,
                "timestamp": 1748779200000,
                "text": "calling tool",
                "category": "AGENT_REASONING",
                "data": {"stopReason": "tool_use"},
            },
            {
                "eventId": "e2",
                "sequenceNumber": 2,
                "timestamp": None,
                "text": "tool ran",
                "category": "TOOL_EXECUTION",
                "data": {"stopReason": "end_turn"},
            },
            {
                "eventId": "e3",
                "sequenceNumber": 3,
                "timestamp": None,
                "text": "no data",
                "category": "AGENT_REASONING",
                "data": {},
            },
            {
                "eventId": "e4",
                "sequenceNumber": 4,
                "timestamp": None,
                "text": "all done",
                "category": "AGENT_REASONING",
                "data": {"stopReason": "end_turn"},
            },
            {
                "eventId": "e5",
                "sequenceNumber": 5,
                "timestamp": None,
                "text": "trailing step",
                "category": "AGENT_REASONING",
                "data": {"stopReason": "tool_use"},
            },
        ]
        return mock_service

    @pytest.mark.asyncio
    async def test_describe_session_default_filters_to_end_turn(self):
        """Default mode keeps only end_turn events and output is that text"""
        ctx = _make_context(self._mixed_service())

        result = await agent_session_manager.describe_session(ctx, "sess-mix")

        assert [e.event_id for e in result.reasoning_events] == ["e4"]
        assert result.reasoning_events[0].stop_reason == "end_turn"
        assert result.output == "all done"

    @pytest.mark.asyncio
    async def test_describe_session_include_all_events(self):
        """include_all_events keeps every AGENT_REASONING event in order"""
        ctx = _make_context(self._mixed_service())

        result = await agent_session_manager.describe_session(
            ctx, "sess-mix", include_all_events=True
        )

        assert [e.event_id for e in result.reasoning_events] == [
            "e1",
            "e3",
            "e4",
            "e5",
        ]
        assert [e.stop_reason for e in result.reasoning_events] == [
            "tool_use",
            None,
            "end_turn",
            "tool_use",
        ]
        # An end_turn event exists, so output is still its text
        assert result.output == "all done"

    @pytest.mark.asyncio
    async def test_describe_session_include_all_converts_timestamps(self):
        """include_all_events still converts epoch timestamps"""
        ctx = _make_context(self._mixed_service())

        with patch(
            "itential_mcp.tools.agent_session_manager.timeutils.epoch_to_timestamp"
        ) as mock_ts:
            mock_ts.return_value = "2025-06-01T10:00:00Z"
            result = await agent_session_manager.describe_session(
                ctx, "sess-mix", include_all_events=True
            )

        assert result.reasoning_events[0].timestamp == "2025-06-01T10:00:00Z"

    @staticmethod
    def _turn_events():
        def reasoning(eid, ts, typ, text, data):
            return {
                "eventId": eid,
                "sessionId": "s",
                "timestamp": ts,
                "sequenceNumber": int(ts // 1000),
                "category": "AGENT_REASONING",
                "type": typ,
                "text": text,
                "data": data,
            }

        def tool(eid, ts, name, status="succeeded", err=None):
            return {
                "eventId": eid,
                "timestamp": ts,
                "sequenceNumber": None,
                "category": "TOOL_CALLED",
                "type": "tool-execution",
                "text": "",
                "data": {
                    "toolName": name,
                    "toolType": "method",
                    "summary": f"ran {name}",
                    "status": status,
                    "durationMs": 7,
                    "errorMessage": err,
                    "input": {"secret": "x"},
                    "output": "big",
                },
            }

        usage = {"inputTokens": 10, "outputTokens": 3}
        return [
            reasoning("p1", 1000, "inference-pending", "", {}),
            reasoning(
                "r1",
                2000,
                "inference-succeeded",
                "",
                {"durationMs": 50, "stopReason": "tool_use", "tokenUsage": usage},
            ),
            tool("t1", 2025, "alpha"),
            tool("t2", 2026, "beta", "failed", "boom"),
            reasoning("p2", 3000, "inference-pending", None, {}),
            reasoning(
                "r2",
                4000,
                "inference-succeeded",
                "narration",
                {"durationMs": 60, "stopReason": "tool_use", "tokenUsage": usage},
            ),
            tool("t3", 4025, "gamma"),
            reasoning("p3", 5000, "inference-pending", "", {}),
            reasoning(
                "r3",
                6000,
                "inference-succeeded",
                "all done",
                {"stopReason": "end_turn"},
            ),
        ]

    @staticmethod
    def _svc(events):
        mock_service = AsyncMock()
        mock_service.get_session.return_value = {"sessionId": "s", "status": "OK"}
        mock_service.get_session_messages.return_value = events
        return mock_service

    @pytest.mark.asyncio
    async def test_default_mode_unchanged_with_tool_and_pending_events(self):
        """Default mode ignores pending markers and tool events"""
        ctx = _make_context(self._svc(self._turn_events()))

        result = await agent_session_manager.describe_session(ctx, "s")

        assert [e.event_id for e in result.reasoning_events] == ["r3"]
        assert result.reasoning_events[0].tool_calls == []
        assert result.output == "all done"

    @pytest.mark.asyncio
    async def test_include_all_groups_tool_calls_and_metrics(self):
        """Pending markers dropped, tools grouped under preceding turn"""
        ctx = _make_context(self._svc(self._turn_events()))

        result = await agent_session_manager.describe_session(
            ctx, "s", include_all_events=True
        )

        events = result.reasoning_events
        assert [e.event_id for e in events] == ["r1", "r2", "r3"]
        assert events[0].duration_ms == 50
        assert events[0].input_tokens == 10
        assert events[0].output_tokens == 3
        assert events[0].text == ""
        assert [c.tool_name for c in events[0].tool_calls] == ["alpha", "beta"]
        failed = events[0].tool_calls[1]
        assert failed.status == "failed"
        assert failed.error_message == "boom"
        assert failed.tool_type == "method"
        assert failed.summary == "ran beta"
        assert failed.duration_ms == 7
        assert "input" not in failed.model_dump()
        assert [c.tool_name for c in events[1].tool_calls] == ["gamma"]
        assert events[2].tool_calls == []
        assert events[2].duration_ms is None
        assert events[2].input_tokens is None
        assert result.output == "all done"

    @pytest.mark.asyncio
    async def test_include_all_sorts_out_of_order_by_timestamp(self):
        """Shuffled input is ordered by timestamp, not sequenceNumber"""
        events = list(reversed(self._turn_events()))
        ctx = _make_context(self._svc(events))

        result = await agent_session_manager.describe_session(
            ctx, "s", include_all_events=True
        )

        assert [e.event_id for e in result.reasoning_events] == ["r1", "r2", "r3"]
        assert [c.tool_name for c in result.reasoning_events[0].tool_calls] == [
            "alpha",
            "beta",
        ]

    @pytest.mark.asyncio
    async def test_include_all_tolerates_missing_keys_and_type(self):
        """Missing data keys, missing type and noise detection without type"""
        events = [
            {"eventId": "n", "category": "AGENT_REASONING", "text": "", "data": {}},
            {"eventId": "a", "category": "AGENT_REASONING", "text": "hi"},
            {
                "eventId": "b",
                "category": "AGENT_REASONING",
                "type": "inference-succeeded",
                "text": None,
                "data": {"tokenUsage": None},
            },
            {"eventId": "t", "category": "TOOL_CALLED", "data": None},
        ]
        ctx = _make_context(self._svc(events))

        result = await agent_session_manager.describe_session(
            ctx, "s", include_all_events=True
        )

        assert [e.event_id for e in result.reasoning_events] == ["a", "b"]
        assert result.reasoning_events[1].input_tokens is None
        call = result.reasoning_events[1].tool_calls[0]
        assert call.tool_name is None and call.status is None

    @pytest.mark.asyncio
    async def test_orphan_tool_event_attached_to_first_turn(self):
        """A tool event before any kept turn goes to the first turn"""
        events = [
            {
                "eventId": "t0",
                "category": "TOOL_CALLED",
                "data": {"toolName": "early"},
            },
            {
                "eventId": "r1",
                "category": "AGENT_REASONING",
                "type": "inference-succeeded",
                "text": "x",
                "data": {"stopReason": "end_turn"},
            },
        ]
        ctx = _make_context(self._svc(events))

        result = await agent_session_manager.describe_session(
            ctx, "s", include_all_events=True
        )

        assert [c.tool_name for c in result.reasoning_events[0].tool_calls] == ["early"]

    @pytest.mark.asyncio
    async def test_orphan_tool_event_dropped_without_turns(self):
        """With no turn at all, tool events are dropped without error"""
        events = [
            {"eventId": "t0", "category": "TOOL_CALLED", "data": {"toolName": "a"}}
        ]
        ctx = _make_context(self._svc(events))

        result = await agent_session_manager.describe_session(
            ctx, "s", include_all_events=True
        )

        assert result.reasoning_events == []
        assert result.output is None

    @pytest.mark.asyncio
    async def test_output_fallback_ignores_tool_events(self):
        """Tool event text never becomes output"""
        events = [
            {
                "eventId": "r1",
                "timestamp": 1,
                "category": "AGENT_REASONING",
                "type": "inference-succeeded",
                "text": "turn text",
                "data": {"stopReason": "tool_use"},
            },
            {
                "eventId": "t",
                "timestamp": 2,
                "category": "TOOL_CALLED",
                "text": "tool text",
                "data": {"toolName": "a"},
            },
        ]
        for include_all in (False, True):
            ctx = _make_context(self._svc(events))
            result = await agent_session_manager.describe_session(
                ctx, "s", include_all_events=include_all
            )
            assert result.output == "turn text"

    @pytest.mark.asyncio
    @pytest.mark.parametrize("include_all", [False, True])
    async def test_describe_session_output_fallback_no_end_turn(self, include_all):
        """With no end_turn event, output is the last AGENT_REASONING text"""
        mock_service = AsyncMock()
        mock_service.get_session.return_value = {
            "sessionId": "sess-tool",
            "status": "COMPLETE",
        }
        mock_service.get_session_messages.return_value = [
            {
                "eventId": f"t{i}",
                "sequenceNumber": i,
                "text": f"turn {i}",
                "category": "AGENT_REASONING",
                "data": {"stopReason": "tool_use"},
            }
            for i in range(1, 4)
        ]
        ctx = _make_context(mock_service)

        result = await agent_session_manager.describe_session(
            ctx, "sess-tool", include_all_events=include_all
        )

        assert result.output == "turn 3"
        assert len(result.reasoning_events) == (3 if include_all else 0)

    @pytest.mark.asyncio
    async def test_describe_session_include_all_excludes_other_categories(self):
        """Non-reasoning categories are excluded even with include_all_events"""
        mock_service = AsyncMock()
        mock_service.get_session.return_value = {
            "sessionId": "sess-cat",
            "status": "COMPLETE",
        }
        mock_service.get_session_messages.return_value = [
            {"eventId": "x", "category": "TOOL_EXECUTION", "text": "a", "data": {}},
            {"eventId": "y", "category": "SESSION_STATUS", "text": "b", "data": None},
        ]
        ctx = _make_context(mock_service)

        result = await agent_session_manager.describe_session(
            ctx, "sess-cat", include_all_events=True
        )

        assert result.reasoning_events == []
        assert result.output is None

    @pytest.mark.asyncio
    @pytest.mark.parametrize("include_all", [False, True])
    async def test_describe_session_fallback_skips_empty_trailing_text(
        self, include_all
    ):
        """Fallback skips trailing None/empty/whitespace-only text events"""
        mock_service = AsyncMock()
        mock_service.get_session.return_value = {
            "sessionId": "s",
            "status": "FAILED",
        }
        mock_service.get_session_messages.return_value = [
            {
                "eventId": "a",
                "category": "AGENT_REASONING",
                "text": "real text",
                "data": {"stopReason": "tool_use"},
            },
            {
                "eventId": "b",
                "category": "AGENT_REASONING",
                "text": "",
                "data": {"stopReason": "tool_use"},
            },
            {"eventId": "c", "category": "AGENT_REASONING", "text": None, "data": {}},
            {
                "eventId": "d",
                "category": "AGENT_REASONING",
                "text": "  \n",
                "data": None,
            },
        ]
        ctx = _make_context(mock_service)

        result = await agent_session_manager.describe_session(
            ctx, "s", include_all_events=include_all
        )

        assert result.output == "real text"

    @pytest.mark.asyncio
    async def test_describe_session_fallback_all_empty_is_none(self):
        """All-empty reasoning text gives output None"""
        mock_service = AsyncMock()
        mock_service.get_session.return_value = {"sessionId": "s", "status": "X"}
        mock_service.get_session_messages.return_value = [
            {
                "eventId": "a",
                "category": "AGENT_REASONING",
                "text": "",
                "data": {"stopReason": "tool_use"},
            },
            {"eventId": "b", "category": "AGENT_REASONING", "text": None, "data": {}},
        ]
        ctx = _make_context(mock_service)

        result = await agent_session_manager.describe_session(ctx, "s")

        assert result.output is None

    @pytest.mark.asyncio
    async def test_describe_session_end_turn_null_text_still_none(self):
        """An end_turn event with null text keeps output None (unchanged)"""
        mock_service = AsyncMock()
        mock_service.get_session.return_value = {"sessionId": "s", "status": "X"}
        mock_service.get_session_messages.return_value = [
            {
                "eventId": "a",
                "category": "AGENT_REASONING",
                "text": "earlier",
                "data": {"stopReason": "tool_use"},
            },
            {
                "eventId": "b",
                "category": "AGENT_REASONING",
                "text": None,
                "data": {"stopReason": "end_turn"},
            },
        ]
        ctx = _make_context(mock_service)

        result = await agent_session_manager.describe_session(ctx, "s")

        assert result.output is None

    @pytest.mark.asyncio
    async def test_describe_session_no_kept_events_output_none(self):
        """Test describe_session's output is None when nothing is kept"""
        mock_service = AsyncMock()
        mock_service.get_session.return_value = {
            "sessionId": "sess-007",
            "status": "FAILED",
        }
        mock_service.get_session_messages.return_value = [
            {
                "eventId": "evt-060",
                "sequenceNumber": 1,
                "timestamp": None,
                "text": "something broke",
                "category": "SESSION_STATUS",
                "data": None,
            },
        ]
        ctx = _make_context(mock_service)

        result = await agent_session_manager.describe_session(ctx, "sess-007")

        assert result.output is None
        assert result.reasoning_events == []

    @pytest.mark.asyncio
    async def test_describe_session_epoch_timestamps_on_session_converted(self):
        """Test describe_session converts epoch timestamps on the session record"""
        mock_service = AsyncMock()
        mock_service.get_session.return_value = {
            "sessionId": "sess-008",
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
            result = await agent_session_manager.describe_session(ctx, "sess-008")

        assert result.started_at == "ts(1748779200000)"
        assert result.end_time == "ts(1748779260000)"

    @pytest.mark.asyncio
    async def test_describe_session_no_agent_snapshot(self):
        """Test describe_session handles missing agentSnapshot gracefully"""
        mock_service = AsyncMock()
        mock_service.get_session.return_value = {
            "sessionId": "sess-009",
            "status": "COMPLETE",
        }
        mock_service.get_session_messages.return_value = []
        ctx = _make_context(mock_service)

        result = await agent_session_manager.describe_session(ctx, "sess-009")

        assert result.agent_name is None

    @pytest.mark.asyncio
    async def test_describe_session_client_error_propagates(self):
        """Test describe_session propagates errors from the service layer"""
        mock_service = AsyncMock()
        mock_service.get_session.side_effect = Exception("session not found")
        ctx = _make_context(mock_service)

        with pytest.raises(Exception, match="session not found"):
            await agent_session_manager.describe_session(ctx, "sess-missing")


class TestGetAgentTokenUsageTool:
    """Test the get_agent_token_usage tool function"""

    @staticmethod
    def _session(
        agent_name="CVE Assessment",
        status="COMPLETE",
        started_at="2026-01-01T00:00:00Z",
        input_tokens=100,
        output_tokens=50,
        duration_ms=1000,
    ):
        return {
            "session_id": "sess-x",
            "agent_name": agent_name,
            "status": status,
            "started_at": started_at,
            "end_time": None,
            "duration_ms": duration_ms,
            "total_input_tokens": input_tokens,
            "total_output_tokens": output_tokens,
        }

    @pytest.mark.asyncio
    async def test_groups_by_agent_name_with_correct_math(self):
        """Test aggregation computes sum/avg/min/max correctly per agent"""
        mock_service = AsyncMock()
        mock_service.get_sessions.return_value = [
            self._session(
                agent_name="CVE Assessment",
                input_tokens=100,
                output_tokens=50,
                duration_ms=1000,
            ),
            self._session(
                agent_name="CVE Assessment",
                input_tokens=300,
                output_tokens=150,
                duration_ms=3000,
            ),
            self._session(
                agent_name="Compliance Bot", input_tokens=10, output_tokens=5
            ),
        ]
        ctx = _make_context(mock_service)

        result = await agent_session_manager.get_agent_token_usage(
            ctx, None, False, None, None
        )

        assert isinstance(result, GetAgentTokenUsageResponse)
        by_name = {s.agent_name: s for s in result.root}

        cve = by_name["CVE Assessment"]
        assert cve.session_count == 2
        assert cve.total_input_tokens == 400
        assert cve.total_output_tokens == 200
        assert cve.total_tokens == 600
        assert cve.avg_input_tokens == 200
        assert cve.min_input_tokens == 100
        assert cve.max_input_tokens == 300
        assert cve.avg_output_tokens == 100
        assert cve.min_output_tokens == 50
        assert cve.max_output_tokens == 150
        assert cve.total_duration_ms == 4000
        assert cve.avg_duration_ms == 2000
        assert cve.min_duration_ms == 1000
        assert cve.max_duration_ms == 3000

        compliance = by_name["Compliance Bot"]
        assert compliance.session_count == 1
        assert compliance.total_tokens == 15

    @pytest.mark.asyncio
    async def test_sorted_by_total_tokens_descending(self):
        """Test results are sorted by total_tokens descending"""
        mock_service = AsyncMock()
        mock_service.get_sessions.return_value = [
            self._session(agent_name="Small Agent", input_tokens=1, output_tokens=1),
            self._session(
                agent_name="Big Agent", input_tokens=1000, output_tokens=1000
            ),
        ]
        ctx = _make_context(mock_service)

        result = await agent_session_manager.get_agent_token_usage(
            ctx, None, False, None, None
        )

        assert [s.agent_name for s in result.root] == ["Big Agent", "Small Agent"]

    @pytest.mark.asyncio
    async def test_default_only_includes_complete_sessions(self):
        """Test that by default, only COMPLETE sessions contribute to usage"""
        mock_service = AsyncMock()
        mock_service.get_sessions.return_value = [
            self._session(status="COMPLETE", input_tokens=100, output_tokens=50),
            self._session(status="FAILED", input_tokens=999, output_tokens=999),
            self._session(status="RUNNING", input_tokens=999, output_tokens=999),
            self._session(status="PAUSED", input_tokens=999, output_tokens=999),
        ]
        ctx = _make_context(mock_service)

        result = await agent_session_manager.get_agent_token_usage(
            ctx, None, False, None, None
        )

        assert len(result.root) == 1
        assert result.root[0].session_count == 1
        assert result.root[0].total_input_tokens == 100
        assert result.root[0].total_output_tokens == 50

    @pytest.mark.asyncio
    async def test_include_failed_adds_failed_sessions_only(self):
        """Test include_failed=True folds in FAILED but not other non-terminal statuses"""
        mock_service = AsyncMock()
        mock_service.get_sessions.return_value = [
            self._session(status="COMPLETE", input_tokens=100, output_tokens=50),
            self._session(status="FAILED", input_tokens=10, output_tokens=5),
            self._session(status="RUNNING", input_tokens=999, output_tokens=999),
            self._session(status="PENDING", input_tokens=999, output_tokens=999),
        ]
        ctx = _make_context(mock_service)

        result = await agent_session_manager.get_agent_token_usage(
            ctx, None, True, None, None
        )

        assert len(result.root) == 1
        assert result.root[0].session_count == 2
        assert result.root[0].total_input_tokens == 110
        assert result.root[0].total_output_tokens == 55

    @pytest.mark.asyncio
    async def test_missing_token_values_count_session_as_zero(self):
        """Test a session with null token fields still counts toward session_count"""
        mock_service = AsyncMock()
        mock_service.get_sessions.return_value = [
            self._session(input_tokens=100, output_tokens=50),
            self._session(input_tokens=None, output_tokens=None),
        ]
        ctx = _make_context(mock_service)

        result = await agent_session_manager.get_agent_token_usage(
            ctx, None, False, None, None
        )

        assert len(result.root) == 1
        stats = result.root[0]
        assert stats.session_count == 2
        assert stats.total_input_tokens == 100
        assert stats.total_output_tokens == 50
        assert stats.min_input_tokens == 0
        assert stats.min_output_tokens == 0

    @pytest.mark.asyncio
    async def test_missing_duration_counts_as_zero(self):
        """Test a session with a null duration_ms still counts toward session_count"""
        mock_service = AsyncMock()
        mock_service.get_sessions.return_value = [
            self._session(duration_ms=1000),
            self._session(duration_ms=None),
        ]
        ctx = _make_context(mock_service)

        result = await agent_session_manager.get_agent_token_usage(
            ctx, None, False, None, None
        )

        assert len(result.root) == 1
        stats = result.root[0]
        assert stats.session_count == 2
        assert stats.total_duration_ms == 1000
        assert stats.avg_duration_ms == 500
        assert stats.min_duration_ms == 0
        assert stats.max_duration_ms == 1000

    @pytest.mark.asyncio
    async def test_agent_name_substring_filter_case_insensitive(self):
        """Test agent_name filter matches substrings case-insensitively"""
        mock_service = AsyncMock()
        mock_service.get_sessions.return_value = [
            self._session(agent_name="CVE Assessment"),
            self._session(agent_name="Compliance Bot"),
        ]
        ctx = _make_context(mock_service)

        result = await agent_session_manager.get_agent_token_usage(
            ctx, "cve", False, None, None
        )

        assert len(result.root) == 1
        assert result.root[0].agent_name == "CVE Assessment"

    @pytest.mark.asyncio
    async def test_agent_name_none_sessions_excluded_from_name_filter(self):
        """Test sessions with no agent name are excluded when a name filter is set"""
        mock_service = AsyncMock()
        mock_service.get_sessions.return_value = [
            self._session(agent_name=None),
            self._session(agent_name="CVE Assessment"),
        ]
        ctx = _make_context(mock_service)

        result = await agent_session_manager.get_agent_token_usage(
            ctx, "cve", False, None, None
        )

        assert len(result.root) == 1
        assert result.root[0].agent_name == "CVE Assessment"

    @pytest.mark.asyncio
    async def test_agent_name_none_sessions_grouped_when_unfiltered(self):
        """Test sessions with no agent name land in a None-keyed group, not dropped"""
        mock_service = AsyncMock()
        mock_service.get_sessions.return_value = [
            self._session(agent_name=None, input_tokens=7, output_tokens=3),
        ]
        ctx = _make_context(mock_service)

        result = await agent_session_manager.get_agent_token_usage(
            ctx, None, False, None, None
        )

        assert len(result.root) == 1
        assert result.root[0].agent_name is None
        assert result.root[0].total_tokens == 10

    @pytest.mark.asyncio
    async def test_started_after_filter_excludes_earlier_sessions(self):
        """Test started_after excludes sessions started before the given time"""
        mock_service = AsyncMock()
        mock_service.get_sessions.return_value = [
            self._session(started_at="2026-01-01T00:00:00Z"),
            self._session(started_at="2026-02-01T00:00:00Z"),
        ]
        ctx = _make_context(mock_service)

        result = await agent_session_manager.get_agent_token_usage(
            ctx, None, False, "2026-01-15T00:00:00Z", None
        )

        assert result.root[0].session_count == 1

    @pytest.mark.asyncio
    async def test_started_before_filter_excludes_later_sessions(self):
        """Test started_before excludes sessions started after the given time"""
        mock_service = AsyncMock()
        mock_service.get_sessions.return_value = [
            self._session(started_at="2026-01-01T00:00:00Z"),
            self._session(started_at="2026-02-01T00:00:00Z"),
        ]
        ctx = _make_context(mock_service)

        result = await agent_session_manager.get_agent_token_usage(
            ctx, None, False, None, "2026-01-15T00:00:00Z"
        )

        assert result.root[0].session_count == 1

    @pytest.mark.asyncio
    async def test_started_at_boundary_is_inclusive(self):
        """Test a session started exactly at the boundary is included on both ends"""
        mock_service = AsyncMock()
        mock_service.get_sessions.return_value = [
            self._session(started_at="2026-01-15T00:00:00Z"),
        ]
        ctx = _make_context(mock_service)

        result_after = await agent_session_manager.get_agent_token_usage(
            ctx, None, False, "2026-01-15T00:00:00Z", None
        )
        result_before = await agent_session_manager.get_agent_token_usage(
            ctx, None, False, None, "2026-01-15T00:00:00Z"
        )

        assert result_after.root[0].session_count == 1
        assert result_before.root[0].session_count == 1

    @pytest.mark.asyncio
    async def test_no_matching_sessions_returns_empty_response(self):
        """Test that no matches returns an empty response, not an error"""
        mock_service = AsyncMock()
        mock_service.get_sessions.return_value = [
            self._session(agent_name="Other Agent"),
        ]
        ctx = _make_context(mock_service)

        result = await agent_session_manager.get_agent_token_usage(
            ctx, "nonexistent", False, None, None
        )

        assert isinstance(result, GetAgentTokenUsageResponse)
        assert result.root == []

    @pytest.mark.asyncio
    async def test_invalid_started_after_raises_validation_exception(self):
        """Test a malformed started_after timestamp raises ValidationException"""
        mock_service = AsyncMock()
        mock_service.get_sessions.return_value = []
        ctx = _make_context(mock_service)

        with pytest.raises(ValidationException):
            await agent_session_manager.get_agent_token_usage(
                ctx, None, False, "not-a-timestamp", None
            )

    @pytest.mark.asyncio
    async def test_fetches_sessions_without_server_side_filter(self):
        """Test the service is called unfiltered so name-substring matching can happen locally"""
        mock_service = AsyncMock()
        mock_service.get_sessions.return_value = []
        ctx = _make_context(mock_service)

        await agent_session_manager.get_agent_token_usage(
            ctx, "some-agent", False, None, None
        )

        mock_service.get_sessions.assert_called_once_with(None)


class TestGetAgentSessionTokenUsageTool:
    """Test the get_agent_session_token_usage tool function"""

    @staticmethod
    def _session(
        session_id="sess-x",
        agent_name="CVE Assessment",
        status="COMPLETE",
        started_at="2026-01-01T00:00:00Z",
        end_time=None,
        duration_ms=1000,
        input_tokens=100,
        output_tokens=50,
    ):
        return {
            "session_id": session_id,
            "agent_name": agent_name,
            "status": status,
            "started_at": started_at,
            "end_time": end_time,
            "duration_ms": duration_ms,
            "total_input_tokens": input_tokens,
            "total_output_tokens": output_tokens,
        }

    @pytest.mark.asyncio
    async def test_one_row_per_session_no_aggregation(self):
        """Test each session produces its own row, not a grouped aggregate"""
        mock_service = AsyncMock()
        mock_service.get_sessions.return_value = [
            self._session(session_id="sess-1", started_at="2026-01-01T00:00:00Z"),
            self._session(session_id="sess-2", started_at="2026-01-02T00:00:00Z"),
        ]
        ctx = _make_context(mock_service)

        result = await agent_session_manager.get_agent_session_token_usage(
            ctx, "CVE", False, None, None
        )

        assert isinstance(result, GetAgentSessionTokenUsageResponse)
        assert len(result.root) == 2
        ids = {e.session_id for e in result.root}
        assert ids == {"sess-1", "sess-2"}

    @pytest.mark.asyncio
    async def test_total_tokens_computed_with_nulls_as_zero(self):
        """Test total_tokens sums input/output, treating null as 0"""
        mock_service = AsyncMock()
        mock_service.get_sessions.return_value = [
            self._session(input_tokens=None, output_tokens=None),
        ]
        ctx = _make_context(mock_service)

        result = await agent_session_manager.get_agent_session_token_usage(
            ctx, "CVE", False, None, None
        )

        assert result.root[0].total_tokens == 0
        assert result.root[0].total_input_tokens is None
        assert result.root[0].total_output_tokens is None

    @pytest.mark.asyncio
    async def test_results_sorted_by_started_at_ascending(self):
        """Test results are sorted by started_at ascending"""
        mock_service = AsyncMock()
        mock_service.get_sessions.return_value = [
            self._session(session_id="sess-late", started_at="2026-03-01T00:00:00Z"),
            self._session(session_id="sess-early", started_at="2026-01-01T00:00:00Z"),
        ]
        ctx = _make_context(mock_service)

        result = await agent_session_manager.get_agent_session_token_usage(
            ctx, "CVE", False, None, None
        )

        assert [e.session_id for e in result.root] == ["sess-early", "sess-late"]

    @pytest.mark.asyncio
    async def test_session_with_none_started_at_sorts_last(self):
        """Test a session with started_at=None sorts after all real timestamps"""
        mock_service = AsyncMock()
        mock_service.get_sessions.return_value = [
            self._session(session_id="sess-none", started_at=None),
            self._session(session_id="sess-real", started_at="2026-01-01T00:00:00Z"),
        ]
        ctx = _make_context(mock_service)

        result = await agent_session_manager.get_agent_session_token_usage(
            ctx, "CVE", False, None, None
        )

        assert [e.session_id for e in result.root] == ["sess-real", "sess-none"]

    @pytest.mark.asyncio
    async def test_agent_name_substring_filter_case_insensitive(self):
        """Test agent_name filter matches substrings case-insensitively"""
        mock_service = AsyncMock()
        mock_service.get_sessions.return_value = [
            self._session(session_id="sess-1", agent_name="CVE Assessment"),
            self._session(session_id="sess-2", agent_name="Compliance Bot"),
        ]
        ctx = _make_context(mock_service)

        result = await agent_session_manager.get_agent_session_token_usage(
            ctx, "cve", False, None, None
        )

        assert len(result.root) == 1
        assert result.root[0].session_id == "sess-1"

    @pytest.mark.asyncio
    async def test_default_only_includes_complete_sessions(self):
        """Test that by default, only COMPLETE sessions are returned"""
        mock_service = AsyncMock()
        mock_service.get_sessions.return_value = [
            self._session(session_id="sess-1", status="COMPLETE"),
            self._session(session_id="sess-2", status="FAILED"),
        ]
        ctx = _make_context(mock_service)

        result = await agent_session_manager.get_agent_session_token_usage(
            ctx, "CVE", False, None, None
        )

        assert len(result.root) == 1
        assert result.root[0].session_id == "sess-1"

    @pytest.mark.asyncio
    async def test_include_failed_adds_failed_sessions(self):
        """Test include_failed=True includes FAILED sessions alongside COMPLETE"""
        mock_service = AsyncMock()
        mock_service.get_sessions.return_value = [
            self._session(session_id="sess-1", status="COMPLETE"),
            self._session(session_id="sess-2", status="FAILED"),
        ]
        ctx = _make_context(mock_service)

        result = await agent_session_manager.get_agent_session_token_usage(
            ctx, "CVE", True, None, None
        )

        assert len(result.root) == 2

    @pytest.mark.asyncio
    async def test_started_after_and_before_window_inclusive(self):
        """Test started_after/started_before window includes the inclusive boundary"""
        mock_service = AsyncMock()
        mock_service.get_sessions.return_value = [
            self._session(
                session_id="sess-boundary", started_at="2026-01-15T00:00:00Z"
            ),
            self._session(session_id="sess-out", started_at="2026-02-01T00:00:00Z"),
        ]
        ctx = _make_context(mock_service)

        result = await agent_session_manager.get_agent_session_token_usage(
            ctx, "CVE", False, "2026-01-15T00:00:00Z", "2026-01-15T00:00:00Z"
        )

        assert len(result.root) == 1
        assert result.root[0].session_id == "sess-boundary"

    @pytest.mark.asyncio
    async def test_no_matching_sessions_returns_empty_response(self):
        """Test that no matches returns an empty response, not an error"""
        mock_service = AsyncMock()
        mock_service.get_sessions.return_value = [
            self._session(agent_name="Other Agent"),
        ]
        ctx = _make_context(mock_service)

        result = await agent_session_manager.get_agent_session_token_usage(
            ctx, "nonexistent", False, None, None
        )

        assert result == GetAgentSessionTokenUsageResponse(root=[])

    @pytest.mark.asyncio
    async def test_invalid_started_after_raises_validation_exception(self):
        """Test a malformed started_after timestamp raises ValidationException"""
        mock_service = AsyncMock()
        mock_service.get_sessions.return_value = []
        ctx = _make_context(mock_service)

        with pytest.raises(ValidationException):
            await agent_session_manager.get_agent_session_token_usage(
                ctx, "CVE", False, "not-a-timestamp", None
            )

    @pytest.mark.asyncio
    async def test_fetches_sessions_without_server_side_filter(self):
        """Test the service is called unfiltered so name-substring matching can happen locally"""
        mock_service = AsyncMock()
        mock_service.get_sessions.return_value = []
        ctx = _make_context(mock_service)

        await agent_session_manager.get_agent_session_token_usage(
            ctx, "CVE", False, None, None
        )

        mock_service.get_sessions.assert_called_once_with(None)


class TestDescribeSessionTokenUsageTool:
    """Test the describe_session_token_usage tool function"""

    @pytest.mark.asyncio
    async def test_succeeded_turn_extracts_duration_and_token_usage(self):
        """Test a succeeded turn produces duration_ms and token_usage"""
        mock_service = AsyncMock()
        mock_service.get_session_messages.return_value = [
            {
                "sessionId": "sess-1",
                "eventId": "evt-1",
                "timestamp": 1748779200000,
                "type": "inference-succeeded",
                "category": "AGENT_REASONING",
                "sequenceNumber": 1,
                "text": "Device configured.",
                "data": {
                    "durationMs": 500,
                    "tokenUsage": {"inputTokens": 100, "outputTokens": 50},
                },
            },
        ]
        ctx = _make_context(mock_service)

        result = await agent_session_manager.describe_session_token_usage(ctx, "sess-1")

        assert isinstance(result, DescribeSessionTokenUsageResponse)
        assert len(result.turns) == 1
        turn = result.turns[0]
        assert turn.event_type == "succeeded"
        assert turn.duration_ms == 500
        assert turn.token_usage.input_tokens == 100
        assert turn.token_usage.output_tokens == 50
        assert turn.sequence_number == 1

    @pytest.mark.asyncio
    async def test_token_usage_extracts_cache_fields_from_live_shape(self):
        """Test tokenUsage extraction against the confirmed live platform shape,
        including cacheReadTokens/cacheCreationTokens"""
        mock_service = AsyncMock()
        mock_service.get_session_messages.return_value = [
            {
                "sessionId": "sess-1",
                "type": "inference-succeeded",
                "sequenceNumber": 3,
                "timestamp": None,
                "text": "...",
                "data": {
                    "durationMs": 6747,
                    "stopReason": "tool_use",
                    "tokenUsage": {
                        "inputTokens": 8606,
                        "outputTokens": 296,
                        "cacheReadTokens": 120,
                        "cacheCreationTokens": 40,
                    },
                },
            },
        ]
        ctx = _make_context(mock_service)

        result = await agent_session_manager.describe_session_token_usage(ctx, "sess-1")

        turn = result.turns[0]
        assert turn.token_usage.input_tokens == 8606
        assert turn.token_usage.output_tokens == 296
        assert turn.token_usage.cache_read_tokens == 120
        assert turn.token_usage.cache_creation_tokens == 40
        assert turn.token_usage.total_tokens == 8902

    @pytest.mark.asyncio
    async def test_token_usage_candidate_key_variant_prompt_completion(self):
        """Test tokenUsage extraction handles promptTokens/completionTokens spelling"""
        mock_service = AsyncMock()
        mock_service.get_session_messages.return_value = [
            {
                "sessionId": "sess-1",
                "type": "inference-succeeded",
                "sequenceNumber": 1,
                "timestamp": None,
                "text": "output",
                "data": {
                    "durationMs": 100,
                    "tokenUsage": {"promptTokens": 20, "completionTokens": 10},
                },
            },
        ]
        ctx = _make_context(mock_service)

        result = await agent_session_manager.describe_session_token_usage(ctx, "sess-1")

        turn = result.turns[0]
        assert turn.token_usage.input_tokens == 20
        assert turn.token_usage.output_tokens == 10

    @pytest.mark.asyncio
    async def test_token_usage_candidate_key_variant_input_output(self):
        """Test tokenUsage extraction handles inputTokens/outputTokens spelling"""
        mock_service = AsyncMock()
        mock_service.get_session_messages.return_value = [
            {
                "sessionId": "sess-1",
                "type": "inference-succeeded",
                "sequenceNumber": 1,
                "timestamp": None,
                "text": "output",
                "data": {
                    "durationMs": 100,
                    "tokenUsage": {"inputTokens": 30, "outputTokens": 15},
                },
            },
        ]
        ctx = _make_context(mock_service)

        result = await agent_session_manager.describe_session_token_usage(ctx, "sess-1")

        turn = result.turns[0]
        assert turn.token_usage.input_tokens == 30
        assert turn.token_usage.output_tokens == 15

    @pytest.mark.asyncio
    async def test_raw_preserves_original_token_usage_dict(self):
        """Test SessionTurnTokenUsage.raw preserves the untouched original dict"""
        mock_service = AsyncMock()
        original = {"promptTokens": 20, "completionTokens": 10, "extraKey": "value"}
        mock_service.get_session_messages.return_value = [
            {
                "sessionId": "sess-1",
                "type": "inference-succeeded",
                "sequenceNumber": 1,
                "timestamp": None,
                "text": "output",
                "data": {"durationMs": 100, "tokenUsage": original},
            },
        ]
        ctx = _make_context(mock_service)

        result = await agent_session_manager.describe_session_token_usage(ctx, "sess-1")

        assert result.turns[0].token_usage.raw == original

    @pytest.mark.asyncio
    async def test_failed_turn_has_no_token_usage_and_populates_error(self):
        """Test a failed turn has token_usage=None and error from text"""
        mock_service = AsyncMock()
        mock_service.get_session_messages.return_value = [
            {
                "sessionId": "sess-1",
                "type": "inference-failed",
                "sequenceNumber": 2,
                "timestamp": None,
                "text": "model timeout",
                "data": {"durationMs": 200},
            },
        ]
        ctx = _make_context(mock_service)

        result = await agent_session_manager.describe_session_token_usage(ctx, "sess-1")

        turn = result.turns[0]
        assert turn.event_type == "failed"
        assert turn.token_usage is None
        assert turn.error == "model timeout"
        assert turn.duration_ms == 200

    @pytest.mark.asyncio
    async def test_non_inference_message_types_filtered_out(self):
        """Test tool-execution and status events are excluded from turns"""
        mock_service = AsyncMock()
        mock_service.get_session_messages.return_value = [
            {
                "sessionId": "sess-1",
                "type": "tool-execution",
                "sequenceNumber": 1,
                "timestamp": None,
                "data": {},
            },
            {
                "sessionId": "sess-1",
                "type": "agent-session-completed",
                "sequenceNumber": 2,
                "timestamp": None,
                "data": {},
            },
        ]
        ctx = _make_context(mock_service)

        result = await agent_session_manager.describe_session_token_usage(ctx, "sess-1")

        assert result.turns == []
        assert result.summary.turn_count == 0

    @pytest.mark.asyncio
    async def test_summary_math_is_correct(self):
        """Test summary sums duration and tokens across all turns, missing as 0"""
        mock_service = AsyncMock()
        mock_service.get_session_messages.return_value = [
            {
                "sessionId": "sess-1",
                "type": "inference-succeeded",
                "sequenceNumber": 1,
                "timestamp": None,
                "text": "a",
                "data": {
                    "durationMs": 100,
                    "tokenUsage": {"inputTokens": 10, "outputTokens": 5},
                },
            },
            {
                "sessionId": "sess-1",
                "type": "inference-succeeded",
                "sequenceNumber": 2,
                "timestamp": None,
                "text": "b",
                "data": {"durationMs": 200},
            },
            {
                "sessionId": "sess-1",
                "type": "inference-failed",
                "sequenceNumber": 3,
                "timestamp": None,
                "text": "boom",
                "data": {},
            },
        ]
        ctx = _make_context(mock_service)

        result = await agent_session_manager.describe_session_token_usage(ctx, "sess-1")

        assert result.summary.session_id == "sess-1"
        assert result.summary.turn_count == 3
        assert result.summary.total_duration_ms == 300
        assert result.summary.total_input_tokens == 10
        assert result.summary.total_output_tokens == 5
        assert result.summary.total_tokens == 15

    @pytest.mark.asyncio
    async def test_zero_inference_turns_returns_zeroed_summary(self):
        """Test a session with zero inference turns returns a zeroed summary, not an error"""
        mock_service = AsyncMock()
        mock_service.get_session_messages.return_value = []
        ctx = _make_context(mock_service)

        result = await agent_session_manager.describe_session_token_usage(
            ctx, "sess-empty"
        )

        assert result.turns == []
        assert result.summary.turn_count == 0
        assert result.summary.total_duration_ms == 0
        assert result.summary.total_input_tokens == 0
        assert result.summary.total_output_tokens == 0
        assert result.summary.total_tokens == 0

    @pytest.mark.asyncio
    async def test_epoch_timestamp_conversion(self):
        """Test epoch millisecond timestamps are converted to ISO 8601"""
        mock_service = AsyncMock()
        mock_service.get_session_messages.return_value = [
            {
                "sessionId": "sess-1",
                "type": "inference-succeeded",
                "sequenceNumber": 1,
                "timestamp": 1748779200000,
                "text": "a",
                "data": {"durationMs": 100},
            },
        ]
        ctx = _make_context(mock_service)

        with patch(
            "itential_mcp.tools.agent_session_manager.timeutils.epoch_to_timestamp"
        ) as mock_ts:
            mock_ts.return_value = "2025-06-01T12:00:00Z"
            result = await agent_session_manager.describe_session_token_usage(
                ctx, "sess-1"
            )

        mock_ts.assert_called_with(1748779200000)
        assert result.turns[0].timestamp == "2025-06-01T12:00:00Z"

    @pytest.mark.asyncio
    async def test_client_error_propagates(self):
        """Test describe_session_token_usage propagates errors from the service layer"""
        mock_service = AsyncMock()
        mock_service.get_session_messages.side_effect = Exception("session not found")
        ctx = _make_context(mock_service)

        with pytest.raises(Exception, match="session not found"):
            await agent_session_manager.describe_session_token_usage(
                ctx, "sess-missing"
            )


class TestEarlyFailedSessionsThroughService:
    """Raw platform data containing a session that failed before getting a
    sessionId must not break the three tools that list sessions."""

    @staticmethod
    def _ctx():
        from itential_mcp.platform.services.agent_session_manager import Service

        good = {
            "sessionId": "sess-001",
            "agentSnapshot": {"name": "network-agent"},
            "status": "COMPLETE",
            "startedAt": "2026-01-01T00:00:00Z",
            "totalInputTokens": 10,
            "totalOutputTokens": 5,
        }
        early_failed = {
            "agentDefinitionId": "def-1",
            "agentSnapshot": {"name": "network-agent"},
            "createdAt": 1700000000000,
            "createdBy": "user-1",
            "endTime": 1700000001000,
            "errorMessage": "Failed to look up tool definitions",
            "inputs": {},
            "status": "FAILED",
            "trigger": {},
        }
        res = MagicMock()
        res.json.return_value = {
            "data": [good, early_failed],
            "total": 2,
            "offset": 0,
            "limit": 100,
        }
        client = AsyncMock()
        client.get.return_value = res
        return _make_context(Service(client))

    @pytest.mark.asyncio
    async def test_get_sessions(self):
        result = await agent_session_manager.get_sessions(self._ctx(), None)

        assert [e.session_id for e in result.results] == ["sess-001"]
        assert result.returned == 1

    @pytest.mark.asyncio
    @pytest.mark.parametrize("include_failed", [False, True])
    async def test_get_agent_token_usage(self, include_failed):
        result = await agent_session_manager.get_agent_token_usage(
            self._ctx(), None, include_failed, None, None
        )

        assert isinstance(result, GetAgentTokenUsageResponse)
        assert len(result.root) == 1
        assert result.root[0].session_count == 1

    @pytest.mark.asyncio
    @pytest.mark.parametrize("include_failed", [False, True])
    async def test_get_agent_session_token_usage(self, include_failed):
        result = await agent_session_manager.get_agent_session_token_usage(
            self._ctx(), "network", include_failed, None, None
        )

        assert isinstance(result, GetAgentSessionTokenUsageResponse)
        assert [e.session_id for e in result.root] == ["sess-001"]


class TestDescribeSessionPendingManualTasks:
    """Test the pending_manual_tasks field of describe_session"""

    @staticmethod
    def _ctx(status):
        service = AsyncMock()
        service.get_session.return_value = {
            "sessionId": "sess-1",
            "status": status,
            "agentSnapshot": {"name": "a"},
        }
        service.get_session_messages.return_value = []
        ctx = _make_context(service)
        client = ctx.request_context.lifespan_context.get.return_value
        client.work_center = AsyncMock()
        return ctx, client

    @pytest.mark.asyncio
    async def test_running_with_pending_item(self):
        ctx, client = self._ctx("RUNNING")
        client.work_center.get_work_items.return_value = [
            {
                "id": "wi-1",
                "summary": "Approve",
                "status": "pending",
                "view": "/workflow_engine/task/InteractiveHTML",
                "createdAt": 0,
            }
        ]

        result = await agent_session_manager.describe_session(ctx, "sess-1")

        assert [t.work_item_id for t in result.pending_manual_tasks] == ["wi-1"]
        client.work_center.get_work_items.assert_awaited_once_with("sess-1")

    @pytest.mark.asyncio
    async def test_running_with_only_completed_items(self):
        ctx, client = self._ctx("RUNNING")
        client.work_center.get_work_items.return_value = [
            {"id": "wi-1", "status": "completed", "view": "/a/ViewData"}
        ]

        result = await agent_session_manager.describe_session(ctx, "sess-1")

        assert result.pending_manual_tasks == []

    @pytest.mark.asyncio
    async def test_running_with_404(self):
        from itential_mcp.core.exceptions import ItentialMcpException

        ctx, client = self._ctx("RUNNING")
        client.work_center.get_work_items.side_effect = ItentialMcpException(
            "404", http_status=404
        )

        result = await agent_session_manager.describe_session(ctx, "sess-1")

        assert result.pending_manual_tasks == []

    @pytest.mark.asyncio
    @pytest.mark.parametrize("code", [403, 500])
    async def test_running_with_lookup_error_is_unknown(self, code):
        from itential_mcp.core.exceptions import ItentialMcpException

        ctx, client = self._ctx("RUNNING")
        client.work_center.get_work_items.side_effect = ItentialMcpException(
            "err", http_status=code
        )

        result = await agent_session_manager.describe_session(ctx, "sess-1")

        assert result.pending_manual_tasks is None
        assert result.status == "RUNNING"

    @pytest.mark.asyncio
    @pytest.mark.parametrize("status", ["COMPLETE", "FAILED", "PAUSED"])
    async def test_non_running_makes_no_lookup(self, status):
        ctx, client = self._ctx(status)

        result = await agent_session_manager.describe_session(ctx, "sess-1")

        assert result.pending_manual_tasks == []
        client.work_center.get_work_items.assert_not_called()

    def test_docstring_mentions_manual_tasks(self):
        assert "pending_manual_tasks" in agent_session_manager.describe_session.__doc__
