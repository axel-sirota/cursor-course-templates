"""
Application Configuration
"""
from pydantic_settings import BaseSettings
from typing import List


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    # Server Configuration
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    DEBUG: bool = True
    
    # Database Configuration
    DATABASE_URL: str
    
    # CORS Configuration (comma-separated string converted to list)
    ALLOWED_ORIGINS: str = "http://localhost:3000"
    
    class Config:
        env_file = ".env"
        case_sensitive = True
    
    @property
    def origins_list(self) -> List[str]:
        """Convert comma-separated ALLOWED_ORIGINS to list."""
        return [origin.strip() for origin in self.ALLOWED_ORIGINS.split(",")]


settings = Settings()
