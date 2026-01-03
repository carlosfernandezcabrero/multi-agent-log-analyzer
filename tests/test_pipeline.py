import os
from pathlib import Path
from unittest.mock import patch

import pytest

from orchestrator.pipeline import LogAnalysisPipeline
from utils.exceptions import PipelineExecutionError

valid_log_path = Path("data/sample_logs.txt")
os.environ["OPENAI_API_KEY"] = "test_api_key"


@pytest.fixture
def pipeline():
    with patch("orchestrator.pipeline.LogAnalystAgent") as LogAnalystMock, patch(
        "orchestrator.pipeline.DiagnosisAgent"
    ) as DiagnosisMock, patch(
        "orchestrator.pipeline.SupervisorAgent"
    ) as SupervisorMock, patch(
        "orchestrator.pipeline.ReportGeneratorAgent"
    ) as ReportMock, patch(
        "orchestrator.pipeline.RAGContextRetriever"
    ) as RetrieverMock:
        pipeline_instance = LogAnalysisPipeline(
            log_analyst=LogAnalystMock.return_value,
            diagnosis_agent=DiagnosisMock.return_value,
            supervisor_agent=SupervisorMock.return_value,
            report_generator=ReportMock.return_value,
            context_retriever=RetrieverMock.return_value,
        )

        yield pipeline_instance


@pytest.fixture
def supervisor_continue():
    class SupervisorResult:
        decision = "continue"
        rationale = "Proceed"

    return SupervisorResult()


def test_pipeline_when_log_analyst_agent_launch_exception(pipeline):
    pipeline.log_analyst.run.side_effect = Exception("Simulated failure")

    with pytest.raises(PipelineExecutionError) as exc:
        pipeline.run(valid_log_path)

    assert isinstance(exc.value, PipelineExecutionError)
    assert "LogAnalystAgent" in str(exc)


def test_pipeline_when_diagnosis_agent_launch_exception(pipeline):
    pipeline.diagnosis_agent.run.side_effect = Exception("Simulated failure")

    with pytest.raises(PipelineExecutionError) as exc:
        pipeline.run(valid_log_path)

    assert isinstance(exc.value, PipelineExecutionError)
    assert "DiagnosisAgent" in str(exc)


def test_pipeline_when_rag_retriever_launch_exception(pipeline):
    pipeline.context_retriever.retrieve.side_effect = Exception("Simulated failure")

    with pytest.raises(PipelineExecutionError) as exc:
        pipeline.run(valid_log_path)

    assert isinstance(exc.value, PipelineExecutionError)
    assert "RAGContextRetriever" in str(exc)


def test_pipeline_when_supervisor_agent_launch_exception(pipeline):
    pipeline.supervisor_agent.run.side_effect = Exception("Simulated failure")

    with pytest.raises(PipelineExecutionError) as exc:
        pipeline.run(valid_log_path)

    assert isinstance(exc.value, PipelineExecutionError)
    assert "SupervisorAgent" in str(exc)


def test_pipeline_when_supervisor_agent_aborts_pipeline(pipeline):
    with pytest.raises(PipelineExecutionError) as exc:
        pipeline.run(valid_log_path)

    assert isinstance(exc.value, PipelineExecutionError)
    assert "Pipeline aborted by supervisor" in str(exc)


def test_pipeline_when_report_generator_agent_launch_exception(
    pipeline, supervisor_continue
):
    pipeline.report_generator.run.side_effect = Exception("Simulated failure")
    pipeline.supervisor_agent.run.return_value = supervisor_continue

    with pytest.raises(PipelineExecutionError) as exc:
        pipeline.run(valid_log_path)

    assert isinstance(exc.value, PipelineExecutionError)
    assert "ReportGeneratorAgent" in str(exc)


def test_pipeline_generates_report_successfully(pipeline, supervisor_continue):
    pipeline.supervisor_agent.run.return_value = supervisor_continue
    pipeline.report_generator.run.return_value = "Simulated final report"

    result = pipeline.run(valid_log_path)

    assert result == "Simulated final report"
