from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from backend.app.ai_brief_generator.service import generate_brief
from backend.app.blockchain.service import AvalancheRegistryService
from backend.app.cache_layer.cache import cache
from backend.app.config import get_settings
from backend.app.ingestion.sources import collect_demo_batch
from backend.app.schemas import ContentBrief, GenerateBriefRequest, RawSignal, RegisterTrendRequest, RegistryRecord, Trend
from backend.app.storage import store
from backend.app.trend_engine.engine import build_trends

settings = get_settings()
app = FastAPI(title=settings.app_name, version="0.1.0")
registry_service = AvalancheRegistryService(settings)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.frontend_url, "http://localhost:8000", "http://127.0.0.1:8000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def refresh_demo_pipeline() -> list[Trend]:
    signals = collect_demo_batch()
    for signal in signals:
        store.save_signal(signal)

    trends = build_trends(signals)
    for trend in trends:
        store.save_trend(trend)

    cache.set("trending:kenya", trends, ttl_seconds=120)
    cache.set("trending:global", trends, ttl_seconds=120)
    return trends


@app.on_event("startup")
def load_seed_data() -> None:
    refresh_demo_pipeline()


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok", "service": settings.app_name}


@app.post("/ingest/demo", response_model=list[RawSignal])
def ingest_demo() -> list[RawSignal]:
    signals = collect_demo_batch()
    for signal in signals:
        store.save_signal(signal)
    refresh_demo_pipeline()
    return signals


@app.get("/trends", response_model=list[Trend])
def get_trends() -> list[Trend]:
    cached = cache.get("trending:kenya")
    if cached is not None:
        return cached

    if not store.trends:
        return refresh_demo_pipeline()

    trends = store.ranked_trends()
    cache.set("trending:kenya", trends, ttl_seconds=120)
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
def post_generate_brief(request: GenerateBriefRequest) -> ContentBrief:
    trend = store.trends.get(request.trend_id)
    if trend is None:
        refresh_demo_pipeline()
        trend = store.trends.get(request.trend_id)
    if trend is None:
        raise HTTPException(status_code=404, detail="Trend not found")

    brief = generate_brief(trend)
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
