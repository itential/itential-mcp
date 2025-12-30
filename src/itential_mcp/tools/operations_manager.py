# Copyright (c) 2025 Itential, Inc
# GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from typing import Annotated

from pydantic import Field

from fastmcp import Context

from itential_mcp.utilities import time as timeutils
from itential_mcp.core import exceptions
from itential_mcp.utilities import json as jsonutils

from itential_mcp.models import operations_manager as models


__tags__ = ("operations_manager",)


async def _account_id_to_username(ctx: Context, account_id: str) -> str:
    """Retrieve the username for an account ID.

    This function will take an account ID and use it to look up the username
    associated with it.

    Args:
        ctx (Context): The FastMCP Context object.
        account_id (str): The ID of the account to lookup and return the
            username for.

    Returns:
        str: The username associated with the account ID.

    Raises:
        ValueError: If the account ID cannot be found on the server.
        Exception: If there is an error communicating with the authorization API.
    """
    client = ctx.request_context.lifespan_context.get("client")

    limit = 100
    skip = 0
    cnt = 0

    params = {"limit": limit}
    value = None

    while True:
        params["skip"] = skip

        res = await client.get("/authorization/accounts", params=params)

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

    return value


async def get_workflows(
    ctx: Annotated[Context, Field(description="The FastMCP Context object")],
) -> models.GetWorkflowsResponse:
    """
    Get all workflow API endpoints from Itential Platform.

    Workflows are the core automation engine of Itential Platform, defining
    executable processes that orchestrate network operations, device management,
    and service provisioning. Each workflow exposes an API endpoint that can be
    triggered by external systems or other platform components.

    Args:
        ctx (Context): The FastMCP Context object

    Returns:
        models.GetWorkflowsResponse: Response model containing a list of workflow objects with the following fields:
            - name: Workflow name (use this as the identifier for workflow operations)
            - description: Workflow description
            - schema: Input schema for workflow parameters (JSON Schema draft-07 format)
            - route_name: API route name for triggering the workflow (use with `start_workflow`)
            - last_executed: ISO 8601 timestamp of last execution (null if never executed)

    Notes:
        - Use the 'name' field as the workflow identifier for most operations
        - Use the 'route_name' field specifically for `start_workflow` function
        - The 'input_schema' field defines required input parameters for workflow execution
        - Only enabled workflows are returned by this function
    """
    await ctx.info("inside get_workflows(...)")

    client = ctx.request_context.lifespan_context.get("client")

    data = await client.operations_manager.get_workflows()

    workflow_elements = []

    for item in data:
        if item.get("lastExecuted") is not None:
            lastExecuted = timeutils.epoch_to_timestamp(item["lastExecuted"])
        else:
            lastExecuted = None

        workflow_element = models.WorkflowElement(
            **{
                "name": item.get("name"),
                "description": item.get("description"),
                "input_schema": item.get("schema"),
                "route_name": item.get("routeName"),
                "last_executed": lastExecuted,
            }
        )
        workflow_elements.append(workflow_element)

    return models.GetWorkflowsResponse(root=workflow_elements)


