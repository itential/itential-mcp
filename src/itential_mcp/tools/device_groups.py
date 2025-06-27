# Copyright (c) 2025 Itential, Inc
# GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)

from typing import Annotated

from pydantic import Field

from fastmcp import Context


async def get_device_groups(
    ctx: Annotated[Context, Field(
        description="The FastMCP Context object"
    )],
) -> list[dict]:
    """
    Get all device groups from Itential Platform server

    This tool will retrieve all of the configured device groups from
    Itential Platform server.  The response includes a list of elements
    where each element represents a unique device group.

    Each element has the following fields:

        * id: The unique identifier for the group
        * name: The name of the device group
        * devices: The list of device names that comprise this group
        * description: A short description of this device group
        * created: ISO 8601 timestamp of when the trigger was created
        * createdBy: Account name that created the trigger
        * updated: ISO 8601 timestamp of when the trigger was last updated
        * updatedBy: Account name that last updated the trigger
        * gbac: Returns the groups that have read and write access to this
            device group

    Args:
        ctx (Context): The FastMCP Context object

    Returns:
        dict: A Python list of dict objects that represents the list
            of device groups configured on Itential Platform

    Raises:
        None
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
    Create a new device group on Itential Server

    This tool will create a new device group on the server.  It has one
    required argument `name` which defines the name of the group to
    create.  If a group with the same name already exists, an
    error is returned, otherwise the group is created.

    The optional `description` argument sets a short description of
    the device group.

    The optional `devices` argument configures the list of devices to
    include in the device group.  The list of devices should be devices
    known to Itential Platform.  The list of devices can be found
    using the `get_devices` tool.

    This tool will return a message to indicate the device was created
    successfully.

        * id: The unqiue identifer for this device group
        * name: The name of the device group
        * message: Short status message describing the create operation
        * status: Current status of the device group.

    Args:
        ctx (Context): The FastMCP Context object

        name (str): The name of the device group to create

        description (str): Short description of the device group

        devices: (list): List of devices to add to the group when it is
            created

    Returns:
        dict: An object that provides the status of the device group
            create operation

    Raises:
        ValueError: Raised if a device group by the same name already
            exists on the server
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
