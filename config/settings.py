import os
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import SecretStr
from typing import Optional


SQLITE_URL = "sqlite+aiosqlite:///./mister_predictor.db"


class Settings(BaseSettings):
    BOT_TOKEN: SecretStr = SecretStr("")
    FOOTBALL_DATA_API_KEY: SecretStr = SecretStr("")
    ODDS_API_KEY: SecretStr = SecretStr("")

    SQLITE_DB_PATH: str = SQLITE_URL

    ADMIN_IDS: str = ""

    MIN_VALUE_EDGE: float = 0.05
    DEFAULT_KELLY_FRACTION: float = 0.1
    MAX_STAKE_PERCENT: float = 0.05
    DEFAULT_BANKROLL: float = 1000.0

    DAILY_RUN_HOUR: int = 5
    DAILY_RUN_MINUTE: int = 0

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    @property
    def admin_id_list(self) -> list[int]:
        if not self.ADMIN_IDS:
            return []
        return [int(x.strip()) for x in self.ADMIN_IDS.split(",") if x.strip()]

    @property
    def db_url(self) -> str:
        return self.SQLITE_DB_PATH


settings = Settings()
