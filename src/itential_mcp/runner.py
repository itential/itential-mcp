# Copyright (c) 2025 Itential, Inc
# GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)

import json

from typing import Mapping, Any

from fastmcp import Client

from itential_mcp import config
from itential_mcp import server


async def run(tool: str, params: Mapping[str, Any] | None=None) -> None:
    """
    Run the specified tool and return the results

    This function will invoke the tool as identified by the `tool` argument
    and return the results.  Additional paramters can be specified using the
    `params` argument.

    If the tool is not a valid tool name (or has been excluded) this function
    will raise an exception.  Additionally, if any required properties are
    missing or invalid, an exception will be raised.

    The tool function will be invoked and the result will be sent as a JSON
    string to stdout

    Args:
        tool (str): The name of the tool to invoke

        params (dict): The set of properties to pass to the tool as keyword
            arguments when the function is invoked

    Returns:
        None

    Raises:
        ValueError: If the tool does not exist

        ValueError: The one or more required parameters are missing

        ValueError: If there are invalid parameters
    """
    async with Client(server.new(config.get())) as client:
        # Basic server interaction
        if await client.ping() is False:
            raise ValueError("ERROR: cannot reach the server")

        tools = {}

        res = await client.list_tools_mcp()

        for t in res.tools:
            tools[t.name] = t.inputSchema

        kwargs = {
            "arguments": json.loads(params) if params else None
        }

        if tool not in tools:
            raise ValueError(f"invalid tool: {tool}")

        required = tools[tool].get("required") or list()

        if required and set(required).difference((kwargs["arguments"] or {})):
            for item in required:
                if kwargs["arguments"] is None or item not in kwargs["arguments"]:
                    raise ValueError(f"missing required property: {item}")

        if kwargs["arguments"]:
            if set(kwargs["arguments"]).difference(tools[tool]["properties"]):
                for item in kwargs["arguments"]:
                    if item not in tools[tool]["properties"]:
                        raise ValueError(f"invalid argument: {item}")


        # Execute operations
        result = await client.call_tool(tool, **kwargs)

        data = json.loads(result.content[0].text)
        print(f"\n{json.dumps(data, indent=4)}")
