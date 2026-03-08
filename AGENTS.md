# Itential MCP — Codebase Reference

**Version:** 0.12.1 | **Python:** 3.10–3.13 | **Updated:** 2026-03-08

---

## Purpose & Architecture

Itential MCP is a production-grade Model Context Protocol (MCP) server that bridges AI agents with the Itential Platform — a network automation and orchestration system. It exposes 56+ tools across 10 functional categories (health, device config, workflow execution, lifecycle management, adapters, applications, compliance, projects, gateway, operations), allowing AI agents to configure devices, execute workflows, run compliance checks, and monitor platform health through a standardized MCP interface.

**Primary data flow:**

```
AI Agent → MCP Transport (stdio|sse|http)
  → Middleware Stack (error → timing → logging → bindings → serialization)
    → FastMCP tool dispatch
      → Tool function (tools/*.py)
        → PlatformClient (platform/client.py)
          → Service plugin (platform/services/*.py)
            → ipsdk.AsyncPlatform → Itential REST API
```

**Key modules and responsibilities:**

| Module | Responsibility |
|--------|----------------|
| `app.py` | Entry point, exit code handling, debug tracebacks |
| `server/server.py` | Server initialization, transport startup, lifespan management |
| `platform/client.py` | Wraps ipsdk, service plugin loading, timeout/TLS enforcement |
| `platform/services/` | Per-feature API wrappers auto-loaded as `client.<name>` |
| `config/` | Immutable config models, precedence resolution, cached loading |
| `tools/` | MCP tool implementations, auto-discovered at startup |
| `models/` | Pydantic return types for all tools |
| `bindings/` | Dynamic tool creation from config (endpoint and service types) |
| `middleware/` | FastMCP middleware stack (bindings injection, serialization) |
| `runtime/` | CLI argument parsing, command handlers, tool runner |
| `utilities/tool.py` | Tool discovery generator, tag system, schema extraction |
| `core/exceptions.py` | 19-class exception hierarchy with HTTP status mapping |

**Non-obvious design decisions:**

- **Lifespan context for client injection**: `PlatformClient` is created once in `server.py:lifespan()` and injected into FastMCP's lifespan context. Tools access it via `ctx.request_context.lifespan_context.get("client")`. This is a single shared instance across all requests — connection pooling is delegated to ipsdk.
- **Service plugins as client attributes**: `platform/services/*.py` modules are auto-discovered and registered as attributes on `PlatformClient` (e.g., `client.health`, `client.workflow_engine`). A single plugin failure does not crash initialization.
- **Dynamic bindings via environment**: Tools can be created at runtime without writing Python by setting `ITENTIAL_MCP_TOOL_<NAME>` env vars with JSON config. This enables exposing workflows as MCP tools without code changes.
- **Tag system for tool filtering**: Each tool module declares `__tags__` and individual functions can use `@tags()`. Tool name is always auto-tagged. `include_tags`/`exclude_tags` in server config controls what tools are exposed to clients.
- **Config immutability**: All config dataclasses use `frozen=True`. You cannot mutate config after load — set env vars before startup.
- **BindingsMiddleware uses O(1) dict lookup**: Previously iterated all bindings on every request. Now uses `tool_name → Tool config` dict. Critical for deployments with many dynamic tools.

---

## Tech Stack

**Language:** Python 3.10–3.13 (all versions tested via tox)

**Core dependencies and why:**

| Dependency | Role |
|------------|------|
| `fastmcp` | MCP server framework — handles protocol, tool registration, middleware, transports |
| `ipsdk>=0.7.0` | Itential Platform SDK — async HTTP client with auth and connection pooling |
| `pydantic` | Config models (frozen dataclasses), tool return types, validation |
| `uvicorn` | ASGI server for SSE and HTTP transports |
| `python-toon` | Alternative response serialization format (configured via `ITENTIAL_MCP_SERVER_RESPONSE_FORMAT=toon`) |
| `wsproto` | WebSocket protocol support |

