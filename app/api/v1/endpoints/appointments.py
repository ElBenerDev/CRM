from typing import List
from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session
from app.api.deps import get_current_user
from app.db.session import get_db
from app.db.models.appointment import Appointment
from app.schemas.appointment import AppointmentCreate, AppointmentResponse
from datetime import datetime

router = APIRouter()

@router.get("/", response_model=List[AppointmentResponse])
async def get_appointments(
    request: Request,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    appointments = db.query(Appointment)\
        .order_by(Appointment.date.desc())\
        .all()
    return appointments

@router.post("/", response_model=AppointmentResponse)
async def create_appointment(
    appointment: AppointmentCreate,
    request: Request,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    new_appointment = Appointment(
        patient_id=appointment.patient_id,
        date=appointment.date,
        service_type=appointment.service_type,
        notes=appointment.notes,
        created_by=current_user.id
    )
    
    db.add(new_appointment)
    try:
        db.commit()
        db.refresh(new_appointment)
        return new_appointment
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=str(e))