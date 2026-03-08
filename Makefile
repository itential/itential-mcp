# !make

# Copyright 2025 Itential Inc. All Rights Reserved
# GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

# ==============================================================================
# Itential MCP — MCP server for the Itential Platform
# ==============================================================================
# Usage:
#   make              Show help
#   make build        Set up local development environment
#   make ci           Run full CI pipeline locally
#
# Dependencies:
#   - uv  (https://github.com/astral-sh/uv)
#   - docker or podman  (for the container target)
# ==============================================================================

SHELL := bash
.SHELLFLAGS := -eu -o pipefail -c
.DEFAULT_GOAL := help
.DELETE_ON_ERROR:

# ------------------------------------------------------------------------------
# Configuration
# ------------------------------------------------------------------------------

CONTAINER_RUNTIME ?= docker
CONTAINER_TAG     ?= itential-mcp:devel

PKG_NAME := itential_mcp
SRC_DIR  := src
TEST_DIR := tests

# Set once — inherited by all recipe subshells, no per-target repetition needed.
export PYTHONDONTWRITEBYTECODE := 1

# ------------------------------------------------------------------------------
# .PHONY declarations
# ------------------------------------------------------------------------------

.PHONY: build certs check check-headers clean clean-venv container coverage \
        fix fix-headers format lint ci run security test \
        tox tox-py310 tox-py311 tox-py312 tox-py313 \
        tox-coverage tox-format tox-lint tox-list tox-ci tox-security \
        help

# ------------------------------------------------------------------------------
# Build / Setup
# ------------------------------------------------------------------------------

build: ## Set up local development environment
	uv sync

run: ## Run the MCP server locally (stdio transport)
	uv run itential-mcp run

# ------------------------------------------------------------------------------
# Test & Quality
# ------------------------------------------------------------------------------

test: ## Run test suite
	uv run pytest $(TEST_DIR) -v -s

coverage: ## Run tests with HTML and terminal coverage report
	uv run pytest --cov=$(PKG_NAME) --cov-report=term --cov-report=html $(TEST_DIR)/

check: ## Lint source and test code with ruff (read-only)
	uv run ruff check $(SRC_DIR) $(TEST_DIR)

lint: check ## Alias for check (backwards compatibility)

format: ## Format source and test code with ruff
	uv run ruff format $(SRC_DIR) $(TEST_DIR)

fix: ## Auto-fix linting issues where possible
	uv run ruff check --fix $(SRC_DIR) $(TEST_DIR)

security: ## Run security analysis with bandit
	uv run bandit -c pyproject.toml -r $(SRC_DIR)/

check-headers: ## Verify copyright headers in all Python files
	uv run python scripts/check_headers.py

fix-headers: ## Add missing copyright headers to Python files
	uv run python scripts/check_headers.py --fix

ci: clean format check check-headers security test ## Run full CI pipeline locally (mirrors CI)

# ------------------------------------------------------------------------------
# Container
# ------------------------------------------------------------------------------

container: ## Build multi-arch container image (amd64 + arm64)
	$(CONTAINER_RUNTIME) buildx build $(PWD) \
		--file Containerfile \
		--tag $(CONTAINER_TAG) \
		--platform linux/amd64,linux/arm64

# ------------------------------------------------------------------------------
# Tox (multi-version testing)
# ------------------------------------------------------------------------------

tox: ## Run tests across all supported Python versions (3.10-3.13)
	uv run tox

tox-py310: ## Run tests with Python 3.10
	uv run tox -e py310

tox-py311: ## Run tests with Python 3.11
	uv run tox -e py311

tox-py312: ## Run tests with Python 3.12
	uv run tox -e py312

tox-py313: ## Run tests with Python 3.13
	uv run tox -e py313

tox-coverage: ## Run tests with coverage report via tox
	uv run tox -e coverage

tox-lint: ## Run linting checks via tox
	uv run tox -e lint

tox-format: ## Format code via tox
	uv run tox -e format

tox-security: ## Run security analysis via tox
	uv run tox -e security

tox-ci: ## Run full CI pipeline via tox
	uv run tox -e premerge

tox-list: ## List all available tox environments
	uv run tox list

# ------------------------------------------------------------------------------
# Development
# ------------------------------------------------------------------------------

certs: ## Generate self-signed certificates for local development
	@scripts/makecerts.sh

# ------------------------------------------------------------------------------
# Housekeeping
# ------------------------------------------------------------------------------

clean: ## Remove build artifacts, caches, and coverage reports
	@rm -rf .pytest_cache coverage.* htmlcov dist build *.egg-info certificates
	@find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true

clean-venv: clean ## Full reset — also removes the virtual environment
	@rm -rf .venv

# ------------------------------------------------------------------------------
# Help
# ------------------------------------------------------------------------------

help: ## Show this help message
	@echo "Usage: make <target>"
	@echo ""
	@grep -E '^[a-zA-Z0-9_/-]+:.*##' $(MAKEFILE_LIST) \
		| awk 'BEGIN {FS = ":.*##"}; {printf "  \033[36m%-20s\033[0m %s\n", $$1, $$2}' \
		| sort
	@echo ""
