## Environment Setup

1. Copy `.env.example` to `.env`:
   ```bash
   cp .env.example .env
   ```
2. Update the `.env` file with secure passwords

## Running and Resetting the Database with Docker Compose

To start the database in the background:

```bash
docker compose up -d
```

To stop and remove all containers, networks, and volumes (full reset):

```bash
docker compose down -v
```

## Running Redis Database

To start Redis with Redis Stack:

```bash
docker run -d -p 6379:6379 --name redis-local redis/redis-stack:latest
```
