# Copyright (c) 2025 Itential, Inc
# GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

import pytest
from pydantic import ValidationError

from itential_mcp.models.templates import GetTemplatesElement, GetTemplatesResponse


class TestGetTemplatesElement:
    """Test cases for GetTemplatesElement model"""

    def test_templates_element_valid_textfsm_creation(self):
        """Test creating GetTemplatesElement with valid textfsm data"""
        element = GetTemplatesElement(
            name="cisco-show-version",
            description="Parse Cisco show version output",
            type="textfsm",
        )

        assert element.name == "cisco-show-version"
        assert element.description == "Parse Cisco show version output"
        assert element.type == "textfsm"

    def test_templates_element_valid_jinja2_creation(self):
        """Test creating GetTemplatesElement with valid jinja2 data"""
        element = GetTemplatesElement(
            name="interface-config",
            description="Generate interface configuration",
            type="jinja2",
        )

        assert element.name == "interface-config"
        assert element.description == "Generate interface configuration"
        assert element.type == "jinja2"

    def test_templates_element_optional_description(self):
        """Test GetTemplatesElement with optional description field"""
        element = GetTemplatesElement(name="no-desc-template", type="textfsm")

        assert element.name == "no-desc-template"
        assert element.description is None
        assert element.type == "textfsm"

    def test_templates_element_none_description(self):
        """Test GetTemplatesElement with explicitly None description"""
        element = GetTemplatesElement(
            name="explicit-none-template", description=None, type="jinja2"
        )

        assert element.name == "explicit-none-template"
        assert element.description is None
        assert element.type == "jinja2"

    def test_templates_element_missing_required_fields(self):
        """Test GetTemplatesElement validation with missing required fields"""
        # Missing name
        with pytest.raises(ValidationError) as exc_info:
            GetTemplatesElement(description="Missing name field", type="jinja2")

        error = exc_info.value
        assert "name" in str(error)

        # Missing type
        with pytest.raises(ValidationError) as exc_info:
            GetTemplatesElement(
                name="missing-type-template", description="Missing type field"
            )

        error = exc_info.value
        assert "type" in str(error)

    def test_templates_element_invalid_type(self):
        """Test GetTemplatesElement validation with invalid type"""
        with pytest.raises(ValidationError) as exc_info:
            GetTemplatesElement(
                name="invalid-type-template",
                description="Invalid type",
                type="invalid_type",
            )

        error = exc_info.value
        assert "type" in str(error)

    def test_templates_element_empty_strings(self):
        """Test GetTemplatesElement with empty string values"""
        element = GetTemplatesElement(name="", description="", type="textfsm")

        assert element.name == ""
        assert element.description == ""
        assert element.type == "textfsm"

    def test_templates_element_serialization_textfsm(self):
        """Test GetTemplatesElement model serialization for textfsm"""
        element = GetTemplatesElement(
            name="serialization-template",
            description="Template for testing serialization",
            type="textfsm",
        )

        data = element.model_dump()
        expected = {
            "name": "serialization-template",
            "description": "Template for testing serialization",
            "type": "textfsm",
        }

        assert data == expected

    def test_templates_element_serialization_jinja2(self):
        """Test GetTemplatesElement model serialization for jinja2"""
        element = GetTemplatesElement(
            name="jinja2-template", description="Jinja2 template test", type="jinja2"
        )

        data = element.model_dump()
        expected = {
            "name": "jinja2-template",
            "description": "Jinja2 template test",
            "type": "jinja2",
        }

        assert data == expected

    def test_templates_element_serialization_no_description(self):
        """Test GetTemplatesElement model serialization without description"""
        element = GetTemplatesElement(name="no-description-template", type="textfsm")

        data = element.model_dump()
        expected = {
            "name": "no-description-template",
            "description": None,
            "type": "textfsm",
        }

        assert data == expected

    def test_templates_element_deserialization(self):
        """Test GetTemplatesElement model deserialization"""
        data = {
            "name": "deserialization-template",
            "description": "Template for testing deserialization",
            "type": "jinja2",
        }

        element = GetTemplatesElement(**data)

        assert element.name == "deserialization-template"
        assert element.description == "Template for testing deserialization"
        assert element.type == "jinja2"

    def test_templates_element_deserialization_missing_description(self):
        """Test GetTemplatesElement model deserialization without description"""
        data = {"name": "no-desc-deserialize", "type": "textfsm"}

        element = GetTemplatesElement(**data)

        assert element.name == "no-desc-deserialize"
        assert element.description is None
        assert element.type == "textfsm"


