# Copyright (c) 2025 Itential, Inc
# GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)

from typing import Annotated

from pydantic import Field

from fastmcp import Context

from itential_mcp import exceptions
from itential_mcp.models import automation_studio as models


__tags__ = ("automation_studio", "projects")


async def get_projects(
    ctx: Annotated[Context, Field(
        description="The FastMCP Context object"
    )]
) -> models.GetProjectsResponse:
    """
    Get all Automation Studio projects from Itential Platform.

    This function retrieves a list of all projects available in the Automation Studio,
    including project metadata such as name, description, creator, and timestamps.
    The response is filtered to focus on essential project information.

    Args:
        ctx (Context): The FastMCP Context object

    Returns:
        GetProjectsResponse: An object containing the response message, list of project
            summaries with _id, name, description, iid, createdBy, created, and lastUpdated
            fields, and metadata for pagination.

    Raises:
        Exception: If there is an error communicating with the Itential Platform API
            or if the API returns an unexpected response format.

    Examples:
        Get all projects:
            >>> projects = await get_projects(ctx)
            >>> print(f"Total projects: {projects.metadata.total}")
            >>> for project in projects.data:
            ...     print(f"Project: {project.name} (ID: {project.iid})")
    """
    await ctx.info("inside get_projects(...)")

    client = ctx.request_context.lifespan_context.get("client")

    res = await client.get("/automation-studio/projects")

    data = res.json()

    # Filter and structure the response as specified in thoughts
    return models.GetProjectsResponse(
        message=data.get("message", "Successfully retrieved projects"),
        data=data.get("data", []),
        metadata=data.get("metadata", {})
    )


async def describe_project(
    ctx: Annotated[Context, Field(
        description="The FastMCP Context object"
    )],
    project_id: Annotated[int, Field(
        description="The project ID (iid) to describe"
    )]
) -> models.DescribeProjectResponse:
    """
    Get detailed information about a specific Automation Studio project.

    This function retrieves comprehensive project details including all components,
    workflows, and configuration data. The project_id should be the 'iid' field
    from the project object returned by get_projects().

    Args:
        ctx (Context): The FastMCP Context object
        project_id (int): The project internal ID (iid) to describe

    Returns:
        DescribeProjectResponse: An object containing the response message and
            project data with focus on _id, name, description, and components.

    Raises:
        Exception: If there is an error communicating with the Itential Platform API,
            if the project is not found, or if the API returns an unexpected response format.

    Examples:
        Describe a specific project:
            >>> project_details = await describe_project(ctx, 97)
            >>> print(f"Project: {project_details.data['name']}")
            >>> print(f"Components: {len(project_details.data['components'])}")
            >>> for component in project_details.data['components']:
            ...     if component['type'] == 'workflow':
            ...         print(f"Workflow: {component['document']['name']}")

        Get project after listing:
            >>> projects = await get_projects(ctx)
            >>> for project in projects.data:
            ...     if project.name == "My Project":
            ...         details = await describe_project(ctx, project.iid)
            ...         break
    """
    await ctx.info(f"inside describe_project(...) for project_id: {project_id}")

    client = ctx.request_context.lifespan_context.get("client")

    res = await client.get(f"/automation-studio/projects/{project_id}/export")

    data = res.json()

    # Filter and structure the response as specified in thoughts
    # Focus on message, data, and inside data _id, name, description, components only
    filtered_data = {
        "id": data.get("data", {}).get("_id"),
        "name": data.get("data", {}).get("name"),
        "description": data.get("data", {}).get("description"),
        "components": data.get("data", {}).get("components", [])
    }

    return models.DescribeProjectResponse(
        message=data.get("message", "Successfully exported project"),
        data=filtered_data
    )
