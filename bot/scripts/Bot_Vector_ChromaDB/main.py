"""
Main navigator script for the RAG Pipeline.
Orchestrates document loading, chunking, and ChromaDB storage with metadata.

Usage:
    # Local files
    python main.py ingest --file <path> [--description "text"]     # Single file
    python main.py ingest --dir <path> --type txt [--description]  # Directory

    # Web & External Sources
    python main.py ingest --web <url> [<url2> ...] [--description] # Web URLs
    python main.py ingest --github <repo_url> [--description]      # GitHub repo
    python main.py ingest --sharepoint <url> [--description]       # SharePoint
    python main.py ingest --google-drive <folder_id> [--description] # Google Drive

    # Search & Stats
    python main.py search --query "your query" [--results 5]        # Search documents
    python main.py stats                                            # Get collection statistics
    python main.py interactive                                      # Interactive mode

Documents are automatically enriched with metadata including:
  - Source type and origin information
  - File details (name, path, type, size) for local files
  - URLs for web sources
  - Repository info for GitHub
  - SharePoint/Google Drive identifiers
  - Ingestion date and optional custom descriptions
"""

import os
import sys
import argparse
from pathlib import Path
from typing import Optional, List

from train_file import DocumentProcessor
from chroma_handler import ChromaDBHandler


