# Copyright (c) 2025 Itential, Inc
# GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

import pytest
from unittest.mock import AsyncMock, MagicMock, Mock, patch
from dataclasses import dataclass

from pydantic import BaseModel

from itential_mcp.bindings import service
from itential_mcp.platform import PlatformClient
from itential_mcp.core import exceptions
from fastmcp import Context


class TestGetService:
    """Test cases for the _get_service function"""

    @pytest.fixture
    def mock_platform_client(self):
        """Create a mock platform client"""
        mock_client = AsyncMock(spec=PlatformClient)
        mock_client.gateway_manager = AsyncMock()
        return mock_client

    @pytest.fixture
    def mock_tool_config(self):
        """Create a mock tool configuration"""

        @dataclass
        class MockTool:
            name: str = "test-service"
            tool_name: str = "test_tool"

        return MockTool()

    @pytest.mark.asyncio
    async def test_get_service_success(self, mock_platform_client, mock_tool_config):
        """Test successful service retrieval"""
        expected_service = {
            "service_metadata": {
                "name": "test-service",
                "location": "cluster-1",
                "description": "Test service",
                "decorator": {"type": "object"},
            }
        }

        mock_platform_client.gateway_manager.get_services.return_value = [
            {"service_metadata": {"name": "other-service", "location": "cluster-2"}},
            expected_service,
        ]

        result = await service._get_service(mock_platform_client, mock_tool_config)

        assert result == expected_service
        mock_platform_client.gateway_manager.get_services.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_service_not_found(self, mock_platform_client, mock_tool_config):
        """Test service not found raises NotFoundError"""
        mock_platform_client.gateway_manager.get_services.return_value = [
            {"service_metadata": {"name": "other-service", "location": "cluster-1"}}
        ]

        with pytest.raises(
            exceptions.NotFoundError, match="service test-service could not be found"
        ):
            await service._get_service(mock_platform_client, mock_tool_config)

    @pytest.mark.asyncio
    async def test_get_service_empty_services_list(
        self, mock_platform_client, mock_tool_config
    ):
        """Test service not found with empty services list"""
        mock_platform_client.gateway_manager.get_services.return_value = []

        with pytest.raises(exceptions.NotFoundError):
            await service._get_service(mock_platform_client, mock_tool_config)

    @pytest.mark.asyncio
    async def test_get_service_first_match_returned(
        self, mock_platform_client, mock_tool_config
    ):
        """Test that first matching service is returned when multiple matches exist"""
        first_service = {
            "service_metadata": {
                "name": "test-service",
                "location": "cluster-1",
                "version": "1.0",
            }
        }
        second_service = {
            "service_metadata": {
                "name": "test-service",
                "location": "cluster-2",
                "version": "2.0",
            }
        }

        mock_platform_client.gateway_manager.get_services.return_value = [
            first_service,
            second_service,
        ]

        result = await service._get_service(mock_platform_client, mock_tool_config)

        assert result == first_service
        assert result["service_metadata"]["version"] == "1.0"

    @pytest.mark.asyncio
    async def test_get_service_case_sensitive_match(self, mock_platform_client):
        """Test that service matching is case sensitive"""

        @dataclass
        class MockTool:
            name: str = "Test-Service"  # Different case
            tool_name: str = "test_tool"

        tool_config = MockTool()

        mock_platform_client.gateway_manager.get_services.return_value = [
            {
                "service_metadata": {
                    "name": "test-service",  # lowercase
                    "location": "cluster-1",
                }
            }
        ]

        with pytest.raises(exceptions.NotFoundError):
            await service._get_service(mock_platform_client, tool_config)

    @pytest.mark.asyncio
    async def test_get_service_with_special_characters(self, mock_platform_client):
        """Test service retrieval with special characters in name"""

        @dataclass
        class MockTool:
            name: str = "test-service_v2.0"
            tool_name: str = "test_tool"

        tool_config = MockTool()
        expected_service = {
            "service_metadata": {"name": "test-service_v2.0", "location": "cluster-1"}
        }

        mock_platform_client.gateway_manager.get_services.return_value = [
            expected_service
        ]

        result = await service._get_service(mock_platform_client, tool_config)

        assert result == expected_service


