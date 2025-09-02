# Itential MCP Development

Itential MCP is a Python (3.10 or later) server that provides a MCP server for
conneting Itential Plaform to AI agents.

## Development Commands

** ALWAYS SET PYTHONDONTWRITEBYTECODE=1 WHEN RUNNING PYTHON COMMANDS **

### Build and Setup
- `make build` - Build the local development environment using uv
- `uv sync` - Sync dependencies and create virtual environment

### Testing
- `make test` - Run the test suite using pytest
- `uv run pytest tests -v -s` - Run tests with verbose output
- `make coverage` - Generate test coverage report (outputs to htmlcov/)
- `uv run pytest --cov=itential_mcp --cov-report=term --cov-report=html tests/` - Run coverage directly

### Code Quality
- `make check` - Check code quality without making changes (runs ruff check)
- `make lint` - Run ruff linter on source and test code (alias for check)
- `make format` - Format code using ruff formatter
- `make fix` - Auto-fix code quality issues where possible
- `uv run ruff check src` - Lint source code only
- `uv run ruff check tests` - Lint test code only
- `uv run ruff format src tests` - Format source and test code
- `make premerge` - Run full premerge pipeline (clean, format, lint, test)

### Cleanup
- `make clean` - Remove build artifacts, test cache, and coverage files

### Container
- `make container` - Build container image with tag `itential-mcp:devel`

### Running the Server
- `itential-mcp` - Start MCP server with default settings (stdio transport)
- `itential-mcp --transport sse --host 0.0.0.0 --port 8000` - Start with SSE transport
- `uv run python -m itential_mcp` - Run from source

## Architecture Overview

### Core Components

**MCP Server (`src/itential_mcp/server.py`)**
- Uses FastMCP framework for Model Context Protocol implementation
- Automatically discovers and registers tools from the `tools/` directory
- Supports multiple transport methods: stdio, SSE, and streamable-http
- Lifespan management creates shared client and cache instances

**Platform Client (`src/itential_mcp/client.py`)**
- Wraps the `ipsdk` library for Itential Platform API communication
- Provides async HTTP methods (get, post, put, delete)
- Handles authentication and connection management
- Returns standardized Response objects

**Tool Discovery**
- Tools are automatically discovered from `src/itential_mcp/tools/`
- Each tool is a Python file with async functions that take a `Context` parameter
- Functions are registered with FastMCP using tags for filtering
- Tools can be tagged with `__tags__` attribute or function decorators

**Configuration (`src/itential_mcp/config.py`)**
- Supports configuration via command line, environment variables, and config files
- Environment variables use `ITENTIAL_MCP_SERVER_` prefix
- Precedence: Environment > Command Line > Config File > Defaults

## Adding New Tools

1. Create a Python file in `src/itential_mcp/tools/`
2. Define async functions with `Context` parameter:
   ```python
   from fastmcp import Context

   async def my_tool(ctx: Context) -> dict:
       """Tool description"""
       client = ctx.request_context.lifespan_context.get("client")
       res = await client.get("/api/endpoint")
       return res.json()
   ```
3. Tools are auto-discovered on server startup
4. Use tags to control tool inclusion/exclusion

### Documentation Standards

- Always put verbose documentation for all methods and functions
- Docstrings should use google style documentation strings
- All docstrings must include Args:, Returns:, Raises:
- Raises must only document exceptions returned by the function or method


## Testing Strategy

- Unit tests in `tests/` directory mirror `src/` structure
- Uses pytest with asyncio support
- Coverage reports generated in `htmlcov/`
- All tests must pass before merging (`make premerge`)

## Dependencies

- **FastMCP**: Model Context Protocol framework
- **ipsdk**: Itential Platform SDK for API communication
- **pydantic**: Data validation and serialization
- **pytest**: Testing framework
- **ruff**: Code linting and formatting
