from pydantic_settings import BaseSettings
from typing import List

class Settings(BaseSettings):
    # Información de la aplicación
    SECRET_KEY: str = "8f96d3a4e5b7c9d1f2g3h4j5k6l7m8n9p0q1r2s3t4u5v6w7x8y9z"
    APP_NAME: str = "Dental CRM"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = True
    ENVIRONMENT: str = "development"

    # Configuración de la base de datos
    DATABASE_URL: str = "postgresql://neondb_owner:npg_mTJhLZ5FtRA3@ep-little-term-a8x9ojn0-pooler.eastus2.azure.neon.tech/neondb?sslmode=require"
    DATABASE_POOL_SIZE: int = 5
    DATABASE_MAX_OVERFLOW: int = 10
    DATABASE_POOL_TIMEOUT: int = 30

    # Configuración CORS
    ALLOWED_ORIGINS: List[str] = [
        "http://localhost",
        "http://localhost:8000",
        "https://crm-oarr.onrender.com"
    ]

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