from pydantic import BaseModel
from datetime import datetime as dt, date, time
from typing import Optional, Annotated
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
    datetime: dt
    status: AppointmentStatus
    created_by: int
    created_at: dt
    updated_at: dt

    class Config:
        from_attributes = True