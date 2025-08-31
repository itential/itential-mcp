# Copyright (c) 2025 Itential, Inc
# GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)

import inspect

from typing import List, Annotated

from pydantic import BaseModel, RootModel, Field


class GoldenConfigTree(BaseModel):
    """Represents a Golden Configuration tree from the Itential platform.

    This model defines the structure for Golden Configuration tree information
    returned from the Configuration Manager API endpoints. Golden Configuration
    trees provide hierarchical templates for device configuration management.

    Attributes:
        name: The unique identifier name of the Golden Configuration tree.
        device_type: The device type this tree is designed for (e.g., 'cisco_ios', 'juniper').
        versions: List of available versions for this configuration tree.
    """

    name: Annotated[
        str,
        Field(
            description=inspect.cleandoc(
                """
                The name of the Golden Configuration tree
                """
            )
        )
    ]

    device_type: Annotated[
        str,
        Field(
            description=inspect.cleandoc(
                """
                The device type this tree is designed for
                """
            )
        )
    ]

    versions: Annotated[
        List[str],
        Field(
            description=inspect.cleandoc(
                """
                List of available versions for this tree
                """
            )
        )
    ]


class GetGoldenConfigTreesResponse(RootModel[List[GoldenConfigTree]]):
    """Response model for get_golden_config_trees function.

    This model represents the complete response from the get_golden_config_trees
    function, which returns a list of Golden Configuration trees available
    in the Configuration Manager.
    """

    root: List[GoldenConfigTree]


class CreateGoldenConfigTreeResponse(BaseModel):
    """Response model for create_golden_config_tree function.

    This model defines the structure for the response returned when creating
    a new Golden Configuration tree in the Configuration Manager.

    Attributes:
        name: Name of the created Golden Configuration tree.
        device_type: The device type this tree is designed for.
    """

    name: Annotated[
        str,
        Field(
            description=inspect.cleandoc(
                """
                Name of the created Golden Configuration tree
                """
            )
        )
    ]

    device_type: Annotated[
        str,
        Field(
            description=inspect.cleandoc(
                """
                The device type this tree is designed for
                """
            )
        )
    ]


class AddGoldenConfigNodeResponse(BaseModel):
    """Response model for add_golden_config_node function.

    This model defines the structure for the response returned when adding
    a new node to an existing Golden Configuration tree.

    Attributes:
        message: Success message confirming the node addition operation.
    """

    message: Annotated[
        str,
        Field(
            description=inspect.cleandoc(
                """
                Success message confirming node addition
                """
            )
        )
    ]