# Copyright (c) 2025 Itential, Inc
# GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import annotations

import inspect

from typing import Annotated, Any

from pydantic import BaseModel, Field


class CommandTemplate(BaseModel):
    """Represents a command template configuration.

    This model represents a command template that can be executed against
    network devices to perform automated configuration and validation tasks.
    Templates can be global or belong to specific projects.

    Attributes:
        id: Unique identifier for the command template.
        name: Human-readable template name.
        description: Brief description of what the template does.
        namespace: Project namespace (null for global templates).
        passRule: Pass rule configuration for template evaluation.
    """

    id: Annotated[
        str,
        Field(
            alias="_id",
            description=inspect.cleandoc(
                """
                Unique identifier for the command template
                """
            ),
        ),
    ]

    name: Annotated[
        str,
        Field(
            description=inspect.cleandoc(
                """
                Human-readable name of the command template
                """
            )
        ),
    ]

    description: Annotated[
        str | None,
        Field(
            description=inspect.cleandoc(
                """
                Brief description of what the template does (null if not provided)
                """
            )
        ),
    ]

    namespace: Annotated[
        dict[str, Any] | None,
        Field(
            description=inspect.cleandoc(
                """
                Project namespace object (null for global templates)
                """
            )
        ),
    ]

    passRule: Annotated[
        bool,
        Field(
            description=inspect.cleandoc(
                """
                Pass rule configuration (True=all must pass, False=one must pass)
                """
            )
        ),
    ]


class GetCommandTemplatesResponse(BaseModel):
    """Response model for the get command templates API endpoint.

    This model wraps a list of CommandTemplate objects representing
    all available command templates from both global space and projects.

    Attributes:
        templates: List of command template objects.
    """

    templates: Annotated[
        list[CommandTemplate],
        Field(
            description=inspect.cleandoc(
                """
                List of command template objects with configuration details
                """
            )
        ),
    ]


class CommandTemplateDetail(BaseModel):
    """Represents detailed command template information.

    This model extends the basic CommandTemplate with detailed information
    including the actual commands and rules that will be executed when
    the template is run against devices.

    Attributes:
        id: Unique identifier for the command template.
        name: Human-readable template name.
        commands: List of commands and associated validation rules.
        namespace: Project namespace (null for global templates).
        passRule: Pass rule configuration for template evaluation.
    """

    id: Annotated[
        str,
        Field(
            alias="_id",
            description=inspect.cleandoc(
                """
                Unique identifier for the command template
                """
            ),
        ),
    ]

    name: Annotated[
        str,
        Field(
            description=inspect.cleandoc(
                """
                Human-readable name of the command template
                """
            )
        ),
    ]

    commands: Annotated[
        list[dict[str, Any]],
        Field(
            description=inspect.cleandoc(
                """
                List of commands and associated validation rules
                """
            )
        ),
    ]

    namespace: Annotated[
        dict[str, Any] | None,
        Field(
            description=inspect.cleandoc(
                """
                Project namespace object (null for global templates)
                """
            )
        ),
    ]

    passRule: Annotated[
        bool,
        Field(
            description=inspect.cleandoc(
                """
                Pass rule configuration (True=all must pass, False=one must pass)
                """
            )
        ),
    ]


class DescribeCommandTemplateResponse(BaseModel):
    """Response model for the describe command template API endpoint.

    This model wraps a CommandTemplateDetail object containing detailed
    information about a specific command template.

    Attributes:
        template: Detailed command template information.
    """

    template: Annotated[
        CommandTemplateDetail,
        Field(
            description=inspect.cleandoc(
                """
                Detailed command template information including commands and rules
                """
            )
        ),
    ]


class RuleEvaluation(BaseModel):
    """Represents a rule evaluation result.

    This model contains the results of evaluating a validation rule
    against device command output during template execution.

    Attributes:
        eval: Type of rule evaluation performed.
        rule: Data used for performing the rule check.
        severity: Severity level if rule matches.
        result: Boolean result from the rule check.
    """

    eval: Annotated[
        str,
        Field(
            description=inspect.cleandoc(
                """
                Type of rule evaluation performed. Supported values:
                - "contains": Check if output contains the rule string
                - "!contains": Check if output does NOT contain the rule string
                - "contains1": Check if output contains the rule string (case-sensitive)
                - "RegEx": Use regular expression pattern matching
                - "!RegEx": Use regular expression pattern matching (negated)
                - "#comparison": Numeric comparison evaluation
                """
            )
        ),
    ]

    rule: Annotated[
        Any,
        Field(
            description=inspect.cleandoc(
                """
                Data used for performing the rule check. Can be:
                - String for contains operations
                - Regular expression pattern for RegEx evaluation
                - String with variable substitution syntax <!variable!>
                - Numeric value for #comparison operations
                """
            )
        ),
    ]

    severity: Annotated[
        str,
        Field(
            description=inspect.cleandoc(
                """
                Severity level if rule matches (e.g., error, warning, info)
                """
            )
        ),
    ]

    result: Annotated[
        bool,
        Field(
            description=inspect.cleandoc(
                """
                Boolean result from the rule check (True if rule passed)
                """
            )
        ),
    ]


