# Copyright (c) 2025 Itential, Inc
# GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)

from typing import Annotated

from pydantic import Field

from fastmcp import Context


async def get_devices(
    ctx: Annotated[Context, Field(
        description="The FastMCP Context object"
    )],
) -> list[dict]:
    """
    Retrieve all devies known to Itential Platform

    Itential Platform will federate device information from multiple
    sources and make it available to workflows for performing tasks
    against physical devices. This function will query Itential Platform
    and return all of the devices known to it.

    Args:
        ctx (Context): The FastMCP Context object

    Returns:
        dict: A Python list of dict objects that reprsesent all of the devices
            knownn to Itential Platform

    Raises:
        None
    """
    await ctx.info("inside get_devices(...)")

    client = ctx.request_context.lifespan_context.get("client")

    limit = 100
    start = 0

    results = list()

    while True:
        body = {
            "options": {
                "order": "ascending",
                "sort": [{"name": 1}],
                "start": start,
                "limit": limit
            }
        }

        res = await client.post(
            "/configuration_manager/devices",
            json=body,
        )

        data = res.json()

        results.extend(data["list"])

        if len(results) == data["return_count"]:
            break

        start += limit

    return results


async def get_device_configuration(
    ctx: Annotated[Context, Field(
        description="The FastMCP Context object"
        )],
    name: Annotated[str, Field(
        description="The name of the device to retrieve the configuration from"
    )]
) -> str:
    """
    Get the device current configuration

    This tool will get the current device configuration using Itential
    Platform.  The device configuration will be returned if the device
    is a valid device otherwise it will raise an error.

    Args:
        ctx (Context): The FastMCP Context object

        name (str): The name of the device to backup.  The device must be
            available in the list of devices returned from Itential Platform

    Returns:
        str: The current device configuration

    Raises:
        ValueError: When there is an exception making the API call
    """
    await ctx.info("inside get_device_configuration(...)")

    client = ctx.request_context.lifespan_context.get("client")

    try:
        res = await client.get(f"/configuration_manager/devices/{name}/configuration")
    except ValueError:
        raise

    return res.json()["config"]


async def backup_device_configuration(
    ctx: Annotated[Context, Field(
        description="The FastMCP Context object"
        )],
    name: Annotated[str, Field(
        description="The name of the device to backup"
    )],
    description: Annotated[str, Field(
        description="Short description to attach to the backup",
        default=None
    )],
    notes: Annotated[str, Field(
        description="Notes to attach to the backup",
        default=None
    )]
) -> dict:
    """
    Backup a device configuration to Itential Platform

    This tool will invoke an operation to backup the configuration of a
    specific device to Itential Platform.  The deivce's configuration will be
    backed up and added to the Itential Platform server.

    The returned object includes the following fields:

        * id: The unique identifer for the backup on the server.  This value
            can be used to retreive the backup later
        * status: The status of the backup operation job
        * message: A short descriptive message about the status of the job

    Args:
        ctx (Context): The FastMCP Context object

        name (str): The name of the device to backup.  The device must be
            available in the list of devices returned from Itential Platform

        description (str): Optional short description of the backup

        notes (str): Optional text notes to append to the backup for later
            reference

    Returns:
        dict: A Python dic object that returns the success or failure of the
            backup operation

    Raises:
        None
    """
    await ctx.info("inside backup_device_configuration(...)")

    client = ctx.request_context.lifespan_context.get("client")

    body = {
        "name": name,
        "options": {
            "description": description or "",
            "notes": notes or ""
        }
    }

    res = await client.post(
        "/configuration_manager/devices/backups",
        json=body
    )

    return res.json()
