# Copyright (c) 2025 Itential, Inc
# GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)

from typing import Annotated

from pydantic import Field

from fastmcp import Context


__tags__ = ("configuration_manager",)


async def get_devices(
    ctx: Annotated[Context, Field(
        description="The FastMCP Context object"
    )],
) -> list[dict]:
    """
    Get all devices known to Itential Platform.

    Itential Platform federates device information from multiple sources and makes
    it available for network automation workflows. Devices represent physical or
    virtual network infrastructure that can be managed, configured, and monitored.

    Args:
        ctx (Context): The FastMCP Context object

    Returns:
        list[dict]: List of device objects containing device information and metadata
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
    Retrieve the current configuration from a network device.

    Args:
        ctx (Context): The FastMCP Context object
        name (str): Name of the device to retrieve configuration from. Use `get_devices` to see available devices.

    Returns:
        str: The current device configuration

    Raises:
        ValueError: If there is an error retrieving the configuration or device is not found
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
    Create a backup of a device configuration in Itential Platform.

    Configuration backups provide recovery points and change tracking for network
    devices, enabling rollback capabilities and configuration management workflows.

    Args:
        ctx (Context): The FastMCP Context object
        name (str): Name of the device to backup. Use `get_devices` to see available devices.
        description (str): Short description of the backup (optional)
        notes (str): Additional notes for the backup (optional)

    Returns:
        dict: Backup operation result with the following fields:
            - id: Unique identifier for the backup
            - status: Status of the backup operation
            - message: Descriptive message about the operation status
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


async def apply_device_configuration(
    ctx: Annotated[Context, Field(
        description="The FastMCP Context object"
        )],
    device: Annotated[str, Field(
        description="The name of the device to apply the configuration to"
    )],
    config: Annotated[str, Field(
        description="The configuration to apply to the device"
    )]
) -> dict:
    """
    Apply configuration commands to a network device through Itential Platform.

    Configuration deployment enables automated provisioning and updates of network
    device settings, supporting configuration management and infrastructure automation.

    Args:
        ctx (Context): The FastMCP Context object
        device (str): Name of the target device. Use `get_devices` to see available devices.
        config (str): Configuration string to apply to the device

    Returns:
        dict: Configuration application results and operation status
    """
    await ctx.info("inside apply_device_configuration(...)")

    client = ctx.request_context.lifespan_context.get("client")

    body = {
        "config": {
            "device": device,
            "config": config,
        }
    }

    res = await client.post(
        f"/configuration_manager/devices/{device}/configuration",
        json=body
    )

    return res.json()
