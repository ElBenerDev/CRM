from pydantic import BaseModel, EmailStr
from typing import Optional, List
from app.schemas.base import TimestampedSchema

class PatientBase(BaseModel):
    name: str
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    address: Optional[str] = None
    notes: Optional[str] = None

class PatientCreate(PatientBase):
    pass

class PatientResponse(PatientBase, TimestampedSchema):
    created_by: Optional[int] = None
    appointments: Optional[List['AppointmentResponse']] = []