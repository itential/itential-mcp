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
        ValueError: If the specified workflow id cannot be found
    """
    cache = ctx.request_context.lifespan_context.get("cache")

    value = cache.get(f"/workflows/{workflow_id}")
    if value is not None:
        return value

    client = ctx.request_context.lifespan_context.get("client")

    res = await client.get(
        "/automation-studio/workflows",
        params={
            "equals[_id]": workflow_id,
            "include": "_id,name",
        }
    )

    data = res.json()

    if data["total"] == 0:
        raise ValueError(f"unable to find workflow with id {workflow_id}")

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

    limit = 100
    skip = 0
    cnt = 0

    params = {"limit": limit}

    while True:
        params["skip"] = skip

        res = await client.get(
            "/authorization/accounts",
            params=params
        )

        data = res.json()
        results = data["results"]

        for item in results:
            if item["_id"] == account_id:
                value = item["username"]
                break

        cnt += len(results)

        if cnt == data["total"]:
            break

        skip += limit

    if value is None:
        raise ValueError(f"unable to find account with id {account_id}")

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


async def group_id_to_name(ctx: Context, group_id: str) -> str:
    """
    Retrieves the group anme for the specified group id

    This function will attempt to get the group name for the specified
    group ID.

    Args:
        ctx (Context): The FastMCP Context object

        group_id (str): The group ID to find the group name for

    Returns:
        str: The name of the group associated with this group ID

    Raises:
    """
    cache = ctx.request_context.lifespan_context.get("cache")

    value = cache.get(f"/authorization/groups/{group_id}")
    if value is not None:
        return value

    client = ctx.request_context.lifespan_context.get("client")

    res = await client.get(f"/authorization/groups/{group_id}")

    data = res.json()

    value = data["name"]

    cache.put(f"/authorization/groups/{group_id}", value)


async def project_name_to_id(ctx: Context, name: str) -> str:
    """
    Retrieves the project ID for the specified project name

    This function will attempt to find the a project on the Itential
    Server with the name as specified by the name argument.   If the
    project exists, the project ID will be returned.  If the project
    does not exist, an exception will be raised

    Args:
        ctx (Context): The FastMCP Context object

        name (str): The project name to return the ID for

    Returns:
        str: The project ID of the project based on the name

    Raises:
        ValueError: If the specific project name could not be found on
            the server
    """
    cache = ctx.request_context.lifespan_context.get("cache")

    value = cache.get(f"/projects/{name}")
    if value is not None:
        return value

    client = ctx.request_context.lifespan_context.get("client")

    res = await client.get(
        "/automation-studio/projects",
        params={"equals[name]": name}
    )

    data = res.json()
    if data["metadata"]["total"] != 1:
        raise ValueError(f"error locating project {name}")

    value = data["data"][0]["_id"]

    cache.put(f"/projects/{name}", value)

    return value
