# Copyright (c) 2025 Itential, Inc
# GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import annotations

import inspect
from typing import Annotated, Any

from pydantic import BaseModel, Field, RootModel


class InventoryElement(BaseModel):
    """
    Represents an individual inventory element in Itential Platform.

    Inventories are collections of network devices managed through the
    Configuration Manager for organizing and performing bulk operations
    such as configuration backups, compliance checks, and device management.
    """

    object_id: Annotated[
        str,
        Field(
            alias="_id",
            description=inspect.cleandoc(
                """
                Unique identifier for the inventory
                """
            ),
        ),
    ]

    name: Annotated[
        str,
        Field(
            description=inspect.cleandoc(
                """
                Inventory name
                """
            )
        ),
    ]

    description: Annotated[
        str,
        Field(
            description=inspect.cleandoc(
                """
                Inventory description
                """
            ),
            default="",
        ),
    ]

    node_count: Annotated[
        int,
        Field(
            alias="nodeCount",
            description=inspect.cleandoc(
                """
                Number of nodes (devices) in the inventory
                """
            ),
            default=0,
        ),
    ]

    model_config = {"extra": "allow"}


class GetInventoriesResponse(RootModel):
    """
    Response model for retrieving all inventories from Itential Platform.

    This model wraps a list of InventoryElement objects, providing a complete
    listing of all inventories configured on the platform instance along
    with their metadata.
    """

    root: Annotated[
        list[InventoryElement],
        Field(
            description=inspect.cleandoc(
                """
                List of inventory objects with id, name, description, and device count
                """
            ),
            default_factory=list,
        ),
    ]


class CreateInventoryResponse(BaseModel):
    """
    Response model for creating an inventory on Itential Platform.

    Contains the result of an inventory creation operation including
    the unique identifier, name, and status information.
    """

    object_id: Annotated[
        str,
        Field(
            alias="_id",
            description=inspect.cleandoc(
                """
                Unique identifier for the created inventory
                """
            ),
        ),
    ]

    name: Annotated[
        str,
        Field(
            description=inspect.cleandoc(
                """
                Name of the inventory
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
            ),
            default="Inventory created successfully",
        ),
    ]

    model_config = {"extra": "allow"}


class DescribeInventoryResponse(BaseModel):
    """
    Response model for describing a specific inventory from Itential Platform.

    Contains detailed information about an inventory including its
    description, groups, actions, tags, nodes, and metadata.
    """

    object_id: Annotated[
        str,
        Field(
            alias="_id",
            description=inspect.cleandoc(
                """
                Unique identifier for the inventory
                """
            ),
        ),
    ]

    name: Annotated[
        str,
        Field(
            description=inspect.cleandoc(
                """
                Inventory name
                """
            )
        ),
    ]

    description: Annotated[
        str,
        Field(
            description=inspect.cleandoc(
                """
                Inventory description
                """
            ),
            default="",
        ),
    ]

    groups: Annotated[
        list[str],
        Field(
            description=inspect.cleandoc(
                """
                List of authorization group names associated with the inventory
                """
            ),
            default_factory=list,
        ),
    ]

    actions: Annotated[
        list[dict[str, Any]],
        Field(
            description=inspect.cleandoc(
                """
                List of actions configured for the inventory
                """
            ),
            default_factory=list,
        ),
    ]

    tags: Annotated[
        list[str],
        Field(
            description=inspect.cleandoc(
                """
                Tags associated with the inventory
                """
            ),
            default_factory=list,
        ),
    ]

    nodes: Annotated[
        list[dict[str, Any]],
        Field(
            description=inspect.cleandoc(
                """
                List of node objects in the inventory, each containing
                name, attributes (such as itential_host, itential_platform,
                cluster_id), and optional tags
                """
            ),
            default_factory=list,
        ),
    ]

    model_config = {"extra": "allow"}


class AddNodesToInventoryResponse(BaseModel):
    """
    Response model for adding nodes to an inventory on Itential Platform.

    Contains the result of a bulk node addition operation including
    the operation status and descriptive message.
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


class DeleteInventoryResponse(BaseModel):
    """
    Response model for deleting an inventory from Itential Platform.

    Contains the result of an inventory deletion operation including
    status and confirmation message.
    """

    status: Annotated[
        str,
        Field(
            description=inspect.cleandoc(
                """
                Status of the delete operation
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
