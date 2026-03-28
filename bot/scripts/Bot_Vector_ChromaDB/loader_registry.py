"""
Loader registry for managing document loaders by source type.
Implements factory pattern for instantiating appropriate loaders.
"""

from typing import List, Optional, Union, Dict
from enum import Enum

from langchain_core.documents import Document

from base_loader import BaseLoader
from local_files import LocalFileLoader
from github_files import GitHubLoader
from gdrive_files import GoogleDriveFileLoader
from sharepoint_files import SharePointFileLoader
from web_files import WebLoader


class SourceType(Enum):
    """Enumeration of supported document sources."""
    LOCAL = "local"
    GITHUB = "github"
    GOOGLE_DRIVE = "google_drive"
    SHAREPOINT = "sharepoint"
    WEB = "web"


class LoaderRegistry:
    """Factory and registry for document loaders."""

    _loaders: Dict[SourceType, BaseLoader] = {}
    _chunk_size: int = 1000
    _chunk_overlap: int = 200

    @classmethod
    def configure_chunking(cls, chunk_size: int = 1000, chunk_overlap: int = 200):
        """
        Configure global chunk parameters for all loaders.

        Args:
            chunk_size: Size of each chunk in characters
            chunk_overlap: Overlap between chunks
        """
        cls._chunk_size = chunk_size
        cls._chunk_overlap = chunk_overlap
        # Reset cached loaders so they'll be recreated with new params
        cls._loaders.clear()

    @classmethod
    def get_loader(cls, source_type: Union[str, SourceType]) -> BaseLoader:
        """
        Get or instantiate a loader for the given source type.

        Args:
            source_type: Source type as string or SourceType enum

        Returns:
            Appropriate loader instance
        """
        # Convert string to enum if needed
        if isinstance(source_type, str):
            source_type = SourceType(source_type.lower())

        # Return cached loader or create new one
        if source_type not in cls._loaders:
            cls._loaders[source_type] = cls._create_loader(source_type)

        return cls._loaders[source_type]

    @classmethod
    def _create_loader(cls, source_type: SourceType) -> BaseLoader:
        """
        Create a new loader instance for the given source type.

        Args:
            source_type: Source type enum

        Returns:
            Loader instance
        """
        if source_type == SourceType.LOCAL:
            return LocalFileLoader(chunk_size=cls._chunk_size, chunk_overlap=cls._chunk_overlap)
        elif source_type == SourceType.GITHUB:
            return GitHubLoader(chunk_size=cls._chunk_size, chunk_overlap=cls._chunk_overlap)
        elif source_type == SourceType.GOOGLE_DRIVE:
            return GoogleDriveFileLoader(chunk_size=cls._chunk_size, chunk_overlap=cls._chunk_overlap)
        elif source_type == SourceType.SHAREPOINT:
            return SharePointFileLoader(chunk_size=cls._chunk_size, chunk_overlap=cls._chunk_overlap)
        elif source_type == SourceType.WEB:
            return WebLoader(chunk_size=cls._chunk_size, chunk_overlap=cls._chunk_overlap)
        else:
            raise ValueError(f"Unsupported source type: {source_type}")

    @classmethod
    def process_documents(
        cls,
        source_type: Union[str, SourceType],
        source_params: Dict,
        description: Optional[str] = None,
        chunk_size: Optional[int] = None,
        chunk_overlap: Optional[int] = None,
    ) -> List[Document]:
        """
        Process documents from a specified source using the registry.

        Args:
            source_type: Type of document source
            source_params: Parameters specific to the source type
            description: Optional description for all documents
            chunk_size: Optional chunk size (uses registry default if not provided)
            chunk_overlap: Optional chunk overlap (uses registry default if not provided)

        Returns:
            List of chunked Document objects

        Example usage:
            # Load local files
            chunks = LoaderRegistry.process_documents(
                source_type="local",
                source_params={"file_path": "/path/to/file.txt"},
                description="My document"
            )

            # Load GitHub repo
            chunks = LoaderRegistry.process_documents(
                source_type="github",
                source_params={
                    "repo_url": "https://github.com/owner/repo",
                    "file_extensions": [".md", ".py"]
                },
                description="My repo docs"
            )

            # Load Google Drive folder
            chunks = LoaderRegistry.process_documents(
                source_type="google_drive",
                source_params={"folder_id": "your_folder_id"},
                description="My folder"
            )

            # Load web URLs
            chunks = LoaderRegistry.process_documents(
                source_type="web",
                source_params={"urls": ["https://example.com", "https://docs.example.com"]},
                description="My web docs"
            )

            # Load SharePoint folder
            chunks = LoaderRegistry.process_documents(
                source_type="sharepoint",
                source_params={
                    "sharepoint_url": "https://company.sharepoint.com/sites/mysite",
                    "folder_path": "Shared Documents/My Folder"
                },
                description="SharePoint docs"
            )
        """
        # Configure chunk parameters if provided
        if chunk_size is not None or chunk_overlap is not None:
            cls.configure_chunking(
                chunk_size=chunk_size or cls._chunk_size,
                chunk_overlap=chunk_overlap or cls._chunk_overlap,
            )

        # Convert string to enum if needed
        if isinstance(source_type, str):
            source_type = SourceType(source_type.lower())

        loader = cls.get_loader(source_type)

        # Route to appropriate loader method based on source type
        if source_type == SourceType.LOCAL:
            return loader.process_files(
                file_path=source_params.get("file_path"),
                directory_path=source_params.get("directory_path"),
                file_type=source_params.get("file_type", "txt"),
                description=description,
            )
        elif source_type == SourceType.GITHUB:
            return loader.process_github_repo(
                repo_url=source_params["repo_url"],
                file_extensions=source_params.get("file_extensions"),
                description=description,
            )
        elif source_type == SourceType.GOOGLE_DRIVE:
            return loader.process_google_drive_folder(
                folder_id=source_params["folder_id"],
                file_types=source_params.get("file_types"),
                description=description,
            )
        elif source_type == SourceType.SHAREPOINT:
            return loader.process_sharepoint_folder(
                sharepoint_url=source_params["sharepoint_url"],
                folder_path=source_params["folder_path"],
                description=description,
            )
        elif source_type == SourceType.WEB:
            return loader.process_web_urls(
                urls=source_params["urls"],
                description=description,
            )
        else:
            raise ValueError(f"Unsupported source type: {source_type}")

    @classmethod
    def get_supported_sources(cls) -> List[str]:
        """
        Get list of supported source types.

        Returns:
            List of source type names
        """
        return [source.value for source in SourceType]

    @classmethod
    def reset_loaders(cls):
        """Reset all cached loader instances."""
        cls._loaders.clear()
