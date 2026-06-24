# Copyright (c) 2025 Itential, Inc
# GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

import pytest
from unittest.mock import AsyncMock, MagicMock

from ipsdk.platform import AsyncPlatform

from itential_mcp.platform.services import ServiceBase
from itential_mcp.platform.services.agent_session_manager import Service


class TestService:
    """Test the agent_session_manager Service class"""

    @pytest.fixture
    def mock_client(self):
        """Create a mock AsyncPlatform client"""
        return AsyncMock(spec=AsyncPlatform)

    @pytest.fixture
    def service(self, mock_client):
        """Create a Service instance with mock client"""
        return Service(mock_client)

    def test_service_initialization(self, mock_client):
        """Test Service initialization"""
        service = Service(mock_client)

        assert service.client == mock_client
        assert service.name == "agent_session_manager"

    def test_service_inherits_service_base(self, service):
        """Test Service inherits from ServiceBase"""
        assert isinstance(service, ServiceBase)
        assert hasattr(service, "client")

    def test_service_name_attribute(self, service):
        """Test Service has correct name attribute"""
        assert service.name == "agent_session_manager"


class TestGetSessions:
    """Test the get_sessions method"""

    @pytest.fixture
    def mock_client(self):
        return AsyncMock(spec=AsyncPlatform)

    @pytest.fixture
    def service(self, mock_client):
        return Service(mock_client)

    @pytest.mark.asyncio
    async def test_get_sessions_no_filter_returns_all(self, service, mock_client):
        """Test get_sessions with no agent_name filter returns all sessions"""
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "data": [
                {
                    "sessionId": "sess-001",
                    "status": "COMPLETE",
                    "agentSnapshot": {"name": "agent-a"},
                    "startedAt": "2025-06-01T10:00:00Z",
                    "endTime": "2025-06-01T10:01:00Z",
                    "durationMs": 60000,
                },
                {
                    "sessionId": "sess-002",
                    "status": "RUNNING",
                    "agentSnapshot": {"name": "agent-b"},
                    "startedAt": "2025-06-01T11:00:00Z",
                },
            ],
            "metadata": {"total": 2},
        }
        mock_client.get.return_value = mock_response

        result = await service.get_sessions()

        assert len(result) == 2
        assert result[0]["session_id"] == "sess-001"
        assert result[0]["agent_name"] == "agent-a"
        assert result[0]["status"] == "COMPLETE"
        assert result[0]["duration_ms"] == 60000
        assert result[1]["session_id"] == "sess-002"
        assert result[1]["end_time"] is None

    @pytest.mark.asyncio
    async def test_get_sessions_agent_name_filter_passes_correct_params(
        self, service, mock_client
    ):
        """Test get_sessions passes equalsField and equals params when agent_name given"""
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "data": [
                {
                    "sessionId": "sess-001",
                    "status": "COMPLETE",
                    "agentSnapshot": {"name": "my-agent"},
                }
            ],
            "metadata": {"total": 1},
        }
        mock_client.get.return_value = mock_response

        result = await service.get_sessions(agent_name="my-agent")

        call_kwargs = mock_client.get.call_args
        params = (
            call_kwargs[1]["params"]
            if "params" in call_kwargs[1]
            else call_kwargs[0][1]
        )
        assert params.get("equalsField") == "agentSnapshot.name"
        assert params.get("equals") == "my-agent"
        assert len(result) == 1
        assert result[0]["agent_name"] == "my-agent"

    @pytest.mark.asyncio
    async def test_get_sessions_pagination(self, service, mock_client):
        """Test get_sessions paginates until all results are retrieved"""
        page1 = MagicMock()
        page1.json.return_value = {
            "data": [{"sessionId": "sess-001", "status": "COMPLETE"}],
            "metadata": {"total": 2},
        }
        page2 = MagicMock()
        page2.json.return_value = {
            "data": [{"sessionId": "sess-002", "status": "FAILED"}],
            "metadata": {"total": 2},
        }
        mock_client.get.side_effect = [page1, page2]

        result = await service.get_sessions()

        assert len(result) == 2
        assert mock_client.get.call_count == 2

    @pytest.mark.asyncio
    async def test_get_sessions_empty_result(self, service, mock_client):
        """Test get_sessions returns empty list when no sessions exist"""
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "data": [],
            "metadata": {"total": 0},
        }
        mock_client.get.return_value = mock_response

        result = await service.get_sessions()

        assert result == []

    @pytest.mark.asyncio
    async def test_get_sessions_missing_agent_snapshot(self, service, mock_client):
        """Test get_sessions handles sessions with no agentSnapshot gracefully"""
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "data": [
                {
                    "sessionId": "sess-001",
                    "status": "COMPLETE",
                }
            ],
            "metadata": {"total": 1},
        }
        mock_client.get.return_value = mock_response

        result = await service.get_sessions()

        assert result[0]["agent_name"] is None

    @pytest.mark.asyncio
    async def test_get_sessions_client_error_propagates(self, service, mock_client):
        """Test get_sessions propagates client errors"""
        mock_client.get.side_effect = Exception("connection refused")

        with pytest.raises(Exception, match="connection refused"):
            await service.get_sessions()


