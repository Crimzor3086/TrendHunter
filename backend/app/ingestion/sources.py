from datetime import datetime, timedelta, timezone
from email.utils import parsedate_to_datetime
from xml.etree import ElementTree

import httpx

from backend.app.config import Settings
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


def parse_csv(value: str) -> list[str]:
    return [item.strip() for item in value.split(",") if item.strip()]


def parse_datetime(value: str | None) -> datetime:
    if not value:
        return datetime.now(timezone.utc)
    try:
        parsed = parsedate_to_datetime(value)
        return parsed if parsed.tzinfo else parsed.replace(tzinfo=timezone.utc)
    except (TypeError, ValueError):
        return datetime.now(timezone.utc)


def xml_text(node: ElementTree.Element, tag: str) -> str:
    child = node.find(tag)
    return child.text.strip() if child is not None and child.text else ""


async def collect_news_rss(settings: Settings) -> list[RawSignal]:
    urls = parse_csv(settings.news_rss_urls)
    if not urls:
        return []

    signals: list[RawSignal] = []
    async with httpx.AsyncClient(timeout=10, follow_redirects=True) as client:
        for url in urls:
            try:
                response = await client.get(url)
                response.raise_for_status()
                root = ElementTree.fromstring(response.text)
            except (httpx.HTTPError, ElementTree.ParseError):
                continue

            for item in root.findall(".//item")[:10]:
                title = xml_text(item, "title")
                description = xml_text(item, "description")
                link = xml_text(item, "link")
                published = xml_text(item, "pubDate")
                if not title:
                    continue

                signals.append(
                    RawSignal(
                        source=Source.news,
                        content_id=f"news:{link or title}",
                        text=f"{title}. {description}",
                        metrics=SignalMetrics(views=5000),
                        timestamp=parse_datetime(published),
                        url=link or url,
                    )
                )

    return signals


async def collect_reddit(settings: Settings) -> list[RawSignal]:
    subreddits = parse_csv(settings.reddit_subreddits)
    if not subreddits:
        return []

    signals: list[RawSignal] = []
    headers = {"User-Agent": settings.reddit_user_agent}
    async with httpx.AsyncClient(timeout=10, follow_redirects=True, headers=headers) as client:
        for subreddit in subreddits[:6]:
            url = f"https://www.reddit.com/r/{subreddit}/hot.json?limit=10"
            try:
                response = await client.get(url)
                response.raise_for_status()
                posts = response.json().get("data", {}).get("children", [])
            except (httpx.HTTPError, ValueError):
                continue

            for post in posts:
                data = post.get("data", {})
                title = data.get("title") or ""
                if not title:
                    continue
                created = datetime.fromtimestamp(data.get("created_utc", datetime.now(timezone.utc).timestamp()), timezone.utc)
                signals.append(
                    RawSignal(
                        source=Source.reddit,
                        content_id=f"reddit:{data.get('id', title)}",
                        text=f"{title}. {data.get('selftext', '')[:500]}",
                        metrics=SignalMetrics(
                            likes=int(data.get("ups") or 0),
                            comments=int(data.get("num_comments") or 0),
                            views=int((data.get("ups") or 0) * 35),
                        ),
                        timestamp=created,
                        url=f"https://reddit.com{data.get('permalink', '')}",
                    )
                )

    return signals


async def collect_x_recent_search(settings: Settings) -> list[RawSignal]:
    if not settings.x_bearer_token:
        return []

    params = {
        "query": settings.x_query,
        "max_results": "10",
        "tweet.fields": "created_at,public_metrics",
    }
    headers = {"Authorization": f"Bearer {settings.x_bearer_token}"}
    try:
        async with httpx.AsyncClient(timeout=10, headers=headers) as client:
            response = await client.get("https://api.twitter.com/2/tweets/search/recent", params=params)
            response.raise_for_status()
            tweets = response.json().get("data", [])
    except (httpx.HTTPError, ValueError):
        return []

    signals: list[RawSignal] = []
    for tweet in tweets:
        metrics = tweet.get("public_metrics", {})
        signals.append(
            RawSignal(
                source=Source.x,
                content_id=f"x:{tweet.get('id')}",
                text=tweet.get("text", ""),
                metrics=SignalMetrics(
                    likes=int(metrics.get("like_count") or 0),
                    shares=int(metrics.get("retweet_count") or 0),
                    comments=int(metrics.get("reply_count") or 0),
                    views=int(metrics.get("impression_count") or 0),
                ),
                timestamp=datetime.fromisoformat(tweet.get("created_at", datetime.now(timezone.utc).isoformat()).replace("Z", "+00:00")),
                url=f"https://x.com/i/web/status/{tweet.get('id')}",
            )
        )
    return signals


async def collect_live_batch(settings: Settings) -> list[RawSignal]:
    signals = []
    signals.extend(await collect_news_rss(settings))
    signals.extend(await collect_reddit(settings))
    signals.extend(await collect_x_recent_search(settings))
    return signals
