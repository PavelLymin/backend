from pydantic import BaseModel
from pydantic_settings import (
    BaseSettings,
    SettingsConfigDict,
)

class ApiConfig(BaseModel):
    router_key: str


class RunConfig(BaseModel):
    host: str = "0.0.0.0"
    port: int = 8000
    reload: bool = False


class DatabaseConfig(BaseModel):
    url: str
    echo: bool = True
    future: bool = True


class UrlPrefix(BaseModel):
    prefix: str = "/api"
    items: str = "/items"
    auth: str = "/auth"
    students: str = "/students"
    images: str = "/images"
    recipes: str = "/recipes"


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=(".env.template", ".env"),
        case_sensitive=False,
        env_nested_delimiter="__",
        env_prefix="APP_CONFIG__",
    )
    run: RunConfig = RunConfig()
    url: UrlPrefix = UrlPrefix()
    db: DatabaseConfig
    api: ApiConfig

settings = Settings()
