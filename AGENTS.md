# Itential MCP - Codebase Documentation

**Last Updated:** 2026-01-10
**Version:** 0.11.0+
**Python Requirements:** 3.10 - 3.13
**Code Base:** ~18,500 lines of Python
**Test Coverage:** 98%

## What This Project Does

Itential MCP is a production-grade Model Context Protocol (MCP) server that bridges AI agents (Claude, GPT, etc.) with the Itential Platform - a network automation and orchestration system. It exposes 56+ tools across 10 functional categories (health, device config, workflow execution, lifecycle management, etc.) allowing AI agents to manage network infrastructure, execute workflows, monitor systems, and perform advanced operations.

**Key Value Proposition:** Instead of AI agents being limited to text generation, this server gives them operational capabilities - they can configure devices, run compliance checks, execute workflows, manage resources, and monitor platform health through a standardized MCP interface.

## Project Structure

```
itential-mcp/
├── src/itential_mcp/           # Main source code (~18.5k lines)
│   ├── app.py                  # Application entry point
│   ├── __main__.py             # CLI entry (python -m itential_mcp)
│   ├── defaults.py             # Configuration defaults
│   │
│   ├── bindings/               # Dynamic tool binding system
│   │   ├── __init__.py         # Binding orchestration and iteration
│   │   ├── endpoint.py         # Workflow endpoint bindings
│   │   └── service.py          # Gateway service bindings
│   │
│   ├── cli/                    # Command-line interface
│   │   ├── parser.py           # Argument parsing
│   │   ├── terminal.py         # Terminal utilities and formatting
│   │   └── argument_groups.py  # CLI argument group definitions
│   │
│   ├── config/                 # Configuration system (modular package)
│   │   ├── __init__.py         # Public API and cached config loader
│   │   ├── models.py           # Pydantic dataclass models
│   │   ├── loaders.py          # Config file/env loading logic
│   │   ├── validators.py       # Validation functions
│   │   └── converters.py       # Type conversion utilities
│   │
│   ├── core/                   # Core utilities and shared logic
│   │   ├── env.py              # Environment variable helpers
│   │   ├── errors.py           # Legacy error helpers (consider deprecating)
│   │   ├── exceptions.py       # Exception hierarchy (comprehensive)
│   │   ├── logging.py          # Logging configuration
│   │   ├── metadata.py         # Version and package metadata
│   │   └── heuristics.py       # Type detection and inference
│   │
│   ├── middleware/             # FastMCP middleware components
│   │   ├── bindings.py         # Dynamic tool injection (O(1) lookup)
│   │   └── serialization.py    # Response serialization with toon support
│   │
│   ├── models/                 # Pydantic data models (18 files)
│   │   ├── adapters.py         # Adapter lifecycle models
│   │   ├── applications.py     # Application models
│   │   ├── command_templates.py# Network command templates
│   │   ├── devices.py          # Device configuration models
│   │   ├── health.py           # Health monitoring models
│   │   ├── integrations.py     # External integration models
│   │   ├── lifecycle_manager.py# Resource lifecycle models
│   │   ├── operations_manager.py # Workflow/job models
│   │   └── ...                 # (10+ additional model files)
│   │
│   ├── platform/               # Platform API client
│   │   ├── __init__.py         # Package exports
│   │   ├── client.py           # Main PlatformClient (HTTP wrapper)
│   │   ├── response.py         # Response wrapper
│   │   └── services/           # Service-specific API wrappers
│   │       ├── adapters.py     # Adapter service API
│   │       ├── configuration_manager.py  # Config management API
│   │       ├── health.py       # Health monitoring API
│   │       ├── operations_manager.py     # Workflow execution API
│   │       └── ...             # (10+ service files)
│   │
│   ├── runtime/                # Application runtime logic
│   │   ├── parser.py           # CLI command parsing
│   │   ├── handlers.py         # Command handler routing
│   │   ├── commands.py         # Command implementations
│   │   ├── runner.py           # Server runner
│   │   └── constants.py        # Runtime constants
│   │
│   ├── serializers/            # Response serialization (toon support)
│   │
│   ├── server/                 # MCP server implementation
│   │   ├── server.py           # Server class and lifespan management
│   │   ├── auth.py             # Authentication providers (JWT, OAuth)
│   │   ├── routes.py           # Health check endpoints (/status/*)
│   │   └── keepalive.py        # Session keepalive mechanism
│   │
│   ├── tools/                  # MCP tool implementations (18 files)
│   │   ├── health.py           # Platform health monitoring
│   │   ├── devices.py          # Device management
│   │   ├── operations_manager.py # Workflow execution
│   │   ├── lifecycle_manager.py  # Resource lifecycle
│   │   └── ...                 # (14+ additional tool files)
│   │
│   └── utilities/              # Shared utility functions
│       ├── json.py             # JSON handling
│       └── tool.py             # Tool discovery and introspection
│
├── tests/                      # Comprehensive test suite (69 files)
│   ├── test_*.py               # Unit tests mirror src/ structure
│   └── utilities/              # Test helpers and fixtures
│
├── docs/                       # User documentation
│   ├── integration.md          # MCP client integration guide
│   ├── oauth-authentication.md # OAuth setup
│   ├── jwt-authentication.md   # JWT authentication
│   ├── tls.md                  # TLS configuration
│   ├── tools.md                # Tool reference
│   ├── tags.md                 # Tagging system
│   └── ...                     # (12+ documentation files)
│
├── Makefile                    # Development commands
├── pyproject.toml              # Project metadata and dependencies
├── Containerfile               # Container image definition
└── CHANGELOG.md                # Version history
```

