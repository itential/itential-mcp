# Copyright (c) 2025 Itential, Inc
# GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)
import re

from typing import Annotated

from pydantic import Field

from fastmcp import Context


async def get_jobs(
    ctx: Annotated[Context, Field(
        description="The FastMCP Context object"
    )],
    status: Annotated[str | None, Field(
        description="Job status used to filter the results",
        default=None
    )]
) -> list[dict]:
    """
    Get all jobs from the Itential Platform server

    This tool will retrieve all jobs from the Itential Platform server and
    return the metdata from the jobs as a list.  The metadata includes the
    job id and name, current job status, and the job description if it was
    set.

    This tool accepts an optional `status` argument that can be used to
    filter the list of returned jobs.  By default all jobs found on the
    server are returned.  Setting the `status` argument will return only
    those jobs that match the value for `status`.  Valid values for `status`
    include `error`, `complete`, `running`, `cancelled`, `incomplete` or
    `paused`.

    The following data is returned for each job in the list:

        * _id: The unique job identifier
        * created: The timestamp when the job was created
        * created_by: The id of the user that created the job
        * description: A short description of the job created by the user
        * updated: The timestamp of when the job was last updated
        * updated_by: The id of user that last updated the job
        * name: The name of the job
        * status: The current status of the job.  The job status will be one
            of `error`, `complete`, `running`, `cancelled`, `incomplete`, or
            `paused`

    Args:
        ctx (Context): The FastMCP Context object

        status (str): Filter the jobs by the current job status.

    Returns:
        list[dict]: A list of Python dict objects where each element
            represents the metadata for a single job

    Raises:
        None
    """
    await ctx.info("running get_jobs(...)")

    client = ctx.request_context.lifespan_context.get("client")

    results = list()

    limit = 100
    skip = 0
    cnt = 0

    params = {"limit": limit}

    while True:
        params["skip"] = skip

        res = await client.get("/operations-manager/jobs", params=params)

        data = res.json()
        metadata = data.get("metadata")

        for item in data.get("data") or list():
            if status is None or (status is not None and item["status"] == status):
                results.append({
                    "_id": item.get("_id"),
                    "created": item.get("created"),
                    "created_by": item.get("created_by"),
                    "updated": item.get("last_updated"),
                    "updated_by": item.get("last_updated_by"),
                    "name": item.get("name"),
                    "description": item.get("description"),
                    "status": item.get("status")
                })

        cnt += len(data)

        if cnt == metadata["total"]:
            break

        skip += limit

    return results


async def describe_job(
    ctx: Annotated[Context, Field(
        description="The FastMCP Context object"
    )],
    job_id: Annotated[str, Field(
        description="The ID used to retreive the job"
    )]
) -> dict:
    """
    Get details about a job from Itential Platform

    When a workflow is started a new job is automatically created that
    contains the status of the job.  All details about the job are stored
    in the job document.  The job document provides information about
    the execution of a workflow.

    This function will retrieve the job document from Itential Platform based
    on the unique `job_id` argument.   The `job_id` is used to uniquely
    identify the desired job document.

    The job document will return the following:
        * _id: The unique identifier for this job
        * name: The name of the API endpoint trigger
        * description: Short description of the API endpoint trigger
        * type: Identifies the type of job.  Valid values for type are
            `automation`, `resource:action`, or `resource:compliance`
        * tasks: The full set of tasks to be executed
        * updated: ISO 8601 timestamp of when the trigger was last updated
        * status: The status of the job.  This will return one of the
            following values: `error`, `complete`, `running`, `canceled`,
            `incomplete` or `paused`
        * metrics: Job metrics that include the job start time, job end
            time and account

    Args:
        ctx (Context): The FastMCP Context object

        job_id (str): The job identifier returned from the job _id returned
            for any triggered job

    Returns:
        dict: A Python dict object that represents the job status from the
            server

    Raises:
        None
    """

    await ctx.info("inside describe_job(...)")

    client = ctx.request_context.lifespan_context.get("client")

    res = await client.get(f"/operations-manager/jobs/{job_id}")

    data = res.json()["data"]

    return {
        "_id": data["_id"],
        "name": data["name"],
        "description": data["description"],
        "type": data["type"],
        "tasks": data["tasks"],
        "status": data["status"],
        "metrics": data["metrics"],
        "updated": data["last_updated"]
    }


async def get_single_workflow_jobs(
    ctx: Annotated[Context, Field(
        description="The FastMCP Context object"
    )],
    workflow_name: Annotated[str, Field(
        description="The workflow name used for the job"
    )]
) -> list[dict]:
    """
    Get details about jobs for given a workflow from Itential Platform

    When a workflow is started a new job is automatically created that
    contains the status of the job.  All details about the job are stored
    in the job document.  The job document provides information about
    the execution of a workflow.

    This function will retrieve multiple job documents from Itential Platform based
    on the provided `workflow_name` argument.   

    The job documents will return the following:
        * _id: The unique identifier for this job
        * name: The name of the API endpoint trigger
        * description: Short description of the API endpoint trigger
        * type: Identifies the type of job.  Valid values for type are
            `automation`, `resource:action`, or `resource:compliance`
        * tasks: The full set of tasks to be executed
        * updated: ISO 8601 timestamp of when the trigger was last updated
        * status: The status of the job.  This will return one of the
            following values: `error`, `complete`, `running`, `canceled`,
            `incomplete` or `paused`
        * metrics: Job metrics that include the job start time, job end
            time and account

    Args:
        ctx (Context): The FastMCP Context object

        workflow_name (str): The workflow_name

    Returns:
        dict: A list of job status dicts from the server

    Raises:
        None
    """

    await ctx.info("inside describe_job(...)")

    client = ctx.request_context.lifespan_context.get("client")

    res = await client.get("/operations-manager/jobs")

    res_json = res.json()
    data = res_json.get("data", [])

    if not isinstance(data, list):
        await ctx.error(f"Unexpected 'data' format in job response: {type(data)}")
        return None

    results = list()

    pattern = re.compile(f".*{re.escape(workflow_name)}.*", re.IGNORECASE)

    for item in data:
        if pattern.search(item.get("name")):

            results.append({
                "_id": item.get("_id"),
                "name": item.get("name", ""),
                "description": item.get("description", ""),
                "type": item.get("type", ""),
                "tasks": item.get("tasks", []),
                "status": item.get("status", "unknown"),
                "metrics": item.get("metrics", {}),
                "updated": item.get("last_updated", "")
            })

    return results
