# Copyright (c) 2025 Itential, Inc
# GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)

from fastmcp import Context


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
