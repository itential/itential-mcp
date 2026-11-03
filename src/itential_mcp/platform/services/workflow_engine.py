# Copyright (c) 2025 Itential, Inc
# GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import annotations

from typing import Any

from itential_mcp.platform.services import ServiceBase


class Service(ServiceBase):
    """
    Workflow Engine service for interacting with Itential Platform workflow metrics.

    This service provides methods to retrieve workflow and task execution metrics
    from the Itential Platform Workflow Engine. It supports bounded, single-page
    API calls (limit/skip) so that large datasets are never retrieved in full.

    Attributes:
        name: Service identifier for the workflow engine
    """

    name: str = "workflow_engine"

    async def _get_route(
        self,
        path: str,
        params: dict[str, Any] | None = None,
        *,
        limit: int = 200,
        skip: int = 0,
    ) -> tuple[list[dict[str, Any]], int]:
        """Retrieve a single page of data from a workflow engine API endpoint.

        This internal method makes one request with the given skip/limit values
        so that response size stays bounded. It is used by both the job metrics
        and task metrics endpoints.

        Args:
            path: The API endpoint path to retrieve data from
            params: Optional query parameters to filter results (for example
                equals/equalsField or contains/containsField)
            limit: Maximum number of items to return (default: 200)
            skip: Number of items to skip (default: 0)

        Returns:
            tuple[list[dict[str, Any]], int]: The metric elements in the page and
                the total number of matching elements on the platform

        Raises:
            Exception: If there is an error retrieving data from the API endpoint
        """
        return await self._get_page(
            path,
            params=params,
            limit=limit,
            skip=skip,
            data_key="results",
            total_key="total",
        )

    async def get_job_metrics(
        self,
        params: dict[str, Any] | None = None,
        *,
        limit: int = 200,
        skip: int = 0,
    ) -> tuple[list[dict[str, Any]], int]:
        """
        Retrieve a page of job metrics from the Workflow Engine.

        Fetches job execution metrics including performance data, completion
        statistics, and workflow-specific metrics. Exactly one page is
        requested; use `skip` to walk through larger result sets.

        Args:
            params: Optional query parameters to filter job metrics. Common filters
                include workflow name, date ranges, or execution status. If None,
                all job metrics are eligible.
            limit: Maximum number of job metrics to return (default: 200)
            skip: Number of job metrics to skip (default: 0)

        Returns:
            A tuple of (items, total). Items is a list of dictionaries, each
            including:
                - _id: Unique identifier for the job metric
                - workflow: Name of the workflow
                - metrics: Performance and execution metrics data
                - jobsComplete: Number of completed jobs
                - totalRunTime: Cumulative execution time in seconds
            Total is the number of job metrics available on the platform.

        Raises:
            Exception: If there is an error retrieving job metrics from the API
        """
        return await self._get_route(
            "/workflow_engine/jobs/metrics", params=params, limit=limit, skip=skip
        )

    async def get_task_metrics(
        self,
        params: dict[str, Any] | None = None,
        *,
        limit: int = 200,
        skip: int = 0,
    ) -> tuple[list[dict[str, Any]], int]:
        """
        Retrieve a page of task metrics from the Workflow Engine.

        Fetches task-level execution metrics including task performance,
        application usage patterns, and workflow associations. Exactly one page
        is requested; use `skip` to walk through larger result sets.

        Args:
            params: Optional query parameters to filter task metrics. Common filters
                include task name, application name, workflow name, or task type.
                If None, all task metrics are eligible.
            limit: Maximum number of task metrics to return (default: 200)
            skip: Number of task metrics to skip (default: 0)

        Returns:
            A tuple of (items, total). Items is a list of dictionaries, each
            including:
                - taskId: Unique identifier for the task within its workflow
                - taskType: Type of task (automatic, manual)
                - name: Human-readable task name
                - metrics: Task execution and performance metrics
                - app: Application responsible for executing the task
                - workflow: Name of the workflow containing the task
            Total is the number of task metrics available on the platform.

        Raises:
            Exception: If there is an error retrieving task metrics from the API
        """
        return await self._get_route(
            "/workflow_engine/tasks/metrics", params=params, limit=limit, skip=skip
        )
