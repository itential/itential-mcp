# Copyright (c) 2025 Itential, Inc
# GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

import pytest
from unittest.mock import AsyncMock, MagicMock

from itential_mcp.tools.templates import (
    get_templates,
    describe_template,
    create_template,
    update_template,
)
from itential_mcp.models.templates import GetTemplatesElement, DescribeTemplateResponse


class TestAutomationStudioTemplates:
    """Test cases for the automation_studio_templates tool functions"""

    @pytest.fixture
    def mock_context(self):
        """Create a mock FastMCP context."""
        mock_ctx = MagicMock()
        mock_ctx.info = AsyncMock()
        mock_ctx.request_context.lifespan_context.get.return_value = MagicMock()
        return mock_ctx

    @pytest.fixture
    def mock_client(self):
        """Create a mock platform client."""
        mock_client = MagicMock()
        mock_client.automation_studio = MagicMock()
        mock_client.automation_studio.get_templates = AsyncMock()
        return mock_client

    @pytest.fixture
    def sample_templates_response(self):
        """Sample templates API response data."""
        return [
            {
                "_id": "template-textfsm-1",
                "name": "Cisco Show Version Parser",
                "description": "Parse Cisco show version output",
                "type": "textfsm",
                "group": "parsing",
                "template": "Value VERSION (\\S+)\\nStart\\n  ^.*Software.*Version ${VERSION}",
            },
            {
                "_id": "template-jinja2-1",
                "name": "Interface Configuration Generator",
                "description": "Generate interface configuration",
                "type": "jinja2",
                "group": "configuration",
                "template": "interface {{ interface }}\\n description {{ description }}",
            },
            {
                "_id": "template-textfsm-2",
                "name": "BGP Neighbor Parser",
                "description": "Parse BGP neighbor information",
                "type": "textfsm",
                "group": "parsing",
                "template": "Value NEIGHBOR (\\S+)\\nValue STATE (\\S+)",
            },
        ]

    @pytest.mark.asyncio
    async def test_get_templates_success_no_filter(
        self, mock_context, mock_client, sample_templates_response
    ):
        """Test successful retrieval of all templates without filtering."""
        mock_context.request_context.lifespan_context.get.return_value = mock_client
        mock_client.automation_studio.get_templates.return_value = (
            sample_templates_response
        )

        result = await get_templates(mock_context, template_type=None)

        # Verify service was called with correct parameters
        mock_client.automation_studio.get_templates.assert_called_once_with(
            template_type=None
        )

        # Verify context logging was called
        mock_context.info.assert_called_once_with("inside get_templates(...)")

        # Verify response structure and data
        assert isinstance(result, list)
        assert len(result) == 3

        # Check first template (TextFSM)
        assert isinstance(result[0], GetTemplatesElement)
        assert result[0].name == "Cisco Show Version Parser"
        assert result[0].description == "Parse Cisco show version output"
        assert result[0].type == "textfsm"

        # Check second template (Jinja2)
        assert isinstance(result[1], GetTemplatesElement)
        assert result[1].name == "Interface Configuration Generator"
        assert result[1].description == "Generate interface configuration"
        assert result[1].type == "jinja2"

        # Check third template (TextFSM)
        assert isinstance(result[2], GetTemplatesElement)
        assert result[2].name == "BGP Neighbor Parser"
        assert result[2].type == "textfsm"

    @pytest.mark.asyncio
    async def test_get_templates_success_textfsm_filter(
        self, mock_context, mock_client
    ):
        """Test successful retrieval of templates with textfsm filter."""
        mock_context.request_context.lifespan_context.get.return_value = mock_client

        # Mock service to return only textfsm templates
        textfsm_templates = [
            {
                "_id": "template-textfsm-1",
                "name": "Cisco Parser",
                "description": "Parse Cisco output",
                "type": "textfsm",
            },
            {
                "_id": "template-textfsm-2",
                "name": "Juniper Parser",
                "description": "Parse Juniper output",
                "type": "textfsm",
            },
        ]
        mock_client.automation_studio.get_templates.return_value = textfsm_templates

        result = await get_templates(mock_context, template_type="textfsm")

        # Verify service was called with correct filter
        mock_client.automation_studio.get_templates.assert_called_once_with(
            template_type="textfsm"
        )

        # Verify response
        assert len(result) == 2
        assert all(template.type == "textfsm" for template in result)
        assert result[0].name == "Cisco Parser"
        assert result[1].name == "Juniper Parser"

    @pytest.mark.asyncio
    async def test_get_templates_success_jinja2_filter(self, mock_context, mock_client):
        """Test successful retrieval of templates with jinja2 filter."""
        mock_context.request_context.lifespan_context.get.return_value = mock_client

        # Mock service to return only jinja2 templates
        jinja2_templates = [
            {
                "_id": "template-jinja2-1",
                "name": "Config Generator",
                "description": "Generate device configuration",
                "type": "jinja2",
            }
        ]
        mock_client.automation_studio.get_templates.return_value = jinja2_templates

        result = await get_templates(mock_context, template_type="jinja2")

        # Verify service was called with correct filter
        mock_client.automation_studio.get_templates.assert_called_once_with(
            template_type="jinja2"
        )

        # Verify response
        assert len(result) == 1
        assert result[0].type == "jinja2"
        assert result[0].name == "Config Generator"

    @pytest.mark.asyncio
    async def test_get_templates_empty_response(self, mock_context, mock_client):
        """Test handling of empty templates response."""
        mock_context.request_context.lifespan_context.get.return_value = mock_client
        mock_client.automation_studio.get_templates.return_value = []

        result = await get_templates(mock_context, template_type=None)

        # Verify service was called
        mock_client.automation_studio.get_templates.assert_called_once_with(
            template_type=None
        )

        # Verify empty response handling
        assert isinstance(result, list)
        assert len(result) == 0

    @pytest.mark.asyncio
    async def test_get_templates_missing_optional_fields(
        self, mock_context, mock_client
    ):
        """Test handling of templates with missing optional fields."""
        mock_context.request_context.lifespan_context.get.return_value = mock_client

        # Mock templates with missing optional fields (description can be None)
        templates_with_missing_fields = [
            {
                "_id": "template-minimal",
                "name": "Minimal Template",
                "type": "textfsm",
                # Missing description
            },
            {
                "_id": "template-null-desc",
                "name": "Null Description Template",
                "description": None,
                "type": "jinja2",
            },
        ]
        mock_client.automation_studio.get_templates.return_value = (
            templates_with_missing_fields
        )

        result = await get_templates(mock_context, template_type=None)

        # Verify handling of missing fields
        assert len(result) == 2

        # First template with missing description
        assert result[0].name == "Minimal Template"
        assert result[0].description is None
        assert result[0].type == "textfsm"

        # Second template with null description
        assert result[1].name == "Null Description Template"
        assert result[1].description is None
        assert result[1].type == "jinja2"

    @pytest.mark.asyncio
    async def test_get_templates_service_error_propagation(
        self, mock_context, mock_client
    ):
        """Test that service errors are properly propagated."""
        mock_context.request_context.lifespan_context.get.return_value = mock_client

        # Mock service to raise an exception
        mock_client.automation_studio.get_templates.side_effect = Exception(
            "Service unavailable"
        )

        with pytest.raises(Exception) as exc_info:
            await get_templates(mock_context, template_type=None)

        assert "Service unavailable" in str(exc_info.value)

        # Verify service was still called
        mock_client.automation_studio.get_templates.assert_called_once_with(
            template_type=None
        )

    @pytest.mark.asyncio
    async def test_get_templates_model_validation_success(
        self, mock_context, mock_client
    ):
        """Test that valid template data passes model validation."""
        mock_context.request_context.lifespan_context.get.return_value = mock_client

        valid_template = [
            {
                "_id": "valid-template",
                "name": "Valid Template",
                "description": "This is a valid template",
                "type": "textfsm",
            }
        ]
        mock_client.automation_studio.get_templates.return_value = valid_template

        result = await get_templates(mock_context, template_type="textfsm")

        # Verify model validation passed
        assert len(result) == 1
        template = result[0]
        assert isinstance(template, GetTemplatesElement)
        assert template.name == "Valid Template"
        assert template.description == "This is a valid template"
        assert template.type == "textfsm"

    @pytest.mark.asyncio
    async def test_get_templates_context_client_retrieval(self, mock_context):
        """Test proper client retrieval from context."""
        mock_client = MagicMock()
        mock_client.automation_studio.get_templates = AsyncMock(return_value=[])

        # Set up context to return our mock client
        mock_context.request_context.lifespan_context.get.return_value = mock_client

        await get_templates(mock_context, template_type=None)

        # Verify context was used to get the client
        mock_context.request_context.lifespan_context.get.assert_called_once_with(
            "client"
        )

    @pytest.mark.asyncio
    async def test_get_templates_large_response_handling(
        self, mock_context, mock_client
    ):
        """Test handling of large number of templates."""
        mock_context.request_context.lifespan_context.get.return_value = mock_client

        # Create a large response with 250 templates
        large_response = []
        for i in range(250):
            template_type = "textfsm" if i % 2 == 0 else "jinja2"
            large_response.append(
                {
                    "_id": f"template-{i}",
                    "name": f"Template {i}",
                    "description": f"Description for template {i}",
                    "type": template_type,
                }
            )

        mock_client.automation_studio.get_templates.return_value = large_response

        result = await get_templates(mock_context, template_type=None)

        # Verify large response is handled correctly
        assert len(result) == 250
        assert all(isinstance(template, GetTemplatesElement) for template in result)

        # Spot check a few templates
        assert result[0].name == "Template 0"
        assert result[0].type == "textfsm"

        assert result[249].name == "Template 249"
        assert result[249].type == "jinja2"

    @pytest.mark.asyncio
    async def test_get_templates_data_transformation(self, mock_context, mock_client):
        """Test proper data transformation from service response to model objects."""
        mock_context.request_context.lifespan_context.get.return_value = mock_client

        # Mock service response with extra fields that shouldn't be in the model
        service_response = [
            {
                "_id": "template-transform",
                "name": "Transform Test Template",
                "description": "Test data transformation",
                "type": "textfsm",
                "group": "parsing",  # Extra field
                "template": "Value TEST \\S+",  # Extra field
                "created": "2025-01-01T00:00:00Z",  # Extra field
                "lastUpdated": "2025-01-01T00:00:00Z",  # Extra field
            }
        ]
        mock_client.automation_studio.get_templates.return_value = service_response

        result = await get_templates(mock_context, template_type=None)

        # Verify transformation extracts only the model fields
        assert len(result) == 1
        template = result[0]

        # Check that only model fields are present
        assert template.name == "Transform Test Template"
        assert template.description == "Test data transformation"
        assert template.type == "textfsm"

        # Verify the model object doesn't have extra attributes
        # (Pydantic models only expose defined fields)
        assert not hasattr(template, "group")
        assert not hasattr(template, "template")
        assert not hasattr(template, "created")

    @pytest.mark.asyncio
    async def test_get_templates_mixed_types_response(self, mock_context, mock_client):
        """Test handling of mixed template types in response."""
        mock_context.request_context.lifespan_context.get.return_value = mock_client

        mixed_templates = [
            {"_id": "textfsm-1", "name": "TextFSM 1", "type": "textfsm"},
            {"_id": "jinja2-1", "name": "Jinja2 1", "type": "jinja2"},
            {"_id": "textfsm-2", "name": "TextFSM 2", "type": "textfsm"},
            {"_id": "jinja2-2", "name": "Jinja2 2", "type": "jinja2"},
        ]
        mock_client.automation_studio.get_templates.return_value = mixed_templates

        result = await get_templates(mock_context, template_type=None)

        # Verify mixed types are handled correctly
        assert len(result) == 4

        # Check types are preserved
        types = [template.type for template in result]
        assert types.count("textfsm") == 2
        assert types.count("jinja2") == 2

        # Verify specific templates
        textfsm_templates = [t for t in result if t.type == "textfsm"]
        jinja2_templates = [t for t in result if t.type == "jinja2"]

        assert len(textfsm_templates) == 2
        assert len(jinja2_templates) == 2


