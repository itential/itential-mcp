# Tags

The Itential MCP server supports the use of both include and exclude tags to
control which tools are made available to clients.   Tags can be used in
conjunction with different Itential Platform authentications to create
customzied MCP servers.  This allows operators to constrain what a given MCP
server is allowed to perform against the infrastructure.

When adding a tool to the Itential MCP server, the tool name is the same as the
function name.   For every tool registered with the server, a tag is included
with the tool name.  This allows for every granular level of control.  Specific
tools can easily be excluded or included simply by adding the tool name to the
appropriate configuration option or command line option.

There are standard tags that are also recognized in the Itential MCP server.
by default, all tools with the tag `experimental` or `beta` are excluded from
being registered by default.   This behavior can be changed by modifying the
exclude tags configuration option.

# Tag Groups

The server now supports tag groups.  Tag groups will apply a tag to a group
of tools so they can all be excluded or included with a single tag.  See the
[tools](tools.md) file for a list of all avaiable groups and which tools
are assoicated with those groups.

To add tags to function there is a new decorator available.   For instance,
this below example will add the tags "public", "released" to the tool call
`my_new_tool`.

```python
from fastmcp import Context

from itential_mcp.toolutils import tags

tags("public", "released")
async def my_new_tool(ctx: Context) -> dict:
    """
    Description of what the tool does

    Args:
        ctx (Context): The FastMCP Context object

    Returns:
        dict: The response data

    Raises:
        None
    """
    # Get the platform client
    client = ctx.request_context.lifespan_context.get("client")

    # Make API requests
    res = await client.get("/your/api/path")

    # Return JSON-serializable results
    return res.json()
```

Using the `tags` decorator will attach the tags `public` and `released` to the
tool and those tags can now be used in include and/or exclude tags
configuration options to control tool registration with the server.


