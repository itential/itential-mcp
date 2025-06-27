# Copyright (c) 2025 Itential, Inc
# GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)

from typing import Annotated

from pydantic import Field

from fastmcp import Context


async def get_compliance_plans(
    ctx: Annotated[Context, Field(
        description="The FastMCP Context object"
    )],
) -> list[dict]:
    """
    Gets all configured compliance plans from Itential Platform

    This tool will return a all of the configured compliance plans found
    on from Itential Platform.  Each element in the returned list represents
    a configured compliance plan.  If there are no configured compliance
    plans, the tool will return an empty list.

    Elements in the list have the following fields:

        * id: The unique identifier for the compliance plan
        * name: The name of the compliance plan
        * description: Short description about the compliance plan
        * throttle: The configured number of devices that will be checked
            in parallel when the compliance plan is run

    Args:
        ctx (Context): The FastMCP Context object

    Returns:
        dict: A Python list of dict objects that reprsesent all of the devices
            knownn to Itential Platform

    Raises:
        None
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
    Run a compliance plan from Itential Platform

    This tool will start the running of the compliance plan specified
    by the name argument.  Once started, this tool will return the
    running instance of the compliance plan.  If the compliance plan
    does not exist, this tool will return an error.

    The name argument is case sensitive

    The returned object has the following fields:

        * id: The unique identifier for this compliance plan instance
        * name: The name of the compliance plan that was started
        * description: Short description of the compliance plan
        * jobStatus: The current job status of the compliance plan instance

    Args:
        ctx (Context): The FastMCP Context object

        name (str): The name of the compliance plan to run

    Returns:
        dict: an object that represents the running instance of the
            compliance plan

    Raises:
        ValueError: Raises when the compliance plan specified by the
            name argument is not found
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
