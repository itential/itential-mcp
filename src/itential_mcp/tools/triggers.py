# Copyright (c) 2025 Itential, Inc
# GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)

from fastmcp import Context


async def get_trigger_endpoints(ctx: Context) -> list[dict]:
    """
    Get trigger endpoints from the Itential Platform

    Itential Platform provides a mechanism to add one or more triggers to a
    automation job in Operations Manager.  Different trigger types offer
    different ways to launch a job.   This function will retrieve all of
    the defined triggers of type `endpoint` and return them as a list
    of dict objects

    Args:
        ctx (Context): The FastMCP Context object

    Returns:
        list[dict]: A Python list of dict objects that represent the available
            workflows found on the server.

    Raises:
        None
    """

    await ctx.info("inside get_trigger_endpoints(...)")

    client = ctx.request_context.lifespan_context.get("client")

    skip = 0
    limit = 100

    params = {"limit": limit}

    results = list()

    while True:
        params.update({
            "skip": skip,
            "equalsField": "type",
            "equals": "endpoint",
        })

        res = await client.get("/operations-manager/triggers", params=params)

        data = res.json()

        results.extend(data["data"])

        if len(results) == data["metadata"]["total"]:
            break

        skip += limit

    return results
