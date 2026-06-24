# Copyright (c) 2025 Itential, Inc
# GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import annotations

import json

from typing import Annotated, Any

from pydantic import Field

from fastmcp import Context

from itential_mcp.utilities import time as timeutils
from itential_mcp.core import exceptions
from itential_mcp.utilities import json as jsonutils

from itential_mcp.models import operations_manager as models


__tags__ = ("operations_manager",)


def _coerce_value(value: Any, schema: dict) -> Any:
    """Coerce a single value to the type declared in its JSON Schema definition.

    LLMs often stringify nested structures (arrays, objects) when calling tools.
    This converts them back to the correct Python type using the schema as ground truth.
    If the value cannot be parsed or the schema has no type declaration, it is returned
    unchanged so the platform produces the real error rather than a silent wrong cast.
    """
    expected_type = schema.get("type")
    if not isinstance(value, str) or expected_type not in ("array", "object"):
        return value

    try:
        parsed = json.loads(value)
    except (json.JSONDecodeError, ValueError):
        return value

    if expected_type == "array" and isinstance(parsed, list):
        return parsed
    if expected_type == "object" and isinstance(parsed, dict):
        return parsed

    return value


def _coerce_data_to_schema(data: dict, input_schema: dict) -> dict:
    """Recursively coerce data values to match the types declared in the workflow input schema.

    Only top-level properties are coerced — nested structures beyond the first level
    are left to the platform's own validation.
    """
    properties: dict = input_schema.get("properties") or {}
    result = {}
    for key, value in data.items():
        prop_schema = properties.get(key, {})
        result[key] = _coerce_value(value, prop_schema)
    return result


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


async def get_agents(
    ctx: Annotated[Context, Field(description="The FastMCP Context object")],
) -> models.GetAgentsResponse:
    """
    Get all agent automations from Itential Platform.

    Agents are AI-driven automation components managed by the Operations Manager.
    Each agent automation may optionally have an endpoint trigger that exposes it
    for programmatic invocation via the same mechanism as workflows.

    Args:
        ctx (Context): The FastMCP Context object

    Returns:
        models.GetAgentsResponse: List of agent objects with the following fields:
            - name: Human-readable name of the automation wrapping the agent
            - description: Description of the agent automation
            - agent_id: UUID of the underlying agent component
            - route_name: API route name for triggering (use with trigger_automation);
              None means no endpoint trigger exists yet — use expose_agent to create one
            - input_schema: JSON Schema for the endpoint input (None if no endpoint trigger)
            - last_executed: ISO 8601 timestamp of last endpoint trigger execution

    Notes:
        - Use agent_id when creating a new automation via create_automation
        - Use route_name with trigger_automation to trigger an agent that has an endpoint
        - Agents without a route_name must be exposed first via expose_agent
    """
    await ctx.info("inside get_agents(...)")
    client = ctx.request_context.lifespan_context.get("client")
    data = await client.operations_manager.get_agents()

    agent_elements = []
    for item in data:
        last_executed = None
        if item.get("last_executed") is not None:
            last_executed = timeutils.epoch_to_timestamp(item["last_executed"])
        agent_elements.append(
            models.AgentElement(
                name=item["name"],
                description=item.get("description"),
                agent_id=item["agent_id"],
                route_name=item.get("route_name"),
                input_schema=item.get("input_schema"),
                last_executed=last_executed,
            )
        )
    return models.GetAgentsResponse(root=agent_elements)


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
) -> models.StartWorkflowResponse | models.StartAgentResponse:
    """
    Execute a workflow by triggering its API endpoint.

    Workflows are the core automation processes in Itential Platform. This function
    initiates workflow execution and returns a job object that can be monitored
    for progress and results. When the triggered route belongs to an agent automation,
    a StartAgentResponse with a session_id is returned instead.

    Args:
        ctx (Context): The FastMCP Context object

        route_name (str): API route name for the workflow. Use the 'route_name'
            field from `get_workflows`.

        data (dict | None): Input data for workflow execution. Structure must
            match the workflow's input schema (available in the 'schema'
            field from `get_workflows`).

    Returns:
        models.StartWorkflowResponse | models.StartAgentResponse: Job execution details
            or agent session details. If the route triggers an agent, a
            StartAgentResponse with session_id and status is returned instead of
            the normal job response.

    Notes:
        - Use the returned 'object_id' field with `describe_job` to monitor workflow progress
        - The 'data' parameter must conform to the workflow's input schema
        - Job status can be monitored using the `get_jobs` or `describe_job` functions
        - Workflow schemas are available via the `get_workflows` function
        - Agent triggers return `StartAgentResponse` with `session_id` instead of a job object
    """
    await ctx.info("inside start_workflow(...)")

    client = ctx.request_context.lifespan_context.get("client")

    # Parse data if it's a JSON string
    if isinstance(data, str):
        data = jsonutils.loads(data)

    # Coerce stringified values (e.g. arrays passed as strings by LLMs) using
    # the workflow's declared input schema so the platform receives the right types.
    # A failure to fetch the schema must not block the workflow start — fall back to
    # sending the data unchanged so the platform still produces the real error.
    if data:
        try:
            workflows = await client.operations_manager.get_workflows()
            input_schema = next(
                (
                    w.get("schema") or {}
                    for w in workflows
                    if w.get("routeName") == route_name
                ),
                {},
            )
            data = _coerce_data_to_schema(data, input_schema)
        except Exception as exc:
            await ctx.warning(
                f"skipping input coercion for '{route_name}'; "
                f"could not fetch workflow schema: {exc}"
            )

    res = await client.operations_manager.start_workflow(route_name, data)

    if "sessionId" in res:
        return models.StartAgentResponse(
            session_id=res["sessionId"],
            status=res.get("status", "RUNNING"),
        )

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
            - variables: Job variable outputs produced during workflow execution
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
            "variables": data.get("variables"),
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