class TestDescribeTemplate:
    """Test cases for the describe_template tool function"""

    @pytest.fixture
    def mock_context(self):
        """Create a mock FastMCP context."""
        mock_ctx = MagicMock()
        mock_ctx.info = AsyncMock()
        mock_ctx.request_context.lifespan_context.get.return_value = MagicMock()
        return mock_ctx

    @pytest.fixture
    def mock_client(self):
        """Create a mock platform client."""
        mock_client = MagicMock()
        mock_client.automation_studio = MagicMock()
        mock_client.automation_studio.describe_template = AsyncMock()
        return mock_client

    @pytest.fixture
    def sample_template_response(self):
        """Sample template API response data."""
        return {
            "_id": "template-123",
            "name": "Cisco Show Version Parser",
            "description": "Parse Cisco show version output",
            "type": "textfsm",
            "group": "parsing",
            "command": "show version",
            "template": "Value VERSION (\\S+)\\nStart\\n  ^.*Software.*Version ${VERSION}",
            "data": "Cisco IOS Software, Version 15.1(4)M",
        }

    @pytest.mark.asyncio
    async def test_describe_template_success(
        self, mock_context, mock_client, sample_template_response
    ):
        """Test successful template description retrieval."""
        mock_context.request_context.lifespan_context.get.return_value = mock_client
        mock_client.automation_studio.describe_template.return_value = (
            sample_template_response
        )

        result = await describe_template(
            mock_context, name="test-template", project=None
        )

        # Verify service was called with correct parameters
        mock_client.automation_studio.describe_template.assert_called_once_with(
            name="test-template", project=None
        )

        # Verify context logging was called
        mock_context.info.assert_called_once_with("inside get_templates(...)")

        # Verify response structure and data
        assert isinstance(result, DescribeTemplateResponse)
        assert result.name == "Cisco Show Version Parser"
        assert result.description == "Parse Cisco show version output"
        assert result.type == "textfsm"
        assert result.group == "parsing"
        assert result.command == "show version"
        assert (
            result.template
            == "Value VERSION (\\S+)\\nStart\\n  ^.*Software.*Version ${VERSION}"
        )
        assert result.data == "Cisco IOS Software, Version 15.1(4)M"

    @pytest.mark.asyncio
    async def test_describe_template_with_project(
        self, mock_context, mock_client, sample_template_response
    ):
        """Test template description retrieval with project specified."""
        mock_context.request_context.lifespan_context.get.return_value = mock_client
        mock_client.automation_studio.describe_template.return_value = (
            sample_template_response
        )

        result = await describe_template(
            mock_context, name="test-template", project="my-project"
        )

        # Verify service was called with project parameter
        mock_client.automation_studio.describe_template.assert_called_once_with(
            name="test-template", project="my-project"
        )

        # Verify response
        assert isinstance(result, DescribeTemplateResponse)
        assert result.name == "Cisco Show Version Parser"
        assert result.type == "textfsm"

    @pytest.mark.asyncio
    async def test_describe_template_missing_optional_fields(
        self, mock_context, mock_client
    ):
        """Test handling of template with missing optional fields."""
        mock_context.request_context.lifespan_context.get.return_value = mock_client

        template_response = {
            "_id": "minimal-template",
            "name": "Minimal Template",
            "type": "jinja2",
            "group": "config",
            "command": "",
            "template": "",
            # Missing description and data fields
        }
        mock_client.automation_studio.describe_template.return_value = template_response

        result = await describe_template(
            mock_context, name="minimal-template", project=None
        )

        # Verify handling of missing fields
        assert isinstance(result, DescribeTemplateResponse)
        assert result.name == "Minimal Template"
        assert result.description is None
        assert result.type == "jinja2"
        assert result.group == "config"
        assert result.command == ""
        assert result.template == ""
        assert result.data is None

    @pytest.mark.asyncio
    async def test_describe_template_service_error_propagation(
        self, mock_context, mock_client
    ):
        """Test that service errors are properly propagated."""
        mock_context.request_context.lifespan_context.get.return_value = mock_client

        # Mock service to raise an exception
        mock_client.automation_studio.describe_template.side_effect = Exception(
            "Template not found"
        )

        with pytest.raises(Exception) as exc_info:
            await describe_template(
                mock_context, name="nonexistent-template", project=None
            )

        assert "Template not found" in str(exc_info.value)

        # Verify service was still called
        mock_client.automation_studio.describe_template.assert_called_once_with(
            name="nonexistent-template", project=None
        )


