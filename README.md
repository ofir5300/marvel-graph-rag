# Marvel GraphRAG

## Development Setup

### Building and Running with Docker Compose

1. Copy and configure environment:

```bash
cp .env.example .env
# Edit .env with your settings
```

2. Build and start all services:

```bash
docker compose up --build
```

3. Access the API:

- Swagger UI: http://localhost:8000/docs
- API endpoints: http://localhost:8000/...

4. Stop and clean up:

```bash
docker compose down -v
```

### Local Development

1. Install Python 3.11.6:

```bash
pyenv install 3.11.6
pyenv local 3.11.6
```

2. Create and activate virtual environment:

```bash
python -m venv venv
source venv/bin/activate  # or `venv\Scripts\activate` on Windows
```

3. Install dependencies:

```bash
pip install -r requirements.txt
```

4. Start Local Databases:

```bash
# Start Redis
docker run -d -p 6379:6379 --name redis-local redis/redis-stack:latest

# Start Neo4j
docker run -d \
    -p 7474:7474 -p 7687:7687 \
    -e NEO4J_AUTH=neo4j/neo4jpassforprojectgeneforge123qweasdzxc \
    --name neo4j-local \
    neo4j:5.12.0
```

5. Set up environment variables:

```bash
cp .env.example .env
```

Edit `.env` with local settings:
