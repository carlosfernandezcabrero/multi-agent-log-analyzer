from typing import Literal

from pydantic import BaseModel, Field

SupervisorDecision = Literal["continue", "abort"]


class SupervisorAgentResult(BaseModel):
    decision: SupervisorDecision = Field(
        description="Decision on whether the pipeline should continue"
    )
    rationale: str = Field(description="Explanation for the decision")
    confidence: float = Field(
        ge=0.0, le=1.0, description="Confidence level in the decision"
    )
