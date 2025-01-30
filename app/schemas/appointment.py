from pydantic import BaseModel
from datetime import datetime
from typing import Optional
from app.schemas.base import TimestampedSchema
from app.db.models.appointment import AppointmentStatus, ServiceType

class AppointmentBase(BaseModel):
    patient_id: int
    date: datetime
    service_type: ServiceType
    status: AppointmentStatus = AppointmentStatus.SCHEDULED
    notes: Optional[str] = None

class AppointmentCreate(AppointmentBase):
    pass

class AppointmentResponse(AppointmentBase, TimestampedSchema):
    created_by: Optional[int] = None
    patient: Optional['PatientResponse'] = None