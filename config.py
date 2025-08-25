import os
from typing import Optional

class Settings:
    """Application settings"""
    
    # API Settings
    API_V1_STR: str = "/api/v1"
    PROJECT_NAME: str = "Booking Services API"
    VERSION: str = "1.0.0"
    
    # Database Settings
    DATABASE_URL: str = os.getenv(
        "DATABASE_URL", 
        "sqlite:///./test.db"
    )
    
    # Server Settings
    HOST: str = os.getenv("HOST", "0.0.0.0")
    PORT: int = int(os.getenv("PORT", "8000"))
    
    # CORS Settings
    BACKEND_CORS_ORIGINS: list = ["*"]
    
    # Data Generation Settings
    GENERATE_USERS_COUNT: int = int(os.getenv("GENERATE_USERS_COUNT", "1000"))
    GENERATE_SERVICES_COUNT: int = int(os.getenv("GENERATE_SERVICES_COUNT", "500"))
    GENERATE_BOOKINGS_COUNT: int = int(os.getenv("GENERATE_BOOKINGS_COUNT", "5000"))
    
    # Pagination Settings
    DEFAULT_PAGE_SIZE: int = int(os.getenv("DEFAULT_PAGE_SIZE", "100"))
    MAX_PAGE_SIZE: int = int(os.getenv("MAX_PAGE_SIZE", "1000"))

settings = Settings()
