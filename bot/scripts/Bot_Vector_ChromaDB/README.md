# Document Ingestion to ChromaDB with Metadata

This system loads documents from multiple sources (local files, web, GitHub, SharePoint, Google Drive), chunks them, and stores them in a remote ChromaDB instance with comprehensive metadata tracking for semantic search and document retrieval capabilities.

## Supported Sources

- **Local Files**: `.txt`, `.md`, `.pdf` files and directories
- **Web**: HTML content from URLs
- **GitHub**: Repository files with configurable extensions
- **SharePoint**: Microsoft SharePoint documents
- **Google Drive**: Files from Google Drive folders

## Setup

### 1. Environment Variable
Set your ChromaDB URL as an environment variable:

```bash
export CHROMADB_URL=http://localhost:8000
```

Or specify it directly in your code.

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Source-Specific Setup

#### Google Drive
1. Create a Google Cloud project and enable the Google Drive API
2. Create a service account or OAuth 2.0 credentials
3. Download credentials as JSON and save as `credentials.json` in your working directory
4. See: https://developers.google.com/docs/api/quickstart/python

#### SharePoint
1. Ensure you have access to the SharePoint site
2. Have your username and password ready (or use app-specific password)
3. Provide the site URL for authentication

#### GitHub
1. No special setup required for public repositories
2. For private repositories, set GitHub token as environment variable:
   ```bash
   export GITHUB_TOKEN=your_github_token
   ```

## Architecture

### Components

1. **train_file.py** (`DocumentProcessor`)
   - Loads documents from multiple sources
   - Supports local files (`.txt`, `.md`, `.pdf`)
   - Web URLs, GitHub repos, SharePoint, Google Drive
   - Chunks documents using `RecursiveCharacterTextSplitter`
   - Automatically extracts and attaches source-specific metadata
   - Configurable chunk size and overlap

2. **chroma_handler.py** (`ChromaDBHandler`)
   - Connects to remote ChromaDB server
   - Creates/manages collections
   - Adds documents with full metadata
   - Performs semantic searches with metadata retrieval
   - Retrieves individual document information

3. **main.py** (`RAGPipeline`)
   - Orchestrates the full ingestion pipeline
   - Ties together document processing and ChromaDB storage
   - Provides search with rich metadata display
   - CLI interface with multiple commands

## Metadata Tracking

Each document chunk automatically captures and stores comprehensive metadata for citation, retrieval, and integrity verification:

### Document & Chunk Tracking Metadata

| Field | Description | Example |
|---|---|---|
| `document_id` | Unique identifier for source document | `doc_a1b2c3d4e5f6` |
| `chunk_id` | Unique ID for this chunk | `doc_a1b2c3d4e5f6_chunk_2` |
| `chunk_number` | Position of chunk in sequence (0-indexed) | `0`, `1`, `2` |
| `total_chunks` | Total number of chunks from this document | `5` |
| `chunk_content` | Full text content of the chunk | `"The first paragraph..."` |
| `retrieval_url` | URL to retrieve this specific chunk | `chroma://doc/doc_a1b2c3d4e5f6/2` |

### Citation & Reference Metadata

| Field | Description | Example |
|---|---|---|
| `title` | Document title | `Q4 Financial Report` |
| `author` | Author/Creator name | `John Smith` |
| `description` | User-provided description | `Quarterly financial summary` |
| `citation_apa` | Pre-formatted APA citation | `Smith, J. (2025). Q4 Financial Report...` |
| `citation_mla` | Pre-formatted MLA citation | `Smith, John. "Q4 Financial Report." ...` |
| `citation_chicago` | Pre-formatted Chicago citation | `Smith, John. "Q4 Financial Report." ...` |
| `citation_bibtex` | Pre-formatted BibTeX entry | `@misc{...}` |

### Integrity Verification Metadata

