from fastapi import APIRouter
from app.api.v1.endpoints import patients, appointments, leads

api_router = APIRouter()

api_router.include_router(patients.router, prefix="/patients", tags=["patients"])
api_router.include_router(appointments.router, prefix="/appointments", tags=["appointments"])
api_router.include_router(leads.router, prefix="/leads", tags=["leads"])