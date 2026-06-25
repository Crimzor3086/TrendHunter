from datetime import datetime, timezone

from backend.app.persistence import RegistryPersistence
from backend.app.schemas import RegistryRecord, TrendCategory


def test_registry_persistence_round_trip(tmp_path):
    db_path = tmp_path / "registry.db"
    persistence = RegistryPersistence(str(db_path))
    record = RegistryRecord(
        trend_id="ai-interns",
        trend_hash="0xabc",
        category=TrendCategory.founder_culture,
        score=86,
        first_seen=datetime(2026, 6, 25, tzinfo=timezone.utc),
        content_hash="0xabc|sha256:def",
        status="confirmed",
        payload={"title": "AI replacing interns in startups"},
    )

    persistence.save(record)
    loaded = persistence.load_all()

    assert len(loaded) == 1
    assert loaded[0].trend_id == "ai-interns"
    assert loaded[0].status == "confirmed"
    assert loaded[0].payload["title"] == "AI replacing interns in startups"
