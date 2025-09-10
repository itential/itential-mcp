# Tags

The Itential MCP server supports the use of both include and exclude tags to
control which tools are made available to clients.   Tags can be used in
conjunction with different Itential Platform authentications to create
customzied MCP servers.  This allows operators to constrain what a given MCP
server is allowed to perform against the infrastructure.

When adding a tool to the Itential MCP server, the tool name is the same as the
function name.   For every tool registered with the server, a tag is included
with the tool name.  This allows for every granular level of control.  Specific
tools can easily be excluded or included simply by adding the tool name to the
appropriate configuration option or command line option.

There are standard tags that are also recognized in the Itential MCP server.
by default, all tools with the tag `experimental` or `beta` are excluded from
being registered by default.   This behavior can be changed by modifying the
exclude tags configuration option.

# Tag Groups

The server now supports tag groups.  Tag groups will apply a tag to a group
of tools so they can all be excluded or included with a single tag.  See the
[tools](tools.md) file for a list of all avaiable groups and which tools
are assoicated with those groups.

To add tags to function there is a new decorator available.   For instance,
this below example will add the tags "public", "released" to the tool call
`my_new_tool`.

```python
from fastmcp import Context

from itential_mcp.toolutils import tags

tags("public", "released")
async def my_new_tool(ctx: Context) -> dict:
    """
    Description of what the tool does

    Args:
        ctx (Context): The FastMCP Context object

    Returns:
        dict: The response data

    Raises:
        None
    """
    # Get the platform client
    client = ctx.request_context.lifespan_context.get("client")

    # Make API requests
    res = await client.get("/your/api/path")

    # Return JSON-serializable results
    return res.json()
```

Using the `tags` decorator will attach the tags `public` and `released` to the
tool and those tags can now be used in include and/or exclude tags
configuration options to control tool registration with the server.

# Available Tags Reference

## Tag Groups

The following table lists all available tag groups and the number of tools they contain:

| Tag Group | File(s) | Tools Count | Description |
|-----------|---------|-------------|-------------|
| `adapters` | adapters.py | 4 | Adapter lifecycle management (get, start, stop, restart) |
| `applications` | applications.py | 4 | Application lifecycle management (get, start, stop, restart) |
| `automation_studio` | command_templates.py | 4 | Command templates and device command execution |
| `configuration_manager` | compliance_plans.py, compliance_reports.py, configuration_manager.py, device_groups.py, devices.py, golden_config.py | 15 | Configuration management, compliance, devices, and golden configs |
| `gateway_manager` | gateway_manager.py | 3 | Gateway and service management |
| `health` | health.py | 1 | Platform health monitoring |
| `integrations` | integrations.py | 2 | Integration model management |
| `lifecycle_manager` | lifecycle_manager.py | 6 | Resource lifecycle and instance management |
| `operations_manager` | operations_manager.py | 4 | Workflow execution and job management |
| `workflow_engine` | workflow_engine.py | 6 | Job and task metrics |

## Standard Tags

| Tag | Default Behavior | Description |
|-----|-----------------|-------------|
| `experimental` | Excluded | Tools under development or testing |
| `beta` | Excluded | Tools in beta phase |

## Individual Tool Tags

Every tool function automatically receives a tag matching its function name. This enables fine-grained control over individual tools. The complete list includes 48 tool-specific tags:

### Adapters Tools
- `get_adapters`
- `start_adapter`
- `stop_adapter`
- `restart_adapter`

### Applications Tools
- `get_applications`
- `start_application`
- `stop_application`
- `restart_application`

### Automation Studio Tools
- `get_command_templates`
- `describe_command_template`
- `run_command_template`
- `run_command`

### Configuration Manager Tools
- `get_compliance_plans`
- `run_compliance_plan`
- `describe_compliance_report`
- `render_template`
- `get_device_groups`
- `create_device_group`
- `add_devices_to_group`
- `remove_devices_from_group`
- `get_devices`
- `get_device_configuration`
- `backup_device_configuration`
- `apply_device_configuration`
- `get_golden_config_trees`
- `create_golden_config_tree`
- `add_golden_config_node`

### Gateway Manager Tools
- `get_services`
- `get_gateways`
- `run_service`

### Health Tools
- `get_health`

### Integrations Tools
- `get_integration_models`
- `create_integration_model`

### Lifecycle Manager Tools
- `get_resources`
- `create_resource`
- `describe_resource`
- `get_instances`
- `describe_instance`
- `run_action`

### Operations Manager Tools
- `get_workflows`
- `start_workflow`
- `get_jobs`
- `describe_job`

### Workflow Engine Tools
- `get_job_metrics`
- `get_job_metrics_for_workflow`
- `get_task_metrics`
- `get_task_metrics_for_workflow`
- `get_task_metrics_for_app`
- `get_task_metrics_for_task`

## Usage Examples

### Including specific tag groups:
```bash
--include-tags adapters,health
```

### Excluding beta and experimental features:
```bash
--exclude-tags beta,experimental
```

### Including only specific tools:
```bash
--include-tags get_devices,get_device_configuration
```

### Combining group and individual tags:
```bash
--include-tags configuration_manager,get_health
```