class RAGPipeline:
    """Complete pipeline for document ingestion into ChromaDB."""

    def __init__(
        self,
        chromadb_url: Optional[str] = None,
        collection_name: str = "documents",
        chunk_size: int = 1000,
        chunk_overlap: int = 200,
    ):
        """
        Initialize the RAG pipeline.

        Args:
            chromadb_url: URL for ChromaDB (defaults to CHROMADB_URL env var)
            collection_name: Name of the ChromaDB collection
            chunk_size: Size of document chunks
            chunk_overlap: Overlap between chunks
        """
        self.doc_processor = DocumentProcessor(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
        )
        self.chroma_handler = ChromaDBHandler(
            chromadb_url=chromadb_url,
            collection_name=collection_name,
        )
        self.chroma_handler.create_or_get_collection()

    def ingest_documents(
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
    ) -> int:
        """
        Load documents from various sources, chunk them, and store in ChromaDB.

        Args:
            file_path: Path to a single local file
            directory_path: Path to a directory containing files
            file_type: Type of local files ('txt' or 'pdf')
            web_urls: List of web URLs to load
            github_repo: GitHub repository URL
            github_extensions: File extensions to load from GitHub
            sharepoint_url: SharePoint site URL
            sharepoint_folder: Specific SharePoint folder path
            google_drive_folder: Google Drive folder ID
            description: Optional description for the documents

        Returns:
            Number of chunks stored
        """
        try:
            # Load and chunk documents
            print("\n--- Processing Documents ---")
            chunks = self.doc_processor.process_documents(
                file_path=file_path,
                directory_path=directory_path,
                file_type=file_type,
                web_urls=web_urls,
                github_repo=github_repo,
                github_extensions=github_extensions,
                sharepoint_url=sharepoint_url,
                sharepoint_folder=sharepoint_folder,
                google_drive_folder=google_drive_folder,
                description=description,
            )

            # Store in ChromaDB
            print("\n--- Storing in ChromaDB ---")
            self.chroma_handler.add_langchain_documents(chunks)

            # Verify storage
            count = self.chroma_handler.get_collection_count()
            print(f"\n✓ Successfully stored {count} chunks in ChromaDB")

            return len(chunks)
        except Exception as e:
            print(f"✗ Error during ingestion: {e}")
            raise

    def search(self, query: str, num_results: int = 5) -> dict:
        """
        Search for documents in ChromaDB.

        Args:
            query: Search query
            num_results: Number of results to return

        Returns:
            Search results dictionary
        """
        print(f"\n--- Searching for: '{query}' ---")
        results = self.chroma_handler.search(query, num_results=num_results)

        if results["documents"] and results["documents"][0]:
            print(f"✓ Found {len(results['documents'][0])} results:\n")
            for i, (doc, distance, metadata) in enumerate(
                zip(
                    results["documents"][0],
                    results["distances"][0],
                    results["metadatas"][0] if results["metadatas"] else [],
                )
            ):
                print(f"{'=' * 80}")
                print(f"Result {i + 1} (Similarity: {1 - distance:.4f})")
                print(f"{'=' * 80}")
                
                # Display citation first
                if metadata:
                    if metadata.get("citation_apa"):
                        print("📚 Citation (APA):")
                        print(f"   {metadata.get('citation_apa')}\n")
                
                # Display metadata if available
                if metadata:
                    print("📄 Metadata:")
                    
                    # Document tracking info
                    if metadata.get("document_id"):
                        print(f"   📋 Document ID: {metadata.get('document_id')}")
                    if metadata.get("chunk_id"):
                        print(f"          Chunk ID: {metadata.get('chunk_id')}")
                    if metadata.get("chunk_number") is not None:
                        chunk_num = metadata.get("chunk_number")
                        total = metadata.get("total_chunks", "?")
                        print(f"   🔗 Chunk: {chunk_num + 1}/{total}")
                    
                    # Source information
                    source_type = metadata.get("source_type", "file")
                    print(f"   Source Type: {source_type}")
                    
                    if source_type == "file":
                        if metadata.get("file_name"):
                            print(f"   File: {metadata.get('file_name')}")
                        if metadata.get("file_path"):
                            print(f"   Path: {metadata.get('file_path')}")
                        if metadata.get("file_type"):
                            print(f"   Type: {metadata.get('file_type')}")
                        if metadata.get("source_hash"):
                            print(f"   Integrity: {metadata.get('source_hash')[:16]}...")
                        if metadata.get("file_size_bytes"):
                            print(f"   Size: {metadata.get('file_size_bytes')} bytes")
                        if metadata.get("modified_date"):
                            print(f"   Modified: {metadata.get('modified_date')}")
                    elif source_type == "web":
                        if metadata.get("url"):
                            print(f"   🌐 URL: {metadata.get('url')}")
                        if metadata.get("domain"):
                            print(f"       Domain: {metadata.get('domain')}")
                    elif source_type == "github":
                        if metadata.get("repository_url"):
                            print(f"   🐙 Repository: {metadata.get('repository_url')}")
                        if metadata.get("repository_owner"):
                            print(f"       Owner: {metadata.get('repository_owner')}")
                    elif source_type == "sharepoint":
                        if metadata.get("sharepoint_url"):
                            print(f"   📊 SharePoint: {metadata.get('sharepoint_url')}")
                        if metadata.get("site_name"):
                            print(f"       Site: {metadata.get('site_name')}")
                    elif source_type == "google_drive":
                        if metadata.get("folder_url"):
                            print(f"   ☁️  Folder: {metadata.get('folder_url')}")
                        if metadata.get("folder_id"):
                            print(f"       ID: {metadata.get('folder_id')}")
                    
                    # Integrity
                    if metadata.get("content_hash"):
                        print(f"   ✓ Content Hash: {metadata.get('content_hash')[:16]}...")
                    
                    # Temporal info
                    if metadata.get("obtained_date"):
                        print(f"   ⏱️  Obtained: {metadata.get('obtained_date')}")
                    if metadata.get("indexed_timestamp"):
                        print(f"   📌 Indexed: {metadata.get('indexed_timestamp')}")
                    
                    # Description
                    if metadata.get("description"):
                        print(f"   📝 Description: {metadata.get('description')}")
                    
                    # Additional citations available
                    citations_available = []
                    if metadata.get("citation_mla"):
                        citations_available.append("MLA")
                    if metadata.get("citation_chicago"):
                        citations_available.append("Chicago")
                    if metadata.get("citation_bibtex"):
                        citations_available.append("BibTeX")
                    if citations_available:
                        print(f"   📖 Also available: {', '.join(citations_available)}")
                
                print("\n📄 Content Preview:")
                print(f"   {doc[:300]}{'...' if len(doc) > 300 else ''}\n")
        else:
            print("✗ No results found")

        return results

    def get_stats(self) -> dict:
        """Get collection statistics."""
        count = self.chroma_handler.get_collection_count()
        return {"total_chunks": count, "collection": self.chroma_handler.collection_name}


