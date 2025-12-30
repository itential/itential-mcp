# Copyright (c) 2025 Itential, Inc
# GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import annotations

import inspect

from typing import Annotated, Any

from pydantic import BaseModel, Field


class DescribeComplianceReportResponse(BaseModel):
    """
    Response model for describing a compliance report.

    This model represents the detailed compliance report results from Itential Platform,
    containing validation results, device compliance status, rule violations, and
    configuration analysis from running compliance checks against network infrastructure.
    """

    result: Annotated[
        dict[str, Any],
        Field(
            description=inspect.cleandoc(
                """
                Compliance report details containing validation results,
                device compliance status, rule violations, and configuration
                analysis
                """
            )
        ),
    ]
