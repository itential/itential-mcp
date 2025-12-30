# Copyright (c) 2025 Itential, Inc
# GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import annotations

import inspect

from typing import Annotated, Any, Literal, Mapping

from pydantic import BaseModel, Field, RootModel


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
            description=inspect.cleandoc(
                """
                The name of the resource model
                """
            )
        ),
    ]

    description: Annotated[
        str | None,
        Field(
            description=inspect.cleandoc(
                """
            Short description of the resource model.
            """
            ),
            default=None,
        ),
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
        list[GetResourcesElement],
        Field(
            description=inspect.cleandoc(
                """
                A list of elements where each element represents a configured
                resource model from the server
                """
            ),
            default_factory=list,
        ),
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
            description=inspect.cleandoc(
                """
                The configured name of the action
                """
            )
        ),
    ]

    type: Annotated[
        Literal["create", "update", "delete"],
        Field(
            description=inspect.cleandoc(
                """
                The type of action to be performed.
                """
            )
        ),
    ]

    input_schema: Annotated[
        Mapping[str, Any] | list[Any],
        Field(
            description=inspect.cleandoc(
                """
                A JSON Schema object that defines the input schema required
                to successfully run the action. Can be either a dictionary
                or a list depending on the schema structure.
                """
            )
        ),
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
            description=inspect.cleandoc(
                """
                The name of the resource model
                """
            )
        ),
    ]

    description: Annotated[
        str,
        Field(
            description=inspect.cleandoc(
                """
                Short description of the resource model
                """
            ),
            default=None,
        ),
    ]

    actions: Annotated[
        list[Action],
        Field(
            description=inspect.cleandoc(
                """
                List of elements where each element represents an action that
                can be invoked for a resource model instance
                """
            ),
            default_factory=list,
        ),
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
            description=inspect.cleandoc(
                """
                The name of the last action performed on the instance
                """
            )
        ),
    ]

    type: Annotated[
        Literal["create", "update", "delete"],
        Field(
            description=inspect.cleandoc(
                """
                The type of the last action performed
                """
            )
        ),
    ]

    status: Annotated[
        Literal["running", "error", "complete", "canceled", "paused"],
        Field(
            description=inspect.cleandoc(
                """
                The status of the last action performed
                """
            )
        ),
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
            description=inspect.cleandoc(
                """
                The name of the resource instance
                """
            )
        ),
    ]

    description: Annotated[
        str | None,
        Field(
            description=inspect.cleandoc(
                """
                Short description of the resource instance
                """
            ),
            default=None,
        ),
    ]

    instance_data: Annotated[
        Mapping[str, Any] | None,
        Field(
            description=inspect.cleandoc(
                """
                Data object associated with this instance
                """
            )
        ),
    ]

    last_action: Annotated[
        LastAction,
        Field(
            description=inspect.cleandoc(
                """
                Information about the last action performed on this instance
                """
            )
        ),
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
        list[GetInstancesElement],
        Field(
            description=inspect.cleandoc(
                """
                A list of elements where each element represents a resource
                instance from the server
                """
            ),
            default_factory=list,
        ),
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
            description=inspect.cleandoc(
                """
                Short description of the instance
                """
            ),
            default=None,
        ),
    ]

    instance_data: Annotated[
        Mapping[str, Any],
        Field(
            description=inspect.cleandoc(
                """
                Data about the instance
                """
            ),
            default=None,
        ),
    ]

    last_action: Annotated[
        LastAction,
        Field(
            description=inspect.cleandoc(
                """
                Information about the last action performed on the instance
                """
            )
        ),
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
            description=inspect.cleandoc(
                """
                Status message about the action
                """
            ),
            default=None,
        ),
    ]

    start_time: Annotated[
        str,
        Field(
            description=inspect.cleandoc(
                """
                The time the action was started on the server
                """
            )
        ),
    ]

    job_id: Annotated[
        str,
        Field(
            description=inspect.cleandoc(
                """
                Id used to get status updates using describe_job tool
                """
            )
        ),
    ]

    status: Annotated[
        str,
        Field(
            description=inspect.cleandoc(
                """
                The current status of the action
                """
            )
        ),
    ]


class ActionExecutionError(BaseModel):
    """Represents an error that occurred during action execution.

    Attributes:
        message: Error message describing what went wrong.
        timestamp: ISO 8601 timestamp when the error occurred.
        origin: The component where the error originated.
        metadata: Additional error metadata and context.
        step_id: Optional identifier for the step where error occurred.
    """

    message: Annotated[
        str,
        Field(
            description=inspect.cleandoc(
                """
                Error message describing what went wrong
                """
            )
        ),
    ]

    timestamp: Annotated[
        str,
        Field(
            description=inspect.cleandoc(
                """
                ISO 8601 timestamp when the error occurred
                """
            )
        ),
    ]

    origin: Annotated[
        str,
        Field(
            description=inspect.cleandoc(
                """
                The component where the error originated
                """
            )
        ),
    ]

    metadata: Annotated[
        Mapping[str, Any] | str | None,
        Field(
            description=inspect.cleandoc(
                """
                Additional error metadata and context
                """
            ),
            default=None,
        ),
    ]

    step_id: Annotated[
        str | None,
        Field(
            description=inspect.cleandoc(
                """
                Identifier for the step where error occurred
                """
            ),
            default=None,
            alias="stepId",
        ),
    ]


