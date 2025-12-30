# Copyright (c) 2025 Itential, Inc
# GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from typing import Literal, Mapping, Any

from itential_mcp.core import exceptions
from itential_mcp.utilities import string as stringutils

from itential_mcp.platform.services import ServiceBase


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

    async def start_workflow(self, route_name: str, data: dict | None = None) -> dict:
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

    async def get_jobs(self, name: str, project: str | None = None) -> list[dict]:
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

    async def describe_job(self, object_id: str) -> dict:
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

    async def start_job(self, workflow: str, description: str, variables: dict) -> dict:
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

    async def create_automation(
        self,
        name: str,
        component_type: Literal["workflows", "ucm_compliance_plan"],
        component_name: str | None = None,
        description: str | None = None,
    ) -> Mapping[str, Any]:
        """Create a new automation in the Operations Manager.

        This method creates an automation object that wraps a workflow or compliance
        plan for execution through the Operations Manager. Automations serve as the
        execution containers that can be triggered through various mechanisms including
        manual triggers, scheduled triggers, or API endpoints.

        The automation acts as a bridge between the underlying component (workflow or
        compliance plan) and the trigger mechanisms that initiate execution.

        Args:
            name (str): The name of the automation to create. This name will be
                used to identify the automation in the Operations Manager.
            component_type (Literal["workflows", "ucm_compliance_plan"]): The type
                of component this automation will execute. "workflows" for Automation
                Studio workflows, "ucm_compliance_plan" for compliance plans.
            component_name (str | None): The name of the specific component to
                associate with this automation. If provided, the method will look up
                the component ID. Defaults to None.
            description (str | None): Optional description for the automation.
                Defaults to None.

        Returns:
            Mapping[str, Any]: The created automation object containing automation
                details including ID, name, description, and associated component information.

        Raises:
            NotFoundError: If the specified component_name is provided but the
                component cannot be found.
            Exception: If there is an error creating the automation in the
                Operations Manager.
        """
        body = {"name": name, "componentType": component_type}

        if description:
            body["description"] = description

        if component_name:
            if component_type == "workflows":
                res = await self.client.get(
                    "/automation-studio/workflows",
                    params={"equals[name]": component_name},
                )
                json_data = res.json()

                if json_data["total"] != 1:
                    raise exceptions.NotFoundError(
                        f"workflow {component_name} not found"
                    )

                body["componentId"] = json_data["items"][0]["_id"]

            elif component_type == "ucm_compliance_plan":
                pass

        res = await self.client.post("/operations-manager/automations", json=body)

        return res.json()["data"]

    async def create_manual_trigger(
        self, name: str, automation_id: str, description: str | None = None
    ) -> Mapping[str, Any]:
        """Create a manual trigger for an automation.

        This method creates a manual trigger that allows users to manually initiate
        an automation through the Itential Platform user interface. Manual triggers
        provide a user-friendly way to execute automations on-demand without requiring
        API calls or scheduled executions.

        The created trigger will be enabled by default and associated with the
        specified automation for execution.

        Args:
            name (str): The name of the manual trigger to create. This name will
                be displayed in the user interface.
            automation_id (str): The unique identifier of the automation that this
                trigger will execute. This should be obtained from create_automation()
                or other automation management methods.
            description (str | None): Optional description for the trigger that
                provides context about its purpose. Defaults to None.

        Returns:
            Mapping[str, Any]: The created trigger object containing trigger details
                including ID, name, description, and associated automation information.

        Raises:
            Exception: If there is an error creating the manual trigger in the
                Operations Manager.
        """
        body = {
            "actionId": automation_id,
            "actionType": "automations",
            "name": name,
            "type": "manual",
            "description": description,
            "enabled": True,
        }

        res = await self.client.post("/operations-manager/triggers", json=body)

        return res.json()["data"]

    async def create_endpoint_trigger(
        self,
        name: str,
        automation_id: str,
        route_name: str,
        schema: dict | None = None,
        description: str | None = None,
    ) -> Mapping[str, Any]:
        """Create an API endpoint trigger for an automation.

        This method creates an HTTP API endpoint trigger that allows external systems
        to initiate automation execution through REST API calls. Endpoint triggers
        enable integration with external systems, webhooks, and programmatic automation
        execution.

        The created endpoint will accept POST requests and can include input validation
        through JSON Schema if provided.

        Args:
            name (str): The name of the endpoint trigger to create. This name will
                be used for identification in the Operations Manager.
            automation_id (str): The unique identifier of the automation that this
                trigger will execute. This should be obtained from create_automation()
                or other automation management methods.
            route_name (str): The API route name that will be used to access this
                endpoint. This becomes part of the URL path for triggering the automation.
            schema (dict | None): Optional JSON Schema definition for validating
                input data sent to the endpoint. If None, a default permissive schema
                is used. Defaults to None.
            description (str | None): Optional description for the trigger that
                provides context about its purpose. Defaults to None.

        Returns:
            Mapping[str, Any]: The created trigger object containing trigger details
                including ID, name, route information, schema, and associated automation.

        Raises:
            Exception: If there is an error creating the endpoint trigger in the
                Operations Manager.
        """
        if not stringutils.is_valid_url_path(route_name):
            raise ValueError("route_name is invalid")

        body = {
            "actionId": automation_id,
            "actionType": "automations",
            "name": name,
            "type": "endpoint",
            "verb": "POST",
            "routeName": route_name,
            "description": description,
            "enabled": True,
            "schema": schema,
        }

        if not schema:
            body["schema"] = {
                "type": "object",
                "properties": {},
                "additionalProperties": True,
            }

        res = await self.client.post("/operations-manager/triggers", json=body)

        return res.json()["data"]

    async def delete_automation(self, automation_id: str) -> Mapping[str, str]:
        """Delete an automation from the Operations Manager.

        This method removes an automation object from the Operations Manager. When
        an automation is deleted, it can no longer be triggered or executed. This
        operation is permanent and cannot be undone.

        Note: Deleting an automation will also affect any associated triggers.
        Ensure that dependent triggers are handled appropriately before deleting
        the automation.

        Args:
            automation_id (str): The unique identifier of the automation to delete.
                This should be the automation ID obtained from create_automation()
                or other automation management methods.

        Returns:
            Mapping[str, str]: A dictionary containing a success message confirming
                the deletion operation.

        Raises:
            Exception: If there is an error deleting the automation from the
                Operations Manager, or if the automation ID is not found.
        """
        res = await self.client.delete(
            f"/operations-manager/automations/{automation_id}"
        )
        json_data = res.json()
        return {"message": json_data["message"]}
