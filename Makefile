# !make

# Copyright 2025 Itential Inc. All Rights Reserved
# GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)

CONTAINER_RUNTIME ?= docker
CONTAINER_TAG ?= itential-mcp:devel

.DEFAULT_GOAL := help

.PHONY: build clean container coverage lint security permerge test

# The help target displays a help message that includes the avialable targets
# in this `Makefile`.  It is the default target if `make` is run without any
# parameters.
help:
	@echo "Available targets:"
	@echo "  build      - Build the local development environment"
	@echo "  clean      - Cleans the development environment"
	@echo "  container  - Builds the the application as a container"
	@echo "  coverage   - Run test coverage report"
	@echo "  lint       - Run analysis on source files"
	@echo "  security   - Run security analysis with bandit"
	@echo "  premerge   - Run the permerge tests locallly"
	@echo "  test       - Run test suite"
	@echo ""

# The test target will invoke the unit tests using pytest.   This target
# requires uv to be installed and the environment created.
test:
	uv run pytest tests -v -s

# Builds the local environment which can be used for development or simply
# running the server from source.  This target requires `uv` to be installed
# and available in the system path.
build:
	uv sync

# The coverage target will invoke pytest with coverage support.  It will
# display a summary of the unit test coverage as well as output the coverage
# data report
coverage:
	uv run pytest --cov=itential_mcp --cov-report=term --cov-report=html tests/

# The lint target invokes ruff to run the linter against both the library
# and test code.   This target is invoked in the premerge pipeline.
lint:
	uv run ruff check src
	uv run ruff check tests

# The security target runs bandit security analysis on the source code.
# This target is invoked in the premerge pipeline to catch security issues.
security:
	uv run bandit -c pyproject.toml -r src/

# The clean target will remove build and dev artififacts that are not 
# part of the application and get created by other targets.
clean:
	@rm -rf .pytest_cache coverage.* htmlcov dist build *.egg-info
	@find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true

# The premerge target will run the permerge tests locally.  This is
# the same target that is invoked in the permerge pipeline.
premerge: clean lint security test

# Build a container image that include the MCP server.  The server will start
# when the container is run and can be configured using environment variables
container:
	${CONTAINER_RUNTIME} build ${PWD} --file Containerfile --tag ${CONTAINER_TAG}