def validate_chromadb_url():
    """Validate that CHROMADB_URL is set."""
    if not os.getenv("CHROMADB_URL"):
        print("❌ ERROR: CHROMADB_URL environment variable is not set")
        print("\nSet it with:")
        print("  export CHROMADB_URL=http://localhost:8000")
        print("\nOr pass it to your Docker/environment configuration")
        sys.exit(1)


def cmd_ingest(args, pipeline):
    """Handle document ingestion from multiple sources."""
    # Count how many sources are specified
    sources = [
        args.file,
        args.dir,
        args.web,
        args.github,
        args.sharepoint,
        args.google_drive,
    ]
    source_count = sum(1 for s in sources if s)

    if source_count != 1:
        print("❌ Must specify exactly one source: --file, --dir, --web, --github, --sharepoint, or --google-drive")
        sys.exit(1)

    try:
        # Parse GitHub extensions if provided
        github_extensions = None
        if args.github_extensions:
            github_extensions = args.github_extensions.split(",")

        pipeline.ingest_documents(
            file_path=args.file,
            directory_path=args.dir,
            file_type=args.type,
            web_urls=args.web,
            github_repo=args.github,
            github_extensions=github_extensions,
            sharepoint_url=args.sharepoint,
            sharepoint_folder=args.sharepoint_folder,
            google_drive_folder=args.google_drive,
            description=args.description,
        )
    except Exception as e:
        print(f"❌ Ingestion failed: {e}")
        sys.exit(1)


def cmd_search(args, pipeline):
    """Handle document search."""
    if not args.query:
        print("❌ Must provide --query")
        sys.exit(1)

    try:
        pipeline.search(args.query, num_results=args.results)
    except Exception as e:
        print(f"❌ Search failed: {e}")
        sys.exit(1)


def cmd_stats(args, pipeline):
    """Display collection statistics."""
    try:
        stats = pipeline.get_stats()
        print("\n📊 Collection Statistics:")
        print(f"  Collection Name: {stats['collection']}")
        print(f"  Total Chunks: {stats['total_chunks']}")
    except Exception as e:
        print(f"❌ Failed to get stats: {e}")
        sys.exit(1)


def cmd_interactive(args, pipeline):
    """Run interactive mode."""
    print("\n🤖 RAG Pipeline - Interactive Mode")
    print("Commands: ingest, search, stats, help, exit\n")

    while True:
        try:
            command = input(">> ").strip().split()
            if not command:
                continue

            if command[0] == "exit":
                print("Goodbye!")
                break
            elif command[0] == "help":
                print_help()
            elif command[0] == "ingest":
                file_path = input("File path (or 'dir' to use directory): ").strip()
                if file_path.lower() == "dir":
                    dir_path = input("Directory path: ").strip()
                    file_type = input("File type (txt/pdf): ").strip() or "txt"
                    description = input("Description (optional): ").strip() or None
                    pipeline.ingest_documents(
                        directory_path=dir_path,
                        file_type=file_type,
                        description=description,
                    )
                else:
                    description = input("Description (optional): ").strip() or None
                    pipeline.ingest_documents(file_path=file_path, description=description)
            elif command[0] == "search":
                query = input("Search query: ").strip()
                results = input("Number of results (default: 5): ").strip()
                num_results = int(results) if results.isdigit() else 5
                pipeline.search(query, num_results=num_results)
            elif command[0] == "stats":
                stats = pipeline.get_stats()
                print(f"\n📊 Collection: {stats['collection']}, Chunks: {stats['total_chunks']}")
            else:
                print(f"Unknown command: {command[0]}. Try 'help'")
        except KeyboardInterrupt:
            print("\nExiting...")
            break
        except Exception as e:
            print(f"❌ Error: {e}")


