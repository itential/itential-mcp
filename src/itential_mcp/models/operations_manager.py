# Copyright (c) 2025 Itential, Inc
# GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import annotations

import inspect

from typing import Annotated, Any, Literal, Mapping

from pydantic import BaseModel, Field, RootModel


class WorkflowElement(BaseModel):
    """
    Represents a single workflow object from the operations manager.

    This model defines the structure for workflow information returned
    from the platform's operations manager API endpoints. Workflows are
    the core automation engine defining executable processes.

    Attributes:
        object_id: Unique identifier for the workflow.
        name: Workflow name (use this as the identifier for workflow operations).
        description: Workflow description.
        input_schema: Input schema for workflow parameters (JSON Schema draft-07 format).
        route_name: API route name for triggering the workflow (use with start_workflow).
        last_executed: ISO 8601 timestamp of last execution (null if never executed).
    """

    name: Annotated[
        str,
        Field(
            description=inspect.cleandoc(
                """
                Workflow name (use this as the identifier for workflow operations)
                """
            )
        ),
    ]

    description: Annotated[
        str | None,
        Field(
            description=inspect.cleandoc(
                """
                Workflow description
                """
            ),
            default=None,
        ),
    ]

    input_schema: Annotated[
        Mapping[str, Any] | None,
        Field(
            description=inspect.cleandoc(
                """
                Input schema for workflow parameters (JSON Schema draft-07 format)
                """
            ),
            default=None,
        ),
    ]

    route_name: Annotated[
        str | None,
        Field(
            description=inspect.cleandoc(
                """
                API route name for triggering the workflow (use with start_workflow)
                """
            ),
            default=None,
        ),
    ]

    last_executed: Annotated[
        str | None,
        Field(
            description=inspect.cleandoc(
                """
                ISO 8601 timestamp of last execution (null if never executed)
                """
            ),
            default=None,
        ),
    ]


class GetWorkflowsResponse(RootModel):
    """
    Response model for workflow collection endpoints.

    This root model wraps a list of workflow elements, providing a
    standardized response format for API endpoints that return multiple
    workflows from the operations manager.

    Attributes:
        root: A list of WorkflowElement objects representing all
            available workflows on the platform.
    """

    root: Annotated[
        list[WorkflowElement],
        Field(
            description=inspect.cleandoc(
                """
                List of workflow objects with workflow metadata and configuration
                """
            ),
            default_factory=list,
        ),
    ]


class JobMetrics(BaseModel):
    """
    Represents job execution metrics from workflow operations.

    This model captures timing and user information about workflow
    job execution for monitoring and auditing purposes.

    Attributes:
        start_time: The time when the job execution was started.
        end_time: The time when the job execution completed (if finished).
        user: Username of the user who initiated the job execution.
    """

    start_time: Annotated[
        str | None,
        Field(
            description=inspect.cleandoc(
                """
                The time when the job execution was started.
                """
            ),
            default=None,
        ),
    ]

    end_time: Annotated[
        str | None,
        Field(
            description=inspect.cleandoc(
                """
                The time when the job execution completed (if finished).
                """
            ),
            default=None,
        ),
    ]

    user: Annotated[
        str | None,
        Field(
            description=inspect.cleandoc(
                """
                Username of the user who initiated the job execution
                """
            ),
            default=None,
        ),
    ]


class StartWorkflowResponse(BaseModel):
    """
    Response model for workflow execution endpoints.

    This model represents the response returned when starting a workflow
    execution through the operations manager API. It contains job details
    that can be monitored for progress and results.

    Attributes:
        object_id: Unique job identifier (use with describe_job for monitoring).
        name: Workflow name that was executed.
        description: Workflow description.
        tasks: Complete set of tasks to be executed in the workflow.
        status: Current job status (error, complete, running, canceled, incomplete, paused).
        metrics: Job execution metrics including start_time, end_time, and user.
    """

    object_id: Annotated[
        str,
        Field(
            description=inspect.cleandoc(
                """
                Unique job identifier (use with describe_job for monitoring)
                """
            )
        ),
    ]

    name: Annotated[
        str,
        Field(
            description=inspect.cleandoc(
                """
                Workflow name that was executed
                """
            )
        ),
    ]

    description: Annotated[
        str | None,
        Field(
            description=inspect.cleandoc(
                """
                Workflow description
                """
            ),
            default=None,
        ),
    ]

    tasks: Annotated[
        Mapping[str, Any],
        Field(
            description=inspect.cleandoc(
                """
                Complete set of tasks to be executed in the workflow
                """
            )
        ),
    ]

    status: Annotated[
        Literal["error", "complete", "running", "canceled", "incomplete", "paused"],
        Field(
            description=inspect.cleandoc(
                """
                Current job status (error, complete, running, canceled, incomplete, paused)
                """
            )
        ),
    ]

    metrics: Annotated[
        JobMetrics,
        Field(
            description=inspect.cleandoc(
                """
                Job execution metrics including start_time, end_time, and user
                """
            )
        ),
    ]


