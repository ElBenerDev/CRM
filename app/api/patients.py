from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
from app.utils.db import get_db
from app.services.crm import CRMService
from pydantic import BaseModel, EmailStr
from datetime import datetime

router = APIRouter()

class PatientBase(BaseModel):
    name: str
    email: EmailStr
    phone: str
    address: Optional[str] = None
    notes: Optional[str] = None

class PatientCreate(PatientBase):
    pass

class PatientUpdate(PatientBase):
    pass

class PatientResponse(PatientBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True

@router.post("/", response_model=PatientResponse, status_code=status.HTTP_201_CREATED)
def create_patient(patient: PatientCreate, db: Session = Depends(get_db)):
    crm_service = CRMService(db)
    return crm_service.create_patient(patient)

@router.get("/", response_model=List[PatientResponse])
def get_patients(
    skip: int = 0, 
    limit: int = 100, 
    search: Optional[str] = None,
    db: Session = Depends(get_db)
):
    crm_service = CRMService(db)
    return crm_service.get_patients(skip=skip, limit=limit, search=search)

@router.get("/{patient_id}", response_model=PatientResponse)
def get_patient(patient_id: int, db: Session = Depends(get_db)):
    crm_service = CRMService(db)
    patient = crm_service.get_patient(patient_id)
    if patient is None:
        raise HTTPException(status_code=404, detail="Patient not found")
    return patient

@router.put("/{patient_id}", response_model=PatientResponse)
def update_patient(
    patient_id: int,
    patient_update: PatientUpdate,
    db: Session = Depends(get_db)
):
    crm_service = CRMService(db)
    updated_patient = crm_service.update_patient(patient_id, patient_update)
    if updated_patient is None:
        raise HTTPException(status_code=404, detail="Patient not found")
    return updated_patient

@router.delete("/{patient_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_patient(patient_id: int, db: Session = Depends(get_db)):
    crm_service = CRMService(db)
    if not crm_service.delete_patient(patient_id):
        raise HTTPException(status_code=404, detail="Patient not found")
    return {"ok": True}