# Docker Deployment

Docker Compose setup for running multiple agents in containers.

## Quick Start

```bash
# 1. Copy environment template
cp .env.example .env

# 2. Edit .env with your settings
nano .env

# 3. Start all services
docker-compose up -d

# 4. View logs
docker-compose logs -f
```

---

## Files

### `docker-compose.yml`

Multi-service Docker Compose configuration.

**Includes:**
- Redis service (event streaming)
- SQL agent container
- RAG agent container
- Algorithm agent container

**Services:**

```yaml
services:
  redis:          # Redis for event streaming
  sql-agent:      # LangChain SQL agent
  rag-agent:      # LangChain RAG agent  
  algorithm-agent: # Hard-coded algorithm agent
```

---

### `Dockerfile.agent`

Dockerfile template for containerizing agents.

**Features:**
- Python 3.11 slim base
- Installs SDK dependencies
- Copies agent code
- Configurable via environment variables

**Build Custom Agent:**

```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy SDK and your agent
COPY python/ ./python/
COPY my_agent.py .

# Run your agent
CMD ["python", "my_agent.py"]
```

---

### `.env.example`

Environment variable template.

**Required:**
```bash
OPENAI_API_KEY=your-key-here
```

**Optional:**
```bash
API_URL=http://localhost:3000
REDIS_HOST=redis
REDIS_PORT=6379
REDIS_PASSWORD=
```

---

## Usage

### Start All Agents

```bash
docker-compose up -d
```

### Start Specific Agent

```bash
docker-compose up -d sql-agent
```

### View Logs

```bash
# All agents
docker-compose logs -f

# Specific agent
docker-compose logs -f sql-agent
```

### Stop Agents

```bash
docker-compose down
```

### Rebuild After Changes

```bash
docker-compose up -d --build
```

---

## Adding Your Own Agent

### Option 1: Add to docker-compose.yml

```yaml
services:
  my-agent:
    build:
      context: ..
      dockerfile: docker/Dockerfile.agent
    environment:
      - REDIS_HOST=redis
      - API_URL=http://host.docker.internal:3000
      - OPENAI_API_KEY=${OPENAI_API_KEY}
      - AGENT_TYPE=my_custom_agent
    depends_on:
      redis:
        condition: service_healthy
    volumes:
      - ../examples:/app/examples
      - ../python:/app/python
    command: python examples/my_custom_agent.py
    restart: unless-stopped
```

### Option 2: Create Custom Dockerfile

```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install dependencies
COPY ../requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy SDK
COPY ../python/ ./python/

# Copy your agent
COPY my_agent.py .

# Environment
ENV PYTHONPATH=/app

# Run
CMD ["python", "my_agent.py"]
```

Build and run:

```bash
docker build -t my-agent -f docker/Dockerfile.my-agent ..
docker run -e OPENAI_API_KEY=$OPENAI_API_KEY my-agent
```

---

## Networking

### Access Quest Agent Forge from Container

**Linux:**
```yaml
environment:
  - API_URL=http://host.docker.internal:3000
```

**macOS/Windows:**
```yaml
environment:
  - API_URL=http://host.docker.internal:3000
```

### Access Redis from Container

```yaml
environment:
  - REDIS_HOST=redis
  - REDIS_PORT=6379
```

---

## Volumes

Mount your code for development:

```yaml
volumes:
  - ../examples:/app/examples
  - ../python:/app/python
  - ./my_data:/app/data
```

Changes to mounted files take effect on restart.

---

## Health Checks

### Redis

```yaml
healthcheck:
  test: ["CMD", "redis-cli", "ping"]
  interval: 5s
  timeout: 3s
  retries: 5
```

### Agent

Add to your agent service:

```yaml
healthcheck:
  test: ["CMD", "python", "-c", "import redis; r = redis.Redis(host='redis'); r.ping()"]
  interval: 30s
  timeout: 10s
  retries: 3
```

---

## Scaling

Run multiple instances of an agent:

```bash
docker-compose up -d --scale sql-agent=3
```

All instances will consume from the same Redis consumer group, providing load balancing.

---

## Production Deployment

### Use Environment-Specific Compose Files

```bash
# Development
docker-compose -f docker-compose.yml up

# Production
docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d
```

### docker-compose.prod.yml

```yaml
version: '3.8'

services:
  redis:
    restart: always
    command: redis-server --appendonly yes --requirepass ${REDIS_PASSWORD}
  
  sql-agent:
    restart: always
    deploy:
      replicas: 3
      resources:
        limits:
          cpus: '0.5'
          memory: 512M
```

---

## Monitoring

### View Resource Usage

```bash
docker stats
```

### View Container Logs

```bash
docker-compose logs -f --tail=100 sql-agent
```

### Access Container

```bash
docker-compose exec sql-agent /bin/bash
```

---

## Troubleshooting

### Container Won't Start

```bash
# Check logs
docker-compose logs sql-agent

# Check if Redis is healthy
docker-compose ps
```

### Can't Connect to Quest

```bash
# Test from container
docker-compose exec sql-agent curl http://host.docker.internal:3000/api/agents

# Check network
docker-compose exec sql-agent ping host.docker.internal
```

### Redis Connection Failed

```bash
# Test Redis
docker-compose exec sql-agent redis-cli -h redis ping

# Check Redis logs
docker-compose logs redis
```

---

## Cleanup

```bash
# Stop and remove containers
docker-compose down

# Remove volumes
docker-compose down -v

# Remove images
docker-compose down --rmi all
```

---

## Examples

### Deploy Algorithm Agent Only

```bash
# Edit .env
cp .env.example .env
nano .env

# Start Redis + Algorithm Agent
docker-compose up -d redis algorithm-agent

# View logs
docker-compose logs -f algorithm-agent
```

### Deploy All Agents

```bash
docker-compose up -d
docker-compose ps
```

---

## Documentation

- **Getting Started:** [../docs/GETTING_STARTED.md](../docs/GETTING_STARTED.md)
- **Examples:** [../examples/README.md](../examples/README.md)

---

**Perfect for containerized deployment of your Quest agents!** 🐳
