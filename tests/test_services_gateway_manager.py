# Copyright (c) 2025 Itential, Inc
# GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)

import pytest
from unittest.mock import AsyncMock, MagicMock

from itential_mcp.services.gateway_manager import Service


class TestGatewayManagerService:
    """Test cases for the gateway_manager Service class"""

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
        assert service.name == "gateway_manager"


class TestGetServices:
    """Test cases for the get_services method"""

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
    async def test_get_services_success(self, service, mock_client):
        """Test successful services retrieval"""
        expected_services = [
            {
                "name": "test-service-1",
                "cluster": "cluster-1",
                "type": "ansible-playbook",
                "description": "Test Ansible playbook service",
                "decorator": {"type": "object", "properties": {"param1": {"type": "string"}}}
            },
            {
                "name": "test-service-2",
                "cluster": "cluster-2",
                "type": "python-script",
                "description": "Test Python script service",
                "decorator": {"type": "object", "properties": {"param2": {"type": "integer"}}}
            }
        ]

        # Mock response data
        mock_response = MagicMock()
        mock_response.json.return_value = expected_services
        mock_client.get.return_value = mock_response

        result = await service.get_services()

        # Verify client was called with correct endpoint
        mock_client.get.assert_called_once_with("/gateway_manager/v1/services")

        # Verify result
        assert result == expected_services
        assert len(result) == 2
        assert result[0]["name"] == "test-service-1"
        assert result[1]["type"] == "python-script"

    @pytest.mark.asyncio
    async def test_get_services_empty_list(self, service, mock_client):
        """Test services retrieval with empty list"""
        # Mock response with empty list
        mock_response = MagicMock()
        mock_response.json.return_value = []
        mock_client.get.return_value = mock_response

        result = await service.get_services()

        assert result == []
        mock_client.get.assert_called_once_with("/gateway_manager/v1/services")

    @pytest.mark.asyncio
    async def test_get_services_client_error(self, service, mock_client):
        """Test services retrieval with client error"""
        mock_client.get.side_effect = Exception("API Error")

        with pytest.raises(Exception, match="API Error"):
            await service.get_services()

    @pytest.mark.asyncio
    async def test_get_services_json_error(self, service, mock_client):
        """Test services retrieval with JSON decode error"""
        mock_response = MagicMock()
        mock_response.json.side_effect = ValueError("Invalid JSON")
        mock_client.get.return_value = mock_response

        with pytest.raises(ValueError, match="Invalid JSON"):
            await service.get_services()


class TestGetGateways:
    """Test cases for the get_gateways method"""

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
    async def test_get_gateways_success(self, service, mock_client):
        """Test successful gateways retrieval"""
        expected_gateways = [
            {
                "name": "gateway-1",
                "cluster": "cluster-1",
                "description": "Primary gateway",
                "status": "connected",
                "enabled": True
            },
            {
                "name": "gateway-2",
                "cluster": "cluster-2",
                "description": "Secondary gateway",
                "status": "disconnected",
                "enabled": False
            }
        ]

        # Mock response data
        mock_response = MagicMock()
        mock_response.json.return_value = expected_gateways
        mock_client.get.return_value = mock_response

        result = await service.get_gateways()

        # Verify client was called with correct endpoint
        mock_client.get.assert_called_once_with("/gateway_manager/v1/gateways")

        # Verify result
        assert result == expected_gateways
        assert len(result) == 2
        assert result[0]["name"] == "gateway-1"
        assert result[0]["enabled"] is True
        assert result[1]["status"] == "disconnected"

    @pytest.mark.asyncio
    async def test_get_gateways_empty_list(self, service, mock_client):
        """Test gateways retrieval with empty list"""
        # Mock response with empty list
        mock_response = MagicMock()
        mock_response.json.return_value = []
        mock_client.get.return_value = mock_response

        result = await service.get_gateways()

        assert result == []
        mock_client.get.assert_called_once_with("/gateway_manager/v1/gateways")

    @pytest.mark.asyncio
    async def test_get_gateways_client_error(self, service, mock_client):
        """Test gateways retrieval with client error"""
        mock_client.get.side_effect = Exception("Connection failed")

        with pytest.raises(Exception, match="Connection failed"):
            await service.get_gateways()

    @pytest.mark.asyncio
    async def test_get_gateways_json_error(self, service, mock_client):
        """Test gateways retrieval with JSON decode error"""
        mock_response = MagicMock()
        mock_response.json.side_effect = ValueError("Invalid JSON")
        mock_client.get.return_value = mock_response

        with pytest.raises(ValueError, match="Invalid JSON"):
            await service.get_gateways()