class TestRunService:
    """Test cases for the run_service function"""

    @pytest.fixture
    def mock_context(self):
        """Create a mock FastMCP context"""
        context = MagicMock(spec=Context)
        platform_client = AsyncMock(spec=PlatformClient)
        platform_client.gateway_manager = AsyncMock()
        context.request_context.lifespan_context.get.return_value = platform_client
        return context

    @pytest.fixture
    def mock_tool_config(self):
        """Create a mock tool configuration"""

        @dataclass
        class MockTool:
            name: str = "test-service"
            tool_name: str = "test_tool"

        return MockTool()

    @pytest.mark.asyncio
    async def test_run_service_success(self, mock_context, mock_tool_config):
        """Test successful service execution"""
        # Setup mock service
        mock_service = {
            "service_metadata": {
                "name": "test-service",
                "location": "cluster-1",
                "description": "Test service",
            }
        }

        platform_client = mock_context.request_context.lifespan_context.get.return_value
        platform_client.gateway_manager.get_services.return_value = [mock_service]

        # Mock the gateway_manager.run_service call
        expected_result = MagicMock(spec=BaseModel)

        with patch(
            "itential_mcp.bindings.service.gateway_manager.run_service"
        ) as mock_run:
            mock_run.return_value = expected_result

            result = await service.run_service(
                mock_context,
                _tool_config=mock_tool_config,
                input_params={"param1": "value1"},
            )

            assert result == expected_result
            mock_run.assert_called_once_with(
                mock_context,
                name="test-service",
                cluster="cluster-1",
                input_params={"param1": "value1"},
            )

    @pytest.mark.asyncio
    async def test_run_service_no_input_params(self, mock_context, mock_tool_config):
        """Test service execution without input parameters"""
        mock_service = {
            "service_metadata": {"name": "test-service", "location": "cluster-1"}
        }

        platform_client = mock_context.request_context.lifespan_context.get.return_value
        platform_client.gateway_manager.get_services.return_value = [mock_service]

        expected_result = MagicMock(spec=BaseModel)

        with patch(
            "itential_mcp.bindings.service.gateway_manager.run_service"
        ) as mock_run:
            mock_run.return_value = expected_result

            result = await service.run_service(
                mock_context, _tool_config=mock_tool_config
            )

            assert result == expected_result
            mock_run.assert_called_once_with(
                mock_context,
                name="test-service",
                cluster="cluster-1",
                input_params=None,
            )

    @pytest.mark.asyncio
    async def test_run_service_not_found(self, mock_context, mock_tool_config):
        """Test service execution with service not found"""
        platform_client = mock_context.request_context.lifespan_context.get.return_value
        platform_client.gateway_manager.get_services.return_value = []

        with pytest.raises(exceptions.NotFoundError):
            await service.run_service(mock_context, _tool_config=mock_tool_config)

    @pytest.mark.asyncio
    async def test_run_service_extracts_correct_metadata(
        self, mock_context, mock_tool_config
    ):
        """Test that run_service correctly extracts service metadata"""

        # Change tool config name to match service name
        @dataclass
        class MockTool:
            name: str = "complex-service"  # Match the service name
            tool_name: str = "test_tool"

        mock_tool_config = MockTool()

        mock_service = {
            "service_metadata": {
                "name": "complex-service",
                "location": "production-cluster",
                "description": "Complex production service",
                "version": "2.1.0",
            },
            "other_data": "ignored",
        }

        platform_client = mock_context.request_context.lifespan_context.get.return_value
        platform_client.gateway_manager.get_services.return_value = [mock_service]

        with patch(
            "itential_mcp.bindings.service.gateway_manager.run_service"
        ) as mock_run:
            await service.run_service(mock_context, _tool_config=mock_tool_config)

            mock_run.assert_called_once_with(
                mock_context,
                name="complex-service",
                cluster="production-cluster",
                input_params=None,
            )

    @pytest.mark.asyncio
    async def test_run_service_with_empty_input_params(
        self, mock_context, mock_tool_config
    ):
        """Test service execution with empty input parameters dict"""
        mock_service = {
            "service_metadata": {"name": "test-service", "location": "cluster-1"}
        }

        platform_client = mock_context.request_context.lifespan_context.get.return_value
        platform_client.gateway_manager.get_services.return_value = [mock_service]

        with patch(
            "itential_mcp.bindings.service.gateway_manager.run_service"
        ) as mock_run:
            await service.run_service(
                mock_context, _tool_config=mock_tool_config, input_params={}
            )

            mock_run.assert_called_once_with(
                mock_context, name="test-service", cluster="cluster-1", input_params={}
            )


