from pathlib import Path

from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI

from agents.diagnosis.schemas import DiagnosisAgentResult
from configs.default import MODEL_NAME

PROMPT_PATH = Path("prompts/report_generator_prompt.txt")


class ReportGeneratorAgent:
    def __init__(self, model: str = MODEL_NAME):
        llm = ChatOpenAI(model=model, temperature=0)

        system_prompt = PROMPT_PATH.read_text()

        prompt = ChatPromptTemplate.from_messages(
            [
                ("system", system_prompt),
                (
                    "human",
                    "Diagnosis data:\n{diagnosis}",
                ),
            ]
        )

        self.chain = prompt | llm

    def run(self, diagnosis: DiagnosisAgentResult, context) -> str:
        response = self.chain.invoke(
            {"diagnosis": diagnosis.model_dump(), "retrieved_context": context}
        )
        return str(response.content)
