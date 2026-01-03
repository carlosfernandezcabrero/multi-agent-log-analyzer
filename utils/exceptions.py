class PipelineError(Exception):
    """Base exception for pipeline-related errors."""


class AgentExecutionError(PipelineError):
    """Raised when an agent fails during execution."""

    def __init__(self, agent_name: str, message: str):
        super().__init__(f"{agent_name} failed: {message}")
        self.agent_name = agent_name


class PipelineExecutionError(PipelineError):
    """Raised when the pipeline cannot complete successfully."""
