# Copyright (c) 2025 Itential, Inc
# GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)

from typing import List, Optional, Any
from pydantic import BaseModel, Field


class ProjectCreator(BaseModel):
    """Model for project creator information."""
    
    id: str = Field(alias="_id", description="Creator user ID")
    provenance: Optional[str] = Field(description="Authentication method used", default=None)
    username: Optional[str] = Field(description="Creator username", default=None)


class ProjectMetadata(BaseModel):
    """Model for project list metadata."""
    
    skip: int = Field(description="Number of items skipped")
    limit: int = Field(description="Maximum number of items returned")
    total: int = Field(description="Total number of projects")
    nextPageSkip: Optional[int] = Field(description="Skip value for next page", default=None)
    previousPageSkip: Optional[int] = Field(description="Skip value for previous page", default=None)


class ProjectSummary(BaseModel):
    """Model for project summary information."""
    
    id: str = Field(alias="_id", description="Unique project identifier")
    name: str = Field(description="Project name")
    description: str = Field(description="Project description")
    iid: int = Field(description="Project internal ID")
    createdBy: ProjectCreator = Field(description="Project creator information")
    created: str = Field(description="Project creation timestamp")
    lastUpdated: str = Field(description="Last update timestamp")


class GetProjectsResponse(BaseModel):
    """Response model for get_projects function."""
    
    message: str = Field(description="Response message")
    data: List[ProjectSummary] = Field(description="List of project summaries")
    metadata: ProjectMetadata = Field(description="Pagination and count metadata")


class Component(BaseModel):
    """Model for project component information."""
    
    iid: int = Field(description="Component internal ID")
    type: str = Field(description="Component type (e.g., workflow)")
    folder: str = Field(description="Component folder path")
    reference: str = Field(description="Component reference ID")
    document: dict = Field(description="Component document data")


class DescribeProjectResponse(BaseModel):
    """Response model for describe_project function."""
    
    message: str = Field(description="Response message")
    data: dict = Field(description="Project details including components")


class TextFSMTemplate(BaseModel):
    """TextFSM template model for parsing network device output."""

    id: str = Field(alias="_id", description="Template ID")
    name: str = Field(description="Template name")
    group: str = Field(description="Group name")
    description: str = Field(description="Template description")
    template: str = Field(description="TextFSM template body with Value definitions and state machine")
    data: str = Field(description="Sample data for testing the template")
    command: str = Field(description="Command that produces the data to parse")
    type: str = Field(default="textfsm", description="Template type (textfsm)")
    created: str = Field(description="Creation timestamp")
    lastUpdated: str = Field(description="Last update timestamp")
    createdBy: str = Field(description="Creator user ID")
    lastUpdatedBy: str = Field(description="Last updater user ID")
    tags: list[str] = Field(default_factory=list, description="Template tags")


class CreateTextFSMTemplateRequest(BaseModel):
    """Request model for creating a TextFSM template."""

    name: str = Field(description="Template name")
    group: str = Field(description="Group name")
    description: str = Field(description="Template description")
    template: str = Field(description="TextFSM template body with Value definitions and state machine")
    data: str = Field(default="", description="Sample data for testing the template")
    command: str = Field(default="", description="Command that produces the data to parse")


class CreateTextFSMTemplateResponse(BaseModel):
    """Response model for creating a TextFSM template."""

    created: TextFSMTemplate = Field(description="Created template")
    edit: str = Field(description="Edit URL for the template")


class UpdateTextFSMTemplateRequest(BaseModel):
    """Request model for updating a TextFSM template."""

    name: str = Field(description="Template name")
    group: str = Field(description="Group name")
    description: str = Field(description="Template description")
    template: str = Field(description="TextFSM template body with Value definitions and state machine")
    data: str = Field(default="", description="Sample data for testing the template")
    command: str = Field(default="", description="Command that produces the data to parse")


class UpdateTextFSMTemplateResponse(BaseModel):
    """Response model for updating a TextFSM template."""

    updated: TextFSMTemplate = Field(description="Updated template")
    edit: str = Field(description="Edit URL for the template")
