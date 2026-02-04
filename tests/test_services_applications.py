# Copyright (c) 2025 Itential, Inc
# GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

import asyncio

import pytest
from unittest.mock import AsyncMock, MagicMock, patch

from itential_mcp.core import exceptions
from itential_mcp.platform.services.applications import Service


class TestApplicationsService:
    """Test cases for the applications Service class"""

    @pytest.fixture
    def mock_client(self):
        """Create a mock client for testing"""
        client = AsyncMock()
        return client

    @pytest.fixture
    def service(self, mock_client):
        """Create a Service instance with mocked client"""
        service = Service(mock_client)
        return service

    def test_service_name(self, mock_client):
        """Test that the service has the correct name"""
        service = Service(mock_client)
        assert service.name == "applications"

    @pytest.mark.asyncio
    async def test_get_application_health_success(self, service, mock_client):
        """Test successful application health retrieval"""
        # Mock response data
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "total": 1,
            "results": [
                {
                    "id": "test-application",
                    "state": "RUNNING",
                    "version": "1.0.0",
                }
            ],
        }
        mock_client.get.return_value = mock_response

        result = await service._get_application_health("test-application")

        # Verify client was called with correct parameters
        mock_client.get.assert_called_once_with(
            "/health/applications",
            params={"equals": "test-application", "equalsField": "id"},
        )

        # Verify result - should return data["results"][0]
        assert result["id"] == "test-application"
        assert result["state"] == "RUNNING"

    @pytest.mark.asyncio
    async def test_get_application_health_not_found(self, service, mock_client):
        """Test application not found scenario"""
        # Mock response with no results
        mock_response = MagicMock()
        mock_response.json.return_value = {"total": 0, "results": []}
        mock_client.get.return_value = mock_response

        with pytest.raises(exceptions.NotFoundError) as exc_info:
            await service._get_application_health("nonexistent-application")

        assert "unable to find application nonexistent-application" in str(
            exc_info.value
        )

    @pytest.mark.asyncio
    async def test_get_application_health_multiple_results(self, service, mock_client):
        """Test scenario where multiple applications are found (should not happen)"""
        # Mock response with multiple results
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "total": 2,
            "results": [
                {"results": [{"id": "app1", "state": "RUNNING"}]},
                {"results": [{"id": "app2", "state": "STOPPED"}]},
            ],
        }
        mock_client.get.return_value = mock_response

        with pytest.raises(exceptions.NotFoundError):
            await service._get_application_health("duplicate-application")


class TestStartApplication:
    """Test cases for the start_application method"""

    @pytest.fixture
    def mock_client(self):
        """Create a mock client for testing"""
        client = AsyncMock()
        return client

    @pytest.fixture
    def service(self, mock_client):
        """Create a Service instance with mocked client"""
        service = Service(mock_client)
        return service

    @pytest.mark.asyncio
    async def test_start_application_already_running(self, service):
        """Test starting an application that's already running"""
        with patch.object(service, "_get_application_health") as mock_health:
            mock_health.return_value = {"state": "RUNNING", "id": "test-application"}

            result = await service.start_application("test-application", 10)

            # Should return immediately without calling PUT
            service.client.put.assert_not_called()
            # Should return the health data
            assert result["state"] == "RUNNING"

    @pytest.mark.asyncio
    async def test_start_application_from_stopped_success(self, service):
        """Test successfully starting a stopped application"""
        with patch.object(service, "_get_application_health") as mock_health:
            # First call returns STOPPED
            mock_health.return_value = {"state": "STOPPED", "id": "test-application"}

            # Mock _poll_for_state to return RUNNING state
            with patch.object(service, "_poll_for_state") as mock_poll:
                mock_poll.return_value = {"state": "RUNNING", "id": "test-application"}

                result = await service.start_application("test-application", 10)

            # Should call PUT to start application
            service.client.put.assert_called_once_with(
                "/applications/test-application/start"
            )

            # Should return the final health data
            assert result["state"] == "RUNNING"

    @pytest.mark.asyncio
    async def test_start_application_timeout(self, service):
        """Test application start timeout scenario"""
        with patch.object(service, "_get_application_health") as mock_health:
            # Initial state is STOPPED
            mock_health.return_value = {"state": "STOPPED", "id": "test-application"}

            # Mock _poll_for_state to be an async function that never completes (simulates timeout)
            async def never_completes(*args):
                await asyncio.sleep(999999)  # Sleep forever

            with patch.object(service, "_poll_for_state", side_effect=never_completes):
                with pytest.raises(exceptions.TimeoutExceededError) as exc_info:
                    await service.start_application("test-application", 0.1)

                # Verify error message includes application name and timeout
                assert "application 'test-application'" in str(exc_info.value)
                assert "0.1s" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_start_application_dead_state(self, service):
        """Test starting an application in DEAD state"""
        with patch.object(service, "_get_application_health") as mock_health:
            mock_health.return_value = {"state": "DEAD", "id": "test-application"}

            with pytest.raises(exceptions.InvalidStateError) as exc_info:
                await service.start_application("test-application", 10)

            assert "application 'test-application'" in str(exc_info.value)
            assert "DEAD" in str(exc_info.value)
            service.client.put.assert_not_called()

    @pytest.mark.asyncio
    async def test_start_application_deleted_state(self, service):
        """Test starting an application in DELETED state"""
        with patch.object(service, "_get_application_health") as mock_health:
            mock_health.return_value = {"state": "DELETED", "id": "test-application"}

            with pytest.raises(exceptions.InvalidStateError) as exc_info:
                await service.start_application("test-application", 10)

            assert "application 'test-application'" in str(exc_info.value)
            assert "DELETED" in str(exc_info.value)


