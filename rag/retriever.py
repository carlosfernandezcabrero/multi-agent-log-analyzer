from pathlib import Path
from typing import List

from langchain_community.vectorstores import FAISS
from langchain_core.documents import Document
from langchain_openai import OpenAIEmbeddings

from agents.diagnosis.schemas import DiagnosisAgentResult


class RAGContextRetriever:
    def __init__(self, documents_path: Path):
        self.embeddings = OpenAIEmbeddings()

        docs = self._load_documents(documents_path)
        self.vector_store = FAISS.from_documents(docs, self.embeddings)

    @staticmethod
    def _load_documents(path: Path) -> List[Document]:
        documents = []

        for file in path.glob("*.txt"):
            documents.append(
                Document(
                    page_content=file.read_text(),
                    metadata={"source": file.name},
                )
            )

        return documents

    @staticmethod
    def build_rag_query(diagnosis: DiagnosisAgentResult) -> str:
        return " | ".join(issue.title for issue in diagnosis.issues)

    def retrieve(self, query: str, k: int = 3) -> List[Document]:
        return self.vector_store.similarity_search(query, k=k)
