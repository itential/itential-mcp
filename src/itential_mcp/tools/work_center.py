# Copyright (c) 2025 Itential, Inc
# GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import annotations

import asyncio

from typing import Annotated

from pydantic import Field

from fastmcp import Context

from itential_mcp.utilities.tool import annotate
from itential_mcp.models import work_center as models


__tags__ = ("work_center",)


@annotate(
    read_only=True,
    idempotent=True,
    open_world=False,
    title="Describe Manual Task",
)
async def describe_manual_task(
    ctx: Annotated[Context, Field(description="The FastMCP Context object")],
    work_item_id: Annotated[
        str,
        Field(
            description=(
                "The work item ID of the manual task (the work_item_id from "
                "pending_manual_tasks in describe_job or describe_session)"
            )
        ),
    ],
) -> models.DescribeManualTaskResponse:
    """
    Describe a manual task (work item) that is waiting on, or was given to, a human.

    Use this after describe_job or describe_session reports a non-empty
    pending_manual_tasks list. It returns what a human would see in the task
    (header, message, body, variables and button labels), which view type it
    is, and which job or agent session owns it. This tool is read-only; it
    does not complete or alter the task.

    Args:
        ctx (Context): The FastMCP Context object.
        work_item_id (str): The work item ID, from the work_item_id field of
            pending_manual_tasks in describe_job or describe_session.

    Returns:
        models.DescribeManualTaskResponse: The manual task detail:
            - work_item_id: Work item identifier
            - title: Human-readable task title
            - view_type: View type (ViewData, ViewHTML, InteractiveHTML,
              RenderJsonSchema, ...)
            - completion_supported: Whether MCP can complete this view type
            - status: pending or completed
            - header, message, body, variables: Content shown to the human
            - btn_success, btn_failure: Button labels; btn_failure is empty
              for success-only views (ViewData, ViewHTML)
            - run_id, run_type: The owning job or session ("job"/"session")

    Notes:
        - Identity: the platform executes every MCP operation as the MCP
          service account or OAuth client, with no per-user authorization.
          What this tool can see is what that account can see, not what the
          end user who is talking to the agent is entitled to see.
        - Form views (RenderJsonSchema, viewTemplateResults) report
          completion_supported False.
    """
    await ctx.debug("inside describe_manual_task(...)")

    client = ctx.request_context.lifespan_context.get("client")

    item, incoming = await asyncio.gather(
        client.work_center.get_work_item(work_item_id),
        client.work_center.get_work_item_incoming(work_item_id),
    )

    view = item.get("view")
    view_type = view.rsplit("/", 1)[-1] if isinstance(view, str) and view else None

    execution = item.get("execution") or {}
    root_execution = item.get("rootExecution") or {}
    incoming = incoming or {}

    return models.DescribeManualTaskResponse(
        work_item_id=item.get("id", work_item_id),
        title=item.get("summary"),
        view_type=view_type,
        completion_supported=models.completion_supported(view_type),
        status=item.get("status"),
        header=incoming.get("header"),
        message=incoming.get("message"),
        body=incoming.get("body"),
        variables=incoming.get("variables"),
        btn_success=incoming.get("btn_success"),
        btn_failure=incoming.get("btn_failure"),
        run_id=execution.get("id") or root_execution.get("id"),
        run_type=execution.get("type"),
    )
