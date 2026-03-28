"""
SharePoint loader for document extraction.
"""

from typing import List, Optional
from datetime import datetime

from langchain_community.document_loaders import SharePointLoader as LangChainSharePointLoader
from langchain_core.documents import Document

from base_loader import BaseLoader


class SharePointFileLoader(BaseLoader):
    """Handles loading and processing of documents from SharePoint."""

    def load_from_sharepoint(
        self,
        sharepoint_url: str,
        folder_path: str,
        description: Optional[str] = None,
    ) -> List[Document]:
        """
        Load documents from a SharePoint folder.

        Args:
            sharepoint_url: SharePoint site URL
            folder_path: Path to the folder within SharePoint
            description: Optional user-provided description

        Returns:
            List of Document objects
        """
        print(f"Loading from SharePoint: {sharepoint_url}/{folder_path}")

        loader = LangChainSharePointLoader(
            sharepoint_url=sharepoint_url,
            folder_path=folder_path,
        )

        try:
            documents = loader.load()
        except Exception as e:
            print(f"Error loading from SharePoint: {e}")
            raise

        if not documents:
            raise ValueError(f"No documents found at {sharepoint_url}/{folder_path}")

        # Enrich with SharePoint metadata
        enriched_docs = self.enrich_sharepoint_metadata(
            documents,
            sharepoint_url=sharepoint_url,
            folder_path=folder_path,
            description=description,
        )

        print(f"Loaded {len(documents)} documents from SharePoint")
        return enriched_docs

    def enrich_sharepoint_metadata(
        self,
        documents: List[Document],
        sharepoint_url: str,
        folder_path: str,
        description: Optional[str] = None,
    ) -> List[Document]:
        """
        Add SharePoint-specific metadata to documents.

        Args:
            documents: List of Document objects
            sharepoint_url: SharePoint site URL
            folder_path: Path to the folder
            description: Optional user-provided description

        Returns:
            Documents with enriched metadata
        """
        # Extract site name from SharePoint URL
        site_name = sharepoint_url.split("/")[-1] if "/" in sharepoint_url else "SharePoint"

        for doc in documents:
            if doc.metadata is None:
                doc.metadata = {}

            # Extract file name from source
            file_name = doc.metadata.get("source", "unknown")
            
            # Generate document ID from site + folder + file
            document_id = f"sharepoint_{site_name}_{folder_path}_{file_name}".replace("/", "_").replace(".", "_").replace(" ", "_").lower()

            # Compute content hash
            content_hash = self.compute_content_hash(doc.page_content)

            # Generate citations
            full_path = f"{sharepoint_url}/{folder_path}/{file_name}"
            citations = self.generate_citations(
                title=f"{site_name}: {file_name}",
                author=site_name,
                url=full_path,
                date=datetime.now().isoformat(),
                source_type="sharepoint",
            )

            # Update metadata
            doc.metadata.update(
                {
                    # Document identification
                    "document_id": document_id,
                    "document_type": "sharepoint_file",
                    
                    # SharePoint info
                    "sharepoint_url": sharepoint_url,
                    "site_name": site_name,
                    "folder_path": folder_path,
                    "file_name": file_name,
                    "full_path": full_path,
                    
                    # Content integrity
                    "content_hash": content_hash,
                    
                    # Citation metadata
                    "title": f"{site_name}: {file_name}",
                    "author": site_name,
                    "description": description or f"Document from SharePoint: {folder_path}",
                    
                    # Timestamps
                    "ingestion_timestamp": datetime.now().isoformat(),
                    
                    # Citations
                    **citations,
                    
                    # Source tracking
                    "source_type": "sharepoint",
                    "source": "sharepoint",
                }
            )

        return documents

    def process_sharepoint_folder(
        self,
        sharepoint_url: str,
        folder_path: str,
        description: Optional[str] = None,
    ) -> List[Document]:
        """
        Load and chunk documents from a SharePoint folder.

        Args:
            sharepoint_url: SharePoint site URL
            folder_path: Path to the folder
            description: Optional description

        Returns:
            List of chunked Document objects
        """
        # Load documents
        documents = self.load_from_sharepoint(
            sharepoint_url=sharepoint_url,
            folder_path=folder_path,
            description=description,
        )

        # Chunk the documents
        chunks = self.chunk_documents(documents)
        print(f"Created {len(chunks)} chunks from SharePoint folder")

        return chunks
