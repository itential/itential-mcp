# Copyright (c) 2025 Itential, Inc
# GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from itential_mcp.core import logging
from itential_mcp.models import work_center as models

LIVE_JOB_STATUS = "running"
LIVE_SESSION_STATUS = "RUNNING"


def _waiting_age_seconds(created_at: Any) -> int | None:
    """Compute seconds elapsed since a work item's creation time.

    Args:
        created_at (Any): Epoch milliseconds (int/float) or an ISO 8601 string.

    Returns:
        int | None: Non-negative elapsed seconds, or None if the value is
            missing or cannot be parsed.

    Raises:
        None
    """
    if created_at is None or isinstance(created_at, bool):
        return None

    created: datetime | None = None
    if isinstance(created_at, (int, float)):
        try:
            created = datetime.fromtimestamp(created_at / 1000, tz=timezone.utc)
        except (OverflowError, OSError, ValueError):
            return None
    elif isinstance(created_at, str):
        try:
            created = datetime.fromisoformat(created_at.replace("Z", "+00:00"))
        except ValueError:
            return None
        if created.tzinfo is None:
            created = created.replace(tzinfo=timezone.utc)

    if created is None:
        return None

    return max(0, int((datetime.now(timezone.utc) - created).total_seconds()))


def summarize(item: dict[str, Any]) -> models.ManualTaskSummary:
    """Build a ManualTaskSummary from a raw work item.

    Args:
        item (dict[str, Any]): A work item as returned by the platform.

    Returns:
        models.ManualTaskSummary: The summary model.

    Raises:
        KeyError: If the item has no `id`.
    """
    view = item.get("view")
    view_type = view.rsplit("/", 1)[-1] if isinstance(view, str) and view else None
    return models.ManualTaskSummary(
        work_item_id=item["id"],
        title=item.get("summary"),
        view_type=view_type,
        waiting_age_seconds=_waiting_age_seconds(item.get("createdAt")),
        completion_supported=models.completion_supported(view_type),
    )


async def pending_manual_tasks(
    client: Any, run_id: str, *, status: str, live_status: str
) -> list[models.ManualTaskSummary] | None:
    """Look up the pending manual tasks for a job or agent session.

    Result semantics (tri-state):
        - `None`: unknown. The lookup raised an error other than 404 (for
          example 403, 500 or a timeout). The caller must still succeed.
        - `[]`: none pending. Covers a 404 (unknown run, no work item created
          yet, or a run that never has one), only completed items, and a
          non-live run. A non-live run returns `[]` without calling the API.
        - list of summaries: the pending items.

    Only manual tasks attached directly to `run_id` are found; nested runs
    (child workflows, agent-calls-workflow) are not guaranteed.

    Args:
        client (Any): The platform client exposing the `work_center` service.
        run_id (str): The job ID or agent session ID.
        status (str): The run's current status.
        live_status (str): The only status for which a lookup is performed
            (`running` for jobs, `RUNNING` for sessions).

    Returns:
        list[models.ManualTaskSummary] | None: See the tri-state semantics.

    Raises:
        None
    """
    if status != live_status:
        return []

    try:
        items = await client.work_center.get_work_items(run_id)
        return [summarize(i) for i in items if i.get("status") == "pending"]
    except Exception as exc:
        if getattr(exc, "http_status", None) == 404:
            return []
        logging.debug(
            f"manual task lookup failed for run {run_id}: {type(exc).__name__}"
            f" (http_status={getattr(exc, 'http_status', None)})"
        )
        return None
