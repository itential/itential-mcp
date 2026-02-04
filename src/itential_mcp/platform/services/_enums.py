# Copyright (c) 2025 Itential, Inc
# GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

"""Enumerations for Itential Platform service states and types.

This module provides type-safe enumerations for various states and types
used across the platform services, reducing the risk of typos and improving
code maintainability.
"""

from enum import Enum


class AdapterState(str, Enum):
    """Valid adapter states in Itential Platform.

    Adapters can be in one of these states during their lifecycle.
    These states represent the operational status of an adapter instance.
    """

    RUNNING = "RUNNING"
    STOPPED = "STOPPED"
    DEAD = "DEAD"
    DELETED = "DELETED"
    STARTING = "STARTING"
    STOPPING = "STOPPING"


class ApplicationState(str, Enum):
    """Valid application states in Itential Platform.

    Applications can be in one of these states during their lifecycle.
    These states represent the operational status of an application instance.
    """

    RUNNING = "RUNNING"
    STOPPED = "STOPPED"
    DEAD = "DEAD"
    DELETED = "DELETED"
    STARTING = "STARTING"
    STOPPING = "STOPPING"
