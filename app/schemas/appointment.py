from pydantic import BaseModel
from datetime import datetime as dt, date, time
from typing import Optional
from app.db.models.appointment import ServiceType, AppointmentStatus

class AppointmentBase(BaseModel):
    patient_id: int
    service_type: ServiceType
    notes: Optional[str] = None
    duration: Optional[int] = 30

class AppointmentCreate(AppointmentBase):
    date: date
    time: time

class AppointmentUpdate(AppointmentBase):
    status: Optional[AppointmentStatus] = None

class AppointmentResponse(AppointmentBase):
    id: int
    date: dt  # Cambiado de datetime a date para coincidir con el modelo
    status: AppointmentStatus
    created_at: Optional[dt] = None
    updated_at: Optional[dt] = None

    class Config:
        from_attributes = True