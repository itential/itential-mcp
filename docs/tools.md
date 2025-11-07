# Itential MCP Tools Reference

This document provides a comprehensive list of all tools available in the Itential MCP (Model Context Protocol) server, organized by category and including their associated tags for filtering.

## Tool Tags

The following tags are available for filtering tools based on their functionality:

- `adapters` - Adapter lifecycle management tools
- `applications` - Application lifecycle management tools  
- `automation_studio` - Command templates, projects, and template management tools
- `configuration_manager` - Configuration, compliance, device, and golden config management tools
- `gateway_manager` - Gateway and external service management tools
- `health` - Platform health and monitoring tools
- `integrations` - External system integration tools
- `lifecycle_manager` - Resource lifecycle and instance management tools
- `operations_manager` - Workflow and job management tools
- `workflow_engine` - Workflow execution metrics and performance tools

## Tool Count Summary

- **Total Tools**: 56 MCP tools across 17 files
- **Most Popular Tags**: `configuration_manager` (15 tools), `automation_studio` (8 tools), `lifecycle_manager` (7 tools)

## Adapters Management (`adapters.py`)
**Group Tags:** `adapters`

- **get_adapters** - Get all adapters configured on the Itential Platform instance
- **start_adapter** - Start an adapter on Itential Platform with timeout and state validation
- **stop_adapter** - Stop an adapter on Itential Platform with timeout and state validation
- **restart_adapter** - Restart an adapter on Itential Platform with timeout and state validation

## Applications Management (`applications.py`)
**Group Tags:** `applications`

- **get_applications** - Get all applications configured on the Itential Platform instance
- **start_application** - Start an application on Itential Platform with timeout and state validation
- **stop_application** - Stop an application on Itential Platform with timeout and state validation
- **restart_application** - Restart an application on Itential Platform with timeout and state validation

## Command Templates (`command_templates.py`)
**Group Tags:** `automation_studio`

- **get_command_templates** - Get all command templates from Itential Platform (global and project-scoped)
- **describe_command_template** - Get detailed information about a specific command template including commands and rules
- **create_command_template** - Create a new command template with specified name, commands, and validation rules
- **update_command_template** - Update an existing command template with new commands and validation rules
- **run_command_template** - Execute a command template against specified devices with rule evaluation and results
- **run_command** - Run a single command against multiple devices and get execution results

## Templates (`templates.py`)
**Group Tags:** `automation_studio`

- **get_templates** - Get all templates from Automation Studio with optional filtering by template type (textfsm, jinja2)
- **describe_template** - Get detailed information about a specific template from Automation Studio including name, type, group, command, template content, and sample data
- **create_template** - Create a new template in Automation Studio with specified name, type, group, and optional content including command, template text, and sample data
- **update_template** - Update an existing template in Automation Studio with new content including command, template text, and sample data

## Compliance Management (`compliance_plans.py` & `compliance_reports.py`)
**Group Tags:** `configuration_manager`

- **get_compliance_plans** - Get all compliance plans from Itential Platform with pagination support
- **run_compliance_plan** - Execute a compliance plan against network devices and return running instance
- **describe_compliance_report** - Retrieve detailed compliance report results including validation outcomes and rule violations

## Configuration Manager (`configuration_manager.py`)
**Group Tags:** `configuration_manager`

- **render_template** - Render a Jinja2 template with provided variables for configuration generation

## Device Groups (`device_groups.py`)
**Group Tags:** `configuration_manager`

- **get_device_groups** - Get all device groups from Itential Platform with device lists and descriptions
- **create_device_group** - Create a new device group on Itential Platform with optional device assignment and duplicate name validation
- **add_devices_to_group** - Add one or more devices to an existing device group with device list replacement
- **remove_devices_from_group** - Remove one or more devices from an existing device group with filtered device list reconstruction

## Devices Management (`devices.py`)
**Group Tags:** `configuration_manager`

- **get_devices** - Get all devices known to Itential Platform with pagination support
- **get_device_configuration** - Retrieve the current configuration from a network device
- **backup_device_configuration** - Create a backup of a device configuration with description and notes
- **apply_device_configuration** - Apply configuration commands to a network device through Itential Platform

## Gateway Manager (`gateway_manager.py`)
**Group Tags:** `gateway_manager`

- **get_services** - Get all services from Itential Platform Gateway Manager including metadata and schemas
- **get_gateways** - Get all gateways from Gateway Manager with connection status and cluster information
- **run_service** - Execute a service with optional input parameters and get execution results

## Golden Configuration (`golden_config.py`)
**Group Tags:** `configuration_manager`

