"""
Web content loader for document extraction from URLs.
"""

from typing import List, Optional
from datetime import datetime
from urllib.parse import urlparse

from langchain_community.document_loaders import WebBaseLoader
from langchain_core.documents import Document

from base_loader import BaseLoader


class WebLoader(BaseLoader):
    """Handles loading and processing of documents from web URLs."""

    def load_from_web(
        self,
        urls: List[str],
        description: Optional[str] = None,
    ) -> List[Document]:
        """
        Load documents from web URLs.

        Args:
            urls: List of URLs to load
            description: Optional user-provided description

        Returns:
            List of Document objects
        """
        print(f"Loading content from {len(urls)} URL(s)")

        all_documents = []
        
        for url in urls:
            try:
                print(f"  - Fetching: {url}")
                loader = WebBaseLoader(url)
                docs = loader.load()

                if docs:
                    # Enrich with web metadata
                    enriched_docs = self.enrich_web_metadata(
                        docs,
                        url=url,
                        description=description,
                    )
                    all_documents.extend(enriched_docs)
                else:
                    print(f"    Warning: No content loaded from {url}")
            except Exception as e:
                print(f"    Error loading {url}: {e}")
                continue

        if not all_documents:
            raise ValueError(f"No documents loaded from the provided URLs")

        print(f"Loaded {len(all_documents)} documents from web")
        return all_documents

    def enrich_web_metadata(
        self,
        documents: List[Document],
        url: str,
        description: Optional[str] = None,
    ) -> List[Document]:
        """
        Add web-specific metadata to documents.

        Args:
            documents: List of Document objects
            url: Source URL
            description: Optional user-provided description

        Returns:
            Documents with enriched metadata
        """
        # Parse URL for metadata
        parsed_url = urlparse(url)
        domain = parsed_url.netloc
        path = parsed_url.path or "/"

        # Extract title from URL or use domain
        title = url.split("/")[-1] or domain

        for index, doc in enumerate(documents):
            if doc.metadata is None:
                doc.metadata = {}

            # Generate document ID from domain + path + index
            document_id = f"web_{domain}_{path.replace('/', '_')}_{index}".lower()

            # Compute content hash
            content_hash = self.compute_content_hash(doc.page_content)

            # Generate citations
            citations = self.generate_citations(
                title=title,
                author=domain,
                url=url,
                date=datetime.now().isoformat(),
                source_type="web",
            )

            # Update metadata
            doc.metadata.update(
                {
                    # Document identification
                    "document_id": document_id,
                    "document_type": "web_page",
                    "chunk_index": index,
                    
                    # Web info
                    "source_url": url,
                    "domain": domain,
                    "url_path": path,
                    
                    # Content integrity
                    "content_hash": content_hash,
                    
                    # Citation metadata
                    "title": title,
                    "author": domain,
                    "description": description or f"Web content from {domain}",
                    
                    # Timestamps
                    "ingestion_timestamp": datetime.now().isoformat(),
                    "fetched_date": datetime.now().isoformat(),
                    
                    # Citations
                    **citations,
                    
                    # Source tracking
                    "source_type": "web",
                    "source": "web_url",
                }
            )

        return documents

    def process_web_urls(
        self,
        urls: List[str],
        description: Optional[str] = None,
    ) -> List[Document]:
        """
        Load and chunk documents from web URLs.

        Args:
            urls: List of URLs to process
            description: Optional description

        Returns:
            List of chunked Document objects
        """
        # Load documents
        documents = self.load_from_web(
            urls=urls,
            description=description,
        )

        # Chunk the documents
        chunks = self.chunk_documents(documents)
        print(f"Created {len(chunks)} chunks from web URLs")

        return chunks
