from datetime import datetime, timedelta, timezone

from backend.app.schemas import RawSignal, SignalMetrics, Source


def demo_signals() -> list[RawSignal]:
    now = datetime.now(timezone.utc)
    return [
        RawSignal(
            source=Source.x,
            content_id="x-ai-interns-001",
            text="Founder shows AI agent replacing repetitive intern spreadsheet work in a startup.",
            metrics=SignalMetrics(likes=9200, shares=2100, comments=780, views=300000),
            timestamp=now - timedelta(hours=8),
            url="https://x.com/example/status/ai-interns",
        ),
        RawSignal(
            source=Source.reddit,
            content_id="reddit-ai-interns-001",
            text="Are AI agents going to replace entry-level startup interns or just remove busywork?",
            metrics=SignalMetrics(likes=1300, shares=120, comments=360, views=44000),
            timestamp=now - timedelta(hours=7, minutes=30),
            url="https://reddit.com/r/startups/example",
        ),
        RawSignal(
            source=Source.news,
            content_id="news-ai-work-kenya-001",
            text="Kenyan SMEs are testing AI tools to automate finance, customer support and sales admin.",
            metrics=SignalMetrics(likes=180, shares=95, comments=24, views=12000),
            timestamp=now - timedelta(hours=6),
            url="https://example.com/kenya-ai-smes",
        ),
        RawSignal(
            source=Source.x,
            content_id="x-whatsapp-sme-001",
            text="Small businesses in Nairobi are using WhatsApp catalogues as their main storefront.",
            metrics=SignalMetrics(likes=3100, shares=660, comments=220, views=92000),
            timestamp=now - timedelta(hours=17),
        ),
        RawSignal(
            source=Source.news,
            content_id="news-founder-pay-001",
            text="Founder salary transparency posts revive debate about what early-stage builders should pay themselves.",
            metrics=SignalMetrics(likes=640, shares=170, comments=89, views=21000),
            timestamp=now - timedelta(days=2),
        ),
    ]


def collect_demo_batch() -> list[RawSignal]:
    return demo_signals()
