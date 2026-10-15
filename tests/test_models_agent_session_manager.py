# Copyright (c) 2025 Itential, Inc
# GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

import pytest
from pydantic import ValidationError

from itential_mcp.models.agent_session_manager import (
    SessionMessage,
    SessionReasoningEvent,
    SessionElement,
    GetSessionsResponse,
    DescribeSessionResponse,
    AgentTokenUsageStats,
    GetAgentTokenUsageResponse,
    AgentSessionTokenUsageElement,
    GetAgentSessionTokenUsageResponse,
    SessionTurnTokenUsage,
    SessionTurnUsageElement,
    SessionTurnUsageSummary,
    DescribeSessionTokenUsageResponse,
)


class TestSessionMessage:
    """Test the SessionMessage model"""

    def test_session_message_required_fields(self):
        """Test SessionMessage creation with the required event_type field"""
        msg = SessionMessage(type="inference-succeeded")

        assert msg.event_type == "inference-succeeded"
        assert msg.category is None
        assert msg.text is None
        assert msg.timestamp is None

    def test_session_message_all_fields(self):
        """Test SessionMessage creation with all fields"""
        msg = SessionMessage(
            type="inference-succeeded",
            category="output",
            text="The device has been configured.",
            timestamp="2025-06-01T12:00:00Z",
        )

        assert msg.event_type == "inference-succeeded"
        assert msg.category == "output"
        assert msg.text == "The device has been configured."
        assert msg.timestamp == "2025-06-01T12:00:00Z"

    def test_session_message_alias_type_works(self):
        """Test that the 'type' alias is accepted as the field name"""
        msg = SessionMessage(**{"type": "tool-call", "text": "calling get_device"})

        assert msg.event_type == "tool-call"
        assert msg.text == "calling get_device"

    def test_session_message_populate_by_name(self):
        """Test that event_type field name is also accepted via model_config"""
        msg = SessionMessage(event_type="agent-error")

        assert msg.event_type == "agent-error"

    def test_session_message_missing_type_raises(self):
        """Test SessionMessage validation fails when type is missing"""
        with pytest.raises(ValidationError) as exc_info:
            SessionMessage()

        errors = exc_info.value.errors()
        assert any(e["type"] == "missing" for e in errors)

    def test_session_message_optional_fields_default_none(self):
        """Test that optional fields default to None"""
        msg = SessionMessage(type="tool-result")

        assert msg.category is None
        assert msg.text is None
        assert msg.timestamp is None


class TestSessionReasoningEvent:
    """Test the SessionReasoningEvent model"""

    def test_session_reasoning_event_all_fields(self):
        """Test SessionReasoningEvent creation with all fields populated"""
        event = SessionReasoningEvent(
            event_id="evt-001",
            sequence_number=1,
            timestamp="2025-06-01T12:00:00Z",
            text="Device configured.",
        )

        assert event.event_id == "evt-001"
        assert event.sequence_number == 1
        assert event.timestamp == "2025-06-01T12:00:00Z"
        assert event.text == "Device configured."

    def test_session_reasoning_event_no_required_fields(self):
        """Test SessionReasoningEvent can be constructed with no arguments,
        all fields defaulting to None"""
        event = SessionReasoningEvent()

        assert event.event_id is None
        assert event.sequence_number is None
        assert event.timestamp is None
        assert event.text is None

    def test_session_reasoning_event_optional_fields_explicit_none(self):
        """Test SessionReasoningEvent accepts explicit None for all fields"""
        event = SessionReasoningEvent(
            event_id=None,
            sequence_number=None,
            timestamp=None,
            text=None,
        )

        assert event.event_id is None
        assert event.sequence_number is None
        assert event.timestamp is None
        assert event.text is None


