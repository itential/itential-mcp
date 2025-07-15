# Copyright (c) 2025 Itential, Inc
# GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)

from typing import Annotated

from pydantic import Field

from fastmcp import Context


__tags__ = ("configuration_manager",)


async def describe_compliance_report(
    ctx: Annotated[Context, Field(
        description="The FastMCP Context object"
    )],
    report_id: Annotated[str, Field(
        description="The ID of the report to describe"
    )]
) -> dict:
    """
    Retrieve detailed compliance report results from Itential Platform.

    Compliance reports contain the results of executing compliance plans against
    network devices, showing configuration validation outcomes, rule violations,
    and compliance status for each checked device.

    Args:
        ctx (Context): The FastMCP Context object
        report_id (str): Unique identifier of the compliance report to retrieve

    Returns:
        dict: Compliance report details containing validation results, device
            compliance status, rule violations, and configuration analysis from
            running compliance checks against network infrastructure
    """
    await ctx.info("inside describe_compliance_report(...)")

    client = ctx.request_context.lifespan_context.get("client")

    res = await client.get(
        f"/configuration_manager/compliance_reports/details/{report_id}"
    )

    return res.json()
