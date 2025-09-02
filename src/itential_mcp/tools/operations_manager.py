# Copyright (c) 2025 Itential, Inc
# GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)

from typing import Annotated

from pydantic import Field

from fastmcp import Context

from itential_mcp import timeutils
from itential_mcp import functions

from itential_mcp.models import operations_manager as models


__tags__ = ("operations_manager",)


async def get_workflows(
    ctx: Annotated[Context, Field(
        description="The FastMCP Context object"
    )]
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
        - The 'schema' field defines required input parameters for workflow execution
        - Only enabled workflows are returned by this function
    """
    await ctx.info("inside get_workflows(...)")

    client = ctx.request_context.lifespan_context.get("client")

    data = await client.operations_manager.get_workflows()

    workflow_elements = []

    for item in data.get("data") or list():
        if item.get("lastExecuted") is not None:
            lastExecuted = timeutils.epoch_to_timestamp(item["lastExecuted"])
        else:
            lastExecuted = None

        workflow_element = models.WorkflowElement(
            **{
                "name": item.get("name"),
                "description": item.get("description"),
                "schema": item.get("schema"),
                "route_name": item.get("routeName"),
                "last_executed": lastExecuted,
            }
        )
        workflow_elements.append(workflow_element)

    return models.GetWorkflowsResponse(root=workflow_elements)


async def start_workflow(
    ctx: Annotated[Context, Field(
        description="The FastMCP Context object"
    )],
    route_name: Annotated[str, Field(
        description="The name of the API endpoint used to start the workflow"
    )],
    data: Annotated[dict | None, Field(
        description="Data to include in the request body when calling the route",
        default=None
    )]
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
        user = await functions.account_id_to_username(ctx, metrics_data["user"])

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
    ctx: Annotated[Context, Field(
        description="The FastMCP Context object"
    )],
    name: Annotated[str | None, Field(
        description="Workflow name used to filter the results",
        default=None
    )],
    project: Annotated[str | None, Field(
        description="Project name used to filter the results",
        default=None
    )]
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
                "object_id": item.get("_id"),
                "name": item.get("name"),
                "description": item.get("description"),
                "status": item.get("status")
            }
        )
        job_elements.append(job_element)

    return models.GetJobsResponse(root=job_elements)


async def describe_job(
    ctx: Annotated[Context, Field(
        description="The FastMCP Context object"
    )],
    object_id: Annotated[str, Field(
        description="The ID used to retrieve the job"
    )]
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
            "name": data["name"],
            "description": data["description"],
            "type": data["type"],
            "tasks": data["tasks"],
            "status": data["status"],
            "metrics": data["metrics"],
            "updated": data["last_updated"]
        }
    )
