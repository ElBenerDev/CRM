# app/schemas/schemas.py
from pydantic import Field
from pydantic import BaseModel, field_validator
from typing import Optional
from datetime import datetime

class PatientCreate(BaseModel):
    name: str
    email: Optional[str] = None
    phone: Optional[str] = None

    @field_validator('name')
    def validate_name(cls, v):
        if not v or len(v.strip()) < 2:
            raise ValueError('El nombre debe tener al menos 2 caracteres')
        return v.strip()

    @field_validator('email')
    def validate_email(cls, v):
        if v is not None and not '@' in v:
            raise ValueError('Email inválido')
        return v.lower() if v else v

    @field_validator('phone')
    def validate_phone(cls, v):
        if v is not None:
            cleaned = ''.join(filter(str.isdigit, v))
            if len(cleaned) < 10:
                raise ValueError('El número de teléfono debe tener al menos 10 dígitos')
        return v

class AppointmentCreate(BaseModel):
    patient_id: int
    date: str = Field(..., description="Fecha y hora de la cita en formato YYYY-MM-DDTHH:mm")
    service_type: str
    status: str = "scheduled"
    notes: Optional[str] = None

    @field_validator('date')
    def validate_date(cls, v):
        try:
            # Validar el formato de la fecha
            datetime.strptime(v, '%Y-%m-%dT%H:%M')
            return v
        except ValueError:
            raise ValueError("Formato de fecha inválido. Use YYYY-MM-DDTHH:MM")

    @field_validator('service_type')
    def validate_service_type(cls, v):
        valid_types = ["consulta", "limpieza", "emergencia", "revision"]
        if v.lower() not in valid_types:
            raise ValueError(f"Tipo de servicio inválido. Use uno de: {', '.join(valid_types)}")
        return v.lower()

    @field_validator('status')
    def validate_status(cls, v):
        valid_statuses = ["scheduled", "completed", "cancelled", "pending"]
        if v.lower() not in valid_statuses:
            raise ValueError(f"Estado inválido. Use uno de: {', '.join(valid_statuses)}")
        return v.lower()

class LeadCreate(BaseModel):
    name: str
    email: str
    phone: str
    status: str = "nuevo"
    source: Optional[str] = None
    interest: Optional[str] = None
    priority: str = "media"
    notes: Optional[str] = None

    @field_validator('status')
    def validate_status(cls, v):
        valid_statuses = ["nuevo", "contactado", "convertido", "perdido"]
        if v.lower() not in valid_statuses:
            raise ValueError(f"Estado inválido. Use uno de: {', '.join(valid_statuses)}")
        return v.lower()

    @field_validator('priority')
    def validate_priority(cls, v):
        valid_priorities = ["alta", "media", "baja"]
        if v.lower() not in valid_priorities:
            raise ValueError(f"Prioridad inválida. Use uno de: {', '.join(valid_priorities)}")
        return v.lower()

class AppointmentUpdate(BaseModel):
    status: str
    notes: Optional[str] = None

    @field_validator('status')
    def validate_status(cls, v):
        valid_statuses = ["scheduled", "completed", "cancelled", "pending"]
        if v.lower() not in valid_statuses:
            raise ValueError(f"Estado inválido. Use uno de: {', '.join(valid_statuses)}")
        return v.lower()

    @field_validator('notes')
    def validate_notes(cls, v):
        if v is not None and len(v) > 500:
            raise ValueError("Las notas no pueden exceder los 500 caracteres")
        return v

class PatientResponse(BaseModel):
    id: int
    name: str
    email: Optional[str]
    phone: Optional[str]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class AppointmentResponse(BaseModel):
    id: int
    patient_id: int
    patient_name: str  # Agregar este campo
    date: datetime
    service_type: str
    status: str
    notes: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True

class LeadResponse(BaseModel):
    id: int
    name: str
    email: str
    phone: str
    status: str
    source: Optional[str] = None
    interest: Optional[str] = None
    priority: str
    notes: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

# Esquemas adicionales para respuestas específicas
class SuccessResponse(BaseModel):
    status: str = "success"
    message: str

class ErrorResponse(BaseModel):
    status: str = "error"
    detail: str