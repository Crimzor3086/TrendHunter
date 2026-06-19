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
   Registers verified trend events on Avalanche Fuji with a trend hash, timestamp, category, score snapshot, brief hash, and contributor.

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
  trends, briefs, registry endpoints
        |
Avalanche C-Chain Service
  trend hash registration and verification
```

Implemented MVP modules:

- `backend/app/ingestion/` collects normalized demo signals for X, Reddit, and Kenyan news.
- `backend/app/trend_engine/` clusters signals and scores trends with velocity, cross-platform presence, and acceleration.
- `backend/app/classifier/` classifies Founder Culture, Business, Money, or Not Relevant with deterministic MVP logic.
- `backend/app/ai_brief_generator/` generates founder-focused ready-to-shoot briefs.
- `backend/app/api` is represented by `backend/app/main.py`, the FastAPI entrypoint.
- `backend/app/blockchain/` hashes trends and submits to Avalanche Fuji when registry credentials are configured.
- `backend/app/cache_layer/` provides a local TTL cache for hot trend leaderboards.

The production design still supports PostgreSQL, Redis, OpenAI or Claude, Celery/RQ, Playwright, Reddit API, X API, and RSS ingestion. The current 7-day MVP keeps those seams explicit while using deterministic local data so the demo works immediately.

## API Endpoints

- `GET /health`
- `POST /ingest/demo`
- `GET /trends`
- `GET /trends/{trend_id}`
- `POST /generate-brief` with `{ "trend_id": "ai-interns" }`
- `POST /register-trend` with `{ "trend_id": "ai-interns" }`
- `GET /registry`

## Avalanche Integration

Avalanche C-Chain is the verifiable Trend Registry layer. The smart contract records:

- `trendHash`
- `firstSeen`
- `category`
- `score`
- `briefHash`
- `contributor`

This creates transparent proof of who detected a trend first, prevents duplicate trend claims, and sets up a future contributor reputation or USDC rewards layer.

The static MVP uses an injected Core Wallet compatible provider for the Stage 1 demo. The product direction is an embedded wallet flow so non-crypto-native creators do not need to manage seed phrases or wallet setup.

## Stage 1 Demo Flow

1. Open the dashboard and view the **Emerging Trends** feed.
2. Select the trend: `AI agent replacing interns`.
3. Click **Generate Content Brief**.
4. Review the founder-specific hook, script, local relevance metrics, and remix template.
5. Connect Core Wallet on Avalanche Fuji.
6. Paste the deployed `TrendRegistry` contract address.
7. Click **Register on Avalanche**.
8. The transaction log shows the Fuji Explorer transaction link.

Success means a user can move from trend discovery to publishable script to on-chain verified trend record.

## Project Files

- `contracts/YourContract.sol` contains the `TrendRegistry` Solidity contract.
- `test/YourContract.test.js` covers registration, duplicate prevention, score updates, brief attachment, verification, trend hashes, and contributor reputation.
- `frontend/index.html` contains the mobile-first dashboard markup.
- `frontend/styles.css` contains dashboard styling.
- `frontend/js/` contains split frontend logic:
  `state.js`, `mock-data.js`, `api.js`, `trends.js`, `wallet.js`, `registry.js`, `assistant.js`, `toast.js`, and `init.js`.
- `scripts/deploy.js` deploys `TrendRegistry`.

## Run Locally

Install dependencies:

```bash
npm install
```

Install backend dependencies:

```bash
python -m pip install -r requirements-backend.txt
```

Compile:

```bash
npm run compile
```

Test:

```bash
npm test
```

Open the frontend:

```bash
xdg-open frontend/index.html
```

Run the backend:

```bash
npm run backend
```

Then open:

```bash
http://localhost:8000/docs
```

## Deploy To Fuji

Create `.env` from `.env.example` and add a funded Fuji private key:

```bash
cp .env.example .env
```

Deploy:

```bash
npm run deploy:fuji
```

Paste the deployed contract address into the frontend, connect Core Wallet on Fuji, generate the brief, then register the trend on Avalanche.

For backend-side registration, set `TREND_REGISTRY_ADDRESS` and `REGISTRY_PRIVATE_KEY` in `.env`. Without those values, `/register-trend` returns a dry-run registry payload with the computed trend hash instead of submitting a transaction.
