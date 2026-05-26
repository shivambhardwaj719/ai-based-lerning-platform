# AI Learning Platform

A comprehensive, production-grade, full-stack AI-native technical learning platform. This platform provides an immersive environment where students can solve coding problems, attend live competitive programming contests, receive personalized AI mentoring, and practice in cloud-based DevOps labs — all integrated into a modern, responsive web application.

The project is structured as a monorepo containing:
- **Frontend**: A high-performance, responsive UI built with Next.js 15, React 19, and Tailwind CSS.
- **Backend**: A robust, scalable microservices architecture powered by FastAPI, PostgreSQL, and Kafka.

---

## Table of Contents

- [Features](#features)
- [Tech Stack](#tech-stack)
- [Project Structure](#project-structure)
- [Quick Start](#quick-start)
- [Manual Setup](#manual-setup)
- [Environment Variables](#environment-variables)
- [API Reference](#api-reference)
- [Authentication](#authentication)
- [AI System](#ai-system)
- [Code Execution Engine](#code-execution-engine)
- [WebSocket Events](#websocket-events)
- [Testing](#testing)
- [Deployment](#deployment)
- [Monitoring](#monitoring)
- [Contributing](#contributing)

---

## Features

| Area | Details |
|---|---|
| **Auth** | JWT + refresh rotation, 5 OAuth providers (Google / GitHub / Discord / LinkedIn / Meta), TOTP 2FA, email OTP, RBAC (5 roles) |
| **Problems** | 8 languages, Docker-sandboxed execution, test-case evaluation, plagiarism detection |
| **AI Mentor** | LangGraph multi-agent: mentor, roadmap generator, code reviewer, debugger, mock interviewer |
| **RAG** | Qdrant vector search + OpenAI embeddings, indexed study materials |
| **Contests** | Real-time leaderboards over WebSocket, ICPC-style scoring, ELO rating |
| **Roadmaps** | Personalized learning paths with skill-gap analysis |
| **DevOps Labs** | Docker-compose-based sandboxed cloud labs with TTL |
| **Payments** | Stripe + Razorpay, plan tiers, usage quotas |
| **Search** | Elasticsearch full-text + tag filtering |
| **Notifications** | WebSocket push + email + Kafka fan-out |
| **Analytics** | DAU, streaks, leaderboards, per-problem stats |
| **Admin** | User management, content moderation, platform stats |

---

## Tech Stack

| Layer | Technology |
|---|---|
| **Frontend** | Next.js 15 (React 19), App Router, TypeScript |
| **UI & Styling**| Tailwind CSS v4, shadcn/ui, Framer Motion, Lucide Icons |
| **State Mgt** | Zustand, TanStack React Query |
| **IDE & Code** | Monaco Editor (`@monaco-editor/react`) |
| **API** | FastAPI 0.115 + Uvicorn/Gunicorn, Python 3.11 |
| **Database** | PostgreSQL 16 + pgvector (async SQLAlchemy 2.0) |
| **Cache** | Redis 7 (sessions, rate-limiting, leaderboards) |
| **Queue** | Apache Kafka (20+ topics, DLQ) |
| **Tasks** | Celery 5 + RedBeat scheduler (8 queues) |
| **Search** | Elasticsearch 8 |
| **Vector DB** | Qdrant |
| **AI** | LangGraph + LangChain + OpenAI / Anthropic Claude |
| **WebSockets** | FastAPI native WebSockets + Redis pub/sub |
| **Storage** | AWS S3 / MinIO |
| **Containers** | Docker + Kubernetes (HPA, Ingress, TLS) |
| **CI/CD** | GitHub Actions (lint → test → security → build → deploy) |
| **Monitoring** | Prometheus + Grafana + Loki + OpenTelemetry + Jaeger |

---

## Project Structure

```text
ai-learning-platform/
├── frontend/                   # Next.js 15 Client Application
│   ├── src/
│   │   ├── app/                # Next.js App Router (pages, layouts, api routes)
│   │   ├── components/         # Reusable UI components (shadcn, forms, layout)
│   │   ├── lib/                # Utilities, types, API client setup
│   │   ├── providers/          # React Context providers (Theme, Auth)
│   │   └── stores/             # Zustand state stores
│   ├── public/                 # Static assets
│   ├── package.json            # Frontend dependencies and scripts
│   └── next.config.ts          # Next.js configuration
│
├── backend/                    # FastAPI Server Application
│   ├── main.py                 # FastAPI app factory + lifespan
│   ├── core/                   # Infrastructure: DB, Redis, Kafka, ES, config, logging
│   ├── models/                 # SQLAlchemy ORM (User, Problem, Contest, Payment, Lab…)
│   ├── schemas/                # Pydantic v2 request/response models
│   ├── repositories/           # Repository pattern (generic CRUD + domain queries)
│   ├── auth/                   # JWT, OAuth, TOTP 2FA, RBAC, dependencies
│   ├── api/v1/                 # REST endpoints (auth, users, problems, contests, ai…)
│   ├── ai/                     # AI agents (LangGraph), RAG, and tools
│   ├── apps/                   # Domain-specific services (code execution, evaluation, etc.)
│   ├── websocket/              # Room manager + WS route handlers
│   ├── workers/                # Celery config + beat schedule + tasks
│   ├── events/                 # Kafka consumers, producers, handlers
│   ├── migrations/             # Alembic (async) migrations
│   ├── tests/                  # unit / integration / e2e
│   ├── deployment/             # Dockerfile, docker-compose, Nginx
│   └── kubernetes/             # K8s manifests + Helm chart
└── README.md                   # Project documentation
```

---

## Quick Start

**Prerequisites:** Docker 24+, Docker Compose v2, and Node.js 20+ (for frontend).

### 1. Start the Backend (Docker)

```bash
# 1. Clone the repository
https://github.com/shivambhardwaj719/ai-based-lerning-platform
cd ai-learning-platform

# 2. Setup backend environment
cd backend
cp .env.example .env
# Edit .env — fill in every REQUIRED value (see Environment Variables)

# 3. Start all backend services
docker compose -f deployment/docker-compose.yml up -d

# 4. Run database migrations
docker compose exec api alembic upgrade head

# 5. (Optional) Seed initial data
docker compose exec api python scripts/setup_db.py
```

### 2. Start the Frontend (Local Dev)

```bash
# 1. Open a new terminal and navigate to the frontend directory
cd frontend

# 2. Setup frontend environment
cp .env.example .env.local
# Update the variables as needed

# 3. Install dependencies
npm install

# 4. Start the development server
npm run dev
```

### 3. Access the Platform

- **Web Application**: [http://localhost:3000](http://localhost:3000)
- **Interactive API Docs (Swagger)**: [http://localhost:8000/docs](http://localhost:8000/docs)
- **Services**:
  - Flower (Celery): http://localhost:5555
  - Kafka UI: http://localhost:8080
  - Kibana / Grafana: http://localhost:5601 / http://localhost:3001
  - MinIO: http://localhost:9001

---

## Manual Setup

### Prerequisites

- Python 3.11+
- PostgreSQL 16 with `pgvector` extension
- Redis 7
- Apache Kafka
- Elasticsearch 8
- Qdrant
- Docker (for code execution sandbox)

### Install

```bash
# Using Poetry (recommended)
pip install poetry
poetry install

# OR using pip
pip install -r requirements.txt          # production
pip install -r requirements-dev.txt      # + dev/test tools
```

### Database

```bash
# Create the database
createdb ai_learning

# Run init SQL (extensions, roles)
psql ai_learning < deployment/init.sql

# Apply Alembic migrations
alembic upgrade head
```

### Run

```bash
# API server
uvicorn main:app --reload --host 0.0.0.0 --port 8000

# Celery worker (all queues)
celery -A workers.celery_app worker -Q default,high_priority,submissions,ai,analytics,notifications,payments,labs -c 4 --loglevel=info

# Celery beat scheduler
celery -A workers.celery_app beat --scheduler redbeat.RedBeatScheduler --loglevel=info

# Kafka consumers
python -m events.consumers
```

---

## Environment Variables

Copy `.env.example` to `.env` and fill in the required values.

**Required at startup — app refuses to start if missing:**

| Variable | Description |
|---|---|
| `APP_SECRET_KEY` | Min 32-char random hex — `openssl rand -hex 32` |
| `JWT_SECRET_KEY` | Min 32-char random hex — `openssl rand -hex 32` |
| `DATABASE_URL` | PostgreSQL asyncpg connection string |
| `REDIS_URL` | Redis connection string (include password) |
| `KAFKA_BOOTSTRAP_SERVERS` | Kafka broker address |
| `ELASTICSEARCH_URL` | Elasticsearch HTTP URL |
| `ELASTICSEARCH_PASSWORD` | Elasticsearch password |
| `CELERY_BROKER_URL` | Redis URL for Celery broker |
| `CELERY_RESULT_BACKEND` | Redis URL for Celery results |
| `QDRANT_URL` | Qdrant HTTP URL |

**Optional — feature disabled when absent:**

| Variable | Feature enabled when set |
|---|---|
| `OPENAI_API_KEY` / `ANTHROPIC_API_KEY` | AI mentor, roadmap, code review |
| `GOOGLE_CLIENT_ID` + `GOOGLE_CLIENT_SECRET` | Google OAuth login |
| `GITHUB_CLIENT_ID` + `GITHUB_CLIENT_SECRET` | GitHub OAuth login |
| `DISCORD_CLIENT_ID` + `DISCORD_CLIENT_SECRET` | Discord OAuth login |
| `SMTP_HOST` + `SMTP_PASSWORD` | Transactional email |
| `STRIPE_SECRET_KEY` | Stripe payments |
| `AWS_ACCESS_KEY_ID` + `AWS_SECRET_ACCESS_KEY` | S3 file storage |
| `ENCRYPTION_KEY` | Fernet field-level encryption |
| `SENTRY_DSN` | Sentry error tracking |

---

## API Reference

Interactive docs are available at `/docs` (Swagger UI) and `/redoc`.

### Base URL

```
http://localhost:8000/api/v1
```

### Key Endpoints

#### Auth
```
POST   /auth/register              Register a new user
POST   /auth/login                 Login (returns access + refresh tokens)
POST   /auth/refresh               Rotate refresh token
POST   /auth/logout                Invalidate session
POST   /auth/verify-email          Verify email with token
POST   /auth/forgot-password       Send password reset email
POST   /auth/reset-password        Set new password
GET    /auth/oauth/{provider}      Start OAuth flow
GET    /auth/oauth/{provider}/callback  OAuth callback
POST   /auth/2fa/setup             Enable TOTP 2FA
POST   /auth/2fa/verify            Verify TOTP code
GET    /auth/sessions              List active sessions
DELETE /auth/sessions/{id}         Revoke a session
```

#### Users
```
GET    /users/me                   Get own profile
PATCH  /users/me                   Update profile
GET    /users/{username}           Get public profile
GET    /users/leaderboard          Global leaderboard (top 100)
```

#### Problems
```
GET    /problems/                  List problems (filter by difficulty, tags)
GET    /problems/{id}              Get problem detail + test cases
POST   /problems/{id}/submit       Submit solution (dispatched via Kafka)
POST   /problems/run               Run code against custom input (sync)
GET    /problems/{id}/submissions  My submission history
```

#### Contests
```
GET    /contests/                  List upcoming / active contests
GET    /contests/{id}              Contest detail
POST   /contests/{id}/join         Register for contest
GET    /contests/{id}/leaderboard  Live leaderboard
GET    /contests/{id}/problems     Contest problem list
```

#### AI
```
POST   /ai/chat                    Chat with AI mentor (streaming SSE)
POST   /ai/roadmap/generate        Generate personalized roadmap
GET    /ai/roadmap/{id}            Get roadmap with progress
POST   /ai/code-review             Review code for quality/security
POST   /ai/debug                   AI debugging assistant
POST   /ai/interview/start         Start mock interview session
GET    /ai/recommendations         Personalized problem suggestions
```

#### Labs
```
GET    /labs/                      List available labs
POST   /labs/{id}/start            Provision a lab instance
GET    /labs/instances/            My active lab instances
DELETE /labs/instances/{id}        Stop and destroy a lab
```

#### Payments
```
GET    /payments/plans             List subscription plans
POST   /payments/checkout          Create Stripe checkout session
GET    /payments/subscription      Current subscription
DELETE /payments/subscription      Cancel subscription
GET    /payments/history           Payment history
POST   /payments/webhook           Stripe webhook (internal)
```

#### Search
```
GET    /search?q=binary+search     Full-text search (problems + users)
```

#### Admin
```
GET    /admin/stats                Platform KPIs
GET    /admin/users                User management
PATCH  /admin/users/{id}/role      Change user role
POST   /admin/users/{id}/ban       Ban a user
GET    /admin/audit-logs           Audit log viewer
GET    /admin/health               System health check
```

---

## Authentication

The platform uses **JWT access tokens** (15-minute TTL) and **refresh tokens** (30-day TTL with rotation).

```
Authorization: Bearer <access_token>
```

### Token Flow

```
POST /auth/login
  → Returns { access_token, refresh_token, expires_in }

POST /auth/refresh  { "refresh_token": "..." }
  → Returns new { access_token, refresh_token }
  → Old refresh token is immediately invalidated

POST /auth/logout
  → JTI blacklisted in Redis; all subsequent requests with this token fail
```

### Role Hierarchy

```
student  <  mentor  <  instructor  <  admin  <  super_admin
```

---

## AI System

Built on **LangGraph** stateful graphs with **MemorySaver** for multi-turn conversations.

### Agents

| Agent | Description |
|---|---|
| `MentorAgent` | Conversational tutor with RAG, hints, code execution tool |
| `RoadmapAgent` | Generates JSON learning path with nodes/edges |
| `CodeReviewAgent` | Security + quality analysis, returns score + feedback |
| `DebugAgent` | Identifies bugs and suggests fixes step-by-step |
| `InterviewAgent` | Mock FAANG-style interview with debrief scoring |
| `ProblemGenerator` | Generates new problems from a topic + difficulty |

### RAG Pipeline

```
User query → OpenAI text-embedding-3-small → Qdrant cosine search
→ Top-3 relevant chunks → Injected into LLM context → Response
```

Study materials are indexed via the `index_study_material` Celery task.

---

## Code Execution Engine

Each submission runs in an isolated Docker container:

- Network disabled (`--network none`)
- All capabilities dropped (`--cap-drop ALL`)
- `no-new-privileges` seccomp profile
- CPU quota: 50,000 µs per 100ms period
- Memory limit: 256 MB
- PID limit: 50
- Timeout: 10 seconds (configurable)

### Supported Languages

| Language | Image | Extension |
|---|---|---|
| Python 3.11 | `python:3.11-alpine` | `.py` |
| JavaScript (Node 20) | `node:20-alpine` | `.js` |
| TypeScript | `node:20-alpine` | `.ts` |
| Java 21 | `eclipse-temurin:21-alpine` | `.java` |
| Go 1.23 | `golang:1.23-alpine` | `.go` |
| Rust 1.82 | `rust:1.82-alpine` | `.rs` |
| C++ (GCC 13) | `gcc:13-alpine` | `.cpp` |
| Kotlin 2.0 | `eclipse-temurin:21-alpine` | `.kt` |

---

## WebSocket Events

Connect with a valid JWT via query param: `ws://localhost:8000/ws/...?token=<access_token>`

| Endpoint | Room | Events |
|---|---|---|
| `/ws/contest/{id}` | Contest room | `leaderboard_update`, `submission_result`, `chat` |
| `/ws/ai/stream` | Per-user | `ai_chunk`, `ai_done`, `ai_error` |
| `/ws/collaboration/{id}` | Shared editor | `code_delta`, `cursor_move`, `user_joined` |
| `/ws/notifications` | Per-user | `notification`, `submission_result` |
| `/ws/submission/{id}` | Per-submission | `status_update`, `result` |

---

## Testing

```bash
# Run all tests with coverage
pytest

# Unit tests only (no DB required)
pytest tests/unit/ -v

# Integration tests (requires running DB + Redis)
pytest tests/integration/ -v

# End-to-end tests
pytest tests/e2e/ -v -m e2e

# Coverage report
pytest --cov=. --cov-report=html
open htmlcov/index.html
```

Minimum coverage gate: **80%** (enforced in CI).

---

## Deployment

### Docker (Production)

```bash
# Build image
docker build -f deployment/Dockerfile -t ai-learning-api:latest .

# Run production stack
docker compose -f deployment/docker-compose.prod.yml up -d
```

### Kubernetes

```bash
# Apply namespace
kubectl apply -f kubernetes/namespaces/

# Create secrets (fill in kubernetes/secrets/api-secrets.yaml.example first)
kubectl apply -f kubernetes/secrets/
kubectl apply -f kubernetes/configmaps/

# Deploy application
kubectl apply -f kubernetes/deployments/
kubectl apply -f kubernetes/services/
kubectl apply -f kubernetes/ingress/
kubectl apply -f kubernetes/hpa/

# Monitor rollout
kubectl rollout status deployment/ai-learning-api -n ai-learning
```

### Helm (recommended for production)

```bash
helm upgrade --install ai-learning ./kubernetes/helm/ai-learning \
  --namespace ai-learning \
  --create-namespace \
  -f kubernetes/helm/ai-learning/values.yaml \
  --set image.tag=$(git rev-parse --short HEAD)
```

### CI/CD

GitHub Actions pipeline at `.github/workflows/ci.yml`:

```
Push → lint (ruff + mypy)
     → test (pytest, 80% coverage gate)
     → security (bandit + safety + trivy SARIF)
     → build (multi-platform Docker image → GHCR)
     → deploy-staging (auto on main branch)
     → deploy-production (manual approval)
```

---

## Monitoring

| Tool | Purpose | URL (local) |
|---|---|---|
| Prometheus | Metrics scraping | http://localhost:9090 |
| Grafana | Dashboards | http://localhost:3001 |
| Loki | Log aggregation | (via Grafana) |
| Jaeger | Distributed tracing | http://localhost:16686 |
| OpenTelemetry Collector | Telemetry pipeline | port 4317/4318 |
| Flower | Celery task monitor | http://localhost:5555 |

Key alerts configured in `monitoring/prometheus/alert_rules.yml`:
- API error rate > 5%
- P95 latency > 2s
- Database connections > 80% of pool
- Redis memory > 80%
- Celery queue backlog > 100 tasks

---

## Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feat/your-feature`
3. Install pre-commit hooks: `pre-commit install`
4. Write tests for new code
5. Ensure all checks pass: `ruff check . && mypy . && pytest`
6. Open a pull request against `main`

### Code Style

- **Formatter/Linter:** Ruff (`line-length = 100`)
- **Type checking:** mypy strict mode
- **Docstrings:** Only for non-obvious WHY, never restate what the code does
- **Async first:** All I/O must be `async/await`

---

## License

MIT License — see `LICENSE` for details.
