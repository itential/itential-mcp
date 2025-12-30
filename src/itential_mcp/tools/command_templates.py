# Copyright (c) 2025 Itential, Inc
# GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from typing import Annotated
from pydantic import Field

from fastmcp import Context
from itential_mcp.utilities import json as jsonutils
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

    Raises:
        Exception: If there is an error retrieving command templates from the platform
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

    Raises:
        Exception: If there is an error retrieving the command template or template is not found
    """
    await ctx.info("inside describe_command_template(...)")

    client = ctx.request_context.lifespan_context.get("client")

    data = await client.mop.describe_command_template(name=name, project=project)

    template = models.CommandTemplateDetail(**data)

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

    Raises:
        Exception: If there is an error running the command template or template is not found
    """
    await ctx.info("inside run_command_templates(...)")

    client = ctx.request_context.lifespan_context.get("client")

    data = await client.mop.run_command_template(
        name=name, devices=devices, project=project
    )

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

    Raises:
        Exception: If there is an error running the command on the devices
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


async def create_command_template(
    ctx: Annotated[Context, Field(description="The FastMCP Context object")],
    name: Annotated[str, Field(description="Name for the command template")],
    commands: Annotated[
        list[dict] | str,
        Field(description="List of commands with their validation rules"),
    ],
    project: Annotated[
        str | None,
        Field(
            description="Project name to create the template in (None for global templates)",
            default=None,
        ),
    ],
    description: Annotated[
        str | None,
        Field(
            description="Optional description for the template",
            default=None,
        ),
    ],
    os: Annotated[
        str,
        Field(
            description="Operating system type (default: empty string)",
            default="",
        ),
    ],
    pass_rule: Annotated[
        bool,
        Field(
            description="Pass rule configuration (True=all must pass, False=one must pass)",
            default=True,
        ),
    ],
    ignore_warnings: Annotated[
        bool,
        Field(
            description="Whether to ignore warnings during execution",
            default=False,
        ),
    ],
) -> models.CreateCommandTemplateResponse:
    """
    Create a new command template in Itential Platform.

    Creates a new command template with the specified name, commands, and validation rules.
    Templates can be created in the global space or within a specific project.

    Args:
        ctx (Context): The FastMCP Context object
        name (str): Name for the command template
        commands (list[dict]): List of commands with their validation rules. Each command should have:
            - command: The command string to execute (supports variable substitution <!variable!>)
            - passRule: Whether this command must pass (True/False)
            - rules: List of validation rules with eval, rule, and severity fields
                - eval: Evaluation type ("contains", "!contains", "contains1", "RegEx", "!RegEx", "#comparison")
                - rule: Rule pattern (string, regex, or with variable substitution <!variable!>)
                - severity: Severity level ("error", "warning", "info")
        project (str | None): Project name to create the template in (None for global templates)
        description (str | None): Optional description for the template
        os (str): Operating system type (default: empty string)
        pass_rule (bool): Pass rule configuration (True=all must pass, False=one must pass)
        ignore_warnings (bool): Whether to ignore warnings during execution

    Returns:
        CreateCommandTemplateResponse: Response containing creation result with template details

    Raises:
        ValueError: If the project name cannot be located
        Exception: If there is an error creating the command template

    Example:
        # Simple contains check
        commands = [
            {
                "command": "show version",
                "passRule": True,
                "rules": [
                    {
                        "rule": "Version 16.12",
                        "eval": "contains",
                        "severity": "error"
                    }
                ]
            }
        ]

        # Regex with variable substitution
        commands = [
            {
                "command": "show interfaces <!type!> <!interface!>.<!subInterface!>",
                "passRule": True,
                "rules": [
                    {
                        "rule": "<!type!><!interface!>.<!subInterface!>.*\\s+.*(down|up)",
                        "eval": "RegEx",
                        "severity": "error"
                    }
                ]
            }
        ]

        # Multiple evaluation types
        commands = [
            {
                "command": "show version",
                "passRule": True,
                "rules": [
                    {
                        "rule": "Version 16.12",
                        "eval": "contains",
                        "severity": "error"
                    },
                    {
                        "rule": "Version 15.0",
                        "eval": "!contains",
                        "severity": "warning"
                    }
                ]
            }
        ]
    """
    await ctx.info("inside create_command_template(...)")

    client = ctx.request_context.lifespan_context.get("client")

    # Parse commands if it's a JSON string
    if isinstance(commands, str):
        commands = jsonutils.loads(commands)

    data = await client.mop.create_command_template(
        name=name,
        commands=commands,
        project=project,
        description=description,
        os=os,
        pass_rule=pass_rule,
        ignore_warnings=ignore_warnings,
    )

    return models.CreateCommandTemplateResponse(**data)