| Field | Description | Example |
|---|---|---|
| `content_hash` | MD5 hash of chunk content | `a1b2c3d4e5f6g7h8` |
| `source_hash` | SHA256 hash of source file | `x1y2z3a4b5c6d7e8f9...` |
| `encoding` | Character encoding | `utf-8` |
| `content_length` | Length of chunk in characters | `1245` |

### Temporal & Source Metadata

| Field | Description | Example |
|---|---|---|
| `obtained_date` | When source was accessed | `2025-03-15T10:30:00` |
| `ingestion_timestamp` | When added to system | `2025-03-15T10:35:22` |
| `indexed_timestamp` | When chunk was indexed | `2025-03-15T10:35:25` |
| `modified_date` | Last modification time | `2025-03-12T15:45:00` |
| `created_date` | File creation time | `2025-03-10T09:00:00` |

### Local Files Metadata

| Field | Description | Example |
|---|---|---|
| `source_type` | Type of source | `file` |
| `file_name` | Name of the source file | `report.pdf` |
| `file_path` | Full absolute path to file | `/Users/john/docs/report.pdf` |
| `file_type` | File extension | `.pdf` |
| `file_size_bytes` | Size in bytes | `245632` |
| `mime_type` | MIME type | `application/pdf` |
| `byte_offset` | Byte position in file | `1024` |

### Web Metadata

| Field | Description | Example |
|---|---|---|
| `source_type` | Type of source | `web` |
| `url` | Source URL | `https://docs.example.com/guide` |
| `obtained_date` | Ingestion date (ISO) | `2025-03-15T10:30:00` |
| `description` | Custom description | `API Documentation` |

### GitHub Metadata

| Field | Description | Example |
|---|---|---|
| `source_type` | Type of source | `github` |
| `repository_url` | GitHub repository URL | `https://github.com/user/repo` |
| `obtained_date` | Ingestion date (ISO) | `2025-03-15T10:30:00` |
| `description` | Custom description | `Project Documentation` |

### SharePoint Metadata

| Field | Description | Example |
|---|---|---|
| `source_type` | Type of source | `sharepoint` |
| `sharepoint_url` | SharePoint site URL | `https://company.sharepoint.com/sites/project` |
| `obtained_date` | Ingestion date (ISO) | `2025-03-15T10:30:00` |
| `description` | Custom description | `Project Documents` |

### Google Drive Metadata

| Field | Description | Example |
|---|---|---|
| `source_type` | Type of source | `google_drive` |
| `folder_id` | Google Drive folder ID | `1abc2def3ghi4jkl5mno` |
| `obtained_date` | Ingestion date (ISO) | `2025-03-15T10:30:00` |
| `description` | Custom description | `Team Shared Documents` |

## Usage

### Python API

#### Local Files
```python
from main import RAGPipeline

pipeline = RAGPipeline(collection_name="documents")

# Single file
pipeline.ingest_documents(
    file_path="./document.txt",
    description="Product specification"
)

# Directory
pipeline.ingest_documents(
    directory_path="./documents",
    file_type="pdf",
    description="2025 Reports"
)
```

#### Web URLs
```python
pipeline.ingest_documents(
    web_urls=[
        "https://docs.example.com/guide",
        "https://blog.example.com/article"
    ],
    description="API Documentation"
)
```

#### GitHub Repository
```python
pipeline.ingest_documents(
    github_repo="https://github.com/owner/repo",
    github_extensions=[".md", ".txt", ".py"],
    description="Project documentation"
)
```

#### SharePoint
```python
pipeline.ingest_documents(
    sharepoint_url="https://company.sharepoint.com/sites/project",
    sharepoint_folder="/Shared Documents",
    description="Project documents"
)
```

#### Google Drive
```python
pipeline.ingest_documents(
    google_drive_folder="1abc2def3ghi4jkl5mno6pqr7stu8vwx",
    description="Team documents"
)
```

