# Copyright (c) 2025 Itential, Inc
# GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import annotations

from typing import Annotated

from pydantic import Field

from fastmcp import Context

from itential_mcp.utilities import time as timeutils
from itential_mcp.models import agent_session_manager as models


__tags__ = ("agent_session_manager",)


async def get_sessions(
    ctx: Annotated[Context, Field(description="The FastMCP Context object")],
    agent_name: Annotated[
        str | None,
        Field(
            description="Optional agent name used to filter sessions",
            default=None,
        ),
    ],
) -> models.GetSessionsResponse:
    """
    List agent sessions from Itential Platform.

    Agent sessions are created when an agent automation is triggered via an
    endpoint trigger. Each session records the agent that ran, its execution
    status, and timing information.

    Args:
        ctx (Context): The FastMCP Context object.
        agent_name (str | None): Filter sessions to a specific agent by name.
            When omitted, all sessions are returned.

    Returns:
        models.GetSessionsResponse: List of session objects with the following fields:
            - session_id: Unique session identifier (use with describe_session)
            - agent_name: Name of the agent that ran
            - status: Session status (RUNNING, COMPLETE, FAILED)
            - started_at: ISO 8601 start timestamp
            - end_time: ISO 8601 end timestamp (None if still running)
            - duration_ms: Total session duration in milliseconds

    Notes:
        - Use describe_session with a session_id to get the full event log and output
        - Timestamps are converted from epoch milliseconds to ISO 8601 format
    """
    await ctx.info("inside get_sessions(...)")

    client = ctx.request_context.lifespan_context.get("client")

    data = await client.agent_session_manager.get_sessions(agent_name)

    session_elements = []

    for item in data:
        started_at = item.get("started_at")
        if isinstance(started_at, int):
            started_at = timeutils.epoch_to_timestamp(started_at)

        end_time = item.get("end_time")
        if isinstance(end_time, int):
            end_time = timeutils.epoch_to_timestamp(end_time)

        session_element = models.SessionElement(
            session_id=item["session_id"],
            agent_name=item.get("agent_name"),
            status=item["status"],
            started_at=started_at,
            end_time=end_time,
            duration_ms=item.get("duration_ms"),
        )
        session_elements.append(session_element)

    return models.GetSessionsResponse(root=session_elements)


async def describe_session(
    ctx: Annotated[Context, Field(description="The FastMCP Context object")],
    session_id: Annotated[
        str,
        Field(description="The session ID to retrieve full details for"),
    ],
) -> models.DescribeSessionResponse:
    """
    Get detailed information about a specific agent session.

    Returns the full session record including all event messages emitted
    during agent execution and the final text output produced by the agent.

    Args:
        ctx (Context): The FastMCP Context object.
        session_id (str): Unique session identifier. Session IDs are returned
            by get_sessions.

    Returns:
        models.DescribeSessionResponse: Full session details with the following fields:
            - session_id: Unique session identifier
            - agent_name: Name of the agent that ran
            - status: Session status (RUNNING, COMPLETE, FAILED)
            - output: Final text produced by the agent (None if not yet complete)
            - started_at: ISO 8601 start timestamp
            - end_time: ISO 8601 end timestamp (None if still running)
            - duration_ms: Total session duration in milliseconds
            - messages: Ordered list of session event messages

    Notes:
        - The output field is extracted from the inference-succeeded event message
        - Message timestamps are converted from epoch milliseconds to ISO 8601 format
    """
    await ctx.info("inside describe_session(...)")

    client = ctx.request_context.lifespan_context.get("client")

    session = await client.agent_session_manager.get_session(session_id)
    raw_messages = await client.agent_session_manager.get_session_messages(session_id)

    agent_snapshot = session.get("agentSnapshot") or {}
    agent_name = agent_snapshot.get("name")

    started_at = session.get("startedAt")
    if isinstance(started_at, int):
        started_at = timeutils.epoch_to_timestamp(started_at)

    end_time = session.get("endTime")
    if isinstance(end_time, int):
        end_time = timeutils.epoch_to_timestamp(end_time)

    messages = []
    output = None

    for raw in raw_messages:
        msg_timestamp = raw.get("timestamp")
        if isinstance(msg_timestamp, int):
            msg_timestamp = timeutils.epoch_to_timestamp(msg_timestamp)

        msg = models.SessionMessage(
            type=raw.get("type", ""),
            category=raw.get("category"),
            text=raw.get("text"),
            timestamp=msg_timestamp,
        )
        messages.append(msg)

        if raw.get("type") == "inference-succeeded" and raw.get("text") is not None:
            output = raw["text"]

    return models.DescribeSessionResponse(
        session_id=session.get("sessionId", session_id),
        agent_name=agent_name,
        status=session.get("status", ""),
        output=output,
        started_at=started_at,
        end_time=end_time,
        duration_ms=session.get("durationMs"),
        messages=messages,
    )