class CommandResult(BaseModel):
    """Represents a command execution result from a device.

    This model contains the results of executing a single command
    against a device as part of a command template execution.

    Attributes:
        raw: Original command as entered in the template.
        evaluated: Command as actually sent to the device.
        device: Target device name where command was executed.
        response: Device response used for rule evaluation.
        rules: List of rule evaluation results.
    """

    raw: Annotated[
        str,
        Field(
            description=inspect.cleandoc(
                """
                Original command as entered in the template
                """
            )
        ),
    ]

    evaluated: Annotated[
        str,
        Field(
            description=inspect.cleandoc(
                """
                Command as actually sent to the device after variable substitution
                """
            )
        ),
    ]

    device: Annotated[
        str,
        Field(
            description=inspect.cleandoc(
                """
                Target device name where command was executed
                """
            )
        ),
    ]

    response: Annotated[
        str,
        Field(
            description=inspect.cleandoc(
                """
                Device response used for rule evaluation
                """
            )
        ),
    ]

    rules: Annotated[
        list[RuleEvaluation],
        Field(
            description=inspect.cleandoc(
                """
                List of rule evaluation results for this command execution
                """
            )
        ),
    ]


class RunCommandTemplateResponse(BaseModel):
    """Response model for the run command template API endpoint.

    This model contains the complete results of executing a command
    template against one or more devices, including all command
    results and rule evaluations.

    Attributes:
        name: Command template name that was executed.
        all_pass_flag: Whether all rules must pass for success.
        command_results: List of results for each command/device combination.
    """

    name: Annotated[
        str,
        Field(
            description=inspect.cleandoc(
                """
                Command template name that was executed
                """
            )
        ),
    ]

    all_pass_flag: Annotated[
        bool,
        Field(
            description=inspect.cleandoc(
                """
                Whether all rules must pass for success (True=all must pass, False=any can pass)
                """
            )
        ),
    ]

    command_results: Annotated[
        list[CommandResult],
        Field(
            description=inspect.cleandoc(
                """
                List of results for each command/device combination
                """
            )
        ),
    ]


class DeviceCommandResult(BaseModel):
    """Represents a simple device command execution result.

    This model contains the basic results of executing a single
    command against a device without rule evaluation.

    Attributes:
        device: Target device name where command was executed.
        command: Command that was sent to the device.
        response: Output received from running the command.
    """

    device: Annotated[
        str,
        Field(
            description=inspect.cleandoc(
                """
                Target device name where command was executed
                """
            )
        ),
    ]

    command: Annotated[
        str,
        Field(
            description=inspect.cleandoc(
                """
                Command that was sent to the device
                """
            )
        ),
    ]

    response: Annotated[
        str,
        Field(
            description=inspect.cleandoc(
                """
                Output received from running the command
                """
            )
        ),
    ]


class RunCommandResponse(BaseModel):
    """Response model for the run command API endpoint.

    This model wraps a list of DeviceCommandResult objects representing
    the results of executing a single command against multiple devices.

    Attributes:
        results: List of command execution results for each device.
    """

    results: Annotated[
        list[DeviceCommandResult],
        Field(
            description=inspect.cleandoc(
                """
                List of command execution results for each device
                """
            )
        ),
    ]


class CreateCommandTemplateRequest(BaseModel):
    """Request model for creating a new command template.

    This model defines the structure for creating a new command template
    with commands and validation rules.

    Attributes:
        name: Name for the command template.
        commands: List of commands with their validation rules.
        project: Project name to create the template in (None for global).
        description: Optional description for the template.
        os: Operating system type.
        pass_rule: Pass rule configuration.
        ignore_warnings: Whether to ignore warnings during execution.
    """

    name: Annotated[
        str,
        Field(
            description=inspect.cleandoc(
                """
                Name for the command template
                """
            )
        ),
    ]

    commands: Annotated[
        list[dict[str, Any]],
        Field(
            description=inspect.cleandoc(
                """
                List of commands with their validation rules
                """
            )
        ),
    ]

    project: Annotated[
        str | None,
        Field(
            description=inspect.cleandoc(
                """
                Project name to create the template in (None for global templates)
                """
            ),
            default=None,
        ),
    ]

    description: Annotated[
        str | None,
        Field(
            description=inspect.cleandoc(
                """
                Optional description for the template
                """
            ),
            default=None,
        ),
    ]

    os: Annotated[
        str,
        Field(
            description=inspect.cleandoc(
                """
                Operating system type (default: empty string)
                """
            ),
            default="",
        ),
    ]

    pass_rule: Annotated[
        bool,
        Field(
            description=inspect.cleandoc(
                """
                Pass rule configuration (True=all must pass, False=one must pass)
                """
            ),
            default=True,
        ),
    ]

    ignore_warnings: Annotated[
        bool,
        Field(
            description=inspect.cleandoc(
                """
                Whether to ignore warnings during execution
                """
            ),
            default=False,
        ),
    ]


