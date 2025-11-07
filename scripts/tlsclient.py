# mcp_streamable_http_client.py
import argparse
import asyncio
import json
import typing as t
from datetime import timedelta
import contextlib

import httpx
from mcp.client.session import ClientSession
from mcp.client.streamable_http import streamablehttp_client
from mcp.shared.exceptions import McpError
from mcp.types import Implementation

JSON = t.Dict[str, t.Any]


class MCPClient:
    """
    Minimal MCP client for Streamable HTTP transport with TLS using the official MCP Python SDK.
    Implements:
      - initialize
      - tools/list
      - tools/call
    Supports:
      - JSON responses
      - SSE ("text/event-stream") streaming responses
      - Session management via Mcp-Session-Id header
    """

    def __init__(
        self,
        base_url: str,
        *,
        verify: t.Union[str, bool, None] = True,        # CA bundle path or True/False
        cert: t.Optional[t.Tuple[str, str]] = None,     # (cert_file, key_file) for mTLS
        auth_header: t.Optional[str] = None,            # e.g., "Bearer <token>"
        timeout: float = 60.0,
        sse_read_timeout: float = 300.0,
    ):
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self.sse_read_timeout = sse_read_timeout
        self.verify = verify
        self.cert = cert

        # Build headers
        self.headers: t.Dict[str, str] = {
            "Accept": "application/json, text/event-stream",
            "Content-Type": "application/json",
        }
        if auth_header:
            self.headers["Authorization"] = auth_header

    def _create_httpx_client_factory(
        self,
        headers: t.Optional[t.Dict[str, str]] = None,
        timeout: t.Optional[httpx.Timeout] = None,
        auth: t.Optional[httpx.Auth] = None,
    ) -> httpx.AsyncClient:
        """Create httpx client with TLS configuration matching MCP SDK signature."""
        # Merge provided headers with our headers
        merged_headers = self.headers.copy()
        if headers:
            merged_headers.update(headers)

        # Use provided timeout or our default
        client_timeout = timeout or httpx.Timeout(self.timeout)

        return httpx.AsyncClient(
            timeout=client_timeout,
            verify=self.verify,
            cert=self.cert,
            headers=merged_headers,
            auth=auth,
            follow_redirects=True,  # MCP default
        )

    @contextlib.asynccontextmanager
    async def connect_session(
        self,
        client_name: str = "mcp-python-client",
        client_version: str = "0.1.0",
    ) -> t.AsyncIterator[ClientSession]:
        """Connect and yield an active MCP session."""
        client_info = Implementation(name=client_name, version=client_version)

        async with streamablehttp_client(
            url=self.base_url,
            headers=self.headers,
            timeout=timedelta(seconds=self.timeout),
            sse_read_timeout=timedelta(seconds=self.sse_read_timeout),
            httpx_client_factory=self._create_httpx_client_factory,
        ) as transport:
            read_stream, write_stream, _ = transport
            async with ClientSession(
                read_stream, write_stream, client_info=client_info
            ) as session:
                yield session

    async def initialize(self, *, client_name="mcp-python-client", client_version="0.1.0") -> JSON:
        """Initialize the MCP session."""
        async with self.connect_session(client_name, client_version) as session:
            result = await session.initialize()
            return result.model_dump() if result else {}

    async def list_tools(self) -> JSON:
        """List available tools."""
        async with self.connect_session() as session:
            await session.initialize()
            result = await session.list_tools()
            return result.model_dump() if result else {"tools": []}

    async def call_tool(self, *, name: str, arguments: JSON) -> JSON:
        """Call a tool."""
        async with self.connect_session() as session:
            await session.initialize()
            result = await session.call_tool(name=name, arguments=arguments)
            return result.model_dump() if result else {}


async def main(url: str):
    """
    Example run:
      - Connect to specified MCP URL (TLS)
      - List tools
      - Call a tool named "get_adapters"
    """
    client = MCPClient( url, verify=False)

    try:
        init = await client.initialize()
        print("Initialized:", json.dumps(init, indent=2))

        tools = await client.list_tools()
        print("Tools:", json.dumps(tools, indent=2))

        # Change this to the tool your server exposes
        result = await client.call_tool(name="get_adapters", arguments={})
        print("get_adapters() result:", json.dumps(result, indent=2))

    except Exception as e:
        print(f"Connection failed: {e}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="MCP Streamable HTTP Client with TLS support")
    parser.add_argument("--url", default="https://localhost:8000/mcp", help="MCP server URL (e.g., https://localhost:8000/mcp)")

    args = parser.parse_args()
    asyncio.run(main(args.url))
