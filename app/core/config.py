import os
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    APP_NAME: str = "CRM Dental"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = True

    # Configuración de JWT
    SECRET_KEY: str = "09d25e094faa6ca2556c818166b7a9563b93f7099f6f0f4caa6cf63b88e8d3e7"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    # Configuración de directorios
    BASE_DIR: str = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    STATIC_DIR: str = os.path.join(BASE_DIR, "app", "static")
    TEMPLATES_DIR: str = os.path.join(BASE_DIR, "app", "templates")

    class Config:
        env_file = ".env"

settings = Settings()