**Build toolchain:**

| Tool | Role |
|------|------|
| `uv` | Package manager and venv management (replaces pip/venv) |
| `hatchling` + `uv-dynamic-versioning` | Build backend with git-tag-based semver |
| `ruff` | Linter and formatter (single tool, replaces flake8/black/isort) |
| `bandit` | Security scanner |
| `tox` + `tox-uv` | Multi-version test matrix |
| `pytest` + `pytest-asyncio` | Async-capable test framework |

**What's intentionally absent:**

- No `requests` — all HTTP is async via ipsdk
- No `typing.Dict`, `typing.List`, `typing.Optional` — modern union syntax (`X | Y`) used throughout
- No `time.sleep` or blocking I/O in async code
- No wildcard imports
- No bare `except:` clauses

---

## Development Workflow

**Initial setup:**

```bash
make build          # Creates .venv, installs all dependencies via uv
```

**Daily commands:**

```bash
make test           # Run test suite
make format         # Format with ruff
make check          # Lint with ruff check
make coverage       # HTML + terminal coverage report
make security       # bandit security scan
make premerge       # Full pipeline: clean → format → check → security → test
```

**Before every commit:** `make premerge` — this is what CI runs.

**Running the server locally:**

```bash
uv run itential-mcp run                                         # stdio (direct process)
uv run itential-mcp run --transport sse --host 0.0.0.0 --port 8000   # SSE
uv run itential-mcp run --config config.conf                    # from config file
ITENTIAL_MCP_SERVER_LOG_LEVEL=DEBUG uv run itential-mcp run    # verbose logging
```

**CLI reference:**

```
itential-mcp [--config FILE]
  run       - Start the server
  tools     - List available tools
  tags      - List available tags
  call      - Call a specific tool
  version   - Show version
```

**Multi-version testing:**

```bash
make tox            # Test against Python 3.10, 3.11, 3.12, 3.13
make tox-py312      # Single version
make tox-premerge   # Full premerge pipeline via tox
```

**Environment variables for local dev:**

```bash
ITENTIAL_MCP_PLATFORM_HOST=platform.example.com
ITENTIAL_MCP_PLATFORM_USER=admin
ITENTIAL_MCP_PLATFORM_PASSWORD=secret
ITENTIAL_MCP_PLATFORM_DISABLE_TLS=true       # Dev only
ITENTIAL_MCP_PLATFORM_DISABLE_VERIFY=true    # Dev only
ITENTIAL_MCP_SERVER_LOG_LEVEL=DEBUG
ITENTIAL_MCP_SERVER_TRANSPORT=sse
ITENTIAL_MCP_SERVER_PORT=8000
ITENTIAL_MCP_DEBUG=true                       # Enables full tracebacks on error
```

**Dynamic tool binding (no code required):**

```bash
ITENTIAL_MCP_TOOL_DEPLOY='{"type":"endpoint","name":"deploy_trigger","automation":"Deploy Configuration"}'
ITENTIAL_MCP_TOOL_ANSIBLE='{"type":"service","name":"ansible_playbook","cluster":"default"}'
```

**Container:**

```bash
make container      # Builds amd64 + arm64 container
```

**Copyright headers:** All `.py` files must have SPDX copyright headers.

```bash
make check-headers  # Verify
make fix-headers    # Add missing
```

**TLS certs for dev:**

```bash
make certs          # Generate self-signed development certificates
```

---

## Code Standards

These are enforced by CI — violations block merge.

### Type Hints

Modern syntax only, no `typing` module generics:

- `dict[str, Any]` not `Dict[str, Any]`
- `list[str]` not `List[str]`
- `str | None` not `Optional[str]`
- `from __future__ import annotations` at top of all files

### Async

