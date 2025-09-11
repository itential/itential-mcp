# Copyright (c) 2025 Itential, Inc
# GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)

from typing import Annotated

from pydantic import Field

from fastmcp import Context

from itential_mcp.models import automation_studio as models

__tags__ = ("automation_studio", "textfsm")


async def get_textfsm_templates(
    ctx: Annotated[Context, Field(description="The FastMCP Context object")],
    include: Annotated[
        str | None,
        Field(
            description="Comma-separated fields to include in the response (e.g., '_id,name,group,command')",
            default="_id,name,group",
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
    List TextFSM templates with pagination and filters.

    Returns the API pagination envelope including items, total, skip, limit, count, next, previous.
    """
    await ctx.info("inside get_textfsm_templates(...)")

    client = ctx.request_context.lifespan_context.get("client")

    # Convert comma-separated string to list if needed
    include_list = None
    if include:
        include_list = [field.strip() for field in include.split(",")]

    return await client.automation_studio.get_templates(
        include=include_list,
        exclude_project_members=exclude_project_members,
        limit=limit,
        sort=sort,
        skip=skip,
    )


async def create_textfsm_template(
    ctx: Annotated[Context, Field(description="The FastMCP Context object")],
    name: Annotated[str, Field(description="Template name")],
    group: Annotated[str, Field(description="Group name")],
    description: Annotated[str, Field(description="Template description")],
    template: Annotated[str, Field(description="TextFSM template body with Value definitions and state machine")],
    data: Annotated[
        str,
        Field(description="Sample data for testing the template", default=""),
    ],
    command: Annotated[
        str,
        Field(description="Command that produces the data to parse", default=""),
    ],
) -> models.CreateTextFSMTemplateResponse:
    """
    Create a new TextFSM template for parsing network device output.

    TextFSM templates use a state machine approach to parse semi-formatted text output from network devices.
    The template should include:
    
    1. Value definitions (e.g., "Value Required,Filldown ACL_NAME (\\S+)")
    2. State machine rules (e.g., "Start", "Continue", "EOF")
    3. Regular expressions to match and extract data
    
    Example TextFSM template structure:
    ```
    Value Required,Filldown ACL_NAME (\\S+)
    Value ACL_TYPE (standard|extended)
    Value ACTION (permit|deny)
    Value PROTOCOL ([a-z]+)
    
    Start
      ^ip\\s+access-list\\s+${ACL_TYPE}\\s+${ACL_NAME}\\s* -> Record
      ^\\s+${ACTION}\\s+${PROTOCOL}\\s+.* -> Record
    
    EOF
    ```

    Args:
        ctx: The FastMCP Context object
        name: Template name
        group: Group name  
        description: Template description
        template: TextFSM template body with Value definitions and state machine
        data: Sample data for testing the template
        command: Command that produces the data to parse

    Returns:
        CreateTextFSMTemplateResponse: Server response including the created template and edit link
    """
    await ctx.info("inside create_textfsm_template(...)")

    client = ctx.request_context.lifespan_context.get("client")

    response = await client.automation_studio.create_textfsm_template(
        name=name,
        group=group,
        description=description,
        template=template,
        data=data,
        command=command,
    )

    return models.CreateTextFSMTemplateResponse(**response)


async def update_textfsm_template(
    ctx: Annotated[Context, Field(description="The FastMCP Context object")],
    template_id: Annotated[str, Field(description="Template _id to update")],
    name: Annotated[str, Field(description="Template name")],
    group: Annotated[str, Field(description="Group name")],
    description: Annotated[str, Field(description="Template description")],
    template: Annotated[str, Field(description="TextFSM template body with Value definitions and state machine")],
    data: Annotated[
        str,
        Field(description="Sample data for testing the template", default=""),
    ],
    command: Annotated[
        str,
        Field(description="Command that produces the data to parse", default=""),
    ],
) -> models.UpdateTextFSMTemplateResponse:
    """
    Update an existing TextFSM template by id.

    TextFSM templates use a state machine approach to parse semi-formatted text output from network devices.
    The template should include:
    
    1. Value definitions (e.g., "Value Required,Filldown ACL_NAME (\\S+)")
    2. State machine rules (e.g., "Start", "Continue", "EOF")
    3. Regular expressions to match and extract data
    
    Example TextFSM template structure:
    ```
    Value Required,Filldown ACL_NAME (\\S+)
    Value ACL_TYPE (standard|extended)
    Value ACTION (permit|deny)
    Value PROTOCOL ([a-z]+)
    
    Start
      ^ip\\s+access-list\\s+${ACL_TYPE}\\s+${ACL_NAME}\\s* -> Record
      ^\\s+${ACTION}\\s+${PROTOCOL}\\s+.* -> Record
    
    EOF
    ```

    Args:
        ctx: The FastMCP Context object
        template_id: Template _id to update
        name: Template name
        group: Group name
        description: Template description
        template: TextFSM template body with Value definitions and state machine
        data: Sample data for testing the template
        command: Command that produces the data to parse

    Returns:
        UpdateTextFSMTemplateResponse: Server response including the updated template and edit link
    """
    await ctx.info("inside update_textfsm_template(...)")

    client = ctx.request_context.lifespan_context.get("client")

    response = await client.automation_studio.update_textfsm_template(
        template_id=template_id,
        name=name,
        group=group,
        description=description,
        template=template,
        data=data,
        command=command,
    )

    return models.UpdateTextFSMTemplateResponse(**response)