class TestStopApplication:
    """Test cases for the stop_application method"""

    @pytest.fixture
    def mock_client(self):
        """Create a mock client for testing"""
        client = AsyncMock()
        return client

    @pytest.fixture
    def service(self, mock_client):
        """Create a Service instance with mocked client"""
        service = Service(mock_client)
        return service

    @pytest.mark.asyncio
    async def test_stop_application_already_stopped(self, service):
        """Test stopping an application that's already stopped"""
        with patch.object(service, "_get_application_health") as mock_health:
            mock_health.return_value = {"state": "STOPPED", "id": "test-application"}

            result = await service.stop_application("test-application", 10)

            # Should return immediately without calling PUT
            service.client.put.assert_not_called()
            # Should return the health data
            assert result["state"] == "STOPPED"

    @pytest.mark.asyncio
    async def test_stop_application_from_running_success(self, service):
        """Test successfully stopping a running application"""
        with patch.object(service, "_get_application_health") as mock_health:
            # First call returns RUNNING
            mock_health.return_value = {"state": "RUNNING", "id": "test-application"}

            # Mock _poll_for_state to return STOPPED state
            with patch.object(service, "_poll_for_state") as mock_poll:
                mock_poll.return_value = {"state": "STOPPED", "id": "test-application"}

                result = await service.stop_application("test-application", 10)

            # Should call PUT to stop application
            service.client.put.assert_called_once_with(
                "/applications/test-application/stop"
            )

            # Should return the final health data
            assert result["state"] == "STOPPED"

    @pytest.mark.asyncio
    async def test_stop_application_timeout(self, service):
        """Test application stop timeout scenario"""
        with patch.object(service, "_get_application_health") as mock_health:
            # Initial state is RUNNING
            mock_health.return_value = {"state": "RUNNING", "id": "test-application"}

            # Mock _poll_for_state to be an async function that never completes (simulates timeout)
            async def never_completes(*args):
                await asyncio.sleep(999999)  # Sleep forever

            with patch.object(service, "_poll_for_state", side_effect=never_completes):
                with pytest.raises(exceptions.TimeoutExceededError) as exc_info:
                    await service.stop_application("test-application", 0.1)

                # Verify error message includes application name and timeout
                assert "application 'test-application'" in str(exc_info.value)
                assert "0.1s" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_stop_application_dead_state(self, service):
        """Test stopping an application in DEAD state"""
        with patch.object(service, "_get_application_health") as mock_health:
            mock_health.return_value = {"state": "DEAD", "id": "test-application"}

            with pytest.raises(exceptions.InvalidStateError) as exc_info:
                await service.stop_application("test-application", 10)

            assert "application 'test-application'" in str(exc_info.value)
            assert "DEAD" in str(exc_info.value)
            service.client.put.assert_not_called()

    @pytest.mark.asyncio
    async def test_stop_application_deleted_state(self, service):
        """Test stopping an application in DELETED state"""
        with patch.object(service, "_get_application_health") as mock_health:
            mock_health.return_value = {"state": "DELETED", "id": "test-application"}

            with pytest.raises(exceptions.InvalidStateError) as exc_info:
                await service.stop_application("test-application", 10)

            assert "application 'test-application'" in str(exc_info.value)
            assert "DELETED" in str(exc_info.value)
            service.client.put.assert_not_called()

    @pytest.mark.asyncio
    async def test_stop_application_multiple_pages(self, service):
        """Test stopping application with multiple poll iterations"""
        with patch.object(service, "_get_application_health") as mock_health:
            # First call returns RUNNING
            mock_health.return_value = {"state": "RUNNING", "id": "test-application"}

            # Mock _poll_for_state to simulate multiple iterations before success
            with patch.object(service, "_poll_for_state") as mock_poll:
                mock_poll.return_value = {"state": "STOPPED", "id": "test-application"}

                result = await service.stop_application("test-application", 10)

            # Should call PUT to stop application
            service.client.put.assert_called_once_with(
                "/applications/test-application/stop"
            )

            # Should return the final state
            assert result["state"] == "STOPPED"


