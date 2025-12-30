# Copyright (c) 2025 Itential, Inc
# GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from typing import Annotated

from pydantic import Field

from fastmcp import Context

from itential_mcp.models import compliance_plans as models


__tags__ = ("configuration_manager",)


async def get_compliance_plans(
    ctx: Annotated[Context, Field(description="The FastMCP Context object")],
) -> models.GetCompliancePlansResponse:
    """
    Get all compliance plans from Itential Platform.

    Compliance plans define configuration validation rules and checks that can be
    executed against network devices to ensure they meet organizational standards.

    Args:
        ctx (Context): The FastMCP Context object

    Returns:
        models.GetCompliancePlansResponse: Response containing list of compliance plan objects

    Raises:
        Exception: If there is an error retrieving compliance plans from the platform
    """
    await ctx.info("inside get_compliance_plans(...)")
    client = ctx.request_context.lifespan_context.get("client")
    results = client.configuration_manager.get_compliance_plans()
    return models.GetCompliancePlansResponse(plans=results)


async def run_compliance_plan(
    ctx: Annotated[Context, Field(description="The FastMCP Context object")],
    name: Annotated[str, Field(description="The name of the compliance plan to run")],
) -> models.RunCompliancePlanResponse:
    """
    Execute a compliance plan against network devices.

    Compliance plans validate device configurations against organizational standards
    by running predefined checks and rules. This function starts a compliance plan
    execution and returns the running instance details.

    Args:
        ctx (Context): The FastMCP Context object
        name (str): Case-sensitive name of the compliance plan to run

    Returns:
        models.RunCompliancePlanResponse: Response containing running compliance plan instance details

    Raises:
        ValueError: If the specified compliance plan name is not found
    """
    await ctx.info("inside run_compliance_plan(...)")
    client = ctx.request_context.lifespan_context.get("client")
    data = client.configuration_manager.run_compliance_plan(name=name)
    compliance_instance = models.CompliancePlanInstance(
        id=data["id"],
        name=data["name"],
        description=data["description"],
        jobStatus=data["jobStatus"],
    )
    return models.RunCompliancePlanResponse(instance=compliance_instance)
