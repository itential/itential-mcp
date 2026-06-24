# Copyright (c) 2025 Itential, Inc
# GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import annotations

import inspect

from typing import Annotated

from pydantic import BaseModel, Field, RootModel


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

    Provides the full detail of an agent session including the complete event
    log and the final output text produced by the agent. Use this model to
    inspect what the agent did and what it returned.

    Attributes:
        session_id: Unique session identifier.
        agent_name: Name of the agent that ran.
        status: Session status (RUNNING, COMPLETE, FAILED).
        output: Final text output produced by the agent (from the
            inference-succeeded event). None if the session has not yet
            completed or produced no output.
        started_at: ISO 8601 start timestamp.
        end_time: ISO 8601 end timestamp (None if still running).
        duration_ms: Total session duration in milliseconds.
        messages: Ordered list of session event messages.
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
                Final text output produced by the agent; extracted from the
                inference-succeeded event. None if the session has not completed
                or produced no text output.
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

    messages: Annotated[
        list[SessionMessage],
        Field(
            description=inspect.cleandoc(
                """
                Ordered list of session event messages captured during agent execution
                """
            ),
            default_factory=list,
        ),
    ]
