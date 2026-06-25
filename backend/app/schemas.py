from datetime import datetime, timezone
from enum import Enum
from typing import Any
from uuid import uuid4

from pydantic import BaseModel, Field


class Source(str, Enum):
    tiktok = "tiktok"
    x = "x"
    reddit = "reddit"
    youtube = "youtube"
    news = "news"


class TrendCategory(str, Enum):
    entrepreneurship = "Entrepreneurship"
    business = "Business"
    money = "Money"
    founder_culture = "Founder Culture"
    not_relevant = "Not Relevant"


class TrendStage(str, Enum):
    emerging = "emerging"
    growing = "growing"
    peak = "peak"
    declining = "declining"


class SignalMetrics(BaseModel):
    likes: int = 0
    shares: int = 0
    comments: int = 0
    views: int = 0


class RawSignal(BaseModel):
    source: Source
    content_id: str
    text: str
    metrics: SignalMetrics = Field(default_factory=SignalMetrics)
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    url: str | None = None


class Classification(BaseModel):
    category: TrendCategory
    kenya_relevance: float = Field(ge=0, le=1)
    confidence: float = Field(ge=0, le=1)
    reasoning: str


class Trend(BaseModel):
    trend_id: str = Field(default_factory=lambda: str(uuid4()))
    title: str
    category: TrendCategory
    score: int = Field(ge=0, le=100)
    stage: TrendStage
    first_seen: datetime
    platforms: list[Source]
    raw_signals: list[RawSignal]
    classification: Classification | None = None


class ContentBrief(BaseModel):
    trend_id: str
    hook: str
    angle: str
    why_it_is_spreading: str
    kenyan_context: str
    script_30_60s: str
    remix_template: str
    generated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class GenerateBriefRequest(BaseModel):
    trend_id: str


class RegisterTrendRequest(BaseModel):
    trend_id: str
    brief_hash: str | None = None


class RegistryRecord(BaseModel):
    trend_id: str
    trend_hash: str
    category: TrendCategory
    score: int
    first_seen: datetime
    content_hash: str | None = None
    on_chain_trend_id: int | None = None
    transaction_hash: str | None = None
    explorer_url: str | None = None
    status: str
    payload: dict[str, Any]


class BlockchainStatus(BaseModel):
    configured: bool = False
    rpc_url: str
    chain_id: int
    contract_address: str | None = None
    connected: bool = False
    trend_count: int | None = None
    signer_address: str | None = None
    error: str | None = None


class OnChainTrend(BaseModel):
    on_chain_trend_id: int
    title: str
    category: str
    score: int
    first_seen: int
    content_hash: str
    creator: str
    verified: bool
