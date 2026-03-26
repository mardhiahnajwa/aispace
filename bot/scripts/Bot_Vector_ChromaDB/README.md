# Document Ingestion to ChromaDB with Metadata

This system loads documents, chunks them, and stores them in a remote ChromaDB instance with comprehensive metadata tracking for semantic search and document retrieval capabilities.

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

## Architecture

### Components

1. **train_file.py** (`DocumentProcessor`)
   - Loads documents from files or directories
   - Supports `.txt`, `.md`, and `.pdf` formats
   - Chunks documents using `RecursiveCharacterTextSplitter`
   - Automatically extracts and attaches file metadata
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

Each document chunk automatically captures and stores:

| Metadata Field | Description | Example |
|---|---|---|
| `file_name` | Name of the source file | `report.pdf` |
| `file_path` | Full absolute path to the file | `/Users/john/docs/report.pdf` |
| `file_type` | File extension | `.pdf` |
| `file_size_bytes` | Size of the file in bytes | `245632` |
| `created_date` | File creation timestamp (ISO format) | `2025-03-12T14:30:00` |
| `modified_date` | Last modification timestamp | `2025-03-12T15:45:00` |
| `description` | Custom description (user-provided) | `Q4 2025 Financial Report` |
| `source` | Document source tracking | `document_import` |

## Usage

### Basic Usage with Metadata

```python
from main import RAGPipeline

# Initialize pipeline
pipeline = RAGPipeline(collection_name="documents")

# Ingest documents with description
pipeline.ingest_documents(
    file_path="./document.txt",
    description="Product specification manual"
)

# Or from a directory with description
pipeline.ingest_documents(
    directory_path="./documents",
    file_type="pdf",
    description="2025 Quarterly Reports"
)

# Search documents (results include full metadata)
results = pipeline.search("financial forecast", num_results=5)

# Get collection stats
stats = pipeline.get_stats()
```

### Command Line Usage

```bash
# Ingest a file with description
python main.py ingest --file ./data/report.pdf --description "Sales Report Q1"

# Ingest directory with description
python main.py ingest --dir ./documents --type pdf --description "Legal docs 2025"

# Search documents
python main.py search --query "budget allocation" --results 10

# View collection stats
python main.py stats

# Interactive mode
python main.py interactive
```

### Interactive Mode

```bash
python main.py interactive
```

Then use commands like:
```
>> ingest
File path (or 'dir' to use directory): document.txt
Description (optional): Marketing strategy document

>> search
Search query: market analysis
Number of results (default: 5): 5

>> stats

>> exit
```

### Advanced: Manual Control

```python
from train_file import DocumentProcessor
from chroma_handler import ChromaDBHandler

# Process documents with metadata
processor = DocumentProcessor(chunk_size=1000, chunk_overlap=200)
chunks = processor.process_documents(
    file_path="./report.pdf",
    description="Annual Performance Review"
)

# Store in ChromaDB (includes metadata)
handler = ChromaDBHandler(chromadb_url="http://localhost:8000")
handler.create_or_get_collection()
handler.add_langchain_documents(chunks)

# Search shows metadata automatically
results = handler.search("performance metrics", num_results=5)
print(results["metadatas"])  # View metadata from search results
```

## Search Results Format

Search results include comprehensive metadata:

```
Result 1 (Similarity: 0.8934)
==================================================
📄 Metadata:
   File: report.pdf
   Path: /Users/john/documents/report.pdf
   Type: .pdf
   Description: Q4 2025 Financial Report
   Size: 2450123 bytes
   Modified: 2025-03-12T15:45:23.123456

📝 Content:
   The quarterly financial report shows strong growth in...
```

## Configuration

### DocumentProcessor
- `chunk_size`: Characters per chunk (default: 1000)
- `chunk_overlap`: Character overlap between chunks (default: 200)

### ChromaDBHandler
- `chromadb_url`: URL to ChromaDB server (env var: CHROMADB_URL)
- `collection_name`: Name of ChromaDB collection (default: "documents")

## Supported File Types

- `.txt`: Plain text files
- `.md`: Markdown files
- `.pdf`: PDF documents (requires `pypdf`)

## Metadata Best Practices

1. **Descriptions**: Provide meaningful descriptions during ingestion to aid discovery
2. **Timestamps**: Automatically captured; use for document freshness filtering
3. **Source Tracking**: All documents marked with source for audit trails
4. **File Info**: Path and name preserved for document linking back to source

## Example: Filtering by Metadata

After retrieving search results, you can filter by metadata:

```python
results = pipeline.search("data analysis")

for doc, metadata in zip(results["documents"][0], results["metadatas"][0]):
    # Filter by file type
    if metadata.get("file_type") == ".pdf":
        print(f"PDF: {metadata.get('file_name')}")
    
    # Filter by date range
    modified = metadata.get("modified_date")
    if modified and "2025-03" in modified:
        print(f"Recently modified: {metadata.get('file_name')}")
```

## Error Handling

The pipeline validates:
- CHROMADB_URL is set
- Files/directories exist
- ChromaDB server is accessible
- Documents are successfully loaded and stored
- Metadata is properly extracted and attached

## API Reference

### RAGPipeline

```python
ingest_documents(file_path, directory_path, file_type, description)
    # Load documents, chunk them, and store in ChromaDB with metadata
    
search(query, num_results)
    # Search for similar documents (results include metadata)
    
get_stats()
    # Return collection statistics
```

### ChromaDBHandler

```python
create_or_get_collection()
    # Create or fetch the collection
    
add_documents(documents, ids, metadatas)
    # Add plain text documents with metadata
    
add_langchain_documents(langchain_docs)
    # Add LangChain Document objects (metadata extracted automatically)
    
search(query, num_results)
    # Query the collection (returns metadata with results)
    
get_document_info(doc_id)
    # Get detailed info about a specific document chunk
    
get_collection_count()
    # Get number of documents
    
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
