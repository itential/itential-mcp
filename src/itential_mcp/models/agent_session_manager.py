# Copyright (c) 2025 Itential, Inc
# GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import annotations

import inspect

from typing import Annotated, Any

from pydantic import BaseModel, Field, RootModel

from itential_mcp.models.work_center import ManualTaskSummary


class SessionMessage(BaseModel):
    """
    Represents a single event message from an agent session.

    Session messages capture the discrete events emitted during agent execution,
    including model inference steps, tool calls, and final outputs. Each message
    has a type that classifies the event and an optional text payload.

    Attributes:
        event_type: The event classification (e.g., "inference-succeeded",
            "tool-call", "agent-error").
        category: Optional grouping category for the event.
        text: The text content of the event (e.g., model output, error message).
        timestamp: ISO 8601 timestamp when the event was emitted.
    """

    event_type: Annotated[
        str,
        Field(
            alias="type",
            description=inspect.cleandoc(
                """
                Event classification for this message (e.g., inference-succeeded,
                tool-call, agent-error)
                """
            ),
        ),
    ]

    category: Annotated[
        str | None,
        Field(
            description=inspect.cleandoc(
                """
                Optional grouping category for the event
                """
            ),
            default=None,
        ),
    ]

    text: Annotated[
        str | None,
        Field(
            description=inspect.cleandoc(
                """
                Text content of the event such as model output or error message
                """
            ),
            default=None,
        ),
    ]

    timestamp: Annotated[
        str | None,
        Field(
            description=inspect.cleandoc(
                """
                ISO 8601 timestamp when this event was emitted
                """
            ),
            default=None,
        ),
    ]

    model_config = {"populate_by_name": True}


class SessionReasoningEvent(BaseModel):
    """
    Represents a single kept AGENT_REASONING event from an agent session.

    describe_session filters the raw session event log down to only the
    AGENT_REASONING events whose data.stopReason is "end_turn" — these are
    the reasoning steps that represent a completed model turn, as opposed to
    tool-execution events, pending-inference events, tool_use-stopReason
    reasoning steps (mid-turn, not yet final), or reasoning events with no
    data at all. Each kept event carries its own text payload.

    Attributes:
        event_id: Unique identifier for this event.
        sequence_number: Ordering number for this event within the session.
        timestamp: ISO 8601 timestamp when this event was emitted.
        text: Text content of this reasoning event.
    """

    event_id: Annotated[
        str | None,
        Field(
            description=inspect.cleandoc(
                """
                Unique identifier for this event
                """
            ),
            default=None,
        ),
    ]

    sequence_number: Annotated[
        int | None,
        Field(
            description=inspect.cleandoc(
                """
                Ordering number for this event within the session
                """
            ),
            default=None,
        ),
    ]

    timestamp: Annotated[
        str | None,
        Field(
            description=inspect.cleandoc(
                """
                ISO 8601 timestamp when this event was emitted
                """
            ),
            default=None,
        ),
    ]

    text: Annotated[
        str | None,
        Field(
            description=inspect.cleandoc(
                """
                Text content of this reasoning event
                """
            ),
            default=None,
        ),
    ]


