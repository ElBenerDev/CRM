from typing import Optional, List
from pydantic import BaseModel
from app.schemas.common import TimestampedSchema

class PatientBase(BaseModel):
    name: str
    email: Optional[str] = None
    phone: Optional[str] = None
    address: Optional[str] = None

class PatientCreate(PatientBase):
    pass

class PatientUpdate(PatientBase):
    pass

class PatientResponse(PatientBase, TimestampedSchema):
    id: int
    created_by: Optional[int] = None

    class Config:
        from_attributes = True

# Esta clase se usa solo para las respuestas que incluyen citas
class PatientWithAppointments(PatientResponse):
    appointments: List['AppointmentResponse'] = []

    class Config:
        from_attributes = True

from app.schemas.appointment import AppointmentResponse  # importación al final