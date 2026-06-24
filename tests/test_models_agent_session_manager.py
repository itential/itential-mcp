# Copyright (c) 2025 Itential, Inc
# GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

import pytest
from pydantic import ValidationError

from itential_mcp.models.agent_session_manager import (
    SessionMessage,
    SessionElement,
    GetSessionsResponse,
    DescribeSessionResponse,
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

    def test_session_element_all_fields(self):
        """Test SessionElement creation with all fields"""
        element = SessionElement(
            session_id="sess-002",
            agent_name="network-config-agent",
            status="COMPLETE",
            started_at="2025-06-01T10:00:00Z",
            end_time="2025-06-01T10:01:30Z",
            duration_ms=90000,
        )

        assert element.session_id == "sess-002"
        assert element.agent_name == "network-config-agent"
        assert element.status == "COMPLETE"
        assert element.started_at == "2025-06-01T10:00:00Z"
        assert element.end_time == "2025-06-01T10:01:30Z"
        assert element.duration_ms == 90000

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
        msg = SessionMessage(type="inference-succeeded", text="Done.")

        response = DescribeSessionResponse(
            session_id="sess-001",
            agent_name="network-agent",
            status="COMPLETE",
            output="Done.",
            started_at="2025-06-01T10:00:00Z",
            end_time="2025-06-01T10:01:00Z",
            duration_ms=60000,
            messages=[msg],
        )

        assert response.session_id == "sess-001"
        assert response.agent_name == "network-agent"
        assert response.status == "COMPLETE"
        assert response.output == "Done."
        assert response.started_at == "2025-06-01T10:00:00Z"
        assert response.end_time == "2025-06-01T10:01:00Z"
        assert response.duration_ms == 60000
        assert len(response.messages) == 1
        assert response.messages[0].event_type == "inference-succeeded"

    def test_describe_session_response_output_none_when_running(self):
        """Test DescribeSessionResponse output is None for running sessions"""
        response = DescribeSessionResponse(
            session_id="sess-002",
            status="RUNNING",
            output=None,
        )

        assert response.output is None
        assert response.agent_name is None
        assert response.messages == []

    def test_describe_session_response_no_inference_succeeded(self):
        """Test DescribeSessionResponse with messages but no inference-succeeded"""
        msgs = [
            SessionMessage(type="tool-call", text="calling list_devices"),
            SessionMessage(type="tool-result", text="[router1, router2]"),
        ]

        response = DescribeSessionResponse(
            session_id="sess-003",
            status="FAILED",
            output=None,
            messages=msgs,
        )

        assert response.output is None
        assert len(response.messages) == 2

    def test_describe_session_response_missing_required_raises(self):
        """Test DescribeSessionResponse validation fails when required fields are absent"""
        with pytest.raises(ValidationError) as exc_info:
            DescribeSessionResponse()

        errors = exc_info.value.errors()
        error_locs = {e["loc"][0] for e in errors}
        assert "session_id" in error_locs
        assert "status" in error_locs

    def test_describe_session_response_default_messages_empty(self):
        """Test DescribeSessionResponse messages defaults to empty list"""
        response = DescribeSessionResponse(session_id="sess-004", status="COMPLETE")

        assert response.messages == []

    def test_describe_session_response_optional_fields_default_none(self):
        """Test DescribeSessionResponse optional fields default to None"""
        response = DescribeSessionResponse(session_id="sess-005", status="COMPLETE")

        assert response.agent_name is None
        assert response.output is None
        assert response.started_at is None
        assert response.end_time is None
        assert response.duration_ms is None
