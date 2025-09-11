# Copyright (c) 2025 Itential, Inc
# GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)

from itential_mcp import exceptions

from itential_mcp.services import ServiceBase


class Service(ServiceBase):
    """Operations Manager service for Itential Platform workflow and job management.

    This service provides methods for interacting with the Itential Platform's
    Operations Manager component, which handles workflow execution, job management,
    and automation orchestration. It serves as the primary interface for triggering
    workflows, monitoring job execution, and retrieving workflow metadata.

    The Operations Manager is the core automation engine of Itential Platform,
    enabling the execution of complex network automation workflows, device
    management operations, and service provisioning tasks.

    Attributes:
        name (str): The service identifier used for registration and routing.
            Set to "operations_manager".

    Inherits:
        ServiceBase: Base service class providing common functionality including
            client initialization and configuration management.
    """

    name: str = "operations_manager"

    async def get_workflows(self) -> list[dict]:
        """
        Retrieve all workflow API endpoints from Itential Platform.

        This method queries the Itential Platform operations manager to fetch all
        workflow trigger endpoints that are enabled and of type "endpoint". It
        implements pagination to handle large result sets by making multiple API
        calls until all workflows are retrieved.

        Workflows are the core automation engine of Itential Platform, defining
        executable processes that orchestrate network operations, device management,
        and service provisioning. Each workflow exposes an API endpoint that can be
        triggered by external systems or other platform components.

        Args:
            None

        Returns:
            list[dict]: A list of dictionaries containing workflow data.

        Raises:
            Exception: If there is an error communicating with the Itential Platform API
                or if the API returns an unexpected response format.
        """
        limit = 100
        skip = 0

        results = list()

        while True:
            call_params = {
                "limit": limit,
                "skip": skip,
                "equalsField": "type",
                "equals": "endpoint",
                "enabled": True,
            }

            res = await self.client.get(
                "/operations-manager/triggers",
                params=call_params,
            )

            response_data = res.json()
            results.extend(response_data.get("data", []))

            if len(results) >= response_data.get("metadata", {}).get("total", 0):
                break

            skip += limit

        return results

    async def start_workflow(
        self,
        route_name: str,
        data: dict | None = None
    ) -> dict:
        """
        Execute a workflow by triggering its API endpoint.

        This method initiates workflow execution by making a POST request to the
        specified workflow endpoint on the Itential Platform. Workflows are the
        core automation processes that orchestrate network operations, device
        management, and service provisioning.

        The method triggers the workflow and returns job execution details that
        can be monitored for progress and results using other operations manager
        endpoints.

        Args:
            route_name (str): API route name for the workflow endpoint. This should
                correspond to the 'routeName' field from workflow objects returned
                by get_workflows().
            data (dict | None, optional): Input data for workflow execution. The
                structure must match the workflow's input schema. Defaults to None.

        Returns:
            dict: Job execution details containing information about the started
                workflow job, including job ID, status, tasks, and metrics.

        Raises:
            Exception: If there is an error communicating with the Itential Platform API,
                if the workflow endpoint is not found, or if the API returns an
                unexpected response format.

        Examples:
            Start workflow without data:
                >>> result = await service.start_workflow("my-workflow-route")
                >>> print(result["_id"])  # Job ID for monitoring

            Start workflow with input data:
                >>> data = {"device": "router1", "action": "backup"}
                >>> result = await service.start_workflow("backup-device", data)
                >>> print(result["status"])  # Initial job status
        """
        res = await self.client.post(
            f"/operations-manager/triggers/endpoint/{route_name}",
            json=data,
        )

        return res.json().get("data")

    async def get_jobs(
        self,
        name: str,
        project: str | None = None
    ) -> list[dict]:
        """
        Retrieve jobs from Itential Platform operations manager.

        This method queries the Itential Platform to fetch job execution instances
        that track the status, progress, and results of automated workflow tasks.
        It implements pagination to handle large result sets and supports filtering
        by workflow name.

        Jobs represent workflow execution instances and provide visibility into
        automation operations. Each job contains essential information about the
        workflow execution including status, name, description, and unique identifier.

        Note:
            Project filtering is not yet implemented in this service layer method.
            When project parameter is provided, the method raises NotImplementedError.

        Args:
            name (str): Workflow name to filter jobs by. Only jobs from workflows
                with this exact name will be returned.
            project (str | None, optional): Project name for additional filtering.
                Currently not implemented and will raise NotImplementedError if provided.
                Defaults to None.

        Returns:
            list[dict]: A list of dictionaries containing job data. Each dictionary
                contains '_id', 'name', 'description', and 'status' fields.

        Raises:
            NotImplementedError: If project parameter is provided, since project
                filtering is not yet implemented in the service layer.
            Exception: If there is an error communicating with the Itential Platform API
                or if the API returns an unexpected response format.

        Examples:
            Get all jobs for a specific workflow:
                >>> jobs = await service.get_jobs("backup-workflow")
                >>> for job in jobs:
                ...     print(f"Job {job['_id']}: {job['status']}")

            Attempt to filter by project (will raise error):
                >>> # This will raise NotImplementedError
                >>> jobs = await service.get_jobs("workflow", "my-project")
        """
        results = list()

        limit = 100
        skip = 0

        params = {"limit": limit}

        if project is not None:
            res = await self.client.get(
                "/automation-studio/projects", params={"equals[name]": name}
            )

            data = res.json()

            if data["metadata"]["total"] == 0:
                raise exceptions.NotFoundError(f"project {project} could not be found")

            project_id = data["data"][0]["_id"]

            if name is not None:
                params["equals[name]"] = f"@{project_id}: {name}"
            else:
                params["starts-with[name]"] = f"@{project_id}"

        elif name is not None:
            params["equals[name]"] = name

        while True:
            params["skip"] = skip

            res = await self.client.get("/operations-manager/jobs", params=params)

            data = res.json()
            metadata = data.get("metadata")

            for item in data.get("data") or list():
                results.append(
                    {
                        "_id": item.get("_id"),
                        "name": item.get("name"),
                        "description": item.get("description"),
                        "status": item.get("status"),
                    }
                )

            if len(results) == metadata["total"]:
                break

            skip += limit

        return results

    async def describe_job(
        self,
        object_id: str
    ) -> dict:
        """
        Retrieve detailed information about a specific job.

        This method fetches comprehensive details about a job execution instance
        from the Itential Platform operations manager. Jobs are created automatically
        when workflows are executed and contain detailed information about the
        execution including status, tasks, metrics, and results.

        The returned job details provide complete visibility into workflow execution
        progress and can be used for monitoring, debugging, and audit purposes.

        Args:
            object_id (str): Unique job identifier to retrieve. Object IDs are typically
                obtained from start_workflow() responses or get_jobs() results.

        Returns:
            dict: Comprehensive job details including all execution information,
                status, tasks, metrics, timestamps, and results. The exact structure
                depends on the workflow type and execution state.

        Raises:
            Exception: If there is an error communicating with the Itential Platform API,
                if the job is not found, or if the API returns an unexpected response format.

        Examples:
            Get detailed job information:
                >>> job_detail = await service.describe_job("job-123")
                >>> print(f"Status: {job_detail['status']}")
                >>> print(f"Tasks: {job_detail.get('tasks', {})}")
                >>> print(f"Updated: {job_detail.get('last_updated')}")

            Monitor job completion:
                >>> job_detail = await service.describe_job(object_id)
                >>> if job_detail["status"] in ["complete", "error"]:
                ...     print("Job finished")
                ... else:
                ...     print("Job still running")
        """
        res = await self.client.get(f"/operations-manager/jobs/{object_id}")
        return res.json()["data"]

    async def start_job(
        self,
        workflow: str,
        description: str,
        variables: dict
    ) -> dict:
        """Start a job execution directly using workflow name.

        This method initiates a job execution by directly specifying the workflow
        name rather than using a trigger endpoint. It creates a new job with the
        provided description and variables for workflow execution on the Itential
        Platform operations manager.

        This is an alternative way to start workflows compared to start_workflow(),
        which uses trigger endpoints. This method provides more direct control
        over job creation parameters including custom descriptions and variable sets.

        Args:
            workflow (str): The name of the workflow to execute. This should be
                the exact workflow name as defined in the platform.
            description (str): Human-readable description for the job execution.
                This description will be associated with the created job for
                identification and tracking purposes.
            variables (dict): Dictionary of variables to pass to the workflow
                execution. The structure should match the workflow's expected
                input schema.

        Returns:
            dict: Job creation response containing details about the newly created
                job including job ID, status, and other execution metadata.

        Raises:
            Exception: If there is an error communicating with the Itential Platform API,
                if the workflow is not found, or if the API returns an unexpected
                response format.

        Examples:
            Start a job with description and variables:
                >>> variables = {"device": "router1", "config": "template1"}
                >>> result = await service.start_job(
                ...     "device-config-workflow",
                ...     "Configure router1 with template1",
                ...     variables
                ... )
                >>> print(f"Job created: {result.get('_id')}")

            Start a job with minimal parameters:
                >>> result = await service.start_job(
                ...     "health-check",
                ...     "Scheduled health check",
                ...     {}
                ... )
        """
        body = {
            "workflow": workflow,
            "options": {
                "type": "automation",
                "groups": [],
                "description": description or "",
                "variables": variables or {},
            },
        }

        res = await self.client.post("/operations_manager/jobs/start", json=body)

        return res.json()
