# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

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
- Migrate from toonify to toon-python (#270)
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
