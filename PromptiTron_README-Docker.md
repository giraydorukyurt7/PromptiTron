# PromptiTron Docker Deployment

This guide explains how to run PromptiTron with Docker and Docker Compose.

## Prerequisites

Make sure the following are installed:

- Docker
- Docker Compose
- A valid Google API key for Gemini integration

## Environment Setup

Copy the Docker environment template if your project includes one:

```bash
cp .env.docker .env
```

Then edit `.env` and set the required values, for example:

```env
GOOGLE_API_KEY=your_google_api_key_here
GEMINI_MODEL=gemini-2.5-flash
TEMPERATURE=0.7
ENVIRONMENT=production
HOST=0.0.0.0
PORT=8000
CHROMA_HOST=chroma-db
CHROMA_PORT=8000
```

## Start the Services

### Full deployment

```bash
docker-compose up -d
```

### Check running services

```bash
docker-compose ps
```

### View logs

```bash
docker-compose logs -f
```

## Main Services

Typical services in the Docker setup include:

- **promptitron-api** — FastAPI backend
- **chroma-db** — vector database for retrieval
- **promptitron-worker** — background processing
- **promptitron-monitor** — monitoring / health endpoints
- **frontend** — optional web frontend, depending on compose configuration

## Local URLs

Typical access points:

- API docs: `http://localhost:8000/docs`
- API health: `http://localhost:8000/health`
- ChromaDB heartbeat: `http://localhost:8001/api/v1/heartbeat`
- Monitor health: `http://localhost:8002/health`

Use the actual ports defined in your compose files if they differ.

## Service Management

### Start selected services only

```bash
docker-compose up -d promptitron-api chroma-db
```

### Restart a service

```bash
docker-compose restart promptitron-worker
```

### Stop a service

```bash
docker-compose stop promptitron-monitor
```

## Rebuild After Changes

```bash
docker-compose build
docker-compose up -d
```

If you need a clean rebuild:

```bash
docker-compose build --no-cache
docker-compose up -d
```

## Health Checks

### API health

```bash
curl http://localhost:8000/health
```

### Monitor health

```bash
curl http://localhost:8002/health
```

### ChromaDB heartbeat

```bash
curl http://localhost:8001/api/v1/heartbeat
```

## Troubleshooting

### Port already in use

Check port usage:

```bash
netstat -tlnp | grep :8000
```

Or run a service on a different exposed port if needed.

### ChromaDB connection issue

Restart ChromaDB:

```bash
docker-compose restart chroma-db
```

Test internal connectivity:

```bash
docker-compose exec promptitron-api curl http://chroma-db:8000/api/v1/heartbeat
```

### Memory issues

Clean unused Docker resources:

```bash
docker system prune
```

## Backup Notes

If you persist ChromaDB data in a Docker volume, back it up before major changes.

Example:

```bash
docker volume ls
```

Use your own backup command depending on how volumes are named in your local setup.

## Stop and Clean Up

### Stop containers

```bash
docker-compose down
```

### Stop and remove volumes

```bash
docker-compose down -v
```

> Warning: removing volumes may delete persisted data.
