"""Application configuration using Pydantic Settings."""
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    # Application metadata
    app_name: str = "Verityn"
    app_version: str = "0.3.0"
    api_version: str = "v1"
    
    # MongoDB configuration
    mongodb_uri: str = "mongodb://localhost:27017"
    mongodb_database: str = "verityn"
    
    # Tavily API configuration
    tavily_api_key: str = ""
    tavily_max_results: int = 5
    tavily_search_timeout: int = 10
    
    # Server configuration
    debug: bool = False
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False
    )


# Global settings instance
settings = Settings()
