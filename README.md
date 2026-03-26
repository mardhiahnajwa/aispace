# AISpace

A comprehensive Django-based platform for building AI-related applications including RAG systems, AI agents, MCP servers, vector databases, and more.

## Requirements

### System Requirements
- Python 3.11+
- Docker and Docker Compose (for containerized deployment)

## Installation

### Option 1: Local Development Setup

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd aispace
   ```

2. **Create a virtual environment**
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables**
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

### Option 2: Docker Setup

1. **Build and run with Docker Compose**
   ```bash
   docker-compose up --build
   ```

## Running the Application

### Local Development
```bash
# Activate virtual environment
source venv/bin/activate

# Run migrations (if database is configured)
python manage.py migrate

# Start development server
python manage.py runserver
```

The application will be available at `http://localhost:8000`

### Docker
```bash
# Start services
docker-compose up

# Stop services
docker-compose down
```

The application will be available at `http://localhost:8000`

## Project Structure

- `agentic_rag/` - Agentic RAG (Retrieval-Augmented Generation) application module
- `langchain_agent/` - LangChain-based AI agent integration
- `bot/` - Bot application with ChromaDB vector database integration
- `aispace/` - Django project settings and configuration
- `inc/` - Shared utilities for database connections and integrations
