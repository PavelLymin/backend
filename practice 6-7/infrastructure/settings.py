from pydantic import BaseModel
from pydantic_settings import BaseSettings, SettingsConfigDict
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent


class RunConfig(BaseModel):
    host: str = "localhost"
    port: int = 8000


class DatabaseConfig(BaseModel):
    url: str
    echo: bool = False
    echo_pool: bool = False
    pool_size: int = 50
    max_overflow: int = 10


class UrlPrefix(BaseModel):
    prefix: str = "/api"


class ProrationStrategy(BaseModel):
    kind: str = "immediate"


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=(BASE_DIR / ".env.template", BASE_DIR / ".env"),
        case_sensitive=False,
        env_nested_delimiter="__",
        env_prefix="APP_CONFIG__",
    )
    run: RunConfig = RunConfig()
    url: UrlPrefix = UrlPrefix()
    db: DatabaseConfig
    proration: ProrationStrategy = ProrationStrategy()
