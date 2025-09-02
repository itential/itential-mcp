# Copyright (c) 2025 Itential, Inc
# GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)

import inspect

from typing import Annotated, List, Literal, Mapping, Any

from pydantic import BaseModel, RootModel, Field


class GetResourcesElement(BaseModel):
    """Represents a single resource model configuration from the lifecycle manager.
    
    This model defines the structure for resource model information returned
    from the platform's lifecycle manager API endpoints.
    
    Attributes:
        name: The unique identifier name of the resource model.
        description: Optional human-readable description of the resource model's
            purpose and functionality.
    """

    name: Annotated[
        str,
        Field(
            description = inspect.cleandoc(
                """
                The name of the resource model
                """
            )
        )
    ]

    description: Annotated[
        str | None,
        Field(
            description = inspect.cleandoc(
            """
            Short description of the resource model.
            """
            ),
        default = None
        )
    ]


class GetResourcesResponse(RootModel):
    """Response model for resource collection endpoints.
    
    This root model wraps a list of resource elements, providing a
    standardized response format for API endpoints that return multiple
    resource models from the lifecycle manager.
    
    Attributes:
        root: A list of GetResourcesElement objects representing all
            available resource models on the platform.
    """

    root: Annotated[
        List[GetResourcesElement],
        Field(
            description = inspect.cleandoc(
                """
                A list of elements where each element represents a configured
                resource model from the server
                """
            ),
            default_factory = list
        )
    ]


class CreateResourceResponse(BaseModel):
    """Response model for resource creation operations.
    
    This model represents the response returned when creating a new resource
    instance through the lifecycle manager API.
    
    Note:
        Currently a placeholder model that can be extended with specific
        response fields as needed by the API implementation.
    """
    pass


class Action(BaseModel):
    """Represents an action that can be performed on a resource model.
    
    This model defines the structure for actions available within a resource
    model, including the action metadata and input schema requirements.
    
    Attributes:
        name: The configured name identifier for this action.
        type: The type of operation this action performs (create, update, delete).
        input_schema: A JSON Schema object defining the required input structure
            for successfully executing this action.
    """

    name: Annotated[
        str,
        Field(
            description = inspect.cleandoc(
                """
                The configured name of the action
                """
            )
        )
    ]

    type: Annotated[
        Literal["create", "update", "delete"],
        Field(
            description = inspect.cleandoc(
                """
                The type of action to be performed.
                """
            )
        )
    ]

    input_schema: Annotated[
        Mapping[str, Any],
        Field(
            description = inspect.cleandoc(
                """
                A JSON Schema object that defines the input schema required
                to successfully run the action.
                """
            )
        )
    ]


class DescribeResourceResponse(BaseModel):
    """Response model for detailed resource description endpoints.
    
    This model provides comprehensive information about a specific resource
    model, including its metadata and available actions.
    
    Attributes:
        name: The unique identifier name of the resource model.
        description: Human-readable description of the resource model's
            purpose and functionality.
        actions: A list of Action objects representing all operations
            that can be performed on instances of this resource model.
    """

    name: Annotated[
        str,
        Field(
            description = inspect.cleandoc(
                """
                The name of the resource model
                """
            )
        )
    ]

    description: Annotated[
        str,
        Field(
            description = inspect.cleandoc(
                """
                Short description of the resource model
                """
            ),
            default = None
        )
    ]

    actions: Annotated[
        List[Action],
        Field(
            description = inspect.cleandoc(
                """
                List of elements where each element represents an action that
                can be invoked for a resource model instance
                """
            ),
            default_factory = list
        )
    ]


