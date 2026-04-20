from pydantic import BaseModel
from pydantic_settings import (
    BaseSettings,
    SettingsConfigDict,
)
from typing import Literal

class ApiConfig(BaseModel):
    router_key: str


class RunConfig(BaseModel):
    host: str = "0.0.0.0"
    port: int = 8000
    reload: bool = True


class DatabaseConfig(BaseModel):
    url: str
    echo: bool = False
    future: bool = True
    

class UrlPrefix(BaseModel):
    auth: str = "/auth"
    prefix: str = "/api"
    recipes: str = "/recipes"
    cuisines: str = "/cuisines"
    allergens: str = "/allergens"
    ingredients: str = "/ingredients"
    users: str = "/users"

    @property
    def bearer_token_url(self) -> str:
        # api/auth/login
        parts = (self.prefix, self.auth, "/login")
        path = "".join(parts)
        return path.removeprefix("/")
    

class AuthConfig(BaseModel):
    cookie_max_age: int = 3600
    cookie_secure: bool = False
    cookie_samesite: Literal["lax", "strict", "none"] = "lax"


class AccessToken(BaseModel):
    lifetime_seconds: int = 3600
    reset_password_token_secret: str
    verification_token_secret: str


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=(".env.template", ".env"),
        case_sensitive=False,
        env_nested_delimiter="__",
        env_prefix="APP_CONFIG__",
    )
    run: RunConfig = RunConfig()
    url: UrlPrefix = UrlPrefix()
    auth: AuthConfig = AuthConfig()
    db: DatabaseConfig
    access_token: AccessToken
    api: ApiConfig
    

settings = Settings()
