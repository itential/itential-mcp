# Copyright (c) 2025 Itential, Inc
# GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)

import inspect

from typing import Literal, List, Annotated

from pydantic import BaseModel, RootModel, Field


class GetAdaptersElement(BaseModel):
    """Represents a single adapter configuration element.

    This model represents an individual adapter returned by the
    get adapters API endpoint, containing information about the
    adapter's identity, package details, and operational state.

    Attributes:
        name: The unique name identifier of the adapter.
        package: The NodeJS package name for the adapter.
        version: The version string of the adapter.
        description: A brief description of what the adapter does.
        state: The current operational state of the adapter.
    """

    name: Annotated[
        str,
        Field(
            description = inspect.cleandoc(
                """
                The name of the adapter
                """
            )
        )
    ]

    package: Annotated[
        str,
        Field(
            description = inspect.cleandoc(
                """
                The NodeJS package name for the adapter
                """
            )
        )
    ]

    version: Annotated[
        str,
        Field(
            description = inspect.cleandoc(
                """
                The adapter version
                """
            )
        )
    ]

    description:  Annotated[
        str,
        Field(
            description = inspect.cleandoc(
                """
                Short description of the adapter
                """
            )
        )
    ]

    state: Annotated[
        Literal["DEAD", "STOPPED", "RUNNING", "DELETED"],
        Field(
            description = inspect.cleandoc(
                """
                Opreational state (DEAD, STOPPED, RUNNING, DELETED)
                """
            )
        )
    ]


class GetAdaptersResponse(RootModel):
    """Response model for the get adapters API endpoint.

    This root model wraps a list of GetAdaptersElement objects representing
    all configured adapters on the Itential Platform server.

    Attributes:
        root: List of adapter elements, each containing adapter details.
    """

    root: Annotated[
        List[GetAdaptersElement],
        Field(
            description = inspect.cleandoc(
                """
                A list of elements where each element represents a configured
                adapter from the server
                """
            )
        )
    ]


class StartAdapterResponse(BaseModel):
    """Response model for the start adapter API operation.

    This model represents the response returned when starting an adapter,
    containing the adapter name and its new operational state.

    Attributes:
        name: The name of the adapter that was started.
        state: The current operational state after the start operation.
    """

    name: Annotated[
        str,
        Field(
            description = inspect.cleandoc(
                """
                The name of the adapter
                """
            )
        )
    ]

    state: Annotated[
        Literal["DEAD", "STOPPED", "RUNNING", "DELETED"],
        Field(
            description = inspect.cleandoc(
                """
                Opreational state (DEAD, STOPPED, RUNNING, DELETED)
                """
            )
        )
    ]

class StopAdapterResponse(BaseModel):
    """Response model for the stop adapter API operation.

    This model represents the response returned when stopping an adapter,
    containing the adapter name and its new operational state.

    Attributes:
        name: The name of the adapter that was stopped.
        state: The current operational state after the stop operation.
    """

    name: Annotated[
        str,
        Field(
            description = inspect.cleandoc(
                """
                The name of the adapter
                """
            )
        )
    ]

    state: Annotated[
        Literal["DEAD", "STOPPED", "RUNNING", "DELETED"],
        Field(
            description = inspect.cleandoc(
                """
                Opreational state (DEAD, STOPPED, RUNNING, DELETED)
                """
            )
        )
    ]



class RestartAdapterResponse(BaseModel):
    """Response model for the restart adapter API operation.

    This model represents the response returned when restarting an adapter,
    containing the adapter name and its new operational state.

    Attributes:
        name: The name of the adapter that was restarted.
        state: The current operational state after the restart operation.
    """

    name: Annotated[
        str,
        Field(
            description = inspect.cleandoc(
                """
                The name of the adapter
                """
            )
        )
    ]

    state: Annotated[
        Literal["DEAD", "STOPPED", "RUNNING", "DELETED"],
        Field(
            description = inspect.cleandoc(
                """
                Opreational state (DEAD, STOPPED, RUNNING, DELETED)
                """
            )
        )
    ]


