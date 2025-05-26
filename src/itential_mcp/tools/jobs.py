# Copyright (c) 2025 Itential, Inc
# GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)

from fastmcp import Context


async def get_job_status(ctx: Context, job_id: str) -> dict:
    """
    Get the status of a job from the Itential Platform

    Args:
        ctx (Context): The FastMCP Context object

        job_id (str): The job identifier returned from thjob _id returned
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
