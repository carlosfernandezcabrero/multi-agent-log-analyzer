from pathlib import Path

from langchain_core.output_parsers import PydanticOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI

from agents.diagnosis.schemas import DiagnosisAgentResult
from agents.supervisor.schemas import SupervisorAgentResult
from configs.default import MODEL_NAME

PROMPT_PATH = Path("prompts/supervisor_prompt.txt")


class SupervisorAgent:
    def __init__(self, model: str = MODEL_NAME):
        llm = ChatOpenAI(model=model, temperature=0)

        self.output_parser = PydanticOutputParser(pydantic_object=SupervisorAgentResult)

        system_prompt = PROMPT_PATH.read_text()
        prompt = ChatPromptTemplate.from_messages(
            [
                ("system", system_prompt),
                ("human", "Diagnosis:\n{diagnosis}"),
            ]
        )

        self.chain = prompt | llm | self.output_parser

    def run(self, diagnosis: DiagnosisAgentResult, context) -> SupervisorAgentResult:
        return self.chain.invoke(
            {
                "diagnosis": diagnosis.model_dump(),
                "format_instructions": self.output_parser.get_format_instructions(),
                "retrieved_context": context,
            }
        )