async def start_workflow(
    ctx: Annotated[Context, Field(description="The FastMCP Context object")],
    route_name: Annotated[
        str,
        Field(description="The name of the API endpoint used to start the workflow"),
    ],
    data: Annotated[
        dict | str | None,
        Field(
            description="Data to include in the request body when calling the route",
            default=None,
        ),
    ],
) -> models.StartWorkflowResponse:
    """
    Execute a workflow by triggering its API endpoint.

    Workflows are the core automation processes in Itential Platform. This function
    initiates workflow execution and returns a job object that can be monitored
    for progress and results.

    Args:
        ctx (Context): The FastMCP Context object

        route_name (str): API route name for the workflow. Use the 'route_name'
            field from `get_workflows`.

        data (dict | None): Input data for workflow execution. Structure must
            match the workflow's input schema (available in the 'schema'
            field from `get_workflows`).

    Returns:
        models.StartWorkflowResponse: Job execution details with the following fields:
            - object_id: Unique job identifier (use with `describe_job` for monitoring)
            - name: Workflow name that was executed
            - description: Workflow description
            - tasks: Complete set of tasks to be executed in the workflow
            - status: Current job status (error, complete, running, canceled, incomplete, paused)
            - metrics: Job execution metrics including start_time, end_time, and user

    Notes:
        - Use the returned 'object_id' field with `describe_job` to monitor workflow progress
        - The 'data' parameter must conform to the workflow's input schema
        - Job status can be monitored using the `get_jobs` or `describe_job` functions
        - Workflow schemas are available via the `get_workflows` function
    """
    await ctx.info("inside start_workflow(...)")

    client = ctx.request_context.lifespan_context.get("client")

    # Parse data if it's a JSON string
    if isinstance(data, str):
        data = jsonutils.loads(data)

    res = await client.operations_manager.start_workflow(route_name, data)

    metrics_data = res.get("metrics") or {}

    start_time = None
    end_time = None
    user = None

    if metrics_data.get("start_time") is not None:
        start_time = timeutils.epoch_to_timestamp(metrics_data["start_time"])

    if metrics_data.get("end_time") is not None:
        end_time = timeutils.epoch_to_timestamp(metrics_data["end_time"])

    if metrics_data.get("user") is not None:
        user = await _account_id_to_username(ctx, metrics_data["user"])

    metrics = models.JobMetrics(
        start_time=start_time,
        end_time=end_time,
        user=user,
    )

    return models.StartWorkflowResponse(
        **{
            "object_id": res["_id"],
            "name": res["name"],
            "description": res.get("description"),
            "tasks": res["tasks"],
            "status": res["status"],
            "metrics": metrics,
        }
    )


async def get_jobs(
    ctx: Annotated[Context, Field(description="The FastMCP Context object")],
    name: Annotated[
        str | None,
        Field(description="Workflow name used to filter the results", default=None),
    ],
    project: Annotated[
        str | None,
        Field(description="Project name used to filter the results", default=None),
    ],
) -> models.GetJobsResponse:
    """
    Get all jobs from Itential Platform.

    Jobs represent workflow execution instances that track the status, progress,
    and results of automated tasks. They provide visibility into workflow
    execution and enable monitoring of automation operations.

    Args:
        ctx (Context): The FastMCP Context object
        name (str | None): Filter jobs by workflow name (optional)
        project (str | None): Filter jobs by project name (optional)

    Returns:
        models.GetJobsResponse: List of job objects with the following fields:
            - _id: Unique job identifier
            - description: Job description
            - name: Job name
            - status: Current job status (error, complete, running, cancelled, incomplete, paused)
    """
    await ctx.info("running get_jobs(...)")

    client = ctx.request_context.lifespan_context.get("client")

    data = await client.operations_manager.get_jobs(name=name, project=project)

    job_elements = []

    for item in data or []:
        job_element = models.JobElement(
            **{
                "_id": item.get("_id"),
                "name": item.get("name"),
                "description": item.get("description"),
                "status": item.get("status"),
            }
        )
        job_elements.append(job_element)

    return models.GetJobsResponse(root=job_elements)


async def describe_job(
    ctx: Annotated[Context, Field(description="The FastMCP Context object")],
    object_id: Annotated[str, Field(description="The ID used to retrieve the job")],
) -> models.DescribeJobResponse:
    """
    Get detailed information about a specific job from Itential Platform.

    Jobs are created automatically when workflows are executed and contain
    comprehensive information about the workflow execution including status,
    tasks, metrics, and results.

    Args:
        ctx (Context): The FastMCP Context object

        object_id (str): Unique job identifier to retrieve. Object IDs are returned
            by `start_workflow` and `get_jobs`.

    Returns:
        models.DescribeJobResponse: Job details with the following fields:
            - name: Job name
            - description: Job description
            - type: Job type (automation, resource:action, resource:compliance)
            - tasks: Complete set of tasks executed
            - status: Current job status (error, complete, running, canceled, incomplete, paused)
            - metrics: Job execution metrics including start time, end time, and account
            - updated: Last update timestamp
    """
    await ctx.info("inside describe_job(...)")

    client = ctx.request_context.lifespan_context.get("client")

    data = await client.operations_manager.describe_job(object_id)

    return models.DescribeJobResponse(
        **{
            "_id": data["_id"],
            "name": data["name"],
            "description": data["description"],
            "type": data["type"],
            "tasks": data["tasks"],
            "status": data["status"],
            "metrics": data["metrics"],
            "updated": data["last_updated"],
        }
    )


