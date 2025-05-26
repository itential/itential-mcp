# Copyright (c) 2025 Itential, Inc
# GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)

from fastmcp import Context


async def get_command_templates(ctx: Context) -> dict:
    """Get a list command templates from the Itential Platform API

    Command Templates are run-time templates that actively pass commands 
    to a list of specified devices during their runtime. After all responses 
    are collected, the output set is evaluated against a set of defined rules. 
    These executed templates are referred to as Pre and Post steps, which are 
    typically separated by a procedure (router upgrade, service migration, etc.).

    Args:

    Returns:
        An array of command templates. The "name" key is the command template 
        name to use in other operations

    Raises:
        None

    """
    await ctx.info("inside get_command_templates(...)")

    client = ctx.request_context.lifespan_context.get("client")

    results = {}

    uri = "/mop/listTemplates"

    res = await client.get(uri)
    data = res.json()
    results["command_templates"] = data

    return results

async def run_command_template(
    ctx: Context,
    name: str,
    devices: list[str],
    variables: dict | None = None
) -> dict:
    """
    Run a command template

    Command Templates are run-time templates that actively pass commands 
    to a list of specified devices during their runtime. After all responses 
    are collected, the output set is evaluated against a set of defined rules.
    This function provides a way to run a command template against an array of devices
    It will attempt to start the command template specified by the `name` argument.

    Args:
        ctx (Context): The FastMCP Context object
        name (str): The name of the command template to start
        devices: An array of devices. Must be an array even for a single device
        variables: (dict): One or more variables to inject into the command template
            when it is started. This variable object format can be obtained using 
            get_command_templates

    Returns:
        dict: A Python dict object that is the result document from Itential
            Platform workflow engine

    Raises:
        None
    """

    if variables is None:
        variables = {}

    await ctx.info("inside run_command_template(...)")

    client = ctx.request_context.lifespan_context.get("client")

    body = {
        "template": name,
        "variables": variables,
        "devices": devices
    }

    res = await client.post(
        "/mop/RunCommandTemplate",
        json=body
    )

    return res.json()
