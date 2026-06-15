from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    app_name: str = "Tima"
    debug: bool = False
    mongodb_url: str = "mongodb://localhost:27017"
    mongodb_db: str = "tima"
    secret_key: str
    access_token_expire_minutes: int = 30
    algorithm: str = "HS256"


settings = Settings()
