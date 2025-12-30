# Copyright (c) 2025 Itential, Inc
# GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import annotations

import inspect

from typing import Annotated

from pydantic import BaseModel, Field, RootModel


class GetProjectsElement(BaseModel):
    """Model for project summary information.

    Contains essential project information including unique identifier,
    name, and description. This model provides a simplified view of
    project details for listing operations.

    Attributes:
        id: The unique project identifier from the Platform.
        name: The human-readable name of the project.
        description: A brief description of the project's purpose.
    """

    id: Annotated[
        str,
        Field(
            description=inspect.cleandoc(
                """
                Unique project identifier
                """
            ),
        ),
    ]

    name: Annotated[
        str,
        Field(
            description=inspect.cleandoc(
                """
                Project name
                """
            )
        ),
    ]

    description: Annotated[
        str | None,
        Field(
            description=inspect.cleandoc(
                """
                Project description
                """
            ),
            default=None,
        ),
    ]


class GetProjectsResponse(RootModel):
    """
    Response model for get_projects function.

    Contains the list of project summaries returned by the get_projects
    operation. Each project summary includes only the essential fields:
    id, name, and description.

    Attributes:
        root: List of project summary objects.
    """

    root: Annotated[
        list[GetProjectsElement],
        Field(
            description=inspect.cleandoc(
                """
                List of project summaries
                """
            )
        ),
    ]


class DescribeProjectComponent(BaseModel):
    """Model for project component information in describe operations.

    Represents a component within an Automation Studio project with
    detailed information including its identity, type, and location.
    This model is used specifically for describe project operations
    to provide comprehensive component details.

    Attributes:
        id: The component reference identifier.
        name: The component name.
        type: The type of component (e.g., workflow, template).
        folder: The folder path where the component is stored.
    """

    id: Annotated[
        str,
        Field(
            description=inspect.cleandoc(
                """
                Template ID
                """
            ),
        ),
    ]

    name: Annotated[
        str,
        Field(
            description=inspect.cleandoc(
                """
                Template name
                """
            )
        ),
    ]

    type: Annotated[
        str,
        Field(
            description=inspect.cleandoc(
                """
                The type of component
                """
            )
        ),
    ]

    folder: Annotated[
        str,
        Field(
            description=inspect.cleandoc(
                """
                The folder path containing the component
                """
            )
        ),
    ]


class DescribeProjectResponse(GetProjectsElement):
    """Response model for describe_project function.

    Extends the basic project information with detailed component listings.
    Provides comprehensive project details including all contained components
    and their metadata for detailed project analysis and management.

    Attributes:
        Inherits id, name, description from GetProjectsElement.
        components: List of detailed component information.
    """

    components: Annotated[
        list[DescribeProjectComponent],
        Field(
            description=inspect.cleandoc(
                """
                List of components contained in the project
                """
            )
        ),
    ]
