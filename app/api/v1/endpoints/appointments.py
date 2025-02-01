from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session
from datetime import datetime, timezone
from app.api.deps import get_current_user
from app.db.session import get_db
from app.db.models.appointment import Appointment
from app.schemas.appointment import AppointmentCreate, AppointmentResponse, AppointmentUpdate
from typing import List

router = APIRouter()

@router.get("/", response_model=List[dict])
async def get_appointments(
    request: Request,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    appointments = db.query(Appointment).all()
    return [{
        'id': str(apt.id),
        'title': f"{apt.patient.name}",
        'start': apt.datetime.isoformat(),
        'end': (apt.datetime + apt.duration).isoformat(),
        'extendedProps': {
            'patientId': apt.patient_id,
            'serviceType': apt.service_type
        }
    } for apt in appointments]

@router.post("/", response_model=AppointmentResponse)
async def create_appointment(
    appointment: AppointmentCreate,
    request: Request,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    # Convertir fecha y hora a datetime
    date_str = f"{appointment.date}T{appointment.time}"
    appointment_datetime = datetime.fromisoformat(date_str)
    
    new_appointment = Appointment(
        patient_id=appointment.patient_id,
        datetime=appointment_datetime,
        service_type=appointment.service_type,
        duration=appointment.duration  # Puedes establecer una duración predeterminada
    )
    
    db.add(new_appointment)
    try:
        db.commit()
        db.refresh(new_appointment)
        return new_appointment
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/{appointment_id}", response_model=AppointmentResponse)
async def get_appointment(
    appointment_id: int,
    request: Request,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    appointment = db.query(Appointment).filter(Appointment.id == appointment_id).first()
    if not appointment:
        raise HTTPException(status_code=404, detail="Appointment not found")
    return appointment