class TestCreateTemplate:
    """Test cases for the create_template tool function"""

    @pytest.fixture
    def mock_context(self):
        """Create a mock FastMCP context."""
        mock_ctx = MagicMock()
        mock_ctx.info = AsyncMock()
        mock_ctx.request_context.lifespan_context.get.return_value = MagicMock()
        return mock_ctx

    @pytest.fixture
    def mock_client(self):
        """Create a mock platform client."""
        mock_client = MagicMock()
        mock_client.automation_studio = MagicMock()
        mock_client.automation_studio.create_template = AsyncMock()
        return mock_client

    @pytest.fixture
    def sample_create_response(self):
        """Sample create template API response data."""
        return {
            "_id": "new-template-123",
            "name": "New Template",
            "description": "A new test template",
            "type": "textfsm",
            "group": "testing",
            "command": "show interfaces",
            "template": "Value INTERFACE (\\S+)",
            "data": "GigabitEthernet0/1",
        }

    @pytest.mark.asyncio
    async def test_create_template_success(
        self, mock_context, mock_client, sample_create_response
    ):
        """Test successful template creation."""
        mock_context.request_context.lifespan_context.get.return_value = mock_client
        mock_client.automation_studio.create_template.return_value = (
            sample_create_response
        )

        result = await create_template(
            ctx=mock_context,
            name="New Template",
            template_type="textfsm",
            group="testing",
            project=None,
            command="show interfaces",
            template="Value INTERFACE (\\S+)",
            data="GigabitEthernet0/1",
        )

        # Verify service was called with correct parameters
        mock_client.automation_studio.create_template.assert_called_once_with(
            name="New Template",
            template_type="textfsm",
            group="testing",
            project=None,
            command="show interfaces",
            template="Value INTERFACE (\\S+)",
            data="GigabitEthernet0/1",
        )

        # Verify context logging was called
        mock_context.info.assert_called_once_with("inside create_template(...)")

        # Verify response structure and data
        assert isinstance(result, DescribeTemplateResponse)
        assert result.name == "New Template"
        assert result.description == "A new test template"
        assert result.type == "textfsm"
        assert result.group == "testing"
        assert result.command == "show interfaces"
        assert result.template == "Value INTERFACE (\\S+)"
        assert result.data == "GigabitEthernet0/1"

    @pytest.mark.asyncio
    async def test_create_template_with_project(
        self, mock_context, mock_client, sample_create_response
    ):
        """Test template creation with project specified."""
        mock_context.request_context.lifespan_context.get.return_value = mock_client
        mock_client.automation_studio.create_template.return_value = (
            sample_create_response
        )

        result = await create_template(
            ctx=mock_context,
            name="Project Template",
            template_type="jinja2",
            group="config",
            project="my-project",
            command=None,
            template=None,
            data=None,
        )

        # Verify service was called with project parameter
        mock_client.automation_studio.create_template.assert_called_once_with(
            name="Project Template",
            template_type="jinja2",
            group="config",
            project="my-project",
            command=None,
            template=None,
            data=None,
        )

        # Verify response
        assert isinstance(result, DescribeTemplateResponse)

    @pytest.mark.asyncio
    async def test_create_template_minimal_params(
        self, mock_context, mock_client, sample_create_response
    ):
        """Test template creation with only required parameters."""
        mock_context.request_context.lifespan_context.get.return_value = mock_client
        mock_client.automation_studio.create_template.return_value = (
            sample_create_response
        )

        result = await create_template(
            ctx=mock_context,
            name="Minimal Template",
            template_type="jinja2",
            group="minimal",
            project=None,
            command=None,
            template=None,
            data=None,
        )

        # Verify service was called with minimal parameters
        mock_client.automation_studio.create_template.assert_called_once_with(
            name="Minimal Template",
            template_type="jinja2",
            group="minimal",
            project=None,
            command=None,
            template=None,
            data=None,
        )

        # Verify response
        assert isinstance(result, DescribeTemplateResponse)

    @pytest.mark.asyncio
    async def test_create_template_service_error_propagation(
        self, mock_context, mock_client
    ):
        """Test that service errors are properly propagated."""
        mock_context.request_context.lifespan_context.get.return_value = mock_client

        # Mock service to raise an exception
        mock_client.automation_studio.create_template.side_effect = Exception(
            "Template already exists"
        )

        with pytest.raises(Exception) as exc_info:
            await create_template(
                ctx=mock_context,
                name="Duplicate Template",
                template_type="textfsm",
                group="test",
                project=None,
                command=None,
                template=None,
                data=None,
            )

        assert "Template already exists" in str(exc_info.value)

        # Verify service was still called
        mock_client.automation_studio.create_template.assert_called_once()


