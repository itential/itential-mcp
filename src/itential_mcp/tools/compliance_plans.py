# Copyright (c) 2025 Itential, Inc
# GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)

from typing import Annotated

from pydantic import Field

from fastmcp import Context


__tags__ = ("configuration_manager",)


async def get_compliance_plans(
    ctx: Annotated[Context, Field(
        description="The FastMCP Context object"
    )],
) -> list[dict]:
    """
    Get all compliance plans from Itential Platform.

    Compliance plans define configuration validation rules and checks that can be
    executed against network devices to ensure they meet organizational standards.

    Args:
        ctx (Context): The FastMCP Context object

    Returns:
        list[dict]: List of compliance plan objects with the following fields:
            - id: Unique identifier for the compliance plan
            - name: Compliance plan name
            - description: Plan description
            - throttle: Number of devices checked in parallel during execution
    """
    await ctx.info("inside get_compliance_plans(...)")

    client = ctx.request_context.lifespan_context.get("client")

    limit = 100
    start = 0

    results = list()

    while True:
        body = {
            "name": "",
            "options": {
                "start": start,
                "limit": limit
            }
        }

        res = await client.post(
            "/configuration_manager/search/compliance_plans",
            json=body,
        )

        data = res.json()

        print(data)

        for ele in data["plans"]:
            results.append({
                "id": ele["id"],
                "name": ele["name"],
                "description": ele["description"],
                "throttle": ele["throttle"]
            })

        if len(results) == data["totalCount"]:
            break

        start += limit

    return results


async def run_compliance_plan(
    ctx: Annotated[Context, Field(
        description="The FastMCP Context object"
    )],
    name: Annotated[str, Field(
        description="The name of the compliance plan to run"
    )]
) -> dict:
    """
    Execute a compliance plan against network devices.

    Compliance plans validate device configurations against organizational standards
    by running predefined checks and rules. This function starts a compliance plan
    execution and returns the running instance details.

    Args:
        ctx (Context): The FastMCP Context object
        name (str): Case-sensitive name of the compliance plan to run

    Returns:
        dict: Running compliance plan instance with the following fields:
            - id: Unique identifier for this compliance plan instance
            - name: Name of the compliance plan that was started
            - description: Compliance plan description
            - jobStatus: Current execution status of the compliance plan instance

    Raises:
        ValueError: If the specified compliance plan name is not found
    """
    await ctx.info("inside run_compliance_plan(...)")

    client = ctx.request_context.lifespan_context.get("client")

    plans = await get_compliance_plans(ctx)

    plan_id = None

    for ele in plans:
        if ele["name"] == name:
            plan_id = ele["id"]
            break
    else:
        raise ValueError(f"compliance plan {name} not found")

    await client.post(
        "/configuration_manager/compliance_plans/run",
        json={"planId": plan_id}
    )

    body = {
        "searchParams": {
            "limit": 1,
            "planId": plan_id,
            "sort": { "started": -1 },
            "start": 0
        }
    }

    res = await client.post(
        "/configuration_manager/search/compliance_plan_instances",
        json=body
    )

    instance = res.json()
    data = instance["plans"][0]

    return {
        "id": data["id"],
        "name": data["name"],
        "description": data["description"],
        "jobStatus": data["jobStatus"]
    }
