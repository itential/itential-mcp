# Copyright (c) 2025 Itential, Inc
# GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)

from fastmcp import Context


async def describe_compliance_report(ctx: Context, report_id: str) -> dict:
    """
    Retrieve the compliance report from the server

    Args:
        ctx (Context): The FastMCP Context object

        report_id (str): The unique report identifier

    Returns:
        dict: A Python dict object that represents the output from running a
            compliance report against devices in the infrastructure

    Raises:
        None
    """

    await ctx.info("inside describe_compliance_report(...)")

    client = ctx.request_context.lifespan_context.get("client")

    res = await client.get(
        f"/configuration_manager/compliance_reports/details/{report_id}"
    )

    return res.json()
