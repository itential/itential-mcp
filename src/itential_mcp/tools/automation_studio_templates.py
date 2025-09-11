# Copyright (c) 2025 Itential, Inc
# GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)

from typing import Annotated, Sequence

from pydantic import Field

from fastmcp import Context


__tags__ = ("automation_studio",)


async def get_templates(
    ctx: Annotated[Context, Field(description="The FastMCP Context object")],
    include: Annotated[
        Sequence[str] | None,
        Field(
            description="Fields to include in the response (_id,name,group)",
            default=("_id", "name", "group"),
        ),
    ],
    exclude_project_members: Annotated[
        bool,
        Field(
            description="Exclude project member data for speed",
            default=True,
        ),
    ],
    limit: Annotated[int, Field(description="Page size limit", default=50)],
    sort: Annotated[str, Field(description="Sort field", default="group")],
    skip: Annotated[int | None, Field(description="Pagination offset", default=None)],
):
    """
    List Automation Studio templates with pagination and filters.

    Returns the API pagination envelope including items, total, skip, limit, count, next, previous.
    """
    await ctx.info("inside get_templates(...)")

    client = ctx.request_context.lifespan_context.get("client")

    return await client.automation_studio.get_templates(
        include=include,
        exclude_project_members=exclude_project_members,
        limit=limit,
        sort=sort,
        skip=skip,
    )


async def create_template(
    ctx: Annotated[Context, Field(description="The FastMCP Context object")],
    name: Annotated[str, Field(description="Template name")],
    group: Annotated[str, Field(description="Group name")],
    description: Annotated[str, Field(description="Template description")],
    template: Annotated[str, Field(description="Template body (e.g., Jinja2)")],
    data: Annotated[
        str,
        Field(description="Default data JSON string", default=""),
    ],
    command: Annotated[
        str,
        Field(description="Optional command string", default=""),
    ],
    type: Annotated[
        str,
        Field(description="Template type (jinja2)", default="jinja2"),
    ],
):
    """
    Create a new Automation Studio template.

    Mirrors the API semantics described in your example. Returns the server response
    including the created template and edit link.
    """
    await ctx.info("inside create_template(...)")

    client = ctx.request_context.lifespan_context.get("client")

    return await client.automation_studio.create_template(
        name=name,
        group=group,
        description=description,
        template=template,
        data=data,
        command=command,
        type=type,
    )


async def update_template(
    ctx: Annotated[Context, Field(description="The FastMCP Context object")],
    template_id: Annotated[str, Field(description="Template _id to update")],
    name: Annotated[str, Field(description="Template name")],
    group: Annotated[str, Field(description="Group name")],
    description: Annotated[str, Field(description="Template description")],
    template: Annotated[str, Field(description="Template body (e.g., Jinja2)")],
    data: Annotated[
        str,
        Field(description="Default data JSON string", default=""),
    ],
    command: Annotated[
        str,
        Field(description="Optional command string", default=""),
    ],
    type: Annotated[
        str,
        Field(description="Template type (jinja2)", default="jinja2"),
    ],
):
    """
    Update an existing Automation Studio template by id.

    Returns the server response including the updated template and edit link.
    """
    await ctx.info("inside update_template(...)")

    client = ctx.request_context.lifespan_context.get("client")

    return await client.automation_studio.update_template(
        template_id=template_id,
        name=name,
        group=group,
        description=description,
        template=template,
        data=data,
        command=command,
        type=type,
    )


