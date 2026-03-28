"""
Base loader utilities for citation generation, hashing, and chunk enrichment.
Shared across all loader modules.
"""

from typing import List, Optional, Dict, Any
from datetime import datetime
import hashlib

from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.documents import Document


class BaseLoader:
    """Base class with common utilities for all loaders."""

    def __init__(self, chunk_size: int = 1000, chunk_overlap: int = 200):
        """
        Initialize base loader.

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

    def compute_file_hash(self, file_path: str, algorithm: str = "sha256") -> str:
        """
        Compute hash of file for integrity verification.

        Args:
            file_path: Path to the file
            algorithm: Hash algorithm (sha256, md5)

        Returns:
            Hex digest of file hash
        """
        try:
            hash_obj = hashlib.new(algorithm)
            with open(file_path, "rb") as f:
                for chunk in iter(lambda: f.read(4096), b""):
                    hash_obj.update(chunk)
            return hash_obj.hexdigest()
        except Exception as e:
            print(f"⚠️ Could not compute file hash: {e}")
            return ""

    def compute_content_hash(self, content: str) -> str:
        """
        Compute hash of content for deduplication.

        Args:
            content: Text content

        Returns:
            MD5 hash of content
        """
        return hashlib.md5(content.encode()).hexdigest()

    def generate_citations(
        self,
        title: str,
        author: Optional[str] = None,
        url: Optional[str] = None,
        date: Optional[str] = None,
        source_type: str = "web",
    ) -> Dict[str, str]:
        """
        Generate citation strings in multiple formats.

        Args:
            title: Document title
            author: Author name
            url: Source URL
            date: Publication/Access date
            source_type: Type of source (web, file, github, etc.)

        Returns:
            Dictionary with citation formats
        """
        author_str = author or "Unknown Author"
        date_str = date or datetime.now().strftime("%Y-%m-%d")
        
        # Extract year from date
        year = date_str.split("-")[0] if date_str else datetime.now().year
        
        # APA format: Author (Year). Title. Retrieved from URL
        apa = f"{author_str} ({year}). {title}."
        if url:
            apa += f" Retrieved from {url}"
        
        # MLA format: Author. "Title." URL. Accessed date.
        mla = f'{author_str}. "{title}."'
        if url:
            mla += f" {url}."
        mla += f" Accessed {date_str}."
        
        # Chicago format
        chicago = f"{author_str}. \"{title}.\" Accessed {date_str}."
        if url:
            chicago += f" {url}."
        
        # BibTeX format
        bibtex = f"""@misc{{{hashlib.md5(title.encode()).hexdigest()[:8]},
  author = {{{author_str}}},
  title = {{{title}}},
  year = {{{year}}},
  url = {{{url or "N/A"}}},
  note = {{Accessed: {date_str}}}
}}"""
        
        return {
            "citation_apa": apa,
            "citation_mla": mla,
            "citation_chicago": chicago,
            "citation_bibtex": bibtex,
        }

    def enrich_chunks_with_metadata(
        self,
        chunks: List[Document],
        document_id: Optional[str] = None,
    ) -> List[Document]:
        """
        Enhance chunks with comprehensive tracking and citation metadata.

        Adds:
        - document_id: Unique identifier for source document
        - chunk_number: Sequential position
        - content_hash: MD5 hash for deduplication
        - byte_offset: Approximate byte position
        - retrieval_url: How to reference this chunk

        Args:
            chunks: List of chunked Document objects
            document_id: Optional document ID

        Returns:
            Chunks with comprehensive metadata
        """
        # Generate document ID if not provided
        if not document_id:
            first_content = chunks[0].page_content if chunks else ""
            document_id = f"doc_{hashlib.md5(first_content.encode()).hexdigest()[:12]}"

        # Track byte positions for retrieval
        byte_positions = [0]
        for chunk in chunks[:-1]:
            byte_positions.append(byte_positions[-1] + len(chunk.page_content.encode("utf-8")))

        for chunk_num, chunk in enumerate(chunks):
            if chunk.metadata is None:
                chunk.metadata = {}

            # Compute content hash for deduplication
            content_hash = self.compute_content_hash(chunk.page_content)

            # Add retrieval metadata
            chunk.metadata.update({
                # Document tracking
                "document_id": document_id,
                "chunk_number": chunk_num,
                "total_chunks": len(chunks),
                "chunk_content": chunk.page_content,
                
                # Integrity verification
                "content_hash": content_hash,
                "content_length": len(chunk.page_content),
                
                # Position information
                "byte_offset": byte_positions[chunk_num] if chunk_num < len(byte_positions) else 0,
                
                # Retrieval references
                "chunk_id": f"{document_id}_chunk_{chunk_num}",
                "retrieval_url": f"chroma://doc/{document_id}/{chunk_num}",
                
                # Temporal tracking
                "indexed_timestamp": datetime.now().isoformat(),
            })

        return chunks

    def chunk_documents(self, documents: List[Document], document_ids: Optional[List[str]] = None) -> List[Document]:
        """
        Split documents into chunks with enhanced metadata tracking.

        Args:
            documents: List of Document objects to chunk
            document_ids: Optional list of document IDs

        Returns:
            List of chunked Document objects with metadata
        """
        all_chunks = []

        for idx, doc in enumerate(documents):
            # Chunk individual documents
            chunks = self.text_splitter.split_documents([doc])

            # Get document ID from metadata or generate
            doc_id = document_ids[idx] if document_ids and idx < len(document_ids) else None
            if not doc_id and doc.metadata:
                doc_id = doc.metadata.get("document_id")

            # Enrich chunks with metadata
            enriched_chunks = self.enrich_chunks_with_metadata(chunks, doc_id)
            all_chunks.extend(enriched_chunks)

        return all_chunks
