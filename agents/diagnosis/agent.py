from pathlib import Path

from langchain_core.output_parsers import PydanticOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI

from agents.diagnosis.schemas import DiagnosisAgentResult
from agents.log_analyst.schemas import LogAnalystAgentResult
from configs.default import MODEL_NAME

PROMPT_PATH = Path("prompts/diagnosis_prompt.txt")


class DiagnosisAgent:
    def __init__(self, model: str = MODEL_NAME):
        llm = ChatOpenAI(model=model, temperature=0)

        self.output_parser = PydanticOutputParser(pydantic_object=DiagnosisAgentResult)

        system_prompt = PROMPT_PATH.read_text()
        prompt = ChatPromptTemplate.from_messages(
            [
                ("system", system_prompt),
                (
                    "human",
                    "Log analysis result:\n{analysis}",
                ),
            ]
        )

        self.chain = prompt | llm | self.output_parser

    def run(self, analysis: LogAnalystAgentResult) -> DiagnosisAgentResult:
        return self.chain.invoke(
            {
                "analysis": analysis.model_dump(),
                "format_instructions": self.output_parser.get_format_instructions(),
            }
        )