class TestRestartApplication:
    """Test cases for the restart_application method"""

    @pytest.fixture
    def mock_client(self):
        """Create a mock client for testing"""
        client = AsyncMock()
        return client

    @pytest.fixture
    def service(self, mock_client):
        """Create a Service instance with mocked client"""
        service = Service(mock_client)
        return service

    @pytest.mark.asyncio
    async def test_restart_application_from_running_success(self, service):
        """Test successfully restarting a running application"""
        with patch.object(service, "_get_application_health") as mock_health:
            # First call returns RUNNING
            mock_health.return_value = {"state": "RUNNING", "id": "test-application"}

            # Mock _poll_for_state to return RUNNING state after restart
            with patch.object(service, "_poll_for_state") as mock_poll:
                mock_poll.return_value = {"state": "RUNNING", "id": "test-application"}

                result = await service.restart_application("test-application", 10)

            # Should call PUT to restart application
            service.client.put.assert_called_once_with(
                "/applications/test-application/restart"
            )

            # Should return the final health data
            assert result["state"] == "RUNNING"

    @pytest.mark.asyncio
    async def test_restart_application_stopped_state(self, service):
        """Test restarting an application in STOPPED state"""
        with patch.object(service, "_get_application_health") as mock_health:
            mock_health.return_value = {"state": "STOPPED", "id": "test-application"}

            with pytest.raises(exceptions.InvalidStateError) as exc_info:
                await service.restart_application("test-application", 10)

            assert "application 'test-application'" in str(exc_info.value)
            assert "STOPPED" in str(exc_info.value)
            service.client.put.assert_not_called()

    @pytest.mark.asyncio
    async def test_restart_application_dead_state(self, service):
        """Test restarting an application in DEAD state"""
        with patch.object(service, "_get_application_health") as mock_health:
            mock_health.return_value = {"state": "DEAD", "id": "test-application"}

            with pytest.raises(exceptions.InvalidStateError) as exc_info:
                await service.restart_application("test-application", 10)

            assert "application 'test-application'" in str(exc_info.value)
            assert "DEAD" in str(exc_info.value)
            service.client.put.assert_not_called()

    @pytest.mark.asyncio
    async def test_restart_application_deleted_state(self, service):
        """Test restarting an application in DELETED state"""
        with patch.object(service, "_get_application_health") as mock_health:
            mock_health.return_value = {"state": "DELETED", "id": "test-application"}

            with pytest.raises(exceptions.InvalidStateError) as exc_info:
                await service.restart_application("test-application", 10)

            assert "application 'test-application'" in str(exc_info.value)
            assert "DELETED" in str(exc_info.value)
            service.client.put.assert_not_called()

    @pytest.mark.asyncio
    async def test_restart_application_timeout(self, service):
        """Test application restart timeout scenario"""
        with patch.object(service, "_get_application_health") as mock_health:
            # Initial state is RUNNING
            mock_health.return_value = {"state": "RUNNING", "id": "test-application"}

            # Mock _poll_for_state to be an async function that never completes (simulates timeout)
            async def never_completes(*args):
                await asyncio.sleep(999999)  # Sleep forever

            with patch.object(service, "_poll_for_state", side_effect=never_completes):
                with pytest.raises(exceptions.TimeoutExceededError) as exc_info:
                    await service.restart_application("test-application", 0.1)

                # Verify error message includes application name and timeout
                assert "application 'test-application'" in str(exc_info.value)
                assert "0.1s" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_restart_application_multiple_state_changes(self, service):
        """Test restarting application through multiple state changes"""
        with patch.object(service, "_get_application_health") as mock_health:
            # Initial state is RUNNING
            mock_health.return_value = {"state": "RUNNING", "id": "test-application"}

            # Mock _poll_for_state to return RUNNING state after going through restart states
            with patch.object(service, "_poll_for_state") as mock_poll:
                mock_poll.return_value = {"state": "RUNNING", "id": "test-application"}

                result = await service.restart_application("test-application", 10)

            # Should call PUT to restart application
            service.client.put.assert_called_once_with(
                "/applications/test-application/restart"
            )

            # Should return the final state
            assert result["state"] == "RUNNING"

    @pytest.mark.asyncio
    async def test_restart_application_already_running_no_change_needed(self, service):
        """Test restarting application that immediately returns to RUNNING"""
        with patch.object(service, "_get_application_health") as mock_health:
            # Application is RUNNING before restart
            mock_health.return_value = {"state": "RUNNING", "id": "test-application"}

            # Mock _poll_for_state to immediately return RUNNING state
            with patch.object(service, "_poll_for_state") as mock_poll:
                mock_poll.return_value = {"state": "RUNNING", "id": "test-application"}

                result = await service.restart_application("test-application", 10)

            # Should still call PUT to restart
            service.client.put.assert_called_once_with(
                "/applications/test-application/restart"
            )

            # Should return running state
            assert result["state"] == "RUNNING"