## Architecture Deep Dive

### 1. Server Initialization Flow

```
app.py:run()
  → runtime/parser.py:parse_args()
  → runtime/handlers.py:get_command_handler()
  → server/server.py:run()
    → Server.__init__(config)
    → Server.__init_server__()    # Create FastMCP instance
    → Server.__init_tools__()     # Discover and register tools
    → Server.__init_bindings__()  # Register dynamic tool bindings
    → Server.__init_routes__()    # Register health endpoints
    → Server.run()                # Start transport (stdio/SSE/HTTP)
```

**Lifespan Management:**
- `lifespan()` async context manager creates PlatformClient instance
- Client is injected into FastMCP context for all tool requests
- Keepalive task prevents session timeouts (configurable interval)
- Proper cleanup on shutdown (cancel keepalive, close connections)

### 2. Platform Client Architecture

**src/itential_mcp/platform/client.py:PlatformClient**

Key Design Decisions:
- Wraps `ipsdk.AsyncPlatform` for Itential API communication
- Dynamic service plugin loading from `platform/services/` directory
- Each service is a class with `name` attribute (e.g., "health", "adapters")
- Services are registered as PlatformClient attributes (e.g., `client.health`)
- Async context manager for proper resource cleanup
- Timeout protection on all HTTP requests (default 30s, configurable)

**Service Plugin Pattern:**
```python
# platform/services/health.py
class Service:
    name = "health"

    def __init__(self, client):
        self.client = client

    async def get_status_health(self):
        return await self.client.get("/health")
```

Services are auto-discovered and loaded at client initialization. This pattern allows easy extension without modifying core client code.

### 3. Configuration System (Recently Refactored - v0.11.0)