- All I/O must be async — no `time.sleep`, no `requests.*`
- Parallel calls use `asyncio.gather()` — never sequential awaits when calls are independent
- Timeout protection via `asyncio.wait_for()` on all external calls
- Always use async context managers for resource cleanup

### Function Signatures

- Explicit keyword parameters over `**kwargs` or `Mapping` — this is a hard rule
- Optional parameters after `*` marker (keyword-only enforcement)
- Pydantic models for structured return types — no raw `dict` returns from tools

### Error Handling

- EAFP style: try/except, not check-before-access
- Use the exception hierarchy in `core/exceptions.py` — don't raise `ValueError` directly
- Never swallow exceptions with `except Exception: pass`
- Let specific exceptions propagate from tools — `ErrorHandlingMiddleware` handles formatting

### Documentation

Google-style docstrings on all public functions: Args, Returns, Raises sections. Module docstrings explaining purpose and contents. Inline comments explain *why*, not *what*.

### Imports

Order: stdlib → third-party → local (relative). No wildcard imports. Relative imports within the package.

### Immutability

Config objects are frozen Pydantic dataclasses — attempting to set attributes raises `FrozenInstanceError`. Design code around this.

### Naming

- Modules: `lowercase_with_underscores`
- Classes: `PascalCase`
- Functions: `lowercase_with_underscores`
- Constants: `UPPERCASE_WITH_UNDERSCORES`
- Private: `_leading_underscore`

---

## Adding Tools, Services, and Bindings

### New Static Tool

1. Create `src/itential_mcp/tools/my_feature.py` with `__tags__` and async functions returning Pydantic models
2. Create `src/itential_mcp/models/my_feature.py` with response models
3. If the tool needs API calls, add `src/itential_mcp/platform/services/my_feature.py` with a `Service` class having `name = "my_feature"`
4. Write tests in `tests/test_tools_my_feature.py`
5. Run `make premerge`

Tools are discovered automatically — no registration code needed.

### New Service Plugin

Create `src/itential_mcp/platform/services/my_service.py` with:

```python
class Service:
    name = "my_service"   # Available as client.my_service

    def __init__(self, client): ...
    async def get_resource(self, id: str) -> dict: ...
```

Auto-loaded at client initialization.

### Dynamic Binding

Set `ITENTIAL_MCP_TOOL_<NAME>` env var or add `[[tools]]` section to config file. No Python required.

---

## Configuration Reference

**Precedence (highest → lowest):** env vars → CLI args → config file → defaults

**Key environment variable prefixes:**

- `ITENTIAL_MCP_SERVER_*` — server settings (transport, host, port, logging, tags)
- `ITENTIAL_MCP_PLATFORM_*` — platform connection (host, auth, TLS, timeout)
- `ITENTIAL_MCP_AUTH_*` — authentication (jwt, oauth, oauth_proxy)
- `ITENTIAL_MCP_TOOL_*` — dynamic tool definitions (JSON blobs)

**Config loading:**

```python
from itential_mcp import config
cfg = config.get()   # Cached with @lru_cache — loads once, immutable
```

Config example: `docs/mcp.conf.example`

---

## Current State & Known Debt

### Active Tech Debt (ranked by impact)

1. **`core/errors.py` is dead code** — this module contains simple error message functions and is imported only by `tests/test_errors.py`. It has zero production usage. Safe to delete, but exists in test assertions that would need updating.

2. **No retry logic** — transient failures (network hiccups, platform restarts) propagate directly to the caller. No exponential backoff anywhere. For production deployments with unreliable networks this matters.

3. **Connection pooling opacity** — pooling is fully delegated to ipsdk. There's no visibility into pool state, no metrics, no configuration for pool size. This is a blackbox.

4. **Limited logging configuration** — log level is global. No per-module log levels. `ITENTIAL_MCP_SERVER_LOG_LEVEL=DEBUG` makes everything verbose.

