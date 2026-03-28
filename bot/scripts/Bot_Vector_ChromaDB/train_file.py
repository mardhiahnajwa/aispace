"""
Document loading and chunking module for preparing documents for ChromaDB storage.
Supports: Local files, Web URLs, GitHub, SharePoint, and Google Drive.

This module now uses a modular loader architecture to separate concerns.
See: base_loader.py, local_files.py, github_files.py, gdrive_files.py, 
      sharepoint_files.py, web_files.py, loader_registry.py
"""

from typing import List, Optional, Dict, Union
from datetime import datetime

from langchain_core.documents import Document

from loader_registry import LoaderRegistry, SourceType


class DocumentProcessor:
    """
    Handles document loading from multiple sources and preparation for ChromaDB.
    
    Uses LoaderRegistry as a facade to access modular document loaders.
    This class now serves as a simplified wrapper maintaining backward compatibility.
    """

    def __init__(
        self,
        chunk_size: int = 1000,
        chunk_overlap: int = 200,
    ):
        """
        Initialize the document processor.

        Args:
            chunk_size: Size of each chunk in characters (passed to loaders)
            chunk_overlap: Overlap between chunks (passed to loaders)
        """
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.loader_registry = LoaderRegistry()

    def process_documents_v2(
        self,
        source_type: Union[str, SourceType],
        source_params: Dict,
        description: Optional[str] = None,
    ) -> List[Document]:
        """
        Process documents from any supported source using LoaderRegistry.

        Uses chunk_size and chunk_overlap from this processor's initialization.

        Args:
            source_type: Type of source (local, github, google_drive, sharepoint, web)
            source_params: Source-specific parameters
            description: Optional description for documents

        Returns:
            List of chunked Document objects with metadata

        Example:
            # Load local file with custom chunks
            processor = DocumentProcessor(chunk_size=800, chunk_overlap=150)
            chunks = processor.process_documents_v2(
                source_type="local",
                source_params={"file_path": "/path/to/file.txt"},
                description="My file"
            )
        """
        return LoaderRegistry.process_documents(
            source_type=source_type,
            source_params=source_params,
            description=description,
            chunk_size=self.chunk_size,
            chunk_overlap=self.chunk_overlap,
        )

    def process_documents(
        self,
        file_path: Optional[str] = None,
        directory_path: Optional[str] = None,
        file_type: str = "txt",
        web_urls: Optional[List[str]] = None,
        github_repo: Optional[str] = None,
        github_extensions: Optional[List[str]] = None,
        sharepoint_url: Optional[str] = None,
        sharepoint_folder: Optional[str] = None,
        google_drive_folder: Optional[str] = None,
        description: Optional[str] = None,
    ) -> List[Document]:
        """
        Process documents from various sources (backward compatible wrapper).

        This method maintains backward compatibility with the original API
        but now delegates to LoaderRegistry under the hood.

        Args:
            file_path: Path to a single local file (optional)
            directory_path: Path to directory containing files (optional)
            file_type: Type of local files to load ('txt' or 'pdf')
            web_urls: List of web URLs to load (optional)
            github_repo: GitHub repository URL (optional)
            github_extensions: File extensions to load from GitHub (optional)
            sharepoint_url: SharePoint site URL (optional)
            sharepoint_folder: Specific SharePoint folder path (optional)
            google_drive_folder: Google Drive folder ID (optional)
            description: Optional description for the document(s)

        Returns:
            List of chunked Document objects with metadata

        Note:
            For new code, consider using process_documents_v2() with LoaderRegistry
            which provides a cleaner, more modular interface.
        """
        # Determine source type and build params
        if file_path:
            return self.process_documents_v2(
                source_type="local",
                source_params={"file_path": file_path, "file_type": file_type},
                description=description,
            )
        elif directory_path:
            return self.process_documents_v2(
                source_type="local",
                source_params={"directory_path": directory_path, "file_type": file_type},
                description=description,
            )
        elif web_urls:
            return self.process_documents_v2(
                source_type="web",
                source_params={"urls": web_urls},
                description=description,
            )
        elif github_repo:
            return self.process_documents_v2(
                source_type="github",
                source_params={
                    "repo_url": github_repo,
                    "file_extensions": github_extensions,
                },
                description=description,
            )
        elif sharepoint_url:
            return self.process_documents_v2(
                source_type="sharepoint",
                source_params={
                    "sharepoint_url": sharepoint_url,
                    "folder_path": sharepoint_folder,
                },
                description=description,
            )
        elif google_drive_folder:
            return self.process_documents_v2(
                source_type="google_drive",
                source_params={"folder_id": google_drive_folder},
                description=description,
            )
        else:
            raise ValueError(
                "Must provide one of: file_path, directory_path, web_urls, "
                "github_repo, sharepoint_url, or google_drive_folder"
            )