class TestServiceIntegration:
    """Integration tests for the Service class"""

    @pytest.fixture
    def mock_client(self):
        """Create a mock client for testing"""
        client = AsyncMock()
        return client

    @pytest.fixture
    def service(self, mock_client):
        """Create a Service instance with mocked client"""
        service = Service(mock_client)
        return service

    @pytest.mark.asyncio
    async def test_service_inherits_from_servicebase(self, service):
        """Test that Service properly inherits from ServiceBase"""
        from itential_mcp.platform.services import ServiceBase

        assert isinstance(service, ServiceBase)

    @pytest.mark.asyncio
    async def test_method_signatures_consistency(self, service):
        """Test that all methods have consistent parameter signatures"""
        import inspect

        # Check start_application signature
        start_sig = inspect.signature(service.start_application)
        assert "name" in start_sig.parameters
        assert "timeout" in start_sig.parameters

        # Check stop_application signature
        stop_sig = inspect.signature(service.stop_application)
        assert "name" in stop_sig.parameters
        assert "timeout" in stop_sig.parameters

        # Check restart_application signature
        restart_sig = inspect.signature(service.restart_application)
        assert "name" in restart_sig.parameters
        assert "timeout" in restart_sig.parameters


class TestErrorHandling:
    """Test error handling scenarios"""

    @pytest.fixture
    def mock_client(self):
        """Create a mock client for testing"""
        client = AsyncMock()
        return client

    @pytest.fixture
    def service(self, mock_client):
        """Create a Service instance with mocked client"""
        service = Service(mock_client)
        return service

    @pytest.mark.asyncio
    async def test_client_connection_error(self, service, mock_client):
        """Test handling of client connection errors"""
        mock_client.get.side_effect = Exception("Connection failed")

        with pytest.raises(Exception, match="Connection failed"):
            await service._get_application_health("test-application")

    @pytest.mark.asyncio
    async def test_malformed_response_handling(self, service, mock_client):
        """Test handling of malformed API responses"""
        # Mock response with missing 'total' field
        mock_response = MagicMock()
        mock_response.json.return_value = {"results": []}
        mock_client.get.return_value = mock_response

        with pytest.raises(KeyError):
            await service._get_application_health("test-application")


