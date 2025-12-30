# Copyright (c) 2025 Itential, Inc
# GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import annotations

import inspect

from typing import Annotated, Any

from pydantic import BaseModel, Field, RootModel


class ServiceElement(BaseModel):
    """Represents a single service from Gateway Manager.

    This model represents an individual service returned by the
    get_services API endpoint, containing information about the
    service's identity, type, and configuration.

    Attributes:
        name: The service name.
        cluster: The cluster name where the service is located.
        type: The service type (ansible-playbook, python-script, opentofu-plan).
        description: Short description of the service.
        decorator: JSON schema that defines the service input.
    """

    name: Annotated[
        str,
        Field(
            description=inspect.cleandoc(
                """
                The service name
                """
            )
        ),
    ]

    cluster: Annotated[
        str,
        Field(
            description=inspect.cleandoc(
                """
                The cluster name
                """
            )
        ),
    ]

    type: Annotated[
        str,
        Field(
            description=inspect.cleandoc(
                """
                The service type (ansible-playbook, python-script, opentofu-plan)
                """
            )
        ),
    ]

    description: Annotated[
        str | None,
        Field(
            description=inspect.cleandoc(
                """
                Short description of the service
                """
            )
        ),
    ]

    decorator: Annotated[
        Any,
        Field(
            description=inspect.cleandoc(
                """
                JSON schema that defines the service input
                """
            )
        ),
    ]


class GetServicesResponse(RootModel):
    """Response model for the get services API endpoint.

    This root model wraps a list of ServiceElement objects representing
    all services available through Gateway Manager.

    Attributes:
        root: List of service elements, each containing service details.
    """

    root: Annotated[
        list[ServiceElement],
        Field(
            description=inspect.cleandoc(
                """
                List of service objects with service metadata and configuration
                """
            )
        ),
    ]


class GatewayElement(BaseModel):
    """Represents a single gateway from Gateway Manager.

    This model represents an individual gateway returned by the
    get_gateways API endpoint, containing information about the
    gateway's identity, status, and configuration.

    Attributes:
        name: The gateway name.
        cluster: The cluster name where the gateway is located.
        description: Short description of the gateway.
        status: Current status of the gateway connection.
        enabled: Whether or not the gateway is enabled and usable.
    """

    name: Annotated[
        str,
        Field(
            description=inspect.cleandoc(
                """
                The gateway name
                """
            )
        ),
    ]

    cluster: Annotated[
        str,
        Field(
            description=inspect.cleandoc(
                """
                The cluster name
                """
            )
        ),
    ]

    description: Annotated[
        str,
        Field(
            description=inspect.cleandoc(
                """
                Short description of the gateway
                """
            )
        ),
    ]

    status: Annotated[
        str,
        Field(
            description=inspect.cleandoc(
                """
                Current status of the gateway connection
                """
            )
        ),
    ]

    enabled: Annotated[
        bool,
        Field(
            description=inspect.cleandoc(
                """
                Whether or not the gateway is enabled and usable
                """
            )
        ),
    ]


class GetGatewaysResponse(RootModel):
    """Response model for the get gateways API endpoint.

    This root model wraps a list of GatewayElement objects representing
    all gateways available through Gateway Manager.

    Attributes:
        root: List of gateway elements, each containing gateway details.
    """

    root: Annotated[
        list[GatewayElement],
        Field(
            description=inspect.cleandoc(
                """
                List of gateway objects with gateway metadata and status
                """
            )
        ),
    ]


class RunServiceResponse(BaseModel):
    """Response model for the run service API operation.

    This model represents the response returned when running a service
    through Gateway Manager, containing execution results and metadata.

    Attributes:
        stdout: The output sent to stdout.
        stderr: The output sent to stderr.
        return_code: The return code generated by the service.
        start_time: The start time when the service was started.
        end_time: The end time when the service run completed.
        elapsed_time: The number of seconds the service ran for.
    """

    stdout: Annotated[
        str | dict | None,
        Field(
            description=inspect.cleandoc(
                """
                The output sent to stdout
                """
            ),
            default=None,
        ),
    ]

    stderr: Annotated[
        str | None,
        Field(
            description=inspect.cleandoc(
                """
                The output sent to stderr
                """
            ),
            default=None,
        ),
    ]

    return_code: Annotated[
        int,
        Field(
            description=inspect.cleandoc(
                """
                The return code generated by the service
                """
            )
        ),
    ]

    start_time: Annotated[
        str,
        Field(
            description=inspect.cleandoc(
                """
                The start time when the service was started
                """
            )
        ),
    ]

    end_time: Annotated[
        str,
        Field(
            description=inspect.cleandoc(
                """
                The end time when the service run completed
                """
            )
        ),
    ]

    elapsed_time: Annotated[
        float,
        Field(
            description=inspect.cleandoc(
                """
                The number of seconds the service ran for
                """
            )
        ),
    ]
