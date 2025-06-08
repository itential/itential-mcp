# Copyright (c) 2025 Itential, Inc
# GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)

from fastmcp import Context

async def workflow_id_to_name(ctx: Context, workflow_id: str) -> str:
    """
    Retrieves the workflow name for the specified workflow id

    This function will attempt to get the name of a workflow based on the
    specified workflow id.   The function will cache the workflow name
    to avoid uncessary lookups.

    Args:
        ctx (Context): The FastMCP Context object

        workflow_id (str): The workflow ID to find the name for

    Returns:
        str: The workflow name based on the specified workflow ID

    Raises:
        None
    """
    cache = ctx.request_context.lifespan_context.get("cache")

    value = cache.get(f"/workflows/{workflow_id}")
    if value is not None:
        return value

    client = ctx.request_context.lifespan_context.get("client")
    res = await client.get(
        "/automation-studio/workflows",
        params={"equals[_id]": workflow_id}
    )

    data = res.json()
    value = data["items"][0]["name"]

    cache.put(f"/workflows/{workflow_id}", value)

    return value


async def account_id_to_username(ctx: Context, account_id: str) -> str:
    """
    Retrieves the username for an account id

    This function will take an account id and use it to look up the username
    associated with it.  The function will cache the username value to
    avoid making duplicate calls to the server.

    Args:
        ctx (Context): The FastMCP Context object

        acccount_id (str): The ID of the account to lookup and return the
            username for

    Returns:
        str: The username assoicated with the account id

    Raises:
        None
    """
    cache = ctx.request_context.lifespan_context.get("cache")

    value = cache.get(f"/accounts/{account_id}")
    if value is not None:
        return value

    client = ctx.request_context.lifespan_context.get("client")

    res = await client.get(f"/authorization/accounts/{account_id}")

    value = res.json()["username"]

    cache.put(f"/accounts/{account_id}", value)

    return value


async def transformation_id_to_name(ctx: Context, jst_id: str) -> str:
    """
    Retrieves the transformation name for the specified transformation id

    This function will attempt to get the name of a transformation based on the
    specified transformation id.   The function will cache the transformation
    name to avoid uncessary lookups.

    Args:
        ctx (Context): The FastMCP Context object

        jst_id (str): The transformation ID to find the name for

    Returns:
        str: The transformation name based on the specified transformation ID

    Raises:
        None
    """
    cache = ctx.request_context.lifespan_context.get("cache")

    value = cache.get(f"/transformations/{jst_id}")
    if value is not None:
        return value

    client = ctx.request_context.lifespan_context.get("client")
    res = await client.get(f"/transformations/{jst_id}")

    data = res.json()
    value = data["name"]

    cache.put(f"/transformations/{jst_id}", value)

    return value


async def resource_name_to_id(ctx: Context, name: str) -> str:
    """
    Retrieves the resource id for the specified resource name

    This function will attempt to get the id of a resource based on the
    specified resource name.   The function will cache the resource id
    to avoid uncessary lookups.

    Args:
        ctx (Context): The FastMCP Context object

        name (str): The resource name to find the reosurce ID for

    Returns:
        str: The resource ID of the resource based on the resource name

    Raises:
        ValueError: If the specific resource name could not be found on
            the server
    """
    cache = ctx.request_context.lifespan_context.get("cache")

    value = cache.get(f"/resources/{name}")
    if value is not None:
        return value

    client = ctx.request_context.lifespan_context.get("client")
    res = await client.get(
        "/lifecycle-manager/resources",
        params={"equals[name]": name}
    )

    data = res.json()
    if data["metadata"]["total"] != 1:
        raise ValueError(f"error locating resouce {name}")

    value = data["data"][0]["_id"]

    cache.put(f"/resources/{name}", value)

    return value


