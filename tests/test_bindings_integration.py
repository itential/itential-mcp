# Copyright (c) 2025 Itential, Inc
# GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

"""In-process regression tests for dynamic tool bindings.

These tests build a real ``Server`` from a real ``Config`` that contains one
``EndpointTool`` and one ``ServiceTool``, register the bindings with a real
FastMCP instance, and exercise them through an in-process ``Client``. Only the
Itential Platform is faked.
"""

from __future__ import annotations

from contextlib import asynccontextmanager
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
import pytest_asyncio
from fastmcp import Client
from fastmcp.exceptions import ToolError
from mcp.shared.exceptions import MCPError

from itential_mcp import config
from itential_mcp.models.gateway_manager import RunServiceResponse
from itential_mcp.models.operations_manager import StartWorkflowResponse
from itential_mcp.server import server as server_module


ENDPOINT_TOOL_NAME = "run_endpoint_binding"
SERVICE_TOOL_NAME = "run_service_binding"


def _workflow_response() -> StartWorkflowResponse:
    return StartWorkflowResponse(
        object_id="job-123",
        name="my-workflow",
        description="A workflow",
        tasks={},
        status="running",
        metrics={"start_time": "2026-01-01T00:00:00Z", "user": "admin"},
    )


def _service_response() -> RunServiceResponse:
    return RunServiceResponse(
        stdout="hello",
        stderr=None,
        return_code=0,
        start_time="2026-01-01T00:00:00Z",
        end_time="2026-01-01T00:00:01Z",
        elapsed_time=1.0,
    )


def _make_config() -> config.Config:
    return config.Config(
        tools=[
            config.EndpointTool(
                name="my-trigger",
                tool_name=ENDPOINT_TOOL_NAME,
                type="endpoint",
                automation="my-automation",
            ),
            config.ServiceTool(
                name="my-service",
                tool_name=SERVICE_TOOL_NAME,
                type="service",
                cluster="cluster-1",
            ),
        ]
    )


def _make_platform_client() -> MagicMock:
    """Build a fake platform client covering the lookups bindings perform."""

    def fake_get(url, params=None):
        res = MagicMock()
        if "automations" in url:
            res.json.return_value = {
                "data": [{"_id": "auto-1", "name": "my-automation"}]
            }
        else:
            res.json.return_value = {
                "data": [
                    {
                        "name": "my-trigger",
                        "description": "Endpoint description",
                        "schema": {"type": "object"},
                        "routeName": "my-route",
                    }
                ]
            }
        return res

    platform_client = MagicMock()
    platform_client.client.get = AsyncMock(side_effect=fake_get)
    platform_client.gateway_manager.get_services = AsyncMock(
        return_value=[
            {
                "service_metadata": {
                    "name": "my-service",
                    "location": "cluster-1",
                    "description": "Service description",
                    "decorator": {"type": "object"},
                }
            }
        ]
    )
    return platform_client


@pytest_asyncio.fixture
async def bound_server():
    """Yield a real, fully initialized Server with both bindings registered."""
    platform_client = _make_platform_client()

    @asynccontextmanager
    async def fake_platform_client():
        yield platform_client

    @asynccontextmanager
    async def fake_lifespan(mcp):
        yield {"client": platform_client}

    with (
        patch("itential_mcp.bindings.PlatformClient", fake_platform_client),
        patch.object(server_module, "lifespan", fake_lifespan),
        patch.object(server_module, "PlatformClient", fake_platform_client),
    ):
        srv = server_module.Server(_make_config())
        # Reproduces the FastMCP 4 startup crash (unsupported exclude_args)
        # on unfixed code.
        await srv.__init_server__()
        await srv.__init_bindings__()
        yield srv


class TestDynamicBindingsIntegration:
    """End-to-end tests of dynamic bindings against a real FastMCP server."""

    @pytest.mark.asyncio
    async def test_schemas_hide_internal_parameters(self, bound_server):
        async with Client(bound_server.mcp) as client:
            tools = {t.name: t for t in await client.list_tools()}

        assert ENDPOINT_TOOL_NAME in tools
        assert SERVICE_TOOL_NAME in tools

        for tool in tools.values():
            props = tool.input_schema.get("properties", {})
            assert "_tool_config" not in props
            assert "ctx" not in props
            assert "_tool_config" not in tool.input_schema.get("required", [])

        assert set(tools[ENDPOINT_TOOL_NAME].input_schema["properties"]) == {"data"}
        assert set(tools[SERVICE_TOOL_NAME].input_schema["properties"]) == {
            "input_params"
        }

    @pytest.mark.asyncio
    async def test_output_schemas_have_real_properties(self, bound_server):
        async with Client(bound_server.mcp) as client:
            tools = {t.name: t for t in await client.list_tools()}

        for name, field in (
            (ENDPOINT_TOOL_NAME, "object_id"),
            (SERVICE_TOOL_NAME, "return_code"),
        ):
            schema = tools[name].output_schema
            assert schema is not None
            assert field in str(schema), schema
            assert schema != {"type": "object", "properties": {}}

    @pytest.mark.asyncio
    async def test_endpoint_call_uses_bound_config(self, bound_server):
        with patch(
            "itential_mcp.bindings.endpoint.operations_manager.start_workflow",
            new=AsyncMock(return_value=_workflow_response()),
        ) as mock_start:
            async with Client(bound_server.mcp) as client:
                result = await client.call_tool(ENDPOINT_TOOL_NAME, {"data": {"a": 1}})

        # Regression: the result must not be filtered down to an empty object.
        payload = result.structured_content
        payload = payload.get("result", payload)  # union return is wrapped
        assert payload["object_id"] == "job-123"
        assert payload["name"] == "my-workflow"

        mock_start.assert_awaited_once()
        assert mock_start.await_args.kwargs == {
            "route_name": "my-route",
            "data": {"a": 1},
        }

    @pytest.mark.asyncio
    async def test_service_call_uses_bound_config(self, bound_server):
        with patch(
            "itential_mcp.bindings.service.gateway_manager.run_service",
            new=AsyncMock(return_value=_service_response()),
        ) as mock_run:
            async with Client(bound_server.mcp) as client:
                result = await client.call_tool(
                    SERVICE_TOOL_NAME, {"input_params": {"b": 2}}
                )

        # Regression: the result must not be filtered down to an empty object.
        assert result.structured_content["stdout"] == "hello"
        assert result.structured_content["return_code"] == 0

        mock_run.assert_awaited_once()
        assert mock_run.await_args.kwargs == {
            "name": "my-service",
            "cluster": "cluster-1",
            "input_params": {"b": 2},
        }

    @pytest.mark.asyncio
    @pytest.mark.parametrize("tool_name", [ENDPOINT_TOOL_NAME, SERVICE_TOOL_NAME])
    async def test_tool_config_argument_is_rejected(self, bound_server, tool_name):
        async with Client(bound_server.mcp) as client:
            with pytest.raises((ToolError, MCPError), match="_tool_config"):
                await client.call_tool(tool_name, {"_tool_config": {"name": "evil"}})
