from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from app.db.session import get_db
from app.db.models.appointment import Appointment, AppointmentStatus, ServiceType
from pydantic import BaseModel
from typing import List, Optional

# Definiendo los schemas Pydantic
class AppointmentCreate(BaseModel):
    patient_id: int
    date: str  # formato YYYY-MM-DD
    time: str  # formato HH:MM
    service_type: ServiceType
    notes: Optional[str] = None
    duration: Optional[int] = 30

class AppointmentResponse(BaseModel):
    id: int
    patient_id: int
    datetime: datetime
    service_type: ServiceType
    notes: Optional[str]
    duration: int
    status: AppointmentStatus

    class Config:
        from_attributes = True

# El router y los endpoints
router = APIRouter()

@router.get("")
@router.get("/")
async def get_appointments(
    request: Request,
    db: Session = Depends(get_db)
):
    appointments = db.query(Appointment).all()
    return [{
        'id': str(apt.id),
        'title': f"{apt.patient.name}",
        'start': apt.datetime.isoformat(),
        'end': (apt.datetime + timedelta(minutes=apt.duration or 30)).isoformat(),
        'extendedProps': {
            'patientId': apt.patient_id,
            'serviceType': apt.service_type,
            'duration': apt.duration or 30,
            'notes': apt.notes,
            'status': apt.status
        }
    } for apt in appointments]
    
@router.post("/", response_model=AppointmentResponse)
async def create_appointment(
    appointment: AppointmentCreate,
    request: Request,
    db: Session = Depends(get_db)
):
    # Agregar logs para debugging
    print(f"Recibiendo datos de cita: {appointment}")
    try:
        date_str = f"{appointment.date}T{appointment.time}"
        appointment_datetime = datetime.fromisoformat(date_str)
        
        new_appointment = Appointment(
            patient_id=appointment.patient_id,
            datetime=appointment_datetime,
            service_type=appointment.service_type,
            notes=appointment.notes,
            duration=appointment.duration or 30,
            status=AppointmentStatus.SCHEDULED
        )
        
        db.add(new_appointment)
        db.commit()
        db.refresh(new_appointment)
        return new_appointment
    except ValueError as e:
        print(f"Error de validación: {e}")  # Para debugging
        raise HTTPException(status_code=400, detail=f"Invalid date or time format: {str(e)}")
    except Exception as e:
        print(f"Error general: {e}")  # Para debugging
        db.rollback()
        raise HTTPException(status_code=400, detail=str(e))