class LastAction(BaseModel):
    """Represents the last action performed on a resource instance.
    
    This model captures information about the most recent lifecycle action
    that was executed on a resource instance.
    
    Attributes:
        name: The name of the action that was performed.
        type: The type of action (create, update, delete).
        status: The current execution status of the action.
    """

    name: Annotated[
        str,
        Field(
            description = inspect.cleandoc(
                """
                The name of the last action performed on the instance
                """
            )
        )
    ]

    type: Annotated[
        Literal["create", "update", "delete"],
        Field(
            description = inspect.cleandoc(
                """
                The type of the last action performed
                """
            )
        )
    ]

    status: Annotated[
        Literal["running", "error", "complete", "canceled", "paused"],
        Field(
            description = inspect.cleandoc(
                """
                The status of the last action performed
                """
            )
        )
    ]


class GetInstancesElement(BaseModel):
    """Represents a single resource instance from the lifecycle manager.
    
    This model defines the structure for resource instance information 
    returned from the platform's lifecycle manager API endpoints.
    
    Attributes:
        name: The unique identifier name of the resource instance.
        description: Optional human-readable description of the instance.
        instance_data: Data object associated with this instance.
        last_action: Information about the last action performed on this instance.
    """

    name: Annotated[
        str,
        Field(
            description = inspect.cleandoc(
                """
                The name of the resource instance
                """
            )
        )
    ]

    description: Annotated[
        str | None,
        Field(
            description = inspect.cleandoc(
                """
                Short description of the resource instance
                """
            ),
            default = None
        )
    ]

    instance_data: Annotated[
        Mapping[str, Any],
        Field(
            description = inspect.cleandoc(
                """
                Data object associated with this instance
                """
            )
        )
    ]

    last_action: Annotated[
        LastAction,
        Field(
            description = inspect.cleandoc(
                """
                Information about the last action performed on this instance
                """
            )
        )
    ]


class GetInstancesResponse(RootModel):
    """Response model for instance collection endpoints.
    
    This root model wraps a list of instance elements, providing a
    standardized response format for API endpoints that return multiple
    resource instances from the lifecycle manager.
    
    Attributes:
        root: A list of GetInstancesElement objects representing all
            instances of a specific resource model.
    """

    root: Annotated[
        List[GetInstancesElement],
        Field(
            description = inspect.cleandoc(
                """
                A list of elements where each element represents a resource
                instance from the server
                """
            ),
            default_factory = list
        )
    ]


class DescribeInstanceResponse(BaseModel):
    """Response model for detailed instance description endpoints.
    
    This model provides comprehensive information about a specific resource
    instance, including its data and action history.
    
    Attributes:
        description: Human-readable description of the instance.
        instance_data: Data object associated with this instance.
        last_action: Information about the last action performed on this instance.
    """

    description: Annotated[
        str | None,
        Field(
            description = inspect.cleandoc(
                """
                Short description of the instance
                """
            ),
            default = None
        )
    ]

    instance_data: Annotated[
        Mapping[str, Any],
        Field(
            description = inspect.cleandoc(
                """
                Data about the instance
                """
            )
        )
    ]

    last_action: Annotated[
        LastAction,
        Field(
            description = inspect.cleandoc(
                """
                Information about the last action performed on the instance
                """
            )
        )
    ]


class RunActionResponse(BaseModel):
    """Response model for action execution endpoints.
    
    This model represents the response returned when executing an action
    on a resource instance through the lifecycle manager API.
    
    Attributes:
        message: Status message about the action execution.
        start_time: The time when the action was started on the server.
        job_id: Job identifier used to get status updates using describe_job tool.
        status: The current status of the action execution.
    """

    message: Annotated[
        str | None,
        Field(
            description = inspect.cleandoc(
                """
                Status message about the action
                """
            ),
            default = None
        )
    ]

    start_time: Annotated[
        str,
        Field(
            description = inspect.cleandoc(
                """
                The time the action was started on the server
                """
            )
        )
    ]

    job_id: Annotated[
        str,
        Field(
            description = inspect.cleandoc(
                """
                Id used to get status updates using describe_job tool
                """
            )
        )
    ]

    status: Annotated[
        str,
        Field(
            description = inspect.cleandoc(
                """
                The current status of the action
                """
            )
        )
    ]


