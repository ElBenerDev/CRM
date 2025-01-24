from fastapi import FastAPI
from config.settings import settings

def create_app() -> FastAPI:
    app = FastAPI(
        title=settings.APP_NAME,
        description="Sistema CRM para gestión dental",
        version=settings.APP_VERSION,
    )
    
    return app