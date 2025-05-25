# Copyright (c) 2025 Itential, Inc
# GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)

import urllib.parse

from ipsdk.platform import AsyncPlatform

from fastmcp import Context


async def _get_group_id_from_name(
    client: AsyncPlatform,
    name: str
) -> str:
    """
    Get the group ID for the group name

    This function will attempt to find the group ID for the group name
    specified in the `name` argument.   If the group exists, the group
    id will be returned to the calling function.  If the group does not
    exist, this function will raise an exception.

    Args:
        client (AsyncPlatform): An instance of `ipsdk.platform.AsyncPlatform`
        name (str): The group name translate to group ID

    Returns:
        str: The group ID associated with the group name

    Raises:
        ValueErorr: If the group name is not found on the server
    """
    res = client.get("/authorization/groups")
    for item in res.json()["results"]:
        if item["name"] == name:
            return item["_id"]
    else:
        raise ValueError(f"group `{name}` not found")


async def describe_workflow(
    ctx: Context,
    name: str
) -> dict:
    """
    Describe a workflow in detail

    Workflows can be uniquely described by the workflow name.  The `name`
    argument is used to find the specified workflow and return the entire
    workflow document.

    Args:
        ctx (Context): The FastMCP Context object

        name: (str): The name of the specific worklow to retrieve from the
            Itential Platform server.  This value represents the name of the
            workflow as it is seen in the UI.

        Returns:
            dict: A Python dict object that describes the workflow specified
                by the `name` argument

    Raises:
        None
    """
    await ctx.info("inside describe_workflow(...)")

    client = ctx.request_context.lifespan_context.get("client")

    res = await client.get(
        urllib.parse.quote(f"/automation-studio/workflows/detailed/{name}")
    )

    return res.json()



async def get_workflows(
    ctx: Context,
    include_projects: bool = False,
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
        ctx (Context): The FastMCP Context object

        include_projects (bool): Include all workflows associated with
            projects in the return data.  If this value is set to True
            the list of projects will include global workflows and workflows
            associated with projects.  If this value is set to False it will
            only return global workflows.  The default value is False

    Returns:
        list[dict]: A Python list of dict objects that represent the available
            workflows found on the server.

    Raises:
        None
    """
    await ctx.info("inside get_workflows(...)")

    client = ctx.request_context.lifespan_context.get("client")

    limit = 100
    skip = 0

    params = {"limit": limit}

    if include_projects is None:
        include_projects = False

    params["exclude-project-members"] = include_projects

    results = list()

    while True:
        params["skip"] = skip

        res = await client.get("/automation-studio/workflows", params=params)

        data = res.json()

        for item in data.get("items") or list():
            results.append({
                "_id": item.get("_id"),
                "created": item.get("created"),
                "created_by": item.get("created_by"),
                "updated": item.get("last_updated"),
                "updated_by": item.get("last_updated_by"),
                "name": item.get("name"),
                "description": item.get("description")
            })

        if len(results) == data["total"]:
            break

        skip += limit

    return results


async def start_workflow(
    ctx: Context,
    name: str,
    description: str | None = None,
    variables: dict | None = None,
    groups: list | None = None,
) -> dict:
    """
    Start a workflow

    Itential Platform provides a set of workflows that can be run from the
    server.  This function provides a way to start workflow.  It will
    attempt to start the workflow specified by the `name` argument.

    Args:
        ctx (Context): The FastMCP Context object
        name (str): The name of the workflow to start
        description (str): A short summary description that describes this
            particular workflow run
        variables: (dict): One or more variables to inject into the workflow
            when it is started
        groups (list): A list of groups that have access to the running
            workflow.  This function will handle translating the list
            of group names to group ids.

    Returns:
        dict: A Python dict object that is the job document from Itential
            Platform workflow engine

    Raises:
        ValueError: Raised if one of the specified groups does not exist
            on the server
        ValueError: Raises if the workflow specified by `name` does not
            exist on the server
    """
    await ctx.info("inside get_workflows(...)")

    client = ctx.request_context.lifespan_context.get("client")

    group_ids = list()
    if groups is not None:
        try:
            for item in groups:
                group_ids.append(_get_group_id_from_name(client, item))
        except ValueError:
            await ctx.error(f"group `{item}` does not exist")
            raise

    body = {
        "workflow": name,
        "options": {
            "description": description,
            "type": "automation",
            "variables": {} if variables is None else variables,
            "groups": group_ids,
        }
    }

    res = await client.post(
        "/operations-manager/jobs/start",
        json=body
    )

    return res.json()
