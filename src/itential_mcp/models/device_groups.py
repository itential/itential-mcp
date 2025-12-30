# Copyright (c) 2025 Itential, Inc
# GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import annotations

import inspect
from typing import Annotated

from pydantic import BaseModel, Field, RootModel


class DeviceGroupElement(BaseModel):
    """
    Represents an individual device group element in Itential Platform.

    Device groups are logical collections of network devices that can be managed
    together for configuration, compliance, and automation tasks. This model contains
    all essential information about a single device group including its identity,
    member devices, and description.
    """

    object_id: Annotated[
        str,
        Field(
            alias="id",
            description=inspect.cleandoc(
                """
                Unique identifier for the device group
                """
            ),
        ),
    ]

    name: Annotated[
        str,
        Field(
            description=inspect.cleandoc(
                """
                Device group name
                """
            )
        ),
    ]

    devices: Annotated[
        list[str],
        Field(
            description=inspect.cleandoc(
                """
                List of device names in this group
                """
            ),
            default_factory=list,
        ),
    ]

    description: Annotated[
        str,
        Field(
            description=inspect.cleandoc(
                """
                Device group description
                """
            )
        ),
    ]


class GetDeviceGroupsResponse(RootModel):
    """
    Response model for retrieving all device groups from Itential Platform.

    This model wraps a list of DeviceGroupElement objects, providing a complete
    inventory of all device groups configured on the platform instance along
    with their member devices and metadata.
    """

    root: Annotated[
        list[DeviceGroupElement],
        Field(
            description=inspect.cleandoc(
                """
                List of device group objects with id, name, devices, and description
                """
            ),
            default_factory=list,
        ),
    ]


class CreateDeviceGroupResponse(BaseModel):
    """
    Response model for creating a device group on Itential Platform.

    Contains the result of a device group creation operation including the
    unique identifier, name, status message, and current status of the
    newly created device group.
    """

    object_id: Annotated[
        str,
        Field(
            alias="id",
            description=inspect.cleandoc(
                """
                Unique identifier for the created device group
                """
            ),
        ),
    ]

    name: Annotated[
        str,
        Field(
            description=inspect.cleandoc(
                """
                Name of the device group
                """
            )
        ),
    ]

    message: Annotated[
        str,
        Field(
            description=inspect.cleandoc(
                """
                Status message describing the create operation
                """
            )
        ),
    ]

    status: Annotated[
        str,
        Field(
            description=inspect.cleandoc(
                """
                Current status of the device group
                """
            )
        ),
    ]


class AddDevicesToGroupResponse(BaseModel):
    """
    Response model for adding devices to a device group on Itential Platform.

    Contains the result of adding one or more devices to an existing device
    group including the operation status and descriptive message.
    """

    status: Annotated[
        str,
        Field(
            description=inspect.cleandoc(
                """
                Message that provides the status of the operation
                """
            )
        ),
    ]

    message: Annotated[
        str,
        Field(
            description=inspect.cleandoc(
                """
                Short description of the status of the operation
                """
            )
        ),
    ]


class RemoveDevicesFromGroupResponse(BaseModel):
    """
    Response model for removing devices from a device group on Itential Platform.

    Contains the result of removing one or more devices from an existing device
    group including the operation status and count of devices that were removed.
    """

    status: Annotated[
        str,
        Field(
            description=inspect.cleandoc(
                """
                Message that provides the status of the operation
                """
            )
        ),
    ]

    message: Annotated[
        str,
        Field(
            description=inspect.cleandoc(
                """
                Short description of the status of the operation
                """
            )
        ),
    ]
