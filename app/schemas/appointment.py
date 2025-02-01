from pydantic import BaseModel
from datetime import datetime
from typing import Optional, ForwardRef, Any
from app.schemas.base import TimestampedSchema
from app.db.models.appointment import AppointmentStatus, ServiceType


# Crear una referencia forward para PatientResponse
PatientResponse = ForwardRef('PatientResponse')

class AppointmentBase(BaseModel):
    patient_id: int
    date: datetime
    service_type: ServiceType
    status: AppointmentStatus = AppointmentStatus.SCHEDULED
    notes: Optional[str] = None
    duration: Optional[int] = 30  # duración en minutos, por defecto 30

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
    date: Optional[datetime] = None
    service_type: Optional[ServiceType] = None
    status: Optional[AppointmentStatus] = None
    notes: Optional[str] = None
    duration: Optional[int] = None

class AppointmentResponse(AppointmentBase, TimestampedSchema):
    id: int
    created_by: Optional[int] = None
    patient: Optional[PatientResponse] = None

    class Config:
        from_attributes = True

# Importar PatientResponse después de definir las clases para evitar la importación circular
from app.schemas.patient import PatientResponse

# Actualizar la referencia forward
AppointmentResponse.model_rebuild()