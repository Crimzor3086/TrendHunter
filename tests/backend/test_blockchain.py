from datetime import datetime, timezone

from backend.app.blockchain.service import (
    AvalancheRegistryService,
    build_content_hash,
    fallback_brief_hash,
    trend_hash,
)
from backend.app.config import Settings
from backend.app.schemas import ContentBrief, Trend, TrendCategory, TrendStage


def make_trend() -> Trend:
    first_seen = datetime(2026, 6, 25, 8, 0, tzinfo=timezone.utc)
    return Trend(
        trend_id="ai-interns",
        title="AI replacing interns in startups",
        category=TrendCategory.founder_culture,
        score=86,
        stage=TrendStage.growing,
        first_seen=first_seen,
        platforms=[],
        raw_signals=[],
    )


def make_brief() -> ContentBrief:
    return ContentBrief(
        trend_id="ai-interns",
        hook="Test hook",
        angle="Test angle",
        why_it_is_spreading="Because founders are debating it.",
        kenyan_context="Kenyan founder context.",
        script_30_60s="Short script.",
        remix_template="Remix template.",
        generated_at=datetime(2026, 6, 25, 9, 0, tzinfo=timezone.utc),
    )


def test_trend_hash_is_deterministic():
    trend = make_trend()
    assert trend_hash(trend) == trend_hash(trend)
    assert trend_hash(trend).startswith("0x")
    assert len(trend_hash(trend)) == 66


def test_build_content_hash_includes_brief():
    trend = make_trend()
    brief = make_brief()
    content_hash = build_content_hash(trend, brief)
    assert trend_hash(trend) in content_hash
    assert fallback_brief_hash(brief) in content_hash


def test_register_trend_dry_run_when_unconfigured():
    settings = Settings(
        trend_registry_address=None,
        registry_private_key=None,
    )
    service = AvalancheRegistryService(settings)
    record = service.register_trend(make_trend(), make_brief())
    assert record.status == "dry_run_missing_fuji_config"
    assert record.transaction_hash is None
    assert record.payload["content_hash"]


def test_blockchain_status_without_contract():
    settings = Settings(trend_registry_address=None)
    service = AvalancheRegistryService(settings)
    status = service.get_status()
    assert status.configured is False
    assert status.contract_address is None
