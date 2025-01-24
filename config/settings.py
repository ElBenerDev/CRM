from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    APP_NAME: str = "Dental CRM"
    APP_VERSION: str = "1.0.0"
    DATABASE_URL: str = "postgresql://neondb_owner:npg_mTJhLZ5FtRA3@ep-little-term-a8x9ojn0-pooler.eastus2.azure.neon.tech/neondb?sslmode=require"

    class Config:
        env_file = ".env"
        extra = "allow"  # Permite campos adicionales

settings = Settings()