async def expose_workflow(
    ctx: Annotated[
        Context,
        Field(
            description="The FastMCP Context object",
        ),
    ],
    name: Annotated[
        str,
        Field(
            description="The name of the workflow to expose",
        ),
    ],
    route_name: Annotated[
        str | None,
        Field(
            description="The API route name to assign to this endpoint", default=None
        ),
    ],
    project: Annotated[
        str | None,
        Field(description="The project where the workflow resides", default=None),
    ],
    endpoint_name: Annotated[
        str | None,
        Field(description="Set the name for the trigger endpoint", default=None),
    ],
    endpoint_description: Annotated[
        str | None,
        Field(description="Set a description on the endpoint trigger", default=None),
    ],
    endpoint_schema: Annotated[
        dict | None,
        Field(
            description="Set the request schemd for the endpoint trigger", default=None
        ),
    ],
) -> models.ExposeWorkflowResponse:
    """Expose a workflow as an API endpoint.

    Creates an automation and API endpoint trigger to expose a workflow
    for external consumption. This enables workflows to be called via
    REST API endpoints with custom routing and input validation.

    Args:
        ctx (Context): The FastMCP Context object.
        name (str): The name of the workflow to expose.
        route_name (str | None): The API route name to assign to this endpoint.
            If None, defaults to the workflow name with spaces replaced by underscores.
        project (str | None): The project where the workflow resides.
            If None, looks for the workflow in global space.
        endpoint_name (str | None): Set the name for the trigger endpoint.
            If None, defaults to "API Route for {workflow_name}".
        endpoint_description (str | None): Set a description on the endpoint trigger.
            If None, defaults to "auto-created by itential-mcp".
        endpoint_schema (dict | None): Set the request schema for the endpoint trigger.
            If None, uses the workflow's input schema.

    Returns:
        models.ExposeWorkflowResponse: Response containing the status message
            about the workflow exposure operation.

    Raises:
        exceptions.ConfigurationException: If there is an error creating the endpoint
            trigger or the workflow cannot be exposed.
        Exception: If there is an error retrieving workflow information or
            creating the automation.
    """
    await ctx.info("inside expose_workflow(...)")

    client = ctx.request_context.lifespan_context.get("client")

    if project:
        res = await client.automation_studio.describe_project(project)
        workflow_name = f"@{res['_id']}: {name}"
        automation_name = f"{name} from {project}"
    else:
        workflow_name = name
        automation_name = name

    res = await client.operations_manager.create_automation(
        name=automation_name,
        component_type="workflows",
        component_name=workflow_name,
        description="auto-created by itential-mcp",
    )

    automation_id = res["_id"]

    if not endpoint_schema:
        res = await client.automation_studio.describe_workflow_with_name(workflow_name)
        endpoint_schema = res["inputSchema"]

    try:
        await client.operations_manager.create_endpoint_trigger(
            name=endpoint_name or f"API Route for {name}",
            automation_id=automation_id,
            description=endpoint_description or "auto-created by itential-mcp",
            route_name=route_name or name.replace(" ", "_"),
            schema=endpoint_schema,
        )

    except Exception as exc:
        await client.operations_manager.delete_automation(automation_id)
        raise exceptions.ConfigurationException(f"failed to expose workflow: {exc}")

    return models.ExposeWorkflowResponse(
        message=f"Successfully exposed workflow `{name}` with route `{route_name}`"
    )
