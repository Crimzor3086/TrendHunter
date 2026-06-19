from backend.app.schemas import Classification, RawSignal, TrendCategory


def classify_trend(title: str, signals: list[RawSignal]) -> Classification:
    text = " ".join([title, *(signal.text for signal in signals)]).lower()

    if any(term in text for term in ["intern", "founder", "startup", "entry-level"]):
        return Classification(
            category=TrendCategory.founder_culture,
            kenya_relevance=0.92,
            confidence=0.91,
            reasoning="The debate connects directly to startup team design, founder leverage and junior talent in Kenya.",
        )

    if any(term in text for term in ["whatsapp", "sme", "small business", "storefront"]):
        return Classification(
            category=TrendCategory.business,
            kenya_relevance=0.88,
            confidence=0.87,
            reasoning="WhatsApp commerce is a practical operating channel for Kenyan SMEs and creator-led businesses.",
        )

    if any(term in text for term in ["salary", "pay", "money", "pricing"]):
        return Classification(
            category=TrendCategory.money,
            kenya_relevance=0.74,
            confidence=0.8,
            reasoning="Founder pay and cash discipline are recurring money decisions for early-stage teams.",
        )

    return Classification(
        category=TrendCategory.not_relevant,
        kenya_relevance=0.2,
        confidence=0.72,
        reasoning="The signal does not clearly map to entrepreneurship, money, business or founder culture.",
    )
