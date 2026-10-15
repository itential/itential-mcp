# Copyright (c) 2025 Itential, Inc
# GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import annotations

import inspect

from typing import Annotated, Any

from pydantic import BaseModel, Field


# Manual task views whose incoming variables are a known, simple shape and
# that are completed by a single success (and optionally failure) action.
_COMPLETION_SUPPORTED_VIEWS = frozenset({"ViewData", "ViewHTML", "InteractiveHTML"})


def completion_supported(view_type: str | None) -> bool:
    """Report whether a manual task view type is one MCP can complete.

    Form-style views (RenderJsonSchema, viewTemplateResults) require
    variables in a format that is not yet known, so they are reported as
    unsupported. ViewData, ViewHTML and InteractiveHTML are supported. Any
    view type not recognized is treated as unsupported.

    Args:
        view_type (str | None): The view type, for example "ViewData".

    Returns:
        bool: True if the view type is known to be completable, else False.

    Raises:
        None
    """
    return view_type in _COMPLETION_SUPPORTED_VIEWS


class ManualTaskSummary(BaseModel):
    """
    Summary of a manual task that is waiting on a human.

    Attributes:
        work_item_id: Work item identifier; pass to describe_manual_task.
        title: The task's human-readable title, verbatim from the platform.
        view_type: The task view type (for example "ViewData").
        waiting_age_seconds: Seconds the task has been waiting, or None if
            the creation time is unavailable.
        completion_supported: Whether MCP can complete this view type.
    """

    work_item_id: Annotated[
        str,
        Field(
            description=inspect.cleandoc(
                """
                Work item identifier; pass to describe_manual_task for detail
                """
            )
        ),
    ]

    title: Annotated[
        str | None,
        Field(
            description=inspect.cleandoc(
                """
                Human-readable title of the manual task, as set by the
                workflow author
                """
            ),
            default=None,
        ),
    ]

    view_type: Annotated[
        str | None,
        Field(
            description=inspect.cleandoc(
                """
                Manual task view type, for example ViewData, ViewHTML,
                InteractiveHTML or RenderJsonSchema
                """
            ),
            default=None,
        ),
    ]

    waiting_age_seconds: Annotated[
        int | None,
        Field(
            description=inspect.cleandoc(
                """
                Seconds the task has been waiting on a human (now minus the
                work item's creation time); None if unavailable
                """
            ),
            default=None,
        ),
    ]

    completion_supported: Annotated[
        bool,
        Field(
            description=inspect.cleandoc(
                """
                True if this view type is one that MCP can complete (ViewData,
                ViewHTML, InteractiveHTML); False for form views and unknown
                view types
                """
            ),
            default=False,
        ),
    ]


class DescribeManualTaskResponse(BaseModel):
    """
    Response model for describe_manual_task.

    Attributes:
        work_item_id: Work item identifier.
        title: Human-readable title of the manual task.
        view_type: Task view type.
        completion_supported: Whether MCP can complete this view type.
        status: Work item status (pending or completed).
        header: Header text shown to the human.
        message: Message text shown to the human.
        body: Body content shown to the human.
        variables: Variables supplied to the task view.
        btn_success: Label of the success button.
        btn_failure: Label of the failure button; empty or None when the
            view is success-only.
        run_id: Identifier of the job or session that owns the task.
        run_type: Whether the owning run is a "job" or a "session".
    """

    work_item_id: Annotated[
        str,
        Field(description=inspect.cleandoc("""Work item identifier""")),
    ]

    title: Annotated[
        str | None,
        Field(
            description=inspect.cleandoc(
                """
                Human-readable title of the manual task
                """
            ),
            default=None,
        ),
    ]

    view_type: Annotated[
        str | None,
        Field(
            description=inspect.cleandoc(
                """
                Manual task view type, for example ViewData, ViewHTML,
                InteractiveHTML or RenderJsonSchema
                """
            ),
            default=None,
        ),
    ]

    completion_supported: Annotated[
        bool,
        Field(
            description=inspect.cleandoc(
                """
                True if this view type is one that MCP can complete; False
                for form views and unknown view types
                """
            ),
            default=False,
        ),
    ]

    status: Annotated[
        str | None,
        Field(
            description=inspect.cleandoc(
                """
                Work item status (pending or completed)
                """
            ),
            default=None,
        ),
    ]

    header: Annotated[
        str | None,
        Field(
            description=inspect.cleandoc(
                """
                Header text presented to the human
                """
            ),
            default=None,
        ),
    ]

    message: Annotated[
        str | None,
        Field(
            description=inspect.cleandoc(
                """
                Message text presented to the human
                """
            ),
            default=None,
        ),
    ]

    body: Annotated[
        Any | None,
        Field(
            description=inspect.cleandoc(
                """
                Body content presented to the human
                """
            ),
            default=None,
        ),
    ]

    variables: Annotated[
        Any | None,
        Field(
            description=inspect.cleandoc(
                """
                Variables supplied to the task view
                """
            ),
            default=None,
        ),
    ]

    btn_success: Annotated[
        str | None,
        Field(
            description=inspect.cleandoc(
                """
                Label of the success button
                """
            ),
            default=None,
        ),
    ]

    btn_failure: Annotated[
        str | None,
        Field(
            description=inspect.cleandoc(
                """
                Label of the failure button; empty when the view is
                success-only (ViewData, ViewHTML)
                """
            ),
            default=None,
        ),
    ]

    run_id: Annotated[
        str | None,
        Field(
            description=inspect.cleandoc(
                """
                Identifier of the job or agent session that owns this task
                """
            ),
            default=None,
        ),
    ]

    run_type: Annotated[
        str | None,
        Field(
            description=inspect.cleandoc(
                """
                Type of the owning run: job or session
                """
            ),
            default=None,
        ),
    ]
