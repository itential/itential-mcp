# Creating Custom Tools for Itential MCP

This guide explains how to create custom tools for the Itential MCP server and load them using the new `--tools-path` argument. Custom tools allow you to extend the MCP server's functionality with your own automation logic while leveraging the existing Itential Platform integration.

## Table of Contents

- [Overview](#overview)
- [Tool Structure](#tool-structure)
- [Output Schemas with Pydantic](#output-schemas-with-pydantic)
- [Using Tags](#using-tags)
- [Loading Custom Tools](#loading-custom-tools)
- [Examples](#examples)
- [Best Practices](#best-practices)

## Overview

Custom tools are Python functions that follow specific conventions and can be dynamically loaded by the Itential MCP server. They provide a way to extend the server's capabilities without modifying the core codebase.

### Key Features

- **Dynamic Loading**: Tools are automatically discovered and loaded from specified directories
- **Tag-based Filtering**: Control which tools are exposed using include/exclude tags
- **FastMCP Integration**: Full integration with the Model Context Protocol framework
- **Itential Platform Access**: Access to the Itential Platform client and configuration

## Tool Structure

### Basic Tool Function

A custom tool is a Python function that takes a `Context` parameter and returns data. Here's the basic structure:

```python
from fastmcp import Context

async def my_custom_tool(ctx: Context, parameter1: str, parameter2: int = 42) -> dict:
    """
    Description of what this tool does.

    Args:
        ctx: The FastMCP Context object containing request context and platform client
        parameter1: Description of parameter1
        parameter2: Description of parameter2 with default value

    Returns:
        dict: Description of return value

    Raises:
        Exception: Description of when exceptions might be raised
    """
    # Access the Itential Platform client
    client = ctx.request_context.lifespan_context.get("client")

    # Perform your custom logic
    result = await client.get("/some/endpoint")

    return {
        "status": "success",
        "data": result.json(),
        "parameter1": parameter1,
        "parameter2": parameter2
    }
```

### File Structure

Custom tools should be organized in Python modules within a directory:

```
my-custom-tools/
├── __init__.py          # Optional, can be empty
├── network_tools.py     # Tools related to network operations
├── device_tools.py      # Tools related to device management
└── utility_tools.py     # General utility tools
```

## Output Schemas with Pydantic

The Itential MCP server automatically generates output schemas for tools when they use Pydantic models as return types. This enables AI agents to understand the structure of the data your tools return, improving their ability to work with the results.

### Why Use Pydantic Models?

When you return a Pydantic model from your tool function, the server automatically:

1. **Generates JSON Schema**: The tool's output schema is automatically created from the Pydantic model
2. **Validates Output**: Ensures your tool returns data in the expected format
3. **Provides Type Safety**: Offers better IDE support and runtime validation
4. **Improves Agent Understanding**: AI agents can better interpret and use the structured data

### Basic Pydantic Model Example

```python
from fastmcp import Context
from pydantic import BaseModel, Field
from typing import Optional

class PingResult(BaseModel):
    """Result of a ping operation."""
    hostname: str = Field(description="The hostname or IP address that was pinged")
    success: bool = Field(description="Whether the ping was successful")
    packet_loss: Optional[float] = Field(None, description="Percentage of packet loss (0-100)")
    avg_response_time: Optional[float] = Field(None, description="Average response time in milliseconds")
    output: str = Field(description="Raw ping command output")
    error: Optional[str] = Field(None, description="Error message if ping failed")

async def ping_host(ctx: Context, hostname: str, count: int = 4) -> PingResult:
    """
    Ping a host and return structured results.

    This function automatically generates an output schema because it returns a PydantinModel.
    """
    import subprocess

    try:
        result = subprocess.run(
            ["ping", "-c", str(count), hostname],
            capture_output=True,
            text=True,
            timeout=30
        )

        # Parse output for packet loss and response time
        packet_loss = _parse_packet_loss(result.stdout)
        avg_time = _parse_avg_time(result.stdout)

        return PingResult(
            hostname=hostname,
            success=result.returncode == 0,
            packet_loss=packet_loss,
            avg_response_time=avg_time,
            output=result.stdout,
            error=result.stderr if result.stderr else None
        )
    except subprocess.TimeoutExpired:
        return PingResult(
            hostname=hostname,
            success=False,
            packet_loss=None,
            avg_response_time=None,
            output="",
            error="Ping timeout"
        )

def _parse_packet_loss(output: str) -> Optional[float]:
    """Extract packet loss percentage from ping output."""
    import re
    match = re.search(r'(\d+)% packet loss', output)
    return float(match.group(1)) if match else None

def _parse_avg_time(output: str) -> Optional[float]:
    """Extract average response time from ping output."""
    import re
    match = re.search(r'avg = ([\d.]+)', output)
    return float(match.group(1)) if match else None
```

### Schema Generation Behavior

**With Pydantic Model Return Type (Recommended):**
```python
async def structured_tool(ctx: Context) -> MyModel:
    # Automatically generates output schema from MyModel
    # AI agents understand the exact structure of returned data
    return MyModel(field1="value", field2=42)
```

**With Dict Return Type (Still Valid):**
```python
async def unstructured_tool(ctx: Context) -> dict:
    # No automatic schema generation - agents receive less structural information
    # Tool works normally but agents may be less effective at using the results
    return {"field1": "value", "field2": 42}
```

**What Happens When Schema is Missing:**
- The server logs a warning: `"tool {function_name} has a missing or invalid output_schema"`
- The tool is still registered and fully functional
- AI agents receive less information about the expected output structure
- May result in less effective agent interactions with your tool's output

## Using Tags

Tags are used to organize and filter tools. You can apply tags at both the module level and function level.  By default, the function name will also be converted to a tag that can be used to include or exclude specific functions.

### Module-Level Tags

Use the `__tags__` variable to apply tags to all functions in a module:

```python
# network_tools.py
from fastmcp import Context

# Apply these tags to all functions in this module
__tags__ = ["network", "infrastructure", "public"]

async def get_network_topology(ctx: Context) -> dict:
    """Get network topology information."""
    # Implementation here
    return {"topology": "data"}

async def validate_network_config(ctx: Context, config: str) -> dict:
    """Validate network configuration."""
    # Implementation here
    return {"valid": True}
```

Both functions will automatically have the tags: `["network", "infrastructure", "public", "get_network_topology"]` and `["network", "infrastructure", "public", "validate_network_config"]` respectively.

### Function-Level Tags

Use the `@tags` decorator to apply specific tags to individual functions:

```python
# device_tools.py
from fastmcp import Context
from itential_mcp.toolutils import tags

async def get_device_info(ctx: Context, device_name: str) -> dict:
    """Get basic device information."""
    return {"device": device_name, "status": "online"}

@tags("experimental", "beta")
async def experimental_device_feature(ctx: Context) -> dict:
    """An experimental device feature."""
    return {"feature": "experimental"}

@tags("admin", "dangerous")
async def reset_device(ctx: Context, device_name: str) -> dict:
    """Reset a device (dangerous operation)."""
    return {"device": device_name, "action": "reset"}
```

### Combining Module and Function Tags

You can combine both approaches. Function-level tags are added to module-level tags:

```python
# combined_tools.py
from fastmcp import Context
from itential_mcp.toolutils import tags

# Module-level tags applied to all functions
__tags__ = ["utility", "shared"]

@tags("public")
async def public_utility(ctx: Context) -> dict:
    """A public utility function."""
    # Tags: ["utility", "shared", "public", "public_utility"]
    return {"type": "public"}

@tags("admin", "internal")
async def admin_utility(ctx: Context) -> dict:
    """An admin-only utility function."""
    # Tags: ["utility", "shared", "admin", "internal", "admin_utility"]
    return {"type": "admin"}
```

## Loading Custom Tools

### Using the --tools-path Argument

Load custom tools using the `--tools-path` command-line argument:

```bash
# Load tools from a custom directory
itential-mcp --tools-path /path/to/my-custom-tools

# Use with other options
itential-mcp --tools-path /path/to/my-custom-tools --include-tags "public,network"
```

### Using Environment Variables

Set the tools path via environment variable:

```bash
export ITENTIAL_MCP_SERVER_TOOLS_PATH=/path/to/my-custom-tools
itential-mcp
```

### Using Configuration Files

Add to your configuration file:

```ini
[server]
tools_path = /path/to/my-custom-tools
include_tags = public,network
exclude_tags = experimental,dangerous
```

### Tool Discovery Process

The server loads tools from multiple locations:

1. **Default tools directory**: `src/itential_mcp/tools/` (built-in tools)
2. **Custom tools directory**: Specified via `--tools-path` (your custom tools)

Both directories are scanned, and all discovered tools are registered with the server.  If a custom tool has the same name as a default function, the server will issue a warning and not load the custom tool.

## Examples

### Example 1: Simple Network Tool with Pydantic Schema

```python
# my-tools/network.py
from fastmcp import Context
from pydantic import BaseModel, Field
from typing import Optional
import subprocess
import re

__tags__ = ["network", "public"]

class PingResult(BaseModel):
    """Result of a network ping operation."""
    hostname: str = Field(description="The hostname or IP address that was pinged")
    success: bool = Field(description="Whether the ping operation was successful")
    packets_sent: int = Field(description="Number of packets sent")
    packets_received: int = Field(description="Number of packets received")
    packet_loss_percent: float = Field(description="Percentage of packet loss (0-100)")
    min_time: Optional[float] = Field(None, description="Minimum response time in milliseconds")
    avg_time: Optional[float] = Field(None, description="Average response time in milliseconds")
    max_time: Optional[float] = Field(None, description="Maximum response time in milliseconds")
    raw_output: str = Field(description="Raw ping command output")
    error_message: Optional[str] = Field(None, description="Error message if ping failed")

async def ping_host(ctx: Context, hostname: str, count: int = 4) -> PingResult:
    """
    Ping a host and return structured results with automatic schema generation.

    Args:
        ctx: FastMCP context
        hostname: Hostname or IP address to ping
        count: Number of ping packets to send

    Returns:
        PingResult: Structured ping results with comprehensive timing data
    """
    try:
        result = subprocess.run(
            ["ping", "-c", str(count), hostname],
            capture_output=True,
            text=True,
            timeout=30
        )

        if result.returncode == 0:
            # Parse successful ping output
            stats = _parse_ping_statistics(result.stdout)
            return PingResult(
                hostname=hostname,
                success=True,
                packets_sent=count,
                packets_received=stats.get("received", 0),
                packet_loss_percent=stats.get("packet_loss", 0.0),
                min_time=stats.get("min_time"),
                avg_time=stats.get("avg_time"),
                max_time=stats.get("max_time"),
                raw_output=result.stdout,
                error_message=None
            )
        else:
            # Parse failed ping output
            packet_loss = 100.0  # Assume 100% loss on failure
            return PingResult(
                hostname=hostname,
                success=False,
                packets_sent=count,
                packets_received=0,
                packet_loss_percent=packet_loss,
                min_time=None,
                avg_time=None,
                max_time=None,
                raw_output=result.stdout,
                error_message=result.stderr or "Ping failed"
            )

    except subprocess.TimeoutExpired:
        return PingResult(
            hostname=hostname,
            success=False,
            packets_sent=count,
            packets_received=0,
            packet_loss_percent=100.0,
            min_time=None,
            avg_time=None,
            max_time=None,
            raw_output="",
            error_message="Ping operation timed out"
        )

def _parse_ping_statistics(output: str) -> dict:
    """Parse ping output to extract timing statistics."""
    stats = {"received": 0, "packet_loss": 100.0}

    # Parse packet statistics
    packet_match = re.search(r'(\d+) packets transmitted, (\d+) received, (\d+(?:\.\d+)?)% packet loss', output)
    if packet_match:
        stats["received"] = int(packet_match.group(2))
        stats["packet_loss"] = float(packet_match.group(3))

    # Parse timing statistics (min/avg/max)
    time_match = re.search(r'min/avg/max/mdev = ([\d.]+)/([\d.]+)/([\d.]+)/([\d.]+) ms', output)
    if time_match:
        stats["min_time"] = float(time_match.group(1))
        stats["avg_time"] = float(time_match.group(2))
        stats["max_time"] = float(time_match.group(3))

    return stats
```

### Example 2: Itential Platform Integration Tool with Structured Output

```python
# my-tools/platform.py
from fastmcp import Context
from itential_mcp.toolutils import tags
from pydantic import BaseModel, Field
from typing import Optional, List
from enum import Enum

__tags__ = ["platform", "integration"]

class WorkflowCategory(str, Enum):
    """Categories for workflow classification."""
    BACKUP_RESTORE = "backup_restore"
    DEPLOYMENT = "deployment"
    MONITORING = "monitoring"
    CONFIGURATION = "configuration"
    GENERAL = "general"

class RuntimeEstimate(str, Enum):
    """Estimated runtime categories."""
    SHORT = "short"      # < 5 minutes
    MEDIUM = "medium"    # 5-15 minutes
    LONG = "long"        # > 15 minutes

class EnhancedWorkflow(BaseModel):
    """Enhanced workflow information with custom metadata."""
    id: str = Field(description="Unique workflow identifier")
    name: str = Field(description="Workflow name")
    description: Optional[str] = Field(None, description="Workflow description")
    project: Optional[str] = Field(None, description="Project the workflow belongs to")
    status: str = Field(description="Current workflow status")
    task_count: int = Field(description="Number of tasks in the workflow")
    custom_category: WorkflowCategory = Field(description="Automatically assigned category")
    estimated_runtime: RuntimeEstimate = Field(description="Estimated execution time category")
    complexity_score: int = Field(ge=1, le=10, description="Complexity score from 1-10")
    created_date: Optional[str] = Field(None, description="When the workflow was created")
    last_executed: Optional[str] = Field(None, description="Last execution timestamp")

class WorkflowCollection(BaseModel):
    """Collection of enhanced workflows with metadata."""
    workflows: List[EnhancedWorkflow] = Field(description="List of enhanced workflow objects")
    total_count: int = Field(description="Total number of workflows returned")
    project_filter: Optional[str] = Field(None, description="Project filter that was applied")
    categories: dict = Field(description="Count of workflows by category")
    runtime_distribution: dict = Field(description="Count of workflows by estimated runtime")

async def get_custom_workflows(ctx: Context, project: str = None) -> WorkflowCollection:
    """
    Get workflows with enhanced metadata and structured output schema.

    Args:
        ctx: FastMCP context
        project: Optional project name to filter workflows

    Returns:
        WorkflowCollection: Comprehensive workflow collection with metadata
    """
    # Access the platform client
    client = ctx.request_context.lifespan_context.get("client")

    # Get workflows from platform
    response = await client.get("/api/v2.0/automations")
    workflows_data = response.json()

    # Process and enhance workflows
    enhanced_workflows = []
    category_counts = {}
    runtime_counts = {}

    for workflow_data in workflows_data:
        # Skip if project filter doesn't match
        if project and workflow_data.get("project") != project:
            continue

        # Enhance workflow with custom metadata
        category = _categorize_workflow(workflow_data.get("name", ""))
        runtime = _estimate_runtime(workflow_data)
        complexity = _calculate_complexity(workflow_data)

        enhanced = EnhancedWorkflow(
            id=workflow_data.get("id", ""),
            name=workflow_data.get("name", ""),
            description=workflow_data.get("description"),
            project=workflow_data.get("project"),
            status=workflow_data.get("status", "unknown"),
            task_count=len(workflow_data.get("tasks", [])),
            custom_category=category,
            estimated_runtime=runtime,
            complexity_score=complexity,
            created_date=workflow_data.get("created"),
            last_executed=workflow_data.get("lastExecuted")
        )

        enhanced_workflows.append(enhanced)

        # Update counts for summary statistics
        category_counts[category.value] = category_counts.get(category.value, 0) + 1
        runtime_counts[runtime.value] = runtime_counts.get(runtime.value, 0) + 1

    return WorkflowCollection(
        workflows=enhanced_workflows,
        total_count=len(enhanced_workflows),
        project_filter=project,
        categories=category_counts,
        runtime_distribution=runtime_counts
    )

def _categorize_workflow(name: str) -> WorkflowCategory:
    """Categorize workflow based on name patterns."""
    name_lower = name.lower()
    if "backup" in name_lower or "restore" in name_lower:
        return WorkflowCategory.BACKUP_RESTORE
    elif "deploy" in name_lower:
        return WorkflowCategory.DEPLOYMENT
    elif "monitor" in name_lower:
        return WorkflowCategory.MONITORING
    elif "config" in name_lower:
        return WorkflowCategory.CONFIGURATION
    else:
        return WorkflowCategory.GENERAL

def _estimate_runtime(workflow: dict) -> RuntimeEstimate:
    """Estimate workflow runtime based on task count."""
    task_count = len(workflow.get("tasks", []))
    if task_count < 5:
        return RuntimeEstimate.SHORT
    elif task_count < 15:
        return RuntimeEstimate.MEDIUM
    else:
        return RuntimeEstimate.LONG

def _calculate_complexity(workflow: dict) -> int:
    """Calculate complexity score (1-10) based on task count and structure."""
    tasks = workflow.get("tasks", [])
    base_complexity = min(len(tasks) // 2 + 1, 8)

    # Add complexity for nested structures or complex task types
    complex_task_count = 0
    for task in tasks:
        if task.get("type") in ["loop", "conditional", "parallel"]:
            complex_task_count += 1

    # Adjust complexity based on special task types
    final_complexity = min(base_complexity + complex_task_count, 10)
    return max(final_complexity, 1)  # Ensure minimum complexity of 1

class BulkOperationResult(BaseModel):
    """Result of a single workflow operation."""
    workflow_name: str = Field(description="Name of the workflow that was operated on")
    success: bool = Field(description="Whether the operation succeeded")
    response_data: Optional[dict] = Field(None, description="Response data if successful")
    error_message: Optional[str] = Field(None, description="Error message if failed")
    operation_type: str = Field(description="Type of operation performed")

class BulkOperationSummary(BaseModel):
    """Summary of bulk workflow operations."""
    operation_type: str = Field(description="Type of operation performed (start, stop, delete)")
    total_workflows: int = Field(description="Total number of workflows processed")
    successful_operations: int = Field(description="Number of successful operations")
    failed_operations: int = Field(description="Number of failed operations")
    success_rate: float = Field(ge=0, le=100, description="Success rate as percentage")
    results: List[BulkOperationResult] = Field(description="Detailed results for each workflow")

@tags("admin", "dangerous")
async def bulk_workflow_operation(ctx: Context, operation: str, workflow_names: List[str]) -> BulkOperationSummary:
    """
    Perform bulk operations on multiple workflows with structured results.

    Args:
        ctx: FastMCP context
        operation: Operation to perform (start, stop, delete)
        workflow_names: List of workflow names to operate on

    Returns:
        BulkOperationSummary: Comprehensive results with success metrics
    """
    if operation not in ["start", "stop", "delete"]:
        # Return early with error for invalid operation
        error_results = [
            BulkOperationResult(
                workflow_name=name,
                success=False,
                response_data=None,
                error_message=f"Invalid operation: {operation}",
                operation_type=operation
            )
            for name in workflow_names
        ]

        return BulkOperationSummary(
            operation_type=operation,
            total_workflows=len(workflow_names),
            successful_operations=0,
            failed_operations=len(workflow_names),
            success_rate=0.0,
            results=error_results
        )

    client = ctx.request_context.lifespan_context.get("client")
    results = []

    for workflow_name in workflow_names:
        try:
            if operation == "start":
                response = await client.post(f"/api/v2.0/automations/{workflow_name}/trigger")
            elif operation == "stop":
                response = await client.post(f"/api/v2.0/automations/{workflow_name}/stop")
            elif operation == "delete":
                response = await client.delete(f"/api/v2.0/automations/{workflow_name}")

            results.append(BulkOperationResult(
                workflow_name=workflow_name,
                success=True,
                response_data=response.json(),
                error_message=None,
                operation_type=operation
            ))
        except Exception as e:
            results.append(BulkOperationResult(
                workflow_name=workflow_name,
                success=False,
                response_data=None,
                error_message=str(e),
                operation_type=operation
            ))

    successful_count = len([r for r in results if r.success])
    success_rate = (successful_count / len(results) * 100) if results else 0.0

    return BulkOperationSummary(
        operation_type=operation,
        total_workflows=len(workflow_names),
        successful_operations=successful_count,
        failed_operations=len(results) - successful_count,
        success_rate=success_rate,
        results=results
    )
```

### Example 3: Tagged Tool Organization

```python
# my-tools/organized.py
from fastmcp import Context
from itential_mcp.toolutils import tags

# All functions get these base tags
__tags__ = ["custom", "utility"]

async def basic_function(ctx: Context) -> dict:
    """Basic function with only module tags."""
    # Tags: ["custom", "utility", "basic_function"]
    return {"level": "basic"}

@tags("public")
async def public_function(ctx: Context) -> dict:
    """Public function accessible to all users."""
    # Tags: ["custom", "utility", "public", "public_function"]
    return {"level": "public"}

@tags("admin", "sensitive")
async def admin_function(ctx: Context) -> dict:
    """Admin function for sensitive operations."""
    # Tags: ["custom", "utility", "admin", "sensitive", "admin_function"]
    return {"level": "admin"}

@tags("experimental", "beta", "testing")
async def experimental_function(ctx: Context) -> dict:
    """Experimental function under development."""
    # Tags: ["custom", "utility", "experimental", "beta", "testing", "experimental_function"]
    return {"level": "experimental"}
```

## Best Practices

### 1. Tool Organization

- **Group related tools** in the same module
- **Use descriptive module names** that indicate the tool's purpose
- **Keep tools focused** on a single responsibility
- **Document all functions** with proper docstrings

### 2. Tag Strategy

- **Use consistent tag naming** across your tools
- **Apply module tags** for broad categorization
- **Use function tags** for specific access control
- **Consider tag hierarchies**: `public` → `internal` → `admin` → `dangerous`

### 3. Error Handling

```python
async def robust_tool(ctx: Context, param: str) -> dict:
    """Tool with proper error handling."""
    try:
        # Tool logic here
        client = ctx.request_context.lifespan_context.get("client")
        result = await client.get(f"/api/endpoint/{param}")

        return {
            "success": True,
            "data": result.json()
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "error_type": type(e).__name__
        }
```

### 4. Using Pydantic Models for Output Schemas

**Strongly recommended: Use Pydantic models for return types** to enable automatic schema generation:

```python
from typing import Optional, List
from enum import Enum
from pydantic import BaseModel, Field

class DeviceStatus(str, Enum):
    """Device operational status."""
    ONLINE = "online"
    OFFLINE = "offline"
    MAINTENANCE = "maintenance"

class DeviceInfo(BaseModel):
    """Comprehensive device information."""
    name: str = Field(description="Device hostname or identifier")
    ip_address: str = Field(description="Primary IP address")
    device_type: str = Field(description="Type of network device")
    status: DeviceStatus = Field(description="Current operational status")
    last_seen: Optional[str] = Field(None, description="Last contact timestamp")
    uptime_seconds: Optional[int] = Field(None, ge=0, description="Device uptime in seconds")

    class Config:
        """Pydantic configuration."""
        use_enum_values = True

async def get_device_info(
    ctx: Context,
    device_name: str,
    include_metrics: bool = False
) -> DeviceInfo:
    """Get comprehensive device information with automatic schema generation."""
    client = ctx.request_context.lifespan_context.get("client")

    # Get device data from platform
    response = await client.get(f"/api/devices/{device_name}")
    device_data = response.json()

    return DeviceInfo(
        name=device_data["name"],
        ip_address=device_data["ipAddress"],
        device_type=device_data["type"],
        status=DeviceStatus(device_data["status"]),
        last_seen=device_data.get("lastSeen"),
        uptime_seconds=device_data.get("uptime")
    )
```

**Benefits of using Pydantic models:**
- **Automatic schema generation**: AI agents understand your tool's output structure
- **Automatic validation**: Input/output data is validated at runtime
- **Rich IDE support**: Better autocomplete and type checking
- **Self-documenting**: Field descriptions become part of the schema
- **Consistent API**: Standardized structure for all tool outputs

**Note**: While not required, using Pydantic models is strongly recommended for better AI agent integration. Tools that return basic Python types (dict, list, str) will still work but won't provide structured schema information to agents.

### 5. Testing Custom Tools

Create comprehensive tests for your custom tools, including Pydantic model validation:

```python
# test_my_tools.py
import pytest
from unittest.mock import MagicMock, AsyncMock, patch
from my_tools.network import ping_host, PingResult
from my_tools.platform import get_custom_workflows, WorkflowCollection

@pytest.mark.asyncio
async def test_ping_host_success():
    """Test successful ping with Pydantic model validation."""
    mock_ctx = MagicMock()

    # Mock subprocess.run to simulate successful ping
    with patch('subprocess.run') as mock_run:
        mock_run.return_value.returncode = 0
        mock_run.return_value.stdout = """
PING google.com (142.250.80.14): 56 data bytes
64 bytes from 142.250.80.14: icmp_seq=0 ttl=117 time=15.3 ms
64 bytes from 142.250.80.14: icmp_seq=1 ttl=117 time=14.8 ms
--- google.com ping statistics ---
2 packets transmitted, 2 received, 0% packet loss
round-trip min/avg/max/stddev = 14.8/15.05/15.3/0.25 ms
"""
        mock_run.return_value.stderr = ""

        # Test the tool
        result = await ping_host(mock_ctx, "google.com", 2)

        # Validate return type
        assert isinstance(result, PingResult)

        # Test Pydantic model fields
        assert result.hostname == "google.com"
        assert result.success is True
        assert result.packets_sent == 2
        assert result.packets_received == 2
        assert result.packet_loss_percent == 0.0
        assert result.avg_time == 15.05
        assert result.error_message is None

@pytest.mark.asyncio
async def test_ping_host_failure():
    """Test failed ping with proper error handling."""
    mock_ctx = MagicMock()

    with patch('subprocess.run') as mock_run:
        mock_run.return_value.returncode = 1
        mock_run.return_value.stdout = "ping: cannot resolve google.com: Unknown host"
        mock_run.return_value.stderr = "Name resolution failed"

        result = await ping_host(mock_ctx, "invalid-host", 2)

        assert isinstance(result, PingResult)
        assert result.success is False
        assert result.packet_loss_percent == 100.0
        assert result.error_message == "Name resolution failed"

@pytest.mark.asyncio
async def test_get_custom_workflows():
    """Test workflow collection with mock Itential Platform API."""
    mock_ctx = MagicMock()
    mock_client = MagicMock()
    mock_ctx.request_context.lifespan_context.get.return_value = mock_client

    # Mock API response
    mock_response = MagicMock()
    mock_response.json.return_value = [
        {
            "id": "wf1",
            "name": "Backup Network Config",
            "description": "Daily backup workflow",
            "project": "network-ops",
            "status": "complete",
            "tasks": [{"id": "task1", "name": "backup"}]
        },
        {
            "id": "wf2",
            "name": "Deploy New Service",
            "description": "Deploy service to production",
            "project": "deployments",
            "status": "running",
            "tasks": [
                {"id": "task1", "name": "validate"},
                {"id": "task2", "name": "deploy", "type": "parallel"}
            ]
        }
    ]
    mock_client.get.return_value = mock_response

    # Test the tool
    result = await get_custom_workflows(mock_ctx, project=None)

    # Validate return type
    assert isinstance(result, WorkflowCollection)

    # Test collection properties
    assert result.total_count == 2
    assert len(result.workflows) == 2
    assert result.project_filter is None

    # Test individual workflow properties
    backup_wf = result.workflows[0]
    assert backup_wf.custom_category.value == "backup_restore"
    assert backup_wf.estimated_runtime.value == "short"
    assert backup_wf.complexity_score >= 1

    deploy_wf = result.workflows[1]
    assert deploy_wf.custom_category.value == "deployment"
    assert deploy_wf.estimated_runtime.value == "short"

def test_pydantic_validation():
    """Test Pydantic model validation directly."""
    # Test valid data
    valid_ping = PingResult(
        hostname="test.com",
        success=True,
        packets_sent=4,
        packets_received=4,
        packet_loss_percent=0.0,
        raw_output="ping output",
        error_message=None
    )
    assert valid_ping.hostname == "test.com"

    # Test validation constraints
    with pytest.raises(ValueError):
        # packet_loss_percent should be 0-100
        PingResult(
            hostname="test.com",
            success=False,
            packets_sent=4,
            packets_received=0,
            packet_loss_percent=-5.0,  # Invalid negative value
            raw_output="",
            error_message="Failed"
        )
```

### 6. Server Configuration

Use environment variables or config files for deployment:

```bash
# Production environment
export ITENTIAL_MCP_SERVER_TOOLS_PATH=/opt/itential/custom-tools
export ITENTIAL_MCP_SERVER_INCLUDE_TAGS=public,production
export ITENTIAL_MCP_SERVER_EXCLUDE_TAGS=experimental,testing

itential-mcp --transport sse --host 0.0.0.0 --port 8000
```

## Summary

This comprehensive approach allows you to create powerful, well-organized custom tools that integrate seamlessly with the Itential MCP server while maintaining proper access control through the tagging system.

### Key Takeaways

1. **Use Pydantic Models**: Strongly recommended to return Pydantic models to enable automatic output schema generation for better AI agent integration
2. **Leverage Tagging**: Combine module-level (`__tags__`) and function-level (`@tags`) tagging for flexible tool organization
3. **Custom Tools Path**: Use the `--tools-path` argument to load your custom tools alongside built-in tools
4. **Structured Data**: Provide rich, structured data with detailed field descriptions for optimal agent understanding
5. **Comprehensive Testing**: Test both functionality and Pydantic model validation to ensure reliability

By following these patterns, your custom tools will be discoverable, well-documented, and provide maximum value to AI agents working with the Itential Platform.
