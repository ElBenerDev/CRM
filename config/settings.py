from pydantic_settings import BaseSettings
from typing import Optional
from datetime import datetime

class Settings(BaseSettings):
    # Información de la aplicación
    APP_NAME: str = "Dental CRM"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = True
    ENVIRONMENT: str = "development"

    # Configuración de la base de datos
    DATABASE_URL: str = "postgresql://neondb_owner:npg_mTJhLZ5FtRA3@ep-little-term-a8x9ojn0-pooler.eastus2.azure.neon.tech/neondb?sslmode=require"
    DATABASE_POOL_SIZE: int = 5
    DATABASE_MAX_OVERFLOW: int = 10
    DATABASE_POOL_TIMEOUT: int = 30

    # Usuario por defecto
    DEFAULT_USER_NAME: str = "ElBenerDev"
    DEFAULT_USER_ROLE: str = "Admin"

    # Configuración del servidor
    PORT: int = 8000
    HOST: str = "0.0.0.0"
    
    class Config:
        env_file = ".env"
        case_sensitive = True

settings = Settings()