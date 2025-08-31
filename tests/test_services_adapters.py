# Copyright (c) 2025 Itential, Inc
# GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)

import pytest
import asyncio
from unittest.mock import AsyncMock, MagicMock, patch

from itential_mcp import exceptions
from itential_mcp.models.adapters import (
    StartAdapterResponse,
    StopAdapterResponse,
    RestartAdapterResponse
)
from itential_mcp.services.adapters import Service


class TestAdaptersService:
    """Test cases for the adapters Service class"""

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
        assert service.name == "adapters"

    @pytest.mark.asyncio
    async def test_get_adapter_health_success(self, service, mock_client):
        """Test successful adapter health retrieval"""
        # Mock response data
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "total": 1,
            "results": [
                {
                    "id": "test-adapter",
                    "state": "RUNNING",
                    "version": "1.0.0"
                }
            ]
        }
        mock_client.get.return_value = mock_response

        result = await service._get_adapter_health("test-adapter")

        # Verify client was called with correct parameters
        mock_client.get.assert_called_once_with(
            "/health/adapters",
            params={
                "equals": "test-adapter",
                "equalsField": "id"
            }
        )

        # Verify result
        assert result["total"] == 1
        assert result["results"][0]["id"] == "test-adapter"
        assert result["results"][0]["state"] == "RUNNING"

    @pytest.mark.asyncio
    async def test_get_adapter_health_not_found(self, service, mock_client):
        """Test adapter not found scenario"""
        # Mock response with no results
        mock_response = MagicMock()
        mock_response.json.return_value = {"total": 0, "results": []}
        mock_client.get.return_value = mock_response

        with pytest.raises(exceptions.NotFoundError) as exc_info:
            await service._get_adapter_health("nonexistent-adapter")

        assert "unable to find adapter nonexistent-adapter" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_get_adapter_health_multiple_results(self, service, mock_client):
        """Test scenario where multiple adapters are found (should not happen)"""
        # Mock response with multiple results
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "total": 2,
            "results": [
                {"id": "adapter1", "state": "RUNNING"},
                {"id": "adapter2", "state": "STOPPED"}
            ]
        }
        mock_client.get.return_value = mock_response

        with pytest.raises(exceptions.NotFoundError):
            await service._get_adapter_health("duplicate-adapter")


