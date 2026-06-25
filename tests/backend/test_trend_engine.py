from backend.app.ingestion.sources import collect_demo_batch
from backend.app.trend_engine.engine import build_trends, calculate_score, cluster_signals


def test_demo_signals_cluster_into_known_trends():
    signals = collect_demo_batch()
    clusters = cluster_signals(signals)
    assert "ai-interns" in clusters
    assert "whatsapp-sme" in clusters
    assert "founder-pay" in clusters


def test_build_trends_ranks_by_score():
    trends = build_trends(collect_demo_batch())
    assert len(trends) >= 3
    scores = [trend.score for trend in trends]
    assert scores == sorted(scores, reverse=True)
    assert all(0 <= trend.score <= 100 for trend in trends)


def test_calculate_score_caps_at_100():
    signals = collect_demo_batch()
    score = calculate_score(signals)
    assert 0 <= score <= 100
