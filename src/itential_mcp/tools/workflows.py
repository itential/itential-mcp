# Copyright (c) 2025 Itential, Inc
# GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)

from fastmcp import Context


async def get_workflows(
    ctx: Context,
    name: str | None = None,
    include_projects: bool = False
) -> list[dict]:
    """
    Return a list of workflows from an Itential Platform server

    Itential Platform workflows orchestrate services against infrastructure
    and are identified by the "name" field in the object.   Workflows are
    comprised of tasks which perform API calls to perform actions.  The
    inputSchema defines the data required to start the workflow and the
    outputSchema defines the data structure the workflow can provide at the
    conclusion of a successful run.

    Args:
        include_projects (bool): Include all workflows associated with
            projects in the return data.  If this value is set to True
            the list of projects will include global workflows and workflows
            associated with projects.  If this value is set to False it will
            only return global workflows.  The default value is False

        name: (str): The name of the specific worklow to retrieve from the
            Itential Platform server.  This value represents the name of the
            workflow as it is seen in the UI.

    Returns:
        list[dict]: A Python list of dict objects that represent the available
            workflows found on the server.

    Raises:
        None
    """
    await ctx.info("insidex get_workflows(...)")

    client = ctx.request_context.lifespan_context.get("client")

    limit = 100
    skip = 0

    params = {}

    if include_projects is None:
        include_projects = False

    params["exclude-project-members"] = include_projects

    if name is not None:
        params["equals[name]"] = name

    results = list()

    while True:
        res = await client.get("/automation-studio/workflows", params=params)

        data = res.json()
        results.extend(data["items"])

        if len(results) == data["total"]:
            break

        skip += limit

    return results
