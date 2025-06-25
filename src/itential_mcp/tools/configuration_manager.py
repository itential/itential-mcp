# Copyright (c) 2025 Itential, Inc
# GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)

from typing import Annotated

from pydantic import Field

from fastmcp import Context


async def render_template(
    ctx: Annotated[Context, Field(
        description="The FastMCP Context object"
    )],
    template: Annotated[str, Field(
        description="The Jinaj2 template string"
    )],
    variables: Annotated[dict, Field(
        description="Zero or more variables to associate with this template",
        default=None
    )]
) -> str:
    """
    Renders a Jinja2 template

    This tool will take a Jinja2 template and set of variables and render
    the string.  The template argument defines the Jinja2 template and
    the variables argument is a Python dict that defines the values.

    The returned string is the fully rendered Jinaj2 template.

    Args:
        ctx (Context): The FastMCP Context object

        template (str): The Jinja2 template string to render

        variables (dict): Zero or more key value pairs as a Python dict
            to add to the configuration template

    Returns:
        str: A Python dict object that represents the rendered template

    Raises:
        None
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
