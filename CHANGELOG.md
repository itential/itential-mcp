# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- `describe_job` and `describe_session` now return a `pending_manual_tasks`
  field so agents can see when a run is waiting on a human. It is tri-state:
  `null` means unknown (the lookup failed with an error other than not-found;
  the tool still succeeds), an empty list means none are pending (including a
  not-found result and any run that is not live), and a list holds the pending
  tasks. The lookup only runs for jobs with status `running` and sessions with
  status `RUNNING`.
- New read-only `describe_manual_task` tool (new `work_center` tag, enabled by
  default) returning the detail of a manual task: header, message, body,
  variables, button labels, view type and the owning job or session. Form views
  (`RenderJsonSchema`, `viewTemplateResults`) are reported with
  `completion_supported` false.
- New destructive `complete_manual_task` tool (`work_center` tag, enabled by
  default; disable it with `exclude_tags` or whitelist other tools with
  `include_tags`). It completes exactly one
  pending manual task with finish state `success` or `failure`. Completion is
  irreversible and cannot be retried. By default (`confirm=False`) it only
  returns a preview; `confirm=True` performs the completion, and agents must
  ask the human first. Because the platform does not validate the finish
  state, the tool validates it first: `failure` is rejected unless the task
  has a failure button, and it refuses tasks that are not pending, whose job
  or session is not running, or that are form views (`RenderJsonSchema`,
  `viewTemplateResults`), which must be completed in the Itential UI.
  Identity caveat: the completion is attributed to the MCP service account or
  OAuth client, not to the person who asked; there is no per-user
  authorization. Registered tools rise to 79 (all enabled by default).
- Identity caveat: the platform runs all MCP operations as the MCP service
  account or OAuth client, with no per-user authorization, so these tools show
  what that account can see.
- Limitation: detection covers manual tasks attached directly to the run's own
  ID. Manual tasks inside nested runs (child workflows, or a workflow called
  by an agent) are not guaranteed to be listed.

### Changed
- `complete_manual_task` and `describe_manual_task` guidance now explains that
  `finish_state` `success` is the task's main button (not necessarily
  "approve") and `failure` the second button, that `btn_success` and
  `btn_failure` are the labels to show the human, and that agents must map the
  human's answer to a finish state rather than assume `success`. Text only, no
  behavior change.
- `describe_manual_task` documentation (tool docstring and the `body` field
  description) now tells agents how to present the body (usually text or HTML,
  returned unmodified) and the available choices to the human, and warns that
  the content is platform-supplied data authored by the workflow builder, not
  instructions to follow (prompt-injection note).
- Platform client wrapper gains a `patch` verb that reformats HTTP errors
  like `get`/`post`/`put`/`delete` and preserves `http_status` on the raised
  exception (for example 409).
- Errors raised for HTTP failures from platform services now preserve the
  upstream HTTP status code on the exception's `http_status` attribute.