#### Search Results (with metadata)
```python
results = pipeline.search("financial forecast", num_results=5)
stats = pipeline.get_stats()
```

### Command Line

#### Local Files
```bash
# Single file
python main.py ingest --file ./data/report.pdf --description "Sales Report"

# Directory
python main.py ingest --dir ./documents --type pdf --description "Legal docs"
```

#### Web
```bash
python main.py ingest --web https://docs.example.com https://blog.example.com
```

#### GitHub
```bash
python main.py ingest --github https://github.com/owner/repo --github-extensions .md,.txt,.py
```

#### SharePoint
```bash
python main.py ingest --sharepoint https://company.sharepoint.com/sites/project --sharepoint-folder "/Shared Documents"
```

#### Google Drive
```bash
python main.py ingest --google-drive "1abc2def3ghi4jkl5mno6pqr7stu8vwx"
```

#### Search & Stats
```bash
python main.py search --query "budget allocation" --results 10
python main.py stats
python main.py interactive
```

### Interactive Mode
```bash
python main.py interactive
```

Available commands:
```
>> ingest           # Follow prompts for source
>> search           # Enter query and result count
>> stats            # View collection statistics
>> help             # Show available commands
>> exit             # Exit interactive mode
```

## Search Results Format

Search results include comprehensive citations, document tracking, and source-specific metadata:

### Local File Result
```
Result 1 (Similarity: 0.8934)
==================================================
📚 Citation (APA):
   Smith, J. (2025). Q4 Financial Report. Retrieved from file:///Users/john/documents/report.pdf

📄 Metadata:
   📋 Document ID: doc_a1b2c3d4e5f6
          Chunk ID: doc_a1b2c3d4e5f6_chunk_2
   🔗 Chunk: 2/5
   Source Type: file
   File: report.pdf
   Path: /Users/john/documents/report.pdf
   Type: .pdf
   ✓ Content Hash: a1b2c3d4e5f6g7h8...
   Size: 2450123 bytes
   Modified: 2025-03-12T15:45:23.123456
   📌 Indexed: 2025-03-15T10:35:25.123456
   📝 Description: Q4 2025 Financial Report
   📖 Also available: MLA, Chicago, BibTeX

📄 Content Preview:
   The quarterly financial report shows strong growth in sales...
```

### Web Source Result
```
Result 2 (Similarity: 0.8750)
==================================================
📚 Citation (APA):
   docs.example.com (2025). API Documentation. Retrieved from https://docs.example.com/guide

📄 Metadata:
   📋 Document ID: doc_x7y8z9a0b1c2
          Chunk ID: doc_x7y8z9a0b1c2_chunk_1
   🔗 Chunk: 1/3
   Source Type: web
   🌐 URL: https://docs.example.com/guide
       Domain: docs.example.com
   ✓ Content Hash: x7y8z9a0b1c2d3e4...
   ⏱️  Obtained: 2025-03-15T10:30:00
   📌 Indexed: 2025-03-15T10:35:22.123456
   📝 Description: API Documentation
   📖 Also available: MLA, Chicago, BibTeX

📄 Content Preview:
   API endpoints are documented below...
```

### GitHub Result
```
Result 3 (Similarity: 0.8600)
==================================================
📚 Citation (APA):
   user (2025). GitHub: user/repo. Retrieved from https://github.com/user/repo

📄 Metadata:
   📋 Document ID: doc_m5n6o7p8q9r0
          Chunk ID: doc_m5n6o7p8q9r0_chunk_3
   🔗 Chunk: 3/8
   Source Type: github
   🐙 Repository: https://github.com/user/repo
       Owner: user
   ✓ Content Hash: m5n6o7p8q9r0s1t2...
   Integrity: m5n6o7p8q9r0s1t2u3v4w5x6y7z8a...
   ⏱️  Obtained: 2025-03-15T10:30:00
   📌 Indexed: 2025-03-15T10:35:23.123456
   📝 Description: Project documentation
   📖 Also available: MLA, Chicago, BibTeX

📄 Content Preview:
   README: This project provides...
```