class SessionElement(BaseModel):
    """
    Represents a single agent session from the AgentSessionManager.

    Sessions are created when an agent automation is triggered via an endpoint
    trigger. This lightweight list-view model surfaces the fields most useful
    for scanning recent sessions; use describe_session for the full event log
    and output text.

    Attributes:
        session_id: Unique session identifier (use with describe_session).
        agent_name: Name of the agent that ran.
        status: Session status (RUNNING, COMPLETE, FAILED).
        started_at: ISO 8601 start timestamp.
        end_time: ISO 8601 end timestamp (None if still running).
        duration_ms: Total session duration in milliseconds.
        total_input_tokens: Total input (prompt) tokens consumed by the session.
        total_output_tokens: Total output (completion) tokens produced by the
            session.
    """

    session_id: Annotated[
        str,
        Field(
            description=inspect.cleandoc(
                """
                Unique session identifier; use with describe_session to get the
                full event log and agent output
                """
            )
        ),
    ]

    agent_name: Annotated[
        str | None,
        Field(
            description=inspect.cleandoc(
                """
                Name of the agent that ran
                """
            ),
            default=None,
        ),
    ]

    status: Annotated[
        str,
        Field(
            description=inspect.cleandoc(
                """
                Session status (RUNNING, COMPLETE, FAILED)
                """
            )
        ),
    ]

    started_at: Annotated[
        str | None,
        Field(
            description=inspect.cleandoc(
                """
                ISO 8601 start timestamp
                """
            ),
            default=None,
        ),
    ]

    end_time: Annotated[
        str | None,
        Field(
            description=inspect.cleandoc(
                """
                ISO 8601 end timestamp; None if the session is still RUNNING
                """
            ),
            default=None,
        ),
    ]

    duration_ms: Annotated[
        int | None,
        Field(
            description=inspect.cleandoc(
                """
                Total session duration in milliseconds
                """
            ),
            default=None,
        ),
    ]

    total_input_tokens: Annotated[
        int | None,
        Field(
            description=inspect.cleandoc(
                """
                Total input (prompt) tokens consumed by the session; None if
                not reported by the platform
                """
            ),
            default=None,
        ),
    ]

    total_output_tokens: Annotated[
        int | None,
        Field(
            description=inspect.cleandoc(
                """
                Total output (completion) tokens produced by the session;
                None if not reported by the platform
                """
            ),
            default=None,
        ),
    ]


class GetSessionsResponse(RootModel):
    """
    Response model for agent session collection endpoints.

    Wraps a list of SessionElement objects returned from the AgentSessionManager
    when listing sessions, optionally filtered by agent name.

    Attributes:
        root: List of SessionElement objects with session metadata and status.
    """

    root: Annotated[
        list[SessionElement],
        Field(
            description=inspect.cleandoc(
                """
                List of agent session objects with status and timing metadata
                """
            ),
            default_factory=list,
        ),
    ]


class DescribeSessionResponse(BaseModel):
    """
    Response model for agent session detail endpoints.

    Provides the full detail of an agent session including the filtered
    reasoning event log and the final output text produced by the agent.
    Use this model to inspect what the agent did and what it returned.

    Attributes:
        session_id: Unique session identifier.
        agent_name: Name of the agent that ran.
        status: Session status (RUNNING, COMPLETE, FAILED).
        output: Final text output produced by the agent (the last kept
            reasoning event's text). None if the session has not yet
            completed or produced no matching reasoning event.
        started_at: ISO 8601 start timestamp.
        end_time: ISO 8601 end timestamp (None if still running).
        duration_ms: Total session duration in milliseconds.
        reasoning_events: Ordered list of kept AGENT_REASONING events (those
            with data.stopReason == "end_turn").
        pending_manual_tasks: Manual tasks waiting on a human (None if unknown).
    """

    session_id: Annotated[
        str,
        Field(
            description=inspect.cleandoc(
                """
                Unique session identifier
                """
            )
        ),
    ]

    agent_name: Annotated[
        str | None,
        Field(
            description=inspect.cleandoc(
                """
                Name of the agent that ran
                """
            ),
            default=None,
        ),
    ]

    status: Annotated[
        str,
        Field(
            description=inspect.cleandoc(
                """
                Session status (RUNNING, COMPLETE, FAILED)
                """
            )
        ),
    ]

    output: Annotated[
        str | None,
        Field(
            description=inspect.cleandoc(
                """
                Final text output produced by the agent; taken from the last
                kept reasoning event's text. None if the session has not
                completed or produced no matching reasoning event.
                """
            ),
            default=None,
        ),
    ]

    started_at: Annotated[
        str | None,
        Field(
            description=inspect.cleandoc(
                """
                ISO 8601 start timestamp
                """
            ),
            default=None,
        ),
    ]

    end_time: Annotated[
        str | None,
        Field(
            description=inspect.cleandoc(
                """
                ISO 8601 end timestamp; None if the session is still RUNNING
                """
            ),
            default=None,
        ),
    ]

    duration_ms: Annotated[
        int | None,
        Field(
            description=inspect.cleandoc(
                """
                Total session duration in milliseconds
                """
            ),
            default=None,
        ),
    ]

    reasoning_events: Annotated[
        list[SessionReasoningEvent],
        Field(
            description=inspect.cleandoc(
                """
                Ordered list of kept AGENT_REASONING events (those with
                data.stopReason == "end_turn") captured during agent execution
                """
            ),
            default_factory=list,
        ),
    ]

    pending_manual_tasks: Annotated[
        list[ManualTaskSummary] | None,
        Field(
            description=inspect.cleandoc(
                """
                Manual tasks currently waiting on a human. Tri-state: None
                means unknown (the lookup failed with an error other than
                not-found, e.g. 403, 500 or a timeout; the rest of this
                response is still valid). An empty list means none are
                pending, including when the session is not running (the
                lookup only runs while status is RUNNING). A non-empty list holds the
                pending tasks; use describe_manual_task with a work_item_id for
                detail. Detection covers manual tasks attached directly to
                this session's own ID; tasks inside nested or child runs are not
                guaranteed to be listed.
                """
            ),
            default=None,
        ),
    ]


