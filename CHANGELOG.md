# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

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
