from pathlib import Path

from langchain_core.output_parsers import PydanticOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI

from agents.log_analyst.schemas import LogAnalystAgentResult
from configs.default import MODEL_NAME

SYSTEM_PROMPT_PATH = Path("prompts/log_analyst_prompt.txt")


class LogAnalystAgent:
    def __init__(self, model: str = MODEL_NAME):
        llm = ChatOpenAI(model=model, temperature=0)

        prompt_template = SYSTEM_PROMPT_PATH.read_text()
        prompt = ChatPromptTemplate.from_messages(
            [
                ("system", prompt_template),
                ("human", "Logs:\n{logs}"),
            ]
        )

        self.output_parser = PydanticOutputParser(pydantic_object=LogAnalystAgentResult)

        self.chain = prompt | llm | self.output_parser

    def run(self, logs: str) -> LogAnalystAgentResult:
        return self.chain.invoke(
            {
                "logs": logs,
                "format_instructions": self.output_parser.get_format_instructions(),
            }
        )
