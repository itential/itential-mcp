# Copyright (c) 2025 Itential, Inc
# GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import annotations

from itential_mcp.core import logging
from itential_mcp.platform.services import ServiceBase


class Service(ServiceBase):
    """AgentSessionManager service for Itential Platform agent session access.

    This service provides methods for interacting with the Itential Platform's
    AgentSessionManager component, which manages agent execution sessions.
    Sessions are created when an agent automation is triggered via an endpoint
    trigger and record the full event log and final output produced by the agent.

    Attributes:
        name (str): The service identifier used for registration and routing.
            Set to "agent_session_manager".

    Inherits:
        ServiceBase: Base service class providing common functionality including
            client initialization and configuration management.
    """

    name: str = "agent_session_manager"

    async def get_sessions(self, agent_name: str | None = None) -> list[dict]:
        """Retrieve agent sessions from Itential Platform.

        Queries the AgentSessionManager to fetch agent execution sessions,
        implementing pagination to handle large result sets. Optionally filters
        results to a specific agent by name.

        Args:
            agent_name (str | None): Optional agent name to filter sessions.
                When provided, only sessions where the agent snapshot name
                matches this value are returned. Defaults to None.

        Returns:
            list[dict]: A list of dictionaries containing session data with
                normalized field names: session_id, agent_name, status,
                started_at, end_time, duration_ms, total_input_tokens,
                total_output_tokens. Sessions that failed before an
                execution-engine session ID was assigned (no sessionId) are
                skipped.

        Raises:
            Exception: If there is an error communicating with the Itential
                Platform API or if the API returns an unexpected response format.
        """
        limit = 100
        offset = 0
        results = []

        while True:
            params: dict = {"limit": limit, "offset": offset}

            res = await self.client.get(
                "/agent-session-manager/sessions",
                params=params,
            )

            data = res.json()
            items = data.get("data", [])

            if not items:
                break

            for item in items:
                session_id = item.get("sessionId")
                if session_id is None:
                    # Sessions that failed before the execution engine
                    # assigned an ID carry no sessionId and cannot be
                    # inspected, so they are not listed.
                    logging.debug(
                        "Skipping agent session without a sessionId "
                        f"(status={item.get('status')})"
                    )
                    continue

                results.append(
                    {
                        "session_id": session_id,
                        "agent_name": item.get("agentSnapshot", {}).get("name"),
                        "status": item.get("status"),
                        "started_at": item.get("startedAt"),
                        "end_time": item.get("endTime"),
                        "duration_ms": item.get("durationMs"),
                        "total_input_tokens": item.get("totalInputTokens"),
                        "total_output_tokens": item.get("totalOutputTokens"),
                    }
                )

            total = data.get("total", 0)
            offset += limit
            if offset >= total:
                break

        if agent_name is not None:
            results = [r for r in results if r["agent_name"] == agent_name]

        return results

    async def get_session(self, session_id: str) -> dict:
        """Retrieve detailed information about a specific agent session.

        Fetches the full session record from the AgentSessionManager for the
        given session identifier.

        Args:
            session_id (str): Unique session identifier to retrieve.

        Returns:
            dict: Session details as returned by the platform API.

        Raises:
            Exception: If there is an error communicating with the Itential
                Platform API or if the session is not found.
        """
        res = await self.client.get(f"/agent-session-manager/sessions/{session_id}")
        return res.json()

    async def get_session_messages(self, session_id: str) -> list[dict]:
        """Retrieve the event messages for a specific agent session.

        Fetches the ordered list of event messages emitted during agent
        execution. The endpoint paginates server-side with a default page
        size, so this method pages through the results internally using
        explicit limit/offset params until the complete event log has been
        retrieved. Handles both list responses and dict responses that wrap
        the data under a "data" key.

        Args:
            session_id (str): Unique session identifier whose messages to retrieve.

        Returns:
            list[dict]: Ordered list of session event message dictionaries.

        Raises:
            Exception: If there is an error communicating with the Itential
                Platform API or if the session is not found.
        """
        # TODO: consider making the page size configurable via config instead
        # of hardcoded, if larger session event logs become common.
        limit = 100
        offset = 0
        results = []

        while True:
            params: dict = {"limit": limit, "offset": offset}

            res = await self.client.get(
                f"/agent-session-manager/sessions/{session_id}/messages",
                params=params,
            )
            data = res.json()

            if isinstance(data, list):
                items = data
            else:
                items = data.get("data", [])

            results.extend(items)

            if len(items) < limit:
                break

            offset += limit

        return results