class TestSessionElement:
    """Test the SessionElement model"""

    def test_session_element_required_fields(self):
        """Test SessionElement creation with only required fields"""
        element = SessionElement(session_id="sess-001", status="COMPLETE")

        assert element.session_id == "sess-001"
        assert element.status == "COMPLETE"
        assert element.agent_name is None
        assert element.started_at is None
        assert element.end_time is None
        assert element.duration_ms is None
        assert element.total_input_tokens is None
        assert element.total_output_tokens is None

    def test_session_element_all_fields(self):
        """Test SessionElement creation with all fields"""
        element = SessionElement(
            session_id="sess-002",
            agent_name="network-config-agent",
            status="COMPLETE",
            started_at="2025-06-01T10:00:00Z",
            end_time="2025-06-01T10:01:30Z",
            duration_ms=90000,
            total_input_tokens=200,
            total_output_tokens=100,
        )

        assert element.session_id == "sess-002"
        assert element.agent_name == "network-config-agent"
        assert element.status == "COMPLETE"
        assert element.started_at == "2025-06-01T10:00:00Z"
        assert element.end_time == "2025-06-01T10:01:30Z"
        assert element.duration_ms == 90000
        assert element.total_input_tokens == 200
        assert element.total_output_tokens == 100

    def test_session_element_token_fields_explicit_none(self):
        """Test SessionElement accepts explicit None for token fields"""
        element = SessionElement(
            session_id="sess-002b",
            status="COMPLETE",
            total_input_tokens=None,
            total_output_tokens=None,
        )

        assert element.total_input_tokens is None
        assert element.total_output_tokens is None

    def test_session_element_running_no_end_time(self):
        """Test SessionElement for a running session with no end time"""
        element = SessionElement(
            session_id="sess-003",
            agent_name="my-agent",
            status="RUNNING",
        )

        assert element.status == "RUNNING"
        assert element.end_time is None
        assert element.duration_ms is None

    def test_session_element_missing_required_raises(self):
        """Test SessionElement validation fails when required fields are missing"""
        with pytest.raises(ValidationError) as exc_info:
            SessionElement()

        errors = exc_info.value.errors()
        error_locs = {e["loc"][0] for e in errors}
        assert "session_id" in error_locs
        assert "status" in error_locs

    def test_session_element_optionals_explicit_none(self):
        """Test SessionElement with explicit None for optional fields"""
        element = SessionElement(
            session_id="sess-004",
            status="FAILED",
            agent_name=None,
            started_at=None,
            end_time=None,
            duration_ms=None,
        )

        assert element.agent_name is None
        assert element.started_at is None
        assert element.end_time is None
        assert element.duration_ms is None


class TestGetSessionsResponse:
    """Test the GetSessionsResponse model"""

    def test_get_sessions_response_empty_default(self):
        """Test GetSessionsResponse default factory produces empty list"""
        response = GetSessionsResponse()

        assert response.root == []
        assert len(response.root) == 0

    def test_get_sessions_response_empty_explicit(self):
        """Test GetSessionsResponse with an explicitly empty list"""
        response = GetSessionsResponse(root=[])

        assert response.root == []

    def test_get_sessions_response_with_elements(self):
        """Test GetSessionsResponse with multiple session elements"""
        elem1 = SessionElement(session_id="sess-001", status="COMPLETE")
        elem2 = SessionElement(
            session_id="sess-002",
            agent_name="my-agent",
            status="RUNNING",
        )

        response = GetSessionsResponse(root=[elem1, elem2])

        assert len(response.root) == 2
        assert response.root[0].session_id == "sess-001"
        assert response.root[1].session_id == "sess-002"
        assert response.root[1].agent_name == "my-agent"

    def test_get_sessions_response_is_iterable(self):
        """Test GetSessionsResponse root list is iterable"""
        elem = SessionElement(session_id="sess-001", status="COMPLETE")
        response = GetSessionsResponse(root=[elem])

        sessions = list(response.root)
        assert len(sessions) == 1
        assert sessions[0].session_id == "sess-001"


