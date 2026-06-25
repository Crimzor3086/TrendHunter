from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from backend.app.ai_brief_generator.service import generate_brief
from backend.app.blockchain.service import AvalancheRegistryService
from backend.app.cache_layer.cache import build_cache
from backend.app.config import get_settings
from backend.app.ingestion.sources import collect_demo_batch, collect_live_batch
from backend.app.schemas import (
    BlockchainStatus,
    ContentBrief,
    GenerateBriefRequest,
    OnChainTrend,
    RawSignal,
    RegisterTrendRequest,
    RegistryRecord,
    Trend,
)
from backend.app.storage import store
from backend.app.trend_engine.engine import build_trends

settings = get_settings()
app = FastAPI(title=settings.app_name, version="0.1.0")
registry_service = AvalancheRegistryService(settings)
cache = build_cache(settings.redis_url)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins(),
    allow_origin_regex=settings.cors_origin_regex(),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def process_signals(signals: list[RawSignal]) -> list[Trend]:
    for signal in signals:
        store.save_signal(signal)

    trends = build_trends(signals)
    for trend in trends:
        store.save_trend(trend)

    cache.set("trending:kenya", [trend.model_dump(mode="json") for trend in trends], ttl_seconds=120)
    cache.set("trending:global", [trend.model_dump(mode="json") for trend in trends], ttl_seconds=120)
    return trends


def refresh_demo_pipeline() -> list[Trend]:
    return process_signals(collect_demo_batch())


async def refresh_live_pipeline(use_fallback: bool = True) -> list[Trend]:
    signals = await collect_live_batch(settings)
    if not signals and use_fallback and settings.use_demo_seed:
        signals = collect_demo_batch()
    return process_signals(signals)


def cached_trends() -> list[Trend] | None:
    cached = cache.get("trending:kenya")
    if cached is None:
        return None
    return [Trend.model_validate(item) for item in cached]


@app.on_event("startup")
async def load_seed_data() -> None:
    if settings.live_ingestion_on_startup:
        await refresh_live_pipeline()
    elif settings.use_demo_seed:
        refresh_demo_pipeline()


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok", "service": settings.app_name}


@app.get("/blockchain/status", response_model=BlockchainStatus)
def blockchain_status() -> BlockchainStatus:
    return registry_service.get_status()


@app.get("/blockchain/trends", response_model=list[OnChainTrend])
def blockchain_trends() -> list[OnChainTrend]:
    if not settings.trend_registry_address:
        raise HTTPException(status_code=503, detail="Trend registry contract address is not configured")
    return registry_service.list_on_chain_trends()


@app.post("/ingest/demo", response_model=list[RawSignal])
def ingest_demo() -> list[RawSignal]:
    signals = collect_demo_batch()
    for signal in signals:
        store.save_signal(signal)
    refresh_demo_pipeline()
    return signals


@app.post("/ingest/live", response_model=list[Trend])
async def ingest_live() -> list[Trend]:
    trends = await refresh_live_pipeline(use_fallback=False)
    if not trends:
        raise HTTPException(status_code=424, detail="No live signals collected. Configure RSS, Reddit, or X sources.")
    return trends


@app.get("/trends", response_model=list[Trend])
async def get_trends(refresh_live: bool = False) -> list[Trend]:
    if refresh_live:
        trends = await refresh_live_pipeline(use_fallback=settings.use_demo_seed)
        if trends:
            return trends

    cached = cached_trends()
    if cached is not None:
        return cached

    if not store.trends:
        return refresh_demo_pipeline()

    trends = store.ranked_trends()
    cache.set("trending:kenya", [trend.model_dump(mode="json") for trend in trends], ttl_seconds=120)
    return trends


@app.get("/trends/{trend_id}", response_model=Trend)
def get_trend(trend_id: str) -> Trend:
    trend = store.trends.get(trend_id)
    if trend is None:
        refresh_demo_pipeline()
        trend = store.trends.get(trend_id)
    if trend is None:
        raise HTTPException(status_code=404, detail="Trend not found")
    return trend


@app.post("/generate-brief", response_model=ContentBrief)
async def post_generate_brief(request: GenerateBriefRequest) -> ContentBrief:
    trend = store.trends.get(request.trend_id)
    if trend is None:
        refresh_demo_pipeline()
        trend = store.trends.get(request.trend_id)
    if trend is None:
        raise HTTPException(status_code=404, detail="Trend not found")

    brief = await generate_brief(trend, settings)
    store.save_brief(brief)
    return brief


@app.post("/register-trend", response_model=RegistryRecord)
def post_register_trend(request: RegisterTrendRequest) -> RegistryRecord:
    trend = store.trends.get(request.trend_id)
    if trend is None:
        refresh_demo_pipeline()
        trend = store.trends.get(request.trend_id)
    if trend is None:
        raise HTTPException(status_code=404, detail="Trend not found")

    brief = store.briefs.get(request.trend_id)
    record = registry_service.register_trend(trend, brief, request.brief_hash)
    store.save_registry_record(record)
    return record


@app.get("/registry", response_model=list[RegistryRecord])
def get_registry() -> list[RegistryRecord]:
    return list(store.registry_records.values())
