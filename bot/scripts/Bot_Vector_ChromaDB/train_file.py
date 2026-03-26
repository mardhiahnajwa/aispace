"""
Document loading and chunking module for preparing documents for ChromaDB storage.
"""

import os
from typing import List, Optional, Dict, Any
from pathlib import Path
from datetime import datetime

from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import (
    DirectoryLoader,
    TextLoader,
    PyPDFLoader,
)
from langchain_core.documents import Document


class DocumentProcessor:
    """Handles document loading, chunking, and preparation for ChromaDB."""

    def __init__(
        self,
        chunk_size: int = 1000,
        chunk_overlap: int = 200,
    ):
        """
        Initialize the document processor.

        Args:
            chunk_size: Size of each chunk in characters
            chunk_overlap: Overlap between chunks
        """
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            separators=["\n\n", "\n", " ", ""],
        )

    def _get_file_metadata(self, file_path: str, description: Optional[str] = None) -> Dict[str, Any]:
        """
        Extract metadata from a file.

        Args:
            file_path: Path to the file
            description: Optional user-provided description

        Returns:
            Dictionary containing file metadata
        """
        path = Path(file_path)
        file_stat = path.stat()

        return {
            "file_name": path.name,
            "file_path": str(path.absolute()),
            "file_type": path.suffix.lower(),
            "file_size_bytes": file_stat.st_size,
            "created_date": datetime.fromtimestamp(file_stat.st_ctime).isoformat(),
            "modified_date": datetime.fromtimestamp(file_stat.st_mtime).isoformat(),
            "description": description or "",
            "source": "document_import",
        }

    def _enrich_document_metadata(
        self,
        documents: List[Document],
        file_path: str,
        description: Optional[str] = None,
    ) -> List[Document]:
        """
        Add file metadata to documents.

        Args:
            documents: List of Document objects
            file_path: Path to the source file
            description: Optional description

        Returns:
            Documents with enriched metadata
        """
        file_metadata = self._get_file_metadata(file_path, description)

        for doc in documents:
            # Preserve existing metadata and add file metadata
            if doc.metadata is None:
                doc.metadata = {}
            doc.metadata.update(file_metadata)

        return documents

    def load_text_files(self, directory_path: str) -> List[Document]:
        """
        Load all text files from a directory.

        Args:
            directory_path: Path to the directory containing text files

        Returns:
            List of Document objects
        """
        loader = DirectoryLoader(
            directory_path,
            glob="**/*.txt",
            loader_cls=TextLoader,
        )
        return loader.load()

    def load_pdf_files(self, directory_path: str) -> List[Document]:
        """
        Load all PDF files from a directory.

        Args:
            directory_path: Path to the directory containing PDF files

        Returns:
            List of Document objects
        """
        loader = DirectoryLoader(
            directory_path,
            glob="**/*.pdf",
            loader_cls=PyPDFLoader,
        )
        return loader.load()

    def load_single_file(self, file_path: str) -> List[Document]:
        """
        Load a single file.

        Args:
            file_path: Path to the file

        Returns:
            List of Document objects
        """
        file_ext = Path(file_path).suffix.lower()

        if file_ext == ".pdf":
            loader = PyPDFLoader(file_path)
        elif file_ext in [".txt", ".md"]:
            loader = TextLoader(file_path)
        else:
            raise ValueError(f"Unsupported file type: {file_ext}")

        docs = loader.load()
        # Enrich with file metadata
        return self._enrich_document_metadata(docs, file_path)

    def chunk_documents(self, documents: List[Document]) -> List[Document]:
        """
        Split documents into chunks.

        Args:
            documents: List of Document objects to chunk

        Returns:
            List of chunked Document objects
        """
        return self.text_splitter.split_documents(documents)

    def process_documents(
        self,
        file_path: Optional[str] = None,
        directory_path: Optional[str] = None,
        file_type: str = "txt",
        description: Optional[str] = None,
    ) -> List[Document]:
        """
        Process documents from a file or directory.

        Args:
            file_path: Path to a single file (optional)
            directory_path: Path to directory containing files (optional)
            file_type: Type of files to load ('txt' or 'pdf')
            description: Optional description for the document(s)

        Returns:
            List of chunked Document objects with metadata
        """
        documents = []

        if file_path:
            print(f"Loading single file: {file_path}")
            documents = self.load_single_file(file_path)
            # Add description if provided
            if description:
                for doc in documents:
                    doc.metadata["description"] = description
        elif directory_path:
            print(f"Loading files from directory: {directory_path}")
            if file_type.lower() == "pdf":
                documents = self.load_pdf_files(directory_path)
            else:
                documents = self.load_text_files(directory_path)
            # Enrich directory-loaded documents with metadata
            for doc in documents:
                if doc.metadata and "source" in doc.metadata:
                    self._enrich_document_metadata([doc], doc.metadata["source"], description)
        else:
            raise ValueError("Either file_path or directory_path must be provided")

        if not documents:
            raise ValueError("No documents loaded. Check the path and file types.")

        print(f"Loaded {len(documents)} documents")

        # Chunk the documents
        chunks = self.chunk_documents(documents)
        print(f"Created {len(chunks)} chunks from documents")

        return chunks
