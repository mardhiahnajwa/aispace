"""
Main navigator script for the RAG Pipeline.
Orchestrates document loading, chunking, and ChromaDB storage with metadata.

Usage:
    python main.py ingest --file <path> [--description "text"]     # Ingest a single file
    python main.py ingest --dir <path> --type txt [--description]  # Ingest from directory
    python main.py search --query "your query" [--results 5]        # Search documents
    python main.py stats                                            # Get collection statistics
    python main.py interactive                                      # Interactive mode

Documents are automatically enriched with metadata including:
  - File name, path, type, and size
  - Creation and modification dates
  - Optional custom descriptions
  - Source tracking
"""

import os
import sys
import argparse
from pathlib import Path
from typing import Optional

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
        description: Optional[str] = None,
    ) -> int:
        """
        Load documents, chunk them, and store in ChromaDB.

        Args:
            file_path: Path to a single file
            directory_path: Path to a directory containing files
            file_type: Type of files ('txt' or 'pdf')
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
                
                # Display metadata if available
                if metadata:
                    print("📄 Metadata:")
                    if metadata.get("file_name"):
                        print(f"   File: {metadata.get('file_name')}")
                    if metadata.get("file_path"):
                        print(f"   Path: {metadata.get('file_path')}")
                    if metadata.get("file_type"):
                        print(f"   Type: {metadata.get('file_type')}")
                    if metadata.get("description"):
                        print(f"   Description: {metadata.get('description')}")
                    if metadata.get("file_size_bytes"):
                        print(f"   Size: {metadata.get('file_size_bytes')} bytes")
                    if metadata.get("modified_date"):
                        print(f"   Modified: {metadata.get('modified_date')}")
                
                print("\n📝 Content:")
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
    """Handle document ingestion."""
    if args.file and args.dir:
        print("❌ Cannot specify both --file and --dir")
        sys.exit(1)

    if not args.file and not args.dir:
        print("❌ Must specify either --file or --dir")
        sys.exit(1)

    try:
        pipeline.ingest_documents(
            file_path=args.file,
            directory_path=args.dir,
            file_type=args.type,
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

  ingest       - Load documents into ChromaDB
    --file     - Ingest a single file
    --dir      - Ingest from a directory
    --type     - File type: txt or pdf (default: txt)
    --description - Custom description for the document(s)

  search       - Search documents
    --query    - Search query (required)
    --results  - Number of results (default: 5)

  stats        - Show collection statistics

  interactive  - Enter interactive mode

  help         - Show this help

  exit         - Exit interactive mode

📝 Metadata Tracking:
All documents automatically capture:
  - File name, path, and type
  - File size and modification dates
  - Custom description (if provided)
  - Source tracking information
""")


def create_parser():
    """Create command-line argument parser."""
    parser = argparse.ArgumentParser(
        description="RAG Pipeline: Load documents and store in ChromaDB with metadata",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python main.py ingest --file documents/doc.txt --description "Product manual"
  python main.py ingest --dir ./documents --type pdf --description "Q4 2025 reports"
  python main.py search --query "machine learning" --results 10
  python main.py stats
  python main.py interactive
        """,
    )

    subparsers = parser.add_subparsers(dest="command", help="Commands")

    # Ingest command
    ingest_parser = subparsers.add_parser("ingest", help="Ingest documents")
    ingest_parser.add_argument("--file", help="Single file path")
    ingest_parser.add_argument("--dir", help="Directory path")
    ingest_parser.add_argument(
        "--type", default="txt", choices=["txt", "pdf"], help="File type"
    )
    ingest_parser.add_argument(
        "--description", help="Description of the document(s) being ingested"
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
