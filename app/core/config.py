from pydantic_settings import BaseSettings
from dotenv import load_dotenv

# Load environment variables from a .env file if available
load_dotenv()

class Settings(BaseSettings):
    DATABASE_URL: str
    SECRET_KEY: str

    class Config:
        # Optionally specify the .env file explicitly
        env_file = ".env"
        case_sensitive = True

def get_settings() -> Settings:
    return Settings()

settings = get_settings()