# JD → Project Feature Mapping

Use this as your interview cheat-sheet. For every JD line, know exactly
where in the code it's demonstrated and be ready to explain the "why",
not just the "what".

| JD requirement | Where it lives | Talking point |
|---|---|---|
| Distributed, highly available backend using Python and Node.js | `backend/` (FastAPI) + `gateway/` (Express) | Two independently deployable services in different languages, communicating over REST — shows you can work across a polyglot stack, not just one framework. |
| Custom Python-based ERP, multi-module data pipelines | `backend/app/models.py`, `routers/inventory.py`, `routers/orders.py` | Inventory and Orders are separate modules with a clear data flow: order creation decrements inventory, invalidates cache, and broadcasts an event — a mini pipeline. |
| Event-driven backend architecture | `websocket_manager.py` + broadcast calls in `orders.py` | Order/inventory writes emit events consumed by any connected client — the core of event-driven design, without needing a full Kafka/RabbitMQ setup for a demo. |
| RESTful and gRPC APIs | REST: all `/api/*` routes. gRPC: `grpc_service/notification.proto` + generated stubs | Be ready to explain *why* gRPC for this service specifically: internal, high-frequency, strongly-typed, doesn't need browser-readability like the public REST API does. |
| Advanced React.js patterns, SSR | `frontend/pages/dashboard.js` (`getServerSideProps`) | Explain the SSR data-fetch-then-hydrate flow, and why `/dashboard` is dynamic (`ƒ`) not static — data changes per-request, so you can't pre-render at build time. |
| Agentic AI (Google Antigravity-style) | `backend/app/ai_agent.py` | This is your strongest talking point — see `AGENT_DEEP_DIVE.md`-worthy explanation below: tool-calling pattern, provider abstraction, grounded answers, graceful degradation. |
| Bidirectional WebSockets | `backend/app/routers/ws.py`, `frontend/components/LiveFeed.js` | Server pushes events; client doesn't poll. Mention the single-instance limitation noted in `websocket_manager.py` and how you'd fix it (Redis Pub/Sub fan-out) for multi-instance deployments — shows you know the demo's limits. |
| PostgreSQL + MongoDB clusters | Postgres wired in; Mongo intentionally the "next feature" (see README) | Don't dodge this — say exactly what you'd add (an `events`/audit collection) and why Mongo fits that specific use case better than Postgres. |
| Redis caching, sub-millisecond critical endpoints | `redis_client.py`, `routers/dashboard.py` | Explain cache-aside pattern: read cache → miss → query DB → populate cache with TTL → subsequent writes actively invalidate the key (not just wait for TTL expiry). |
| CI/CD, Docker, scalable cloud deployment | `docker-compose.yml`, `.github/workflows/ci.yml`, per-service `Dockerfile`s | Walk through the CI pipeline stages: backend tests → gateway tests → frontend build+test → full docker compose build, all gated before merge. |
| OAuth 2.0, JWT, RBAC | `security.py`, `auth.py` (backend), `middleware/auth.js` (gateway) | You implemented JWT + RBAC fully; be honest that full OAuth2 (third-party identity provider flow) isn't wired in, and describe how you'd add Google/GitHub OAuth as a login option. |
| Clean, testable code, Jest + PyTest | `backend/tests/` (12 tests), `gateway/tests/` + `frontend/__tests__/` (8 tests) | All 20 tests pass; mention you used SQLite in-memory + a fake Redis for backend tests specifically so tests don't need real infra — a deliberate test-isolation choice. |
| Cloud infra (AWS/GCP), microservices, container orchestration | `docker-compose.yml` today; Render/Vercel deploy in README | Be upfront: this demo uses Render/Vercel (free-tier, simpler) instead of raw AWS/GCP/K8s. Say you know the docker-compose setup translates directly to ECS/Cloud Run/a K8s Deployment+Service per container — and offer to sketch that translation if asked. |

## Honesty is the strategy

Don't claim you've done things the project doesn't do (real OAuth2 SSO,
MongoDB, Kubernetes, LLM embeddings/vector search). Interviewers at this
level will probe exactly the gaps. The strongest answer is always:
**"I built X, deliberately left out Y for time, and here's precisely how
I'd add Y"** — that reads as an engineer who understands scope, not one
who got lucky with a demo.
