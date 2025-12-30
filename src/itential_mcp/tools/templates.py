# Copyright (c) 2025 Itential, Inc
# GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

import inspect

from typing import Annotated, Literal

from pydantic import Field

from fastmcp import Context

from itential_mcp.models import templates as models


__tags__ = ("automation_studio",)


async def get_templates(
    ctx: Annotated[Context, Field(description="The FastMCP Context object")],
    template_type: Annotated[
        Literal["textfsm", "jinja2"] | None,
        Field(description="Retrieve only templates of this type", default=None),
    ],
) -> list[models.GetTemplatesElement]:
    """Get all templates from Automation Studio.

    Retrieves all templates from the Automation Studio, with optional filtering
    by template type. Templates are used for text processing, configuration
    generation, and data parsing within automation workflows.

    This function performs paginated requests through the automation studio service
    to retrieve all available templates, handling large result sets efficiently.
    Results are transformed into standardized GetTemplatesElement objects for
    consistent API responses.

    Args:
        ctx (Context): The FastMCP Context object containing request context
            and lifecycle information including the platform client.
        template_type (Literal["textfsm", "jinja2"] | None): Optional filter to
            retrieve only templates of the specified type. Supported types are
            "textfsm" for TextFSM parsing templates and "jinja2" for Jinja2
            templating. Defaults to None to retrieve all template types.

    Returns:
        list[models.GetTemplatesElement]: A list of template objects containing template
            metadata including id, name, description, and type fields transformed
            into GetTemplatesElement model objects.

    Raises:
        Exception: If there is an error retrieving templates from the
            Automation Studio service.
    """
    await ctx.info("inside get_templates(...)")
    client = ctx.request_context.lifespan_context.get("client")
    res = await client.automation_studio.get_templates(template_type=template_type)

    results = []

    for ele in res:
        results.append(
            models.GetTemplatesElement(
                name=ele.get("name"),
                description=ele.get("description"),
                type=ele.get("type"),
            )
        )

    return results


async def describe_template(
    ctx: Annotated[Context, Field(description="The FastMCP Context object")],
    name: Annotated[str, Field(description="The name of the template to describe")],
    project: Annotated[
        str | None,
        Field(
            description="The name of the project the template resides in ", default=None
        ),
    ],
) -> models.DescribeTemplateResponse:
    """Get detailed information about a specific template from Automation Studio.

    Retrieves comprehensive template information including name, description, type,
    group, command, template content, and sample data. Templates are used for text
    processing, configuration generation, and data parsing within automation workflows.

    Args:
        ctx (Context): The FastMCP Context object containing request context
            and lifecycle information including the platform client.
        name (str): The name of the template to retrieve. Template names are
            case-sensitive and must match exactly.
        project (str | None): The name of the project the template resides in.
            If None, searches for the template in global space. Defaults to None.

    Returns:
        Mapping[str, Any]: Template details containing name, description, type,
            group, command, template content, and sample data fields.

    Raises:
        NotFoundError: If the specified template name cannot be found in the
            Automation Studio.
        Exception: If there is an error retrieving the template information
            from the Automation Studio API.
    """
    await ctx.info("inside get_templates(...)")
    client = ctx.request_context.lifespan_context.get("client")
    res = await client.automation_studio.describe_template(name=name, project=project)
    return models.DescribeTemplateResponse(
        name=res.get("name"),
        description=res.get("description"),
        type=res.get("type"),
        group=res.get("group"),
        command=res.get("command"),
        template=res.get("template"),
        data=res.get("data"),
    )


