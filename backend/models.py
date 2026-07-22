"""Pydantic data models for DevSkillMapper."""

from typing import Optional
from pydantic import BaseModel, Field


class RepoRequest(BaseModel):
    """Input: full repository name like 'facebook/react'."""
    repo_full_name: str = Field(
        ...,
        pattern=r"^[a-zA-Z0-9_.-]+/[a-zA-Z0-9_.-]+$",
        description="Repository full name, e.g. facebook/react",
    )


class HealthScores(BaseModel):
    """Six-dimensional health scoring model."""
    activity: float = Field(ge=0, le=100, description="Activity score based on commits and recency")
    community: float = Field(ge=0, le=100, description="Community health based on issue/PR closure rates")
    documentation: float = Field(ge=0, le=100, description="Documentation quality based on README, CONTRIBUTING, License")
    scale: float = Field(ge=0, le=100, description="Code scale based on languages and total size")
    stability: float = Field(ge=0, le=100, description="Stability based on tags and releases")
    impact: float = Field(ge=0, le=100, description="Community impact based on stars/forks/watchers")


class RepoAnalysis(BaseModel):
    """Complete repository analysis output."""
    full_name: str
    description: Optional[str] = None
    stars: int = 0
    forks: int = 0
    watchers: int = 0
    open_issues: int = 0
    language: Optional[str] = None
    languages: dict = Field(default_factory=dict)
    topics: list[str] = Field(default_factory=list)
    health_scores: HealthScores
    overall_grade: str = "N/A"
    community_metrics: dict = Field(default_factory=dict)
    recommendations: list[dict] = Field(default_factory=list)
    license_name: Optional[str] = None
    has_readme: bool = False
    has_contributing: bool = False
