# Copyright (c) 2025 Itential, Inc
# GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)

from typing import Annotated
from pydantic import Field

from fastmcp import Context
from itential_mcp.models import command_templates as models


__tags__ = ("automation_studio",)


async def get_command_templates(
    ctx: Annotated[Context, Field(description="The FastMCP Context object")],
) -> models.GetCommandTemplatesResponse:
    """
    Get all command templates from Itential Platform.

    Command Templates are run-time templates that actively pass commands to devices
    and evaluate responses against defined rules. Retrieves templates from both
    global space and projects.

    Args:
        ctx (Context): The FastMCP Context object

    Returns:
        GetCommandTemplatesResponse: Response containing list of command template objects
    """
    await ctx.info("inside get_command_templates(...)")

    client = ctx.request_context.lifespan_context.get("client")

    res = await client.mop.get_command_templates()

    results = list()

    for item in res:
        template = models.CommandTemplate(
            **item  # Use dict unpacking to handle the _id alias automatically
        )
        results.append(template)

    return models.GetCommandTemplatesResponse(templates=results)


async def describe_command_template(
    ctx: Annotated[Context, Field(description="The FastMCP Context object")],
    name: Annotated[
        str, Field(description="The name of the command template to describe")
    ],
    project: Annotated[
        str | None,
        Field(
            description="The name of the project to get the command template from",
            default=None,
        ),
    ],
) -> models.DescribeCommandTemplateResponse:
    """
    Get detailed information about a specific command template.

    Args:
        ctx (Context): The FastMCP Context object
        name (str): Name of the command template to describe
        project (str | None): Project name containing the template (None for global templates)

    Returns:
        DescribeCommandTemplateResponse: Response containing detailed command template information
    """
    await ctx.info("inside describe_command_template(...)")

    client = ctx.request_context.lifespan_context.get("client")

    data = await client.mop.describe_command_template(
        name=name, project=project
    )

    template = models.CommandTemplateDetail(
        **data  # Use dict unpacking to handle the _id alias automatically
    )

    return models.DescribeCommandTemplateResponse(template=template)


async def run_command_template(
    ctx: Annotated[Context, Field(description="The FastMCP Context object")],
    name: Annotated[str, Field(description="The name of the command template to run")],
    devices: Annotated[
        list,
        Field(description="The list of devices to run the command template against"),
    ],
    project: Annotated[
        str | None,
        Field(description="Project that contains the command template", default=None),
    ],
) -> models.RunCommandTemplateResponse:
    """
    Execute a command template against specified devices with rule evaluation.

    Command Templates are run-time templates that actively pass commands to a list
    of specified devices during their runtime. After all responses are collected,
    the output set is evaluated against a set of defined rules. These executed
    templates are typically used as Pre and Post steps, which are usually separated
    by a procedure (router upgrade, service migration, etc.).

    Args:
        ctx (Context): The FastMCP Context object
        name (str): Name of the command template to run
        devices (list): List of device names to run the template against. Use `get_devices` to see available devices.
        project (str | None): Project containing the template (None for global templates)

    Returns:
        RunCommandTemplateResponse: Response containing execution results with template name,
            pass flag, and detailed command results for each device
    """
    await ctx.info("inside run_command_templates(...)")

    client = ctx.request_context.lifespan_context.get("client")

    data = await client.mop.run_command_template(
        name=name, devices=devices, project=project
    )

    # Parse command results
    command_results = []

    for result in data.get("command_results", []):
        rules = []
        for rule_data in result.get("rules", []):
            rule = models.RuleEvaluation(
                eval=rule_data["eval"],
                rule=rule_data["rule"],
                severity=rule_data["severity"],
                result=rule_data["result"],
            )
            rules.append(rule)

        cmd_result = models.CommandResult(
            raw=result["raw"],
            evaluated=result["evaluated"],
            device=result["device"],
            response=result["response"],
            rules=rules,
        )
        command_results.append(cmd_result)

    return models.RunCommandTemplateResponse(
        name=data["name"],
        all_pass_flag=data["all_pass_flag"],
        command_results=command_results,
    )


async def run_command(
    ctx: Annotated[Context, Field(description="The FastMCP Context object")],
    cmd: Annotated[str, Field(description="The command to run on the devices")],
    devices: Annotated[
        list[str], Field(description="The list of devices to run the command on")
    ],
) -> models.RunCommandResponse:
    """
    Run a single command against multiple devices.

    Args:
        ctx (Context): The FastMCP Context object
        cmd (str): Command to execute on the devices
        devices (list[str]): List of device names. Use `get_devices` to see available devices.

    Returns:
        RunCommandResponse: Response containing list of command execution results for each device
    """
    await ctx.info("inside run_command(...)")

    client = ctx.request_context.lifespan_context.get("client")

    res = await client.mop.run_command(cmd=cmd, devices=devices)

    results = []
    for item in res:
        result = models.DeviceCommandResult(
            device=item["device"],
            command=item["raw"],
            response=item["response"],
        )
        results.append(result)

    return models.RunCommandResponse(results=results)