class AgentTokenUsageStats(BaseModel):
    """
    Aggregated token usage statistics for a single agent.

    Summarizes token consumption across all agent sessions grouped by agent
    name, including totals, averages, and min/max values for both input and
    output tokens. Sessions with missing token data are still counted toward
    session_count but contribute 0 to the token sums, averages, and min/max
    calculations.

    Attributes:
        agent_name: Agent display name; None if the underlying sessions had
            no agentSnapshot.name.
        session_count: Number of sessions included in this group.
        total_input_tokens: Sum of input tokens across all sessions in the group.
        total_output_tokens: Sum of output tokens across all sessions in the group.
        total_tokens: Sum of total_input_tokens and total_output_tokens.
        avg_input_tokens: Average input tokens per session in the group.
        min_input_tokens: Minimum input tokens across sessions in the group.
        max_input_tokens: Maximum input tokens across sessions in the group.
        avg_output_tokens: Average output tokens per session in the group.
        min_output_tokens: Minimum output tokens across sessions in the group.
        max_output_tokens: Maximum output tokens across sessions in the group.
        total_duration_ms: Sum of session durations across the group.
        avg_duration_ms: Average session duration in the group.
        min_duration_ms: Minimum session duration in the group.
        max_duration_ms: Maximum session duration in the group.
    """

    agent_name: Annotated[
        str | None,
        Field(
            description=inspect.cleandoc(
                """
                Agent display name; None if the underlying sessions had no
                agentSnapshot.name
                """
            )
        ),
    ]

    session_count: Annotated[
        int,
        Field(
            description=inspect.cleandoc(
                """
                Number of sessions included in this group
                """
            )
        ),
    ]

    total_input_tokens: Annotated[
        int,
        Field(
            description=inspect.cleandoc(
                """
                Sum of input tokens across all sessions in the group; missing
                or null values are treated as 0
                """
            )
        ),
    ]

    total_output_tokens: Annotated[
        int,
        Field(
            description=inspect.cleandoc(
                """
                Sum of output tokens across all sessions in the group; missing
                or null values are treated as 0
                """
            )
        ),
    ]

    total_tokens: Annotated[
        int,
        Field(
            description=inspect.cleandoc(
                """
                Sum of total_input_tokens and total_output_tokens
                """
            )
        ),
    ]

    avg_input_tokens: Annotated[
        float,
        Field(
            description=inspect.cleandoc(
                """
                Average input tokens per session in the group
                """
            )
        ),
    ]

    min_input_tokens: Annotated[
        int,
        Field(
            description=inspect.cleandoc(
                """
                Minimum input tokens across sessions in the group
                """
            )
        ),
    ]

    max_input_tokens: Annotated[
        int,
        Field(
            description=inspect.cleandoc(
                """
                Maximum input tokens across sessions in the group
                """
            )
        ),
    ]

    avg_output_tokens: Annotated[
        float,
        Field(
            description=inspect.cleandoc(
                """
                Average output tokens per session in the group
                """
            )
        ),
    ]

    min_output_tokens: Annotated[
        int,
        Field(
            description=inspect.cleandoc(
                """
                Minimum output tokens across sessions in the group
                """
            )
        ),
    ]

    max_output_tokens: Annotated[
        int,
        Field(
            description=inspect.cleandoc(
                """
                Maximum output tokens across sessions in the group
                """
            )
        ),
    ]

    total_duration_ms: Annotated[
        int,
        Field(
            description=inspect.cleandoc(
                """
                Sum of session durations across the group; missing or null
                values are treated as 0
                """
            )
        ),
    ]

    avg_duration_ms: Annotated[
        float,
        Field(
            description=inspect.cleandoc(
                """
                Average session duration in milliseconds across the group
                """
            )
        ),
    ]

    min_duration_ms: Annotated[
        int,
        Field(
            description=inspect.cleandoc(
                """
                Minimum session duration in milliseconds across the group
                """
            )
        ),
    ]

    max_duration_ms: Annotated[
        int,
        Field(
            description=inspect.cleandoc(
                """
                Maximum session duration in milliseconds across the group
                """
            )
        ),
    ]