class TestUpdateTemplate:
    """Test cases for the update_template tool function"""

    @pytest.fixture
    def mock_context(self):
        """Create a mock FastMCP context."""
        mock_ctx = MagicMock()
        mock_ctx.info = AsyncMock()
        mock_ctx.request_context.lifespan_context.get.return_value = MagicMock()
        return mock_ctx

    @pytest.fixture
    def mock_client(self):
        """Create a mock platform client."""
        mock_client = MagicMock()
        mock_client.automation_studio = MagicMock()
        mock_client.automation_studio.update_template = AsyncMock()
        return mock_client

    @pytest.fixture
    def sample_update_response(self):
        """Sample update template API response data."""
        return {
            "_id": "updated-template-123",
            "name": "Updated Template",
            "description": "An updated test template",
            "type": "textfsm",
            "group": "updated",
            "command": "show ip interface brief",
            "template": "Value INTERFACE (\\S+)\\nValue STATUS (\\S+)",
            "data": "GigabitEthernet0/1 10.1.1.1 up",
        }

    @pytest.mark.asyncio
    async def test_update_template_success(
        self, mock_context, mock_client, sample_update_response
    ):
        """Test successful template update."""
        mock_context.request_context.lifespan_context.get.return_value = mock_client
        mock_client.automation_studio.update_template.return_value = (
            sample_update_response
        )

        result = await update_template(
            ctx=mock_context,
            name="Updated Template",
            project=None,
            command="show ip interface brief",
            template="Value INTERFACE (\\S+)\\nValue STATUS (\\S+)",
            data="GigabitEthernet0/1 10.1.1.1 up",
        )

        # Verify service was called with correct parameters
        mock_client.automation_studio.update_template.assert_called_once_with(
            name="Updated Template",
            project=None,
            command="show ip interface brief",
            template="Value INTERFACE (\\S+)\\nValue STATUS (\\S+)",
            data="GigabitEthernet0/1 10.1.1.1 up",
        )

        # Verify context logging was called
        mock_context.info.assert_called_once_with("inside update_template(...)")

        # Verify response structure and data
        assert isinstance(result, DescribeTemplateResponse)
        assert result.name == "Updated Template"
        assert result.description == "An updated test template"
        assert result.type == "textfsm"
        assert result.group == "updated"
        assert result.command == "show ip interface brief"
        assert result.template == "Value INTERFACE (\\S+)\\nValue STATUS (\\S+)"
        assert result.data == "GigabitEthernet0/1 10.1.1.1 up"

    @pytest.mark.asyncio
    async def test_update_template_with_project(
        self, mock_context, mock_client, sample_update_response
    ):
        """Test template update with project specified."""
        mock_context.request_context.lifespan_context.get.return_value = mock_client
        mock_client.automation_studio.update_template.return_value = (
            sample_update_response
        )

        result = await update_template(
            ctx=mock_context,
            name="Project Template",
            project="my-project",
            command="show version",
            template=None,
            data=None,
        )

        # Verify service was called with project parameter
        mock_client.automation_studio.update_template.assert_called_once_with(
            name="Project Template",
            project="my-project",
            command="show version",
            template=None,
            data=None,
        )

        # Verify response
        assert isinstance(result, DescribeTemplateResponse)

    @pytest.mark.asyncio
    async def test_update_template_partial_update(
        self, mock_context, mock_client, sample_update_response
    ):
        """Test template update with only some fields."""
        mock_context.request_context.lifespan_context.get.return_value = mock_client
        mock_client.automation_studio.update_template.return_value = (
            sample_update_response
        )

        result = await update_template(
            ctx=mock_context,
            name="Partial Template",
            project=None,
            command="show interfaces",
            template=None,
            data=None,
        )

        # Verify service was called with only specified parameters
        mock_client.automation_studio.update_template.assert_called_once_with(
            name="Partial Template",
            project=None,
            command="show interfaces",
            template=None,
            data=None,
        )

        # Verify response
        assert isinstance(result, DescribeTemplateResponse)

    @pytest.mark.asyncio
    async def test_update_template_service_error_propagation(
        self, mock_context, mock_client
    ):
        """Test that service errors are properly propagated."""
        mock_context.request_context.lifespan_context.get.return_value = mock_client

        # Mock service to raise an exception
        mock_client.automation_studio.update_template.side_effect = Exception(
            "Template not found"
        )

        with pytest.raises(Exception) as exc_info:
            await update_template(
                ctx=mock_context,
                name="Nonexistent Template",
                project=None,
                command="show version",
                template=None,
                data=None,
            )

        assert "Template not found" in str(exc_info.value)

        # Verify service was still called
        mock_client.automation_studio.update_template.assert_called_once()