class ActionExecutionProgressComponent(BaseModel):
    """Represents progress information for a component in action execution.

    Attributes:
        progress_type: The type of progress being tracked.
        status: Current status of this component.
        error: Error information if the component failed.
        id: Unique identifier for this progress component.
        component_name: Name of the component being tracked.
        component_id: ID of the component being tracked.
        end_time: ISO 8601 timestamp when component completed.
        job_id: Optional job ID if this component triggered a job.
    """

    progress_type: Annotated[
        str,
        Field(
            description=inspect.cleandoc(
                """
                The type of progress being tracked
                """
            ),
            alias="progressType",
        ),
    ]

    status: Annotated[
        str,
        Field(
            description=inspect.cleandoc(
                """
                Current status of this component
                """
            )
        ),
    ]

    error: Annotated[
        Mapping[str, Any] | None,
        Field(
            description=inspect.cleandoc(
                """
                Error information if the component failed
                """
            ),
            default=None,
        ),
    ]

    id: Annotated[
        str,
        Field(
            description=inspect.cleandoc(
                """
                Unique identifier for this progress component
                """
            ),
            alias="_id",
        ),
    ]

    component_name: Annotated[
        str,
        Field(
            description=inspect.cleandoc(
                """
                Name of the component being tracked
                """
            ),
            alias="componentName",
        ),
    ]

    component_id: Annotated[
        str,
        Field(
            description=inspect.cleandoc(
                """
                ID of the component being tracked
                """
            ),
            alias="componentId",
        ),
    ]

    end_time: Annotated[
        str | None,
        Field(
            description=inspect.cleandoc(
                """
                ISO 8601 timestamp when component completed
                """
            ),
            default=None,
            alias="endTime",
        ),
    ]

    job_id: Annotated[
        str | None,
        Field(
            description=inspect.cleandoc(
                """
                Job ID if this component triggered a job
                """
            ),
            default=None,
            alias="jobId",
        ),
    ]


class ActionExecutionElement(BaseModel):
    """Represents a single action execution record from Lifecycle Manager.

    This model captures comprehensive information about an action execution
    including metadata, timing, status, errors, and data changes.

    Attributes:
        id: Unique identifier for this action execution.
        model_name: Name of the resource model.
        instance_id: ID of the resource instance.
        instance_name: Name of the resource instance.
        action_name: Name of the action that was executed.
        action_type: Type of action (create, update, delete).
        start_time: ISO 8601 timestamp when execution started.
        end_time: ISO 8601 timestamp when execution completed.
        initiator: User ID who initiated the action.
        job_id: Optional job ID associated with this execution.
        status: Current status of the execution.
        errors: List of errors that occurred during execution.
        initial_instance_data: Data before the action was executed.
        final_instance_data: Data after the action was executed.
    """

    id: Annotated[
        str,
        Field(
            description=inspect.cleandoc(
                """
                Unique identifier for this action execution
                """
            ),
            alias="_id",
            exclude=True,
        ),
    ]

    model_name: Annotated[
        str,
        Field(
            description=inspect.cleandoc(
                """
                Name of the resource model
                """
            ),
            alias="modelName",
        ),
    ]

    instance_id: Annotated[
        str,
        Field(
            description=inspect.cleandoc(
                """
                ID of the resource instance
                """
            ),
            alias="instanceId",
            exclude=True,
        ),
    ]

    instance_name: Annotated[
        str,
        Field(
            description=inspect.cleandoc(
                """
                Name of the resource instance
                """
            ),
            alias="instanceName",
        ),
    ]

    action_name: Annotated[
        str,
        Field(
            description=inspect.cleandoc(
                """
                Name of the action that was executed
                """
            ),
            alias="actionName",
        ),
    ]

    action_type: Annotated[
        str | None,
        Field(
            description=inspect.cleandoc(
                """
                Type of action (create, update, delete)
                """
            ),
            default=None,
            alias="actionType",
        ),
    ]

    start_time: Annotated[
        str,
        Field(
            description=inspect.cleandoc(
                """
                ISO 8601 timestamp when execution started
                """
            ),
            alias="startTime",
        ),
    ]

    end_time: Annotated[
        str | None,
        Field(
            description=inspect.cleandoc(
                """
                ISO 8601 timestamp when execution completed
                """
            ),
            default=None,
            alias="endTime",
        ),
    ]

    initiator: Annotated[
        str,
        Field(
            description=inspect.cleandoc(
                """
                User ID who initiated the action
                """
            )
        ),
    ]

    job_id: Annotated[
        str | None,
        Field(
            description=inspect.cleandoc(
                """
                Job ID associated with this execution
                """
            ),
            default=None,
            alias="jobId",
        ),
    ]

    status: Annotated[
        str,
        Field(
            description=inspect.cleandoc(
                """
                Current status of the execution (complete, error, canceled, running, etc.)
                """
            )
        ),
    ]

    errors: Annotated[
        list[ActionExecutionError],
        Field(
            description=inspect.cleandoc(
                """
                List of errors that occurred during execution
                """
            ),
            default_factory=list,
        ),
    ]

    initial_instance_data: Annotated[
        Mapping[str, Any] | list[str] | None,
        Field(
            description=inspect.cleandoc(
                """
                Data before the action was executed
                """
            ),
            default=None,
            alias="initialInstanceData",
        ),
    ]

    final_instance_data: Annotated[
        Mapping[str, Any] | list[str] | None,
        Field(
            description=inspect.cleandoc(
                """
                Data after the action was executed
                """
            ),
            default=None,
            alias="finalInstanceData",
        ),
    ]


class GetActionExecutionsResponse(RootModel):
    """Response model for action execution history endpoints.

    This root model wraps a list of action execution elements, providing a
    standardized response format for API endpoints that return action execution
    history from the lifecycle manager.

    Attributes:
        root: A list of ActionExecutionElement objects representing the
            execution history of lifecycle actions.
    """

    root: Annotated[
        list[ActionExecutionElement],
        Field(
            description=inspect.cleandoc(
                """
                A list of action execution records from the lifecycle manager
                """
            ),
            default_factory=list,
        ),
    ]
