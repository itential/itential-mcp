# Copyright (c) 2025 Itential, Inc
# GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from typing import Annotated

from pydantic import Field

from fastmcp import Context

from itential_mcp.models import device_groups as models


__tags__ = ("configuration_manager",)


async def get_device_groups(
    ctx: Annotated[Context, Field(description="The FastMCP Context object")],
) -> models.GetDeviceGroupsResponse:
    """
    Get all device groups from Itential Platform.

    Device groups are logical collections of network devices that can be managed
    together for configuration, compliance, and automation tasks. They provide
    an organizational structure for grouping devices by function, location, or type.

    Args:
        ctx (Context): The FastMCP Context object

    Returns:
        GetDeviceGroupsResponse: List of device group objects with the following fields:
            - id: Unique identifier for the group
            - name: Device group name
            - devices: List of device names in this group
            - description: Device group description

    Raises:
        Exception: If there is an error retrieving device groups from the platform
    """
    await ctx.info("inside get_device_groups(...)")

    client = ctx.request_context.lifespan_context.get("client")

    data = await client.configuration_manager.get_device_groups()

    return models.GetDeviceGroupsResponse(
        [models.DeviceGroupElement(**ele) for ele in data]
    )


async def create_device_group(
    ctx: Annotated[Context, Field(description="The FastMCP Context object")],
    name: Annotated[str, Field(description="The name of the device group to create")],
    description: Annotated[
        str | None,
        Field(description="Short description of the device group", default=None),
    ],
    devices: Annotated[
        list | None,
        Field(description="List of devices to add to the group", default=None),
    ],
) -> models.CreateDeviceGroupResponse:
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
        CreateDeviceGroupResponse: Creation operation result with the following fields:
            - id: Unique identifier for the created device group
            - name: Name of the device group
            - message: Status message describing the create operation
            - status: Current status of the device group

    Raises:
        ValueError: If a device group with the same name already exists
    """
    await ctx.info("inside create_device_group(...)")

    client = ctx.request_context.lifespan_context.get("client")

    res = await client.configuration_manager.create_device_group(
        name=name, description=description, devices=devices
    )

    return models.CreateDeviceGroupResponse(**res)


async def add_devices_to_group(
    ctx: Annotated[Context, Field(description="The FastMCP Context object")],
    name: Annotated[
        str, Field(description="The name of the device group to add devices to")
    ],
    devices: Annotated[
        list | None,
        Field(
            description="List of devices to add to the group",
        ),
    ],
) -> models.AddDevicesToGroupResponse:
    """
    Add one or more devices to a device group

    This tool will add one or more devices to a named device group defined
    in Itential Platform.  The name argument specifies the name of the device
    group to add the list of devices to.  The name must be a valid device
    group.  The list of named device groups can be found using the
    get_device_groups tool.

    The devices argument provides the list of devices to be added to the
    named device group.

    Args:
        ctx (Context): The FastMCP Context object

        name (str): The name of the device group to add devices too

        devices (list[str]): The list of device names to add to the
            device group

    Returns:
        AddDevicesToGroupResponse: An object representing the status of the operation with the
            following fields:
            - status: Message that provides the status of the operation
            - message: Short description of the status of the operation

    Raises:
        Exception: If there is an error adding devices to the group

    """
    await ctx.info("inside add_devices_to_group(...)")

    client = ctx.request_context.lifespan_context.get("client")

    data = await client.configuration_manager.add_devices_to_group(name, devices)

    return models.AddDevicesToGroupResponse(
        status=data["status"], message=data.get("message", "Devices added successfully")
    )


async def remove_devices_from_group(
    ctx: Annotated[Context, Field(description="The FastMCP Context object")],
    name: Annotated[
        str, Field(description="The name of the device group to remove devices from")
    ],
    devices: Annotated[
        list[str] | None, Field(description="List of devices to remove from the group")
    ],
) -> models.RemoveDevicesFromGroupResponse:
    """
    Remove one or more devices from a device group

    This tool will remove one or more devices from a named device group.
    The name argument specifies the name of the device group to remove the
    list of devices from.  The name must be a valid device group.  The
    list of device groups can be found using the get_device_groups
    tool.

    The devices argument provides the list of devices to be removed from
    the device group.

    Args:
        ctx (Context): The FastMCP Context object

        name (str): The name of the device group to remove devices from

        devices (list[str]): The list of device names to remove from the
            device group

    Returns:
        RemoveDevicesFromGroupResponse: An object representing the status of the operation with the
            following fields:
            - status: Message that provides the status of the operation
            - message: Short description of the status of the operation

    Raises:
        Exception: If there is an error removing devices from the group
    """
    await ctx.info("inside remove_devices_from_group(...)")

    client = ctx.request_context.lifespan_context.get("client")

    data = await client.configuration_manager.remove_devices_from_group(name, devices)

    return models.RemoveDevicesFromGroupResponse(
        status=data["status"],
        message=data.get("message", "Devices removed successfully"),
    )
