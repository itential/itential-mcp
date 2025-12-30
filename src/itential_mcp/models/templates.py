# Copyright (c) 2025 Itential, Inc
# GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import annotations

import inspect

from typing import Annotated, Literal

from pydantic import BaseModel, Field, RootModel


class GetTemplatesElement(BaseModel):
    """Template element model for Automation Studio templates.

    Represents a single template from the Automation Studio with its core
    attributes including unique identifier, name, description, and type.
    Templates are used for text processing, configuration generation,
    and data parsing within automation workflows.

    This model is used as part of the GetTemplatesResponse to provide
    structured template information in API responses.

    Attributes:
        id (str): Unique template identifier assigned by the platform.
        name (str): Human-readable template name.
        description (str | None): Optional template description providing
            context about the template's purpose and usage.
        type (Literal["textfsm", "jinja2"]): Template type indicating the
            processing engine - "textfsm" for parsing templates or "jinja2"
            for configuration templating.
    """

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

    description: Annotated[
        str | None,
        Field(
            description=inspect.cleandoc(
                """
                Template description
                """
            ),
            default=None,
        ),
    ]

    type: Annotated[
        Literal["textfsm", "jinja2"],
        Field(
            description=inspect.cleandoc(
                """
                Template type (textfsm or jinja2)
                """
            ),
        ),
    ]


class GetTemplatesResponse(RootModel):
    """Response model for template retrieval operations.

    Root model that wraps a list of GetTemplatesElement objects to provide
    a standardized response format for template listing operations from
    the Automation Studio.

    This model follows the Pydantic RootModel pattern to create a response
    that serializes directly as a list while maintaining type safety and
    validation capabilities.

    Attributes:
        root (List[GetTemplatesElement]): List of template elements containing
            template metadata and attributes.
    """

    root: Annotated[
        list[GetTemplatesElement],
        Field(
            description=inspect.cleandoc(
                """
                List of templates
                """
            )
        ),
    ]


class DescribeTemplateResponse(GetTemplatesElement):
    """Extended template model for detailed template information.

    Represents a complete template from the Automation Studio with all available
    attributes including group, command, template content, and sample data.
    Extends GetTemplatesElement to provide comprehensive template details for
    describe operations.

    This model is used in template describe, create, and update operations to
    provide full template information including executable content and metadata.

    Attributes:
        Inherits all attributes from GetTemplatesElement (name, description, type)
        plus the following additional fields:

        group (str): The group the template is currently part of for organizational
            purposes within the Automation Studio.
        command (str): The command sent to the device to generate the source text
            that will be processed by the template.
        template (str): The template content used to generate the final output.
            For textfsm templates, contains parsing rules. For jinja2 templates,
            contains templating syntax with variable substitution.
        data (str | None): Sample data used to test the template functionality
            and validate template processing. Optional field that may be None.
    """

    group: Annotated[
        str,
        Field(
            description=inspect.cleandoc(
                """
                The group the template is currently part of
                """
            )
        ),
    ]

    command: Annotated[
        str,
        Field(
            description=inspect.cleandoc(
                """
                The command send to the device to generate the source text
                """
            )
        ),
    ]

    template: Annotated[
        str,
        Field(
            description=inspect.cleandoc(
                """
                The template used to generate the final output
                """
            )
        ),
    ]

    data: Annotated[
        str | None,
        Field(
            description=inspect.cleandoc(
                """
                Sample data used to test the template
                """
            ),
            default=None,
        ),
    ]


CreateTemplateResponse = DescribeTemplateResponse
UpdateTemplateResponse = DescribeTemplateResponse
