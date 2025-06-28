# Kronos Chat Application

A dockerized chat application that combines React frontend, FastAPI backend, PostgreSQL database, and Ollama AI integration.

## Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   React Frontend│    │   Kronos API    │    │     Ollama AI   │
│   (port 3001)  │◄──►│   (port 8000)   │◄──►│   (port 11434)  │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                                │
                                ▼
                       ┌─────────────────┐
                       │   PostgreSQL    │
                       │   (port 5432)   │
                       └─────────────────┘
```

## Services

- **Frontend**: React app with Tailwind CSS (http://localhost:3001)
- **Kronos API**: FastAPI backend with vector search (http://localhost:8000)
- **Ollama**: Local AI service for chat responses (http://localhost:11434)
- **PostgreSQL**: Database with pgvector extension
- **PgAdmin**: Database administration (http://localhost:8080)

## Quick Start

1. **Start all services:**
   ```bash
   docker-compose up --build
   ```

2. **Setup Ollama models (in another terminal):**
   ```bash
   # Pull recommended models
   ./scripts/ollama/manage-models.sh setup
   
   # Or pull specific models
   ./scripts/ollama/manage-models.sh pull llama3.2
   ```

3. **Access the applications:**
   - Chat Application: http://localhost:3001
   - API Documentation: http://localhost:8000/docs
   - Ollama API: http://localhost:11434

## Managing Ollama Models

Use the provided script to manage AI models:

```bash
# Show menu
./scripts/ollama/manage-models.sh

# Pull a specific model
./scripts/ollama/manage-models.sh pull mistral

# List available models
./scripts/ollama/manage-models.sh list

# Test a model
./scripts/ollama/manage-models.sh test llama3.2
```

## Recommended Models

- **llama3.2** - General purpose, good balance of speed and quality
- **codellama** - Specialized for programming tasks
- **mistral** - Fast and efficient
- **phi3** - Very small and fast for simple tasks

## Development

### Frontend Development
```bash
# Start just frontend for development
docker-compose up frontend

# The frontend automatically reloads on code changes
```

### Backend Development
```bash
# Start backend with dependencies
docker-compose up kronos postgres

# Logs
docker-compose logs -f kronos
```

### Database Access
- **PgAdmin**: http://localhost:8080
- **Direct connection**: localhost:5432

## Environment Variables

### Kronos API
- `OLLAMA_URL`: URL to Ollama service (default: http://172.10.0.9:11434)
- `PG_SERVER_HOST`: PostgreSQL host
- `PG_SERVER_PORT`: PostgreSQL port
- `PG_SERVER_NAME`: Database name
- `PG_SERVER_USER`: Database user
- `PG_SERVER_PASSWORD`: Database password

### Frontend
- `VITE_API_URL`: Kronos API URL (default: http://172.10.0.7:8000)

## Network Configuration

All services run on a custom bridge network (172.10.0.0/16):
- Apache: 172.10.0.2
- Planka: 172.10.0.3
- Wiki: 172.10.0.4
- PostgreSQL: 172.10.0.5
- PgAdmin: 172.10.0.6
- Kronos: 172.10.0.7
- Frontend: 172.10.0.8
- Ollama: 172.10.0.9

## Data Persistence

- `ollama_models`: Stores downloaded AI models
- `postgres_data`: Database files
- `pgadmin_data`: PgAdmin configuration

## Troubleshooting

### Ollama Issues
```bash
# Check if Ollama is running
docker ps | grep ollama

# Check Ollama logs
docker-compose logs ollama

# Test Ollama directly
curl http://localhost:11434/api/tags
```

### Frontend Issues
```bash
# Check if API is accessible
curl http://localhost:8000/health

# Check frontend logs
docker-compose logs frontend
```

### Database Issues
```bash
# Check database connection
docker-compose logs postgres

# Access database directly
docker exec -it postgres psql -U postgres
```

## API Endpoints

- `GET /` - Welcome message
- `GET /health` - Health check
- `POST /chat` - Send chat message
- `GET /ollama/status` - Check Ollama status
- `GET /conversations` - List conversations
- `GET /tags` - List tags
- `GET /memory` - Search memory

## GPU Support

Both Kronos and Ollama containers are configured with GPU support for faster AI processing. Make sure you have:
- NVIDIA Docker runtime installed
- Compatible GPU drivers

Without GPU, the containers will fall back to CPU processing.
