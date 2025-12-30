# Copyright (c) 2025 Itential, Inc
# GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import annotations

import inspect

from typing import Annotated

from pydantic import BaseModel, Field


class CompliancePlan(BaseModel):
    """Represents a compliance plan from the Itential platform.

    This model defines the structure for compliance plan information
    returned from the Configuration Manager API endpoints. Compliance plans
    define configuration validation rules and checks that can be executed
    against network devices to ensure they meet organizational standards.

    Attributes:
        id: Unique identifier for the compliance plan.
        name: The compliance plan name.
        description: A description of the compliance plan.
        throttle: Number of devices checked in parallel during execution.
    """

    id: Annotated[
        str,
        Field(
            description=inspect.cleandoc(
                """
                Unique identifier for the compliance plan
                """
            )
        ),
    ]

    name: Annotated[
        str,
        Field(
            description=inspect.cleandoc(
                """
                Compliance plan name
                """
            )
        ),
    ]

    description: Annotated[
        str,
        Field(
            description=inspect.cleandoc(
                """
                Plan description
                """
            )
        ),
    ]

    throttle: Annotated[
        int,
        Field(
            description=inspect.cleandoc(
                """
                Number of devices checked in parallel during execution
                """
            )
        ),
    ]


class GetCompliancePlansResponse(BaseModel):
    """Response model for get_compliance_plans function.

    This model represents the list of compliance plans returned by the
    get_compliance_plans function from the Configuration Manager.

    Attributes:
        plans: List of compliance plan objects.
    """

    plans: Annotated[
        list[CompliancePlan],
        Field(
            description=inspect.cleandoc(
                """
                List of compliance plan objects
                """
            )
        ),
    ]


class CompliancePlanInstance(BaseModel):
    """Represents a running compliance plan instance from the Itential platform.

    This model defines the structure for a compliance plan instance that
    is created when a compliance plan is executed. It contains the runtime
    information and current status of the execution.

    Attributes:
        id: Unique identifier for this compliance plan instance.
        name: Name of the compliance plan that was started.
        description: Compliance plan description.
        jobStatus: Current execution status of the compliance plan instance.
    """

    id: Annotated[
        str,
        Field(
            description=inspect.cleandoc(
                """
                Unique identifier for this compliance plan instance
                """
            )
        ),
    ]

    name: Annotated[
        str,
        Field(
            description=inspect.cleandoc(
                """
                Name of the compliance plan that was started
                """
            )
        ),
    ]

    description: Annotated[
        str,
        Field(
            description=inspect.cleandoc(
                """
                Compliance plan description
                """
            )
        ),
    ]

    jobStatus: Annotated[
        str,
        Field(
            description=inspect.cleandoc(
                """
                Current execution status of the compliance plan instance
                """
            )
        ),
    ]


class RunCompliancePlanResponse(BaseModel):
    """Response model for run_compliance_plan function.

    This model represents the running compliance plan instance returned by the
    run_compliance_plan function from the Configuration Manager.

    Attributes:
        instance: The running compliance plan instance details.
    """

    instance: Annotated[
        CompliancePlanInstance,
        Field(
            description=inspect.cleandoc(
                """
                Running compliance plan instance details
                """
            )
        ),
    ]
