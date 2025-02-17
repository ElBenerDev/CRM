from pydantic import BaseSettings
from functools import lru_cache
import os
from typing import Optional

class Settings(BaseSettings):
    APP_NAME: str = "Medical CRM"  # Cambiamos el nombre para que sea más genérico
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False
    ENVIRONMENT: str = "production"
    
    # Database
    DATABASE_URL: str
    
    # Security
    SECRET_KEY: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    ALGORITHM: str = "HS256"  # Agregamos el algoritmo para JWT
    
    # Specialties Configuration
    AVAILABLE_SPECIALTIES: list = [
        "dental",
        "ophthalmology",
        "general_medicine"
    ]
    
    class Config:
        env_file = ".env"
        case_sensitive = True

@lru_cache()
def get_settings() -> Settings:
    return Settings()

settings = get_settings()