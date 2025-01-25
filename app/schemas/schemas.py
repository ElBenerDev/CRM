# app/schemas/schemas.py

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
    date: str
    service_type: str
    status: str = "scheduled"
    notes: Optional[str] = None

    @field_validator('date')
    def validate_date(cls, v):
        try:
            date = datetime.strptime(v, "%Y-%m-%dT%H:%M")
            if date < datetime.now():
                raise ValueError("La fecha no puede ser en el pasado")
            if date > datetime.now() + datetime.timedelta(days=365):
                raise ValueError("La fecha no puede ser más de un año en el futuro")
            return v
        except ValueError as e:
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

    @field_validator('notes')
    def validate_notes(cls, v):
        if v is not None:
            if len(v) > 500:
                raise ValueError("Las notas no pueden exceder los 500 caracteres")
        return v

class LeadCreate(BaseModel):
    name: str
    email: str
    phone: str
    status: str = "nuevo"
    notes: Optional[str] = None

    @field_validator('name')
    def validate_name(cls, v):
        if not v or len(v.strip()) < 2:
            raise ValueError('El nombre debe tener al menos 2 caracteres')
        return v.strip()

    @field_validator('email')
    def validate_email(cls, v):
        if not '@' in v:
            raise ValueError('Email inválido')
        return v.lower()

    @field_validator('phone')
    def validate_phone(cls, v):
        cleaned = ''.join(filter(str.isdigit, v))
        if len(cleaned) < 10:
            raise ValueError('El número de teléfono debe tener al menos 10 dígitos')
        return v

    @field_validator('status')
    def validate_status(cls, v):
        valid_statuses = ["nuevo", "contactado", "convertido", "perdido"]
        if v.lower() not in valid_statuses:
            raise ValueError(f"Estado inválido. Use uno de: {', '.join(valid_statuses)}")
        return v.lower()

    @field_validator('notes')
    def validate_notes(cls, v):
        if v is not None and len(v) > 500:
            raise ValueError("Las notas no pueden exceder los 500 caracteres")
        return v

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
    patient_name: Optional[str]  # Agregado para mostrar el nombre del paciente
    date: datetime
    service_type: str
    status: str
    notes: Optional[str]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class LeadResponse(BaseModel):
    id: int
    name: str
    email: str
    phone: str
    status: str
    notes: Optional[str]
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