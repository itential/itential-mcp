# Copyright (c) 2025 Itential, Inc
# GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)

import inspect

from typing import Literal, List, Annotated, Optional

from pydantic import BaseModel, RootModel, Field


class GetIntegrationModelsElement(BaseModel):
    """Represents a single integration model element.

    This model represents an individual integration model returned by the
    get integration models API endpoint, containing information about the
    model's identity, version, and description.

    Attributes:
        id: Unique identifier assigned by Itential Platform.
        title: Model title from the OpenAPI spec info block.
        version: Model version from the OpenAPI spec info block.
        description: Optional model description.
    """

    id: Annotated[
        str,
        Field(
            description = inspect.cleandoc(
                """
                Unique identifier assigned by Itential Platform
                """
            )
        )
    ]

    title: Annotated[
        str,
        Field(
            description = inspect.cleandoc(
                """
                Model title from the OpenAPI spec info block
                """
            )
        )
    ]

    version: Annotated[
        str,
        Field(
            description = inspect.cleandoc(
                """
                Model version from the OpenAPI spec info block
                """
            )
        )
    ]

    description: Annotated[
        Optional[str],
        Field(
            default=None,
            description = inspect.cleandoc(
                """
                Optional model description
                """
            )
        )
    ]


class GetIntegrationModelsResponse(RootModel):
    """Response model for the get integration models API endpoint.

    This root model wraps a list of GetIntegrationModelsElement objects representing
    all integration models on the Itential Platform server.

    Attributes:
        root: List of integration model elements, each containing model details.
    """

    root: Annotated[
        List[GetIntegrationModelsElement],
        Field(
            description = inspect.cleandoc(
                """
                A list of elements where each element represents an integration
                model from the server
                """
            )
        )
    ]


class CreateIntegrationModelResponse(BaseModel):
    """Response model for the create integration model API operation.

    This model represents the response returned when creating an integration model,
    containing the operation status and descriptive message.

    Attributes:
        status: Operation status (OK or CREATED).
        message: Descriptive message about the operation.
    """

    status: Annotated[
        Literal["OK", "CREATED"],
        Field(
            description = inspect.cleandoc(
                """
                Operation status (OK or CREATED)
                """
            )
        )
    ]

    message: Annotated[
        str,
        Field(
            description = inspect.cleandoc(
                """
                Descriptive message about the operation
                """
            )
        )
    ]