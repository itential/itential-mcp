# !make

# Copyright 2025 Itential Inc. All Rights Reserved
# GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)

CONTAINER_RUNTIME ?= docker
CONTAINER_TAG ?= itential-mcp:devel

.DEFAULT_GOAL := help

.PHONY: build certs check clean container coverage fix format lint security premerge test

# The help target displays a help message that includes the available targets
# in this `Makefile`. It is the default target if `make` is run without any
# parameters.
help:
	@echo "Available targets:"
	@echo "  build      - Build the local development environment"
	@echo "  certs      - Generate certificates for the local development environment"
	@echo "  check      - Check code quality without making changes"
	@echo "  clean      - Clean the development environment"
	@echo "  container  - Build the application as a container"
	@echo "  coverage   - Run test coverage report"
	@echo "  fix        - Auto-fix code quality issues where possible"
	@echo "  format     - Format code using ruff formatter"
	@echo "  lint       - Run analysis on source files (alias for check)"
	@echo "  security   - Run security analysis with bandit"
	@echo "  premerge   - Run the premerge tests locally"
	@echo "  test       - Run test suite"
	@echo ""

# The test target will invoke the unit tests using pytest. This target
# requires uv to be installed and the environment created.
test:
	PYTHONDONTWRITEBYTECODE=1 uv run pytest tests -v -s

# Builds the local environment which can be used for development or simply
# running the server from source. This target requires `uv` to be installed
# and available in the system path.
build:
	uv sync

# The certs target generates development certificates using the makecerts.sh script.
# This creates a self-signed CA and server certificate for local development.
certs:
	@scripts/makecerts.sh

# The clean target will remove build and dev artifacts that are not
# part of the application and get created by other targets.
clean:
	@rm -rf .pytest_cache coverage.* htmlcov dist build *.egg-info certificates
	@find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true


# The coverage target will invoke pytest with coverage support. It will
# display a summary of the unit test coverage as well as output the coverage
# data report.
coverage:
	PYTHONDONTWRITEBYTECODE=1 uv run pytest --cov=itential_mcp --cov-report=term --cov-report=html tests/

# The check target invokes ruff to check code quality against both the library
# and test code. This target is invoked in the premerge pipeline.
check:
	PYTHONDONTWRITEBYTECODE=1 uv run ruff check src
	PYTHONDONTWRITEBYTECODE=1 uv run ruff check tests

# The lint target is an alias for the check target for backwards compatibility.
lint: check

# The format target formats code using ruff formatter on both source and test code.
format:
	PYTHONDONTWRITEBYTECODE=1 uv run ruff format src tests

# The fix target auto-fixes code quality issues where possible using ruff.
fix:
	PYTHONDONTWRITEBYTECODE=1 uv run ruff check --fix src
	PYTHONDONTWRITEBYTECODE=1 uv run ruff check --fix tests

# The security target runs bandit security analysis on the source code.
# This target is invoked in the premerge pipeline to catch security issues.
security:
	PYTHONDONTWRITEBYTECODE=1 uv run bandit -c pyproject.toml -r src/

# The premerge target will run the premerge tests locally. This is
# the same target that is invoked in the premerge pipeline.
premerge: clean format check security test

# Build a container image that includes the MCP server. The server will start
# when the container is run and can be configured using environment variables.
container:
	${CONTAINER_RUNTIME} buildx build ${PWD} --file Containerfile --tag ${CONTAINER_TAG} --platform linux/amd64,linux/arm64
