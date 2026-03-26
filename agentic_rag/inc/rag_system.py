"""RAG utilities for document retrieval."""
import os
from typing import List
import chromadb
from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import Chroma
from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter


class RAGSystem:
    """Vector store for document retrieval."""

    def __init__(self, collection_name: str = "documents"):
        self.embeddings = OpenAIEmbeddings(model="text-embedding-3-small")
        self.chroma_host = os.getenv("CHROMADB_HOST", "chromadb")
        self.chroma_port = int(os.getenv("CHROMADB_PORT", "8000"))
        
        self.client = chromadb.HttpClient(
            host=self.chroma_host,
            port=self.chroma_port
        )
        
        self.vector_store = Chroma(
            client=self.client,
            collection_name=collection_name,
            embedding_function=self.embeddings,
        )
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000, chunk_overlap=200
        )

    def add_text(self, text: str, metadata: dict = None):
        """Add text to vector store."""
        doc = Document(page_content=text, metadata=metadata or {})
        chunks = self.text_splitter.split_documents([doc])
        self.vector_store.add_documents(chunks)

    def retrieve(self, query: str, k: int = 4) -> List[Document]:
        """Retrieve documents."""
        return self.vector_store.similarity_search(query, k=k)


_rag_instance = None

def get_rag() -> RAGSystem:
    global _rag_instance
    if _rag_instance is None:
        _rag_instance = RAGSystem()
    return _rag_instance
