"""
Configuration settings for the Phantom Forecast Tool API.

Uses pydantic-settings BaseSettings pattern from congressional-trading-system.
"""

from functools import lru_cache
from typing import List, Optional

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # Application
    app_name: str = "Phantom Forecast Tool API"
    app_version: str = "0.1.0"
    debug: bool = False
    environment: str = "development"

    # Server
    host: str = "0.0.0.0"
    port: int = 8000

    # Database (PostgreSQL)
    database_url: str = "sqlite:///./phantom_forecast.db"
    supabase_database_url: Optional[str] = None  # Legacy, use database_url

    # Supabase
    supabase_url: Optional[str] = None
    supabase_anon_key: Optional[str] = None
    supabase_service_role_key: Optional[str] = None
    supabase_jwt_secret: Optional[str] = None

    # Anthropic (Claude API for Phantom reasoning)
    anthropic_api_key: Optional[str] = None

    # Perplexity (Market data intelligence)
    perplexity_api_key: Optional[str] = None

    # Finnhub (Financial data)
    finnhub_api_key: Optional[str] = None

    # CORS
    cors_origins: List[str] = [
        "http://localhost:3000",
        "http://localhost:3003",
        "http://localhost:6100",
        "http://localhost:8080",
        "https://frontend-production-ce8b.up.railway.app",
    ]
    cors_allow_credentials: bool = True
    cors_allow_methods: List[str] = ["*"]
    cors_allow_headers: List[str] = ["*"]

    # Phantom Engine Settings
    phantom_temperature: float = 1.0  # High for distinct responses
    synthesis_temperature: float = 0.7  # Balanced for synthesis
    parsing_temperature: float = 0.3  # Low for consistency

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()


# Convenience export
settings = get_settings()