async def update_command_template(
    ctx: Annotated[Context, Field(description="The FastMCP Context object")],
    name: Annotated[str, Field(description="Name of the command template to update")],
    commands: Annotated[
        list[dict] | str,
        Field(description="List of commands with their validation rules"),
    ],
    project: Annotated[
        str | None,
        Field(
            description="Project name containing the template (None for global templates)",
            default=None,
        ),
    ],
    description: Annotated[
        str | None,
        Field(
            description="Optional description for the template",
            default=None,
        ),
    ],
    os: Annotated[
        str,
        Field(
            description="Operating system type (default: empty string)",
            default="",
        ),
    ],
    pass_rule: Annotated[
        bool,
        Field(
            description="Pass rule configuration (True=all must pass, False=one must pass)",
            default=True,
        ),
    ],
    ignore_warnings: Annotated[
        bool,
        Field(
            description="Whether to ignore warnings during execution",
            default=False,
        ),
    ],
) -> models.UpdateCommandTemplateResponse:
    """
    Update an existing command template in Itential Platform.

    Updates an existing command template with new commands and validation rules.
    The template must exist in the specified project or global space.

    Args:
        ctx (Context): The FastMCP Context object
        name (str): Name of the command template to update
        commands (list[dict]): List of commands with their validation rules. Each command should have:
            - command: The command string to execute (supports variable substitution <!variable!>)
            - passRule: Whether this command must pass (True/False)
            - rules: List of validation rules with eval, rule, and severity fields
                - eval: Evaluation type ("contains", "!contains", "contains1", "RegEx", "!RegEx", "#comparison")
                - rule: Rule pattern (string, regex, or with variable substitution <!variable!>)
                - severity: Severity level ("error", "warning", "info")
        project (str | None): Project name containing the template (None for global templates)
        description (str | None): Optional description for the template
        os (str): Operating system type (default: empty string)
        pass_rule (bool): Pass rule configuration (True=all must pass, False=one must pass)
        ignore_warnings (bool): Whether to ignore warnings during execution

    Returns:
        UpdateCommandTemplateResponse: Response containing update result with operation status

    Raises:
        ValueError: If the project name cannot be located or template not found
        Exception: If there is an error updating the command template

    Example:
        # Simple contains check
        commands = [
            {
                "command": "show ip interface brief",
                "passRule": True,
                "rules": [
                    {
                        "rule": "up",
                        "eval": "contains",
                        "severity": "error"
                    }
                ]
            }
        ]

        # Regex with variable substitution
        commands = [
            {
                "command": "show interfaces <!type!> <!interface!>.<!subInterface!>",
                "passRule": True,
                "rules": [
                    {
                        "rule": "<!type!><!interface!>.<!subInterface!>.*\\s+.*(down|up)",
                        "eval": "RegEx",
                        "severity": "error"
                    }
                ]
            }
        ]

        # Multiple evaluation types
        commands = [
            {
                "command": "show version",
                "passRule": True,
                "rules": [
                    {
                        "rule": "Version 16.12",
                        "eval": "contains",
                        "severity": "error"
                    },
                    {
                        "rule": "Version 15.0",
                        "eval": "!contains",
                        "severity": "warning"
                    }
                ]
            }
        ]
    """
    await ctx.info("inside update_command_template(...)")

    client = ctx.request_context.lifespan_context.get("client")

    # Parse commands if it's a JSON string
    if isinstance(commands, str):
        commands = jsonutils.loads(commands)

    data = await client.mop.update_command_template(
        name=name,
        commands=commands,
        project=project,
        description=description,
        os=os,
        pass_rule=pass_rule,
        ignore_warnings=ignore_warnings,
    )
    return models.UpdateCommandTemplateResponse(**data)
