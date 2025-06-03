# Copyright (c) 2025 Itential, Inc
# GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)

from fastmcp import Context


async def get_automations(ctx: Context) -> list[dict]:
    """
    Get all automations from the Itential Platform server

    This tool will retreive all configured automations available on the
    Itential Server and return them as a list.   The returned results
    include all of the configured automations.

    Each element in the list includes the following key fields:
        * _id: The unique identifer for the automation
        * componentId: The unique identifier for the component that is
            associated with this automation
        * componentType: The component type associated with this automation.
            Valid component types include `workflows` or `ucm_compliance_plans`
        * created: Timestamp when the automation was created
        * createdBy: The account that created the automation
        * description: Short description of the automation
        * gbac: Accounts and/or groups that have read or write access to the
            automation
        * lastUpdated: Timestamp when the automation was last updated
        * lastUpdatedBy: Account that last updated the automation
        * name: The name of the automation

    Args:
        ctc (Context): The FastMCP Context object

    Returns:
        list[dict]: A list of Python dict objects where each element represents
            a configured automation in Itential Platform

    Raises:
        None
    """
    await ctx.info("inside get_automations(...)")

    client = ctx.request_context.lifespan_context.get("client")

    limit = 100
    skip = 0

    params = {"limit": limit}

    results = list()

    while True:
        params["skip"] = skip

        res = await client.get(
            "/operations-manager/automations",
            params=params
        )

        data = res.json()
        metadata = data["metadata"]

        results.extend(data.get("data") or list())

        if len(results) == metadata["total"]:
            break

        skip += limit

    return results