class GetAgentTokenUsageResponse(RootModel):
    """
    Response model for the agent token usage aggregation endpoint.

    Wraps a list of AgentTokenUsageStats objects, one per distinct agent name
    (including a None-keyed entry for sessions with no agent name), sorted by
    total_tokens descending.

    Attributes:
        root: List of AgentTokenUsageStats objects with aggregated token
            usage metrics per agent.
    """

    root: Annotated[
        list[AgentTokenUsageStats],
        Field(
            description=inspect.cleandoc(
                """
                List of per-agent token usage aggregation objects, sorted by
                total_tokens descending
                """
            ),
            default_factory=list,
        ),
    ]


class AgentSessionTokenUsageElement(BaseModel):
    """
    Represents per-session token usage for a single agent session.

    Provides a time-series-friendly, non-aggregated view of one session's
    token consumption and timing, for use alongside get_agent_token_usage's
    aggregate statistics.

    Attributes:
        session_id: Unique session identifier.
        status: Session status (RUNNING, COMPLETE, FAILED).
        started_at: ISO 8601 start timestamp.
        end_time: ISO 8601 end timestamp (None if still running).
        duration_ms: Total session duration in milliseconds.
        total_input_tokens: Total input (prompt) tokens consumed.
        total_output_tokens: Total output (completion) tokens produced.
        total_tokens: Sum of total_input_tokens and total_output_tokens.
    """

    session_id: Annotated[
        str,
        Field(
            description=inspect.cleandoc(
                """
                Unique session identifier
                """
            )
        ),
    ]

    status: Annotated[
        str,
        Field(
            description=inspect.cleandoc(
                """
                Session status (RUNNING, COMPLETE, FAILED)
                """
            )
        ),
    ]

    started_at: Annotated[
        str | None,
        Field(
            description=inspect.cleandoc(
                """
                ISO 8601 start timestamp
                """
            ),
            default=None,
        ),
    ]

    end_time: Annotated[
        str | None,
        Field(
            description=inspect.cleandoc(
                """
                ISO 8601 end timestamp; None if the session is still RUNNING
                """
            ),
            default=None,
        ),
    ]

    duration_ms: Annotated[
        int | None,
        Field(
            description=inspect.cleandoc(
                """
                Total session duration in milliseconds
                """
            ),
            default=None,
        ),
    ]

    total_input_tokens: Annotated[
        int | None,
        Field(
            description=inspect.cleandoc(
                """
                Total input (prompt) tokens consumed by the session; None if
                not reported by the platform
                """
            ),
            default=None,
        ),
    ]

    total_output_tokens: Annotated[
        int | None,
        Field(
            description=inspect.cleandoc(
                """
                Total output (completion) tokens produced by the session;
                None if not reported by the platform
                """
            ),
            default=None,
        ),
    ]

    total_tokens: Annotated[
        int,
        Field(
            description=inspect.cleandoc(
                """
                Sum of total_input_tokens and total_output_tokens; missing or
                null values are treated as 0
                """
            )
        ),
    ]