## Configuration

### DocumentProcessor
- `chunk_size`: Characters per chunk (default: 1000)
- `chunk_overlap`: Character overlap between chunks (default: 200)
- Supports automatic source-type metadata enrichment

### ChromaDBHandler
- `chromadb_url`: URL to ChromaDB server (env var: CHROMADB_URL)
- `collection_name`: Name of ChromaDB collection (default: "documents")

## Citation Support

Every document chunk includes pre-formatted citations in multiple formats (APA, MLA, Chicago, BibTeX) for easy referencing and bibliography generation.

### Accessing Citations

```python
from main import RAGPipeline

pipeline = RAGPipeline()
results = pipeline.search("financial analysis", num_results=5)

# Get citations for each result
for metadata in results["metadatas"][0]:
    print("APA:", metadata.get("citation_apa"))
    print("MLA:", metadata.get("citation_mla"))
    print("Chicago:", metadata.get("citation_chicago"))
    print("BibTeX:", metadata.get("citation_bibtex"))
```

### Citation Examples

**APA Format:**
```
Smith, J. (2025). Q4 Financial Report. Retrieved from file:///Users/john/docs/report.pdf
```

**MLA Format:**
```
Smith, John. "Q4 Financial Report." file:///Users/john/docs/report.pdf. Accessed 2025-03-15.
```

**Chicago Format:**
```
Smith, John. "Q4 Financial Report." Accessed 2025-03-15. file:///Users/john/docs/report.pdf.
```

**BibTeX Format:**
```bibtex
@misc{a1b2c3d4,
  author = {Smith, John},
  title = {Q4 Financial Report},
  year = {2025},
  url = {file:///Users/john/docs/report.pdf},
  note = {Accessed: 2025-03-15}
}
```

## Supported Sources

| Source | Setup Required | File Types | Metadata |
|---|---|---|---|
| Local Files | None | .txt, .md, .pdf | Name, path, size, dates, citations |
| Web URLs | None | HTML content | URL, ingestion date, citations |
| GitHub | Optional token | Configurable extensions | Repo URL, file list, citations |
| SharePoint | Username/Password | All formats | Site URL, folder path, citations |
| Google Drive | Service account/OAuth | All formats | Folder ID, file list, citations |

## Metadata Best Practices

1. **Descriptions**: Provide meaningful descriptions during ingestion for better discovery
2. **Source Type**: Automatically tracked; use for source-specific filtering
3. **Timestamps**: Captured for ingestion/modification dates; useful for freshness filtering
4. **Identifiers**: Preserve for linking back to original sources

## Example: Filtering by Source

After retrieving search results, filter by source type:

```python
from main import RAGPipeline

pipeline = RAGPipeline()
results = pipeline.search("data analysis", num_results=10)

# Separate results by source
for doc, metadata in zip(results["documents"][0], results["metadatas"][0]):
    source_type = metadata.get("source_type", "file")
    
    if source_type == "file":
        print(f"Local: {metadata.get('file_name')}")
    elif source_type == "web":
        print(f"Web: {metadata.get('url')}")
    elif source_type == "github":
        print(f"GitHub: {metadata.get('repository_url')}")
    elif source_type == "sharepoint":
        print(f"SharePoint: {metadata.get('sharepoint_url')}")
    elif source_type == "google_drive":
        print(f"Google Drive: {metadata.get('folder_id')}")
```

## Example: Accessing Document IDs and Chunk Information

Access document IDs, chunk positions, and full chunk content:

```python
from main import RAGPipeline

pipeline = RAGPipeline()
results = pipeline.search("budget", num_results=10)

# Access document tracking metadata
for doc_chunk, metadata in zip(results["documents"][0], results["metadatas"][0]):
    # Get document identifier
    doc_id = metadata.get("document_id")
    
    # Get chunk position
    chunk_num = metadata.get("chunk_number", 0)
    total_chunks = metadata.get("total_chunks", 1)
    
    # Get full chunk content (also available in doc_chunk)
    chunk_content = metadata.get("chunk_content")
    
    # Get source information
    source = metadata.get("source_type", "file")
    description = metadata.get("description")
    
    print(f"Document: {doc_id} | Chunk: {chunk_num + 1}/{total_chunks}")
    print(f"Source: {source} | Description: {description}")
    print(f"Content: {chunk_content[:200]}...\n")
```

### Retrieve All Chunks from a Specific Document

```python
from chroma_handler import ChromaDBHandler

handler = ChromaDBHandler()
handler.create_or_get_collection()

# Query for all chunks from a document
results = handler.collection.get(
    where={"document_id": "doc_a1b2c3d4e5f6"},
    include=["documents", "metadatas"]
)

# Get chunks in order
chunks_ordered = sorted(
    zip(results["documents"], results["metadatas"]),
    key=lambda x: x[1].get("chunk_number", 0)
)

# Reconstruct document content
full_content = "\n\n".join([chunk[0] for chunk in chunks_ordered])
print(f"Full document content:\n{full_content}")
```

## Error Handling

The pipeline validates:
- CHROMADB_URL is set
- Sources are accessible (URLs valid, files exist, credentials correct)
- ChromaDB server is accessible
- Documents are successfully loaded and stored
- Metadata is properly extracted and attached

## Advanced: Low-Level Access

```python
from train_file import DocumentProcessor
from chroma_handler import ChromaDBHandler

# Load from any source
processor = DocumentProcessor()
chunks = processor.load_from_web(
    urls=["https://docs.example.com"],
    description="API docs"
)

# Store in ChromaDB
handler = ChromaDBHandler()
handler.create_or_get_collection()
handler.add_langchain_documents(chunks)

# Search with metadata
results = handler.search("query", num_results=5)
```

## API Reference

### Raw Document Loaders

```python
processor = DocumentProcessor()

# Local
processor.load_single_file(file_path)
processor.load_text_files(directory_path)
processor.load_pdf_files(directory_path)

# External
processor.load_from_web(urls, description)
processor.load_from_github(repo_url, file_extensions, description)
processor.load_from_sharepoint(sharepoint_url, folder_path, description)
processor.load_from_google_drive(folder_id, description)
```
    
delete_collection()
    # Delete the entire collection
```

### DocumentProcessor

```python
load_text_files(directory_path)
    # Load all .txt files
    
load_pdf_files(directory_path)
    # Load all .pdf files
    
load_single_file(file_path)
    # Load a single file with metadata
    
chunk_documents(documents)
    # Split documents into chunks
    
process_documents(file_path, directory_path, file_type, description)
    # Complete processing pipeline with metadata enrichment
```

## Tips

1. **Chunk Size**: Start with 1000 characters. Increase for longer documents, decrease for shorter.
2. **Overlap**: 20% overlap (200 chars for 1000-char chunks) works well for most cases.
3. **Descriptions**: Add descriptive text during ingestion for better context
4. **Collections**: Use different collections for different document sets
5. **Performance**: Batch ingestion is more efficient than one-by-one additions
6. **Metadata Filtering**: Use metadata in post-processing for fine-grained search results

## Troubleshooting

**"CHROMADB_URL environment variable must be set"**
- Set the environment variable: `export CHROMADB_URL=http://localhost:8000`

**"Connection refused"**
- Ensure ChromaDB Docker container is running
- Check that the URL and port are correct

**"No documents loaded"**
- Verify files exist at the specified path
- Check file extensions match the `file_type` parameter

**"Metadata not appearing in search results"**
- Ensure documents were ingested after metadata enhancements
- Check that ChromaDB configuration includes metadata in responses
