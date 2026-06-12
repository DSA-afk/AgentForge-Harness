from pydantic_settings import BaseSettings, SettingsConfigDict
from pathlib import Path

BASE_DIR = Path(__file__).parent.parent.parent


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=BASE_DIR / ".env", extra="ignore")

    # 数据库
    APP_DB_URL: str
    MIGRATION_DB_URL: str

    # JWT
    JWT_SECRET_KEY: str  # 必填，缺了直接报错
    JWT_ALGORITHM: str = "HS256"  # 有默认值
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 15  # 自动转 int，不用手动 int()
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7


settings = Settings()
