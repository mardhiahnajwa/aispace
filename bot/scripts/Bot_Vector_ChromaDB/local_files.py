"""
Local file loader for .txt, .md, and .pdf files.
"""

from typing import List, Optional
from pathlib import Path
from datetime import datetime
import mimetypes

from langchain_community.document_loaders import (
    DirectoryLoader,
    TextLoader,
    PyPDFLoader,
)
from langchain_core.documents import Document

from base_loader import BaseLoader


class LocalFileLoader(BaseLoader):
    """Handles loading and processing of local files."""

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
        return self.enrich_document_metadata(docs, file_path)

    def get_file_metadata(self, file_path: str, description: Optional[str] = None, author: Optional[str] = None) -> dict:
        """
        Extract metadata from a file with citation support.

        Args:
            file_path: Path to the file
            description: Optional user-provided description
            author: Optional author name

        Returns:
            Dictionary containing comprehensive file metadata
        """
        path = Path(file_path)
        file_stat = path.stat()
        
        # Compute hashes
        file_hash = self.compute_file_hash(file_path)
        
        # Get MIME type
        mime_type, _ = mimetypes.guess_type(file_path)
        
        # Extract title from filename
        title = path.stem  # Filename without extension
        
        # Dates
        created_date = datetime.fromtimestamp(file_stat.st_ctime).isoformat()
        modified_date = datetime.fromtimestamp(file_stat.st_mtime).isoformat()
        
        # Generate citations
        citations = self.generate_citations(
            title=title,
            author=author or "Unknown",
            url=f"file://{path.absolute()}",
            date=modified_date,
            source_type="file"
        )

        return {
            # Basic file info
            "file_name": path.name,
            "file_path": str(path.absolute()),
            "file_type": path.suffix.lower(),
            "file_size_bytes": file_stat.st_size,
            "mime_type": mime_type or "application/octet-stream",
            
            # Dates
            "created_date": created_date,
            "modified_date": modified_date,
            "ingestion_timestamp": datetime.now().isoformat(),
            
            # Integrity
            "source_hash": file_hash,
            "encoding": "utf-8",
            
            # Citation metadata
            "title": title,
            "author": author or "Unknown",
            
            # User provided
            "description": description or "",
            
            # Citations
            **citations,
            
            # Source tracking
            "source": "document_import",
            "source_type": "file",
        }

    def enrich_document_metadata(
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
        file_metadata = self.get_file_metadata(file_path, description)

        for doc in documents:
            # Preserve existing metadata and add file metadata
            if doc.metadata is None:
                doc.metadata = {}
            doc.metadata.update(file_metadata)

        return documents

    def process_files(
        self,
        file_path: Optional[str] = None,
        directory_path: Optional[str] = None,
        file_type: str = "txt",
        description: Optional[str] = None,
    ) -> List[Document]:
        """
        Process local files (single file or directory).

        Args:
            file_path: Path to single file (optional)
            directory_path: Path to directory (optional)
            file_type: Type of files ('txt' or 'pdf')
            description: Optional description

        Returns:
            List of chunked Document objects
        """
        documents = []

        if file_path:
            print(f"Loading single file: {file_path}")
            documents = self.load_single_file(file_path)
            if description:
                for doc in documents:
                    doc.metadata["description"] = description
        elif directory_path:
            print(f"Loading files from directory: {directory_path}")
            if file_type.lower() == "pdf":
                documents = self.load_pdf_files(directory_path)
            else:
                documents = self.load_text_files(directory_path)
            for doc in documents:
                if doc.metadata and "source" in doc.metadata:
                    self.enrich_document_metadata([doc], doc.metadata["source"], description)
        else:
            raise ValueError("Either file_path or directory_path must be provided")

        if not documents:
            raise ValueError("No documents loaded. Check the path and file types.")

        print(f"Loaded {len(documents)} documents")

        # Chunk the documents
        chunks = self.chunk_documents(documents)
        print(f"Created {len(chunks)} chunks from documents")

        return chunks
