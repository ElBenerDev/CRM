from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
from app.utils.db import get_db
from app.services.crm import CRMService
from pydantic import BaseModel
from datetime import datetime
from app.models.models import AppointmentStatus

router = APIRouter()

class AppointmentBase(BaseModel):
    patient_id: int
    service_type: str
    date: datetime
    notes: Optional[str] = None
    duration: Optional[int] = 30

class AppointmentCreate(AppointmentBase):
    pass

class AppointmentUpdate(BaseModel):
    service_type: Optional[str] = None
    date: Optional[datetime] = None
    status: Optional[AppointmentStatus] = None
    notes: Optional[str] = None
    duration: Optional[int] = None

class AppointmentResponse(AppointmentBase):
    id: int
    status: AppointmentStatus
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True

@router.post("/", response_model=AppointmentResponse, status_code=status.HTTP_201_CREATED)
def create_appointment(appointment: AppointmentCreate, db: Session = Depends(get_db)):
    crm_service = CRMService(db)
    return crm_service.create_appointment(appointment)

@router.get("/", response_model=List[AppointmentResponse])
def get_appointments(
    skip: int = 0,
    limit: int = 100,
    patient_id: Optional[int] = None,
    status: Optional[AppointmentStatus] = None,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    db: Session = Depends(get_db)
):
    crm_service = CRMService(db)
    return crm_service.get_appointments(
        skip=skip,
        limit=limit,
        patient_id=patient_id,
        status=status,
        start_date=start_date,
        end_date=end_date
    )

@router.get("/{appointment_id}", response_model=AppointmentResponse)
def get_appointment(appointment_id: int, db: Session = Depends(get_db)):
    crm_service = CRMService(db)
    appointment = crm_service.get_appointment(appointment_id)
    if appointment is None:
        raise HTTPException(status_code=404, detail="Appointment not found")
    return appointment

@router.put("/{appointment_id}", response_model=AppointmentResponse)
def update_appointment(
    appointment_id: int,
    appointment_update: AppointmentUpdate,
    db: Session = Depends(get_db)
):
    crm_service = CRMService(db)
    updated_appointment = crm_service.update_appointment(appointment_id, appointment_update)
    if updated_appointment is None:
        raise HTTPException(status_code=404, detail="Appointment not found")
    return updated_appointment

@router.delete("/{appointment_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_appointment(appointment_id: int, db: Session = Depends(get_db)):
    crm_service = CRMService(db)
    if not crm_service.delete_appointment(appointment_id):
        raise HTTPException(status_code=404, detail="Appointment not found")
    return {"ok": True}