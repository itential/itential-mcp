# Copyright (c) 2025 Itential, Inc
# GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

"""Unit tests for health check routes."""

import pytest
from unittest.mock import patch, MagicMock, AsyncMock

from starlette.requests import Request
from starlette.responses import JSONResponse

from itential_mcp.server import routes


class TestGetHealthz:
    """Test the get_healthz endpoint."""

    @pytest.mark.asyncio
    async def test_get_healthz_success(self):
        """Test healthz endpoint returns 200 OK."""
        request = MagicMock(spec=Request)

        response = await routes.get_healthz(request)

        assert isinstance(response, JSONResponse)
        assert response.status_code == 200

        # Check response content
        content = response.body.decode()
        assert '"status":"ok"' in content

    @pytest.mark.asyncio
    async def test_get_healthz_handles_exceptions(self):
        """Test healthz endpoint handles exceptions gracefully."""
        request = MagicMock(spec=Request)

        # Mock JSONResponse to raise an exception during construction
        with patch("itential_mcp.server.routes.JSONResponse") as mock_json_response:
            # First call raises exception, second call succeeds for error response
            mock_json_response.side_effect = [
                Exception("Test exception"),
                JSONResponse(content={"status": "unhealthy"}, status_code=503),
            ]

            response = await routes.get_healthz(request)

            # Should return the second call (error response)
            assert response.status_code == 503
            content = response.body.decode()
            assert '"status":"unhealthy"' in content

    @pytest.mark.asyncio
    async def test_get_healthz_request_parameter_used(self):
        """Test that the request parameter is properly handled."""
        request = MagicMock(spec=Request)
        request.headers = {"user-agent": "test-agent"}

        response = await routes.get_healthz(request)

        # Should still return success regardless of request content
        assert response.status_code == 200


class TestGetReadyz:
    """Test the get_readyz endpoint."""

    @pytest.mark.asyncio
    async def test_get_readyz_success(self):
        """Test readyz endpoint returns 200 when platform client succeeds."""
        request = MagicMock(spec=Request)

        # Mock PlatformClient to succeed
        with patch("itential_mcp.server.routes.PlatformClient") as mock_client_class:
            mock_client_instance = AsyncMock()
            mock_client_instance.get = AsyncMock(return_value={"status": "ok"})
            mock_client_class.return_value.__aenter__ = AsyncMock(
                return_value=mock_client_instance
            )
            mock_client_class.return_value.__aexit__ = AsyncMock(return_value=None)

            response = await routes.get_readyz(request)

            assert isinstance(response, JSONResponse)
            assert response.status_code == 200

            # Check response content
            content = response.body.decode()
            assert '"status":"ready"' in content

            # Verify platform client was called
            mock_client_instance.get.assert_called_once_with("/whoami")

    @pytest.mark.asyncio
    async def test_get_readyz_platform_client_failure(self):
        """Test readyz endpoint returns 503 when platform client fails."""
        request = MagicMock(spec=Request)

        # Mock PlatformClient to fail
        with patch("itential_mcp.server.routes.PlatformClient") as mock_client_class:
            mock_client_instance = AsyncMock()
            mock_client_instance.get = AsyncMock(
                side_effect=Exception("Connection failed")
            )
            mock_client_class.return_value.__aenter__ = AsyncMock(
                return_value=mock_client_instance
            )
            mock_client_class.return_value.__aexit__ = AsyncMock(return_value=None)

            response = await routes.get_readyz(request)

            assert isinstance(response, JSONResponse)
            assert response.status_code == 503

            # Check response content
            content = response.body.decode()
            assert '"status":"not ready"' in content
            assert '"reason":"Connection failed"' in content

    @pytest.mark.asyncio
    async def test_get_readyz_context_manager_failure(self):
        """Test readyz endpoint handles context manager failures."""
        request = MagicMock(spec=Request)

        # Mock PlatformClient context manager to fail
        with patch("itential_mcp.server.routes.PlatformClient") as mock_client_class:
            mock_client_class.return_value.__aenter__ = AsyncMock(
                side_effect=Exception("Context manager failed")
            )

            response = await routes.get_readyz(request)

            assert isinstance(response, JSONResponse)
            assert response.status_code == 503

            # Check response content
            content = response.body.decode()
            assert '"status":"not ready"' in content
            assert '"reason":"Context manager failed"' in content

    @pytest.mark.asyncio
    async def test_get_readyz_various_exceptions(self):
        """Test readyz endpoint handles various exception types."""
        request = MagicMock(spec=Request)

        exception_types = [
            ConnectionError("Network error"),
            TimeoutError("Request timeout"),
            ValueError("Invalid response"),
            RuntimeError("Runtime error"),
        ]

        for exc in exception_types:
            with patch(
                "itential_mcp.server.routes.PlatformClient"
            ) as mock_client_class:
                mock_client_class.return_value.__aenter__ = AsyncMock(side_effect=exc)

                response = await routes.get_readyz(request)

                assert response.status_code == 503
                content = response.body.decode()
                assert '"status":"not ready"' in content
                assert str(exc) in content


