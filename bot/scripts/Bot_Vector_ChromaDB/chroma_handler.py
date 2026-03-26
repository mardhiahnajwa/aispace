"""
ChromaDB handler for storing and retrieving document chunks.
"""

import os
from typing import List, Optional, Dict, Any
import chromadb
from chromadb.config import Settings


class ChromaDBHandler:
    """Handles ChromaDB connections and document storage/retrieval."""

    def __init__(
        self,
        chromadb_url: Optional[str] = None,
        collection_name: str = "documents",
    ):
        """
        Initialize ChromaDB handler.

        Args:
            chromadb_url: URL for the ChromaDB server (defaults to CHROMADB_URL env var)
            collection_name: Name of the collection to use
        """
        self.chromadb_url = chromadb_url or os.getenv("CHROMADB_URL", "http://chromadb:8000")
        
        print(f"Connecting to ChromaDB at: {self.chromadb_url}")

        # Connect to remote ChromaDB server
        self.client = chromadb.HttpClient(
            host=self._parse_host(), 
            port=self._parse_port()
        )
        self.collection_name = collection_name
        self.collection = None

    def _parse_host(self) -> str:
        """Extract host from ChromaDB URL."""
        url = self.chromadb_url.replace("http://", "").replace("https://", "")
        return url.split(":")[0]

    def _parse_port(self) -> int:
        """Extract port from ChromaDB URL, default to 8000."""
        try:
            return int(self.chromadb_url.split(":")[-1])
        except (ValueError, IndexError):
            return 8000

    def create_or_get_collection(self) -> None:
        """Create or get the collection."""
        try:
            # Get or create collection
            self.collection = self.client.get_or_create_collection(
                name=self.collection_name,
                metadata={"hnsw:space": "cosine"},
            )
            print(f"Collection '{self.collection_name}' ready")
        except Exception as e:
            print(f"Error creating/getting collection: {e}")
            raise

    def add_documents(
        self,
        documents: List,
        ids: Optional[List[str]] = None,
        metadatas: Optional[List[dict]] = None,
    ) -> None:
        """
        Add documents to ChromaDB.

        Args:
            documents: List of document content strings
            ids: Optional list of document IDs (will be auto-generated if not provided)
            metadatas: Optional list of metadata dictionaries
        """
        if not self.collection:
            self.create_or_get_collection()

        try:
            # Auto-generate IDs if not provided
            if ids is None:
                ids = [f"doc_{i}" for i in range(len(documents))]

            # Create default metadatas if not provided
            if metadatas is None:
                metadatas = [{"source": "document"} for _ in documents]

            # Add documents to collection
            self.collection.add(
                ids=ids,
                documents=documents,
                metadatas=metadatas,
            )
            print(f"Added {len(documents)} documents to collection '{self.collection_name}'")
        except Exception as e:
            print(f"Error adding documents: {e}")
            raise

    def add_langchain_documents(self, langchain_docs: List) -> None:
        """
        Add LangChain Document objects to ChromaDB.

        Args:
            langchain_docs: List of LangChain Document objects
        """
        if not langchain_docs:
            raise ValueError("No documents provided")

        documents = [doc.page_content for doc in langchain_docs]
        metadatas = [doc.metadata if doc.metadata else {} for doc in langchain_docs]
        ids = [
            f"chunk_{i}_{hash(doc.page_content) % 10000}"
            for i, doc in enumerate(langchain_docs)
        ]

        self.add_documents(documents=documents, ids=ids, metadatas=metadatas)

    def search(
        self,
        query: str,
        num_results: int = 5,
    ) -> dict:
        """
        Search the collection.

        Args:
            query: Search query
            num_results: Number of results to return

        Returns:
            List of search results with metadata
        """
        if not self.collection:
            self.create_or_get_collection()

        try:
            results = self.collection.query(
                query_texts=[query],
                n_results=num_results,
            )
            return results
        except Exception as e:
            print(f"Error searching collection: {e}")
            raise

    def get_document_info(self, doc_id: str) -> Optional[dict]:
        """
        Get detailed information about a specific document.

        Args:
            doc_id: Document ID

        Returns:
            Document information with metadata
        """
        if not self.collection:
            self.create_or_get_collection()

        try:
            result = self.collection.get(ids=[doc_id], include=["documents", "metadatas"])
            if result["documents"] and len(result["documents"]) > 0:
                return {
                    "id": doc_id,
                    "content": result["documents"][0],
                    "metadata": result["metadatas"][0] if result["metadatas"] else {},
                }
            return None
        except Exception as e:
            print(f"Error getting document info: {e}")
            raise

    def get_collection_count(self) -> int:
        """Get the number of documents in the collection."""
        if not self.collection:
            self.create_or_get_collection()

        try:
            return self.collection.count()
        except Exception as e:
            print(f"Error getting collection count: {e}")
            raise

    def delete_collection(self) -> None:
        """Delete the entire collection."""
        try:
            self.client.delete_collection(name=self.collection_name)
            self.collection = None
            print(f"Deleted collection '{self.collection_name}'")
        except Exception as e:
            print(f"Error deleting collection: {e}")
            raise