class TestDescribeSessionResponse:
    """Test the DescribeSessionResponse model"""

    def test_describe_session_response_full_fields(self):
        """Test DescribeSessionResponse with all fields populated"""
        event = SessionReasoningEvent(
            event_id="evt-001",
            sequence_number=1,
            timestamp="2025-06-01T10:00:30Z",
            text="Done.",
        )

        response = DescribeSessionResponse(
            session_id="sess-001",
            agent_name="network-agent",
            status="COMPLETE",
            output="Done.",
            started_at="2025-06-01T10:00:00Z",
            end_time="2025-06-01T10:01:00Z",
            duration_ms=60000,
            reasoning_events=[event],
        )

        assert response.session_id == "sess-001"
        assert response.agent_name == "network-agent"
        assert response.status == "COMPLETE"
        assert response.output == "Done."
        assert response.started_at == "2025-06-01T10:00:00Z"
        assert response.end_time == "2025-06-01T10:01:00Z"
        assert response.duration_ms == 60000
        assert len(response.reasoning_events) == 1
        assert response.reasoning_events[0].event_id == "evt-001"

    def test_describe_session_response_output_none_when_running(self):
        """Test DescribeSessionResponse output is None for running sessions"""
        response = DescribeSessionResponse(
            session_id="sess-002",
            status="RUNNING",
            output=None,
        )

        assert response.output is None
        assert response.agent_name is None
        assert response.reasoning_events == []

    def test_describe_session_response_multiple_reasoning_events(self):
        """Test DescribeSessionResponse with multiple kept reasoning events"""
        events = [
            SessionReasoningEvent(event_id="evt-001", text="first turn"),
            SessionReasoningEvent(event_id="evt-002", text="second turn"),
        ]

        response = DescribeSessionResponse(
            session_id="sess-003",
            status="FAILED",
            output=None,
            reasoning_events=events,
        )

        assert response.output is None
        assert len(response.reasoning_events) == 2

    def test_describe_session_response_missing_required_raises(self):
        """Test DescribeSessionResponse validation fails when required fields are absent"""
        with pytest.raises(ValidationError) as exc_info:
            DescribeSessionResponse()

        errors = exc_info.value.errors()
        error_locs = {e["loc"][0] for e in errors}
        assert "session_id" in error_locs
        assert "status" in error_locs

    def test_describe_session_response_default_reasoning_events_empty(self):
        """Test DescribeSessionResponse reasoning_events defaults to empty list"""
        response = DescribeSessionResponse(session_id="sess-004", status="COMPLETE")

        assert response.reasoning_events == []

    def test_describe_session_response_optional_fields_default_none(self):
        """Test DescribeSessionResponse optional fields default to None"""
        response = DescribeSessionResponse(session_id="sess-005", status="COMPLETE")

        assert response.agent_name is None
        assert response.output is None
        assert response.started_at is None
        assert response.end_time is None
        assert response.duration_ms is None


class TestAgentTokenUsageStats:
    """Test the AgentTokenUsageStats model"""

    def test_agent_token_usage_stats_all_fields(self):
        """Test AgentTokenUsageStats creation with all fields populated"""
        stats = AgentTokenUsageStats(
            agent_name="network-agent",
            session_count=3,
            total_input_tokens=300,
            total_output_tokens=150,
            total_tokens=450,
            avg_input_tokens=100.0,
            min_input_tokens=50,
            max_input_tokens=150,
            avg_output_tokens=50.0,
            min_output_tokens=25,
            max_output_tokens=75,
            total_duration_ms=9000,
            avg_duration_ms=3000.0,
            min_duration_ms=1000,
            max_duration_ms=5000,
        )

        assert stats.agent_name == "network-agent"
        assert stats.session_count == 3
        assert stats.total_input_tokens == 300
        assert stats.total_output_tokens == 150
        assert stats.total_tokens == 450
        assert stats.avg_input_tokens == 100.0
        assert stats.min_input_tokens == 50
        assert stats.max_input_tokens == 150
        assert stats.avg_output_tokens == 50.0
        assert stats.min_output_tokens == 25
        assert stats.max_output_tokens == 75
        assert stats.total_duration_ms == 9000
        assert stats.avg_duration_ms == 3000.0
        assert stats.min_duration_ms == 1000
        assert stats.max_duration_ms == 5000

    def test_agent_token_usage_stats_none_agent_name(self):
        """Test AgentTokenUsageStats accepts a None agent_name (unnamed group)"""
        stats = AgentTokenUsageStats(
            agent_name=None,
            session_count=1,
            total_input_tokens=0,
            total_output_tokens=0,
            total_tokens=0,
            avg_input_tokens=0.0,
            min_input_tokens=0,
            max_input_tokens=0,
            avg_output_tokens=0.0,
            min_output_tokens=0,
            max_output_tokens=0,
            total_duration_ms=0,
            avg_duration_ms=0.0,
            min_duration_ms=0,
            max_duration_ms=0,
        )

        assert stats.agent_name is None
        assert stats.session_count == 1

    def test_agent_token_usage_stats_missing_required_raises(self):
        """Test AgentTokenUsageStats validation fails when required fields are absent"""
        with pytest.raises(ValidationError) as exc_info:
            AgentTokenUsageStats()

        errors = exc_info.value.errors()
        error_locs = {e["loc"][0] for e in errors}
        assert "session_count" in error_locs
        assert "total_input_tokens" in error_locs
        assert "total_duration_ms" in error_locs


