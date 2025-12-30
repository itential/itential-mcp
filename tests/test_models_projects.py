# Copyright (c) 2025 Itential, Inc
# GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

import pytest
from pydantic import ValidationError

from itential_mcp.models.projects import (
    GetProjectsElement,
    GetProjectsResponse,
    DescribeProjectComponent,
    DescribeProjectResponse,
)


class TestGetProjectsElement:
    """Test cases for GetProjectsElement model"""

    def test_projects_element_valid_creation(self):
        """Test creating GetProjectsElement with valid data"""
        element = GetProjectsElement(
            id="project-123",
            name="test-project",
            description="Test project for unit testing",
        )

        assert element.id == "project-123"
        assert element.name == "test-project"
        assert element.description == "Test project for unit testing"

    def test_projects_element_optional_description(self):
        """Test GetProjectsElement with optional description field"""
        element = GetProjectsElement(id="project-456", name="no-desc-project")

        assert element.id == "project-456"
        assert element.name == "no-desc-project"
        assert element.description is None

    def test_projects_element_none_description(self):
        """Test GetProjectsElement with explicitly None description"""
        element = GetProjectsElement(
            id="project-789", name="explicit-none-project", description=None
        )

        assert element.id == "project-789"
        assert element.name == "explicit-none-project"
        assert element.description is None

    def test_projects_element_missing_required_field(self):
        """Test GetProjectsElement validation with missing required fields"""
        with pytest.raises(ValidationError) as exc_info:
            GetProjectsElement(
                name="missing-id-project", description="Missing ID field"
            )

        error = exc_info.value
        assert "id" in str(error)

        with pytest.raises(ValidationError) as exc_info:
            GetProjectsElement(id="project-999", description="Missing name field")

        error = exc_info.value
        assert "name" in str(error)

    def test_projects_element_empty_strings(self):
        """Test GetProjectsElement with empty string values"""
        element = GetProjectsElement(id="", name="", description="")

        assert element.id == ""
        assert element.name == ""
        assert element.description == ""

    def test_projects_element_serialization(self):
        """Test GetProjectsElement model serialization"""
        element = GetProjectsElement(
            id="serialize-test",
            name="serialization-project",
            description="Project for testing serialization",
        )

        data = element.model_dump()
        expected = {
            "id": "serialize-test",
            "name": "serialization-project",
            "description": "Project for testing serialization",
        }

        assert data == expected

    def test_projects_element_deserialization(self):
        """Test GetProjectsElement model deserialization"""
        data = {
            "id": "deserialize-test",
            "name": "deserialization-project",
            "description": "Project for testing deserialization",
        }

        element = GetProjectsElement(**data)

        assert element.id == "deserialize-test"
        assert element.name == "deserialization-project"
        assert element.description == "Project for testing deserialization"


class TestGetProjectsResponse:
    """Test cases for GetProjectsResponse model"""

    def test_projects_response_valid_creation(self):
        """Test creating GetProjectsResponse with valid data"""
        projects = [
            GetProjectsElement(
                id="project-1", name="first-project", description="First test project"
            ),
            GetProjectsElement(
                id="project-2", name="second-project", description="Second test project"
            ),
        ]

        response = GetProjectsResponse(root=projects)

        assert len(response.root) == 2
        assert response.root[0].id == "project-1"
        assert response.root[1].id == "project-2"

    def test_projects_response_empty_list(self):
        """Test GetProjectsResponse with empty project list"""
        response = GetProjectsResponse(root=[])

        assert response.root == []
        assert len(response.root) == 0

    def test_projects_response_single_project(self):
        """Test GetProjectsResponse with single project"""
        project = GetProjectsElement(
            id="single-project", name="single", description="Single project test"
        )

        response = GetProjectsResponse(root=[project])

        assert len(response.root) == 1
        assert response.root[0].id == "single-project"

    def test_projects_response_serialization(self):
        """Test GetProjectsResponse model serialization"""
        projects = [
            GetProjectsElement(id="serial-1", name="serialize-first"),
            GetProjectsElement(
                id="serial-2", name="serialize-second", description="Has description"
            ),
        ]

        response = GetProjectsResponse(root=projects)
        data = response.model_dump()

        assert isinstance(data, list)
        assert len(data) == 2
        assert data[0]["id"] == "serial-1"
        assert data[1]["description"] == "Has description"