async def create_template(
    ctx: Annotated[Context, Field(description="The FastMCP Context object")],
    name: Annotated[str, Field(description="The name of the template to create")],
    template_type: Annotated[
        Literal["textfsm", "jinja2"], Field(description="Type of template to create")
    ],
    group: Annotated[str, Field(description="The gorup this template belongs to")],
    project: Annotated[
        str,
        Field(
            description=inspect.cleandoc(
                """
            The name of the project where this template should be created.
            The available projects can be found using get_projects
            """
            ),
            default=None,
        ),
    ],
    command: Annotated[
        str,
        Field(
            description="The CLI command to be run on the target device", default=None
        ),
    ],
    template: Annotated[
        str,
        Field(
            description="The template text uesd to generate the output", default=None
        ),
    ],
    data: Annotated[
        str, Field(description="Sample data used to test the template", default=None)
    ],
) -> models.CreateTemplateResponse:
    """Create a new template in Automation Studio.

    Creates a new template with the specified name, type, group, and optional
    content including command, template text, and sample data. Templates are
    used for text processing, configuration generation, and data parsing within
    automation workflows.

    Args:
        ctx (Context): The FastMCP Context object containing request context
            and lifecycle information including the platform client.
        name (str): The name of the template to create. Template names must be
            unique within the specified project or global space.
        template_type (Literal["textfsm", "jinja2"]): Type of template to create.
            "textfsm" for parsing templates or "jinja2" for configuration templating.
        group (str): The group this template belongs to for organizational purposes.
        project (str | None): The name of the project where this template should
            be created. If None, creates in global space. Available projects can
            be found using get_projects. Defaults to None.
        command (str | None): The CLI command to be run on the target device to
            generate source text. Defaults to None.
        template (str | None): The template text used to generate the final output.
            For textfsm templates, this contains parsing rules. For jinja2 templates,
            this contains templating syntax. Defaults to None.
        data (str | None): Sample data used to test the template functionality.
            Defaults to None.

    Returns:
        Mapping[str, Any]: Created template details containing name, description,
            type, group, command, template content, and sample data fields.

    Raises:
        ValueError: If a template with the same name already exists in the
            specified project or global space.
        Exception: If there is an error creating the template in the
            Automation Studio API.
    """
    await ctx.info("inside create_template(...)")
    client = ctx.request_context.lifespan_context.get("client")
    res = await client.automation_studio.create_template(
        name=name,
        template_type=template_type,
        group=group,
        project=project,
        command=command,
        template=template,
        data=data,
    )

    return models.CreateTemplateResponse(
        name=res.get("name"),
        description=res.get("description"),
        type=res.get("type"),
        group=res.get("group"),
        command=res.get("command"),
        template=res.get("template"),
        data=res.get("data"),
    )


async def update_template(
    ctx: Annotated[Context, Field(description="The FastMCP Context object")],
    name: Annotated[str, Field(description="The name of the template to update")],
    project: Annotated[
        str,
        Field(
            description=inspect.cleandoc(
                """
            The name of the project where this template resides.  The
            available projects can be found using get_projects
            """
            ),
            default=None,
        ),
    ],
    command: Annotated[
        str,
        Field(
            description="The CLI command to be run on the target device", default=None
        ),
    ],
    template: Annotated[
        str,
        Field(
            description="The template text uesd to generate the output", default=None
        ),
    ],
    data: Annotated[
        str, Field(description="Sample data used to test the template", default=None)
    ],
) -> models.UpdateTemplateResponse:
    """Update an existing template in Automation Studio.

    Updates an existing template with new content including command, template text,
    and sample data. Only specified fields will be updated; fields not provided
    will retain their existing values. Templates are used for text processing,
    configuration generation, and data parsing within automation workflows.

    Args:
        ctx (Context): The FastMCP Context object containing request context
            and lifecycle information including the platform client.
        name (str): The name of the template to update. Template names are
            case-sensitive and must match exactly.
        project (str | None): The name of the project where this template resides.
            If None, searches in global space. Available projects can be found
            using get_projects. Defaults to None.
        command (str | None): The CLI command to be run on the target device to
            generate source text. If None, existing value is preserved.
            Defaults to None.
        template (str | None): The template text used to generate the final output.
            For textfsm templates, this contains parsing rules. For jinja2 templates,
            this contains templating syntax. If None, existing value is preserved.
            Defaults to None.
        data (str | None): Sample data used to test the template functionality.
            If None, existing value is preserved. Defaults to None.

    Returns:
        Mapping[str, Any]: Updated template details containing name, description,
            type, group, command, template content, and sample data fields.

    Raises:
        NotFoundError: If the specified template name cannot be found in the
            Automation Studio.
        Exception: If there is an error updating the template in the
            Automation Studio API.
    """
    await ctx.info("inside update_template(...)")
    client = ctx.request_context.lifespan_context.get("client")
    res = await client.automation_studio.update_template(
        name=name, project=project, command=command, template=template, data=data
    )

    return models.UpdateTemplateResponse(
        name=res.get("name"),
        group=res.get("group"),
        description=res.get("description"),
        type=res.get("type"),
        command=res.get("command"),
        template=res.get("template"),
        data=res.get("data"),
    )
