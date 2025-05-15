# Copyright (c) 2025 Itential, Inc
# GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)

# Create the builder container
FROM ghcr.io/astral-sh/uv:python3.10-bookworm-slim AS builder

# Install the project into `/app`
WORKDIR /app

# Enable bytecode compilation
ENV UV_COMPILE_BYTECODE=1

# Copy from the cache instead of linking since it's a mounted volume
ENV UV_LINK_MODE=copy

# Generate uv lock file
RUN --mount=type=bind,source=pyproject.toml,target=pyproject.toml  \
    --mount=type=bind,source=README.md,target=README.md,relabel=shared  \
    uv lock

# Install the project's dependencies using the lockfile
RUN --mount=type=bind,source=pyproject.toml,target=pyproject.toml \
    --mount=type=bind,source=uv.lock,target=uv.lock,relabel=shared \
    uv sync --frozen --no-install-project --no-dev --no-editable

# Then, add the rest of the project source code and install it
ADD . /app
RUN --mount=type=bind,source=uv.lock,target=uv.lock \
    uv sync --frozen --no-dev --no-editable


# Create the final container with the application installed
FROM python:3.10-slim

WORKDIR /app

#COPY --from=builder --chown=app:app /app/.venv /app/.venv
COPY --from=builder /app/.venv /app/.venv

# Place executables in the environment at the front of the path
ENV PATH="/app/.venv/bin:$PATH"

ENTRYPOINT ["itential-mcp"]