class TestStartAdapter:
    """Test cases for the start_adapter method"""

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
    async def test_start_adapter_already_running(self, service):
        """Test starting an adapter that's already running"""
        with patch.object(service, '_get_adapter_health') as mock_health:
            mock_health.return_value = {
                "results": [{"state": "RUNNING"}]
            }

            result = await service.start_adapter("test-adapter", 10)

            # Should return immediately without calling PUT
            service.client.put.assert_not_called()
            assert isinstance(result, StartAdapterResponse)
            assert result.name == "test-adapter"
            assert result.state == "RUNNING"

    @pytest.mark.asyncio
    async def test_start_adapter_from_stopped_success(self, service):
        """Test successfully starting a stopped adapter"""
        with patch.object(service, '_get_adapter_health') as mock_health:
            # First call returns STOPPED, second returns RUNNING
            mock_health.side_effect = [
                {"results": [{"state": "STOPPED"}]},
                {"results": [{"state": "RUNNING"}]}
            ]

            with patch('asyncio.sleep', new_callable=AsyncMock):
                result = await service.start_adapter("test-adapter", 10)

            # Should call PUT to start adapter
            service.client.put.assert_called_once_with("/adapters/test-adapter/start")

            # Should check health twice (initial + after start)
            assert mock_health.call_count == 2

            assert isinstance(result, StartAdapterResponse)
            assert result.name == "test-adapter"
            assert result.state == "RUNNING"

    @pytest.mark.asyncio
    async def test_start_adapter_timeout(self, service):
        """Test adapter start timeout scenario"""
        with patch.object(service, '_get_adapter_health') as mock_health:
            # Always return STOPPED (never transitions to RUNNING)
            mock_health.side_effect = [
                {"results": [{"state": "STOPPED"}]},  # Initial state
                {"results": [{"state": "STOPPED"}]},  # After start attempt
                {"results": [{"state": "STOPPED"}]},  # Still stopped...
            ]

            with patch('asyncio.sleep', new_callable=AsyncMock) as mock_sleep:
                with pytest.raises(exceptions.TimeoutExceededError):
                    await service.start_adapter("test-adapter", 2)

                # Should have slept timeout number of times
                assert mock_sleep.call_count == 2

    @pytest.mark.asyncio
    async def test_start_adapter_dead_state(self, service):
        """Test starting an adapter in DEAD state"""
        with patch.object(service, '_get_adapter_health') as mock_health:
            mock_health.return_value = {
                "results": [{"state": "DEAD"}]
            }

            with pytest.raises(exceptions.InvalidStateError) as exc_info:
                await service.start_adapter("test-adapter", 10)

            assert "adapter `test-adapter` is `DEAD`" in str(exc_info.value)
            service.client.put.assert_not_called()

    @pytest.mark.asyncio
    async def test_start_adapter_deleted_state(self, service):
        """Test starting an adapter in DELETED state"""
        with patch.object(service, '_get_adapter_health') as mock_health:
            mock_health.return_value = {
                "results": [{"state": "DELETED"}]
            }

            with pytest.raises(exceptions.InvalidStateError) as exc_info:
                await service.start_adapter("test-adapter", 10)

            assert "adapter `test-adapter` is `DELETED`" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_start_adapter_state_transition_during_wait(self, service):
        """Test adapter transitioning to RUNNING during wait period"""
        with patch.object(service, '_get_adapter_health') as mock_health:
            # Simulate state transition: STOPPED -> STOPPED -> RUNNING
            mock_health.side_effect = [
                {"results": [{"state": "STOPPED"}]},  # Initial
                {"results": [{"state": "STOPPED"}]},  # First check
                {"results": [{"state": "RUNNING"}]}   # Second check - success!
            ]

            with patch('asyncio.sleep', new_callable=AsyncMock) as mock_sleep:
                result = await service.start_adapter("test-adapter", 10)

            # Should have slept once before successful state check
            assert mock_sleep.call_count == 1
            assert result.state == "RUNNING"


