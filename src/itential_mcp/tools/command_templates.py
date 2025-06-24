# Copyright (c) 2025 Itential, Inc
# GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)

from typing import Annotated
from pydantic import Field

from fastmcp import Context

from itential_mcp import timeutils


async def _get_project_id_from_name(ctx: Context, name: str) -> str:
    """
    Gets the project ID for the specified project name

    This function will attempt to get the project id based on the name
    of the project.  It will query the server to get the project by name
    and return the project id.  If the project name doesn't not match
    on the server, a ValueError will be raised.

    Note the project name is case sensitive

    Args:
        ctx (Context): The FastMCP Context object
        name (str): The name of the project to locate

    Returns:
        str: The project ID associdated with the project name

    Raises:
        ValueError: Exception raised when the project name could not be
            deinitively located on the server
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
    Get a list of command templates from Itential Platform

    This tool will get the list of command templates from Itential
    Platform.  It will retreive command templates defined in global
    space and in projects and return them as a list of Python dict
    elements.

    The elements contain the following fields:

        *_id: The unique identifier for this element
        * name: The name of the command template
        * description: Short description of the command template
        * namespace: Defines the project the template is part of.  If this
            field is null, the command template is in the global namespace
        * passRule: Configures the rules for passing.  When this value is
            set to True, all commands must pass and when this value is
            set to False, only one of the define commands must pass
        * created: ISO 8601 timestamp of when the trigger was created
        * createdBy: Account name that created the trigger
        * updated: ISO 8601 timestamp of when the trigger was last updated
        * updatedBy: Account name that last updated the trigger

    Args:
        ctx (Context): The FastMCP Context object

    Returns:
        list[dict]: A Python list of dict objects that represent the available
            workflows found on the server.

    Raises:
        None
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
            "created": timeutils.epoch_to_timestamp(item["created"]),
            "createdBy": item["createdBy"],
            "updated": timeutils.epoch_to_timestamp(item["lastUpdated"]),
            "updatedBy": item["lastUpdatedBy"],
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
    Get details about a specific command template

    This tool will retrieve a specific command template defined by the
    `name` argument and return its details.  If the command template is
    in a project, the project name must also be provided using the optional
    `project` argument.  If the `project` argument is None, only command
    templates defined in global space will be considered.

    The tool will return a dict object that represents the command template
    with the following structure:

        * _id: The unique identifier for this command template
        * name: The name of the command template
        * commands: The list of commands and rules associatedw this command
            template
        * namespace: Defines the project the template is part of.  If this
            field is null, the command template is in the global namespace
        * passRule: Configures the rules for passing.  When this value is
            set to True, all commands must pass and when this value is
            set to False, only one of the define commands must pass
        * created: ISO 8601 timestamp of when the trigger was created
        * createdBy: Account name that created the trigger
        * updated: ISO 8601 timestamp of when the trigger was last updated
        * updatedBy: Account name that last updated the trigger

    Args:
        ctx (Context): The FastMCP Context object
        name (str): The name of the command template to run
        devices (list): A list of devices to run the command template
            against.  The devices in this list must be known to Itential
            Platform.  To see the list of devices, use the `get_devices(...)`
            tool.

    Returns:
        list[dict]: A Python list of dict objects that represent the available
            workflows found on the server.

    Raises:
        None
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
        "created": timeutils.epoch_to_timestamp(data["created"]),
        "createdBy": data["createdBy"],
        "updated": timeutils.epoch_to_timestamp(data["lastUpdated"]),
        "updatedBy": data["lastUpdatedBy"],
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
    Runs the command template against the list of devices

    This tool will run the named command template against one or more
    devices defined in the `devices` argument and return the results.  The
    response is an array that includes an element for each device response
    for each command run.

    Command Results
    The command results return the following keys:

        * raw: The command executed on the remote device
        * all_pass_flag: Boolean that indicates whether or not all rules
            must pass
        * evaluated: The command sent to the device
        * parameters: ???
        * rules: One or more rules to be evaluated when the command
            template is run.  See Rules for details on the returned
            object
        * device: The name of the device associated with this result
        * response: The response from the device used to run rules against
        * result: ???

    Rules:
    A command template can define one or more rules to validate the response
    against.  Rules are defined using the following structure:

        * eval: Type of rule evaluation to be performed
        * rule: The data to use for performing the rule check
        * severity: The severity of the error if the rule matches
        * raw: The raw data used when performing the rule check
        * result: The result from the rule check

    Once all commands have been executed against all devices and all rules
    have been processed, this function will return the final results

        * name: The name of the command template that was executed
        * all_pass_flag: Boolean that indicates whether or not all rules
            must pass
        * command_results: A list of elements one for each command executed
            on a device.  See `Command Results` for details about the return
            fields.

    Args:
        ctx (Context): The FastMCP Context object
        name (str): The name of the command template to run
        devices (list): A list of devices to run the command template
            against.  The devices in this list must be known to Itential
            Platform.  To see the list of devices, use the `get_devices(...)`
            tool.

    Returns:
        list[dict]: A Python list of dict objects that represent the available
            workflows found on the server.

    Raises:
        None
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
    Run a command against one or more devices

    This tool will run a command defined in the `cmd` argument against a
    list of devices from Itential Platform.  The command responses are
    returned.   The devices list must be the name of the device as known
    to Itential Platform.  To get a list of all devices using the
    `get_devices(...)` tool.

    The response is a list of dict elements with the following defined
    fields:

        * device: The name of the device the command was run against
        * command: The command sent to the device
        * response: The output from running the command on the device

    Args:
        ctx (Context): The FastMCP Context object
        name (str): The name of the command template to run
        devices (list): A list of devices to run the command template
            against.  The devices in this list must be known to Itential
            Platform.  To see the list of devices, use the `get_devices(...)`
            tool.

    Returns:
        list[dict]: A list of dict objects that represent the results from
            running the command on a device

    Raises:
        None
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
