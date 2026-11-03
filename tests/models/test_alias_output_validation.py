# Copyright (c) 2025 Itential, Inc
# GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

"""End-to-end check that aliased models pass output validation on FastMCP 4.

Drives real tools through an in-process Server and ``fastmcp.Client`` with a
mocked platform client that returns alias-keyed payloads, and asserts the
structured content keeps the alias names (identical to FastMCP 3 wire keys).
"""

from __future__ import annotations

from contextlib import asynccontextmanager
from typing import Any
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from fastmcp import Client

from itential_mcp.config.models import AuthConfig, Config, ServerConfig
from itential_mcp.server import server as server_module

_VERSIONS = {
    k: "1"
    for k in (
        "node acorn ada ares brotli cjs_module_lexer cldr icu llhttp modules "
        "napi nghttp2 openssl simdutf tz undici unicode uv uvwasi v8 zlib"
    ).split()
}


def _platform_client() -> MagicMock:
    client = MagicMock()

    client.health.get_status_health = AsyncMock(
        return_value={
            "host": "h",
            "serverId": "s1",
            "timestamp": 1,
            "apps": "RUNNING",
            "adapters": "RUNNING",
            "services": [],
        }
    )
    client.health.get_system_health = AsyncMock(
        return_value={
            "arch": "x64",
            "release": "r",
            "uptime": 1.0,
            "freemem": 100,
            "totalmem": 200,
            "loadavg": [0.1, 0.2, 0.3],
            "cpus": [],
        }
    )
    client.health.get_server_health = AsyncMock(
        return_value={
            "version": "1",
            "release": "r",
            "arch": "x64",
            "platform": "linux",
            "versions": _VERSIONS,
            "memoryUsage": {"heapTotal": 1, "heapUsed": 2, "arrayBuffers": 3},
            "uptime": 1.0,
            "pid": 1,
        }
    )
    client.health.get_applications_health = AsyncMock(return_value={"results": []})
    client.health.get_adapters_health = AsyncMock(return_value={"results": []})

    client.mop.get_command_templates = AsyncMock(
        return_value=[{"_id": "abc", "name": "tmpl", "passRule": True}]
    )

    client.inventory_manager.describe_inventory = AsyncMock(
        return_value={"_id": "inv1", "name": "inv", "nodeCount": 0}
    )

    client.operations_manager.describe_job = AsyncMock(
        return_value={
            "_id": "job1",
            "name": "job",
            "description": "d",
            "type": "automation",
            "tasks": {},
            "status": "complete",
            "metrics": {},
            "last_updated": "2025-01-01",
        }
    )
    return client


_CASES: list[tuple[str, dict[str, Any], tuple[Any, ...], str]] = [
    ("get_health", {}, ("system", "freemem"), "free_mem"),
    ("get_command_templates", {}, ("templates", 0, "_id"), "id"),
    ("describe_inventory", {"name": "inv"}, ("_id",), "object_id"),
    ("describe_job", {"object_id": "job1"}, ("_id",), "object_id"),
]


def _dig(data: Any, path: tuple[Any, ...]) -> Any:
    for key in path:
        data = data[key]
    return data


@pytest.mark.asyncio
@pytest.mark.parametrize("mode", ["legacy", "auto"])
@pytest.mark.parametrize(
    "tool,args,path,field_name", _CASES, ids=[c[0] for c in _CASES]
)
async def test_alias_keys_survive_output_validation(mode, tool, args, path, field_name):
    platform = _platform_client()

    @asynccontextmanager
    async def fake_lifespan(mcp):
        yield {"client": platform}

    config = Config(
        server=ServerConfig(transport="stdio", log_level="INFO"),
        auth=AuthConfig(type="none"),
    )

    with (
        patch("itential_mcp.server.auth.build_auth_provider", return_value=None),
        patch.object(server_module, "lifespan", fake_lifespan),
    ):
        server = server_module.Server(config)
        async with server:
            async with Client(server.mcp, mode=mode) as client:
                result = await client.call_tool(tool, args)

    assert result.is_error is False
    data = result.structured_content
    assert data is not None
    assert _dig(data, path) is not None
    # The python field name must not leak into the wire payload.
    assert field_name not in _dig(data, path[:-1])


_SESSION_EVENTS = [
    {
        "eventId": "e1",
        "sequenceNumber": 1,
        "timestamp": 1748779200000,
        "text": "calling a tool",
        "category": "AGENT_REASONING",
        "type": "inference-succeeded",
        "data": {
            "stopReason": "tool_use",
            "durationMs": 12,
            "tokenUsage": {"inputTokens": 5, "outputTokens": 2},
        },
    },
    {
        "eventId": "tc1",
        "sequenceNumber": None,
        "timestamp": 1748779200500,
        "text": "",
        "category": "TOOL_CALLED",
        "type": "tool-execution",
        "data": {
            "toolName": "demo_tool",
            "toolType": "method",
            "summary": "did a thing",
            "status": "succeeded",
            "durationMs": 4,
            "errorMessage": None,
        },
    },
    {
        "eventId": "pend",
        "sequenceNumber": 9,
        "timestamp": 1748779200800,
        "text": "",
        "category": "AGENT_REASONING",
        "type": "inference-pending",
        "data": {},
    },
    {
        "eventId": "e2",
        "sequenceNumber": 2,
        "timestamp": 1748779201000,
        "text": "tool output",
        "category": "TOOL_EXECUTION",
        "data": {},
    },
    {
        "eventId": "e3",
        "sequenceNumber": 3,
        "timestamp": 1748779202000,
        "text": "final answer",
        "category": "AGENT_REASONING",
        "data": {"stopReason": "end_turn"},
    },
]


@pytest.mark.asyncio
@pytest.mark.parametrize("mode", ["legacy", "auto"])
@pytest.mark.parametrize(
    "include_all,expected", [(False, ["e3"]), (True, ["e1", "e3"])]
)
async def test_describe_session_include_all_events_output_validation(
    mode, include_all, expected
):
    platform = _platform_client()
    platform.agent_session_manager.get_session = AsyncMock(
        return_value={"sessionId": "s1", "status": "COMPLETE"}
    )
    platform.agent_session_manager.get_session_messages = AsyncMock(
        return_value=_SESSION_EVENTS
    )

    @asynccontextmanager
    async def fake_lifespan(mcp):
        yield {"client": platform}

    config = Config(
        server=ServerConfig(transport="stdio", log_level="INFO"),
        auth=AuthConfig(type="none"),
    )

    args: dict[str, Any] = {"session_id": "s1"}
    if include_all:
        args["include_all_events"] = True

    with (
        patch("itential_mcp.server.auth.build_auth_provider", return_value=None),
        patch.object(server_module, "lifespan", fake_lifespan),
    ):
        server = server_module.Server(config)
        async with server:
            async with Client(server.mcp, mode=mode) as client:
                result = await client.call_tool("describe_session", args)

    assert result.is_error is False
    data = result.structured_content
    assert data is not None
    assert [e["event_id"] for e in data["reasoning_events"]] == expected
    assert data["output"] == "final answer"
    assert data["reasoning_events"][-1]["stop_reason"] == "end_turn"
    if include_all:
        first = data["reasoning_events"][0]
        assert first["duration_ms"] == 12
        assert first["input_tokens"] == 5
        assert first["output_tokens"] == 2
        assert first["tool_calls"][0]["tool_name"] == "demo_tool"
        assert first["tool_calls"][0]["status"] == "succeeded"
    else:
        assert data["reasoning_events"][0]["tool_calls"] == []