class GetAgentSessionTokenUsageResponse(RootModel):
    """
    Response model for the per-session agent token usage endpoint.

    Wraps a list of AgentSessionTokenUsageElement objects for a single agent,
    sorted by started_at ascending.

    Attributes:
        root: List of AgentSessionTokenUsageElement objects with per-session
            token usage and timing metadata.
    """

    root: Annotated[
        list[AgentSessionTokenUsageElement],
        Field(
            description=inspect.cleandoc(
                """
                List of per-session token usage objects for a single agent,
                sorted by started_at ascending
                """
            ),
            default_factory=list,
        ),
    ]


class SessionTurnTokenUsage(BaseModel):
    """
    Token usage figures for a single agent inference turn.

    Confirmed live against a real inference-succeeded event: the platform's
    tokenUsage keys are inputTokens, outputTokens, cacheReadTokens, and
    cacheCreationTokens. Extraction still checks a couple of alternate key
    spellings defensively, with a raw dict passthrough as a safety net in
    case a different provider/model uses different names.

    Attributes:
        input_tokens: Input (prompt) tokens for the turn.
        output_tokens: Output (completion) tokens for the turn.
        cache_read_tokens: Tokens served from prompt cache (cheaper than
            fresh input tokens).
        cache_creation_tokens: Tokens written to prompt cache on this turn.
        total_tokens: Total tokens for the turn, if present under any
            recognized key, else derived from input_tokens + output_tokens.
        raw: The untouched original tokenUsage dict, for cases where the
            real key names differ from the recognized candidates.
    """

    input_tokens: Annotated[
        int | None,
        Field(
            description=inspect.cleandoc(
                """
                Input (prompt) tokens for this turn; None if not present
                under any recognized key
                """
            ),
            default=None,
        ),
    ]

    output_tokens: Annotated[
        int | None,
        Field(
            description=inspect.cleandoc(
                """
                Output (completion) tokens for this turn; None if not
                present under any recognized key
                """
            ),
            default=None,
        ),
    ]

    cache_read_tokens: Annotated[
        int | None,
        Field(
            description=inspect.cleandoc(
                """
                Tokens served from prompt cache on this turn; None if not
                reported
                """
            ),
            default=None,
        ),
    ]

    cache_creation_tokens: Annotated[
        int | None,
        Field(
            description=inspect.cleandoc(
                """
                Tokens written to prompt cache on this turn; None if not
                reported
                """
            ),
            default=None,
        ),
    ]

    total_tokens: Annotated[
        int | None,
        Field(
            description=inspect.cleandoc(
                """
                Total tokens for this turn; None if not present under any
                recognized key and not derivable from input/output tokens
                """
            ),
            default=None,
        ),
    ]

    raw: Annotated[
        dict[str, Any] | None,
        Field(
            description=inspect.cleandoc(
                """
                Untouched original tokenUsage dict; safety net if the real
                platform key names differ from the recognized candidates
                """
            ),
            default=None,
        ),
    ]