class TestGetAgentTokenUsageResponse:
    """Test the GetAgentTokenUsageResponse model"""

    def test_get_agent_token_usage_response_empty_default(self):
        """Test GetAgentTokenUsageResponse default factory produces empty list"""
        response = GetAgentTokenUsageResponse()

        assert response.root == []
        assert len(response.root) == 0

    def test_get_agent_token_usage_response_empty_explicit(self):
        """Test GetAgentTokenUsageResponse with an explicitly empty list"""
        response = GetAgentTokenUsageResponse(root=[])

        assert response.root == []

    def test_get_agent_token_usage_response_with_stats(self):
        """Test GetAgentTokenUsageResponse with multiple stats entries"""
        stat1 = AgentTokenUsageStats(
            agent_name="agent-a",
            session_count=2,
            total_input_tokens=200,
            total_output_tokens=100,
            total_tokens=300,
            avg_input_tokens=100.0,
            min_input_tokens=50,
            max_input_tokens=150,
            avg_output_tokens=50.0,
            min_output_tokens=25,
            max_output_tokens=75,
            total_duration_ms=2000,
            avg_duration_ms=1000.0,
            min_duration_ms=500,
            max_duration_ms=1500,
        )
        stat2 = AgentTokenUsageStats(
            agent_name="agent-b",
            session_count=1,
            total_input_tokens=10,
            total_output_tokens=5,
            total_tokens=15,
            avg_input_tokens=10.0,
            min_input_tokens=10,
            max_input_tokens=10,
            avg_output_tokens=5.0,
            min_output_tokens=5,
            max_output_tokens=5,
            total_duration_ms=200,
            avg_duration_ms=200.0,
            min_duration_ms=200,
            max_duration_ms=200,
        )

        response = GetAgentTokenUsageResponse(root=[stat1, stat2])

        assert len(response.root) == 2
        assert response.root[0].agent_name == "agent-a"
        assert response.root[1].agent_name == "agent-b"


class TestAgentSessionTokenUsageElement:
    """Test the AgentSessionTokenUsageElement model"""

    def test_all_fields(self):
        """Test AgentSessionTokenUsageElement creation with all fields populated"""
        element = AgentSessionTokenUsageElement(
            session_id="sess-001",
            status="COMPLETE",
            started_at="2025-06-01T10:00:00Z",
            end_time="2025-06-01T10:01:00Z",
            duration_ms=60000,
            total_input_tokens=200,
            total_output_tokens=100,
            total_tokens=300,
        )

        assert element.session_id == "sess-001"
        assert element.status == "COMPLETE"
        assert element.started_at == "2025-06-01T10:00:00Z"
        assert element.end_time == "2025-06-01T10:01:00Z"
        assert element.duration_ms == 60000
        assert element.total_input_tokens == 200
        assert element.total_output_tokens == 100
        assert element.total_tokens == 300

    def test_optional_fields_default_none(self):
        """Test optional fields default to None while total_tokens is required"""
        element = AgentSessionTokenUsageElement(
            session_id="sess-002",
            status="RUNNING",
            total_tokens=0,
        )

        assert element.started_at is None
        assert element.end_time is None
        assert element.duration_ms is None
        assert element.total_input_tokens is None
        assert element.total_output_tokens is None

    def test_missing_required_raises(self):
        """Test validation fails when required fields are absent"""
        with pytest.raises(ValidationError) as exc_info:
            AgentSessionTokenUsageElement()

        errors = exc_info.value.errors()
        error_locs = {e["loc"][0] for e in errors}
        assert "session_id" in error_locs
        assert "status" in error_locs
        assert "total_tokens" in error_locs