class TestRunService:
    """Test cases for the run_service method"""

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
    async def test_run_service_success_without_params(self, service, mock_client):
        """Test successful service run without input parameters"""
        service_name = "test-service"
        cluster_name = "test-cluster"
        expected_result = {
            "stdout": "Service executed successfully",
            "stderr": "",
            "return_code": 0,
            "start_time": "2025-01-01T10:00:00Z",
            "end_time": "2025-01-01T10:05:00Z",
            "elapsed_time": 300
        }

        # Mock response data
        mock_response = MagicMock()
        mock_response.json.return_value = expected_result
        mock_client.post.return_value = mock_response

        result = await service.run_service(service_name, cluster_name)

        # Verify client was called with correct parameters
        expected_body = {
            "serviceName": service_name,
            "clusterId": cluster_name
        }
        mock_client.post.assert_called_once_with(
            "/gateway_manager/v1/services/run",
            json=expected_body
        )

        # Verify result
        assert result == expected_result
        assert result["return_code"] == 0

    @pytest.mark.asyncio
    async def test_run_service_success_with_params(self, service, mock_client):
        """Test successful service run with input parameters"""
        service_name = "test-service"
        cluster_name = "test-cluster"
        input_params = {"param1": "value1", "param2": 42}
        expected_result = {
            "stdout": "Service executed with params",
            "stderr": "",
            "return_code": 0,
            "start_time": "2025-01-01T10:00:00Z",
            "end_time": "2025-01-01T10:05:00Z",
            "elapsed_time": 300
        }

        # Mock response data
        mock_response = MagicMock()
        mock_response.json.return_value = expected_result
        mock_client.post.return_value = mock_response

        result = await service.run_service(service_name, cluster_name, input_params)

        # Verify client was called with correct parameters including input params
        expected_body = {
            "serviceName": service_name,
            "clusterId": cluster_name,
            "params": input_params
        }
        mock_client.post.assert_called_once_with(
            "/gateway_manager/v1/services/run",
            json=expected_body
        )

        # Verify result
        assert result == expected_result

    @pytest.mark.asyncio
    async def test_run_service_with_none_params(self, service, mock_client):
        """Test service run with explicitly None input parameters"""
        service_name = "test-service"
        cluster_name = "test-cluster"
        expected_result = {"return_code": 0}

        # Mock response data
        mock_response = MagicMock()
        mock_response.json.return_value = expected_result
        mock_client.post.return_value = mock_response

        await service.run_service(service_name, cluster_name, None)

        # Verify client was called without params in body
        expected_body = {
            "serviceName": service_name,
            "clusterId": cluster_name
        }
        mock_client.post.assert_called_once_with(
            "/gateway_manager/v1/services/run",
            json=expected_body
        )

    @pytest.mark.asyncio
    async def test_run_service_with_empty_dict_params(self, service, mock_client):
        """Test service run with empty dict input parameters"""
        service_name = "test-service"
        cluster_name = "test-cluster"
        input_params = {}
        expected_result = {"return_code": 0}

        # Mock response data
        mock_response = MagicMock()
        mock_response.json.return_value = expected_result
        mock_client.post.return_value = mock_response

        await service.run_service(service_name, cluster_name, input_params)

        # Verify client was called without params because empty dict is falsy
        expected_body = {
            "serviceName": service_name,
            "clusterId": cluster_name
        }
        mock_client.post.assert_called_once_with(
            "/gateway_manager/v1/services/run",
            json=expected_body
        )

    @pytest.mark.asyncio
    async def test_run_service_failure(self, service, mock_client):
        """Test service run failure with non-zero return code"""
        service_name = "failing-service"
        cluster_name = "test-cluster"
        expected_result = {
            "stdout": "",
            "stderr": "Service failed with error",
            "return_code": 1,
            "start_time": "2025-01-01T10:00:00Z",
            "end_time": "2025-01-01T10:01:00Z",
            "elapsed_time": 60
        }

        # Mock response data
        mock_response = MagicMock()
        mock_response.json.return_value = expected_result
        mock_client.post.return_value = mock_response

        result = await service.run_service(service_name, cluster_name)

        # Should still return the result even if service failed
        assert result == expected_result
        assert result["return_code"] == 1
        assert "error" in result["stderr"]

    @pytest.mark.asyncio
    async def test_run_service_client_error(self, service, mock_client):
        """Test service run with client error"""
        mock_client.post.side_effect = Exception("API Error")

        with pytest.raises(Exception, match="API Error"):
            await service.run_service("test-service", "test-cluster")

    @pytest.mark.asyncio
    async def test_run_service_json_error(self, service, mock_client):
        """Test service run with JSON decode error"""
        mock_response = MagicMock()
        mock_response.json.side_effect = ValueError("Invalid JSON")
        mock_client.post.return_value = mock_response

        with pytest.raises(ValueError, match="Invalid JSON"):
            await service.run_service("test-service", "test-cluster")

    @pytest.mark.asyncio
    async def test_run_service_with_complex_params(self, service, mock_client):
        """Test service run with complex nested input parameters"""
        service_name = "complex-service"
        cluster_name = "test-cluster"
        input_params = {
            "config": {
                "environment": "production",
                "settings": {
                    "timeout": 300,
                    "retries": 3
                }
            },
            "targets": ["device1", "device2"],
            "variables": {
                "var1": "value1",
                "var2": None,
                "var3": True
            }
        }
        expected_result = {"return_code": 0}

        # Mock response data
        mock_response = MagicMock()
        mock_response.json.return_value = expected_result
        mock_client.post.return_value = mock_response

        await service.run_service(service_name, cluster_name, input_params)

        # Verify client was called with complex params
        expected_body = {
            "serviceName": service_name,
            "clusterId": cluster_name,
            "params": input_params
        }
        mock_client.post.assert_called_once_with(
            "/gateway_manager/v1/services/run",
            json=expected_body
        )


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

        # Check get_services signature
        get_services_sig = inspect.signature(service.get_services)
        assert len(get_services_sig.parameters) == 0

        # Check get_gateways signature
        get_gateways_sig = inspect.signature(service.get_gateways)
        assert len(get_gateways_sig.parameters) == 0

        # Check run_service signature
        run_service_sig = inspect.signature(service.run_service)
        assert 'name' in run_service_sig.parameters
        assert 'cluster' in run_service_sig.parameters
        assert 'input_params' in run_service_sig.parameters

    @pytest.mark.asyncio
    async def test_all_methods_are_async(self, service):
        """Test that all public methods are async"""
        import inspect

        # Get all public methods (not starting with _)
        public_methods = [
            method for method in dir(service)
            if not method.startswith('_') and callable(getattr(service, method))
        ]

        for method_name in ['get_services', 'get_gateways', 'run_service']:
            if method_name in public_methods:
                method = getattr(service, method_name)
                assert inspect.iscoroutinefunction(method)

    @pytest.mark.asyncio
    async def test_return_types(self, service, mock_client):
        """Test that methods return correct types"""
        from collections.abc import Sequence, Mapping

        # Test get_services return type
        mock_response = MagicMock()
        mock_response.json.return_value = [{"name": "test"}]
        mock_client.get.return_value = mock_response

        services_result = await service.get_services()
        assert isinstance(services_result, Sequence)

        # Test get_gateways return type
        gateways_result = await service.get_gateways()
        assert isinstance(gateways_result, Sequence)

        # Test run_service return type
        mock_response.json.return_value = {"return_code": 0}
        mock_client.post.return_value = mock_response

        run_result = await service.run_service("test", "cluster")
        assert isinstance(run_result, Mapping)


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
    async def test_unicode_service_names(self, service, mock_client):
        """Test service names with Unicode characters"""
        service_name = "测试服务"
        cluster_name = "集群"
        expected_result = {"return_code": 0}

        mock_response = MagicMock()
        mock_response.json.return_value = expected_result
        mock_client.post.return_value = mock_response

        await service.run_service(service_name, cluster_name)

        # Verify Unicode names were handled correctly
        expected_body = {
            "serviceName": service_name,
            "clusterId": cluster_name
        }
        mock_client.post.assert_called_with(
            "/gateway_manager/v1/services/run",
            json=expected_body
        )

    @pytest.mark.asyncio
    async def test_special_characters_in_names(self, service, mock_client):
        """Test service and cluster names with special characters"""
        service_name = "service-with-special@chars!"
        cluster_name = "cluster_with_underscores.and.dots"
        expected_result = {"return_code": 0}

        mock_response = MagicMock()
        mock_response.json.return_value = expected_result
        mock_client.post.return_value = mock_response

        await service.run_service(service_name, cluster_name)

        # Should handle special characters correctly
        expected_body = {
            "serviceName": service_name,
            "clusterId": cluster_name
        }
        mock_client.post.assert_called_with(
            "/gateway_manager/v1/services/run",
            json=expected_body
        )

    @pytest.mark.asyncio
    async def test_empty_string_names(self, service, mock_client):
        """Test service and cluster names as empty strings"""
        service_name = ""
        cluster_name = ""
        expected_result = {"return_code": 1}

        mock_response = MagicMock()
        mock_response.json.return_value = expected_result
        mock_client.post.return_value = mock_response

        await service.run_service(service_name, cluster_name)

        # Should handle empty strings (though may fail on server side)
        expected_body = {
            "serviceName": service_name,
            "clusterId": cluster_name
        }
        mock_client.post.assert_called_with(
            "/gateway_manager/v1/services/run",
            json=expected_body
        )

    @pytest.mark.asyncio
    async def test_very_long_names(self, service, mock_client):
        """Test very long service and cluster names"""
        service_name = "a" * 1000
        cluster_name = "b" * 1000
        expected_result = {"return_code": 0}

        mock_response = MagicMock()
        mock_response.json.return_value = expected_result
        mock_client.post.return_value = mock_response

        await service.run_service(service_name, cluster_name)

        # Should handle long names
        expected_body = {
            "serviceName": service_name,
            "clusterId": cluster_name
        }
        mock_client.post.assert_called_with(
            "/gateway_manager/v1/services/run",
            json=expected_body
        )

    @pytest.mark.asyncio
    async def test_concurrent_operations(self, service, mock_client):
        """Test concurrent service operations"""
        import asyncio

        # Setup different responses for different endpoints
        def mock_get_response(*args, **kwargs):
            endpoint = args[0]
            response = MagicMock()
            if "services" in endpoint:
                response.json.return_value = [{"name": "service1"}]
            else:  # gateways
                response.json.return_value = [{"name": "gateway1"}]
            return response

        def mock_post_response(*args, **kwargs):
            response = MagicMock()
            response.json.return_value = {"return_code": 0}
            return response

        mock_client.get.side_effect = mock_get_response
        mock_client.post.side_effect = mock_post_response

        # Run multiple operations concurrently
        tasks = [
            service.get_services(),
            service.get_gateways(),
            service.run_service("test-service", "test-cluster")
        ]

        results = await asyncio.gather(*tasks, return_exceptions=True)

        # All should complete successfully
        assert len(results) == 3
        for result in results:
            assert not isinstance(result, Exception)


class TestDocumentation:
    """Test service documentation and metadata"""

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

    def test_service_has_docstring(self, service):
        """Test that the Service class has proper documentation"""
        assert service.__class__.__doc__ is not None
        assert len(service.__class__.__doc__.strip()) > 0

    def test_methods_have_docstrings(self, service):
        """Test that all methods have proper documentation"""
        methods = ['get_services', 'get_gateways', 'run_service']
        for method_name in methods:
            method = getattr(service, method_name)
            assert method.__doc__ is not None
            assert len(method.__doc__.strip()) > 0

    def test_docstrings_contain_required_sections(self, service):
        """Test that method docstrings contain required sections"""
        methods = ['get_services', 'get_gateways', 'run_service']
        for method_name in methods:
            method = getattr(service, method_name)
            docstring = method.__doc__
            assert "Args:" in docstring
            assert "Returns:" in docstring
            assert "Raises:" in docstring