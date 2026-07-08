# ArmPilot-AI

An Arm64-first AI optimization platform for deploying, benchmarking, and auto-tuning open-source LLMs with intelligent performance recommendations.

## Architecture

- **backend/** — FastAPI + async SQLAlchemy (asyncpg / aiosqlite) + JWT auth.
  - `app/main.py` — application factory (CORS, middleware, exception handlers, lifespan).
  - `app/api/` — versioned REST routers (`/api/v1/...`) plus `/health` and a live-metrics websocket.
  - `app/services/` — business logic (benchmarks, optimization profiles, inference jobs, recommendations, reports, history, settings, metrics).
  - `app/models/` — SQLAlchemy ORM models; `app/schemas/` — Pydantic request/response models.
  - `app/auth/` — password hashing (bcrypt), JWT issue/verify, current-user dependency.
  - `app/inference/runtime.py` — pluggable inference runtime abstraction (echo placeholder by default; wire llama.cpp / ONNX Runtime / Ollama here).
- **frontend/** — Next.js 16 (App Router) + React 19 + Tailwind v4. Auth context, typed API client, dashboard with live metrics, benchmark CRUD, and recommendation views.

## Backend — run locally

```bash
cd backend
python -m venv .venv && source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env          # then set SECRET_KEY and DATABASE_URL
uvicorn app.main:app --reload
```

For a zero-infra local run, set `DATABASE_URL=sqlite+aiosqlite:///./armpilot.db` in `.env`.
Tables are created automatically on startup. Interactive API docs: `http://localhost:8000/docs`.

## Frontend — run locally

```bash
cd frontend
npm install
# Point the client at the backend (defaults to http://localhost:8000):
export NEXT_PUBLIC_API_URL=http://localhost:8000
npm run dev
```

App runs at `http://localhost:3000`. Register an account, then explore the dashboard.

## API surface (v1)

| Area | Endpoints |
| --- | --- |
| Auth | `POST /auth/register`, `POST /auth/login`, `GET /auth/me` |
| Benchmarks | `GET/POST /benchmark`, `GET/DELETE /benchmark/{id}` |
| Optimization | `GET/POST /optimization`, `GET/PATCH/DELETE /optimization/{id}` |
| Inference | `GET/POST /inference`, `GET/DELETE /inference/{id}` |
| Recommendations | `GET /recommendation/{benchmark_id}` |
| Reports | `GET/POST /reports`, `GET/DELETE /reports/{id}` |
| History | `GET /history` |
| Settings | `GET/PUT /settings`, `DELETE /settings/{key}` |
| Metrics | `GET /metrics`, `WS /api/v1/ws/metrics?token=...` |

All non-auth endpoints require a `Bearer` access token.