class TestGetAgentSessionTokenUsageResponse:
    """Test the GetAgentSessionTokenUsageResponse model"""

    def test_empty_default(self):
        """Test default factory produces an empty list"""
        response = GetAgentSessionTokenUsageResponse()

        assert response.root == []

    def test_empty_explicit(self):
        """Test an explicitly empty list is accepted"""
        response = GetAgentSessionTokenUsageResponse(root=[])

        assert response.root == []

    def test_with_elements(self):
        """Test response wraps multiple elements in order"""
        elem1 = AgentSessionTokenUsageElement(
            session_id="sess-001", status="COMPLETE", total_tokens=10
        )
        elem2 = AgentSessionTokenUsageElement(
            session_id="sess-002", status="COMPLETE", total_tokens=20
        )

        response = GetAgentSessionTokenUsageResponse(root=[elem1, elem2])

        assert len(response.root) == 2
        assert response.root[0].session_id == "sess-001"
        assert response.root[1].session_id == "sess-002"


class TestSessionTurnTokenUsage:
    """Test the SessionTurnTokenUsage model"""

    def test_all_fields(self):
        """Test SessionTurnTokenUsage creation with all fields populated"""
        usage = SessionTurnTokenUsage(
            input_tokens=100,
            output_tokens=50,
            cache_read_tokens=20,
            cache_creation_tokens=5,
            total_tokens=150,
            raw={"inputTokens": 100, "outputTokens": 50},
        )

        assert usage.input_tokens == 100
        assert usage.output_tokens == 50
        assert usage.cache_read_tokens == 20
        assert usage.cache_creation_tokens == 5
        assert usage.total_tokens == 150
        assert usage.raw == {"inputTokens": 100, "outputTokens": 50}

    def test_all_fields_default_none(self):
        """Test all fields default to None"""
        usage = SessionTurnTokenUsage()

        assert usage.input_tokens is None
        assert usage.output_tokens is None
        assert usage.cache_read_tokens is None
        assert usage.cache_creation_tokens is None
        assert usage.total_tokens is None
        assert usage.raw is None


class TestSessionTurnUsageElement:
    """Test the SessionTurnUsageElement model"""

    def test_succeeded_turn_all_fields(self):
        """Test a succeeded turn with all fields populated"""
        usage = SessionTurnTokenUsage(input_tokens=10, output_tokens=5, total_tokens=15)
        turn = SessionTurnUsageElement(
            sequence_number=1,
            timestamp="2025-06-01T10:00:00Z",
            event_type="succeeded",
            duration_ms=500,
            token_usage=usage,
            error=None,
        )

        assert turn.sequence_number == 1
        assert turn.timestamp == "2025-06-01T10:00:00Z"
        assert turn.event_type == "succeeded"
        assert turn.duration_ms == 500
        assert turn.token_usage.input_tokens == 10
        assert turn.error is None

    def test_failed_turn_has_error_no_token_usage(self):
        """Test a failed turn has error populated and token_usage None"""
        turn = SessionTurnUsageElement(
            sequence_number=2,
            event_type="failed",
            duration_ms=200,
            error="model timeout",
        )

        assert turn.event_type == "failed"
        assert turn.token_usage is None
        assert turn.error == "model timeout"

    def test_missing_required_raises(self):
        """Test validation fails when event_type is absent"""
        with pytest.raises(ValidationError) as exc_info:
            SessionTurnUsageElement()

        errors = exc_info.value.errors()
        error_locs = {e["loc"][0] for e in errors}
        assert "event_type" in error_locs

    def test_optional_fields_default_none(self):
        """Test optional fields default to None"""
        turn = SessionTurnUsageElement(event_type="succeeded")

        assert turn.sequence_number is None
        assert turn.timestamp is None
        assert turn.duration_ms is None
        assert turn.token_usage is None
        assert turn.error is None


