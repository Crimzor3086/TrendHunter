from backend.app.config import get_settings
from backend.app.schemas import ContentBrief, RawSignal, RegistryRecord, Trend
from backend.app.persistence import RegistryPersistence


class InMemoryStore:
    def __init__(self, registry_db_path: str) -> None:
        self.raw_signals: dict[str, RawSignal] = {}
        self.trends: dict[str, Trend] = {}
        self.briefs: dict[str, ContentBrief] = {}
        self.registry_records: dict[str, RegistryRecord] = {}
        self._registry_persistence = RegistryPersistence(registry_db_path)
        self._load_registry_records()

    def _load_registry_records(self) -> None:
        for record in self._registry_persistence.load_all():
            self.registry_records[record.trend_id] = record

    def save_signal(self, signal: RawSignal) -> RawSignal:
        self.raw_signals[signal.content_id] = signal
        return signal

    def save_trend(self, trend: Trend) -> Trend:
        self.trends[trend.trend_id] = trend
        return trend

    def save_brief(self, brief: ContentBrief) -> ContentBrief:
        self.briefs[brief.trend_id] = brief
        return brief

    def save_registry_record(self, record: RegistryRecord) -> RegistryRecord:
        self.registry_records[record.trend_id] = record
        self._registry_persistence.save(record)
        return record

    def ranked_trends(self) -> list[Trend]:
        return sorted(self.trends.values(), key=lambda trend: trend.score, reverse=True)


settings = get_settings()
store = InMemoryStore(settings.registry_db_path)