class CreateCommandTemplateResponse(BaseModel):
    """Response model for the create command template API endpoint.

    This model wraps the result of creating a new command template,
    including the created template details and operation status.

    Attributes:
        result: Operation result with success status.
        ops: List of created template operations.
        inserted_count: Number of templates inserted.
        inserted_ids: Mapping of inserted template IDs.
    """

    result: Annotated[
        dict[str, Any],
        Field(
            description=inspect.cleandoc(
                """
                Operation result with success status
                """
            )
        ),
    ]

    ops: Annotated[
        list[dict[str, Any]],
        Field(
            description=inspect.cleandoc(
                """
                List of created template operations
                """
            )
        ),
    ]

    inserted_count: Annotated[
        int,
        Field(
            alias="insertedCount",
            description=inspect.cleandoc(
                """
                Number of templates inserted
                """
            ),
        ),
    ]

    inserted_ids: Annotated[
        dict[str, str],
        Field(
            alias="insertedIds",
            description=inspect.cleandoc(
                """
                Mapping of inserted template IDs
                """
            ),
        ),
    ]


class UpdateCommandTemplateRequest(BaseModel):
    """Request model for updating an existing command template.

    This model defines the structure for updating an existing command template
    with new commands and validation rules.

    Attributes:
        name: Name of the command template to update.
        commands: List of commands with their validation rules.
        project: Project name containing the template (None for global).
        description: Optional description for the template.
        os: Operating system type.
        pass_rule: Pass rule configuration.
        ignore_warnings: Whether to ignore warnings during execution.
    """

    name: Annotated[
        str,
        Field(
            description=inspect.cleandoc(
                """
                Name of the command template to update
                """
            )
        ),
    ]

    commands: Annotated[
        list[dict[str, Any]],
        Field(
            description=inspect.cleandoc(
                """
                List of commands with their validation rules
                """
            )
        ),
    ]

    project: Annotated[
        str | None,
        Field(
            description=inspect.cleandoc(
                """
                Project name containing the template (None for global templates)
                """
            ),
            default=None,
        ),
    ]

    description: Annotated[
        str | None,
        Field(
            description=inspect.cleandoc(
                """
                Optional description for the template
                """
            ),
            default=None,
        ),
    ]

    os: Annotated[
        str,
        Field(
            description=inspect.cleandoc(
                """
                Operating system type (default: empty string)
                """
            ),
            default="",
        ),
    ]

    pass_rule: Annotated[
        bool,
        Field(
            description=inspect.cleandoc(
                """
                Pass rule configuration (True=all must pass, False=one must pass)
                """
            ),
            default=True,
        ),
    ]

    ignore_warnings: Annotated[
        bool,
        Field(
            description=inspect.cleandoc(
                """
                Whether to ignore warnings during execution
                """
            ),
            default=False,
        ),
    ]


class UpdateCommandTemplateResponse(BaseModel):
    """Response model for the update command template API endpoint.

    This model wraps the result of updating an existing command template,
    including the operation status and affected document counts.

    Attributes:
        acknowledged: Whether the update was acknowledged.
        modified_count: Number of documents modified.
        upserted_id: ID of upserted document (if any).
        upserted_count: Number of documents upserted.
        matched_count: Number of documents matched.
    """

    acknowledged: Annotated[
        bool,
        Field(
            description=inspect.cleandoc(
                """
                Whether the update was acknowledged
                """
            )
        ),
    ]

    modified_count: Annotated[
        int,
        Field(
            alias="modifiedCount",
            description=inspect.cleandoc(
                """
                Number of documents modified
                """
            ),
        ),
    ]

    upserted_id: Annotated[
        str | None,
        Field(
            alias="upsertedId",
            description=inspect.cleandoc(
                """
                ID of upserted document (if any)
                """
            ),
        ),
    ]

    upserted_count: Annotated[
        int,
        Field(
            alias="upsertedCount",
            description=inspect.cleandoc(
                """
                Number of documents upserted
                """
            ),
        ),
    ]

    matched_count: Annotated[
        int,
        Field(
            alias="matchedCount",
            description=inspect.cleandoc(
                """
                Number of documents matched
                """
            ),
        ),
    ]