class TestGetTemplatesResponse:
    """Test cases for GetTemplatesResponse model"""

    def test_templates_response_valid_creation(self):
        """Test creating GetTemplatesResponse with valid data"""
        templates = [
            GetTemplatesElement(
                name="first-template", description="First test template", type="textfsm"
            ),
            GetTemplatesElement(
                name="second-template",
                description="Second test template",
                type="jinja2",
            ),
        ]

        response = GetTemplatesResponse(root=templates)

        assert len(response.root) == 2
        assert response.root[0].name == "first-template"
        assert response.root[0].type == "textfsm"
        assert response.root[1].name == "second-template"
        assert response.root[1].type == "jinja2"

    def test_templates_response_empty_list(self):
        """Test GetTemplatesResponse with empty template list"""
        response = GetTemplatesResponse(root=[])

        assert response.root == []
        assert len(response.root) == 0

    def test_templates_response_single_template(self):
        """Test GetTemplatesResponse with single template"""
        template = GetTemplatesElement(
            name="single", description="Single template test", type="textfsm"
        )

        response = GetTemplatesResponse(root=[template])

        assert len(response.root) == 1
        assert response.root[0].name == "single"
        assert response.root[0].type == "textfsm"

    def test_templates_response_mixed_types(self):
        """Test GetTemplatesResponse with mixed template types"""
        templates = [
            GetTemplatesElement(name="textfsm-template", type="textfsm"),
            GetTemplatesElement(name="jinja2-template", type="jinja2"),
            GetTemplatesElement(name="another-textfsm", type="textfsm"),
        ]

        response = GetTemplatesResponse(root=templates)

        assert len(response.root) == 3
        assert response.root[0].type == "textfsm"
        assert response.root[1].type == "jinja2"
        assert response.root[2].type == "textfsm"

    def test_templates_response_serialization(self):
        """Test GetTemplatesResponse model serialization"""
        templates = [
            GetTemplatesElement(name="serialize-first", type="textfsm"),
            GetTemplatesElement(
                name="serialize-second", description="Has description", type="jinja2"
            ),
        ]

        response = GetTemplatesResponse(root=templates)
        data = response.model_dump()

        assert isinstance(data, list)
        assert len(data) == 2
        assert data[0]["name"] == "serialize-first"
        assert data[0]["type"] == "textfsm"
        assert data[1]["description"] == "Has description"
        assert data[1]["type"] == "jinja2"

    def test_templates_response_deserialization(self):
        """Test GetTemplatesResponse model deserialization"""
        data = [
            {
                "name": "first-deserialize",
                "description": "First deserialization test",
                "type": "textfsm",
            },
            {"name": "second-deserialize", "type": "jinja2"},
        ]

        response = GetTemplatesResponse(root=data)

        assert len(response.root) == 2
        assert response.root[0].name == "first-deserialize"
        assert response.root[0].type == "textfsm"
        assert response.root[0].description == "First deserialization test"
        assert response.root[1].name == "second-deserialize"
        assert response.root[1].type == "jinja2"
        assert response.root[1].description is None

    def test_templates_response_validation_error(self):
        """Test GetTemplatesResponse validation with invalid template data"""
        invalid_templates = [
            {"name": "valid-name", "type": "textfsm"},
            {
                "name": "invalid-name",
                "type": "invalid_type",  # Invalid type
            },
        ]

        with pytest.raises(ValidationError) as exc_info:
            GetTemplatesResponse(root=invalid_templates)

        error = exc_info.value
        assert "type" in str(error)
