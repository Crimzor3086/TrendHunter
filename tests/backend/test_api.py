def test_health(client):
    response = client.get("/health")
    assert response.status_code == 200
    payload = response.json()
    assert payload["status"] == "ok"
    assert payload["service"] == "Trend Hunter API"


def test_ingest_demo_returns_signals(seeded_client):
    response = seeded_client.post("/ingest/demo")
    assert response.status_code == 200
    signals = response.json()
    assert len(signals) == 5
    assert {signal["source"] for signal in signals} >= {"x", "reddit", "news"}


def test_get_trends_after_demo_ingest(seeded_client):
    response = seeded_client.get("/trends")
    assert response.status_code == 200
    trends = response.json()
    assert len(trends) >= 3
    assert trends[0]["score"] >= trends[-1]["score"]
    trend_ids = {trend["trend_id"] for trend in trends}
    assert "ai-interns" in trend_ids


def test_get_trend_by_id(seeded_client):
    response = seeded_client.get("/trends/ai-interns")
    assert response.status_code == 200
    trend = response.json()
    assert trend["trend_id"] == "ai-interns"
    assert trend["title"]
    assert trend["classification"] is not None


def test_get_trend_not_found(client):
    response = client.get("/trends/does-not-exist")
    assert response.status_code == 404


def test_generate_brief(seeded_client):
    response = seeded_client.post("/generate-brief", json={"trend_id": "ai-interns"})
    assert response.status_code == 200
    brief = response.json()
    assert brief["trend_id"] == "ai-interns"
    assert brief["hook"]
    assert brief["script_30_60s"]


def test_register_trend_dry_run(seeded_client):
    seeded_client.post("/generate-brief", json={"trend_id": "ai-interns"})
    response = seeded_client.post("/register-trend", json={"trend_id": "ai-interns"})
    assert response.status_code == 200
    record = response.json()
    assert record["trend_id"] == "ai-interns"
    assert record["status"] == "dry_run_missing_fuji_config"
    assert record["trend_hash"].startswith("0x")
    assert record["content_hash"]


def test_registry_lists_saved_records(seeded_client):
    seeded_client.post("/register-trend", json={"trend_id": "ai-interns"})
    response = seeded_client.get("/registry")
    assert response.status_code == 200
    records = response.json()
    assert len(records) == 1
    assert records[0]["trend_id"] == "ai-interns"


def test_blockchain_status_without_config(client):
    response = client.get("/blockchain/status")
    assert response.status_code == 200
    status = response.json()
    assert status["configured"] is False
    assert status["chain_id"] == 43113


def test_blockchain_trends_requires_contract(client):
    response = client.get("/blockchain/trends")
    assert response.status_code == 503


def test_cors_allows_local_network_origin(client):
    response = client.get(
        "/health",
        headers={"Origin": "http://192.168.1.103:8080"},
    )
    assert response.status_code == 200
    assert response.headers.get("access-control-allow-origin") == "http://192.168.1.103:8080"