class SessionTurnUsageElement(BaseModel):
    """
    Represents a single inference turn (succeeded or failed) within a session.

    Attributes:
        sequence_number: Ordering number for the turn within the session.
        timestamp: ISO 8601 timestamp when the turn was emitted.
        event_type: Turn outcome, "succeeded" or "failed".
        duration_ms: Duration of the inference call in milliseconds.
        token_usage: Token usage for succeeded turns; None for failed turns.
        error: Error text for failed turns; None for succeeded turns.
    """

    sequence_number: Annotated[
        int | None,
        Field(
            description=inspect.cleandoc(
                """
                Ordering number for this turn within the session
                """
            ),
            default=None,
        ),
    ]

    timestamp: Annotated[
        str | None,
        Field(
            description=inspect.cleandoc(
                """
                ISO 8601 timestamp when this turn was emitted
                """
            ),
            default=None,
        ),
    ]

    event_type: Annotated[
        str,
        Field(
            description=inspect.cleandoc(
                """
                Turn outcome, "succeeded" or "failed"
                """
            )
        ),
    ]

    duration_ms: Annotated[
        int | None,
        Field(
            description=inspect.cleandoc(
                """
                Duration of the inference call in milliseconds
                """
            ),
            default=None,
        ),
    ]

    token_usage: Annotated[
        SessionTurnTokenUsage | None,
        Field(
            description=inspect.cleandoc(
                """
                Token usage for succeeded turns; None for failed turns
                """
            ),
            default=None,
        ),
    ]

    error: Annotated[
        str | None,
        Field(
            description=inspect.cleandoc(
                """
                Error text for failed turns; None for succeeded turns
                """
            ),
            default=None,
        ),
    ]


class SessionTurnUsageSummary(BaseModel):
    """
    Aggregated summary across all inference turns in a session.

    Attributes:
        session_id: Unique session identifier.
        turn_count: Number of inference turns (succeeded and failed).
        total_duration_ms: Sum of turn durations; missing treated as 0.
        total_input_tokens: Sum of input tokens across succeeded turns;
            missing treated as 0.
        total_output_tokens: Sum of output tokens across succeeded turns;
            missing treated as 0.
        total_tokens: Sum of total_input_tokens and total_output_tokens.
    """

    session_id: Annotated[
        str,
        Field(
            description=inspect.cleandoc(
                """
                Unique session identifier
                """
            )
        ),
    ]

    turn_count: Annotated[
        int,
        Field(
            description=inspect.cleandoc(
                """
                Number of inference turns (succeeded and failed) in the
                session
                """
            )
        ),
    ]

    total_duration_ms: Annotated[
        int,
        Field(
            description=inspect.cleandoc(
                """
                Sum of turn durations in milliseconds; missing or null
                values are treated as 0
                """
            )
        ),
    ]

    total_input_tokens: Annotated[
        int,
        Field(
            description=inspect.cleandoc(
                """
                Sum of input tokens across succeeded turns; missing or null
                values are treated as 0
                """
            )
        ),
    ]

    total_output_tokens: Annotated[
        int,
        Field(
            description=inspect.cleandoc(
                """
                Sum of output tokens across succeeded turns; missing or null
                values are treated as 0
                """
            )
        ),
    ]

    total_tokens: Annotated[
        int,
        Field(
            description=inspect.cleandoc(
                """
                Sum of total_input_tokens and total_output_tokens
                """
            )
        ),
    ]


class DescribeSessionTokenUsageResponse(BaseModel):
    """
    Response model for the per-turn session token usage breakdown endpoint.

    Attributes:
        summary: Aggregated totals across all inference turns in the session.
        turns: Ordered list of per-turn usage details.
    """

    summary: Annotated[
        SessionTurnUsageSummary,
        Field(
            description=inspect.cleandoc(
                """
                Aggregated totals across all inference turns in the session
                """
            )
        ),
    ]

    turns: Annotated[
        list[SessionTurnUsageElement],
        Field(
            description=inspect.cleandoc(
                """
                Ordered list of per-turn usage details
                """
            ),
            default_factory=list,
        ),
    ]
