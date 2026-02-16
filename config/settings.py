
import os
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import SecretStr

class Settings(BaseSettings):
    # Bot / API Keys
    BOT_TOKEN: SecretStr
    FOOTBALL_DATA_API_KEY: SecretStr
    
    # Database
    DATABASE_URL: str = "sqlite+aiosqlite:///./mister_predictor.db"
    
    # Logic Settings (The "Personality")
    MIN_VALUE_EDGE: float = 0.05  # 5% edge minimum to trigger signal
    DEFAULT_KELLY_FRACTION: float = 0.1  # 10% of Kelly for safety
    
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

settings = Settings()


#LoveFromMister