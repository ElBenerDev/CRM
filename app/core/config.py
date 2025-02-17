from pydantic_settings import BaseSettings
from dotenv import load_dotenv
import os

# Load environment variables from a .env file if available
if os.getenv('ENVIRONMENT') != 'production':
    load_dotenv()

class Settings(BaseSettings):
    APP_NAME: str = "Medical CRM"  # Cambiamos el nombre para que sea más genérico
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False
    ENVIRONMENT: str = "production"
    
    # Database
    DATABASE_URL: str
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
        # Optionally specify the .env file explicitly
        env_file = ".env"
        case_sensitive = True

def get_settings() -> Settings:
    return Settings()

settings = get_settings()