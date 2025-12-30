# Copyright (c) 2025 Itential, Inc
# GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from itential_mcp.platform.services import ServiceBase


class Service(ServiceBase):
    """
    Workflow Engine service for interacting with Itential Platform workflow metrics.

    This service provides methods to retrieve workflow and task execution metrics
    from the Itential Platform Workflow Engine. It supports paginated API calls
    to handle large datasets efficiently.

    Attributes:
        name: Service identifier for the workflow engine
    """

    name: str = "workflow_engine"

    async def _get_route(self, path: str, params: dict | None = None) -> list[dict]:
        """
        Generic method to retrieve paginated data from workflow engine API endpoints.

        This internal method handles pagination automatically by making multiple
        API calls with skip/limit parameters until all results are retrieved.
        It's used by both job metrics and task metrics endpoints.

        Args:
            path: The API endpoint path to retrieve data from
            params: Optional query parameters to filter results. The method will
                add pagination parameters (limit, skip) automatically.

        Returns:
            A list of dictionaries containing all results from the paginated API endpoint.
            Each dictionary represents a single metric element (job or task).

        Raises:
            Exception: If there is an error retrieving data from the API endpoint
        """
        limit = 100
        skip = 0

        if params is not None:
            params["limit"] = limit
        else:
            params = {"limit": limit}

        results = list()

        while True:
            params["skip"] = skip

            res = await self.client.get(
                path,
                params=params,
            )

            data = res.json()

            results.extend(data["results"])

            if len(results) == data["total"]:
                break

            skip += limit

        return results

    async def get_job_metrics(self, params: dict | None = None) -> list[dict]:
        """
        Retrieve job metrics from the Workflow Engine.

        Fetches comprehensive job execution metrics including performance data,
        completion statistics, and workflow-specific metrics. This method handles
        pagination automatically to retrieve all available job metrics.

        Args:
            params: Optional query parameters to filter job metrics. Common filters
                include workflow name, date ranges, or execution status. If None,
                all job metrics will be retrieved.

        Returns:
            A list of dictionaries containing job metric data. Each dictionary includes:
                - _id: Unique identifier for the job metric
                - workflow: Name of the workflow
                - metrics: Performance and execution metrics data
                - jobsComplete: Number of completed jobs
                - totalRunTime: Cumulative execution time in seconds

        Raises:
            Exception: If there is an error retrieving job metrics from the API
        """
        return await self._get_route("/workflow_engine/jobs/metrics", params=params)

    async def get_task_metrics(self, params: dict | None = None) -> list[dict]:
        """
        Retrieve task metrics from the Workflow Engine.

        Fetches detailed task-level execution metrics including task performance,
        application usage patterns, and workflow associations. This method handles
        pagination automatically to retrieve all available task metrics.

        Args:
            params: Optional query parameters to filter task metrics. Common filters
                include task name, application name, workflow name, or task type.
                If None, all task metrics will be retrieved.

        Returns:
            A list of dictionaries containing task metric data. Each dictionary includes:
                - taskId: Unique identifier for the task within its workflow
                - taskType: Type of task (automatic, manual)
                - name: Human-readable task name
                - metrics: Task execution and performance metrics
                - app: Application responsible for executing the task
                - workflow: Name of the workflow containing the task

        Raises:
            Exception: If there is an error retrieving task metrics from the API
        """
        return await self._get_route("/workflow_engine/tasks/metrics", params=params)
