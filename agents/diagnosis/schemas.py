from typing import Literal

from pydantic import BaseModel, Field

SeverityLevel = Literal["low", "medium", "high", "critical"]


class DiagnosedIssue(BaseModel):
    title: str = Field(description="Short description of the detected issue")
    description: str = Field(description="Detailed explanation of the issue")
    possible_causes: list[str] = Field(
        description="List of plausible root causes based on the evidence"
    )
    impact: str = Field(description="Potential impact on the system or users")
    severity: SeverityLevel
    affected_components: list[str] = Field(
        description="List of components affected by the issue"
    )


class DiagnosisAgentResult(BaseModel):
    issues: list[DiagnosedIssue]
    overall_assessment: str = Field(
        description="High-level assessment of the system health"
    )