class TestStopAdapter:
    """Test cases for the stop_adapter method"""

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
    async def test_stop_adapter_already_stopped(self, service):
        """Test stopping an adapter that's already stopped"""
        with patch.object(service, '_get_adapter_health') as mock_health:
            mock_health.return_value = {
                "results": [{"state": "STOPPED"}]
            }

            result = await service.stop_adapter("test-adapter", 10)

            # Should return immediately without calling PUT
            service.client.put.assert_not_called()
            assert isinstance(result, StopAdapterResponse)
            assert result.name == "test-adapter"
            assert result.state == "STOPPED"

    @pytest.mark.asyncio
    async def test_stop_adapter_from_running_success(self, service):
        """Test successfully stopping a running adapter"""
        with patch.object(service, '_get_adapter_health') as mock_health:
            # First call returns RUNNING, second returns STOPPED
            mock_health.side_effect = [
                {"results": [{"state": "RUNNING"}]},
                {"results": [{"state": "STOPPED"}]}
            ]

            with patch('asyncio.sleep', new_callable=AsyncMock):
                result = await service.stop_adapter("test-adapter", 10)

            # Should call PUT to stop adapter
            service.client.put.assert_called_once_with("/adapters/test-adapter/stop")

            assert isinstance(result, StopAdapterResponse)
            assert result.name == "test-adapter"
            assert result.state == "STOPPED"

    @pytest.mark.asyncio
    async def test_stop_adapter_timeout(self, service):
        """Test adapter stop timeout scenario"""
        with patch.object(service, '_get_adapter_health') as mock_health:
            # Always return RUNNING (never transitions to STOPPED)
            mock_health.side_effect = [
                {"results": [{"state": "RUNNING"}]},  # Initial state
                {"results": [{"state": "RUNNING"}]},  # After stop attempt
                {"results": [{"state": "RUNNING"}]},  # Still running...
            ]

            with patch('asyncio.sleep', new_callable=AsyncMock) as mock_sleep:
                with pytest.raises(exceptions.TimeoutExceededError):
                    await service.stop_adapter("test-adapter", 2)

                assert mock_sleep.call_count == 2

    @pytest.mark.asyncio
    async def test_stop_adapter_dead_state(self, service):
        """Test stopping an adapter in DEAD state"""
        with patch.object(service, '_get_adapter_health') as mock_health:
            mock_health.return_value = {
                "results": [{"state": "DEAD"}]
            }

            with pytest.raises(exceptions.InvalidStateError) as exc_info:
                await service.stop_adapter("test-adapter", 10)

            assert "adapter `test-adapter` is `DEAD`" in str(exc_info.value)
            service.client.put.assert_not_called()

    @pytest.mark.asyncio
    async def test_stop_adapter_deleted_state(self, service):
        """Test stopping an adapter in DELETED state"""
        with patch.object(service, '_get_adapter_health') as mock_health:
            mock_health.return_value = {
                "results": [{"state": "DELETED"}]
            }

            with pytest.raises(exceptions.InvalidStateError) as exc_info:
                await service.stop_adapter("test-adapter", 10)

            assert "adapter `test-adapter` is `DELETED`" in str(exc_info.value)