**src/itential_mcp/config/** - Modular package with clean separation:

**Design Philosophy:**
- Immutable dataclasses (Pydantic) for type safety
- Clear separation: models, loaders, validators, converters
- Support for multiple config sources with precedence
- Environment variables, CLI args, config files, defaults

**Precedence Order (highest to lowest):**
1. Environment variables (`ITENTIAL_MCP_SERVER_*`, `ITENTIAL_MCP_PLATFORM_*`)
2. Command-line arguments
3. Configuration file (--config)
4. Default values (defaults.py)

**Key Models:**
- `Config` - Root config with nested sections
- `ServerConfig` - Transport, host, port, logging, tool filtering
- `PlatformConfig` - Platform connection settings (host, auth, TLS)
- `AuthConfig` - Authentication configuration (JWT, OAuth)
- `Tool`, `EndpointTool`, `ServiceTool` - Dynamic tool definitions

**Cached Loading:**
```python
from itential_mcp import config

cfg = config.get()  # Loads once, cached with @lru_cache
cfg.server.transport  # Access nested attributes
cfg.platform.host
cfg.auth.type
```

### 4. Tool System

**Static Tools (src/itential_mcp/tools/)**

Each tool file exports async functions with:
- `Context` parameter (FastMCP injection)
- `__tags__` module attribute for filtering
- Pydantic models for return types (type-safe responses)
- Comprehensive docstrings (Args, Returns, Raises)

**Tool Discovery:**
```python
# utilities/tool.py:itertools()
for tool_file in tools_directory.glob("*.py"):
    module = import_module(tool_file)
    for func in get_async_functions(module):
        yield func, get_tags(module)
```

Tools are automatically registered with FastMCP on server startup.

**Dynamic Tool Bindings (src/itential_mcp/bindings/)**

Powerful feature that creates MCP tools from:
1. **Workflow Endpoints** - Expose Itential workflows as callable tools
2. **Gateway Services** - Wrap external services (Ansible, Terraform, Python scripts)

Configuration via environment variables:
```bash
ITENTIAL_MCP_TOOL_MY_WORKFLOW='{"type":"endpoint","name":"trigger_name","automation":"workflow_name"}'
ITENTIAL_MCP_TOOL_RUN_ANSIBLE='{"type":"service","name":"ansible_service","cluster":"default"}'
```

**Binding Flow:**
```
bindings/__init__.py:iterbindings()
  → For each tool in config.tools:
    → bind_to_tool(tool, platform_client)
      → Import binding module (endpoint.py or service.py)
      → Call module.new(tool, client)
      → Return (bound_function, registration_kwargs)
  → FastMCP registers bound_function as MCP tool
```

This enables users to expose custom workflows without writing Python code.

### 5. Middleware Stack

FastMCP middleware (order matters - first added is outermost):

1. **ErrorHandlingMiddleware** - Catch and format exceptions
2. **DetailedTimingMiddleware** - Performance metrics per tool call
3. **LoggingMiddleware** - Request/response logging with payload truncation
4. **BindingsMiddleware** - O(1) tool name lookup (recent optimization)
5. **SerializationMiddleware** - Response serialization with toon support

**BindingsMiddleware Optimization:**
Previously O(n) - iterated all bindings on every request. Now O(1) - uses dict lookup by tool name. Significant performance improvement for deployments with many dynamic tools.

### 6. Authentication & Security

**Supported Auth Methods:**
- Basic Auth (username/password)
- OAuth 2.0 (multiple providers: Auth0, Okta, Azure AD, custom)
- JWT tokens (stateless, bearer token)
- No auth (development only)

**Transport Compatibility:**
- stdio: No auth (local process communication)
- SSE/HTTP: All auth methods supported

**Security Features:**
- TLS/HTTPS support with certificate configuration
- Certificate verification (disable only in dev)
- JWT token validation with issuer verification
- OAuth token introspection
- Sensitive data filtering in logs (passwords, tokens, secrets)
- Request timeout protection (prevents hung requests)
- Connection keepalive with session management

**Security Warnings:**
The logging system actively warns about insecure configurations:
- TLS disabled
- Certificate verification disabled
- Sensitive data in environment variables

### 7. Exception Hierarchy

**src/itential_mcp/core/exceptions.py** - Comprehensive and well-designed:

```
ItentialMcpException (base, http_status=500)
├── ClientException (4xx)
│   ├── ValidationException (400)
│   ├── AuthenticationException (401)
│   ├── AuthorizationException (403)
│   ├── NotFoundError (404)
│   ├── ConflictException (409)
│   │   ├── AlreadyExistsError
│   │   └── InvalidStateError
│   └── RateLimitException (429)
├── ServerException (5xx)
│   ├── ConfigurationException (500)
│   ├── ConnectionException (502)
│   ├── TimeoutExceededError (504)
│   └── ServiceUnavailableException (503)
└── BusinessLogicException (422)
    ├── WorkflowException
    ├── DeviceException
    └── ComplianceException
```

**Features:**
- HTTP status code mapping for REST API contexts
- Optional details dict for structured error info
- Utility functions: `get_exception_for_http_status()`, `create_exception_from_response()`
- Exception categories: `CLIENT_EXCEPTIONS`, `SERVER_EXCEPTIONS`, `BUSINESS_EXCEPTIONS`
- Type-safe exception checking: `is_client_error()`, `is_server_error()`

This is excellent design - proper exception hierarchy with HTTP semantics.

## What's Well Done

### Code Quality & Architecture

1. **Test Coverage** - 98% with comprehensive unit tests
   - 69 test files mirroring source structure
   - Extensive mocking and async testing
   - Edge case coverage (error paths, timeouts, validation)
   - Integration tests for CLI commands

2. **Type Safety** - Modern Python type hints throughout
   - `from __future__ import annotations` for forward references
   - Pydantic dataclasses for validation
   - Type hints on all function signatures
   - Proper use of `Literal`, `Annotated`, `TypedDict`

3. **Documentation** - Comprehensive Google-style docstrings
   - Args, Returns, Raises consistently documented
   - 12+ markdown docs for users (integration, auth, TLS, etc.)
   - Example prompts for Claude and GPT integration
   - Clear separation of user docs vs. developer docs

4. **Configuration System** - Recently refactored (v0.11.0)
   - Clean modular design (models, loaders, validators)
   - Immutable dataclasses prevent accidental mutations
   - Clear precedence rules (env > CLI > file > defaults)
   - Cached loading with `@lru_cache`

5. **Error Handling** - Proper exception hierarchy
   - HTTP status codes mapped to exception types
   - Structured error details (dict)
   - Category-based filtering
   - Clear error messages

6. **Security Awareness** - Production-ready security features
   - TLS/HTTPS support
   - Multiple auth methods (OAuth, JWT, Basic)
   - Sensitive data filtering in logs
   - Security warnings for misconfigurations
   - Timeout protection on all HTTP requests

7. **Performance Optimizations**
   - O(1) bindings middleware lookup (v0.11.0)
   - Parallel async API calls (`asyncio.gather`)
   - Connection pooling via ipsdk
   - Keepalive to prevent reconnections
   - Generator-based tool discovery

8. **Developer Experience**
   - Comprehensive Makefile with clear targets
   - Tox support for multi-version testing (3.10-3.13)
   - Pre-merge pipeline automation
   - Ruff for fast linting and formatting
   - Copyright header checking script

9. **Production Readiness**
   - Kubernetes health endpoints (/status/healthz, /readyz, /livez)
   - Container support (Dockerfile → Containerfile)
   - Multi-architecture builds (amd64, arm64)
   - Proper logging with levels
   - Graceful shutdown handling

10. **Code Organization**
    - Clear package boundaries
    - Single responsibility principle
    - Minimal coupling between modules
    - Consistent naming conventions
    - Logical grouping (core, platform, runtime, tools)

### Specific Highlights

**server/server.py:lifespan()** - Excellent async context manager pattern:
```python
@asynccontextmanager
async def lifespan(mcp: FastMCP) -> AsyncGenerator[dict[str | Any], None]:
    async with PlatformClient() as client_instance:
        keepalive_task = None
        try:
            if keepalive_interval > 0:
                keepalive_task = start_keepalive(client_instance, keepalive_interval)
            yield {"client": client_instance}
        finally:
            if keepalive_task and not keepalive_task.done():
                keepalive_task.cancel()
                try:
                    await keepalive_task
                except asyncio.CancelledError:
                    pass
```
This ensures proper resource cleanup even on errors.

**platform/client.py:_init_plugins()** - Robust service plugin loading:
- Graceful handling of import errors
- Validation of service name attributes
- Debug logging for troubleshooting
- Continues on single plugin failure (doesn't crash entire client)

**middleware/bindings.py** - O(1) optimization is excellent:
```python
# Old: O(n) - iterate all bindings
for binding in all_bindings:
    if binding.name == tool_name:
        return binding

# New: O(1) - dict lookup
return bindings_dict.get(tool_name)
```

## Technical Debt & Areas for Improvement

### Low Priority (Cosmetic/Nice-to-Have)

1. **core/errors.py** - Potential Deprecation Candidate
   - Simple dict-returning helper functions
   - Superseded by comprehensive exceptions.py
   - Only used in a few places
   - Consider migrating to exceptions and deprecating

2. **Inconsistent Return Types**
   - Some tools return dict, others return Pydantic models
   - Should standardize on Pydantic models for type safety
   - Current approach works but lacks consistency

3. **Test Warning Suppressions**
   - pyproject.toml suppresses some RuntimeWarnings
   - These are false positives from Mock objects in async contexts
   - Could be cleaner to fix at source rather than suppress

4. **Minor Code Comments**
   - One `XXX` comment in tools/gateway_manager.py about result filtering
   - Not blocking but indicates a known limitation
   - Consider addressing or documenting as intentional

### Medium Priority (Refactoring Opportunities)

1. **Service Plugin System** - Could Be More Explicit
   - Current: Auto-discover all .py files in services/
   - Services must have `Service` class with `name` attribute
   - Implicit contract - easy to break accidentally
   - **Improvement:** Consider explicit plugin registry or base class

2. **Tool Return Type Validation**
   - Tools with output_schema get validation
   - Tools without output_schema log warning but continue
   - **Improvement:** Consider requiring output_schema for all tools
   - Would improve MCP client experience (better type information)

3. **Response Object** - Thin Wrapper
   - platform/response.py wraps ipsdk.Response
   - Currently just delegates to underlying object
   - **Improvement:** Either add value (error handling, logging) or remove wrapper

4. **Configuration File Format**
   - Supports config files but format is loosely documented
   - mcp.conf.example exists but could be more prominent
   - **Improvement:** Schema validation for config files, better errors

5. **Binding Description Generation**
   - Bindings auto-generate descriptions from platform metadata
   - Could be more sophisticated (include parameter info, examples)
   - **Improvement:** Rich descriptions with schema introspection

### High Priority (Consider Addressing Soon)

1. **Error Recovery** - No Retry Logic
   - HTTP requests have timeout but no retry mechanism
   - Transient network errors cause immediate failure
   - **Improvement:** Add configurable retry with exponential backoff
   - Especially important for platform health monitoring

2. **Connection Pooling** - Delegated to ipsdk
   - PlatformClient relies on ipsdk's connection handling
   - No visibility into pool size, connection limits
   - **Improvement:** Expose connection pool configuration
   - Add metrics for connection pool health

3. **Logging Configuration** - Limited Flexibility
   - Log level is global (INFO, DEBUG, ERROR, etc.)
   - Can't configure per-module logging
   - No support for structured logging (JSON)
   - **Improvement:** Per-module log levels, structured output option
   - Would help in production debugging

4. **Tool Filtering** - Tag-Based Only
   - Include/exclude by tags works well
   - Can't filter by individual tool name
   - Can't filter by other criteria (e.g., risk level)
   - **Improvement:** More granular filtering options
   - Consider allow/deny lists for specific tools

5. **Platform Client Singleton** - Shared Connection
   - Single PlatformClient instance for all requests
   - No connection pooling for concurrent requests
   - Could be a bottleneck under high load
   - **Improvement:** Connection pool or per-request clients
   - Load testing would reveal if this is an issue

## Patterns & Conventions

### Python Style

**Follows Python best practices consistently:**

1. **Type Hints** - Modern annotation style
   ```python
   # Good - modern style
   def func(data: dict[str, Any]) -> list[str]:
       ...

   # Avoid - old style
   from typing import Dict, List
   def func(data: Dict[str, Any]) -> List[str]:
       ...
   ```

2. **String Formatting** - F-strings everywhere
   ```python
   # Used consistently
   f"Error: {error_msg} (code: {status_code})"

   # Not used: .format() or % formatting
   ```

3. **Async/Await** - Proper async patterns
   - Async context managers (`async with`)
   - Parallel execution with `asyncio.gather()`
   - Timeout protection with `asyncio.wait_for()`
   - Proper cancellation handling

4. **Error Handling** - EAFP (Easier to Ask Forgiveness than Permission)
   ```python
   # Used: Try and handle exceptions
   try:
       result = await client.get("/path")
   except ConnectionException:
       # Handle error

   # Not used: Check before access
   if client.is_connected():
       result = await client.get("/path")
   ```

5. **Context Managers** - Resource cleanup
   - PlatformClient as async context manager
   - Proper cleanup in finally blocks
   - No resource leaks

6. **Immutability** - Where appropriate
   - Pydantic dataclasses with `frozen=True`
   - Config objects are immutable
   - Prevents accidental state mutations

### Code Organization Patterns

1. **Package Structure** - Clear boundaries
   ```
   core/        - Fundamental utilities (logging, exceptions, env)
   platform/    - API client and service wrappers
   runtime/     - Application lifecycle (CLI, commands, runner)
   server/      - MCP server implementation
   tools/       - MCP tool implementations
   models/      - Data models (Pydantic)
   bindings/    - Dynamic tool bindings
   middleware/  - FastMCP middleware
   config/      - Configuration system
   utilities/   - Shared helpers
   ```

2. **Module Organization** - Consistent ordering
   ```python
   # 1. Copyright header
   # 2. Module docstring
   # 3. Imports (stdlib, third-party, local)
   # 4. Constants
   # 5. Private functions (_func)
   # 6. Public functions
   # 7. Classes
   ```

3. **Import Style**
   ```python
   # Standard library
   import asyncio
   import pathlib

   # Third-party
   from fastmcp import Context
   from pydantic import Field

   # Local (relative imports within package)
   from .. import config
   from ..core import logging
   ```

4. **Naming Conventions**
   - Modules: lowercase_with_underscores
   - Classes: PascalCase
   - Functions: lowercase_with_underscores
   - Constants: UPPERCASE_WITH_UNDERSCORES
   - Private: _leading_underscore
   - Dunder: __double_leading__ (for class internals)

### Testing Patterns

1. **Test Organization** - Mirrors source structure
   ```
   src/itential_mcp/platform/client.py
   tests/test_client.py
   ```

2. **Test Naming** - Descriptive and consistent
   ```python
   def test_function_name_when_condition_then_expected_result():
       ...

   # Examples:
   def test_get_health_when_platform_available_returns_health_data():
   def test_bind_to_tool_when_invalid_type_raises_import_error():
   ```

3. **Test Structure** - AAA (Arrange, Act, Assert)
   ```python
   async def test_example():
       # Arrange
       mock_client = Mock()
       mock_response = Mock(json=lambda: {"status": "ok"})
       mock_client.get.return_value = mock_response

       # Act
       result = await get_health(mock_client)

       # Assert
       assert result.status == "ok"
       mock_client.get.assert_called_once()
   ```

4. **Mocking Strategy**
   - Mock external dependencies (HTTP calls, file I/O)
   - Don't mock the code under test
   - Use `AsyncMock` for async functions
   - Verify mock calls with assertions

5. **Fixture Usage**
   - Minimal fixtures (only when needed)
   - Prefer explicit setup in tests for clarity
   - Use fixtures for complex shared setup

### Documentation Patterns

1. **Docstrings** - Google style, comprehensive
   ```python
   def function(arg1: str, arg2: int | None = None) -> dict:
       """Short description on first line.

       Longer description with more details about what the function
       does, how it works, and any important notes.

       Args:
           arg1: Description of arg1.
           arg2: Description of arg2. Defaults to None.

       Returns:
           dict: Description of return value with structure details.

       Raises:
           ValueError: When input validation fails.
           ConnectionException: When API communication fails.
       """
   ```

2. **Module Docstrings** - Purpose and contents
   ```python
   """Module description.

   Detailed explanation of what this module provides and how it
   fits into the overall architecture.
   """
   ```

3. **Inline Comments** - Explain "why" not "what"
   ```python
   # Good: Explains reasoning
   # Use timeout to prevent hung requests blocking the server
   result = await asyncio.wait_for(request, timeout=30)

   # Avoid: Restates code
   # Call asyncio.wait_for with timeout parameter
   result = await asyncio.wait_for(request, timeout=30)
   ```

### Configuration Patterns

1. **Environment Variables** - Consistent naming
   ```bash
   ITENTIAL_MCP_SERVER_*    # Server configuration
   ITENTIAL_MCP_PLATFORM_*  # Platform connection
   ITENTIAL_MCP_TOOL_*      # Dynamic tool definitions
   ```

2. **Defaults** - Centralized in defaults.py
   ```python
   # All defaults in one place
   ITENTIAL_MCP_SERVER_TRANSPORT = "stdio"
   ITENTIAL_MCP_SERVER_HOST = "127.0.0.1"
   ITENTIAL_MCP_SERVER_PORT = 8000
   ```

3. **Validation** - Separate validators module
   ```python
   # config/validators.py
   def validate_port(port: int) -> int:
       if not 1 <= port <= 65535:
           raise ValueError(f"Invalid port: {port}")
       return port
   ```

## Development Workflow

### Daily Development Commands

```bash
# Setup
make build              # Create venv, install dependencies

# Development cycle
make format             # Format code with ruff
make check              # Lint code
make test               # Run tests
make coverage           # Generate coverage report

# Before committing
make premerge           # Full pipeline: clean, format, check, test

# Security
make security           # Run bandit security scanner

# Headers
make check-headers      # Verify copyright headers
make fix-headers        # Add missing headers
```

### Testing Workflow

```bash
# Quick test run
PYTHONDONTWRITEBYTECODE=1 uv run pytest tests -v -s

# With coverage
PYTHONDONTWRITEBYTECODE=1 uv run pytest --cov=itential_mcp --cov-report=term --cov-report=html tests/

# Specific test file
PYTHONDONTWRITEBYTECODE=1 uv run pytest tests/test_client.py -v

# Specific test
PYTHONDONTWRITEBYTECODE=1 uv run pytest tests/test_client.py::test_function_name -v

# Multi-version testing
make tox                # Test against Python 3.10, 3.11, 3.12, 3.13
make tox-py310          # Test specific version
```

### Running the Server

```bash
# Development (stdio)
uv run itential-mcp run

# Development (SSE)
uv run itential-mcp run --transport sse --host 0.0.0.0 --port 8000

# With custom config
uv run itential-mcp run --config config.conf

# Debug logging
ITENTIAL_MCP_SERVER_LOG_LEVEL=DEBUG uv run itential-mcp run

# Container
make container
docker run -p 8000:8000 \
  -e ITENTIAL_MCP_SERVER_TRANSPORT=sse \
  -e ITENTIAL_MCP_PLATFORM_HOST=platform.example.com \
  itential-mcp:devel
```

## Adding New Features

### Adding a New Tool

1. **Create tool file** - `src/itential_mcp/tools/my_feature.py`

```python
from typing import Annotated
from pydantic import Field
from fastmcp import Context
from itential_mcp.models.my_feature import MyFeatureResponse

__tags__ = ("my_category",)

async def my_feature_tool(
    ctx: Annotated[Context, Field(description="The FastMCP Context object")],
    param1: Annotated[str, Field(description="Parameter description")],
) -> MyFeatureResponse:
    """Short description.

    Longer description with details about what this tool does,
    when to use it, and any important notes.

    Args:
        ctx: The FastMCP Context object.
        param1: Description of param1.

    Returns:
        MyFeatureResponse: Description of return value.

    Raises:
        ValidationException: When param1 is invalid.
        ConnectionException: When platform communication fails.
    """
    await ctx.info(f"Executing my_feature_tool with param1={param1}")

    client = ctx.request_context.lifespan_context.get("client")

    res = await client.get(f"/api/my-feature/{param1}")

    return MyFeatureResponse(**res.json())
```

2. **Create data model** - `src/itential_mcp/models/my_feature.py`

```python
from pydantic import BaseModel, Field

class MyFeatureResponse(BaseModel):
    """Response from my_feature tool.

    Attributes:
        status: Current status.
        data: Feature data.
    """
    status: str = Field(description="Current status")
    data: dict = Field(description="Feature data")
```

3. **Add service wrapper** (if needed) - `src/itential_mcp/platform/services/my_feature.py`

```python
class Service:
    name = "my_feature"

    def __init__(self, client):
        self.client = client

    async def get_feature(self, feature_id: str):
        """Get feature by ID.

        Args:
            feature_id: The feature identifier.

        Returns:
            dict: Feature data from platform.

        Raises:
            NotFoundError: When feature doesn't exist.
        """
        res = await self.client.get(f"/api/my-feature/{feature_id}")
        return res.json()
```

4. **Write tests** - `tests/test_tools_my_feature.py`

```python
import pytest
from unittest.mock import Mock, AsyncMock
from itential_mcp.tools.my_feature import my_feature_tool

@pytest.mark.asyncio
async def test_my_feature_tool_returns_expected_data():
    # Arrange
    mock_ctx = Mock()
    mock_ctx.info = AsyncMock()
    mock_client = Mock()
    mock_response = Mock(json=lambda: {"status": "ok", "data": {}})
    mock_client.get = AsyncMock(return_value=mock_response)
    mock_ctx.request_context.lifespan_context.get = Mock(return_value=mock_client)

    # Act
    result = await my_feature_tool(mock_ctx, param1="test")

    # Assert
    assert result.status == "ok"
    mock_client.get.assert_called_once_with("/api/my-feature/test")
```

5. **Run premerge** - `make premerge`

The tool is automatically discovered and registered on server startup.

### Adding a New Service

Services are auto-discovered from `platform/services/`. Follow the pattern:

```python
# src/itential_mcp/platform/services/my_service.py

class Service:
    """My service description.

    Provides API wrappers for my service endpoints.
    """

    name = "my_service"  # Attribute name on PlatformClient

    def __init__(self, client):
        """Initialize service with platform client.

        Args:
            client: The AsyncPlatform client instance.
        """
        self.client = client

    async def get_resource(self, resource_id: str) -> dict:
        """Get resource by ID.

        Args:
            resource_id: Resource identifier.

        Returns:
            dict: Resource data.

        Raises:
            NotFoundError: When resource doesn't exist.
        """
        res = await self.client.get(f"/my-service/resources/{resource_id}")
        return res.json()
```

Service is automatically loaded and available as `client.my_service`.

### Adding a Dynamic Binding

Create environment variable or config file entry:

```bash
# Workflow endpoint binding
ITENTIAL_MCP_TOOL_DEPLOY_CONFIG='{"type":"endpoint","name":"deploy_trigger","automation":"Deploy Configuration","description":"Deploy configuration to devices"}'

# Gateway service binding
ITENTIAL_MCP_TOOL_RUN_ANSIBLE='{"type":"service","name":"ansible_playbook","cluster":"default","description":"Run Ansible playbook"}'
```

Or in config file:

```toml
[[tools]]
type = "endpoint"
name = "deploy_trigger"
tool_name = "deploy_config"
automation = "Deploy Configuration"
description = "Deploy configuration to devices"
tags = "network,deployment"

[[tools]]
type = "service"
name = "ansible_playbook"
tool_name = "run_ansible"
cluster = "default"
description = "Run Ansible playbook"
tags = "automation,ansible"
```

## Common Pitfalls & How to Avoid

1. **Forgetting `PYTHONDONTWRITEBYTECODE=1`**
   - Bytecode can cause stale import issues
   - Always set when running Python commands
   - Makefile targets do this automatically

2. **Not using async context managers**
   ```python
   # Good
   async with PlatformClient() as client:
       result = await client.get("/path")

   # Bad - connection leak
   client = PlatformClient()
   result = await client.get("/path")
   ```

3. **Missing tool return type annotation**
   ```python
   # Good - FastMCP generates proper schema
   async def my_tool(ctx: Context) -> MyModel:
       ...

   # Bad - No schema information for MCP clients
   async def my_tool(ctx: Context):
       ...
   ```

4. **Not handling exceptions in tools**
   ```python
   # Good - Let specific exceptions propagate
   async def my_tool(ctx: Context) -> dict:
       client = ctx.request_context.lifespan_context.get("client")
       res = await client.get("/path")  # May raise ConnectionException
       return res.json()

   # Bad - Swallow all exceptions
   async def my_tool(ctx: Context) -> dict:
       try:
           client = ctx.request_context.lifespan_context.get("client")
           res = await client.get("/path")
           return res.json()
       except Exception:
           return {}  # Error silently ignored
   ```

5. **Modifying config after load**
   ```python
   # Bad - Config is frozen (immutable)
   cfg = config.get()
   cfg.server.port = 9000  # Raises FrozenInstanceError

   # Good - Set before loading
   os.environ["ITENTIAL_MCP_SERVER_PORT"] = "9000"
   cfg = config.get()
   ```

## Performance Considerations

1. **Parallel API Calls** - Use `asyncio.gather()` when possible
   ```python
   # Sequential (slow)
   status = await client.health.get_status()
   system = await client.health.get_system()

   # Parallel (fast)
   status, system = await asyncio.gather(
       client.health.get_status(),
       client.health.get_system(),
   )
   ```

2. **Connection Reuse** - PlatformClient is shared across requests
   - Single client instance in lifespan context
   - Connection pooling handled by ipsdk
   - Keepalive prevents connection timeouts

3. **Tool Discovery** - Uses generators for efficiency
   ```python
   # Good - yields as it finds
   for tool, tags in itertools(path):
       yield tool, tags

   # Bad - loads all into memory first
   tools = list(find_all_tools(path))
   for tool in tools:
       yield tool
   ```

4. **Config Caching** - `@lru_cache` on config.get()
   - Config loaded once on first call
   - Subsequent calls return cached instance
   - Restart required for config changes

## Quick Reference

### Environment Variables

```bash
# Server
ITENTIAL_MCP_SERVER_TRANSPORT=stdio|sse|http
ITENTIAL_MCP_SERVER_HOST=0.0.0.0
ITENTIAL_MCP_SERVER_PORT=8000
ITENTIAL_MCP_SERVER_LOG_LEVEL=INFO|DEBUG|ERROR|NONE
ITENTIAL_MCP_SERVER_INCLUDE_TAGS=tag1,tag2
ITENTIAL_MCP_SERVER_EXCLUDE_TAGS=experimental,beta

# Platform
ITENTIAL_MCP_PLATFORM_HOST=platform.example.com
ITENTIAL_MCP_PLATFORM_PORT=3000
ITENTIAL_MCP_PLATFORM_USER=admin
ITENTIAL_MCP_PLATFORM_PASSWORD=secret
ITENTIAL_MCP_PLATFORM_DISABLE_TLS=false
ITENTIAL_MCP_PLATFORM_DISABLE_VERIFY=false
ITENTIAL_MCP_PLATFORM_TIMEOUT=30

# Auth (OAuth)
ITENTIAL_MCP_AUTH_TYPE=oauth
ITENTIAL_MCP_AUTH_ISSUER=https://auth.example.com
ITENTIAL_MCP_AUTH_AUDIENCE=https://api.example.com

# Dynamic Tools
ITENTIAL_MCP_TOOL_<NAME>='{"type":"endpoint","name":"...","automation":"..."}'
```

### Makefile Targets

```bash
make help       # Show all targets
make build      # Setup development environment
make test       # Run test suite
make coverage   # Generate coverage report
make check      # Lint code
make format     # Format code
make fix        # Auto-fix issues
make security   # Security scan
make premerge   # Full pipeline
make clean      # Remove artifacts
make container  # Build container
```

### CLI Commands

```bash
itential-mcp --help                 # Show help
itential-mcp run                    # Start server
itential-mcp version                # Show version
itential-mcp tools                  # List tools
itential-mcp tags                   # List tags
itential-mcp call <tool> [--params] # Call tool
```

### Key Files

```bash
src/itential_mcp/app.py              # Application entry point
src/itential_mcp/server/server.py    # MCP server implementation
src/itential_mcp/platform/client.py  # Platform API client
src/itential_mcp/config/__init__.py  # Configuration loader
src/itential_mcp/core/exceptions.py  # Exception hierarchy
pyproject.toml                       # Project metadata
Makefile                             # Development commands
CHANGELOG.md                         # Version history
```

## Getting Help

- **Documentation:** `docs/` directory
- **Issues:** GitHub Issues
- **Tests:** `tests/` directory mirrors source structure
- **Examples:** `docs/mcp.conf.example`, example prompts

## Summary

This is a **high-quality, production-ready codebase** with:
- Excellent test coverage (98%)
- Comprehensive documentation
- Modern Python practices
- Clean architecture
- Security awareness
- Performance optimizations

**Main strengths:**
- Well-organized package structure
- Type-safe with Pydantic
- Comprehensive exception handling
- Good separation of concerns
- Extensive user documentation

**Areas to watch:**
- No retry logic for transient failures
- Connection pooling delegated to ipsdk
- Limited logging configuration flexibility
- Service plugin system could be more explicit

**For immediate productivity:**
1. Read README.md for user perspective
2. Review `src/itential_mcp/tools/` for examples
3. Check `tests/` for usage patterns
4. Use `make premerge` before committing
5. Follow existing patterns for consistency