class TestDescribeProjectComponent:
    """Test cases for DescribeProjectComponent model"""

    def test_component_valid_creation(self):
        """Test creating DescribeProjectComponent with valid data"""
        component = DescribeProjectComponent(
            id="component-123",
            name="test-workflow",
            type="workflow",
            folder="/workflows",
        )

        assert component.id == "component-123"
        assert component.name == "test-workflow"
        assert component.type == "workflow"
        assert component.folder == "/workflows"

    def test_component_different_types(self):
        """Test DescribeProjectComponent with different component types"""
        workflow_comp = DescribeProjectComponent(
            id="wf-1", name="my-workflow", type="workflow", folder="/workflows"
        )

        template_comp = DescribeProjectComponent(
            id="tmpl-1", name="my-template", type="template", folder="/templates"
        )

        assert workflow_comp.type == "workflow"
        assert template_comp.type == "template"

    def test_component_missing_required_fields(self):
        """Test DescribeProjectComponent validation with missing fields"""
        with pytest.raises(ValidationError):
            DescribeProjectComponent(name="incomplete", type="workflow", folder="/test")

        with pytest.raises(ValidationError):
            DescribeProjectComponent(id="comp-1", type="workflow", folder="/test")

    def test_component_serialization(self):
        """Test DescribeProjectComponent model serialization"""
        component = DescribeProjectComponent(
            id="serial-comp",
            name="serialize-test",
            type="template",
            folder="/templates/test",
        )

        data = component.model_dump()
        expected = {
            "id": "serial-comp",
            "name": "serialize-test",
            "type": "template",
            "folder": "/templates/test",
        }

        assert data == expected


class TestDescribeProjectResponse:
    """Test cases for DescribeProjectResponse model"""

    def test_describe_response_valid_creation(self):
        """Test creating DescribeProjectResponse with valid data"""
        components = [
            DescribeProjectComponent(
                id="comp-1", name="workflow-1", type="workflow", folder="/workflows"
            ),
            DescribeProjectComponent(
                id="comp-2", name="template-1", type="template", folder="/templates"
            ),
        ]

        response = DescribeProjectResponse(
            id="describe-project",
            name="describe-test",
            description="Project for describe testing",
            components=components,
        )

        assert response.id == "describe-project"
        assert response.name == "describe-test"
        assert response.description == "Project for describe testing"
        assert len(response.components) == 2
        assert response.components[0].type == "workflow"
        assert response.components[1].type == "template"

    def test_describe_response_empty_components(self):
        """Test DescribeProjectResponse with empty components list"""
        response = DescribeProjectResponse(
            id="empty-comp-project",
            name="empty-components",
            description="No components",
            components=[],
        )

        assert response.components == []
        assert len(response.components) == 0

    def test_describe_response_inheritance(self):
        """Test that DescribeProjectResponse inherits from GetProjectsElement"""
        response = DescribeProjectResponse(
            id="inherit-test", name="inheritance-project", components=[]
        )

        assert isinstance(response, GetProjectsElement)
        assert response.id == "inherit-test"
        assert response.name == "inheritance-project"
        assert response.description is None

    def test_describe_response_serialization(self):
        """Test DescribeProjectResponse model serialization"""
        components = [
            DescribeProjectComponent(
                id="serial-comp", name="serial-workflow", type="workflow", folder="/wf"
            )
        ]

        response = DescribeProjectResponse(
            id="serial-project",
            name="serialization-test",
            description="Serialization testing",
            components=components,
        )

        data = response.model_dump()

        assert data["id"] == "serial-project"
        assert data["name"] == "serialization-test"
        assert data["description"] == "Serialization testing"
        assert len(data["components"]) == 1
        assert data["components"][0]["type"] == "workflow"
