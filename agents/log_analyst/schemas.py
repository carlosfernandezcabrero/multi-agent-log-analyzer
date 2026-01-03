from pydantic import BaseModel, Field


class LogAnalystAgentSummary(BaseModel):
    total_lines: int = Field(description="Total number of log lines analyzed")
    error_count: int = Field(description="Total number of errors found in the logs")
    warning_count: int = Field(description="Total number of warnings found in the logs")


class LogAnalystAgentError(BaseModel):
    type: str = Field(description="Type of the error")
    count: int = Field(description="Number of occurrences of this error type")
    components: list[str] = Field(
        description="List of affected components for this error type"
    )


class LogAnalystAgentResult(BaseModel):
    summary: LogAnalystAgentSummary
    errors: list[LogAnalystAgentError]
    anomalies: list[str] = Field(description="List of detected anomalies in the logs")