class TestNew:
    """Test cases for the new function"""

    @pytest.fixture
    def mock_platform_client(self):
        """Create a mock platform client"""
        mock_client = AsyncMock(spec=PlatformClient)
        mock_client.gateway_manager = AsyncMock()
        return mock_client

    @pytest.fixture
    def mock_service_tool(self):
        """Create a mock service tool configuration"""

        @dataclass
        class MockServiceTool:
            name: str = "test-service"
            tool_name: str = "test_tool"
            cluster: str = "test-cluster"

        return MockServiceTool()

    @pytest.mark.asyncio
    async def test_new_success_with_description_and_decorator(
        self, mock_platform_client, mock_service_tool
    ):
        """Test successful creation of service binding with description and decorator"""
        mock_service = {
            "service_metadata": {
                "name": "test-service",
                "location": "test-cluster",
                "description": "Test service description",
                "decorator": {
                    "type": "object",
                    "properties": {
                        "param1": {"type": "string"},
                        "param2": {"type": "integer"},
                    },
                },
            }
        }

        mock_platform_client.gateway_manager.get_services.return_value = [mock_service]

        func, description = await service.new(mock_service_tool, mock_platform_client)

        assert func == service.run_service
        assert isinstance(description, str)
        assert "Test service description" in description
        assert "Args:" in description
        assert "data (dict)" in description
        assert "input schema:" in description
        assert "'type': 'object'" in description  # Python repr uses single quotes

    @pytest.mark.asyncio
    async def test_new_success_with_empty_description(
        self, mock_platform_client, mock_service_tool
    ):
        """Test successful creation with empty description"""
        mock_service = {
            "service_metadata": {
                "name": "test-service",
                "location": "test-cluster",
                "description": "",
                "decorator": {"type": "object"},
            }
        }

        mock_platform_client.gateway_manager.get_services.return_value = [mock_service]

        func, description = await service.new(mock_service_tool, mock_platform_client)

        assert func == service.run_service
        assert isinstance(description, str)
        assert "Args:" in description
        assert "data (dict)" in description

    @pytest.mark.asyncio
    async def test_new_success_with_none_description(
        self, mock_platform_client, mock_service_tool
    ):
        """Test successful creation with None description"""
        mock_service = {
            "service_metadata": {
                "name": "test-service",
                "location": "test-cluster",
                "description": None,
                "decorator": {"type": "object"},
            }
        }

        mock_platform_client.gateway_manager.get_services.return_value = [mock_service]

        func, description = await service.new(mock_service_tool, mock_platform_client)

        assert func == service.run_service
        assert isinstance(description, str)
        assert "Args:" in description

    @pytest.mark.asyncio
    async def test_new_success_without_decorator(
        self, mock_platform_client, mock_service_tool
    ):
        """Test successful creation without decorator"""
        mock_service = {
            "service_metadata": {
                "name": "test-service",
                "location": "test-cluster",
                "description": "Simple service",
                "decorator": None,
            }
        }

        mock_platform_client.gateway_manager.get_services.return_value = [mock_service]

        func, description = await service.new(mock_service_tool, mock_platform_client)

        assert func == service.run_service
        assert description == "Simple service"
        assert "Args:" not in description
        assert "input schema:" not in description

    @pytest.mark.asyncio
    async def test_new_success_with_empty_decorator(
        self, mock_platform_client, mock_service_tool
    ):
        """Test successful creation with empty decorator"""
        mock_service = {
            "service_metadata": {
                "name": "test-service",
                "location": "test-cluster",
                "description": "Service with empty decorator",
                "decorator": {},
            }
        }

        mock_platform_client.gateway_manager.get_services.return_value = [mock_service]

        func, description = await service.new(mock_service_tool, mock_platform_client)

        assert func == service.run_service
        assert "Service with empty decorator" in description
        # Empty dict evaluates to False, so no Args section should be added
        assert "Args:" not in description
        assert "{}" not in description

    @pytest.mark.asyncio
    async def test_new_service_not_found(self, mock_platform_client, mock_service_tool):
        """Test new function when service is not found"""
        mock_platform_client.gateway_manager.get_services.return_value = []

        with pytest.raises(exceptions.NotFoundError):
            await service.new(mock_service_tool, mock_platform_client)

    @pytest.mark.asyncio
    async def test_new_complex_decorator(self, mock_platform_client, mock_service_tool):
        """Test new function with complex decorator schema"""
        complex_decorator = {
            "type": "object",
            "properties": {
                "username": {
                    "type": "string",
                    "description": "User name for authentication",
                },
                "config": {
                    "type": "object",
                    "properties": {"timeout": {"type": "integer", "minimum": 1}},
                },
                "options": {"type": "array", "items": {"type": "string"}},
            },
            "required": ["username"],
        }

        mock_service = {
            "service_metadata": {
                "name": "test-service",
                "location": "test-cluster",
                "description": "Complex service",
                "decorator": complex_decorator,
            }
        }

        mock_platform_client.gateway_manager.get_services.return_value = [mock_service]

        func, description = await service.new(mock_service_tool, mock_platform_client)

        assert func == service.run_service
        assert "Complex service" in description
        assert "username" in description
        assert "timeout" in description
        assert "required" in description

    @pytest.mark.asyncio
    async def test_new_return_types(self, mock_platform_client, mock_service_tool):
        """Test that new function returns correct types"""
        mock_service = {
            "service_metadata": {
                "name": "test-service",
                "location": "test-cluster",
                "description": "Test service",
                "decorator": None,
            }
        }

        mock_platform_client.gateway_manager.get_services.return_value = [mock_service]

        result = await service.new(mock_service_tool, mock_platform_client)

        assert isinstance(result, tuple)
        assert len(result) == 2

        func, description = result
        assert callable(func)
        assert isinstance(description, str)

    @pytest.mark.asyncio
    async def test_new_description_formatting(
        self, mock_platform_client, mock_service_tool
    ):
        """Test that description is properly formatted"""
        mock_service = {
            "service_metadata": {
                "name": "test-service",
                "location": "test-cluster",
                "description": "    Multi-line\n    description\n    with whitespace    ",
                "decorator": {"type": "string"},
            }
        }

        mock_platform_client.gateway_manager.get_services.return_value = [mock_service]

        func, description = await service.new(mock_service_tool, mock_platform_client)

        # The original description whitespace is preserved, only the f-string template is cleaned
        assert "Multi-line" in description
        assert "description" in description
        assert "with whitespace" in description
        # The description starts with the original service description whitespace
        assert "    Multi-line" in description


