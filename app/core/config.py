# app/core/config.py
from typing import List
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    PROJECT_NAME: str = "Dental CRM"
    API_V1_STR: str = "/api"
    ALLOWED_ORIGINS: List[str] = [
        "http://localhost",
        "http://localhost:8000",
        "https://crm-oarr.onrender.com"
    ]
    DATABASE_URL: str = "postgresql://user:password@localhost/dbname"

    class Config:
        env_file = ".env"

settings = Settings()