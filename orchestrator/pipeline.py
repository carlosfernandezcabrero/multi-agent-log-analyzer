import time
from pathlib import Path

from langchain_core.documents import Document

from agents.diagnosis.agent import DiagnosisAgent
from agents.log_analyst.agent import LogAnalystAgent
from agents.report_generator.agent import ReportGeneratorAgent
from agents.supervisor.agent import SupervisorAgent
from rag.retriever import RAGContextRetriever
from utils.exceptions import AgentExecutionError, PipelineExecutionError
from utils.logging import get_logger

logger = get_logger(__name__)


class LogAnalysisPipeline:
    def __init__(
        self,
        log_analyst=None,
        diagnosis_agent=None,
        supervisor_agent=None,
        report_generator=None,
        context_retriever=None,
    ):
        self.log_analyst = log_analyst or LogAnalystAgent()
        self.diagnosis_agent = diagnosis_agent or DiagnosisAgent()
        self.supervisor_agent = supervisor_agent or SupervisorAgent()
        self.report_generator = report_generator or ReportGeneratorAgent()
        self.context_retriever = context_retriever or RAGContextRetriever(
            documents_path=Path("knowledge_base/documents")
        )

    @staticmethod
    def _format_retrieved_context(docs: list[Document]):
        return [
            {
                "source": doc.metadata["source"],
                "content": doc.page_content,
            }
            for doc in docs
        ]

    def run(self, log_file_path: Path) -> str:
        try:
            logger.info("Reading log file: %s", log_file_path)
            logs = log_file_path.read_text()

            try:
                logger.info("Starting LogAnalystAgent")
                start = time.perf_counter()
                analysis_result = self.log_analyst.run(logs)
                logger.info(
                    "LogAnalystAgent completed in %.2fs",
                    time.perf_counter() - start,
                )
            except Exception as exc:
                logger.exception("LogAnalystAgent failed")
                raise AgentExecutionError("LogAnalystAgent", str(exc)) from exc

            try:
                logger.info("Starting DiagnosisAgent")
                start = time.perf_counter()
                diagnosis_result = self.diagnosis_agent.run(analysis_result)
                logger.info(
                    "DiagnosisAgent completed in %.2fs",
                    time.perf_counter() - start,
                )
            except Exception as exc:
                logger.exception("DiagnosisAgent failed")
                raise AgentExecutionError("DiagnosisAgent", str(exc)) from exc

            rag_query = self.context_retriever.build_rag_query(diagnosis_result)
            try:
                logger.info("Retrieving context for RAG with query: %s", rag_query)
                start = time.perf_counter()
                context_docs = self.context_retriever.retrieve(rag_query)
                logger.info(
                    "RAG context retrieval completed in %.2fs",
                    time.perf_counter() - start,
                )
            except Exception as exc:
                logger.exception("RAG context retrieval failed")
                raise AgentExecutionError("RAGContextRetriever", str(exc)) from exc
            retrieved_context = self._format_retrieved_context(context_docs)

            try:
                logger.info("Starting SupervisorAgent")
                start = time.perf_counter()
                supervisor_result = self.supervisor_agent.run(
                    diagnosis_result, retrieved_context
                )
                logger.info(
                    "SupervisorAgent completed in %.2fs",
                    time.perf_counter() - start,
                )
            except Exception as exc:
                logger.exception("SupervisorAgent failed")
                raise AgentExecutionError("SupervisorAgent", str(exc)) from exc

            if supervisor_result.decision != "continue":
                raise PipelineExecutionError(
                    f"Pipeline aborted by supervisor: {supervisor_result.rationale}"
                )

            try:
                logger.info("Starting ReportGeneratorAgent")
                report = self.report_generator.run(diagnosis_result, retrieved_context)
                logger.info("ReportGeneratorAgent completed")
            except Exception as exc:
                logger.exception("ReportGeneratorAgent failed")
                raise AgentExecutionError("ReportGeneratorAgent", str(exc)) from exc
        except Exception as exc:
            raise PipelineExecutionError(str(exc)) from exc

        return report
