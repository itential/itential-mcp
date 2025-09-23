# Contributing to Itential MCP

Thank you for your interest in contributing to the Itential MCP project! This document provides guidelines and instructions for contributing to this project.

## Table of Contents

- [Code of Conduct](#code-of-conduct)
- [Getting Started](#getting-started)
- [Contributor License Agreement](#contributor-license-agreement)
- [Development Setup](#development-setup)
- [Contributing Process](#contributing-process)
- [Pull Request Guidelines](#pull-request-guidelines)
- [Pull Request Labels](#pull-request-labels)
- [Testing](#testing)
- [Code Style](#code-style)
- [Documentation](#documentation)
- [Getting Help](#getting-help)

## Code of Conduct

By participating in this project, you are expected to uphold our Code of Conduct. Please report unacceptable behavior to [opensource@itential.com](mailto:opensource@itential.com).

## Getting Started

1. **Fork the repository** on GitHub
2. **Clone your fork** locally
3. **Set up the development environment**
4. **Create a feature branch** for your changes
5. **Make your changes** and test them
6. **Submit a pull request**

## Contributor License Agreement

**All contributors must sign a Contributor License Agreement (CLA) before their contributions can be merged.** 

The CLA ensures that:
- You have the right to contribute the code
- Itential has the necessary rights to use and distribute your contributions
- The project remains legally compliant

When you submit your first pull request, you will be prompted to sign the CLA. Please complete this process before your contribution can be reviewed.

## Development Setup

### Prerequisites

- Python 3.10 or later
- [uv](https://github.com/astral-sh/uv) package manager
- Git

### Setup Instructions

1. **Fork and clone the repository:**
   ```bash
   git clone https://github.com/YOUR-USERNAME/itential-mcp.git
   cd itential-mcp
   ```

2. **Add the upstream remote:**
   ```bash
   git remote add upstream https://github.com/itential/itential-mcp.git
   ```

3. **Set up the development environment:**
   ```bash
   make build
   # or manually:
   uv sync --all-extras --dev
   ```

4. **Verify the setup:**
   ```bash
   make test
   make lint
   ```

## Contributing Process

### Fork and Pull Model

This project uses a fork and pull request model for contributions:

1. **Fork the repository** to your GitHub account
2. **Create a topic branch** from `devel`:
   ```bash
   git checkout devel
   git pull upstream devel
   git checkout -b feature/your-feature-name
   ```

3. **Make your changes** in logical, atomic commits
4. **Test your changes** thoroughly
5. **Push to your fork:**
   ```bash
   git push origin feature/your-feature-name
   ```

6. **Create a pull request** against the `devel` branch

### Branch Naming Conventions

Use descriptive branch names with prefixes:
- `feature/` - New features
- `fix/` - Bug fixes
- `chore/` - Maintenance tasks
- `docs/` - Documentation updates

Examples:
- `feature/add-authentication-support`
- `fix/handle-connection-timeout`
- `chore/update-dependencies`
- `docs/improve-api-examples`

## Pull Request Guidelines

### Before Submitting

- [ ] Ensure your branch is up to date with `devel`
- [ ] Run the full test suite: `make test`
- [ ] Run code quality checks: `make lint`
- [ ] Add tests for new functionality
- [ ] Update documentation if needed
- [ ] Sign the Contributor License Agreement (CLA)

### Pull Request Description

Your pull request should include:

1. **Clear title** describing the change
2. **Detailed description** explaining:
   - What the change does
   - Why the change is needed
   - How it was tested
3. **References to related issues** (if applicable)
4. **Breaking changes** (if any)

### Example Pull Request Template

```markdown
## Summary
Brief description of what this PR does.

## Changes
- List of specific changes made
- Another change

## Testing
- [ ] Unit tests pass
- [ ] Integration tests pass
- [ ] Manual testing completed

## Related Issues
Closes #123
```

## Pull Request Labels

This project uses Release Drafter to automatically generate release notes. Please apply appropriate labels to your pull requests:

### Change Type Labels
- `feature`, `enhancement` - New features and enhancements
- `fix`, `bug`, `bugfix` - Bug fixes and corrections
- `chore`, `dependencies`, `refactor` - Maintenance, dependency updates, and refactoring
- `documentation`, `docs` - Documentation changes
- `security` - Security fixes and improvements
- `breaking`, `breaking-change` - Breaking changes that require major version bump

### Version Impact Labels
- `major` - Breaking changes (increments major version)
- `minor` - New features (increments minor version)
- `patch` - Bug fixes and maintenance (increments patch version)

### Auto-Labeling
The Release Drafter will automatically apply labels based on:
- **Branch names**: `feature/`, `fix/`, `chore/` prefixes
- **File changes**: Documentation files, dependency files
- **PR titles**: Keywords like "feat", "fix", "chore"

### Special Labels
- `skip-changelog` - Exclude from release notes
- `duplicate`, `question`, `invalid`, `wontfix` - Issues that don't represent changes

## Testing

### Running Tests

```bash
# Run all tests
make test

# Run tests with coverage
make coverage

# Run specific test file
PYTHONDONTWRITEBYTECODE=1 uv run pytest tests/test_specific.py -v
```

### Writing Tests

- Place tests in the `tests/` directory
- Mirror the `src/` directory structure
- Use descriptive test names
- Include both positive and negative test cases
- Mock external dependencies appropriately

## Code Style

This project uses [Ruff](https://github.com/astral-sh/ruff) for code formatting and linting.

### Code Quality Commands

```bash
# Check code style
make lint

# Auto-format code
make format

# Auto-fix issues where possible
make fix

# Run full premerge pipeline
make premerge
```

### Style Guidelines

- Follow PEP 8 conventions
- Use type hints for all function parameters and return values
- Write comprehensive docstrings using Google style
- Keep line length to 88 characters (Black default)
- Use meaningful variable and function names

### Documentation Standards

- Always provide verbose documentation for all methods and functions
- Docstrings should use Google style documentation strings
- All docstrings must include `Args:`, `Returns:`, `Raises:` sections
- `Raises:` must only document exceptions returned by the function or method

## Documentation

### Types of Documentation

1. **Code documentation** - Docstrings and inline comments
2. **API documentation** - Tool descriptions and examples
3. **User documentation** - README and usage guides
4. **Developer documentation** - This CONTRIBUTING.md and AGENTS.md

### Documentation Updates

- Update docstrings when changing function signatures
- Add examples for new tools and features
- Update README.md for user-facing changes
- Maintain the AGENTS.md file for development guidelines

## Getting Help

### Resources

- **Documentation**: Check the README.md and AGENTS.md files
- **Issues**: Search existing issues for similar problems
- **Discussions**: Use GitHub Discussions for questions

### Reporting Issues

When reporting issues, please include:

1. **Clear description** of the problem
2. **Steps to reproduce** the issue
3. **Expected vs actual behavior**
4. **Environment information** (Python version, OS, etc.)
5. **Error messages** and stack traces (if applicable)

### Asking Questions

- Use GitHub Discussions for general questions
- Search existing discussions and issues first
- Provide context and specific details
- Be patient and respectful

## Recognition

Contributors who have their pull requests merged will be:
- Listed in the project's contributors
- Mentioned in release notes (when appropriate)
- Recognized in the project documentation

Thank you for contributing to Itential MCP!

---

For questions about contributing, please contact [opensource@itential.com](mailto:opensource@itential.com).