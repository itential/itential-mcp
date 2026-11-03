# Copyright (c) 2025 Itential, Inc
# GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import annotations

from pydantic import BaseModel, ConfigDict


class AliasedModel(BaseModel):
    """Base class for response models that declare field aliases.

    The JSON output schema generated for each tool is built with
    ``model_json_schema()`` (by alias), so the schema requires the alias
    names (e.g. ``freemem``, ``_id``). FastMCP 4 serializes structured
    content by field name unless the model opts in to alias serialization,
    which makes aliased models fail output validation. Setting
    ``serialize_by_alias`` keeps the wire keys identical to FastMCP 3, and
    ``populate_by_name`` lets callers construct models by either name.

    Pydantic does not propagate this setting to nested models, so every
    model that owns an aliased field must inherit from this class.
    """

    model_config = ConfigDict(populate_by_name=True, serialize_by_alias=True)
