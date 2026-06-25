import json
from functools import lru_cache
from pathlib import Path

from pydantic import Field, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

ROOT_DIR = Path(__file__).resolve().parents[2]
DEFAULT_DEPLOYMENT_FILE = ROOT_DIR / "deployments" / "fuji-TrendRegistry.json"


def load_deployment_address(deployment_file: Path) -> str | None:
    if not deployment_file.exists():
        return None
    data = json.loads(deployment_file.read_text(encoding="utf-8"))
    address = data.get("address")
    if isinstance(address, str) and address.startswith("0x") and len(address) == 42:
        return address
    return None


class Settings(BaseSettings):
    app_name: str = "Trend Hunter API"
    api_host: str = "0.0.0.0"
    api_port: int = 8000
    frontend_url: str = "http://localhost:8080"

    openai_api_key: str | None = None
    openai_model: str = "gpt-5.5"
    anthropic_api_key: str | None = None

    redis_url: str | None = None
    database_url: str | None = None
    registry_db_path: str = str(ROOT_DIR / "data" / "registry.db")

    use_demo_seed: bool = True
    live_ingestion_on_startup: bool = False
    news_rss_urls: str = ""
    reddit_subreddits: str = "startups,entrepreneur,smallbusiness,SideProject"
    reddit_user_agent: str = "TrendHunterMVP/0.1"
    x_bearer_token: str | None = Field(default=None, repr=False)
    x_query: str = "startup OR founder OR entrepreneur OR SME Kenya"

    avalanche_rpc_url: str = "https://api.avax-test.network/ext/bc/C/rpc"
    avalanche_chain_id: int = 43113
    trend_registry_address: str | None = None
    registry_private_key: str | None = Field(default=None, repr=False)
    deployment_file: str = str(DEFAULT_DEPLOYMENT_FILE)
    tx_confirmation_timeout: int = 120

    cors_origins: str = "http://localhost:8080,http://127.0.0.1:8080,http://localhost:5173,http://127.0.0.1:5173"
    cors_allow_local_network: bool = True

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    @model_validator(mode="after")
    def apply_deployment_defaults(self) -> "Settings":
        if not self.trend_registry_address:
            self.trend_registry_address = load_deployment_address(Path(self.deployment_file))
        return self

    def allowed_origins(self) -> list[str]:
        origins = {origin.strip() for origin in self.cors_origins.split(",") if origin.strip()}
        origins.add(self.frontend_url)
        origins.add("http://localhost:8000")
        origins.add("http://127.0.0.1:8000")
        return sorted(origins)

    def cors_origin_regex(self) -> str | None:
        if not self.cors_allow_local_network:
            return None
        return (
            r"https?://"
            r"(localhost|127\.0\.0\.1|192\.168\.\d{1,3}\.\d{1,3}|10\.\d{1,3}\.\d{1,3}\.\d{1,3}|"
            r"172\.(?:1[6-9]|2\d|3[0-1])\.\d{1,3}\.\d{1,3})"
            r"(:\d+)?"
        )


@lru_cache
def get_settings() -> Settings:
    return Settings()
