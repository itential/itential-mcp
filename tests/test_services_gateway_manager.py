# Copyright (c) 2025 Itential, Inc
# GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

import pytest
from unittest.mock import AsyncMock, MagicMock

from itential_mcp.platform.services.gateway_manager import Service


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
                "decorator": {
                    "type": "object",
                    "properties": {"param1": {"type": "string"}},
                },
            },
            {
                "name": "test-service-2",
                "cluster": "cluster-2",
                "type": "python-script",
                "description": "Test Python script service",
                "decorator": {
                    "type": "object",
                    "properties": {"param2": {"type": "integer"}},
                },
            },
        ]

        # Mock response data
        mock_response = MagicMock()
        mock_response.json.return_value = {"result": expected_services}
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
        mock_response.json.return_value = {"result": []}
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
                "enabled": True,
            },
            {
                "name": "gateway-2",
                "cluster": "cluster-2",
                "description": "Secondary gateway",
                "status": "disconnected",
                "enabled": False,
            },
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
            "elapsed_time": 300,
        }

        # Mock response data
        mock_response = MagicMock()
        mock_response.json.return_value = expected_result
        mock_client.post.return_value = mock_response

        result = await service.run_service(service_name, cluster_name)

        # Verify client was called with correct parameters
        expected_body = {"serviceName": service_name, "clusterId": cluster_name}
        mock_client.post.assert_called_once_with(
            "/gateway_manager/v1/services/run", json=expected_body
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
            "elapsed_time": 300,
        }

        # Mock response data
        mock_response = MagicMock()
        mock_response.json.return_value = expected_result
        mock_client.post.return_value = mock_response

        result = await service.run_service(
            service_name, cluster_name, input_params=input_params
        )

        # Verify client was called with correct parameters including input params
        expected_body = {
            "serviceName": service_name,
            "clusterId": cluster_name,
            "params": input_params,
        }
        mock_client.post.assert_called_once_with(
            "/gateway_manager/v1/services/run", json=expected_body
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

        await service.run_service(service_name, cluster_name, input_params=None)

        # Verify client was called without params in body
        expected_body = {"serviceName": service_name, "clusterId": cluster_name}
        mock_client.post.assert_called_once_with(
            "/gateway_manager/v1/services/run", json=expected_body
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

        await service.run_service(service_name, cluster_name, input_params=input_params)

        # Verify client was called without params because empty dict is falsy
        expected_body = {"serviceName": service_name, "clusterId": cluster_name}
        mock_client.post.assert_called_once_with(
            "/gateway_manager/v1/services/run", json=expected_body
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
            "elapsed_time": 60,
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
                "settings": {"timeout": 300, "retries": 3},
            },
            "targets": ["device1", "device2"],
            "variables": {"var1": "value1", "var2": None, "var3": True},
        }
        expected_result = {"return_code": 0}

        # Mock response data
        mock_response = MagicMock()
        mock_response.json.return_value = expected_result
        mock_client.post.return_value = mock_response

        await service.run_service(service_name, cluster_name, input_params=input_params)

        # Verify client was called with complex params
        expected_body = {
            "serviceName": service_name,
            "clusterId": cluster_name,
            "params": input_params,
        }
        mock_client.post.assert_called_once_with(
            "/gateway_manager/v1/services/run", json=expected_body
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
        from itential_mcp.platform.services import ServiceBase

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
        assert "name" in run_service_sig.parameters
        assert "cluster" in run_service_sig.parameters
        assert "input_params" in run_service_sig.parameters

    @pytest.mark.asyncio
    async def test_all_methods_are_async(self, service):
        """Test that all public methods are async"""
        import inspect

        # Get all public methods (not starting with _)
        public_methods = [
            method
            for method in dir(service)
            if not method.startswith("_") and callable(getattr(service, method))
        ]

        for method_name in ["get_services", "get_gateways", "run_service"]:
            if method_name in public_methods:
                method = getattr(service, method_name)
                assert inspect.iscoroutinefunction(method)

    @pytest.mark.asyncio
    async def test_return_types(self, service, mock_client):
        """Test that methods return correct types"""
        from collections.abc import Sequence, Mapping

        # Test get_services return type
        mock_response = MagicMock()
        mock_response.json.return_value = {"result": [{"name": "test"}]}
        mock_client.get.return_value = mock_response

        services_result = await service.get_services()
        assert isinstance(services_result, Sequence)

        # Test get_gateways return type
        mock_response.json.return_value = [
            {"name": "gateway"}
        ]  # get_gateways returns direct response
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
        expected_body = {"serviceName": service_name, "clusterId": cluster_name}
        mock_client.post.assert_called_with(
            "/gateway_manager/v1/services/run", json=expected_body
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
        expected_body = {"serviceName": service_name, "clusterId": cluster_name}
        mock_client.post.assert_called_with(
            "/gateway_manager/v1/services/run", json=expected_body
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
        expected_body = {"serviceName": service_name, "clusterId": cluster_name}
        mock_client.post.assert_called_with(
            "/gateway_manager/v1/services/run", json=expected_body
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
        expected_body = {"serviceName": service_name, "clusterId": cluster_name}
        mock_client.post.assert_called_with(
            "/gateway_manager/v1/services/run", json=expected_body
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
                response.json.return_value = {"result": [{"name": "service1"}]}
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
            service.run_service("test-service", "test-cluster"),
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
        methods = [
            "get_gateways",
            "run_service",
        ]  # get_services has empty docstring currently
        for method_name in methods:
            method = getattr(service, method_name)
            assert method.__doc__ is not None
            assert len(method.__doc__.strip()) > 0

    def test_docstrings_contain_required_sections(self, service):
        """Test that method docstrings contain required sections"""
        import inspect

        methods = [
            "get_gateways",
            "run_service",
        ]  # get_services has empty docstring currently
        for method_name in methods:
            method = getattr(service, method_name)
            docstring = method.__doc__
            # Check for Args section only if method has parameters
            sig = inspect.signature(method)
            if len(sig.parameters) > 0:
                assert "Args:" in docstring
            assert "Returns:" in docstring
            assert "Raises:" in docstring


class TestGetService:
    """Test cases for the get_service method"""

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
    async def test_get_service_success(self, service, mock_client):
        """Test successful service retrieval by ID"""
        service_id = "svc_123abc"
        expected_service = {
            "id": service_id,
            "name": "test-service",
            "type": "ansible-playbook",
            "cluster_id": "cluster-1",
            "gateway_id": "gw-1",
            "description": "Test service",
            "enabled": True,
            "parameters": {"param1": {"type": "string"}},
        }

        mock_response = MagicMock()
        mock_response.json.return_value = expected_service
        mock_client.get.return_value = mock_response

        result = await service.get_service(service_id)

        mock_client.get.assert_called_once_with(
            f"/gateway_manager/v1/services/{service_id}"
        )
        assert result == expected_service
        assert result["id"] == service_id

    @pytest.mark.asyncio
    async def test_get_service_not_found(self, service, mock_client):
        """Test get_service with non-existent service ID"""
        mock_client.get.side_effect = Exception("Service not found")

        with pytest.raises(Exception, match="Service not found"):
            await service.get_service("nonexistent_id")


class TestGetCertificates:
    """Test cases for the get_certificates method"""

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
    async def test_get_certificates_success(self, service, mock_client):
        """Test successful certificates retrieval"""
        expected_certs = [
            {
                "id": "cert_1",
                "alias": "prod-cert",
                "contract_id": "contract_1",
                "is_expired": False,
            },
            {
                "id": "cert_2",
                "alias": "dev-cert",
                "contract_id": "contract_2",
                "is_expired": True,
            },
        ]

        mock_response = MagicMock()
        mock_response.json.return_value = expected_certs
        mock_client.get.return_value = mock_response

        result = await service.get_certificates()

        mock_client.get.assert_called_once_with("/gateway_manager/v1/certificates")
        assert result == expected_certs
        assert len(result) == 2

    @pytest.mark.asyncio
    async def test_get_certificates_empty_list(self, service, mock_client):
        """Test get_certificates with no certificates"""
        mock_response = MagicMock()
        mock_response.json.return_value = []
        mock_client.get.return_value = mock_response

        result = await service.get_certificates()

        assert result == []


class TestCreateCertificate:
    """Test cases for the create_certificate method"""

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
    async def test_create_certificate_with_alias(self, service, mock_client):
        """Test certificate creation with alias"""
        raw_cert = "-----BEGIN CERTIFICATE-----\nMIID..."
        contract_id = "contract_123"
        alias = "Production Certificate"
        expected_result = {
            "id": "cert_new",
            "contract_id": contract_id,
            "alias": alias,
        }

        mock_response = MagicMock()
        mock_response.json.return_value = expected_result
        mock_client.post.return_value = mock_response

        result = await service.create_certificate(raw_cert, contract_id, alias=alias)

        expected_body = {
            "raw_certificate": raw_cert,
            "contract_id": contract_id,
            "alias": alias,
        }
        mock_client.post.assert_called_once_with(
            "/gateway_manager/v1/certificates", json=expected_body
        )
        assert result == expected_result

    @pytest.mark.asyncio
    async def test_create_certificate_without_alias(self, service, mock_client):
        """Test certificate creation without alias"""
        raw_cert = "-----BEGIN CERTIFICATE-----\nMIID..."
        contract_id = "contract_123"
        expected_result = {"id": "cert_new", "contract_id": contract_id}

        mock_response = MagicMock()
        mock_response.json.return_value = expected_result
        mock_client.post.return_value = mock_response

        result = await service.create_certificate(raw_cert, contract_id)

        expected_body = {"raw_certificate": raw_cert, "contract_id": contract_id}
        mock_client.post.assert_called_once_with(
            "/gateway_manager/v1/certificates", json=expected_body
        )
        assert result == expected_result


class TestGetCertificate:
    """Test cases for the get_certificate method"""

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
    async def test_get_certificate_success(self, service, mock_client):
        """Test successful certificate retrieval by ID"""
        cert_id = "cert_123"
        expected_cert = {
            "id": cert_id,
            "alias": "Test Certificate",
            "contract_id": "contract_123",
            "is_expired": False,
        }

        mock_response = MagicMock()
        mock_response.json.return_value = expected_cert
        mock_client.get.return_value = mock_response

        result = await service.get_certificate(cert_id)

        mock_client.get.assert_called_once_with(
            f"/gateway_manager/v1/certificates/{cert_id}"
        )
        assert result == expected_cert


class TestUpdateCertificate:
    """Test cases for the update_certificate method"""

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
    async def test_update_certificate_alias_only(self, service, mock_client):
        """Test updating certificate alias only"""
        cert_id = "cert_123"
        new_alias = "Updated Certificate"
        expected_result = {"id": cert_id, "alias": new_alias}

        mock_response = MagicMock()
        mock_response.json.return_value = expected_result
        mock_client.put.return_value = mock_response

        result = await service.update_certificate(cert_id, alias=new_alias)

        expected_body = {"alias": new_alias}
        mock_client.put.assert_called_once_with(
            f"/gateway_manager/v1/certificates/{cert_id}", json=expected_body
        )
        assert result == expected_result

    @pytest.mark.asyncio
    async def test_update_certificate_contract_id_only(self, service, mock_client):
        """Test updating certificate contract_id only"""
        cert_id = "cert_123"
        new_contract_id = "contract_456"
        expected_result = {"id": cert_id, "contract_id": new_contract_id}

        mock_response = MagicMock()
        mock_response.json.return_value = expected_result
        mock_client.put.return_value = mock_response

        result = await service.update_certificate(cert_id, contract_id=new_contract_id)

        expected_body = {"contract_id": new_contract_id}
        mock_client.put.assert_called_once_with(
            f"/gateway_manager/v1/certificates/{cert_id}", json=expected_body
        )
        assert result == expected_result

    @pytest.mark.asyncio
    async def test_update_certificate_raw_certificate_only(self, service, mock_client):
        """Test updating certificate data only"""
        cert_id = "cert_123"
        new_cert = "-----BEGIN CERTIFICATE-----\nNEW..."
        expected_result = {"id": cert_id, "raw_certificate": new_cert}

        mock_response = MagicMock()
        mock_response.json.return_value = expected_result
        mock_client.put.return_value = mock_response

        result = await service.update_certificate(cert_id, raw_certificate=new_cert)

        expected_body = {"raw_certificate": new_cert}
        mock_client.put.assert_called_once_with(
            f"/gateway_manager/v1/certificates/{cert_id}", json=expected_body
        )
        assert result == expected_result

    @pytest.mark.asyncio
    async def test_update_certificate_all_fields(self, service, mock_client):
        """Test updating all certificate fields"""
        cert_id = "cert_123"
        new_alias = "Updated Cert"
        new_contract_id = "contract_new"
        new_cert = "-----BEGIN CERTIFICATE-----\nNEW..."
        expected_result = {
            "id": cert_id,
            "alias": new_alias,
            "contract_id": new_contract_id,
        }

        mock_response = MagicMock()
        mock_response.json.return_value = expected_result
        mock_client.put.return_value = mock_response

        result = await service.update_certificate(
            cert_id,
            alias=new_alias,
            contract_id=new_contract_id,
            raw_certificate=new_cert,
        )

        expected_body = {
            "alias": new_alias,
            "contract_id": new_contract_id,
            "raw_certificate": new_cert,
        }
        mock_client.put.assert_called_once_with(
            f"/gateway_manager/v1/certificates/{cert_id}", json=expected_body
        )
        assert result == expected_result

    @pytest.mark.asyncio
    async def test_update_certificate_no_fields(self, service, mock_client):
        """Test update_certificate with no fields (should send empty body)"""
        cert_id = "cert_123"
        expected_result = {"id": cert_id}

        mock_response = MagicMock()
        mock_response.json.return_value = expected_result
        mock_client.put.return_value = mock_response

        result = await service.update_certificate(cert_id)

        expected_body = {}
        mock_client.put.assert_called_once_with(
            f"/gateway_manager/v1/certificates/{cert_id}", json=expected_body
        )
        assert result == expected_result


class TestDeleteCertificate:
    """Test cases for the delete_certificate method"""

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
    async def test_delete_certificate_success(self, service, mock_client):
        """Test successful certificate deletion"""
        cert_id = "cert_123"
        expected_result = {"success": True, "message": "Certificate deleted"}

        mock_response = MagicMock()
        mock_response.json.return_value = expected_result
        mock_client.delete.return_value = mock_response

        result = await service.delete_certificate(cert_id)

        mock_client.delete.assert_called_once_with(
            f"/gateway_manager/v1/certificates/{cert_id}"
        )
        assert result == expected_result


class TestGetConnections:
    """Test cases for the get_connections method"""

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
    async def test_get_connections_success(self, service, mock_client):
        """Test successful connections retrieval"""
        expected_connections = [
            {"cluster_id": "cluster-1", "gateway_id": "gw-1", "status": "connected"},
            {"cluster_id": "cluster-2", "gateway_id": "gw-2", "status": "connected"},
        ]

        mock_response = MagicMock()
        mock_response.json.return_value = expected_connections
        mock_client.get.return_value = mock_response

        result = await service.get_connections()

        mock_client.get.assert_called_once_with("/gateway_manager/v1/connections")
        assert result == expected_connections


class TestGetConnection:
    """Test cases for the get_connection method"""

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
    async def test_get_connection_success(self, service, mock_client):
        """Test successful connection health check"""
        cluster_id = "cluster-1"
        expected_health = {
            "cluster_id": cluster_id,
            "is_healthy": True,
            "status": "connected",
        }

        mock_response = MagicMock()
        mock_response.json.return_value = expected_health
        mock_client.get.return_value = mock_response

        result = await service.get_connection(cluster_id)

        mock_client.get.assert_called_once_with(
            f"/gateway_manager/v1/connections/{cluster_id}"
        )
        assert result == expected_health


class TestCreateGateway:
    """Test cases for the create_gateway method"""

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
    async def test_create_gateway_required_fields_only(self, service, mock_client):
        """Test gateway creation with required fields only"""
        cluster_id = "prod_cluster_01"
        name = "Production Gateway"
        description = "Gateway for production"
        enabled = True
        expected_result = {
            "id": "gw_new",
            "cluster_id": cluster_id,
            "name": name,
            "description": description,
            "enabled": enabled,
        }

        mock_response = MagicMock()
        mock_response.json.return_value = expected_result
        mock_client.post.return_value = mock_response

        result = await service.create_gateway(cluster_id, name, description, enabled)

        expected_body = {
            "cluster_id": cluster_id,
            "name": name,
            "description": description,
            "enabled": enabled,
        }
        mock_client.post.assert_called_once_with(
            "/gateway_manager/v1/gateways", json=expected_body
        )
        assert result == expected_result

    @pytest.mark.asyncio
    async def test_create_gateway_all_fields(self, service, mock_client):
        """Test gateway creation with all optional fields"""
        cluster_id = "prod_cluster_01"
        name = "Production Gateway"
        description = "Gateway for production"
        enabled = True
        certificate_id = "cert_123"
        connection_config = {"timeout": 30}
        tags = ["production", "network"]
        metadata = {"location": "datacenter-1"}
        expected_result = {"id": "gw_new", "cluster_id": cluster_id}

        mock_response = MagicMock()
        mock_response.json.return_value = expected_result
        mock_client.post.return_value = mock_response

        result = await service.create_gateway(
            cluster_id,
            name,
            description,
            enabled,
            certificate_id=certificate_id,
            connection_config=connection_config,
            tags=tags,
            metadata=metadata,
        )

        expected_body = {
            "cluster_id": cluster_id,
            "name": name,
            "description": description,
            "enabled": enabled,
            "certificate_id": certificate_id,
            "connection_config": connection_config,
            "tags": tags,
            "metadata": metadata,
        }
        mock_client.post.assert_called_once_with(
            "/gateway_manager/v1/gateways", json=expected_body
        )
        assert result == expected_result

    @pytest.mark.asyncio
    async def test_create_gateway_with_some_optional_fields(self, service, mock_client):
        """Test gateway creation with some optional fields"""
        cluster_id = "prod_cluster_01"
        name = "Production Gateway"
        description = "Gateway for production"
        enabled = True
        tags = ["production"]
        expected_result = {"id": "gw_new"}

        mock_response = MagicMock()
        mock_response.json.return_value = expected_result
        mock_client.post.return_value = mock_response

        result = await service.create_gateway(
            cluster_id, name, description, enabled, tags=tags
        )

        expected_body = {
            "cluster_id": cluster_id,
            "name": name,
            "description": description,
            "enabled": enabled,
            "tags": tags,
        }
        mock_client.post.assert_called_once_with(
            "/gateway_manager/v1/gateways", json=expected_body
        )
        assert result == expected_result


class TestGetGateway:
    """Test cases for the get_gateway method"""

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
    async def test_get_gateway_success(self, service, mock_client):
        """Test successful gateway retrieval by ID"""
        gateway_id = "gw_123"
        expected_gateway = {
            "id": gateway_id,
            "name": "Test Gateway",
            "cluster_id": "cluster-1",
            "status": "connected",
        }

        mock_response = MagicMock()
        mock_response.json.return_value = expected_gateway
        mock_client.get.return_value = mock_response

        result = await service.get_gateway(gateway_id)

        mock_client.get.assert_called_once_with(
            f"/gateway_manager/v1/gateways/{gateway_id}"
        )
        assert result == expected_gateway


class TestUpdateGateway:
    """Test cases for the update_gateway method"""

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
    async def test_update_gateway_name_only(self, service, mock_client):
        """Test updating gateway name only"""
        gateway_id = "gw_123"
        new_name = "Updated Gateway"
        expected_result = {"id": gateway_id, "name": new_name}

        mock_response = MagicMock()
        mock_response.json.return_value = expected_result
        mock_client.put.return_value = mock_response

        result = await service.update_gateway(gateway_id, name=new_name)

        expected_body = {"name": new_name}
        mock_client.put.assert_called_once_with(
            f"/gateway_manager/v1/gateways/{gateway_id}", json=expected_body
        )
        assert result == expected_result

    @pytest.mark.asyncio
    async def test_update_gateway_multiple_fields(self, service, mock_client):
        """Test updating multiple gateway fields"""
        gateway_id = "gw_123"
        new_name = "Updated Gateway"
        new_description = "Updated description"
        new_enabled = False
        expected_result = {"id": gateway_id}

        mock_response = MagicMock()
        mock_response.json.return_value = expected_result
        mock_client.put.return_value = mock_response

        result = await service.update_gateway(
            gateway_id, name=new_name, description=new_description, enabled=new_enabled
        )

        expected_body = {
            "name": new_name,
            "description": new_description,
            "enabled": new_enabled,
        }
        mock_client.put.assert_called_once_with(
            f"/gateway_manager/v1/gateways/{gateway_id}", json=expected_body
        )
        assert result == expected_result

    @pytest.mark.asyncio
    async def test_update_gateway_all_fields(self, service, mock_client):
        """Test updating all gateway fields"""
        gateway_id = "gw_123"
        updates = {
            "name": "New Name",
            "description": "New Description",
            "enabled": False,
            "certificate_id": "cert_new",
            "connection_config": {"timeout": 60},
            "tags": ["updated"],
            "metadata": {"key": "value"},
        }
        expected_result = {"id": gateway_id}

        mock_response = MagicMock()
        mock_response.json.return_value = expected_result
        mock_client.put.return_value = mock_response

        result = await service.update_gateway(gateway_id, **updates)

        mock_client.put.assert_called_once_with(
            f"/gateway_manager/v1/gateways/{gateway_id}", json=updates
        )
        assert result == expected_result

    @pytest.mark.asyncio
    async def test_update_gateway_no_fields(self, service, mock_client):
        """Test update_gateway with no fields (should send empty body)"""
        gateway_id = "gw_123"
        expected_result = {"id": gateway_id}

        mock_response = MagicMock()
        mock_response.json.return_value = expected_result
        mock_client.put.return_value = mock_response

        result = await service.update_gateway(gateway_id)

        expected_body = {}
        mock_client.put.assert_called_once_with(
            f"/gateway_manager/v1/gateways/{gateway_id}", json=expected_body
        )
        assert result == expected_result


class TestDeleteGateway:
    """Test cases for the delete_gateway method"""

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
    async def test_delete_gateway_success(self, service, mock_client):
        """Test successful gateway deletion"""
        gateway_id = "gw_123"
        expected_result = {"success": True, "message": "Gateway deleted"}

        mock_response = MagicMock()
        mock_response.json.return_value = expected_result
        mock_client.delete.return_value = mock_response

        result = await service.delete_gateway(gateway_id)

        mock_client.delete.assert_called_once_with(
            f"/gateway_manager/v1/gateways/{gateway_id}"
        )
        assert result == expected_result


class TestGetServiceGroups:
    """Test cases for the get_service_groups method"""

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
    async def test_get_service_groups_success(self, service, mock_client):
        """Test successful service groups retrieval"""
        expected_groups = [
            {"id": "sg_1", "name": "group-1", "service_count": 3},
            {"id": "sg_2", "name": "group-2", "service_count": 5},
        ]

        mock_response = MagicMock()
        mock_response.json.return_value = expected_groups
        mock_client.get.return_value = mock_response

        result = await service.get_service_groups()

        mock_client.get.assert_called_once_with("/gateway_manager/v1/service-groups")
        assert result == expected_groups


class TestCreateServiceGroup:
    """Test cases for the create_service_group method"""

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
    async def test_create_service_group_required_fields_only(
        self, service, mock_client
    ):
        """Test service group creation with required fields only"""
        name = "network_deployment"
        description = "Network deployment services"
        expected_result = {"id": "sg_new", "name": name, "description": description}

        mock_response = MagicMock()
        mock_response.json.return_value = expected_result
        mock_client.post.return_value = mock_response

        result = await service.create_service_group(name, description)

        expected_body = {"name": name, "description": description}
        mock_client.post.assert_called_once_with(
            "/gateway_manager/v1/service-groups", json=expected_body
        )
        assert result == expected_result

    @pytest.mark.asyncio
    async def test_create_service_group_all_fields(self, service, mock_client):
        """Test service group creation with all fields"""
        name = "network_deployment"
        description = "Network deployment services"
        services = ["svc_1", "svc_2"]
        enabled = True
        tags = ["network", "deployment"]
        metadata = {"owner": "team-network"}
        expected_result = {"id": "sg_new"}

        mock_response = MagicMock()
        mock_response.json.return_value = expected_result
        mock_client.post.return_value = mock_response

        result = await service.create_service_group(
            name,
            description,
            services=services,
            enabled=enabled,
            tags=tags,
            metadata=metadata,
        )

        expected_body = {
            "name": name,
            "description": description,
            "services": services,
            "enabled": enabled,
            "tags": tags,
            "metadata": metadata,
        }
        mock_client.post.assert_called_once_with(
            "/gateway_manager/v1/service-groups", json=expected_body
        )
        assert result == expected_result


class TestGetServiceGroup:
    """Test cases for the get_service_group method"""

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
    async def test_get_service_group_success(self, service, mock_client):
        """Test successful service group retrieval by ID"""
        group_id = "sg_123"
        expected_group = {
            "id": group_id,
            "name": "Test Group",
            "description": "Test service group",
            "service_count": 3,
        }

        mock_response = MagicMock()
        mock_response.json.return_value = expected_group
        mock_client.get.return_value = mock_response

        result = await service.get_service_group(group_id)

        mock_client.get.assert_called_once_with(
            f"/gateway_manager/v1/service-groups/{group_id}"
        )
        assert result == expected_group


class TestUpdateServiceGroup:
    """Test cases for the update_service_group method"""

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
    async def test_update_service_group_name_only(self, service, mock_client):
        """Test updating service group name only"""
        group_id = "sg_123"
        new_name = "Updated Group"
        expected_result = {"id": group_id, "name": new_name}

        mock_response = MagicMock()
        mock_response.json.return_value = expected_result
        mock_client.patch.return_value = mock_response

        result = await service.update_service_group(group_id, name=new_name)

        expected_body = {"name": new_name}
        mock_client.patch.assert_called_once_with(
            f"/gateway_manager/v1/service-groups/{group_id}", json=expected_body
        )
        assert result == expected_result

    @pytest.mark.asyncio
    async def test_update_service_group_add_services(self, service, mock_client):
        """Test adding services to service group"""
        group_id = "sg_123"
        add_services = ["svc_789"]
        expected_result = {"id": group_id, "service_count": 4}

        mock_response = MagicMock()
        mock_response.json.return_value = expected_result
        mock_client.patch.return_value = mock_response

        result = await service.update_service_group(group_id, add_services=add_services)

        expected_body = {"add_services": add_services}
        mock_client.patch.assert_called_once_with(
            f"/gateway_manager/v1/service-groups/{group_id}", json=expected_body
        )
        assert result == expected_result

    @pytest.mark.asyncio
    async def test_update_service_group_remove_services(self, service, mock_client):
        """Test removing services from service group"""
        group_id = "sg_123"
        remove_services = ["svc_456"]
        expected_result = {"id": group_id, "service_count": 2}

        mock_response = MagicMock()
        mock_response.json.return_value = expected_result
        mock_client.patch.return_value = mock_response

        result = await service.update_service_group(
            group_id, remove_services=remove_services
        )

        expected_body = {"remove_services": remove_services}
        mock_client.patch.assert_called_once_with(
            f"/gateway_manager/v1/service-groups/{group_id}", json=expected_body
        )
        assert result == expected_result

    @pytest.mark.asyncio
    async def test_update_service_group_all_fields(self, service, mock_client):
        """Test updating all service group fields"""
        group_id = "sg_123"
        updates = {
            "name": "New Name",
            "description": "New Description",
            "services": ["svc_1", "svc_2"],
            "add_services": ["svc_3"],
            "remove_services": ["svc_4"],
            "enabled": False,
            "tags": ["updated"],
            "metadata": {"key": "value"},
        }
        expected_result = {"id": group_id}

        mock_response = MagicMock()
        mock_response.json.return_value = expected_result
        mock_client.patch.return_value = mock_response

        result = await service.update_service_group(group_id, **updates)

        mock_client.patch.assert_called_once_with(
            f"/gateway_manager/v1/service-groups/{group_id}", json=updates
        )
        assert result == expected_result

    @pytest.mark.asyncio
    async def test_update_service_group_no_fields(self, service, mock_client):
        """Test update_service_group with no fields (should send empty body)"""
        group_id = "sg_123"
        expected_result = {"id": group_id}

        mock_response = MagicMock()
        mock_response.json.return_value = expected_result
        mock_client.patch.return_value = mock_response

        result = await service.update_service_group(group_id)

        expected_body = {}
        mock_client.patch.assert_called_once_with(
            f"/gateway_manager/v1/service-groups/{group_id}", json=expected_body
        )
        assert result == expected_result


class TestDeleteServiceGroup:
    """Test cases for the delete_service_group method"""

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
    async def test_delete_service_group_success(self, service, mock_client):
        """Test successful service group deletion"""
        group_id = "sg_123"
        expected_result = {"success": True, "message": "Service group deleted"}

        mock_response = MagicMock()
        mock_response.json.return_value = expected_result
        mock_client.delete.return_value = mock_response

        result = await service.delete_service_group(group_id)

        mock_client.delete.assert_called_once_with(
            f"/gateway_manager/v1/service-groups/{group_id}"
        )
        assert result == expected_result


class TestGetHealthStatus:
    """Test cases for the get_health_status method"""

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
    async def test_get_health_status_success(self, service, mock_client):
        """Test successful health status retrieval"""
        expected_health = {
            "status": "healthy",
            "uptime": 3600,
            "version": "2.1.0",
        }

        mock_response = MagicMock()
        mock_response.json.return_value = expected_health
        mock_client.get.return_value = mock_response

        result = await service.get_health_status()

        mock_client.get.assert_called_once_with("/gateway_manager/v1/health/status")
        assert result == expected_health
        assert result["status"] == "healthy"


class TestGetVersion:
    """Test cases for the get_version method"""

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
    async def test_get_version_success(self, service, mock_client):
        """Test successful version retrieval"""
        expected_version = {
            "version": "2.1.0",
            "build": "abc123",
            "api_version": "v1",
        }

        mock_response = MagicMock()
        mock_response.json.return_value = expected_version
        mock_client.get.return_value = mock_response

        result = await service.get_version()

        mock_client.get.assert_called_once_with("/gateway_manager/v1/version")
        assert result == expected_version
        assert result["version"] == "2.1.0"
