from pathlib import Path

from pydantic_settings import BaseSettings,SettingsConfigDict


class DbConfig(BaseSettings):

    model_config = SettingsConfigDict(
        env_file=Path(__file__).parent.parent.parent / ".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )

    DB_URL: str


config = DbConfig()