class JobElement(BaseModel):
    """
    Represents a single job object from the operations manager.

    This model defines the structure for job information returned
    from the platform's operations manager API endpoints. Jobs represent
    workflow execution instances that track status, progress, and results.

    Attributes:
        object_id: Unique job identifier.
        name: Job name.
        description: Job description.
        status: Current job status (error, complete, running, cancelled, incomplete, paused).
    """

    object_id: Annotated[
        str,
        Field(
            alias="_id",
            description=inspect.cleandoc(
                """
                Unique job identifier
                """
            ),
        ),
    ]

    name: Annotated[
        str,
        Field(
            description=inspect.cleandoc(
                """
                Job name
                """
            )
        ),
    ]

    description: Annotated[
        str | None,
        Field(
            description=inspect.cleandoc(
                """
                Job description
                """
            ),
            default=None,
        ),
    ]

    status: Annotated[
        Literal["error", "complete", "running", "canceled", "incomplete", "paused"],
        Field(
            description=inspect.cleandoc(
                """
                Current job status (error, complete, running, canceled, incomplete, paused)
                """
            )
        ),
    ]


class GetJobsResponse(RootModel):
    """
    Response model for job collection endpoints.

    This root model wraps a list of job elements, providing a
    standardized response format for API endpoints that return multiple
    jobs from the operations manager.

    Attributes:
        root: A list of JobElement objects representing all
            available jobs on the platform.
    """

    root: Annotated[
        list[JobElement],
        Field(
            description=inspect.cleandoc(
                """
                List of job objects with job metadata and status
                """
            ),
            default_factory=list,
        ),
    ]


class DescribeJobResponse(BaseModel):
    """
    Response model for job detail endpoints.

    This model represents detailed information about a specific job
    from the operations manager API, including comprehensive execution
    details, status, tasks, metrics, and output variables.

    Attributes:
        object_id: Unique job identifier.
        name: Job name.
        description: Job description.
        job_type: Job type (automation, resource:action, resource:compliance).
        tasks: Complete set of tasks executed.
        status: Current job status (error, complete, running, canceled, incomplete, paused).
        metrics: Job execution metrics including start time, end time, and account.
        updated: Last update timestamp.
        variables: Job variable outputs produced during workflow execution.
    """

    object_id: Annotated[
        str,
        Field(
            alias="_id",
            description=inspect.cleandoc(
                """
                Unique job identifier
                """
            ),
        ),
    ]

    name: Annotated[
        str,
        Field(
            description=inspect.cleandoc(
                """
                Job name
                """
            )
        ),
    ]

    description: Annotated[
        str | None,
        Field(
            description=inspect.cleandoc(
                """
                Job description
                """
            ),
            default=None,
        ),
    ]

    job_type: Annotated[
        str,
        Field(
            alias="type",
            description=inspect.cleandoc(
                """
                Job type (automation, resource:action, resource:compliance)
                """
            ),
        ),
    ]

    tasks: Annotated[
        Mapping[str, Any],
        Field(
            description=inspect.cleandoc(
                """
                Complete set of tasks executed
                """
            )
        ),
    ]

    status: Annotated[
        Literal["error", "complete", "running", "canceled", "incomplete", "paused"],
        Field(
            description=inspect.cleandoc(
                """
                Current job status (error, complete, running, canceled,
                incomplete, paused)
                """
            )
        ),
    ]

    metrics: Annotated[
        Mapping[str, Any],
        Field(
            description=inspect.cleandoc(
                """
                Job execution metrics including start time, end time, and account
                """
            )
        ),
    ]

    updated: Annotated[
        str,
        Field(
            description=inspect.cleandoc(
                """
                Last update timestamp
                """
            )
        ),
    ]

    variables: Annotated[
        Mapping[str, Any] | None,
        Field(
            description=inspect.cleandoc(
                """
                Job variable outputs produced during workflow execution
                """
            ),
            default=None,
        ),
    ]