class TestGetSession:
    """Test the get_session method"""

    @pytest.fixture
    def mock_client(self):
        return AsyncMock(spec=AsyncPlatform)

    @pytest.fixture
    def service(self, mock_client):
        return Service(mock_client)

    @pytest.mark.asyncio
    async def test_get_session_returns_data(self, service, mock_client):
        """Test get_session returns the parsed JSON response"""
        session_data = {
            "sessionId": "sess-001",
            "status": "COMPLETE",
            "agentSnapshot": {"name": "my-agent"},
        }
        mock_response = MagicMock()
        mock_response.json.return_value = session_data
        mock_client.get.return_value = mock_response

        result = await service.get_session("sess-001")

        assert result == session_data
        mock_client.get.assert_called_once_with(
            "/agent-session-manager/sessions/sess-001"
        )

    @pytest.mark.asyncio
    async def test_get_session_client_error_propagates(self, service, mock_client):
        """Test get_session propagates client errors"""
        mock_client.get.side_effect = Exception("not found")

        with pytest.raises(Exception, match="not found"):
            await service.get_session("sess-missing")


class TestGetSessionMessages:
    """Test the get_session_messages method"""

    @pytest.fixture
    def mock_client(self):
        return AsyncMock(spec=AsyncPlatform)

    @pytest.fixture
    def service(self, mock_client):
        return Service(mock_client)

    @pytest.mark.asyncio
    async def test_get_session_messages_list_response(self, service, mock_client):
        """Test get_session_messages handles a bare list response"""
        messages = [
            {"type": "tool-call", "text": "calling list_devices"},
            {"type": "inference-succeeded", "text": "Done."},
        ]
        mock_response = MagicMock()
        mock_response.json.return_value = messages
        mock_client.get.return_value = mock_response

        result = await service.get_session_messages("sess-001")

        assert result == messages
        assert len(result) == 2

    @pytest.mark.asyncio
    async def test_get_session_messages_dict_response(self, service, mock_client):
        """Test get_session_messages handles a dict-wrapped response"""
        messages = [{"type": "inference-succeeded", "text": "Output text."}]
        mock_response = MagicMock()
        mock_response.json.return_value = {"data": messages}
        mock_client.get.return_value = mock_response

        result = await service.get_session_messages("sess-001")

        assert result == messages

    @pytest.mark.asyncio
    async def test_get_session_messages_empty_dict_response(self, service, mock_client):
        """Test get_session_messages returns empty list when data key is absent"""
        mock_response = MagicMock()
        mock_response.json.return_value = {}
        mock_client.get.return_value = mock_response

        result = await service.get_session_messages("sess-001")

        assert result == []

    @pytest.mark.asyncio
    async def test_get_session_messages_uses_correct_endpoint(
        self, service, mock_client
    ):
        """Test get_session_messages calls the correct API endpoint"""
        mock_response = MagicMock()
        mock_response.json.return_value = []
        mock_client.get.return_value = mock_response

        await service.get_session_messages("sess-xyz")

        mock_client.get.assert_called_once_with(
            "/agent-session-manager/sessions/sess-xyz/messages"
        )
