# Copyright (c) 2025 Itential, Inc
# GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import annotations

import inspect

from typing import Annotated

from pydantic import BaseModel, Field, RootModel


class Device(BaseModel):
    """Represents a network device from the Itential platform.

    This model defines the structure for device information returned from
    the Configuration Manager API endpoints. Devices represent physical or
    virtual network infrastructure that can be managed, configured, and monitored.

    Attributes:
        name: The unique identifier name of the device.
        host: The hostname or IP address of the device.
        deviceType: The type of device (e.g., 'cisco_ios', 'juniper').
        status: Current operational status of the device.
        Additional fields may be present depending on the device and platform configuration.
    """

    name: Annotated[
        str,
        Field(
            description=inspect.cleandoc(
                """
                The unique identifier name of the device
                """
            )
        ),
    ]

    host: Annotated[
        str,
        Field(
            description=inspect.cleandoc(
                """
                The hostname or IP address of the device
                """
            )
        ),
    ]

    deviceType: Annotated[
        str | None,
        Field(
            default=None,
            description=inspect.cleandoc(
                """
                The type of device (e.g., 'cisco_ios', 'juniper')
                """
            ),
        ),
    ]

    status: Annotated[
        str | None,
        Field(
            default=None,
            description=inspect.cleandoc(
                """
                Current operational status of the device
                """
            ),
        ),
    ]

    # Allow additional fields that may be present in device objects
    model_config = {"extra": "allow"}


class GetDevicesResponse(RootModel[list[Device]]):
    """Response model for get_devices function.

    This model represents the complete response from the get_devices function,
    which returns a list of devices available in the Configuration Manager.
    """

    root: list[Device]


class GetDeviceConfigurationResponse(RootModel[str]):
    """Response model for get_device_configuration function.

    This model represents the response from the get_device_configuration function,
    which returns the current configuration of a network device as a string.
    """

    root: str


class BackupDeviceConfigurationResponse(BaseModel):
    """Response model for backup_device_configuration function.

    This model defines the structure for the response returned when creating
    a backup of a device configuration in the Configuration Manager.

    Attributes:
        id: Unique identifier for the created backup.
        status: Status of the backup operation.
        message: Descriptive message about the operation status.
    """

    id: Annotated[
        str,
        Field(
            description=inspect.cleandoc(
                """
                Unique identifier for the backup
                """
            )
        ),
    ]

    status: Annotated[
        str,
        Field(
            description=inspect.cleandoc(
                """
                Status of the backup operation
                """
            )
        ),
    ]

    message: Annotated[
        str,
        Field(
            description=inspect.cleandoc(
                """
                Descriptive message about the operation status
                """
            )
        ),
    ]

    # Allow additional fields that may be present in the response
    model_config = {"extra": "allow"}


class ApplyDeviceConfigurationResponse(BaseModel):
    """Response model for apply_device_configuration function.

    This model defines the structure for the response returned when applying
    configuration commands to a network device through the Configuration Manager.

    Attributes:
        The exact structure depends on the platform response and may vary.
        Additional fields may be present depending on the device and operation.
    """

    # Allow all fields since the exact response structure may vary
    model_config = {"extra": "allow"}
