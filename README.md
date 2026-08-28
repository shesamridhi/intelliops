# IntelliOps — AI-Augmented Mini ERP with Agentic Automation

A distributed, multi-service backend + React (SSR) frontend system built to
demonstrate the full stack of a modern full-stack/SDE role: event-driven
architecture, REST + gRPC APIs, agentic AI, WebSockets, caching, RBAC,
containerization, and CI.

## Why this project exists

This was built to match, feature-for-feature, a real full-stack developer
job description covering: Python + Node.js backends, an ERP-style data
model, RESTful + gRPC APIs, React SSR, agentic AI integration, WebSockets,
PostgreSQL + MongoDB-style data needs, Redis caching, Docker/CI-CD, and
OAuth2/JWT/RBAC security. Every item below maps directly to one of those
requirements — see [`JD_MAPPING.md`](./JD_MAPPING.md).

## Architecture

```
                        ┌─────────────────────┐
                        │   Next.js Frontend   │  (React SSR, port 3000)
                        │  login / dashboard   │
                        └──────────┬───────────┘
                                   │ REST + WebSocket
                        ┌──────────▼───────────┐
                        │   Node.js Gateway     │  (Express BFF, port 4000)
                        │  JWT verify, RBAC,    │
                        │  rate limit, proxy    │
                        └──────┬────────┬───────┘
                     REST/WS   │        │  gRPC (unary + streaming)
                        ┌──────▼───┐ ┌──▼─────────────────┐
                        │ FastAPI  │ │  gRPC Notification  │
                        │ Backend  │ │  Microservice        │
                        │ port 8000│ │  port 50051           │
                        └──┬───┬───┘ └─────────────────────┘
                  ┌────────┘   └────────┐
           ┌──────▼─────┐        ┌──────▼─────┐
           │ PostgreSQL │        │   Redis    │
           │ (source of │        │ (dashboard │
           │   truth)   │        │  cache)    │
           └────────────┘        └────────────┘
```

**Backend (Python / FastAPI)** — owns the data model (users, inventory,
orders), JWT issuance, RBAC enforcement, Redis-cached dashboard stats,
the WebSocket broadcast hub, and the agentic AI endpoint.

**Gateway (Node.js / Express)** — the single entry point the frontend
talks to. Terminates and re-verifies JWTs, applies a second layer of RBAC
(defense in depth), rate-limits, and proxies REST/WS traffic to the
backend. It's also the only service that speaks gRPC to the notification
microservice — showing Node.js consuming a Python-implemented gRPC
contract across the language boundary.

**gRPC Notification microservice (Python)** — a small, independently
deployable service exposing both a unary RPC (`SendNotification`) and a
server-streaming RPC (`StreamNotifications`), compiled from a real
`.proto` contract.

**Frontend (Next.js / React)** — `/dashboard` uses `getServerSideProps`
to fetch initial stats **on the server** on every request (true SSR, not
static generation — see the `ƒ` marker in the build output), then
hydrates into a client app that keeps a live WebSocket connection open
and lets the user chat with the AI ops agent.

**AI agent** — a tool-calling agent: the LLM (or a rule-based fallback
when no API key is configured) decides which internal "tool" to call
(`low_stock_items`, `pending_orders_count`, `inventory_value`), the tool
executes a real query against Postgres, and the answer is grounded in
that result — not hallucinated. Swapping `LLM_PROVIDER=openai|anthropic`
is a one-line config change.

## Why MongoDB isn't wired in (and how to add it)

The JD asks for both PostgreSQL and MongoDB experience. This project uses
Postgres as the relational source of truth (users/inventory/orders,
where referential integrity matters). The natural place for MongoDB is
an **audit/event log** (schemaless, high write-volume, no joins needed):
every order status change or agent query could be written to a
`events` collection. This is intentionally left as the most obvious
"next feature" to implement live in front of an interviewer — see
`JD_MAPPING.md` for the 15-minute version of this you can build on
request.

## Running locally

```bash
cp backend/.env.example backend/.env
cp gateway/.env.example gateway/.env
cp frontend/.env.example frontend/.env
docker compose up --build
```

- Frontend: http://localhost:3000
- Gateway: http://localhost:4000/health
- Backend docs (Swagger): http://localhost:8000/docs
- gRPC service: localhost:50051

Register a user at `/login` (toggle to "Create an account"), pick role
`admin` to unlock inventory creation, then explore the dashboard.

## Running tests

```bash
# Backend (12 tests: auth, RBAC, agent routing)
cd backend && pip install -r requirements.txt && pytest -v

# Gateway (5 tests: health, auth middleware, RBAC, validation)
cd gateway && npm install && npm test

# Frontend (3 tests: API client)
cd frontend && npm install && npm test
```

All 20 tests pass as of the last commit — verified in CI (see
`.github/workflows/ci.yml`), which also builds every Docker image.

## Deployment (free tier)

**Backend + Gateway + gRPC service → Render**
1. Push this repo to GitHub.
2. On Render: New → Web Service → connect repo → set root directory to
   `backend` (repeat for `gateway` and `grpc_service` as separate
   services). Render auto-detects the Dockerfile in each.
3. Add a Render PostgreSQL and Render Redis instance (free tier); copy
   their connection strings into the `backend` service's environment
   variables (`DATABASE_URL`, `REDIS_URL`).
4. Set `JWT_SECRET_KEY` to the same value on **both** `backend` and
   `gateway` (they must share the secret to verify each other's tokens).
5. Set `GRPC_NOTIFICATION_HOST`/`PORT` on `gateway` and `backend` to the
   internal Render hostname of the `grpc_service`.

**Frontend → Vercel**
1. Import the repo on Vercel, set root directory to `frontend`.
2. Set `NEXT_PUBLIC_GATEWAY_URL` to your deployed Render gateway URL.
3. Deploy — Vercel builds and serves the SSR pages automatically.

## Security notes (worth raising proactively in the interview)

- Passwords hashed with bcrypt; JWTs are short-lived (30 min access /
  7 day refresh) and signed with HS256 using a shared secret between
  backend and gateway.
- RBAC is enforced at **two layers** (gateway and backend) — deliberate
  defense in depth, not redundancy for its own sake.
- The demo stores the JWT in `localStorage` + a readable cookie for the
  SSR fetch. In production this should move to an httpOnly, secure,
  SameSite cookie set by the backend, with the gateway/backend reading
  it directly — this trade-off is called out in `login.js` and is a
  good thing to mention unprompted in an interview.
- CORS is wide open (`*`) for local development; tighten to the deployed
  frontend origin before shipping.