def print_help():
    """Print help information."""
    print("""
📖 RAG Pipeline Commands:

  ingest              - Load documents into ChromaDB
    --file            - Ingest a single local file
    --dir             - Ingest from a local directory
    --type            - File type: txt or pdf (default: txt)
    --web <urls>      - Ingest from web URLs (space-separated)
    --github <url>    - Ingest from GitHub repository
    --github-extensions - File extensions from GitHub (comma-separated)
    --sharepoint <url> - Ingest from SharePoint
    --sharepoint-folder - Specific folder path in SharePoint
    --google-drive <id> - Ingest from Google Drive folder
    --description     - Custom description for the document(s)

  search              - Search documents
    --query           - Search query (required)
    --results         - Number of results (default: 5)

  stats               - Show collection statistics

  interactive         - Enter interactive mode

  help                - Show this help

  exit                - Exit interactive mode

📝 Source Types & Metadata:
All documents automatically capture source-specific metadata:
  ✓ Local files: name, path, type, size, modification dates
  ✓ Web: source URL, ingestion date
  ✓ GitHub: repository URL, file extensions
  ✓ SharePoint: site URL, folder path
  ✓ Google Drive: folder ID, ingestion date
""")


def create_parser():
    """Create command-line argument parser."""
    parser = argparse.ArgumentParser(
        description="RAG Pipeline: Load documents from multiple sources and store in ChromaDB with metadata",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Local files
  python main.py ingest --file documents/doc.txt --description "Product manual"
  python main.py ingest --dir ./documents --type pdf --description "Q4 2025 reports"

  # Web sources
  python main.py ingest --web https://docs.example.com https://blog.example.com

  # GitHub
  python main.py ingest --github https://github.com/user/repo --github-extensions .md,.txt,.py

  # SharePoint
  python main.py ingest --sharepoint https://company.sharepoint.com/sites/project

  # Google Drive
  python main.py ingest --google-drive "1abc2def3ghi4jkl5mno6pqr7stu8vwx"

  # Search
  python main.py search --query "machine learning" --results 10
  python main.py stats
  python main.py interactive
  python main.py stats
  python main.py interactive
        """,
    )

    subparsers = parser.add_subparsers(dest="command", help="Commands")

    # Ingest command
    ingest_parser = subparsers.add_parser(
        "ingest",
        help="Ingest documents from various sources",
        description="Ingest documents from local files, web URLs, GitHub, SharePoint, or Google Drive"
    )
    
    # Local file sources
    ingest_parser.add_argument("--file", help="Single file path (local)")
    ingest_parser.add_argument("--dir", help="Directory path (local)")
    ingest_parser.add_argument(
        "--type", default="txt", choices=["txt", "pdf"], help="File type for local sources (default: txt)"
    )
    
    # Web sources
    ingest_parser.add_argument(
        "--web",
        nargs="+",
        help="Web URLs to ingest (space-separated)"
    )
    
    # GitHub sources
    ingest_parser.add_argument(
        "--github",
        help="GitHub repository URL (e.g., https://github.com/owner/repo)"
    )
    ingest_parser.add_argument(
        "--github-extensions",
        help="File extensions to load from GitHub (comma-separated, e.g., .md,.txt,.py)"
    )
    
    # SharePoint sources
    ingest_parser.add_argument(
        "--sharepoint",
        help="SharePoint site URL"
    )
    ingest_parser.add_argument(
        "--sharepoint-folder",
        help="Specific folder path within SharePoint"
    )
    
    # Google Drive sources
    ingest_parser.add_argument(
        "--google-drive",
        help="Google Drive folder ID"
    )
    
    # Common options
    ingest_parser.add_argument(
        "--description",
        help="Description of the document(s) being ingested"
    )

    # Search command
    search_parser = subparsers.add_parser("search", help="Search documents")
    search_parser.add_argument("--query", required=True, help="Search query")
    search_parser.add_argument(
        "--results", type=int, default=5, help="Number of results"
    )

    # Stats command
    subparsers.add_parser("stats", help="Show collection statistics")

    # Interactive command
    subparsers.add_parser("interactive", help="Interactive mode")

    return parser


def main():
    """Main execution function."""
    validate_chromadb_url()

    parser = create_parser()
    args = parser.parse_args()

    # Initialize pipeline
    pipeline = RAGPipeline(collection_name="documents")

    # Route to appropriate command
    if args.command == "ingest":
        cmd_ingest(args, pipeline)
    elif args.command == "search":
        cmd_search(args, pipeline)
    elif args.command == "stats":
        cmd_stats(args, pipeline)
    elif args.command == "interactive":
        cmd_interactive(args, pipeline)
    else:
        parser.print_help()


main()
