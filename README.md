CodeAtlas 

Principle Statement - 

Map your Code, Understand Everythiing

Base statement - 

CodeAtlas is an AI-powered codebase visualization platform that transforms complex repositories into interactive architectural maps. By analyzing source code, dependencies, and relationships, it helps developers understand, navigate, and reason about large software systems through intuitive visualizations and intelligent insights.

---

## Docker Infrastructure Setup

This project uses Docker and Docker Compose to containerize and orchestrate the local development environment. The services communicate with each other using Docker-defined service names within a shared custom bridge network.

### Prerequisites

Ensure you have the following installed on your machine:
- [Docker Desktop](https://www.docker.com/products/docker-desktop/) (which includes Docker Compose)

### Environment Configuration

Before launching the environment, create a `.env` file in the root directory by copying the template file:

```bash
cp .env.example .env
```

Open `.env` and configure the environment variables as needed:
- Add your `OPENAI_API_KEY` for AI features.
- Update `JWT_SECRET` for securing JWT tokens.
- Adjust PostgreSQL and Redis variables if necessary (defaults are preconfigured for instant start).

### Quick Start

To build the images and launch the entire local environment, run:

```bash
docker compose up --build
```

This command will:
1. Initialize the PostgreSQL database (`codeatlas-postgres`) and wait until it is healthy.
2. Initialize the Redis cache (`codeatlas-redis`) and wait until it is healthy.
3. Build and launch the FastAPI server (`codeatlas-server`) on port 8000.
4. Build and launch the FastAPI analysis engine (`codeatlas-analysis-engine`) on port 8001.
5. Build and launch the Next.js client (`codeatlas-client`) on port 3000.

### Exposed Ports & Access

| Service | Internal Port | Host Port | Endpoint / Access |
|---|---|---|---|
| **Next.js Client** | 3000 | `3000` | [http://localhost:3000](http://localhost:3000) |
| **FastAPI Backend Server** | 8000 | `8000` | [http://localhost:8000](http://localhost:8000) |
| **FastAPI Analysis Engine** | 8001 | `8001` | [http://localhost:8001](http://localhost:8001) |
| **PostgreSQL Database** | 5432 | `5432` | `localhost:5432` (User/Password: `postgres`) |
| **Redis Cache** | 6379 | `6379` | `localhost:6379` |

### Key Docker Design Decisions

1. **Multi-stage Next.js Build**: The client Dockerfile leverages multi-stage builds (`deps`, `builder`, `development`, `runner`) to keep the production image extremely lightweight, while supporting a hot-reloading `development` target.
2. **Anonymous Volume Mounts**: To prevent conflicts between host machine dependencies and the Linux Alpine client container, anonymous volume mounts are used for `/app/node_modules` and `/app/.next`.
3. **Layer Caching**: Both Python backend services copy only `requirements.txt` initially to build and cache dependencies. Re-building code changes occurs instantly since pip install is skipped unless dependencies change.
4. **Non-Root System Users**: For improved runtime security, all application services execute under non-root system users (`nextjs` for Next.js, `appuser` for FastAPI).
5. **Bridge Networking**: The containers are assigned to `codeatlas-network`. Services refer to each other by name (e.g. `http://codeatlas-server:8000`) instead of `localhost`.
6. **Health Checks & Start Ordering**: App services depend on Postgres and Redis being fully initialized and reporting "healthy" via Docker healthchecks before they spin up, preventing startup crashes.
7. **Built-in Python Health Check**: FastAPI services execute simple, native Python HTTP calls (`urllib.request`) to run healthchecks, avoiding image bloat from `curl`/`wget`.