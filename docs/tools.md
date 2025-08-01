# Itential MCP Tools Reference

This document provides a comprehensive list of all tools available in the Itential MCP (Model Context Protocol) server, organized by category.

## Adapters Management (`adapters.py`)
- **get_adapters** - Get all adapters configured on the Itential Platform instance
- **start_adapter** - Start an adapter on Itential Platform
- **stop_adapter** - Stop an adapter on Itential Platform
- **restart_adapter** - Restart an adapter on Itential Platform

## Applications Management (`applications.py`)
- **get_applications** - Get all applications configured on the Itential Platform instance
- **start_application** - Start an application on Itential Platform
- **stop_application** - Stop an application on Itential Platform
- **restart_application** - Restart an application on Itential Platform

## Command Templates (`command_templates.py`)
- **get_command_templates** - Get all command templates from Itential Platform
- **describe_command_template** - Get detailed information about a specific command template
- **run_command_template** - Execute a command template against specified devices with rule evaluation
- **run_command** - Run a single command against multiple devices

## Compliance Management (`compliance_plans.py` & `compliance_reports.py`)
- **get_compliance_plans** - Get all compliance plans from Itential Platform
- **run_compliance_plan** - Execute a compliance plan against network devices
- **describe_compliance_report** - Retrieve detailed compliance report results from Itential Platform

## Configuration Manager (`configuration_manager.py`)
- **render_template** - Render a Jinja2 template with provided variables

## Device Groups (`device_groups.py`)
- **get_device_groups** - Get all device groups from Itential Platform
- **create_device_group** - Create a new device group on Itential Platform

## Devices Management (`devices.py`)
- **get_devices** - Get all devices known to Itential Platform
- **get_device_configuration** - Retrieve the current configuration from a network device
- **backup_device_configuration** - Create a backup of a device configuration in Itential Platform
- **apply_device_configuration** - Apply configuration commands to a network device through Itential Platform

## Integrations (`integrations.py`)
- **get_integration_models** - Get all integration models from Itential Platform
- **create_integration_model** - Create a new integration model on Itential Platform from an OpenAPI specification

## Jobs Management (`jobs.py`)
- **get_jobs** - Get all jobs from Itential Platform with optional filtering
- **describe_job** - Get detailed information about a specific job from Itential Platform

## Lifecycle Manager (`lifecycle_manager.py`)
- **get_resources** - Get all Lifecycle Manager resource models from Itential Platform
- **create_resource** - Create a new Lifecycle Manager resource model on Itential Platform
- **describe_resource** - Get detailed information about a Lifecycle Manager resource model
- **get_instances** - Get all instances of a Lifecycle Manager resource from Itential Platform

## System Health (`system.py`)
- **get_health** - Get comprehensive health information from Itential Platform

## Workflow Engine Metrics (`workflow_engine.py`)
- **get_job_metrics** - Get aggregate job metrics from the Workflow Engine
- **get_job_metrics_for_workflow** - Get the job metrics for the specified workflow
- **get_task_metrics** - Get all aggregate task metrics from the Workflow Engine
- **get_task_metrics_for_workflow** - Get all task metrics for the specified workflow
- **get_task_metrics_for_app** - Get all task metrics for the specified application
- **get_task_metrics_for_task** - Get all task metrics for the named task

## Workflows (`workflows.py`)
- **get_workflows** - Get all workflow API endpoints from Itential Platform
- **start_workflow** - Execute a workflow by triggering its API endpoint

## Tool Categories Summary

1. **Infrastructure Management**: Tools for managing adapters, applications, and system health
2. **Device Operations**: Tools for device configuration, backup, and group management
3. **Automation**: Tools for workflows, command templates, and job execution
4. **Compliance & Configuration**: Tools for compliance checking and configuration management
5. **Integration**: Tools for managing external system integrations via OpenAPI specs
6. **Lifecycle Management**: Tools for resource modeling and instance management
7. **Monitoring & Metrics**: Tools for tracking workflow and task performance metrics

Each tool is designed to interact with the Itential Platform's REST API to provide comprehensive network automation capabilities through the Model Context Protocol.