class StartAgentResponse(BaseModel):
    """Response returned when an agent endpoint trigger fires successfully.

    Agent triggers return a session object rather than a job object. Use
    session_id with describe_session to poll for completion and read the output.

    Attributes:
        session_id: Unique session identifier for this agent run.
        status: Initial session status (RUNNING or COMPLETE).
    """

    session_id: Annotated[
        str,
        Field(
            description=inspect.cleandoc(
                """
                Unique session identifier; use with describe_session to poll
                for completion and retrieve the agent output
                """
            )
        ),
    ]

    status: Annotated[
        str,
        Field(
            description=inspect.cleandoc(
                """
                Initial session status (RUNNING or COMPLETE)
                """
            )
        ),
    ]


class SessionMessage(BaseModel):
    """A single message/event from an agent session.

    Attributes:
        event_type: Type of event (inference-succeeded, agent-session-completed, etc.).
        category: Broad category (AGENT_REASONING, AGENT_STATUS, etc.).
        text: Agent output text, present on inference-succeeded events.
        timestamp: ISO 8601 event timestamp.
    """

    event_type: Annotated[
        str,
        Field(alias="type", description="Event type identifier"),
    ]

    category: Annotated[
        str | None,
        Field(description="Broad event category", default=None),
    ]

    text: Annotated[
        str | None,
        Field(
            description="Agent output text (present on inference-succeeded events)",
            default=None,
        ),
    ]

    timestamp: Annotated[
        str | None,
        Field(description="ISO 8601 event timestamp", default=None),
    ]


class DescribeSessionResponse(BaseModel):
    """Full details of a completed or running agent session.

    Attributes:
        session_id: Unique session identifier.
        agent_name: Name of the agent that ran.
        status: Session status (RUNNING, COMPLETE, FAILED).
        output: Final text output from the agent (None while still running).
        started_at: ISO 8601 start timestamp.
        end_time: ISO 8601 end timestamp (None if still running).
        duration_ms: Total session duration in milliseconds.
        messages: All session events in order.
    """

    session_id: Annotated[
        str,
        Field(description="Unique session identifier"),
    ]

    agent_name: Annotated[
        str | None,
        Field(description="Name of the agent that ran", default=None),
    ]

    status: Annotated[
        str,
        Field(description="Session status (RUNNING, COMPLETE, FAILED)"),
    ]

    output: Annotated[
        str | None,
        Field(
            description=inspect.cleandoc(
                """
                Final text output from the agent; None while still RUNNING
                """
            ),
            default=None,
        ),
    ]

    started_at: Annotated[
        str | None,
        Field(description="ISO 8601 start timestamp", default=None),
    ]

    end_time: Annotated[
        str | None,
        Field(
            description="ISO 8601 end timestamp (None if still running)", default=None
        ),
    ]

    duration_ms: Annotated[
        int | None,
        Field(description="Total session duration in milliseconds", default=None),
    ]

    messages: Annotated[
        list[SessionMessage],
        Field(
            description="All session events in chronological order",
            default_factory=list,
        ),
    ]


class AgentElement(BaseModel):
    """
    Represents a single agent automation from the operations manager.

    Agents are AI-driven automation components that can be exposed as API
    endpoints and triggered similarly to workflows. This model surfaces the
    fields most useful to an LLM caller: the agent's identity, its input
    contract, and the route name needed to start it.

    Attributes:
        name: Human-readable automation name wrapping the agent.
        description: Optional description of the agent automation.
        agent_id: UUID of the underlying agent component (componentId).
        route_name: API route name for triggering via start_workflow (None if no
            endpoint trigger has been created for this agent).
        input_schema: JSON Schema for the endpoint trigger's input (None if no
            endpoint trigger exists).
        last_executed: ISO 8601 timestamp of the last trigger execution (None if
            the agent has never been triggered via its endpoint).
    """

    name: Annotated[
        str,
        Field(
            description=inspect.cleandoc(
                """
                Human-readable name of the automation wrapping the agent
                """
            )
        ),
    ]

    description: Annotated[
        str | None,
        Field(
            description=inspect.cleandoc(
                """
                Description of the agent automation
                """
            ),
            default=None,
        ),
    ]

    agent_id: Annotated[
        str | None,
        Field(
            description=inspect.cleandoc(
                """
                UUID of the underlying agent component; use this to identify the agent
                """
            ),
            default=None,
        ),
    ]

    route_name: Annotated[
        str | None,
        Field(
            description=inspect.cleandoc(
                """
                API route name for triggering this agent (use with start_workflow);
                None means no endpoint trigger has been created yet — use expose_agent
                to create one
                """
            ),
            default=None,
        ),
    ]

    input_schema: Annotated[
        Mapping[str, Any] | None,
        Field(
            description=inspect.cleandoc(
                """
                JSON Schema describing the input the agent endpoint accepts
                """
            ),
            default=None,
        ),
    ]

    last_executed: Annotated[
        str | None,
        Field(
            description=inspect.cleandoc(
                """
                ISO 8601 timestamp of last endpoint trigger execution (null if never executed)
                """
            ),
            default=None,
        ),
    ]


