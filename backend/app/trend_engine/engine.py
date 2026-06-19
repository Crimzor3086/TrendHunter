from collections import defaultdict
from datetime import datetime, timezone
import re

from backend.app.classifier.service import classify_trend
from backend.app.schemas import RawSignal, Source, Trend, TrendCategory, TrendStage


CLUSTER_KEYWORDS = {
    "ai-interns": ["ai", "agent", "intern", "entry-level", "busywork"],
    "whatsapp-sme": ["whatsapp", "catalogue", "storefront", "small businesses"],
    "founder-pay": ["founder salary", "pay themselves", "salary transparency"],
}


def keyword_matches(text: str, keyword: str) -> bool:
    if len(keyword) <= 3 and keyword.isalnum():
        return re.search(rf"\b{re.escape(keyword)}\b", text) is not None
    return keyword in text


def cluster_signals(signals: list[RawSignal]) -> dict[str, list[RawSignal]]:
    clusters: dict[str, list[RawSignal]] = defaultdict(list)
    for signal in signals:
        text = signal.text.lower()
        key = "misc"
        for cluster_key, keywords in CLUSTER_KEYWORDS.items():
            if any(keyword_matches(text, keyword) for keyword in keywords):
                key = cluster_key
                break
        clusters[key].append(signal)
    return clusters


def calculate_score(signals: list[RawSignal]) -> int:
    total_engagement = sum(
        signal.metrics.likes + signal.metrics.shares * 2 + signal.metrics.comments * 2 + signal.metrics.views * 0.02
        for signal in signals
    )
    age_hours = max(
        (datetime.now(timezone.utc) - min(signal.timestamp for signal in signals)).total_seconds() / 3600,
        1,
    )
    platforms = {signal.source for signal in signals}

    engagement_velocity = min(total_engagement / age_hours / 260, 100)
    cross_platform_presence = min(len(platforms) / 3 * 100, 100)
    acceleration_rate = min(sum(signal.metrics.shares + signal.metrics.comments for signal in signals) / 35, 100)

    score = engagement_velocity * 0.5 + cross_platform_presence * 0.3 + acceleration_rate * 0.2
    return round(min(score, 100))


def assign_stage(first_seen: datetime) -> TrendStage:
    age_hours = (datetime.now(timezone.utc) - first_seen).total_seconds() / 3600
    if age_hours < 12:
        return TrendStage.emerging
    if age_hours < 72:
        return TrendStage.growing
    if age_hours < 168:
        return TrendStage.peak
    return TrendStage.declining


def title_for_cluster(cluster_key: str, signals: list[RawSignal]) -> str:
    titles = {
        "ai-interns": "AI replacing interns in startups",
        "whatsapp-sme": "Kenyan SMEs selling through WhatsApp storefronts",
        "founder-pay": "Founder salary transparency posts",
    }
    return titles.get(cluster_key, signals[0].text[:80])


def build_trends(signals: list[RawSignal]) -> list[Trend]:
    trends: list[Trend] = []
    for cluster_key, cluster_signals_list in cluster_signals(signals).items():
        first_seen = min(signal.timestamp for signal in cluster_signals_list)
        title = title_for_cluster(cluster_key, cluster_signals_list)
        classification = classify_trend(title, cluster_signals_list)
        if classification.category == TrendCategory.not_relevant:
            continue

        trends.append(
            Trend(
                trend_id=cluster_key,
                title=title,
                category=classification.category,
                score=calculate_score(cluster_signals_list),
                stage=assign_stage(first_seen),
                first_seen=first_seen,
                platforms=sorted({signal.source for signal in cluster_signals_list}, key=lambda source: source.value),
                raw_signals=cluster_signals_list,
                classification=classification,
            )
        )

    return sorted(trends, key=lambda trend: trend.score, reverse=True)
