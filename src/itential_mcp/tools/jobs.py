# Copyright (c) 2025 Itential, Inc
# GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)

from typing import Annotated

from pydantic import Field

from fastmcp import Context

from itential_mcp import functions


async def get_jobs(
    ctx: Annotated[Context, Field(
        description="The FastMCP Context object"
    )],
    name: Annotated[str | None, Field(
        description="Workflow name used to filter the results",
        default=None
    )],
    project: Annotated[str | None, Field(
        description="Project name used to filter the results",
        default=None
    )]
) -> list[dict]:
    """
    Get all jobs from the Itential Platform server

    This tool will retrieve all jobs from the Itential Platform server and
    return the metdata from the jobs as a list.  The metadata includes the
    job id and name, current job status, and the job description if it was
    set.

    This tool has two optional arguments that can be uesd to filter the
    list of returned jobs.  The first optional argument is name which
    defines the name of the workflow to return jobs for.  This will restrict
    the returned list to only workflows that match this name.

    The second optional argument is project.  By default, the returned list
    only considers workflows in the global namespace.  If the workfow is
    embedded in a project, the project argument must be provided.  This
    argument accepts the project name that contains the workflow.

    If the project argument is specified and the name argument is not
    specified, all workflow jobs assoicated with the project are
    returned.

    The following data is returned for each job in the list:

        * _id: The unique job identifier
        * created: The timestamp when the job was created
        * createdBy: The id of the user that created the job
        * description: A short description of the job created by the user
        * updated: The timestamp of when the job was last updated
        * updatedBy: The id of user that last updated the job
        * name: The name of the job
        * status: The current status of the job.  The job status will be one
            of `error`, `complete`, `running`, `cancelled`, `incomplete`, or
            `paused`

    Args:
        ctx (Context): The FastMCP Context object

        name (str): Only return jobs for workflows that match this value

    Returns:
        list[dict]: A list of Python dict objects where each element
            represents the metadata for a single job

    Raises:
        None:
    """
    await ctx.info("running get_jobs(...)")

    client = ctx.request_context.lifespan_context.get("client")

    results = list()

    limit = 100
    skip = 0

    params = {"limit": limit}

    if project is not None:
        project_id = await functions.project_name_to_id(ctx, project)
        if name is not None:
            params["equals[name]"] = f"@{project_id}: {name}"
        else:
            params["starts-with[name]"] = f"@{project_id}"

    elif name is not None:
        params["equals[name]"] = name

    while True:
        params["skip"] = skip

        res = await client.get("/operations-manager/jobs", params=params)

        data = res.json()
        metadata = data.get("metadata")

        for item in data.get("data") or list():
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

        if len(results) == metadata["total"]:
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
