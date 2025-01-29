from fastapi import APIRouter, Request, Depends, HTTPException, status
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import datetime, timezone
from typing import List

from app.utils.db import get_db
from app.models.models import Patient, Appointment, User
from app.schemas.schemas import PatientCreate, PatientResponse

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")

@router.get("/patients", response_class=HTMLResponse)
async def patients_page(request: Request, db: Session = Depends(get_db)):
    try:
        user_id = request.session.get("user_id")
        if not user_id:
            return RedirectResponse(url="/auth/login", status_code=302)
            
        current_user = db.query(User).filter(User.id == user_id).first()
        if not current_user:
            return RedirectResponse(url="/auth/login", status_code=302)

        patients = db.query(Patient).order_by(Patient.created_at.desc()).all()
        
        return templates.TemplateResponse(
            "patients.html",
            {
                "request": request,
                "user": {
                    "name": current_user.name,
                    "email": current_user.email,
                    "role": "Admin"
                },
                "active": "patients",
                "patients": patients,
                "datetime": datetime
            }
        )
    except Exception as e:
        print(f"Error en patients_page: {str(e)}")
        return RedirectResponse(url="/auth/login", status_code=302)

@router.post("/api/patients/", response_model=PatientResponse)
async def create_patient(
    patient: PatientCreate,
    request: Request,
    db: Session = Depends(get_db)
):
    try:
        user_id = request.session.get("user_id")
        if not user_id:
            raise HTTPException(status_code=401, detail="No autenticado")

        new_patient = Patient(
            name=patient.name,
            email=patient.email,
            phone=patient.phone,
            address=patient.address,
            notes=patient.notes,
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc),
            created_by=user_id
        )
        
        db.add(new_patient)
        db.commit()
        db.refresh(new_patient)
        return new_patient
    
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/api/patients/", response_model=List[PatientResponse])
async def get_patients(
    request: Request,
    db: Session = Depends(get_db)
):
    try:
        user_id = request.session.get("user_id")
        if not user_id:
            raise HTTPException(status_code=401, detail="No autenticado")

        patients = db.query(Patient).order_by(Patient.created_at.desc()).all()
        return patients
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/api/patients/", response_model=PatientResponse)
async def create_patient(
    patient: PatientCreate,
    db: Session = Depends(get_db),
    request: Request = None
):
    try:
        user_id = request.session.get("user_id")
        if not user_id:
            raise HTTPException(status_code=401, detail="No autenticado")

        patient = db.query(Patient).filter(Patient.id == patient_id).first()
        if not patient:
            raise HTTPException(status_code=404, detail="Paciente no encontrado")
        
        return patient
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))