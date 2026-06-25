# Trend Hunter

Trend Hunter is an AI-powered real-time trend-to-content engine that converts emerging social trends into ready-to-shoot entrepreneurial video scripts for Kenyan founders.

## Problem

Kenyan creator teams often miss viral windows because they find trends too late, lack local context, and still have to decide the angle, hook, and script manually. The gap is not just discovery. It is turning a signal into a publishable short-form video idea inside the 24-72 hour window.

## Target Users

- Kenyan short-form creators on TikTok, Reels, and YouTube Shorts covering entrepreneurship, money, side hustles, and founder culture.
- Early-stage startup marketing teams in East Africa.
- Media pages covering the African startup ecosystem.

## V1 Features

1. **Real-Time Trend Feed**
   Aggregates social and Kenyan news signals into an emerging trend queue with velocity, category, and lifespan estimates.

2. **AI Content Brief Generator**
   Turns a selected trend into why it is happening, why it matters for Kenyan founders, a hook, a 30-60 second script, and a remix template.

3. **Avalanche Trend Registry**
   Registers verified trend events on Avalanche Fuji with title, category, score snapshot, content hash, timestamp, and creator address.

## Backend Architecture

The backend converts raw social signals into ranked trends, structured content briefs, and optional on-chain records.

```text
Scrapers / APIs
  X | Reddit | Kenyan News | TikTok | YouTube
        |
Ingestion Layer
  normalization, deduplication, event queue
        |
Trend Engine
  clustering, velocity scoring, lifecycle stage
        |
AI Layer
  classification, local context, hook, script, remix template
        |
FastAPI
  trends, briefs, registry, blockchain endpoints
        |
Avalanche C-Chain Service
  trend registration and on-chain reads
```

Implemented MVP modules:

- `backend/app/ingestion/` collects normalized demo signals for X, Reddit, and Kenyan news.
- `backend/app/trend_engine/` clusters signals and scores trends with velocity, cross-platform presence, and acceleration.
- `backend/app/classifier/` classifies Founder Culture, Business, Money, or Not Relevant with deterministic MVP logic.
- `backend/app/ai_brief_generator/` generates founder-focused ready-to-shoot briefs.
- `backend/app/main.py` is the FastAPI entrypoint.
- `backend/app/blockchain/` hashes trends and submits to Avalanche Fuji when registry credentials are configured.
- `backend/app/cache_layer/` provides a local TTL cache or Redis-backed cache for hot trend leaderboards.
- `backend/app/persistence.py` stores registry records in SQLite so backend submissions survive restarts.

The production design still supports PostgreSQL, OpenAI or Claude, Celery/RQ, Playwright, Reddit API, X API, and RSS ingestion. The current MVP keeps those seams explicit while using deterministic local data so the demo works immediately.

## API Endpoints

| Method | Path | Description |
|--------|------|-------------|
| `GET` | `/health` | Service health check |
| `GET` | `/blockchain/status` | RPC connectivity, contract address, trend count |
| `GET` | `/blockchain/trends` | Read all trends from the deployed contract |
| `POST` | `/ingest/demo` | Load demo signals and rebuild trends |
| `POST` | `/ingest/live` | Fetch live RSS, Reddit, or X signals |
| `GET` | `/trends` | Ranked trend feed (`?refresh_live=true` optional) |
| `GET` | `/trends/{trend_id}` | Single trend by ID |
| `POST` | `/generate-brief` | Generate a content brief for a trend |
| `POST` | `/register-trend` | Register a trend on-chain via backend signer |
| `GET` | `/registry` | Backend registry records |

Example brief request:

```json
{ "trend_id": "ai-interns" }
```

Example register request:

```json
{ "trend_id": "ai-interns", "brief_hash": "sha256:optional-brief-digest" }
```

Interactive docs: `http://localhost:8000/docs`

## Avalanche Integration

Avalanche C-Chain is the verifiable Trend Registry layer. The `TrendRegistry` contract stores:

- numeric on-chain trend ID
- `title`
- `category`
- `score`
- `firstSeen`
- `contentHash`
- `creator`
- `verified`

The backend computes a canonical trend hash and combines it with the brief digest into the on-chain `contentHash`. The frontend can register trends either through Core Wallet or through the backend signer.

The static MVP uses Core Wallet on Avalanche Fuji for on-chain registration. The product direction is an embedded wallet flow so non-crypto-native creators do not need to manage seed phrases or wallet setup.

## Stage 1 Demo Flow

1. Open the dashboard and view the **Emerging Trends** feed.
2. Select the trend: `AI replacing interns in startups`.
3. Click **Generate Content Brief**.
4. Review the founder-specific hook, script, local relevance metrics, and remix template.
5. Connect Core Wallet on Avalanche Fuji.
6. Paste the deployed `TrendRegistry` contract address (or let the app load it from backend status).
7. Click **Register on Avalanche**.
8. The transaction log shows the Fuji Explorer transaction link.

