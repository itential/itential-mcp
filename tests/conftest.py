# Copyright (c) 2025 Itential, Inc
# GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

"""Shared pytest fixtures for the itential-mcp test suite."""

import os

import pytest


@pytest.fixture(autouse=True)
def _isolate_environ():
    """
    Snapshot and restore os.environ around every test.

    Several code paths under test (notably runtime.parser's
    _set_environment_variables, exercised end to end by CLI tests that call
    app.run() for real) write ITENTIAL_MCP_* keys directly into the real
    process os.environ as a side effect, with no corresponding cleanup.
    Without this fixture, those writes leak across tests and pollute
    anything that inspects os.environ afterward -- e.g. runtime.parser's
    env-configured-without-subcommand detection, which scans os.environ for
    any ITENTIAL_MCP_* prefix.

    monkeypatch.setenv/delenv only restore keys they were explicitly asked
    to change, so they don't cover this case; a full snapshot/restore does.

    Args:
        None

    Returns:
        None

    Raises:
        None
    """
    snapshot = dict(os.environ)
    try:
        yield
    finally:
        os.environ.clear()
        os.environ.update(snapshot)