async def expose_agent(
    ctx: Annotated[Context, Field(description="The FastMCP Context object")],
    agent_id: Annotated[
        str, Field(description="UUID of the agent to expose (agent_id from get_agents)")
    ],
    automation_name: Annotated[
        str, Field(description="Name for the automation wrapping the agent")
    ],
    route_name: Annotated[
        str | None,
        Field(
            description="API route name; defaults to automation_name with spaces replaced by underscores",
            default=None,
        ),
    ],
    endpoint_name: Annotated[
        str | None, Field(description="Name for the trigger endpoint", default=None)
    ],
    endpoint_description: Annotated[
        str | None,
        Field(description="Description for the endpoint trigger", default=None),
    ],
    endpoint_schema: Annotated[
        dict | None,
        Field(
            description="JSON Schema for endpoint input; defaults to open schema",
            default=None,
        ),
    ],
) -> models.ExposeWorkflowResponse:
    """Expose an agent as an API endpoint trigger.

    Creates an automation wrapping the specified agent and an endpoint trigger
    so the agent can be started via trigger_automation using the assigned route_name.

    Args:
        ctx (Context): The FastMCP Context object.
        agent_id (str): UUID of the agent component to expose. Use get_agents to
            retrieve available agent UUIDs.
        automation_name (str): Name for the automation that wraps this agent in
            the Operations Manager.
        route_name (str | None): API route name for the endpoint. Defaults to
            automation_name with spaces replaced by underscores.
        endpoint_name (str | None): Display name for the trigger.
        endpoint_description (str | None): Description for the trigger.
        endpoint_schema (dict | None): JSON Schema for trigger input validation.
            Defaults to an open schema that accepts any object.

    Returns:
        models.ExposeWorkflowResponse: Status message confirming the operation.

    Raises:
        exceptions.ConfigurationException: If the endpoint trigger cannot be created.
        Exception: If the automation cannot be created.
    """
    await ctx.info("inside expose_agent(...)")
    client = ctx.request_context.lifespan_context.get("client")

    res = await client.operations_manager.create_automation(
        name=automation_name,
        component_type="agents",
        component_name=agent_id,
        description="auto-created by itential-mcp",
    )

    automation_id = res["_id"]
    resolved_route = route_name or automation_name.replace(" ", "_")

    try:
        await client.operations_manager.create_endpoint_trigger(
            name=endpoint_name or f"API Route for {automation_name}",
            automation_id=automation_id,
            description=endpoint_description or "auto-created by itential-mcp",
            route_name=resolved_route,
            schema=endpoint_schema,
        )
    except Exception as exc:
        await client.operations_manager.delete_automation(automation_id)
        raise exceptions.ConfigurationException(f"failed to expose agent: {exc}")

    return models.ExposeWorkflowResponse(
        message=f"Successfully exposed agent `{agent_id}` as automation `{automation_name}` with route `{resolved_route}`"
    )