class TestRestartAdapter:
    """Test cases for the restart_adapter method"""

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
    async def test_restart_adapter_from_running_success(self, service):
        """Test successfully restarting a running adapter"""
        with patch.object(service, '_get_adapter_health') as mock_health:
            # First call returns RUNNING, second returns RUNNING after restart
            mock_health.side_effect = [
                {"results": [{"state": "RUNNING"}]},
                {"results": [{"state": "RUNNING"}]}
            ]

            with patch('asyncio.sleep', new_callable=AsyncMock):
                result = await service.restart_adapter("test-adapter", 10)

            # Should call PUT to restart adapter
            service.client.put.assert_called_once_with("/adapters/test-adapter/restart")

            assert isinstance(result, RestartAdapterResponse)
            assert result.name == "test-adapter"
            assert result.state == "RUNNING"

    @pytest.mark.asyncio
    async def test_restart_adapter_timeout(self, service):
        """Test adapter restart timeout scenario"""
        with patch.object(service, '_get_adapter_health') as mock_health:
            # First call RUNNING, then adapter gets stuck in some other state
            mock_health.side_effect = [
                {"results": [{"state": "RUNNING"}]},   # Initial state
                {"results": [{"state": "STOPPED"}]},   # After restart - stuck
                {"results": [{"state": "STOPPED"}]},   # Still stopped...
            ]

            with patch('asyncio.sleep', new_callable=AsyncMock) as mock_sleep:
                with pytest.raises(exceptions.TimeoutExceededError):
                    await service.restart_adapter("test-adapter", 2)

                assert mock_sleep.call_count == 2

    @pytest.mark.asyncio
    async def test_restart_adapter_dead_state(self, service):
        """Test restarting an adapter in DEAD state"""
        with patch.object(service, '_get_adapter_health') as mock_health:
            mock_health.return_value = {
                "results": [{"state": "DEAD"}]
            }

            with pytest.raises(exceptions.InvalidStateError) as exc_info:
                await service.restart_adapter("test-adapter", 10)

            assert "adapter `test-adapter` is `DEAD`" in str(exc_info.value)
            service.client.put.assert_not_called()

    @pytest.mark.asyncio
    async def test_restart_adapter_deleted_state(self, service):
        """Test restarting an adapter in DELETED state"""
        with patch.object(service, '_get_adapter_health') as mock_health:
            mock_health.return_value = {
                "results": [{"state": "DELETED"}]
            }

            with pytest.raises(exceptions.InvalidStateError) as exc_info:
                await service.restart_adapter("test-adapter", 10)

            assert "adapter `test-adapter` is `DELETED`" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_restart_adapter_stopped_state(self, service):
        """Test restarting an adapter in STOPPED state"""
        with patch.object(service, '_get_adapter_health') as mock_health:
            mock_health.return_value = {
                "results": [{"state": "STOPPED"}]
            }

            with pytest.raises(exceptions.InvalidStateError) as exc_info:
                await service.restart_adapter("test-adapter", 10)

            assert "adapter `test-adapter` is `STOPPED`" in str(exc_info.value)
            service.client.put.assert_not_called()

    @pytest.mark.asyncio
    async def test_restart_adapter_state_transition_during_wait(self, service):
        """Test adapter transitioning back to RUNNING during restart wait"""
        with patch.object(service, '_get_adapter_health') as mock_health:
            # Simulate restart process: RUNNING -> STOPPED -> RUNNING
            mock_health.side_effect = [
                {"results": [{"state": "RUNNING"}]},  # Initial
                {"results": [{"state": "STOPPED"}]},  # During restart
                {"results": [{"state": "RUNNING"}]}   # Back to running
            ]

            with patch('asyncio.sleep', new_callable=AsyncMock) as mock_sleep:
                result = await service.restart_adapter("test-adapter", 10)

            # Should have slept once during the restart process
            assert mock_sleep.call_count == 1
            assert result.state == "RUNNING"


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
        from itential_mcp.services import ServiceBase
        assert isinstance(service, ServiceBase)

    @pytest.mark.asyncio
    async def test_method_signatures_consistency(self, service):
        """Test that all methods have consistent parameter signatures"""
        import inspect

        # Check start_adapter signature
        start_sig = inspect.signature(service.start_adapter)
        assert 'name' in start_sig.parameters
        assert 'timeout' in start_sig.parameters

        # Check stop_adapter signature
        stop_sig = inspect.signature(service.stop_adapter)
        assert 'name' in stop_sig.parameters
        assert 'timeout' in stop_sig.parameters

        # Check restart_adapter signature
        restart_sig = inspect.signature(service.restart_adapter)
        assert 'name' in restart_sig.parameters
        assert 'timeout' in restart_sig.parameters

    @pytest.mark.asyncio
    async def test_all_methods_are_async(self, service):
        """Test that all public methods are async"""
        import inspect

        # Get all public methods (not starting with _)
        public_methods = [
            method for method in dir(service)
            if not method.startswith('_') and callable(getattr(service, method))
        ]

        for method_name in ['start_adapter', 'stop_adapter', 'restart_adapter']:
            if method_name in public_methods:
                method = getattr(service, method_name)
                assert inspect.iscoroutinefunction(method)

    @pytest.mark.asyncio
    async def test_adapter_not_found_propagation(self, service):
        """Test that NotFoundError from _get_adapter_health propagates correctly"""
        with patch.object(service, '_get_adapter_health') as mock_health:
            mock_health.side_effect = exceptions.NotFoundError("Adapter not found")

            with pytest.raises(exceptions.NotFoundError):
                await service.start_adapter("nonexistent", 10)

            with pytest.raises(exceptions.NotFoundError):
                await service.stop_adapter("nonexistent", 10)

            with pytest.raises(exceptions.NotFoundError):
                await service.restart_adapter("nonexistent", 10)


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
            await service._get_adapter_health("test-adapter")

    @pytest.mark.asyncio
    async def test_malformed_response_handling(self, service, mock_client):
        """Test handling of malformed API responses"""
        # Mock response with missing 'total' field
        mock_response = MagicMock()
        mock_response.json.return_value = {"results": []}
        mock_client.get.return_value = mock_response

        with pytest.raises(KeyError):
            await service._get_adapter_health("test-adapter")

    @pytest.mark.asyncio
    async def test_missing_results_field(self, service, mock_client):
        """Test handling of response missing results field"""
        mock_response = MagicMock()
        mock_response.json.return_value = {"total": 1}  # Missing results
        mock_client.get.return_value = mock_response

        # The _get_adapter_health will succeed, but start_adapter will fail
        # when trying to access data["results"][0]["state"]
        with pytest.raises(KeyError):
            await service.start_adapter("test-adapter", 10)

    @pytest.mark.asyncio
    async def test_empty_results_array(self, service, mock_client):
        """Test handling of empty results array"""
        mock_response = MagicMock()
        mock_response.json.return_value = {"total": 0, "results": []}
        mock_client.get.return_value = mock_response

        # Should raise NotFoundError because total != 1
        with pytest.raises(exceptions.NotFoundError):
            await service._get_adapter_health("test-adapter")

    @pytest.mark.asyncio
    async def test_zero_timeout_handling(self, service):
        """Test handling of zero timeout values"""
        with patch.object(service, '_get_adapter_health') as mock_health:
            mock_health.return_value = {"results": [{"state": "STOPPED"}]}

            # Zero timeout should immediately raise TimeoutExceededError
            with pytest.raises(exceptions.TimeoutExceededError):
                await service.start_adapter("test-adapter", 0)


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
    async def test_large_timeout_values(self, service):
        """Test handling of very large timeout values"""
        with patch.object(service, '_get_adapter_health') as mock_health:
            mock_health.return_value = {"results": [{"state": "RUNNING"}]}

            # Should handle large timeout without issues
            result = await service.start_adapter("test-adapter", 999999)
            assert result.state == "RUNNING"

    @pytest.mark.asyncio
    async def test_adapter_name_with_special_characters(self, service, mock_client):
        """Test adapter names with special characters"""
        special_name = "test-adapter_123.456@domain"

        mock_response = MagicMock()
        mock_response.json.return_value = {
            "total": 1,
            "results": [{"state": "RUNNING"}]
        }
        mock_client.get.return_value = mock_response

        await service._get_adapter_health(special_name)

        # Verify the special name was used correctly in the API call
        mock_client.get.assert_called_with(
            "/health/adapters",
            params={
                "equals": special_name,
                "equalsField": "id"
            }
        )

    @pytest.mark.asyncio
    async def test_empty_adapter_name(self, service):
        """Test handling of empty adapter name"""
        with patch.object(service, '_get_adapter_health') as mock_health:
            mock_health.return_value = {"results": [{"state": "RUNNING"}]}

            # Should handle empty name (though it may not be realistic)
            result = await service.start_adapter("", 10)
            assert result.name == ""

    @pytest.mark.asyncio
    async def test_unicode_adapter_name(self, service, mock_client):
        """Test adapter names with Unicode characters"""
        unicode_name = "测试适配器"

        mock_response = MagicMock()
        mock_response.json.return_value = {
            "total": 1,
            "results": [{"state": "RUNNING"}]
        }
        mock_client.get.return_value = mock_response

        await service._get_adapter_health(unicode_name)

        # Verify Unicode name was handled correctly
        mock_client.get.assert_called_with(
            "/health/adapters",
            params={
                "equals": unicode_name,
                "equalsField": "id"
            }
        )

    @pytest.mark.asyncio
    async def test_concurrent_operations(self, service):
        """Test concurrent adapter operations"""
        with patch.object(service, '_get_adapter_health') as mock_health:
            # Create a side_effect function that returns different states based on adapter name
            def mock_health_response(adapter_name):
                if adapter_name == "adapter1":
                    return {"results": [{"state": "RUNNING"}]}  # start_adapter - already running
                elif adapter_name == "adapter2":
                    return {"results": [{"state": "STOPPED"}]}  # stop_adapter - already stopped
                elif adapter_name == "adapter3":
                    return {"results": [{"state": "RUNNING"}]}  # restart_adapter - running
                else:
                    return {"results": [{"state": "RUNNING"}]}  # default
            
            mock_health.side_effect = mock_health_response

            # Run multiple operations concurrently
            tasks = [
                service.start_adapter("adapter1", 10),
                service.stop_adapter("adapter2", 10),
                service.restart_adapter("adapter3", 10)
            ]

            results = await asyncio.gather(*tasks, return_exceptions=True)

            # All should complete successfully with proper model responses
            assert len(results) == 3
            for result in results:
                assert not isinstance(result, Exception)
                assert hasattr(result, 'name')
                assert hasattr(result, 'state')

    @pytest.mark.asyncio
    async def test_state_case_sensitivity(self, service):
        """Test that adapter states are case sensitive"""
        with patch.object(service, '_get_adapter_health') as mock_health:
            # Use lowercase state (should not be recognized as valid)
            mock_health.return_value = {"results": [{"state": "running"}]}

            # The service should fail validation with lowercase state
            with pytest.raises(Exception):  # ValidationError will be raised by pydantic
                await service.start_adapter("test-adapter", 10)


