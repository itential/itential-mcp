# Developer Guide

The developer guide provides information for anyone that is looking to add
additional functionality to the `itential-mcp` project.   Generally the most
common thing would be to add additional tools to the application.

## Adding a new tool

Adding a new tools is realitively easy as most of the code for exposing a tool
is handled by the server code.

Typically a tool is a representation of an Itential Platform server API route
although it could be multiple routes in some cases.  To add a new tool, simply
create a new module in the `tools/` folder or add a new function to an existing
module.

To expose a tool, simply write an async function in the `tools/<module>.py`
file that returns some result.  The function must return either a str value or
a Python object that can be JSON serialized such as a list or dict.

In the new function signature, add an argument that is annotated as a Context
object which will give you access to the Itential Platform client.

For instance, creating a new function for getting the list of all adapters on
the server.  The function might be called `get_adapters()` and the function
signature would look like the following:

```python
from fastmcp import Context

async def get_adapters(ctx: Context) -> list:
    """
    Get list of all adapters on the server
    """
```

In the above example, the argument `ctx` will receive the Context object.  The
argument name can be any name but the `Context` annotation must be there.

When the function is called, the Itential Platform client can be accessed from
the `Context` object.

```python
from fastmcp import Context

async def get_adapters(ctx: Context) -> list:
    """
    Get list of all adapters on the server
    """
    client = ctx.request_context.lifespan_context.get("client")
```

Once you have client, you can now send API requests the to the Itential
Platform API.

```python
from fastmcp import Context

async def get_adapters(ctx: Context) -> list:
    """
    Get list of all adapters on the server
    """
    client = ctx.request_context.lifespan_context.get("client")
    res = client.get("/adapters")
    return res.json()["results"]
```

The above code is the minimum function required to deliver a new tool to the
MCP server.