5. **Service plugin implicit contract** — plugins must have a `Service` class with a `name` attribute, but this is undocumented at the call site. Failed plugin loads are logged at DEBUG and silently skipped, which can cause confusing "method not found" errors at runtime.

6. **`templates.py:get_templates`** returns `list` instead of a `RootModel` — only tool that doesn't return a Pydantic model. Not enforced by the type system.

### Areas in Flux

- FastMCP API compatibility: v0.12.1 fixed a breaking change where `include_tags`/`exclude_tags` kwargs were removed in FastMCP 3.x in favor of `enable()`/`disable()` API. Watch for further FastMCP API changes.
- `ITENTIAL_MCP_SERVER_RESPONSE_FORMAT=toon` — TOON serialization support is relatively new (v0.10.0). Less battle-tested than JSON mode.

### Testing Gaps

- 99% line coverage, but integration tests are limited — most tests mock the platform client. Real platform connectivity is only tested via the `connection test` command.
- `core/errors.py` is only tested in isolation with no production callers — these tests provide false coverage confidence for a dead module.

---

## New Developer Entry Points

### Understand the system

1. Read `README.md` for user perspective and use cases
2. Read `server/server.py` — this is the hub that wires everything together
3. Read one tool implementation in `tools/health.py` — it's the simplest and shows the full pattern
4. Read `platform/client.py` to understand how the platform connection works

### Verify your setup works

```bash
make build
make test
uv run itential-mcp version
uv run itential-mcp tools
```

### What will trip you up

- **Config is immutable** — set env vars before the process starts, not in test code after `config.get()` is called. Use `importlib.reload` or mock `config.get` in tests that need custom config.
- **`config.get()` is cached** — if you call it in a test, the cache persists across tests unless you mock it. Tests in this repo handle this with `patch("itential_mcp.config.get")`.
- **Service plugins fail silently** — if a service plugin fails to load, its methods won't exist on the client. The error is logged at DEBUG level only. Check debug logs first when `AttributeError: 'PlatformClient' object has no attribute '...'` appears.
- **Tool return types must be Pydantic models** — FastMCP generates the MCP schema from the return annotation. Functions returning bare dicts produce no schema and break MCP clients.
- **Middleware order matters** — middleware registered first is applied last (outermost). The current order in `server.py:__init_server__` is intentional.
- **`PYTHONDONTWRITEBYTECODE=1`** — always set when running Python commands. The Makefile targets do this automatically. Bytecode can cause stale import issues during development.
- **The `_tool_config` key** — bindings middleware injects this into tool kwargs and removes it after execution. If you see this parameter in a tool signature, that's why.

### Key files at a glance

```
app.py                          Entry point and exit codes
server/server.py                Server init, lifespan, transport startup
platform/client.py              Platform API client, plugin loading
platform/services/health.py     Simplest service plugin example
tools/health.py                 Simplest tool implementation example
config/__init__.py              Config loading API
config/models.py                All config dataclasses
config/defaults.py              All default values in one place
core/exceptions.py              Exception hierarchy
utilities/tool.py               Tool discovery and tag system
bindings/__init__.py            Dynamic binding orchestration
middleware/bindings.py          O(1) bindings injection
runtime/parser.py               CLI argument handling
pyproject.toml                  Project metadata, dependencies, test config
Makefile                        All development commands
CHANGELOG.md                    Full release history
docs/troubleshooting.md         Diagnostic procedures
docs/mcp.conf.example           Config file reference
```

---

## CI/CD Reference

**Pipelines:** `.github/workflows/`

- `premerge.yaml` — format → lint → check-headers → security → test. Runs on every PR.
- `container.yaml` — builds amd64 + arm64 images on merge to main branches.
- `release.yaml` — publishes to PyPI via OIDC trusted publisher on GitHub release creation.

**Dependabot** is configured for Python dependencies.

**Release process:** Tag → GitHub release → `release.yaml` publishes to PyPI. Changelog generated via `release-drafter.yml`.