class TestModelResponses:
    """Test that the service returns proper model instances"""

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
    async def test_start_adapter_returns_correct_model(self, service):
        """Test that start_adapter returns StartAdapterResponse model"""
        with patch.object(service, '_get_adapter_health') as mock_health:
            mock_health.return_value = {"results": [{"state": "RUNNING"}]}

            result = await service.start_adapter("test-adapter", 10)

            assert isinstance(result, StartAdapterResponse)
            assert hasattr(result, 'name')
            assert hasattr(result, 'state')

    @pytest.mark.asyncio
    async def test_stop_adapter_returns_correct_model(self, service):
        """Test that stop_adapter returns StopAdapterResponse model"""
        with patch.object(service, '_get_adapter_health') as mock_health:
            mock_health.return_value = {"results": [{"state": "STOPPED"}]}

            result = await service.stop_adapter("test-adapter", 10)

            assert isinstance(result, StopAdapterResponse)
            assert hasattr(result, 'name')
            assert hasattr(result, 'state')

    @pytest.mark.asyncio
    async def test_restart_adapter_returns_correct_model(self, service):
        """Test that restart_adapter returns RestartAdapterResponse model"""
        with patch.object(service, '_get_adapter_health') as mock_health:
            mock_health.return_value = {"results": [{"state": "RUNNING"}]}

            result = await service.restart_adapter("test-adapter", 10)

            assert isinstance(result, RestartAdapterResponse)
            assert hasattr(result, 'name')
            assert hasattr(result, 'state')

    @pytest.mark.asyncio
    async def test_model_response_data_integrity(self, service):
        """Test that model responses contain correct data"""
        adapter_name = "integration-test-adapter"

        with patch.object(service, '_get_adapter_health') as mock_health:
            # Mock different scenarios for each method call
            
            # Test start_adapter - adapter already running
            mock_health.return_value = {"results": [{"state": "RUNNING"}]}
            start_result = await service.start_adapter(adapter_name, 10)
            assert start_result.name == adapter_name
            assert start_result.state == "RUNNING"
            
            # Test stop_adapter - adapter already stopped
            mock_health.return_value = {"results": [{"state": "STOPPED"}]}
            stop_result = await service.stop_adapter(adapter_name, 10)
            assert stop_result.name == adapter_name
            assert stop_result.state == "STOPPED"
            
            # Test restart_adapter - adapter running
            mock_health.return_value = {"results": [{"state": "RUNNING"}]}
            restart_result = await service.restart_adapter(adapter_name, 10)
            assert restart_result.name == adapter_name
            assert restart_result.state == "RUNNING"
