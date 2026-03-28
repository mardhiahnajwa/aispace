# AISpace

Django-based platform for AI applications.

## Requirements

- Python 3.11+
- Docker and Docker Compose (optional)

## Local Setup

```bash
# Clone repository
git clone <repository-url>
cd aispace

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Set up environment variables
cp .env.example .env
```

## Running Locally

```bash
# Run migrations
python manage.py migrate

# Start development server
python manage.py runserver
```

Visit `http://localhost:8000`

## Docker Setup

```bash
# Build and run
docker-compose up --build

# Stop services
docker-compose down
```

Visit `http://localhost:8000`
