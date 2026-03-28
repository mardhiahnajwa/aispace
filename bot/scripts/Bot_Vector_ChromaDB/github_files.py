"""
GitHub repository loader for document extraction.
"""

from typing import List, Optional
from datetime import datetime

from langchain_community.document_loaders import GitHubRepositoryLoader
from langchain_core.documents import Document

from base_loader import BaseLoader


class GitHubLoader(BaseLoader):
    """Handles loading and processing of documents from GitHub repositories."""

    def load_from_github(
        self,
        repo_url: str,
        file_extensions: Optional[List[str]] = None,
        description: Optional[str] = None,
    ) -> List[Document]:
        """
        Load documents from a GitHub repository.

        Args:
            repo_url: GitHub repository URL (e.g., "https://github.com/owner/repo")
            file_extensions: List of file extensions to include (e.g., ['.md', '.py'])
            description: Optional user-provided description

        Returns:
            List of Document objects
        """
        print(f"Loading repository: {repo_url}")

        # Extract repo owner and name from URL
        parts = repo_url.rstrip("/").split("/")
        repo_name = parts[-1]
        repo_owner = parts[-2]

        # Convert URL to github org format expected by LangChain
        github_url = f"https://github.com/{repo_owner}/{repo_name}"

        # Determine file types to load
        if file_extensions is None:
            file_extensions = [".md", ".txt", ".py", ".js", ".ts", ".json", ".yaml", ".yml"]

        loader = GitHubRepositoryLoader(
            repo_url=github_url,
            file_filter=lambda x: any(x.endswith(ext) for ext in file_extensions),
            load_all_available_branches=False,
        )

        try:
            documents = loader.load()
        except Exception as e:
            print(f"Error loading from GitHub: {e}")
            raise

        if not documents:
            raise ValueError(f"No documents found in {github_url}")

        # Enrich with GitHub metadata
        enriched_docs = self.enrich_github_metadata(
            documents,
            repo_owner=repo_owner,
            repo_name=repo_name,
            repo_url=github_url,
            description=description,
        )

        print(f"Loaded {len(documents)} documents from GitHub")
        return enriched_docs

    def enrich_github_metadata(
        self,
        documents: List[Document],
        repo_owner: str,
        repo_name: str,
        repo_url: str,
        description: Optional[str] = None,
    ) -> List[Document]:
        """
        Add GitHub-specific metadata to documents.

        Args:
            documents: List of Document objects
            repo_owner: Repository owner
            repo_name: Repository name
            repo_url: Repository URL
            description: Optional user-provided description

        Returns:
            Documents with enriched metadata
        """
        for doc in documents:
            if doc.metadata is None:
                doc.metadata = {}

            # Extract file path from source
            file_path = doc.metadata.get("source", "unknown")

            # Generate document ID from repo + file path
            document_id = f"github_{repo_owner}_{repo_name}_{file_path}".replace("/", "_").replace(".", "_")

            # Compute content hash
            content_hash = self.compute_content_hash(doc.page_content)

            # Generate citations
            citations = self.generate_citations(
                title=f"{repo_owner}/{repo_name}: {file_path}",
                author=repo_owner,
                url=f"{repo_url}/blob/main/{file_path}",
                date=datetime.now().isoformat(),
                source_type="github",
            )

            # Update metadata
            doc.metadata.update(
                {
                    # Document identification
                    "document_id": document_id,
                    "document_type": "github_file",
                    
                    # Repository info
                    "repository_owner": repo_owner,
                    "repository_name": repo_name,
                    "repository_url": repo_url,
                    "file_path": file_path,
                    
                    # Content integrity
                    "content_hash": content_hash,
                    
                    # Citation metadata
                    "title": f"{repo_name}: {file_path}",
                    "author": repo_owner,
                    "description": description or f"Documentation from {repo_url}", 
                    
                    # Timestamps
                    "ingestion_timestamp": datetime.now().isoformat(),
                    
                    # Citations
                    **citations,
                    
                    # Source tracking
                    "source_type": "github",
                    "source": "github_repository",
                }
            )

        return documents

    def process_github_repo(
        self,
        repo_url: str,
        file_extensions: Optional[List[str]] = None,
        description: Optional[str] = None,
    ) -> List[Document]:
        """
        Load and chunk documents from a GitHub repository.

        Args:
            repo_url: GitHub repository URL
            file_extensions: List of file extensions to include
            description: Optional description

        Returns:
            List of chunked Document objects
        """
        # Load documents
        documents = self.load_from_github(
            repo_url=repo_url,
            file_extensions=file_extensions,
            description=description,
        )

        # Chunk the documents
        chunks = self.chunk_documents(documents)
        print(f"Created {len(chunks)} chunks from GitHub repository")

        return chunks
