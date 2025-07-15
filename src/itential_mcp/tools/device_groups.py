# Copyright (c) 2025 Itential, Inc
# GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)

from typing import Annotated

from pydantic import Field

from fastmcp import Context


__tags__ = ("configuration_manager", "devices")


async def get_device_groups(
    ctx: Annotated[Context, Field(
        description="The FastMCP Context object"
    )],
) -> list[dict]:
    """
    Get all device groups from Itential Platform.

    Device groups are logical collections of network devices that can be managed
    together for configuration, compliance, and automation tasks. They provide
    an organizational structure for grouping devices by function, location, or type.

    Args:
        ctx (Context): The FastMCP Context object

    Returns:
        list[dict]: List of device group objects with the following fields:
            - id: Unique identifier for the group
            - name: Device group name
            - devices: List of device names in this group
            - description: Device group description
    """
    await ctx.info("inside get_device_groups(...)")

    client = ctx.request_context.lifespan_context.get("client")

    results = list()

    res = await client.get("/configuration_manager/deviceGroups")

    data = res.json()

    for ele in data:
        results.append({
            "id": ele["id"],
            "name": ele["name"],
            "devices": ele["devices"],
            "description": ele["description"],
        })

    #for ele in data:
    #    for gbac in ("read", "write"):
    #        items = list()
    #        for item in ele["gbac"][gbac]:
    #            items.append(await functions.group_id_to_name(ctx, item))
    #        ele["gbac"][gbac] = items
    #    results.append(ele)

    return results


async def create_device_group(
    ctx: Annotated[Context, Field(
        description="The FastMCP Context object"
    )],
    name: Annotated[str, Field(
        description="The name of the device group to create"
    )],
    description: Annotated[str | None, Field(
        description="Short description of the device group",
        default=None
    )],
    devices: Annotated[list | None, Field(
        description="List of devices to add to the group",
        default=None
    )]
) -> dict:
    """
    Create a new device group on Itential Platform.

    Device groups enable logical organization of network devices for streamlined
    management, configuration deployment, and automation workflows.

    Args:
        ctx (Context): The FastMCP Context object
        name (str): Name of the device group to create
        description (str | None): Short description of the device group (optional)
        devices (list | None): List of device names to include in the group. Use `get_devices` to see available devices. (optional)

    Returns:
        dict: Creation operation result with the following fields:
            - id: Unique identifier for the created device group
            - name: Name of the device group
            - message: Status message describing the create operation
            - status: Current status of the device group

    Raises:
        ValueError: If a device group with the same name already exists
    """
    await ctx.info("inside create_device_group(...)")

    client = ctx.request_context.lifespan_context.get("client")

    groups = await get_device_groups(ctx)

    for ele in groups:
        if ele["name"] == name:
            raise ValueError(f"device group {name} already exists")

    body = {
        "groupName": name,
        "groupDescription": description
    }

    if devices:
        body["deviceNames"] = ",".join(devices)

    res = await client.post(
        "/configuration_manager/devicegroup",
        json=body
    )

    return res.json()