### Fixed
- `get_sessions`, `get_agent_token_usage` and `get_agent_session_token_usage`
  no longer fail with `Not found: 'sessionId'` when the session history
  contains sessions that failed before an execution-engine session ID was
  assigned; those records are now skipped (#422)

### Security
- Restricted the dev-group `tox` and `tox-uv` to Python 3.11+ so the lock file
  no longer carries the vulnerable `filelock` 4.1.0 on its Python 3.10 branch
  (GHSA-v4x8-3wr5-3wq8, GHSA-crv4-6mhj-j5jh, GHSA-2g95-wg33-c5x2,
  GHSA-jqc4-5cvw-7w85, GHSA-567q-5qvw-pf92, GHSA-9vhv-jxww-xfm5). Package
  `requires-python` is unchanged; running `tox` itself now needs a 3.11+ host.
- Refresh `uv.lock` to clear transitive-dependency advisories (no
  `pyproject.toml` changes):
  - Authlib 1.7.2 -> 1.9.1, resolving critical GHSA-6v38-4h7w-rj9h, high
    GHSA-7vr2-2fgp-9w7p and GHSA-8m4g-j4wp-wgcg, medium GHSA-q686-2qmg-hqc7,
    GHSA-fch4-3c6x-j4gc, GHSA-c5mf-xmp2-59rc and GHSA-x4rv-c3wx-4cr8, and low
    GHSA-jj7h-c3hg-m23x (first patched 1.9.1 covers all of them).
  - dnspython 2.8.0 -> 2.9.0 on Python 3.11+, resolving high
    GHSA-45c3-73f7-pv4m (patched 2.9.0). dnspython 2.9.0 requires Python
    3.11+, so the Python 3.10 branch of the lock stays on 2.8.0 and the
    Dependabot alert may remain open for that branch. dnspython is only a
    transitive dependency (via `email-validator`) and is not used directly.
  - No other packages changed.

## [0.14.1] - 2026-10-15

### Fixed
- Exclude agent (and other non-workflow) automation triggers from
  `get_workflows`, which previously listed agent-backed endpoint triggers as
  workflows; they remain available via `get_agents` and `get_automations` (#417)
- `get_automations` now lists only automations with an enabled API endpoint
  trigger (those startable via `trigger_automation`); automations with no or a
  disabled endpoint trigger are no longer returned (#419)
- `itential-mcp tools` now shows each tool's description for all docstring
  styles; previously 8 tools displayed a blank description and undocumented
  tools could raise `AttributeError` (#409)

### Security
- Refresh `uv.lock` to clear transitive-dependency advisories (no
  `pyproject.toml` changes; all three are transitive pins):
  - PyJWT 2.13.0 -> 2.15.1, resolving 13 advisories including critical
    GHSA-ffc3-869f-jxw9 (CVE-2026-102268), high GHSA-p4g4-x82p-q773,
    GHSA-w2cx-738m-mc7w, GHSA-r6x4-923q-g947, GHSA-9j54-fg26-wv3r,
    GHSA-9v7f-9g4p-ffgj, and medium GHSA-2gx3-rcp4-g85q,
    GHSA-jwrc-g2q2-pq5p, GHSA-8wjv-2p76-3863, GHSA-w6j9-cwv2-h6wq,
    GHSA-hxm8-2xgr-2p9m, GHSA-42vr-xj54-vc7v, GHSA-gvp8-978c-rx2q
  - anyio 4.12.1 -> 4.14.2, resolving critical GHSA-82r6-8w77-94w6
    (CVE-2026-63374) and medium GHSA-5p39-cfhj-2xmp (CVE-2026-64847)
  - virtualenv 20.39.0 -> 21.14.5 (dev-only, via tox), resolving high
    GHSA-94p9-xgh2-xp45, GHSA-x78j-v8h9-3j2q, GHSA-p58f-9548-mpm2 and
    medium GHSA-9h9j-4vrj-gf7g; adds python-discovery as a new transitive
    dependency of virtualenv (#420)
- Refresh `uv.lock` again to clear further advisories (no `pyproject.toml`
  changes; all are transitive pins):
  - fastmcp and fastmcp-slim 3.4.4 -> 3.4.11, resolving medium
    GHSA-7xgj-8392-5q4r (authorization skipped on direct calls)
  - mcp 1.29.0 -> 1.30.0, resolving medium GHSA-84m7-p3x7-pcfv
    (CVE-2026-59951)
  - opentelemetry-api 1.39.1 -> 1.45.1, resolving medium GHSA-xcq7-p3pf-p88h
    (CVE-2026-114603)
  - uv 0.12.2 -> 0.13.5, resolving critical GHSA-hq85-5cpj-mr62 (emSign root
    CA)
  - virtualenv 21.14.5 -> 21.14.13 (dev-only, via tox), resolving 12
    advisories: high GHSA-vxj4-q4g9-crj7, GHSA-c978-59m8-c77v,
    GHSA-6w3r-xr62-4xcp, GHSA-394h-qwmc-48pf, medium GHSA-43mp-35q3-x3fq,
    GHSA-cw65-gx24-rc82, GHSA-558c-9hv2-4prj, GHSA-hhxq-47xx-j5xx,
    GHSA-fc2g-4w5p-6whm, and low GHSA-qmx5-4p3x-wvqf, GHSA-494p-63j8-28p3,
    GHSA-cx28-75q4-x26q
  - filelock 3.24.3 -> 4.2.4 (dev-only, via tox/virtualenv) on Python 3.11+;
    Python 3.10 resolves to 4.1.0 because 4.2.x requires Python 3.11+, so
    high GHSA-v4x8-3wr5-3wq8 and low GHSA-567q-5qvw-pf92, GHSA-9vhv-jxww-xfm5
    (patched in 4.2.1) remain open for the Python 3.10 branch of the lock
  - Incidental lock movement: certifi, distlib and packaging, plus
    typing-extensions 4.16.0 on Python below 3.11 only (required by mcp 1.30)

### Docs
- Clarify that `get_workflows` and `get_automations` return only automations
  with an enabled endpoint trigger, and refresh the Operations Manager tool
  lists in `docs/tools.md` and `docs/user-guide.md` (#418)

## [0.14.0] - 2026-08-13

### Added
- Agent token-usage analytics tools for `agent_session_manager`:
  `get_agent_token_usage`, `get_agent_session_token_usage`, and
  `describe_session_token_usage` (#396)
- Gateway configuration export/import tools (`export_gateway_configuration`,
  `import_gateway_configuration`) in `gateway_manager`, including an MCP
  elicitation confirmation gate that prompts before exporting configuration
  containing secrets/credentials (#397)
- Python 3.14 added to the CI test matrix (3.10-3.14 all covered;
  `requires-python` floor remains 3.10, unchanged) (#400)
- MCP tool annotations (`readOnlyHint`/`destructiveHint`/`idempotentHint`/
  `openWorldHint`), per-tool `title`, and deterministic tool
  discovery/registration ordering across all ~77 tools, enforced going
  forward by new CI completeness and safety-invariant guards in
  `tests/utilities/test_tool.py` (#402)
- One-time runtime deprecation warning on `--transport sse` startup, plus a
  README/CLI-help/docs sweep steering new usage toward `http`; `sse` remains
  fully functional and wire-compatible (#406)

### Fixed
- Restore documented config precedence (env vars/CLI flags now correctly
  override config-file values) across all 39 affected
  `ServerConfig`/`AuthConfig`/`PlatformConfig` fields (#403)
- Parse documented `[server] auth_*` config-file keys without silently
  dropping or mangling them, including correcting a global (non-prefix)
  string replace that mangled `oauth_*` field names (#404)
- Wrap `get_templates`'s return in the existing `GetTemplatesResponse`
  `RootModel`, removing a spurious startup warning (type-hygiene only; wire
  payload is unchanged) (#405)

### Security
- Bump pytest, idna, python-dotenv, and uv to patched versions (#398)
- Lift the `cryptography` constraint to `>=50.0.0,<51`, resolving the 3
  held high-severity advisories plus GHSA-537c-gmf6-5ccf that motivated the
  earlier deliberate 46.x hold (#399)

### Changed
- Bump the Containerfile's base Python from 3.10 to 3.13 for both builder
  and runtime stages, including the companion `.python-version` fix needed
  for the bump to actually take effect (#401)
- Fix stale `make premerge` references in `AGENTS.md` (renamed to `make ci`
  in #325), and update `release.yaml`'s description to reflect the
  tag-triggered auto-release flow (#395)

### Docs
- Add `docs/deployment.md` covering platform connectivity/deployment
  guidance (#407)

### Note
- All previously open Dependabot advisories are now resolved: 0 open as of
  this release (see the correction to the 0.13.3 entry below).

## [0.13.3] - 2026-08-05

### Security
- Constrain pydantic-settings to >=2.14.2, resolving GHSA-4xgf-cpjx-pc3j
  (medium severity, `NestedSecretsSettingsSource` issue with
  `secrets_nested_subdir=True`, a feature not used anywhere in this
  codebase); transitive dependency via fastmcp/mcp with no direct usage,
  re-resolved via uv lock with no cascading version changes (#387)

### Fixed
- Merge supplied devices into a device group's existing device list instead
  of replacing it, which previously caused `add_devices_to_group` to silently
  delete every device not included in the current call (#383)
- Raise `NotFoundError` instead of an unhandled `TypeError` from
  `add_devices_to_group`/`remove_devices_from_group` when the target device
  group name does not exist (#384)
- Declare the missing `description` field on `CommandTemplateDetail`, which
  previously caused Pydantic to silently drop it from
  `describe_command_template`'s response even when the platform returned one
  (#385)
- Paginate `get_integration_models` using the existing `_paginate` helper
  (already used by `get_integrations`) instead of a single unpaginated
  request, which previously silently truncated results to the platform's
  default page size of 25 and made `create_integration_model`'s
  duplicate-check unreliable (#386)
- Raise `ConfigurationException` naming the invalid section instead of
  silently dropping any unrecognized top-level config file section (e.g. a
  typo like `[profile prod]`), which previously discarded the section's
  values with zero warning and let affected settings silently fall back to
  their defaults (#388)
- Report itential-mcp's own resolved version in the MCP `initialize`
  handshake's `serverInfo.version` field instead of fastmcp's own package
  version, which previously happened because `FastMCP()` was instantiated
  without a `version=` argument (#390)
- Derive OAuth proxy `base_url`/`redirect_path` from the configured
  `redirect_uri` using proper URL parsing instead of a
  `removesuffix("/auth/callback")` heuristic, which previously was a no-op
  for any redirect URI not literally ending in that path (e.g. `/callback`,
  `/sso/oauth/return`) and silently produced a callback URL that never
  matched what was registered with the upstream IdP (#391)
- Update `ipsdk` to 0.8.0 and adjust internal tests for its now-read-only
  `IpsdkError.request`/`.response` attributes; no `src/` behavior change,
  since existing error-handling code only ever reads these attributes (#389)

### Note
- 9 Dependabot advisories remain open and untouched by this release,
  including 3 new high-severity `cryptography` advisories surfaced
  2026-08-04. The `cryptography` pin (`>=46.0.7,<47`, see 0.13.1/0.13.2
  notes) is still deliberately held at the 46.x line pending evaluation of
  47.x/48.x breaking API changes; not yet re-assessed against the new
  high-severity findings.
  - **Correction (2026-08-13):** this note is stale as of the 0.14.0
    release. The `cryptography` pin was lifted to `>=50.0.0,<51` in #399,
    clearing the 3 high-severity advisories referenced above plus
    GHSA-537c-gmf6-5ccf. A full re-triage on 2026-08-07 confirmed 0 open
    Dependabot advisories remained at that point. See the 0.14.0 entry
    above.

## [0.13.2] - 2026-08-03

### Security
- Bump fastmcp to >=3.4.1,<4, floors transitive starlette to 1.3.1 and
  resolves 5 starlette CVEs (including CVE-2026-48710) that have no patched
  release in the starlette 0.x line; individually live-integration-tested
  against SSE and HTTP transports before merge given the elevated risk of a
  transitive ASGI/transport-layer major bump (#369)
- Constrain mcp SDK to >=1.28.1,<2, resolving 3 high-severity mcp SDK
  advisories while staying below the same-day 2.0.0 major redesign;
  individually live-integration-tested against OAuth/JWT auth flows via a
  local mock IdP and live platform tool calls before merge given the same
  transport-layer risk profile as #369 (#371)

### Fixed
- Surface CLI tool errors by default and include the response body, instead
  of silently exiting 1 with empty stdout/stderr unless
  `ITENTIAL_MCP_DEBUG` was set (#372)
- Replace broken `StaticTokenVerifier` fallback with `JWTVerifier` in
  `oauth_proxy`, fixing a `TypeError` crash at server startup (#373)
- Fail fast with a clear `ConfigurationException` on `auth_type=oauth` (full
  OAuth authorization server mode) instead of silently accepting config that
  produces a confusing "Client ID not found" failure during a real
  authorization-code handshake; documentation corrected to stop presenting
  this mode as supported (#374)
- Allow null `description`, `package`, and `version` fields in
  `get_applications` response payloads (#375)
- Add missing defaults for nullable command template fields on
  `CommandTemplateDetail`/`CommandTemplate` (#376)
- Normalize case of the `status` field in `create_integration_model`
  responses to accept the platform's actual `"Created"` casing (#377)
- Declare the `devices` parameter as `list[str]` (was an untyped bare list)
  in device group and command template tools (#378)
- Raise a clear exception instead of an unhandled `IndexError` in
  `run_compliance_plan` when a compliance plan's run history is empty (#379)
- Use the correct HTTP method and path for `update_command_template`, which
  previously 404'd on every real call (#380)
- Add missing `default=None` to the `devices` parameter in
  `add_devices_to_group` and `remove_devices_from_group`, which caused these
  tools to still fail with a stringified-array validation error even after
  the item-type fix above, since the parameter's JSON schema incorrectly
  marked it as required (#382)
- Fix `add_devices_to_group` and `remove_devices_from_group` failing with
  `method must be of type \`HTTPMethod\`` -- `describe_device_group` (called
  internally by both tools) passed a raw string instead of the required
  `HTTPMethod` enum to the underlying platform client (#382)

### Note
- The two dependency bumps above (#369, #371) touch the ASGI/transport layer
  and carry more inherent risk than the rest of this release; each was
  individually live-integration-tested (SSE/HTTP transports, OAuth/JWT auth
  flows via a local mock IdP, live platform tool calls) before merge, per
  this release's process.
- The cryptography advisory noted as open in 0.13.1 (GHSA-537c-gmf6-5ccf,
  patched floor 48.0.1) remains open in this release; still deliberately
  held at the 46.x line pending evaluation of 47.x/48.x breaking API
  changes.

## [0.13.1] - 2026-07-24

### Security
- Pin fastmcp to >=3.0.2,<4 and declare MCP 2025-11-25 protocol version in README (#363)
- Bump pyjwt and python-multipart to patched versions, closing a JWK-as-HMAC-secret
  forgery advisory (pyjwt) and a negative Content-Length DoS advisory
  (python-multipart) (#365)
- Bump cryptography to 46.0.7 and constrain to the 46.x line, addressing the
  vulnerable-OpenSSL-in-wheels advisory; deliberately holds at 46.x rather than
  47.x/48.x pending evaluation of breaking API removals in those lines (#366)

### Fixed
- Tolerate scalar `cpuUsage` values and missing `description` fields in
  get_health response payloads from platform versions that send this data in
  an unexpected shape (#367)
- Use `str.removesuffix()` instead of `str.rstrip()` when deriving OAuth
  `base_url`, fixing silent corruption of redirect URIs whose host ends in a
  character from the old rstrip character set (e.g. `.uk`-TLD hosts) (#368)

### Changed
- Demote internal tool entry-trace log calls from info to debug level across
  all tool modules -- these were developer-only breadcrumbs riding the
  client-visible notification channel at an inappropriately high severity (#364)

### Note
- The cryptography advisory addressed above (GHSA-537c-gmf6-5ccf) is not fully
  closed by this release: the advisory's patched floor is 48.0.1, not 46.0.7,
  and this release deliberately stays on the 46.x line. This advisory will
  continue to show as open in Dependabot until a follow-up release evaluates
  the 47.x/48.x breaking API changes.
- PR #369 (fastmcp bump to >=3.4.1,<4, resolving starlette CVEs) is
  intentionally not included in this release due to its elevated risk profile
  (breaking major transitive starlette bump) and will ship separately.

## [0.13.0] - 2026-07-23

### Added
- Agent session manager service, tools, and models (#354)
- Agent automation support in operations manager, including StartAgentResponse
  and duck-typed return handling for start_workflow (#355)
- trigger_automation tool and get_automations unified view covering workflows,
  agents, and other automation types; start_workflow is now a stable,
  non-deprecated wrapper delegating to trigger_automation (#356)

### Fixed
- Add missing `from __future__ import annotations` import in two services
  modules and add pagination test coverage for get_automations (#360)
- Handle Union-of-BaseModel return types in tool output schema generation,
  fixing a startup warning for trigger_automation/start_workflow whose
  output_schema could not previously be derived (#361)

### Note
- 0.12.2 (previous release) contained a feature commit (5 new inventory
  manager tools, #319) alongside its patch-shaped bugfixes. Per semver this
  should have been a minor release, not a patch release. 0.13.0 corrects the
  version sequence going forward.

## [0.12.2] - 2026-07-23

### Added
- Inventory manager tools for CRUD operations and node management (#319)

### Security
- Bump pygments to 2.20.0 for CVE-2026-4539 (#350)

### Fixed
- Coerce stringified values in start_workflow data to match workflow input schema (#348)
- Expose variables field in describe_job response (#347)
- Add missing await on render_template service call (#336) (#344)
- Correct Annotated type for optional str parameters in lifecycle_manager (#335) (#343)
- Add missing await on start_application service call (#334) (#342)
- Add missing await on compliance report service call (#333) (#341)
- Add missing await on compliance plan service calls (#332) (#340)
- Make app field optional on TaskMetricElement (#331) (#339)
- Make package and description optional on GetAdaptersElement (#330) (#338)
- Allow optional fields on AdapterInfo for inactive adapter payloads (#329) (#337)
- `--config` flag ignored when placed before subcommand (#322)

### Changed
- Rename premerge to ci and harden CI workflow (#325)
- Modernize Makefile with best practices (#324)
- Rewrite AGENTS.md as concise codebase reference (#323)
- Bump actions/checkout from 6 to 7 (#351)
- Bump softprops/action-gh-release from 2 to 3 (#346)
- Bump docker/build-push-action from 6 to 7 (#326)
- Bump docker/setup-buildx-action from 3 to 4 (#327)
- Bump docker/login-action from 3 to 4 (#328)

## [0.12.1] - 2026-02-25

### Fixed
- Replace removed FastMCP include_tags/exclude_tags kwargs with enable/disable API (#320)
  - FastMCP 3.x removed include_tags and exclude_tags from constructor
  - Migrated to new post-creation API: server.enable() and server.disable()

## [0.12.0] - 2026-02-25

### Added
- Connection test command for platform connectivity validation (#302)
- Comprehensive troubleshooting guide (#303)
- Additional gateway_manager services (#305)

### Changed
- **CLI**: Restructured argument parser to make `--config` a true global CLI option (#313)
- Improved platform services code quality and test coverage (#306)
- Expanded .gitignore and updated documentation (#304)
- Improved test coverage to 99% (#308)

### Fixed
- Pass input_params as keyword argument in run_service tool (#317)
- Add safe JSON deserialization with plain text fallback in runner (#316)
- Correct toon package import after package rename (#315)
- Convert HTTP method strings to HTTPMethod enum for ipsdk compatibility (#307)

## [0.11.1] - 2026-01-16

### Fixed
- Use attribute access for AuthConfig instead of dictionary access (#297)
- AuthConfig AttributeError and tool discovery tag parsing (#295)

## [0.11.0] - 2026-01-08

### Added
- Comprehensive platform package tests (#287)
- TTL support for platform connections (#287)
- Python 3.13 support and tox testing infrastructure (#289)
- Copyright header checking script with SPDX enforcement (#290)
- Better exception logging to logging module (#291)

### Changed
- Restructure config module into modular package with clean API (#292)
- Implement architecture improvements for reliability and security (#285)
- Optimize bindings middleware from O(n) to O(1) lookup (#280)
- Modernize type annotations across all modules (#279)

### Fixed
- Annotated issues preventing mcp from starting (#286)
- Configure pytest to suppress false positive warnings (#288)
- Update IpsdkError exception handling for updated ipsdk library (#283)
- RuntimeWarning coroutines not awaited in tests (#281)
- Add missing await in apply_device_configuration (#278)

### Documentation
- Add comprehensive third-party license attribution file (#284)

### CI/CD
- Migrate PyPI publishing to trusted publisher (OIDC) (#282)

## [0.10.0] - 2025-12-02

### Added
- Serialization middleware with toon support (#268)
- Toon documentation references (#269)

### Changed
- Bump actions/checkout from 5 to 6 (#273)
- Migrate from toonify to python-toon (#270)
- Convert __init_routes__ method to async (#271)

### Fixed
- Resolve websockets deprecation warning (#274)
- Service tool env config (#272)
- Correct tool discovery path in utilities (#267)
- Env var parsing (#266)

## [0.9.0] - 2025-11-11

### Added
- TLS certificate support (#259)
- Integrations tool with model filtering (#258)
- Kubernetes-standard health check endpoints (#253)
- Async context manager support to PlatformClient (#247)
- OAuth 2.0 auth support for HTTP transports (#246)

### Changed
- API returns get_gateways data inconsistently, gw name and cluster id (#264)
- Sensitive data scanner to filter log messages (#263)
- Keepalive functionality to prevent session timeouts (#262)
- Reorganize core modules into runtime package (#261)
- Comprehensive documentation updates and improvements (#260)
- Reorganize CLI modules into cli/ package (#257)
- Comprehensive status endpoints documentation for operators (#256)
- Comprehensive OAuth authentication guide (#254)
- Convert server.py to server package structure (#252)
- Move response module to platform package (#250)
- Move client and services to platform package (#248)

### Fixed
- Filter disconnected gateways in get_gateways function (#255)
- Comprehensive auth module test coverage (#251)
- Modified result object from get_service call to be [] (#245)
- Incorrect function reference for get_gateways tool call (#244)

## [0.8.0] - 2025-11-04

### Added
- JWT authentication support (#229)
- Device type validation for golden config trees (#236)
- Action executions tool to retrieve instance history (#225)
- Comprehensive user guide and documentation index (#237)

### Changed
- GitHub release creation to release workflow (#242)
- README badges (#241)
- Core package for fundamental modules (#239)
- All *utils modules moved into utilities package (#238)
- Async context manager implementation for Server class (#234)
- Middleware package creation (#233)
- README with comprehensive feature updates and container examples (#228)

### Fixed
- Model to accept dict or list (#235)
- Typo and incorrect var value on get_jobs tool (#227)

## [0.7.1] - 2025-10-18

### Fixed
- Remove invalid darwin/arm64 platform from container workflow (#224)

## [0.7.0] - 2025-10-17

### Added
- Multi-architecture container build support (#220)
- NONE log level option (#213)
- ai-assistant-configs examples (#209)

### Changed
- Bump astral-sh/setup-uv from 6 to 7 (#221)
- Added capability to parse out string inputs to handle Claude behavior (#218)

### Fixed
- Added logic to avoid tag overwrite (#222)
- Avoid redundant JSON schema generation in output_schema assignment (#219)
- Added a type check before calling issubclass() (#217)
- Health model validation errors for Node.js versions and syslog field (#212)
- Correct CLI default values (#208)

## [0.6.1] - 2025-09-24

### Fixed
- Set the logging level on server start #205


## [0.6.0] - 2025-09-23

### Added
- Service bindings and JSON utilities (#194)
- Comprehensive logging module (#193)
- Tools extensibility with --tools-path (#191)
- Expose workflow tool (#187)
- Comprehensive command templates support with models, services, and enhanced testing (#169)
- Comprehensive compliance plans support with models and enhanced testing (#168)
- Configuration Manager with models, comprehensive documentation, and tests (#164)

### Changed
- Modernize path handling using pathlib (#196)
- Enforce 95% test coverage threshold (#195)
- Enhance config system with defaults (#192)
- Consolidate Automation Studio models and tools structure (#186)
- Simplify device groups implementation and improve docstrings (#184)
- Improve gateway manager implementation and add missing docstrings (#183)
- Improve docstrings in configuration manager tools (#182)
- Improve command templates formatting and add missing docstrings (#181)
- Simplify adapters service implementation and fix docstring typo (#180)
- Remove cache module and simplify server architecture (#172)
- Default bindings tag is now `bindings` (#171)
- Move account_id_to_username to operations_manager as private function (#170)
- Configuration Manager service enhancements (#167)
- Device management models and comprehensive testing (#166)
- Updated tags docs with all available tags (#160)
- Optimize _get_tools_from_env function and add comprehensive test coverage (#162)

### Fixed
- Correct exception handling in run_service (#197)
- Update adapter service to return raw data and align tests (#188)
- Updates response type hint to reference ipsdk (#179)
- TextFSM Template Validation Issues (#178)
- Describe job pydantic issue (#175)
- Device.deviceType and Device.status to optional (#174)
- Pydantic validation in runner.py and gateway_manager.py (#173)
- Import statements for tools importing models (#165)
- Automation lookup in bindings endpoint (#161)

### Testing
- Add comprehensive test coverage for operations_manager tools (#189)
- Automation Studio Integration with TextFSM & Enhanced Command Templates (#176)
- Add comprehensive unit tests for services/workflow_engine module (#163)

## [0.5.0] - 2025-09-09

### Added
- Bindings system for dynamic tool creation (#158)
- Comprehensive workflow engine metrics support (#157)
- Comprehensive health monitoring system (#155)
- Middleware support to FastMCP server (#151)
- Gateway Manager models and enhance tool type safety (#149)
- Documentation and readme updates (#148)
- Two new tools for managing device groups (#64)

### Changed
- Dependency: bump actions/setup-python from 5 to 6 (#156)

### Fixed
- Instance_data field to be optional in lifecycle manager models (#154)
- Get_workflows response structure and model validation (#153)

## [0.4.0] - 2025-09-02

### Added
- Comprehensive Google-style docstrings across codebase (#145)
- Comprehensive test coverage for missing services modules (#143)
- MCP server documentation (#141)
- Project documentation and build improvements (#140)
- Operations Manager functionality with Pydantic models and comprehensive test coverage (#139)
- Integration models with Pydantic type safety and comprehensive test coverage (#138)
- Comprehensive test coverage for errors module (#137)
- Golden Configuration management functionality (#132)
- Lifecycle manager tools with Pydantic models and comprehensive test coverage (#135)
- Application models and services with type-safe response handling (#134)
- Comprehensive adapter management system (#133)
- Gateway Manager tools for service automation (#124)
- Describe instance tool for Lifecycle Manager resources (#116)
- Lifecycle Manager instance action execution tool (#111)
- CI testing coverage for Python 3.10-3.13 matrix (#112)
- Bandit security scanning integration (#110)
- Tools reference documentation (#103)
- New command for calling tools (#101)
- Unit test cases for the errors module (#99)
- Two new commands to the application (#98)
- CLI module with comprehensive test coverage (#91)
- New tool `get_job_metrics_for_workflow` (#92)

### Changed
- Operations manager test to match actual implementation behavior (#144)
- Action.schema field to input_schema in lifecycle manager models (#142)
- Project dependencies (#131)
- Services architecture and enhance client error handling (#128)
- Client architecture and add comprehensive test coverage (#125)
- Workflow lookup to include project members (#123)
- Removed version pins from pyproject.toml dependencies (#122)
- Use inspect cleandoc (#120)
- Run_action tool (#115)
- Cache module refactoring (#106)
- Server instructions as a global variable (#105)
- Server.py docstrings and instructions (#100)
- Adapters and applications to use async sleep (#96)
- License identifier in `pyproject.toml` (#95)

### Fixed
- Operations manager test to match actual implementation behavior (#144)
- Indents in client module (#127)
- Typo in workflow name (#114)
- Bug in the runner (#107)
- Issue loading module tags (#94)
- Issue with AlreadyExistsError (#90)

### Removed
- Unused utility functions from functions.py (#136)
- Created and update metadata from tools results (#93)

### Security
- Bandit security scanning integration (#110)
- Refactor exception hierarchy and remove legacy error module (#109)

## [0.3.0] - 2025-07-15

### Added
- Tags to tools modules (#87)
- Support for `__tags__` attribute in modules (#86)
- Optimize docstrings across all modules for LLM consumption (#71-83)
  - adapters.py and applications.py (#71)
  - command_templates.py (#72)
  - compliance_plans.py (#73)
  - compliance_reports.py (#74)
  - configuration_manager.py (#75)
  - device_groups.py (#76)
  - devices.py (#77)
  - integrations.py (#78)
  - jobs.py (#79)
  - lcm.py (#80)
  - system.py (#81)
  - wfe.py (#82)
  - workflows.py (#83)
- Several changes guided by LLM. Optimized to focus on keywords and minimal explicit descriptions (#70)
- Module tag to all tools (#68)
- New tools for working with integration models (#67)

### Changed
- Renames the lcm module (#85)
- Updates the get_task_metrics tool (#84)

## [0.2.0] - 2025-07-01

### Added
- New tools for working with adapters (#66)
- New tools for working with applications (#65)
- New tool for creating LCM resources (#62)
- Two new tools for working with compliance plans (#61)
- New tool for working with device groups (#60)
- Apply configuration to a device (#59)
- New tool that will render a Jinja2 template (#58)
- Support for streamable HTTP (#54)
- New tools for working with Lifecycle Manager resources (#52)
- Configuration file and tags to the application (#48)
- New tools for getting device config and performing backup (#47)
- Simple in-memory key value store for caching (#45)
- New tools for working with command templates (#42)
- Verbose output when running `make test` (#38)
- New tool to retrieve automations (#36)
- New tool to retrieve jobs from operations manager (#35)

### Changed
- Generate the CLI options from the config (#57)
- Refactor creating MCP server instance (#56)
- Updates the get_jobs tool to restrict by workflow name (#51)
- Update all tools to use annotated arguments (#46)
- Updates the workflows module (#44)
- Consolidate all utility functions into a single module (#43)
- Updates the jobs tools (#40)

### Fixed
- Fixes typo in command_templates keyword arg (#55)
- Sets the log level only when transport=sse (#53)
- Modified get_workflows docstring to aid LLM workflow name correlation (#50)
- Update the inspect logic to avoid loading imported functions (#41)
- Fixes issue where call to devices tool doesn't return (#37)

## [0.1.0] - 2025-05-01

### Added
- New tool to collect job status (#28)
- New tool for obtaining the compliance report (#27)
- New tool for retrieving triggers (#22)
- New tool for getting all devices (#20)
- Support for setting a timeout value (#12)
- Initial version of developer guide (#7)
- New tool for starting a workflow (#5)
- Tool for job and task aggregate metrics (#4)
- Premerge and release workflows (#1)

### Fixed
- The `get_devices(...)` tool doesn't return all devices (#21)
- Get workflows will timeout (#17)
- Fixes issue coercing env var to proper type (#16)
- Fix ENV -> config typo (#15)
- Fix docker example (#10)
- Fixes spelling error in README.md (#6)
- Write error message to stderr when the server doesn't start (#3)
- Attempting to start the server would fail (#2)

### Changed
- Set the CLI default timeout to 30 (#26)
- Split the workflow tools into a get and a describe (#19)
- Updated container target and build (#13)
- Upgrade all project dependencies (#11)
- docs/readme-enhancements (#9)
- Extracts client from server (#8)

### Removed
- Remove the `docs/` folder (#30)

### Security
- Add CODEOWNERS to the repository (#29)
