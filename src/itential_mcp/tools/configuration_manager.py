# Copyright (c) 2025 Itential, Inc
# GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)

from typing import Annotated

from pydantic import Field

from fastmcp import Context


__tags__ = ("configuration_manager",)


async def render_template(
    ctx: Annotated[Context, Field(
        description="The FastMCP Context object"
    )],
    template: Annotated[str, Field(
        description="The Jinja2 template string"
    )],
    variables: Annotated[dict, Field(
        description="Zero or more variables to associate with this template",
        default=None
    )]
) -> str:
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
        str: The fully rendered template with variables substituted
    """
    await ctx.info("inside render_template()")

    client = ctx.request_context.lifespan_context.get("client")

    body = {
        "template": template,
        "variables": variables or {}
    }

    res = await client.post(
        "/configuration_manager/jinja2",
        json=body
    )

    return res.json()
