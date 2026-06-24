# Copyright (c) 2025 Itential, Inc
# GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

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
                started_at, end_time, duration_ms.

        Raises:
            Exception: If there is an error communicating with the Itential
                Platform API or if the API returns an unexpected response format.
        """
        limit = 100
        skip = 0
        results = []

        params: dict = {}
        if agent_name is not None:
            params["equalsField"] = "agentSnapshot.name"
            params["equals"] = agent_name

        while True:
            params["limit"] = limit
            params["skip"] = skip

            res = await self.client.get(
                "/agent-session-manager/sessions",
                params=params,
            )

            data = res.json()
            items = data.get("data", [])

            for item in items:
                results.append(
                    {
                        "session_id": item["sessionId"],
                        "agent_name": item.get("agentSnapshot", {}).get("name"),
                        "status": item["status"],
                        "started_at": item.get("startedAt"),
                        "end_time": item.get("endTime"),
                        "duration_ms": item.get("durationMs"),
                    }
                )

            total = data.get("metadata", {}).get("total", 0)
            if len(results) >= total:
                break

            skip += limit

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
        execution. Handles both list responses and dict responses that wrap
        the data under a "data" key.

        Args:
            session_id (str): Unique session identifier whose messages to retrieve.

        Returns:
            list[dict]: Ordered list of session event message dictionaries.

        Raises:
            Exception: If there is an error communicating with the Itential
                Platform API or if the session is not found.
        """
        res = await self.client.get(
            f"/agent-session-manager/sessions/{session_id}/messages"
        )
        data = res.json()

        if isinstance(data, list):
            return data

        return data.get("data", [])
