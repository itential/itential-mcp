# Copyright (c) 2025 Itential, Inc
# GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

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
                    "results": [
                        {
                            "id": "test-application",
                            "state": "RUNNING",
                            "version": "1.0.0",
                        }
                    ]
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
        assert result["results"][0]["id"] == "test-application"
        assert result["results"][0]["state"] == "RUNNING"

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
            mock_health.return_value = {"results": [{"state": "RUNNING"}]}

            result = await service.start_application("test-application", 10)

            # Should return immediately without calling PUT
            service.client.put.assert_not_called()
            # Should return the health data
            assert result["results"][0]["state"] == "RUNNING"

    @pytest.mark.asyncio
    async def test_start_application_from_stopped_success(self, service):
        """Test successfully starting a stopped application"""
        with patch.object(service, "_get_application_health") as mock_health:
            # First call returns STOPPED, second returns RUNNING
            mock_health.side_effect = [
                {"results": [{"state": "STOPPED"}]},
                {"results": [{"state": "RUNNING"}]},
            ]

            with patch("asyncio.sleep", new_callable=AsyncMock):
                result = await service.start_application("test-application", 10)

            # Should call PUT to start application
            service.client.put.assert_called_once_with(
                "/applications/test-application/start"
            )

            # Should check health twice (initial + after start)
            assert mock_health.call_count == 2

            # Should return the final health data
            assert result["results"][0]["state"] == "RUNNING"

    @pytest.mark.asyncio
    async def test_start_application_timeout(self, service):
        """Test application start timeout scenario"""
        with patch.object(service, "_get_application_health") as mock_health:
            # Always return STOPPED (never transitions to RUNNING)
            mock_health.side_effect = [
                {"results": [{"state": "STOPPED"}]},  # Initial state
                {"results": [{"state": "STOPPED"}]},  # After start attempt
                {"results": [{"state": "STOPPED"}]},  # Still stopped...
            ]

            with patch("asyncio.sleep", new_callable=AsyncMock) as mock_sleep:
                with pytest.raises(exceptions.TimeoutExceededError):
                    await service.start_application("test-application", 2)

                # Should have slept timeout number of times
                assert mock_sleep.call_count == 2

    @pytest.mark.asyncio
    async def test_start_application_dead_state(self, service):
        """Test starting an application in DEAD state"""
        with patch.object(service, "_get_application_health") as mock_health:
            mock_health.return_value = {"results": [{"state": "DEAD"}]}

            with pytest.raises(exceptions.InvalidStateError) as exc_info:
                await service.start_application("test-application", 10)

            assert "application `test-application` is `DEAD`" in str(exc_info.value)
            service.client.put.assert_not_called()

    @pytest.mark.asyncio
    async def test_start_application_deleted_state(self, service):
        """Test starting an application in DELETED state"""
        with patch.object(service, "_get_application_health") as mock_health:
            mock_health.return_value = {"results": [{"state": "DELETED"}]}

            with pytest.raises(exceptions.InvalidStateError) as exc_info:
                await service.start_application("test-application", 10)

            assert "application `test-application` is `DELETED`" in str(exc_info.value)


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
            mock_health.return_value = {"results": [{"state": "STOPPED"}]}

            result = await service.stop_application("test-application", 10)

            # Should return immediately without calling PUT
            service.client.put.assert_not_called()
            # Should return the health data
            assert result["results"][0]["state"] == "STOPPED"

    @pytest.mark.asyncio
    async def test_stop_application_from_running_success(self, service):
        """Test successfully stopping a running application"""
        with patch.object(service, "_get_application_health") as mock_health:
            # First call returns RUNNING, second returns STOPPED
            mock_health.side_effect = [
                {"results": [{"state": "RUNNING"}]},
                {"results": [{"state": "STOPPED"}]},
            ]

            with patch("asyncio.sleep", new_callable=AsyncMock):
                result = await service.stop_application("test-application", 10)

            # Should call PUT to stop application
            service.client.put.assert_called_once_with(
                "/applications/test-application/stop"
            )

            # Should return the final health data
            assert result["results"][0]["state"] == "STOPPED"

    @pytest.mark.asyncio
    async def test_stop_application_timeout(self, service):
        """Test application stop timeout scenario"""
        with patch.object(service, "_get_application_health") as mock_health:
            # Always return RUNNING (never transitions to STOPPED)
            mock_health.side_effect = [
                {"results": [{"state": "RUNNING"}]},  # Initial state
                {"results": [{"state": "RUNNING"}]},  # After stop attempt
                {"results": [{"state": "RUNNING"}]},  # Still running...
            ]

            with patch("asyncio.sleep", new_callable=AsyncMock) as mock_sleep:
                with pytest.raises(exceptions.TimeoutExceededError):
                    await service.stop_application("test-application", 2)

                # Should have slept timeout number of times
                assert mock_sleep.call_count == 2

    @pytest.mark.asyncio
    async def test_stop_application_dead_state(self, service):
        """Test stopping an application in DEAD state"""
        with patch.object(service, "_get_application_health") as mock_health:
            mock_health.return_value = {"results": [{"state": "DEAD"}]}

            with pytest.raises(exceptions.InvalidStateError) as exc_info:
                await service.stop_application("test-application", 10)

            assert "application `test-application` is `DEAD`" in str(exc_info.value)
            service.client.put.assert_not_called()

    @pytest.mark.asyncio
    async def test_stop_application_deleted_state(self, service):
        """Test stopping an application in DELETED state"""
        with patch.object(service, "_get_application_health") as mock_health:
            mock_health.return_value = {"results": [{"state": "DELETED"}]}

            with pytest.raises(exceptions.InvalidStateError) as exc_info:
                await service.stop_application("test-application", 10)

            assert "application `test-application` is `DELETED`" in str(exc_info.value)
            service.client.put.assert_not_called()

    @pytest.mark.asyncio
    async def test_stop_application_multiple_pages(self, service):
        """Test stopping application with pagination during wait loop"""
        with patch.object(service, "_get_application_health") as mock_health:
            # First call returns RUNNING, then STOPPED after several checks
            mock_health.side_effect = [
                {"results": [{"state": "RUNNING"}]},  # Initial check
                {"results": [{"state": "RUNNING"}]},  # First wait check
                {"results": [{"state": "RUNNING"}]},  # Second wait check
                {"results": [{"state": "STOPPED"}]},  # Finally stopped
            ]

            with patch("asyncio.sleep", new_callable=AsyncMock):
                result = await service.stop_application("test-application", 10)

            # Should call PUT to stop application
            service.client.put.assert_called_once_with(
                "/applications/test-application/stop"
            )

            # Should check health multiple times
            assert mock_health.call_count == 4
            assert result["results"][0]["state"] == "STOPPED"


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
            # First call returns RUNNING, second returns RUNNING after restart
            mock_health.side_effect = [
                {"results": [{"state": "RUNNING"}]},
                {"results": [{"state": "RUNNING"}]},
            ]

            with patch("asyncio.sleep", new_callable=AsyncMock):
                result = await service.restart_application("test-application", 10)

            # Should call PUT to restart application
            service.client.put.assert_called_once_with(
                "/applications/test-application/restart"
            )

            # Should return the final health data
            assert result["results"][0]["state"] == "RUNNING"

    @pytest.mark.asyncio
    async def test_restart_application_stopped_state(self, service):
        """Test restarting an application in STOPPED state"""
        with patch.object(service, "_get_application_health") as mock_health:
            mock_health.return_value = {"results": [{"state": "STOPPED"}]}

            with pytest.raises(exceptions.InvalidStateError) as exc_info:
                await service.restart_application("test-application", 10)

            assert "application `test-application` is `STOPPED`" in str(exc_info.value)
            service.client.put.assert_not_called()

    @pytest.mark.asyncio
    async def test_restart_application_dead_state(self, service):
        """Test restarting an application in DEAD state"""
        with patch.object(service, "_get_application_health") as mock_health:
            mock_health.return_value = {"results": [{"state": "DEAD"}]}

            with pytest.raises(exceptions.InvalidStateError) as exc_info:
                await service.restart_application("test-application", 10)

            assert "application `test-application` is `DEAD`" in str(exc_info.value)
            service.client.put.assert_not_called()

    @pytest.mark.asyncio
    async def test_restart_application_deleted_state(self, service):
        """Test restarting an application in DELETED state"""
        with patch.object(service, "_get_application_health") as mock_health:
            mock_health.return_value = {"results": [{"state": "DELETED"}]}

            with pytest.raises(exceptions.InvalidStateError) as exc_info:
                await service.restart_application("test-application", 10)

            assert "application `test-application` is `DELETED`" in str(exc_info.value)
            service.client.put.assert_not_called()

    @pytest.mark.asyncio
    async def test_restart_application_timeout(self, service):
        """Test application restart timeout scenario"""
        with patch.object(service, "_get_application_health") as mock_health:
            # Always return RUNNING at first, then stays in intermediate state
            mock_health.side_effect = [
                {"results": [{"state": "RUNNING"}]},  # Initial state
                {"results": [{"state": "RESTARTING"}]},  # After restart attempt
                {"results": [{"state": "RESTARTING"}]},  # Still restarting...
            ]

            with patch("asyncio.sleep", new_callable=AsyncMock) as mock_sleep:
                with pytest.raises(exceptions.TimeoutExceededError):
                    await service.restart_application("test-application", 2)

                # Should have slept timeout number of times
                assert mock_sleep.call_count == 2

    @pytest.mark.asyncio
    async def test_restart_application_multiple_state_changes(self, service):
        """Test restarting application through multiple state changes"""
        with patch.object(service, "_get_application_health") as mock_health:
            # Simulate application going through restart states
            mock_health.side_effect = [
                {"results": [{"state": "RUNNING"}]},  # Initial check
                {"results": [{"state": "RESTARTING"}]},  # First wait check
                {"results": [{"state": "STARTING"}]},  # Second wait check
                {"results": [{"state": "RUNNING"}]},  # Finally running
            ]

            with patch("asyncio.sleep", new_callable=AsyncMock):
                result = await service.restart_application("test-application", 10)

            # Should call PUT to restart application
            service.client.put.assert_called_once_with(
                "/applications/test-application/restart"
            )

            # Should check health multiple times
            assert mock_health.call_count == 4
            assert result["results"][0]["state"] == "RUNNING"

    @pytest.mark.asyncio
    async def test_restart_application_already_running_no_change_needed(self, service):
        """Test restarting application that immediately returns to RUNNING"""
        with patch.object(service, "_get_application_health") as mock_health:
            # Application is RUNNING before and after restart
            mock_health.side_effect = [
                {"results": [{"state": "RUNNING"}]},  # Initial check
                {
                    "results": [{"state": "RUNNING"}]
                },  # Immediately running after restart
            ]

            with patch("asyncio.sleep", new_callable=AsyncMock):
                result = await service.restart_application("test-application", 10)

            # Should still call PUT to restart
            service.client.put.assert_called_once_with(
                "/applications/test-application/restart"
            )

            # Should return running state
            assert result["results"][0]["state"] == "RUNNING"


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
            mock_health.return_value = {"results": [{"state": "STOPPED"}]}

            with pytest.raises(exceptions.TimeoutExceededError):
                await service.start_application("test-application", 0)

        # Should call PUT but timeout immediately since timeout=0
        service.client.put.assert_called_once_with(
            "/applications/test-application/start"
        )

    @pytest.mark.asyncio
    async def test_negative_timeout_behavior(self, service, mock_client):
        """Test behavior with negative timeout (demonstrates infinite loop issue)"""
        with patch.object(service, "_get_application_health") as mock_health:
            # Return STOPPED first, then RUNNING after first attempt
            mock_health.side_effect = [
                {"results": [{"state": "STOPPED"}]},
                {
                    "results": [{"state": "RUNNING"}]
                },  # Immediately running to break loop
            ]

            # Should complete successfully with negative timeout if app starts immediately
            result = await service.start_application("test-application", -1)

        # Should call PUT and succeed if application transitions to RUNNING immediately
        service.client.put.assert_called_once_with(
            "/applications/test-application/start"
        )
        assert result["results"][0]["state"] == "RUNNING"

    @pytest.mark.asyncio
    async def test_large_timeout_value(self, service, mock_client):
        """Test behavior with very large timeout value"""
        with patch.object(service, "_get_application_health") as mock_health:
            # Return STOPPED first, then RUNNING
            mock_health.side_effect = [
                {"results": [{"state": "STOPPED"}]},
                {"results": [{"state": "RUNNING"}]},
            ]

            with patch("asyncio.sleep", new_callable=AsyncMock):
                result = await service.start_application("test-application", 999999)

            # Should work normally with large timeout
            assert result["results"][0]["state"] == "RUNNING"

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
                {"results": [{"state": "RUNNING"}]},  # For first operation
                {"results": [{"state": "STOPPED"}]},  # For second operation
            ]

            # Run two operations concurrently (though they should be independent)
            task1 = service.start_application("app1", 10)
            task2 = service.stop_application("app2", 10)

            # Both should complete without interfering with each other
            result1, result2 = await asyncio.gather(task1, task2)

            # Verify results
            assert result1["results"][0]["state"] == "RUNNING"
            assert result2["results"][0]["state"] == "STOPPED"


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
            # Simulate realistic restart state progression
            mock_health.side_effect = [
                {"results": [{"state": "RUNNING"}]},  # Initial state
                {"results": [{"state": "STOPPING"}]},  # Stopping phase
                {"results": [{"state": "STOPPED"}]},  # Stopped phase
                {"results": [{"state": "STARTING"}]},  # Starting phase
                {"results": [{"state": "RUNNING"}]},  # Finally running
            ]

            with patch("asyncio.sleep", new_callable=AsyncMock) as mock_sleep:
                result = await service.restart_application("test-app", 10)

            # Should go through multiple state checks
            assert mock_health.call_count == 5
            assert (
                mock_sleep.call_count == 3
            )  # Sleep after non-RUNNING states (4 checks - 1 final = 3 sleeps)
            assert result["results"][0]["state"] == "RUNNING"

    @pytest.mark.asyncio
    async def test_start_from_error_state(self, service):
        """Test starting application from an ERROR state"""
        with patch.object(service, "_get_application_health") as mock_health:
            # Application in ERROR state initially - will not trigger PUT call
            mock_health.return_value = {"results": [{"state": "ERROR"}]}

            result = await service.start_application("test-app", 10)

            # Should not attempt to start from ERROR state (only STOPPED triggers PUT)
            service.client.put.assert_not_called()
            assert result["results"][0]["state"] == "ERROR"

    @pytest.mark.asyncio
    async def test_unknown_state_handling(self, service):
        """Test handling of unknown application states"""
        with patch.object(service, "_get_application_health") as mock_health:
            # Unknown state initially - will not trigger PUT call
            mock_health.return_value = {"results": [{"state": "UNKNOWN"}]}

            result = await service.start_application("test-app", 10)

            # Should not attempt to start from UNKNOWN state (only STOPPED triggers PUT)
            service.client.put.assert_not_called()
            assert result["results"][0]["state"] == "UNKNOWN"
