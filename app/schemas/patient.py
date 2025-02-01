from pydantic import BaseModel
from typing import Optional, List, ForwardRef
from app.schemas.base import TimestampedSchema

# Crear una referencia forward para AppointmentResponse
AppointmentResponse = ForwardRef('AppointmentResponse')

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
    appointments: Optional[List[AppointmentResponse]] = None

    class Config:
        from_attributes = True

# Importar AppointmentResponse después de definir las clases
from app.schemas.appointment import AppointmentResponse

# Actualizar la referencia forward
PatientResponse.model_rebuild()