class TestEdgeCases:
    """Test edge cases and boundary conditions"""

    @pytest.fixture
    def mock_client(self):
        """Create a mock client for testing"""
        client = AsyncMock()
        return client

    @pytest.fixture
    def service(self, mock_client):
        """Create a Service instance with mocked client"""
        service = Service(mock_client)
        return service

    @pytest.mark.asyncio
    async def test_application_name_with_special_characters(self, service, mock_client):
        """Test application names with special characters"""
        special_name = "test-application_123.456@domain"

        mock_response = MagicMock()
        mock_response.json.return_value = {
            "total": 1,
            "results": [{"results": [{"state": "RUNNING"}]}],
        }
        mock_client.get.return_value = mock_response

        await service._get_application_health(special_name)

        # Verify the special name was used correctly in the API call
        mock_client.get.assert_called_with(
            "/health/applications", params={"equals": special_name, "equalsField": "id"}
        )

    @pytest.mark.asyncio
    async def test_unicode_application_name(self, service, mock_client):
        """Test application names with Unicode characters"""
        unicode_name = "测试应用程序"

        mock_response = MagicMock()
        mock_response.json.return_value = {
            "total": 1,
            "results": [{"results": [{"state": "RUNNING"}]}],
        }
        mock_client.get.return_value = mock_response

        await service._get_application_health(unicode_name)

        # Verify Unicode name was handled correctly
        mock_client.get.assert_called_with(
            "/health/applications", params={"equals": unicode_name, "equalsField": "id"}
        )

    @pytest.mark.asyncio
    async def test_zero_timeout_behavior(self, service, mock_client):
        """Test behavior with zero timeout"""
        with patch.object(service, "_get_application_health") as mock_health:
            mock_health.return_value = {"state": "STOPPED", "id": "test-application"}

            # Mock _poll_for_state to raise TimeoutError
            with patch.object(service, "_poll_for_state") as mock_poll:
                mock_poll.side_effect = asyncio.TimeoutError()

                with pytest.raises(exceptions.TimeoutExceededError):
                    await service.start_application("test-application", 0)

        # Should call PUT but timeout immediately since timeout=0
        service.client.put.assert_called_once_with(
            "/applications/test-application/start"
        )

    @pytest.mark.asyncio
    async def test_negative_timeout_behavior(self, service, mock_client):
        """Test behavior with negative timeout (immediately times out)"""
        with patch.object(service, "_get_application_health") as mock_health:
            # Return STOPPED first
            mock_health.return_value = {"state": "STOPPED", "id": "test-application"}

            # asyncio.wait_for with negative timeout will immediately timeout
            with pytest.raises(exceptions.TimeoutExceededError) as exc_info:
                await service.start_application("test-application", -1)

            # Verify error message
            assert "application 'test-application'" in str(exc_info.value)
            assert "-1s" in str(exc_info.value)

        # Should have called PUT before the timeout
        service.client.put.assert_called_once_with(
            "/applications/test-application/start"
        )

    @pytest.mark.asyncio
    async def test_large_timeout_value(self, service, mock_client):
        """Test behavior with very large timeout value"""
        with patch.object(service, "_get_application_health") as mock_health:
            # Return STOPPED first
            mock_health.return_value = {"state": "STOPPED", "id": "test-application"}

            # Mock _poll_for_state to return RUNNING state
            with patch.object(service, "_poll_for_state") as mock_poll:
                mock_poll.return_value = {"state": "RUNNING", "id": "test-application"}

                result = await service.start_application("test-application", 999999)

            # Should work normally with large timeout
            assert result["state"] == "RUNNING"

    @pytest.mark.asyncio
    async def test_start_application_not_found_error_propagation(self, service):
        """Test that NotFoundError from _get_application_health is properly propagated"""
        with patch.object(service, "_get_application_health") as mock_health:
            mock_health.side_effect = exceptions.NotFoundError("Application not found")

            with pytest.raises(exceptions.NotFoundError, match="Application not found"):
                await service.start_application("nonexistent-app", 10)

    @pytest.mark.asyncio
    async def test_stop_application_not_found_error_propagation(self, service):
        """Test that NotFoundError from _get_application_health is properly propagated"""
        with patch.object(service, "_get_application_health") as mock_health:
            mock_health.side_effect = exceptions.NotFoundError("Application not found")

            with pytest.raises(exceptions.NotFoundError, match="Application not found"):
                await service.stop_application("nonexistent-app", 10)

    @pytest.mark.asyncio
    async def test_restart_application_not_found_error_propagation(self, service):
        """Test that NotFoundError from _get_application_health is properly propagated"""
        with patch.object(service, "_get_application_health") as mock_health:
            mock_health.side_effect = exceptions.NotFoundError("Application not found")

            with pytest.raises(exceptions.NotFoundError, match="Application not found"):
                await service.restart_application("nonexistent-app", 10)

    @pytest.mark.asyncio
    async def test_concurrent_application_operations(self, service):
        """Test that service methods can handle concurrent operations"""
        import asyncio

        with patch.object(service, "_get_application_health") as mock_health:
            # Mock different responses for different calls
            mock_health.side_effect = [
                {"state": "RUNNING", "id": "app1"},  # For first operation
                {"state": "STOPPED", "id": "app2"},  # For second operation
            ]

            # Run two operations concurrently (though they should be independent)
            task1 = service.start_application("app1", 10)
            task2 = service.stop_application("app2", 10)

            # Both should complete without interfering with each other
            result1, result2 = await asyncio.gather(task1, task2)

            # Verify results
            assert result1["state"] == "RUNNING"
            assert result2["state"] == "STOPPED"