Success means a user can move from trend discovery to publishable script to on-chain verified trend record.

## Project Files

- `contracts/TrendRegistry.sol` — on-chain trend registry contract.
- `test/TrendRegistry.test.js` — Hardhat tests for registration, score updates, content hash updates, verification, and reputation.
- `tests/backend/` — FastAPI, blockchain, trend engine, and persistence tests.
- `backend/app/` — FastAPI service modules.
- `frontend/index.html` — mobile-first dashboard markup.
- `frontend/styles.css` — dashboard styling.
- `frontend/js/` — split frontend logic:
  `state.js`, `api.js`, `trends.js`, `wallet.js`, `registry.js`, `assistant.js`, `toast.js`, and `init.js`.
- `scripts/deploy.js` — deploys `TrendRegistry` and writes `deployments/fuji-TrendRegistry.json`.
- `docker-compose.yml` — local API + Redis stack.

## Start the Backend

The frontend depends on the FastAPI backend for trends, briefs, registry records, and blockchain status. Start the backend before opening the dashboard.

### 1. Prerequisites

- Python 3.10+
- Node.js 20+ (for npm scripts and contract tooling)

### 2. Install dependencies

From the project root:

```bash
npm install
python -m pip install -r requirements-backend.txt
```

### 3. Configure environment

```bash
cp .env.example .env
```

Minimum settings for local development:

```bash
FRONTEND_URL=http://localhost:8080
USE_DEMO_SEED=true
```

Optional settings:

```bash
OPENAI_API_KEY=sk-...              # real AI briefs instead of fallback templates
TREND_REGISTRY_ADDRESS=0x...       # auto-loaded from deployments/fuji-TrendRegistry.json after deploy
REGISTRY_PRIVATE_KEY=0x...         # backend on-chain registration via /register-trend
REDIS_URL=redis://localhost:6379/0 # optional Redis cache
```

### 4. Start the API server

```bash
npm run backend
```

The server runs at `http://localhost:8000` with hot reload enabled.

Verify it is working:

```bash
curl http://localhost:8000/health
curl http://localhost:8000/trends
```

Open interactive API docs:

```text
http://localhost:8000/docs
```

### 5. Start the frontend

In a second terminal:

```bash
cd frontend
npm install
npm start
```

Open:

```text
http://localhost:8080
```

The dashboard loads trends from `GET /trends`, syncs registry records from `GET /registry`, and reads the deployed contract address from `GET /blockchain/status`.

### 6. Run with Docker (optional)

```bash
cp .env.example .env
npm run docker:up
```

This starts the API on port `8000` with Redis. Registry records persist in `./data/registry.db`.

## Run Locally

Install dependencies:

```bash
npm install
python -m pip install -r requirements-backend.txt
```

Compile contracts:

```bash
npm run compile
```

Run tests:

```bash
# Smart contract tests
npm test

# Backend tests
npm run test:backend

# Both
npm run test:all
```

Run the backend:

```bash
npm run backend
```

Open API docs:

```text
http://localhost:8000/docs
```

Run the frontend:

```bash
cd frontend
npm install
npm start
```

Then open:

```text
http://localhost:8080
```

The frontend requires the backend to be running. Core Wallet on Avalanche Fuji is required for on-chain registration from the browser.

## Docker

See **Start the Backend → Run with Docker** above.

## Deploy To Fuji

Create `.env` from `.env.example` and add a funded Fuji private key:

```bash
cp .env.example .env
```

Deploy:

```bash
npm run deploy:fuji
```

This writes the deployed address to `deployments/fuji-TrendRegistry.json`. The backend auto-loads that address when `TREND_REGISTRY_ADDRESS` is not set.

Paste the deployed contract address into the frontend, connect Core Wallet on Fuji, generate the brief, then register the trend on Avalanche.

For backend-side registration, set in `.env`:

```bash
TREND_REGISTRY_ADDRESS=0x...
REGISTRY_PRIVATE_KEY=0x...
```

Without those values, `/register-trend` returns a dry-run registry payload with the computed trend hash instead of submitting a transaction.

## Environment Variables

Key backend settings from `.env.example`:

| Variable | Purpose |
|----------|---------|
| `FRONTEND_URL` | Primary CORS origin |
| `CORS_ORIGINS` | Additional allowed frontend origins |
| `OPENAI_API_KEY` | Real AI brief generation |
| `AVALANCHE_RPC_URL` | Fuji RPC endpoint |
| `TREND_REGISTRY_ADDRESS` | Deployed registry contract |
| `REGISTRY_PRIVATE_KEY` | Backend signer for `/register-trend` |
| `REGISTRY_DB_PATH` | SQLite path for persisted registry records |
| `REDIS_URL` | Optional Redis cache backend |
| `TX_CONFIRMATION_TIMEOUT` | Seconds to wait for Fuji tx confirmation |