class TestModuleStructure:
    """Test cases for bindings/service module structure"""

    def test_module_imports(self):
        """Test that module imports are correct"""
        import itential_mcp.bindings.service as bs

        assert hasattr(bs, "_get_service")
        assert hasattr(bs, "run_service")
        assert hasattr(bs, "new")
        assert callable(bs._get_service)
        assert callable(bs.run_service)
        assert callable(bs.new)

    def test_function_signatures(self):
        """Test function signatures are correct"""
        import inspect

        # Test _get_service signature
        sig = inspect.signature(service._get_service)
        assert len(sig.parameters) == 2
        assert "platform_client" in sig.parameters
        assert "t" in sig.parameters

        # Test run_service signature
        sig = inspect.signature(service.run_service)
        assert len(sig.parameters) == 3
        assert "ctx" in sig.parameters
        assert "_tool_config" in sig.parameters
        assert "input_params" in sig.parameters

        # Test new signature
        sig = inspect.signature(service.new)
        assert len(sig.parameters) == 2
        assert "t" in sig.parameters
        assert "platform_client" in sig.parameters

    def test_function_docstrings(self):
        """Test that functions have proper docstrings"""
        assert service._get_service.__doc__ is not None
        assert "Args:" in service._get_service.__doc__
        assert "Returns:" in service._get_service.__doc__
        assert "Raises:" in service._get_service.__doc__

        assert service.run_service.__doc__ is not None
        assert "Args:" in service.run_service.__doc__
        assert "Returns:" in service.run_service.__doc__
        assert "Raises:" in service.run_service.__doc__

        assert service.new.__doc__ is not None
        assert "Args:" in service.new.__doc__
        assert "Returns:" in service.new.__doc__
        assert "Raises:" in service.new.__doc__

    def test_module_dependencies(self):
        """Test that module dependencies are available"""
        import itential_mcp.bindings.service as bs

        # Check that required modules/classes are accessible
        assert hasattr(bs, "inspect")
        assert hasattr(bs, "Tuple")
        assert hasattr(bs, "Callable")
        assert hasattr(bs, "BaseModel")
        assert hasattr(bs, "Context")
        assert hasattr(bs, "config")
        assert hasattr(bs, "PlatformClient")
        assert hasattr(bs, "exceptions")
        assert hasattr(bs, "gateway_manager")


