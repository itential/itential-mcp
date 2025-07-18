# Copyright (c) 2025 Itential, Inc
# GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)

from typing import Annotated
from pydantic import Field

from fastmcp import Context


__tags__ = ("automation_studio",)


async def _get_project_id_from_name(ctx: Context, name: str) -> str:
    """
    Get the project ID for a specified project name.

    Args:
        ctx (Context): The FastMCP Context object
        name (str): Case-sensitive project name to locate

    Returns:
        str: The project ID associated with the project name

    Raises:
        ValueError: If the project name cannot be definitively located
    """
    client = ctx.request_context.lifespan_context.get("client")

    res = await client.get(
        "/automation-studio/projects",
        params={"equals[name]": name}
    )

    data = res.json()

    if len(data["data"]) != 1:
        raise ValueError(f"unable to locate project `{name}`")

    return data["data"][0]["_id"]


async def get_command_templates(
    ctx: Annotated[Context, Field(
        description="The FastMCP Context object"
    )]
) -> list[dict]:
    """
    Get all command templates from Itential Platform.

    Command Templates are run-time templates that actively pass commands to devices
    and evaluate responses against defined rules. Retrieves templates from both
    global space and projects.

    Args:
        ctx (Context): The FastMCP Context object

    Returns:
        list[dict]: List of command template objects with the following fields:
            - _id: Unique identifier
            - name: Template name
            - description: Template description
            - namespace: Project namespace (null for global templates)
            - passRule: Pass rule configuration (True=all must pass, False=one must pass)
    """
    await ctx.info("inside get_command_templates(...)")

    client = ctx.request_context.lifespan_context.get("client")

    res = await client.get("/mop/listTemplates")

    results = list()

    for item in res.json():
        results.append({
            "_id": item["_id"],
            "name": item["name"],
            "description": item["description"],
            "namespace": item["namespace"],
            "passRule": item["passRule"],
        })

    return results

async def describe_command_template(
    ctx: Annotated[Context, Field(
        description="The FastMCP Context object"
    )],
    name: Annotated[str, Field(
        description="The name of the command template to describe"
    )],
    project: Annotated[str | None, Field(
        description="The name of the project to get the command template from",
        default=None
    )]
) -> dict:
    """
    Get detailed information about a specific command template.

    Args:
        ctx (Context): The FastMCP Context object
        name (str): Name of the command template to describe
        project (str | None): Project name containing the template (None for global templates)

    Returns:
        dict: Command template details with the following fields:
            - _id: Unique identifier
            - name: Template name
            - commands: List of commands and associated rules
            - namespace: Project namespace (null for global templates)
            - passRule: Pass rule configuration (True=all must pass, False=one must pass)
    """
    await ctx.info("inside describe_command_template(...)")

    client = ctx.request_context.lifespan_context.get("client")

    if project is not None:
        project_id = await _get_project_id_from_name(ctx, project)
        name = f"@{project_id}: {name}"

    res = await client.get(f"/mop/listATemplate/{name}")

    data = res.json()[0]

    return {
        "_id": data["_id"],
        "name": data["name"],
        "passRule": data["passRule"],
        "commands": data["commands"],
        "namespace": data["namespace"]
    }


async def run_command_template(
    ctx: Annotated[Context, Field(
        description="The FastMCP Context object"
    )],
    name: Annotated[str, Field(
        description="The name of the command template to run"
    )],
    devices: Annotated[list, Field(
        description="The list of devices to run the command template against"
    )],
    project: Annotated[str | None, Field(
        description="Project that contains the command template",
        default=None
    )]
) -> dict:
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
        dict: Execution results with the following structure:
            - name: Command template name that was executed
            - all_pass_flag: Whether all rules must pass for success
            - command_results: List of results for each command/device combination:
                - raw: Original command executed on the remote device
                - evaluated: Command sent to the device
                - device: Target device name
                - response: Device response used for rule evaluation
                - rules: Rule evaluation results with fields:
                    - eval: Type of rule evaluation performed
                    - rule: Data used for performing the rule check
                    - severity: Severity of error if rule matches
                    - result: Result from the rule check
    """
    await ctx.info("inside run_command_templates(...)")

    client = ctx.request_context.lifespan_context.get("client")

    if project is not None:
        project_id = await _get_project_id_from_name(ctx, project)
        name = f"@{project_id}: {name}"

    body = {
        "template": name,
        "devices": devices,
    }

    res = await client.post("/mop/RunCommandTemplate", json=body)

    return res.json()


async def run_command(
    ctx: Annotated[Context, Field(
        description="The FastMCP Context object"
    )],
    cmd: Annotated[str, Field(
        description="The command to run on the devices"
    )],
    devices: Annotated[list[str], Field(
        description="The list of devices to run the command on"
    )]
) -> list[dict]:
    """
    Run a single command against multiple devices.

    Args:
        ctx (Context): The FastMCP Context object
        cmd (str): Command to execute on the devices
        devices (list[str]): List of device names. Use `get_devices` to see available devices.

    Returns:
        list[dict]: List of command execution results with the following fields:
            - device: Target device name
            - command: Command sent to the device
            - response: Output from running the command
    """
    await ctx.info("inside run_command(...)")

    client = ctx.request_context.lifespan_context.get("client")

    body = {
        "command": cmd,
        "devices": devices,
    }

    res = await client.post("/mop/RunCommandDevices", json=body)

    results = list()

    for item in res.json():
        results.append({
            "device": item["device"],
            "command": item["raw"],
            "response": item["response"],
        })

    return results