class TestGetLivez:
    """Test the get_livez endpoint."""

    @pytest.mark.asyncio
    async def test_get_livez_success(self):
        """Test livez endpoint returns 200 OK."""
        request = MagicMock(spec=Request)

        response = await routes.get_livez(request)

        assert isinstance(response, JSONResponse)
        assert response.status_code == 200

        # Check response content
        content = response.body.decode()
        assert '"status":"alive"' in content

    @pytest.mark.asyncio
    async def test_get_livez_handles_exceptions(self):
        """Test livez endpoint handles exceptions gracefully."""
        request = MagicMock(spec=Request)

        # Mock JSONResponse to raise an exception during construction
        with patch("itential_mcp.server.routes.JSONResponse") as mock_json_response:
            # First call raises exception, second call succeeds for error response
            mock_json_response.side_effect = [
                Exception("Test exception"),
                JSONResponse(content={"status": "dead"}, status_code=503),
            ]

            response = await routes.get_livez(request)

            # Should return the second call (error response)
            assert response.status_code == 503
            content = response.body.decode()
            assert '"status":"dead"' in content

    @pytest.mark.asyncio
    async def test_get_livez_request_parameter_used(self):
        """Test that the request parameter is properly handled."""
        request = MagicMock(spec=Request)
        request.method = "GET"
        request.url = "http://example.com/status/livez"

        response = await routes.get_livez(request)

        # Should still return success regardless of request content
        assert response.status_code == 200


class TestRoutesIntegration:
    """Integration tests for routes module."""

    @pytest.mark.asyncio
    async def test_all_routes_return_json_response(self):
        """Test that all route functions return JSONResponse objects."""
        request = MagicMock(spec=Request)

        # Mock PlatformClient for readyz test
        with patch("itential_mcp.server.routes.PlatformClient") as mock_client_class:
            mock_client_instance = AsyncMock()
            mock_client_instance.get = AsyncMock(return_value={"status": "ok"})
            mock_client_class.return_value.__aenter__ = AsyncMock(
                return_value=mock_client_instance
            )
            mock_client_class.return_value.__aexit__ = AsyncMock(return_value=None)

            # Test all endpoints
            routes_to_test = [routes.get_healthz, routes.get_readyz, routes.get_livez]

            for route_func in routes_to_test:
                response = await route_func(request)
                assert isinstance(response, JSONResponse)
                assert hasattr(response, "status_code")
                assert hasattr(response, "body")

    @pytest.mark.asyncio
    async def test_all_routes_have_proper_status_codes(self):
        """Test that all routes return appropriate status codes."""
        request = MagicMock(spec=Request)

        # Test successful cases
        with patch("itential_mcp.server.routes.PlatformClient") as mock_client_class:
            mock_client_instance = AsyncMock()
            mock_client_instance.get = AsyncMock(return_value={"status": "ok"})
            mock_client_class.return_value.__aenter__ = AsyncMock(
                return_value=mock_client_instance
            )
            mock_client_class.return_value.__aexit__ = AsyncMock(return_value=None)

            healthz_response = await routes.get_healthz(request)
            readyz_response = await routes.get_readyz(request)
            livez_response = await routes.get_livez(request)

            assert healthz_response.status_code == 200
            assert readyz_response.status_code == 200
            assert livez_response.status_code == 200

    @pytest.mark.asyncio
    async def test_routes_response_format_consistency(self):
        """Test that all routes return consistent JSON format."""
        request = MagicMock(spec=Request)

        # Mock PlatformClient for readyz test
        with patch("itential_mcp.server.routes.PlatformClient") as mock_client_class:
            mock_client_instance = AsyncMock()
            mock_client_instance.get = AsyncMock(return_value={"status": "ok"})
            mock_client_class.return_value.__aenter__ = AsyncMock(
                return_value=mock_client_instance
            )
            mock_client_class.return_value.__aexit__ = AsyncMock(return_value=None)

            responses = [
                await routes.get_healthz(request),
                await routes.get_readyz(request),
                await routes.get_livez(request),
            ]

            for response in responses:
                content = response.body.decode()
                # All should have a status field
                assert '"status"' in content
                # Content should be valid JSON structure
                assert content.startswith('{"')
                assert content.endswith("}")


class TestRoutesErrorConditions:
    """Test error conditions and edge cases for routes."""

    @pytest.mark.asyncio
    async def test_readyz_with_none_request(self):
        """Test readyz endpoint with None request (edge case)."""
        # Even with None request, should not crash
        response = await routes.get_readyz(None)
        assert isinstance(response, JSONResponse)
        # Should handle gracefully, likely returning error status
        assert response.status_code in [200, 503]

    @pytest.mark.asyncio
    async def test_routes_concurrent_calls(self):
        """Test that routes can handle concurrent calls."""
        import asyncio

        request = MagicMock(spec=Request)

        # Mock PlatformClient for readyz test
        with patch("itential_mcp.server.routes.PlatformClient") as mock_client_class:
            mock_client_instance = AsyncMock()
            mock_client_instance.get = AsyncMock(return_value={"status": "ok"})
            mock_client_class.return_value.__aenter__ = AsyncMock(
                return_value=mock_client_instance
            )
            mock_client_class.return_value.__aexit__ = AsyncMock(return_value=None)

            # Run multiple concurrent calls
            tasks = []
            for _ in range(10):
                tasks.extend(
                    [
                        routes.get_healthz(request),
                        routes.get_readyz(request),
                        routes.get_livez(request),
                    ]
                )

            responses = await asyncio.gather(*tasks)

            # All should succeed
            assert len(responses) == 30
            for response in responses:
                assert isinstance(response, JSONResponse)
                assert response.status_code in [200, 503]
