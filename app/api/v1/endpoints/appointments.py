from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session
from datetime import datetime, timezone, timedelta
from app.api.deps import get_current_user
from app.db.session import get_db
from app.db.models.appointment import Appointment, AppointmentStatus
from app.schemas.appointment import (
    AppointmentCreate, 
    AppointmentResponse, 
    AppointmentUpdate
)
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
        'end': (apt.datetime + timedelta(minutes=apt.duration)).isoformat(),
        'extendedProps': {
            'patientId': apt.patient_id,
            'serviceType': apt.service_type,
            'duration': apt.duration,
            'notes': apt.notes,
            'status': apt.status
        }
    } for apt in appointments]

@router.post("/", response_model=AppointmentResponse)
async def create_appointment(
    appointment: AppointmentCreate,
    request: Request,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    try:
        date_str = f"{appointment.date}T{appointment.time}"
        appointment_datetime = datetime.fromisoformat(date_str)
        
        new_appointment = Appointment(
            patient_id=appointment.patient_id,
            datetime=appointment_datetime,
            service_type=appointment.service_type,
            notes=appointment.notes,
            duration=appointment.duration or 30,
            created_by=current_user.id,
            status=AppointmentStatus.SCHEDULED
        )
        
        db.add(new_appointment)
        db.commit()
        db.refresh(new_appointment)
        return new_appointment
    except ValueError as e:
        raise HTTPException(status_code=400, detail="Invalid date or time format")
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=str(e))
    
class Appointment(Base):
    __tablename__ = "appointments"
    # ... otros campos ...
    patient = relationship("Patient", back_populates="appointments")