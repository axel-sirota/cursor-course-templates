"""
Application Configuration
"""
from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import List


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    model_config = SettingsConfigDict(env_file=".env", extra="ignore", case_sensitive=True)

    # Server Configuration
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    DEBUG: bool = True

    # Database Configuration
    DATABASE_URL: str

    # CORS Configuration (comma-separated string converted to list)
    ALLOWED_ORIGINS: str = "http://localhost:3000"
    
    @property
    def origins_list(self) -> List[str]:
        """Convert comma-separated ALLOWED_ORIGINS to list."""
        return [origin.strip() for origin in self.ALLOWED_ORIGINS.split(",")]


settings = Settings()
