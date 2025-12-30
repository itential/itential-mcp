# Copyright (c) 2025 Itential, Inc
# GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

import re

from typing import Annotated

from pydantic import Field

from fastmcp import Context

from itential_mcp.models import projects as models


__tags__ = ("automation_studio",)


async def get_projects(
    ctx: Annotated[Context, Field(description="The FastMCP Context object")],
) -> models.GetProjectsResponse:
    """Get all Automation Studio projects from Itential Platform.

    Projects in Automation Studio organize workflows, templates, and other
    automation artifacts into logical groupings for team collaboration
    and asset management.

    Args:
        ctx: The FastMCP Context object

    Returns:
        GetProjectsResponse: List of project objects with the following fields:
            - id: Unique project identifier
            - name: Project name
            - description: Project description

    Raises:
        Exception: If there is an error retrieving projects from the platform
    """
    await ctx.info("inside get_projects(...)")
    client = ctx.request_context.lifespan_context.get("client")
    res = await client.automation_studio.get_projects()

    results = []

    for ele in res:
        results.append(
            models.GetProjectsElement(
                id=ele.get("_id"),
                name=ele.get("name"),
                description=ele.get("description"),
            )
        )

    return models.GetProjectsResponse(root=results)


async def describe_project(
    ctx: Annotated[Context, Field(description="The FastMCP Context object")],
    name: Annotated[str, Field(description="The name of the project to describe")],
) -> models.DescribeProjectResponse:
    """Get detailed information about a specific Automation Studio project.

    Retrieves comprehensive project information including all components
    (workflows, templates, and other artifacts) contained within the project
    along with their metadata and organization structure.

    Args:
        ctx: The FastMCP Context object
        name: The name of the project to describe

    Returns:
        DescribeProjectResponse: Detailed project information with the following fields:
            - id: Unique project identifier
            - name: Project name
            - description: Project description
            - components: List of project components with their details

    Raises:
        Exception: If there is an error retrieving the project or project is not found
    """
    await ctx.info("inside describe_project(...)")

    client = ctx.request_context.lifespan_context.get("client")

    data = await client.automation_studio.describe_project(name=name)

    components = []

    for ele in data["components"]:
        match = re.search(r":\s*(.*)", ele["name"])
        component_name = match.group(1).strip()
        components.append(
            models.DescribeProjectComponent(
                id=ele.get("reference"),
                type=ele.get("type"),
                folder=ele.get("folder"),
                name=component_name,
            )
        )

    return models.DescribeProjectResponse(
        id=data.get("_id"),
        name=data.get("name"),
        description=data.get("description"),
        components=components,
    )
