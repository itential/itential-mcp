# Copyright (c) 2025 Itential, Inc
# GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)

from fastmcp import Context


async def get_all_jobs(ctx: Context, status: str | None = None) -> list[dict]:
    """
    Get all jobs from the Itential Platform server

    This tool will retrieve all jobs from the Itential Platform server and
    return the metdata from the jobs as a list.  The metadata includes the
    job id and name, current job status, and the job description if it was
    set.

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
    await ctx.info("running get_all_jobs(...)")

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

        cnt += len(results)

        if cnt == metadata["total"]:
            break

        skip += limit

    return results


async def get_job_status(ctx: Context, job_id: str) -> dict:
    """
    Get the status of a job from the Itential Platform.

    This job_id can be obtained after launching a workflow or triggering
    an endpoint.

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

    await ctx.info("inside get_job_status(...)")

    client = ctx.request_context.lifespan_context.get("client")

    res = await client.get(f"/operations-manager/jobs/{job_id}")

    return res.json().get("data")