- **get_golden_config_trees** - Get all Golden Configuration trees with device types and available versions
- **create_golden_config_tree** - Create a new Golden Configuration tree with device type and optional template
- **add_golden_config_node** - Add a new node to an existing Golden Configuration tree with version and path control

## Integrations (`integrations.py`)
**Group Tags:** `integrations`

- **get_integrations** - Get all integration instances from Itential Platform with optional model filtering
- **get_integration_models** - Get all integration models from Itential Platform with OpenAPI specifications
- **create_integration_model** - Create a new integration model from an OpenAPI specification with validation

## Lifecycle Manager (`lifecycle_manager.py`)
**Group Tags:** `lifecycle_manager`

- **get_resources** - Get all Lifecycle Manager resource models with descriptions
- **create_resource** - Create a new Lifecycle Manager resource model with JSON Schema validation
- **describe_resource** - Get detailed information about a resource model including available actions and schemas
- **get_instances** - Get all instances of a Lifecycle Manager resource with instance data and last actions
- **describe_instance** - Get detailed information about a specific resource instance
- **run_action** - Execute a lifecycle action on a resource instance with input parameters and job tracking
- **get_action_executions** - Get action execution history from Lifecycle Manager filtered by resource and instance

## Operations Manager (`operations_manager.py`)
**Group Tags:** `operations_manager`

- **get_workflows** - Get all workflow API endpoints with schemas, route names, and execution history
- **start_workflow** - Execute a workflow by triggering its API endpoint with input validation and job creation
- **expose_workflow** - Expose a workflow as an API endpoint with custom routing and input validation
- **get_jobs** - Get all jobs from Itential Platform with optional workflow and project filtering
- **describe_job** - Get detailed information about a specific job including tasks, metrics, and execution status

## Projects (`projects.py`)
**Group Tags:** `automation_studio`

- **get_projects** - Get all Automation Studio projects from Itential Platform with project metadata
- **describe_project** - Get detailed information about a specific project including all components and artifacts

## Platform Health (`health.py`)
**Group Tags:** `health`

- **get_health** - Get comprehensive health information including system status, resource utilization, and component status

## Workflow Engine Metrics (`workflow_engine.py`)
**Group Tags:** `workflow_engine`

- **get_job_metrics** - Get aggregate job metrics from the Workflow Engine for all workflows
- **get_job_metrics_for_workflow** - Get job metrics for a specific workflow with completion counts and runtime data
- **get_task_metrics** - Get all aggregate task metrics from the Workflow Engine across all workflows
- **get_task_metrics_for_workflow** - Get task metrics for a specific workflow with task performance data
- **get_task_metrics_for_app** - Get task metrics for a specific application across all workflows
- **get_task_metrics_for_task** - Get metrics for a specific named task across all workflows

## Quick Reference by Category

### System Management Tools
| Tag | Tools | Description |
|-----|--------|-------------|
| `health` | 1 tool | Platform health monitoring |

### Device & Network Management Tools  
| Tag | Tools | Description |
|-----|--------|-------------|
| `configuration_manager` | 15 tools | Devices, device groups, compliance, golden config, template rendering |

### Workflow & Automation Tools
| Tag | Tools | Description |
|-----|--------|-------------|
| `operations_manager` | 5 tools | Workflow execution and job management |
| `workflow_engine` | 6 tools | Workflow and task performance metrics |
| `automation_studio` | 8 tools | Command templates, projects, and template management |

### Platform Management Tools
| Tag | Tools | Description |
|-----|--------|-------------|
| `adapters` | 4 tools | Adapter lifecycle management |
| `applications` | 4 tools | Application lifecycle management |
| `lifecycle_manager` | 7 tools | Resource lifecycle and instance management |

### External Integration Tools
| Tag | Tools | Description |
|-----|--------|-------------|
| `gateway_manager` | 3 tools | Gateway and external service management |
| `integrations` | 3 tools | Integration model and instance management |

## Usage Examples

### Filter Tools by Role
```bash
# Network Engineers - Device management focus
itential-mcp --include-tags "configuration_manager"

# Platform Administrators - System health focus  
itential-mcp --include-tags "health,adapters,applications"

# Automation Developers - Workflow focus
itential-mcp --include-tags "operations_manager,workflow_engine,automation_studio"

# Platform Operators - Daily operations
itential-mcp --include-tags "operations_manager,configuration_manager"
```

### Exclude Beta/Experimental Tools
```bash
# Exclude experimental features
itential-mcp --exclude-tags "experimental,beta"
```