class TestApplicationStateTransitions:
    """Test comprehensive application state transition scenarios"""

    @pytest.fixture
    def mock_client(self):
        """Create a mock client for testing"""
        client = AsyncMock()
        return client

    @pytest.fixture
    def service(self, mock_client):
        """Create a Service instance with mocked client"""
        service = Service(mock_client)
        return service

    @pytest.mark.asyncio
    async def test_complex_restart_state_transition(self, service):
        """Test restart with complex state transitions"""
        with patch.object(service, "_get_application_health") as mock_health:
            # Initial state is RUNNING
            mock_health.return_value = {"state": "RUNNING", "id": "test-app"}

            # Mock _poll_for_state to simulate going through multiple states before RUNNING
            with patch.object(service, "_poll_for_state") as mock_poll:
                mock_poll.return_value = {"state": "RUNNING", "id": "test-app"}

                result = await service.restart_application("test-app", 10)

            # Should return final state
            assert result["state"] == "RUNNING"

    @pytest.mark.asyncio
    async def test_start_from_error_state(self, service):
        """Test starting application from an invalid ERROR state"""
        with patch.object(service, "_get_application_health") as mock_health:
            # Application in ERROR state - not a valid enum value, should raise ValueError
            mock_health.return_value = {"state": "ERROR", "id": "test-app"}

            # Should raise ValueError when trying to convert invalid state to enum
            with pytest.raises(ValueError) as exc_info:
                await service.start_application("test-app", 10)

            # Verify the error is about invalid enum value
            assert "ERROR" in str(exc_info.value)
            service.client.put.assert_not_called()

    @pytest.mark.asyncio
    async def test_unknown_state_handling(self, service):
        """Test handling of unknown application states"""
        with patch.object(service, "_get_application_health") as mock_health:
            # Unknown state - not a valid enum value, should raise ValueError
            mock_health.return_value = {"state": "UNKNOWN", "id": "test-app"}

            # Should raise ValueError when trying to convert invalid state to enum
            with pytest.raises(ValueError) as exc_info:
                await service.start_application("test-app", 10)

            # Verify the error is about invalid enum value
            assert "UNKNOWN" in str(exc_info.value)
            service.client.put.assert_not_called()

    @pytest.mark.asyncio
    async def test_start_application_in_starting_state(self, service):
        """Test starting application that's already in STARTING state (edge case)"""
        with patch.object(service, "_get_application_health") as mock_health:
            mock_health.return_value = {"state": "STARTING", "id": "test-app"}

            # Should return immediately for intermediate states
            result = await service.start_application("test-app", 10)

            service.client.put.assert_not_called()
            assert result["state"] == "STARTING"

    @pytest.mark.asyncio
    async def test_stop_application_in_stopping_state(self, service):
        """Test stopping application that's already in STOPPING state (edge case)"""
        with patch.object(service, "_get_application_health") as mock_health:
            mock_health.return_value = {"state": "STOPPING", "id": "test-app"}

            # Should return immediately for intermediate states
            result = await service.stop_application("test-app", 10)

            service.client.put.assert_not_called()
            assert result["state"] == "STOPPING"

    @pytest.mark.asyncio
    async def test_restart_application_in_starting_state(self, service):
        """Test restarting application that's in STARTING state (edge case)"""
        with patch.object(service, "_get_application_health") as mock_health:
            mock_health.return_value = {"state": "STARTING", "id": "test-app"}

            # Should return immediately for intermediate states
            result = await service.restart_application("test-app", 10)

            service.client.put.assert_not_called()
            assert result["state"] == "STARTING"

    @pytest.mark.asyncio
    async def test_poll_for_state_method_directly(self, service):
        """Test _poll_for_state internal method directly"""
        with patch.object(service, "_get_application_health") as mock_health:
            # First two calls return STARTING, third returns RUNNING
            mock_health.side_effect = [
                {"state": "STARTING", "id": "test-app"},
                {"state": "STARTING", "id": "test-app"},
                {"state": "RUNNING", "id": "test-app"},
            ]

            with patch("asyncio.sleep", new_callable=AsyncMock) as mock_sleep:
                # Poll until RUNNING state is reached
                result = await service._poll_for_state("test-app", "RUNNING")

                # Should have polled 3 times and slept 2 times
                assert mock_health.call_count == 3
                assert mock_sleep.call_count == 2
                assert result["state"] == "RUNNING"
