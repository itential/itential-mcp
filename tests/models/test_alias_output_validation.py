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
