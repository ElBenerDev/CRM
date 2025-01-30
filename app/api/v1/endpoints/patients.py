from typing import List
from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session
from app.api.deps import get_current_user
from app.db.session import get_db
from app.db.models.patient import Patient
from app.schemas.patient import PatientCreate, PatientResponse
from datetime import datetime

router = APIRouter()

@router.get("/", response_model=List[PatientResponse])
async def get_patients(
    request: Request,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    patients = db.query(Patient).order_by(Patient.created_at.desc()).all()
    return patients

@router.post("/", response_model=PatientResponse)
async def create_patient(
    patient: PatientCreate,
    request: Request,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    new_patient = Patient(
        name=patient.name,
        email=patient.email,
        phone=patient.phone,
        address=patient.address,
        notes=patient.notes,
        created_at=datetime.utcnow(),
        created_by=current_user.id
    )
    
    db.add(new_patient)
    try:
        db.commit()
        db.refresh(new_patient)
        return new_patient
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=str(e))