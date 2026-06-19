import json

import httpx

from backend.app.config import Settings
from backend.app.schemas import ContentBrief, Trend


def fallback_brief(trend: Trend) -> ContentBrief:
    if "intern" in trend.title.lower():
        return ContentBrief(
            trend_id=trend.trend_id,
            hook="Everyone is arguing about AI replacing interns. Kenyan founders are asking the wrong question.",
            angle="Shift the conversation from replacing people to removing repetitive work so junior talent creates more value.",
            why_it_is_spreading=(
                "The trend combines AI anxiety, founder productivity pressure and a concrete example people can debate."
            ),
            kenyan_context=(
                "For Kenyan SMEs and startups, the sharper question is how lean teams can automate admin work while "
                "freeing interns to sell, research customers and support growth."
            ),
            script_30_60s=(
                "Everyone is arguing about AI replacing interns.\n\n"
                "But that is not the real opportunity.\n\n"
                "If you are a founder, the goal is not replacing people. The goal is removing repetitive work.\n\n"
                "Imagine your intern spending six hours copying spreadsheets. An AI agent can do that instantly.\n\n"
                "Now your intern focuses on sales, customer interviews and growth.\n\n"
                "The winners will not be founders who replace people. The winners will be founders who multiply productivity."
            ),
            remix_template=(
                "Use the format 'AI replacing X'. Replace X with marketers, assistants, accountants or sales reps. "
                "Then answer: here is what founders should actually do."
            ),
        )

    return ContentBrief(
        trend_id=trend.trend_id,
        hook=f"This trend is moving fast: {trend.title}.",
        angle="Explain the practical founder lesson before the trend peaks.",
        why_it_is_spreading="The topic is gaining attention across platforms because it connects to money, work and business execution.",
        kenyan_context="Frame the lesson around Kenyan SMEs, local distribution and founder constraints.",
        script_30_60s=(
            f"{trend.title} is not just a global trend.\n\n"
            "For Kenyan founders, it points to a practical business question.\n\n"
            "What changes this week? What should a small team do differently? And what should they ignore?\n\n"
            "The fastest creators will turn the noise into a clear action step."
        ),
        remix_template="State the trend, explain the local founder impact, then give one action a small team can take today.",
    )


def brief_from_json(trend: Trend, payload: dict) -> ContentBrief:
    return ContentBrief(
        trend_id=trend.trend_id,
        hook=str(payload.get("hook") or f"This trend is moving fast: {trend.title}."),
        angle=str(payload.get("angle") or "Explain the practical founder lesson before the trend peaks."),
        why_it_is_spreading=str(payload.get("why_it_is_spreading") or payload.get("why_spreading") or ""),
        kenyan_context=str(payload.get("kenyan_context") or payload.get("local_context") or ""),
        script_30_60s=str(payload.get("script_30_60s") or payload.get("script") or ""),
        remix_template=str(payload.get("remix_template") or payload.get("remix") or ""),
    )


def extract_response_text(data: dict) -> str:
    if isinstance(data.get("output_text"), str):
        return data["output_text"]

    chunks: list[str] = []
    for item in data.get("output", []):
        for content in item.get("content", []):
            text = content.get("text")
            if isinstance(text, str):
                chunks.append(text)
    return "\n".join(chunks)


async def generate_openai_brief(trend: Trend, settings: Settings) -> ContentBrief:
    source_text = "\n".join(f"- {signal.source.value}: {signal.text}" for signal in trend.raw_signals[:8])
    prompt = f"""
You generate short-form video briefs for Kenyan entrepreneurship creators.

Return only valid JSON with these keys:
hook, angle, why_it_is_spreading, kenyan_context, script_30_60s, remix_template.

Trend:
Title: {trend.title}
Category: {trend.category.value}
Score: {trend.score}
Stage: {trend.stage.value}
Platforms: {", ".join(platform.value for platform in trend.platforms)}

Signals:
{source_text}
"""

    async with httpx.AsyncClient(timeout=20) as client:
        response = await client.post(
            "https://api.openai.com/v1/responses",
            headers={
                "Authorization": f"Bearer {settings.openai_api_key}",
                "Content-Type": "application/json",
            },
            json={
                "model": settings.openai_model,
                "input": prompt,
            },
        )
        response.raise_for_status()

    text = extract_response_text(response.json()).strip()
    if text.startswith("```"):
        text = text.strip("`")
        text = text.removeprefix("json").strip()

    return brief_from_json(trend, json.loads(text))


async def generate_brief(trend: Trend, settings: Settings | None = None) -> ContentBrief:
    if settings and settings.openai_api_key:
        try:
            return await generate_openai_brief(trend, settings)
        except (httpx.HTTPError, json.JSONDecodeError, KeyError, TypeError, ValueError):
            return fallback_brief(trend)

    return fallback_brief(trend)
