# Copyright (c) 2025 Itential, Inc
# GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from typing import Annotated

from pydantic import Field

from fastmcp import Context

from itential_mcp.utilities import json as jsonutils
from itential_mcp.models import configuration_manager as models


__tags__ = ("configuration_manager",)


async def render_template(
    ctx: Annotated[Context, Field(description="The FastMCP Context object")],
    template: Annotated[str, Field(description="The Jinja2 template string")],
    variables: Annotated[
        dict | str | None,
        Field(
            description="Zero or more variables to associate with this template",
            default=None,
        ),
    ],
) -> models.RenderTemplateResponse:
    """
    Render a Jinja2 template with provided variables.

    Jinja2 templates are commonly used in network automation for generating
    device configurations, commands, and other text-based content by combining
    template structures with dynamic variable values.

    Args:
        ctx (Context): The FastMCP Context object
        template (str): The Jinja2 template string to render
        variables (dict): Key-value pairs to substitute in the template (optional)

    Returns:
        RenderTemplateResponse: The fully rendered template with variables substituted

    Raises:
        Exception: If there is an error rendering the template
    """
    await ctx.info("inside render_template()")
    client = ctx.request_context.lifespan_context.get("client")

    # Parse variables if it's a JSON string
    if isinstance(variables, str):
        variables = jsonutils.loads(variables)

    data = client.configuration_manager.render_template(
        template=template, variables=variables
    )
    return models.RenderTemplateResponse(result=data)
