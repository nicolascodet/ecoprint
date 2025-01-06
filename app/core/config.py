from pydantic_settings import BaseSettings
from functools import lru_cache
import os
from dotenv import load_dotenv
from typing import Optional

load_dotenv()

class Settings(BaseSettings):
    PROJECT_NAME: str = "EcoPrint"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api/v1"
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    DATABASE_URL: str = "sqlite:////tmp/ecoprint.db" if os.environ.get("VERCEL") else "sqlite:///./ecoprint.db"
    OPENAI_API_KEY: Optional[str] = None
    
    # Strava settings (optional)
    STRAVA_CLIENT_ID: Optional[str] = None
    STRAVA_CLIENT_SECRET: Optional[str] = None
    STRAVA_WEBHOOK_VERIFY_TOKEN: Optional[str] = None
    STRAVA_REDIRECT_URI: Optional[str] = None
    
    class Config:
        env_file = ".env"
        extra = "allow"  # Allow extra fields to be passed

@lru_cache()
def get_settings() -> Settings:
    return Settings()
