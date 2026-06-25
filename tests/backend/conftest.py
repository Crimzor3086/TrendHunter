import os

import pytest
from fastapi.testclient import TestClient

# Keep startup deterministic before backend modules load.
os.environ.setdefault("USE_DEMO_SEED", "false")
os.environ.setdefault("LIVE_INGESTION_ON_STARTUP", "false")
os.environ.setdefault("REDIS_URL", "")

from backend.app.blockchain.service import AvalancheRegistryService
from backend.app.cache_layer.cache import build_cache
from backend.app.config import get_settings
from backend.app.main import app
from backend.app.persistence import RegistryPersistence
from backend.app import main
from backend.app import storage


@pytest.fixture(autouse=True)
def isolate_backend(tmp_path, monkeypatch):
    db_path = tmp_path / "registry.db"
    monkeypatch.setenv("REGISTRY_DB_PATH", str(db_path))
    monkeypatch.setenv("TREND_REGISTRY_ADDRESS", "")
    monkeypatch.setenv("REGISTRY_PRIVATE_KEY", "")
    get_settings.cache_clear()

    settings = get_settings()
    main.settings = settings
    main.registry_service = AvalancheRegistryService(settings)
    main.cache = build_cache(None)

    storage.store.raw_signals.clear()
    storage.store.trends.clear()
    storage.store.briefs.clear()
    storage.store.registry_records.clear()
    storage.store._registry_persistence = RegistryPersistence(str(db_path))

    yield


@pytest.fixture
def client():
    with TestClient(app) as test_client:
        yield test_client


@pytest.fixture
def seeded_client(client):
    response = client.post("/ingest/demo")
    assert response.status_code == 200
    return client
