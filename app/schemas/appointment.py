from typing import Optional
from pydantic import BaseModel
from datetime import datetime
from app.schemas.common import TimestampedSchema
from app.db.models.appointment import AppointmentStatus, ServiceType
from app.schemas.patient import PatientResponse

class AppointmentBase(BaseModel):
    patient_id: int
    service_type: ServiceType
    status: AppointmentStatus = AppointmentStatus.SCHEDULED
    notes: Optional[str] = None
    duration: Optional[int] = 30

    class Config:
        from_attributes = True

class AppointmentCreate(BaseModel):
    patient_id: int
    date: str  # Fecha en formato YYYY-MM-DD
    time: str  # Hora en formato HH:MM
    service_type: ServiceType
    notes: Optional[str] = None
    duration: Optional[int] = 30

    class Config:
        from_attributes = True

class AppointmentUpdate(BaseModel):
    patient_id: Optional[int] = None
    date: Optional[str] = None
    time: Optional[str] = None
    service_type: Optional[ServiceType] = None
    status: Optional[AppointmentStatus] = None
    notes: Optional[str] = None
    duration: Optional[int] = None

    class Config:
        from_attributes = True

class AppointmentResponse(TimestampedSchema):
    id: int
    patient_id: int
    datetime: datetime
    duration: int
    service_type: ServiceType
    status: AppointmentStatus
    notes: Optional[str] = None
    created_by: Optional[int] = None
    patient: Optional[PatientResponse] = None

    class Config:
        from_attributes = True