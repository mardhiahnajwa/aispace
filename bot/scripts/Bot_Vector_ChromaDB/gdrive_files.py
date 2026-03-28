"""
Google Drive loader for document extraction.
"""

from typing import List, Optional
from datetime import datetime

from langchain_community.document_loaders import GoogleDriveLoader as LangChainGoogleDriveLoader
from langchain_core.documents import Document

from base_loader import BaseLoader


class GoogleDriveFileLoader(BaseLoader):
    """Handles loading and processing of documents from Google Drive."""

    def load_from_google_drive(
        self,
        folder_id: str,
        file_types: Optional[List[str]] = None,
        description: Optional[str] = None,
    ) -> List[Document]:
        """
        Load documents from a Google Drive folder.

        Args:
            folder_id: Google Drive folder ID
            file_types: List of file types to include (e.g., ['*.pdf', '*.docx', '*.txt'])
            description: Optional user-provided description

        Returns:
            List of Document objects
        """
        print(f"Loading from Google Drive folder: {folder_id}")

        # Default file types
        if file_types is None:
            file_types = [
                "*.pdf",
                "*.txt",
                "*.docx",
                "*.doc",
                "*.xlsx",
                "*.xls",
                "*.pptx",
                "*.ppt",
                "*.md",
            ]

        loader = LangChainGoogleDriveLoader(
            folder_id=folder_id,
            file_types=file_types,
            load_trashed_files=False,
            recursive=True,
        )

        try:
            documents = loader.load()
        except Exception as e:
            print(f"Error loading from Google Drive: {e}")
            raise

        if not documents:
            raise ValueError(f"No documents found in Google Drive folder: {folder_id}")

        # Enrich with Google Drive metadata
        enriched_docs = self.enrich_google_drive_metadata(
            documents,
            folder_id=folder_id,
            file_types=file_types,
            description=description,
        )

        print(f"Loaded {len(documents)} documents from Google Drive")
        return enriched_docs

    def enrich_google_drive_metadata(
        self,
        documents: List[Document],
        folder_id: str,
        file_types: Optional[List[str]] = None,
        description: Optional[str] = None,
    ) -> List[Document]:
        """
        Add Google Drive-specific metadata to documents.

        Args:
            documents: List of Document objects
            folder_id: Google Drive folder ID
            file_types: List of file types loaded
            description: Optional user-provided description

        Returns:
            Documents with enriched metadata
        """
        for doc in documents:
            if doc.metadata is None:
                doc.metadata = {}

            # Extract file name from source
            file_name = doc.metadata.get("source", "unknown")
            
            # Generate document ID from folder + file name
            document_id = f"gdrive_{folder_id}_{file_name}".replace("/", "_").replace(".", "_").replace(" ", "_").lower()

            # Compute content hash
            content_hash = self.compute_content_hash(doc.page_content)

            # Generate citations
            gdrive_url = f"https://drive.google.com/drive/folders/{folder_id}"
            citations = self.generate_citations(
                title=file_name,
                author="Google Drive",
                url=gdrive_url,
                date=datetime.now().isoformat(),
                source_type="google_drive",
            )

            # Update metadata
            doc.metadata.update(
                {
                    # Document identification
                    "document_id": document_id,
                    "document_type": "gdrive_file",
                    
                    # Google Drive info
                    "folder_id": folder_id,
                    "folder_url": gdrive_url,
                    "file_name": file_name,
                    "file_types_supported": file_types or ["multiple"],
                    
                    # Content integrity
                    "content_hash": content_hash,
                    
                    # Citation metadata
                    "title": file_name,
                    "author": "Google Drive",
                    "description": description or f"Document from Google Drive folder {folder_id}",
                    
                    # Timestamps
                    "ingestion_timestamp": datetime.now().isoformat(),
                    
                    # Citations
                    **citations,
                    
                    # Source tracking
                    "source_type": "google_drive",
                    "source": "google_drive",
                }
            )

        return documents

    def process_google_drive_folder(
        self,
        folder_id: str,
        file_types: Optional[List[str]] = None,
        description: Optional[str] = None,
    ) -> List[Document]:
        """
        Load and chunk documents from a Google Drive folder.

        Args:
            folder_id: Google Drive folder ID
            file_types: List of file types to include
            description: Optional description

        Returns:
            List of chunked Document objects
        """
        # Load documents
        documents = self.load_from_google_drive(
            folder_id=folder_id,
            file_types=file_types,
            description=description,
        )

        # Chunk the documents
        chunks = self.chunk_documents(documents)
        print(f"Created {len(chunks)} chunks from Google Drive folder")

        return chunks
