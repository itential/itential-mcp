# Copyright (c) 2025 Itential, Inc
# GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)

import inspect
from typing import Annotated, Literal, List

from pydantic import BaseModel, RootModel, Field


class GetApplicationsElement(BaseModel):
    """
    Represents an individual application element in the Itential Platform.

    This model contains all the essential information about a single application
    including its identity, package details, version, description, and current
    operational state.
    """

    name: Annotated[
        str,
        Field(
            description = inspect.cleandoc(
                """
                The name of the application
                """
            )
        )
    ]

    package: Annotated[
        str,
        Field(
            description = inspect.cleandoc(
                """
                The NodeJS package name for the application
                """
            )
        )
    ]

    version: Annotated[
        str,
        Field(
            description = inspect.cleandoc(
                """
                The application version
                """
            )
        )
    ]

    description: Annotated[
        str,
        Field(
            description = inspect.cleandoc(
                """
                Short description of the application
                """
            )
        )
    ]


    state: Annotated[
        Literal["DEAD", "STOPPED", "RUNNING", "DELETED"],
        Field(
            description = inspect.cleandoc(
                """
                Operational state (DEAD, STOPPED, RUNNING, DELETED)
                """
            )
        )
    ]


class GetApplicationsResponse(RootModel):
    """
    Response model for retrieving all applications from Itential Platform.

    This model wraps a list of GetApplicationsElement objects, providing
    a complete inventory of all applications configured on the platform
    instance along with their current states and metadata.
    """

    root: Annotated[
        List[GetApplicationsElement],
        Field(
            description = inspect.cleandoc(
                """
                List of application objects with name, package, version, description, and state
                """
            ),
            default_factory = list
        )
    ]



class StartApplicationResponse(BaseModel):
    """
    Response model for starting an application on Itential Platform.

    Contains the result of a start operation including the application name
    and its final operational state after the start attempt. Used to confirm
    successful application startup or report any state changes.
    """

    name: Annotated[
        str,
        Field(
            description = inspect.cleandoc(
                """
                The name of the application
                """
            )
        )
    ]

    state: Annotated[
        Literal["DEAD", "STOPPED", "RUNNING", "DELETED"],
        Field(
            description = inspect.cleandoc(
                """
                Operational state (DEAD, STOPPED, RUNNING, DELETED)
                """
            )
        )
    ]


class StopApplicationResponse(BaseModel):
    """
    Response model for stopping an application on Itential Platform.

    Contains the result of a stop operation including the application name
    and its final operational state after the stop attempt. Used to confirm
    successful application shutdown or report any state changes.
    """

    name: Annotated[
        str,
        Field(
            description = inspect.cleandoc(
                """
                The name of the application
                """
            )
        )
    ]

    state: Annotated[
        Literal["DEAD", "STOPPED", "RUNNING", "DELETED"],
        Field(
            description = inspect.cleandoc(
                """
                Operational state (DEAD, STOPPED, RUNNING, DELETED)
                """
            )
        )
    ]


class RestartApplicationResponse(BaseModel):
    """
    Response model for restarting an application on Itential Platform.

    Contains the result of a restart operation including the application name
    and its final operational state after the restart attempt. Used to confirm
    successful application restart or report any state changes.
    """

    name: Annotated[
        str,
        Field(
            description = inspect.cleandoc(
                """
                The name of the application
                """
            )
        )
    ]

    state: Annotated[
        Literal["DEAD", "STOPPED", "RUNNING", "DELETED"],
        Field(
            description = inspect.cleandoc(
                """
                Operational state (DEAD, STOPPED, RUNNING, DELETED)
                """
            )
        )
    ]