class GetAgentsResponse(RootModel):
    """
    Response model for agent automation collection endpoints.

    Wraps a list of AgentElement objects returned from the operations manager
    when querying for agent-type automations.

    Attributes:
        root: List of AgentElement objects with agent metadata and trigger info.
    """

    root: Annotated[
        list[AgentElement],
        Field(
            description=inspect.cleandoc(
                """
                List of agent automation objects with identity and trigger metadata
                """
            ),
            default_factory=list,
        ),
    ]


class AutomationElement(BaseModel):
    """
    Represents a single automation from the Operations Manager.

    Automations are the execution containers in the Operations Manager that
    wrap a component (workflow, agent, or compliance plan) and expose it for
    triggering. This unified model surfaces both workflow and agent automations
    in a single list with a component_type discriminator.

    Attributes:
        name: Human-readable automation name.
        description: Optional description of the automation.
        component_type: Type of the underlying component (workflows, agents,
            ucm_compliance_plan).
        component_id: ID of the underlying component (workflow ID or agent UUID).
        route_name: API route name for triggering via trigger_automation (None if no
            endpoint trigger has been created for this automation).
        input_schema: JSON Schema for the endpoint trigger's input (None if no
            endpoint trigger exists).
        last_executed: ISO 8601 timestamp of the last trigger execution (None if
            never triggered via its endpoint).
    """

    name: Annotated[
        str,
        Field(
            description=inspect.cleandoc(
                """
                Human-readable name of the automation
                """
            )
        ),
    ]

    description: Annotated[
        str | None,
        Field(
            description=inspect.cleandoc(
                """
                Description of the automation
                """
            ),
            default=None,
        ),
    ]

    component_type: Annotated[
        str,
        Field(
            description=inspect.cleandoc(
                """
                Type of the underlying component (workflows, agents, ucm_compliance_plan)
                """
            )
        ),
    ]

    component_id: Annotated[
        str | None,
        Field(
            description=inspect.cleandoc(
                """
                ID or UUID of the underlying component
                """
            ),
            default=None,
        ),
    ]

    route_name: Annotated[
        str | None,
        Field(
            description=inspect.cleandoc(
                """
                API route name for triggering this automation (use with trigger_automation);
                None means no endpoint trigger has been created yet
                """
            ),
            default=None,
        ),
    ]

    input_schema: Annotated[
        Mapping[str, Any] | None,
        Field(
            description=inspect.cleandoc(
                """
                JSON Schema describing the input the automation endpoint accepts
                """
            ),
            default=None,
        ),
    ]

    last_executed: Annotated[
        str | None,
        Field(
            description=inspect.cleandoc(
                """
                ISO 8601 timestamp of last endpoint trigger execution (null if never executed)
                """
            ),
            default=None,
        ),
    ]


class GetAutomationsResponse(RootModel):
    """
    Response model for the unified automations collection endpoint.

    Wraps a list of AutomationElement objects returned from the Operations Manager
    covering all component types (workflows, agents, compliance plans).

    Attributes:
        root: List of AutomationElement objects with automation metadata and trigger info.
    """

    root: Annotated[
        list[AutomationElement],
        Field(
            description=inspect.cleandoc(
                """
                List of automation objects across all component types
                """
            ),
            default_factory=list,
        ),
    ]


class ExposeWorkflowResponse(BaseModel):
    """Response model for workflow exposure endpoints.

    This model represents the response returned when exposing a workflow
    as an API endpoint through the operations manager. It contains status
    information about the workflow exposure operation.

    Attributes:
        message: The status of the expose operation.
    """

    message: Annotated[
        str,
        Field(
            description=inspect.cleandoc(
                """
                The status of the expose operation
                """
            )
        ),
    ]