class TestSessionTurnUsageSummary:
    """Test the SessionTurnUsageSummary model"""

    def test_all_fields(self):
        """Test SessionTurnUsageSummary creation with all fields populated"""
        summary = SessionTurnUsageSummary(
            session_id="sess-001",
            turn_count=3,
            total_duration_ms=900,
            total_input_tokens=100,
            total_output_tokens=50,
            total_tokens=150,
        )

        assert summary.session_id == "sess-001"
        assert summary.turn_count == 3
        assert summary.total_duration_ms == 900
        assert summary.total_input_tokens == 100
        assert summary.total_output_tokens == 50
        assert summary.total_tokens == 150

    def test_missing_required_raises(self):
        """Test validation fails when required fields are absent"""
        with pytest.raises(ValidationError) as exc_info:
            SessionTurnUsageSummary()

        errors = exc_info.value.errors()
        error_locs = {e["loc"][0] for e in errors}
        assert "session_id" in error_locs
        assert "turn_count" in error_locs


class TestDescribeSessionTokenUsageResponse:
    """Test the DescribeSessionTokenUsageResponse model"""

    def test_full_response(self):
        """Test DescribeSessionTokenUsageResponse with summary and turns populated"""
        summary = SessionTurnUsageSummary(
            session_id="sess-001",
            turn_count=1,
            total_duration_ms=500,
            total_input_tokens=10,
            total_output_tokens=5,
            total_tokens=15,
        )
        turn = SessionTurnUsageElement(event_type="succeeded", duration_ms=500)

        response = DescribeSessionTokenUsageResponse(summary=summary, turns=[turn])

        assert response.summary.session_id == "sess-001"
        assert len(response.turns) == 1
        assert response.turns[0].event_type == "succeeded"

    def test_turns_default_empty(self):
        """Test turns defaults to an empty list"""
        summary = SessionTurnUsageSummary(
            session_id="sess-002",
            turn_count=0,
            total_duration_ms=0,
            total_input_tokens=0,
            total_output_tokens=0,
            total_tokens=0,
        )

        response = DescribeSessionTokenUsageResponse(summary=summary)

        assert response.turns == []

    def test_missing_summary_raises(self):
        """Test validation fails when summary is absent"""
        with pytest.raises(ValidationError) as exc_info:
            DescribeSessionTokenUsageResponse()

        errors = exc_info.value.errors()
        error_locs = {e["loc"][0] for e in errors}
        assert "summary" in error_locs


class TestDescribeSessionResponsePendingManualTasks:
    """Test the pending_manual_tasks field on DescribeSessionResponse"""

    def test_defaults_to_none(self):
        r = DescribeSessionResponse(session_id="s", status="RUNNING")
        assert r.pending_manual_tasks is None

    def test_accepts_empty_list_and_summaries(self):
        from itential_mcp.models.work_center import ManualTaskSummary

        r = DescribeSessionResponse(
            session_id="s", status="RUNNING", pending_manual_tasks=[]
        )
        assert r.pending_manual_tasks == []
        r = DescribeSessionResponse(
            session_id="s",
            status="RUNNING",
            pending_manual_tasks=[ManualTaskSummary(work_item_id="w")],
        )
        assert r.pending_manual_tasks[0].work_item_id == "w"

    def test_field_description_spells_out_tri_state(self):
        desc = DescribeSessionResponse.model_fields["pending_manual_tasks"].description
        assert "unknown" in desc
        assert "none are" in desc
        assert "nested" in desc