class TestServiceIntegration:
    """Integration tests for service binding functions"""

    @pytest.fixture
    def mock_complete_setup(self):
        """Setup complete mock environment for integration tests"""
        # Mock platform client
        platform_client = AsyncMock(spec=PlatformClient)
        platform_client.gateway_manager = AsyncMock()

        # Mock context
        context = MagicMock(spec=Context)
        context.request_context.lifespan_context.get.return_value = platform_client

        # Mock tool config
        @dataclass
        class MockTool:
            name: str = "integration-service"
            tool_name: str = "integration_tool"

        tool_config = MockTool()

        # Mock service data
        service_data = {
            "service_metadata": {
                "name": "integration-service",
                "location": "integration-cluster",
                "description": "Integration test service",
                "decorator": {
                    "type": "object",
                    "properties": {"input": {"type": "string"}},
                },
            }
        }

        return {
            "platform_client": platform_client,
            "context": context,
            "tool_config": tool_config,
            "service_data": service_data,
        }

    @pytest.mark.asyncio
    async def test_full_service_binding_workflow(self, mock_complete_setup):
        """Test complete workflow from service discovery to execution"""
        setup = mock_complete_setup

        # Setup mock responses
        setup["platform_client"].gateway_manager.get_services.return_value = [
            setup["service_data"]
        ]

        # Test service discovery through _get_service
        discovered_service = await service._get_service(
            setup["platform_client"], setup["tool_config"]
        )
        assert discovered_service == setup["service_data"]

        # Test new binding creation
        func, description = await service.new(
            setup["tool_config"], setup["platform_client"]
        )
        assert func == service.run_service
        assert "Integration test service" in description

        # Test service execution
        with patch(
            "itential_mcp.bindings.service.gateway_manager.run_service"
        ) as mock_run:
            # Use Mock without spec to avoid AsyncMock creation
            mock_result = Mock()
            mock_run.return_value = mock_result

            result = await service.run_service(
                setup["context"],
                _tool_config=setup["tool_config"],
                input_params={"input": "test"},
            )

            assert result == mock_result
            mock_run.assert_called_once_with(
                setup["context"],
                name="integration-service",
                cluster="integration-cluster",
                input_params={"input": "test"},
            )

    @pytest.mark.asyncio
    async def test_error_propagation_throughout_workflow(self, mock_complete_setup):
        """Test that errors propagate correctly through the workflow"""
        setup = mock_complete_setup

        # Test service not found propagates through all functions
        setup["platform_client"].gateway_manager.get_services.return_value = []

        # Should fail at _get_service level
        with pytest.raises(exceptions.NotFoundError):
            await service._get_service(setup["platform_client"], setup["tool_config"])

        # Should fail at new level
        with pytest.raises(exceptions.NotFoundError):
            await service.new(setup["tool_config"], setup["platform_client"])

        # Should fail at run_service level
        with pytest.raises(exceptions.NotFoundError):
            await service.run_service(
                setup["context"], _tool_config=setup["tool_config"]
            )


class TestEdgeCases:
    """Test cases for edge cases and boundary conditions"""

    @pytest.mark.asyncio
    async def test_service_with_unicode_metadata(self):
        """Test handling of services with unicode characters in metadata"""
        platform_client = AsyncMock(spec=PlatformClient)
        platform_client.gateway_manager = AsyncMock()

        @dataclass
        class MockTool:
            name: str = "测试服务"
            tool_name: str = "unicode_tool"

        tool_config = MockTool()

        unicode_service = {
            "service_metadata": {
                "name": "测试服务",
                "location": "集群-1",
                "description": "Unicode test service with émojis 🚀",
                "decorator": {"说明": "中文属性"},
            }
        }

        platform_client.gateway_manager.get_services.return_value = [unicode_service]

        result = await service._get_service(platform_client, tool_config)
        assert result == unicode_service

        func, description = await service.new(tool_config, platform_client)
        assert "Unicode test service with émojis 🚀" in description
        assert "中文属性" in description

    @pytest.mark.asyncio
    async def test_service_with_very_large_decorator(self):
        """Test handling of services with very large decorator schemas"""
        platform_client = AsyncMock(spec=PlatformClient)
        platform_client.gateway_manager = AsyncMock()

        @dataclass
        class MockTool:
            name: str = "large-schema-service"
            tool_name: str = "large_tool"

        tool_config = MockTool()

        # Create a large decorator schema
        large_decorator = {
            "type": "object",
            "properties": {
                f"property_{i}": {
                    "type": "string",
                    "description": f"Property number {i}",
                }
                for i in range(1000)
            },
        }

        large_service = {
            "service_metadata": {
                "name": "large-schema-service",
                "location": "cluster-1",
                "description": "Service with large schema",
                "decorator": large_decorator,
            }
        }

        platform_client.gateway_manager.get_services.return_value = [large_service]

        func, description = await service.new(tool_config, platform_client)

        assert func == service.run_service
        assert isinstance(description, str)
        assert len(description) > 1000  # Should be quite large
        assert "property_0" in description
        assert "property_999" in description
