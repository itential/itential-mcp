# Running workflows

The Itential MCP Server exposes workflows through MCP that can be run.  The MCP
server will only consider workflows that have an associated automation created
for them and an API endpoint trigger defined.

When retrieving the list of available workflows, the tool will get the list of
available workflows based on those workflows (automations) that have one or
more configured API endpoint triggers.

To expose a workflow to MCP, simply go into Operations Manager on your Itential
Platform server and create a new Automation.   Once the Automation is created
and the workflow is assigned, create one or more triggers of type `endpoint`.

By using the API endpoint trigger as the preferred entry point, the input
schema can be verbosely described using JSON Schema.  This allows the LLM to
fully understand the necessary inputs for a given workflow.
