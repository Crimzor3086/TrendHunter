from backend.app.schemas import ContentBrief, Trend


def generate_brief(trend: Trend) -> ContentBrief:
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
