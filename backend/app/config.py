from functools import lru_cache
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "Trend Hunter API"
    api_host: str = "0.0.0.0"
    api_port: int = 8000
    frontend_url: str = "http://localhost:5173"

    openai_api_key: str | None = None
    openai_model: str = "gpt-5.5"
    anthropic_api_key: str | None = None

    redis_url: str | None = "redis://localhost:6379/0"
    database_url: str | None = None

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

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")


@lru_cache
def get_settings() -> Settings:
    return Settings()
