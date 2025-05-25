# Copyright (c) 2025 Itential, Inc
# GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)

from fastmcp import Context


async def get_devices(ctx: Context) -> list[dict]:
    """
    Retrieve all devies known to Itential Platform

    Itential Platform will federate device information from multiple
    sources and make it available to workflows for performing tasks
    against physical devices.  This function will query Itential Platform
    and return all of the devices known to it.

    Args:
        ctx (Context): The FastMCP Context object

    Returns:
        dict: A Python list of dict objects that reprsesent all of the devices
            knownn to Itential Platform

    Raises:
        None
    """
    await ctx.info("inside get_devices(...)")

    client = ctx.request_context.lifespan_context.get("client")

    limit = 100
    start = 0

    results = list()

    while True:
        body = {
            "options": {
                "order": "ascending",
                "sort": [{"name": 1}],
                "start": start,
                "limit": limit

            }
        }

        res = await client.post(
            "/configuration_manager/devices",
            json=body,
        )

        data = res.json()

        results.extend(data["list"])

        if len(results) == data["total"]:
            break

        start += limit

    return results
