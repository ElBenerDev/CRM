from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

from fastapi import FastAPI, Request, HTTPException, Depends
from fastapi.params import Form
from fastapi.responses import JSONResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.encoders import jsonable_encoder
from sqlalchemy import func
from sqlalchemy.orm import Session

# Importaciones de la aplicación
from app.db.session import get_db, engine
from app.db.models.base import Base
from app.db.models.patient import Patient
from app.db.models.appointment import Appointment, ServiceType, AppointmentStatus
from app.db.models.lead import Lead, LeadStatus


# Crear tablas en la base de datos
Base.metadata.drop_all(bind=engine) 
Base.metadata.create_all(bind=engine)

app = FastAPI(title="Dental CRM")

# Montar archivos estáticos
BASE_DIR = Path(__file__).resolve().parent
app.mount("/static", StaticFiles(directory=str(BASE_DIR / "app" / "static")), name="static")

# Configurar templates
templates = Jinja2Templates(directory=str(BASE_DIR / "app" / "templates"))

@app.get("/")
@app.get("/dashboard")
async def dashboard(
    request: Request,
    db: Session = Depends(get_db)
):
    # Estadísticas
    total_patients = db.query(func.count(Patient.id)).scalar() or 0
    total_appointments = db.query(func.count(Appointment.id)).scalar() or 0
    total_leads = db.query(func.count(Lead.id)).scalar() or 0
    
    # Citas de hoy
    today = datetime.now(timezone.utc)
    appointments_today = db.query(func.count(Appointment.id))\
        .filter(func.date(Appointment.date) == today.date())\
        .scalar() or 0

    # Próximas citas
    upcoming_appointments = db.query(Appointment)\
        .join(Patient)\
        .filter(Appointment.date >= today)\
        .order_by(Appointment.date)\
        .limit(5)\
        .all()

    # Últimos pacientes
    recent_patients = db.query(Patient)\
        .order_by(Patient.created_at.desc())\
        .limit(5)\
        .all()

    return templates.TemplateResponse(
        "dashboard.html",
        {
            "request": request,
            "active": "dashboard",
            "stats": {
                "total_patients": total_patients,
                "total_appointments": total_appointments,
                "appointments_today": appointments_today,
                "total_leads": total_leads
            },
            "upcoming_appointments": upcoming_appointments,
            "recent_patients": recent_patients,
            "datetime": datetime
        }
    )

@app.get("/patients")
async def patients_page(
    request: Request,
    db: Session = Depends(get_db)
):
    patients = db.query(Patient).order_by(Patient.created_at.desc()).all()
    return templates.TemplateResponse(
        "patients.html",
        {
            "request": request,
            "active": "patients",
            "patients": patients
        }
    )

@app.get("/appointments")
async def appointments_page(
    request: Request,
    db: Session = Depends(get_db)
):
    appointments = db.query(Appointment)\
        .join(Patient)\
        .order_by(Appointment.date.desc())\
        .all()
    
    patients = db.query(Patient).order_by(Patient.name).all()
    
    return templates.TemplateResponse(
        "appointments.html",
        {
            "request": request,
            "active": "appointments",
            "appointments": appointments,
            "patients": patients,
            "datetime": datetime
        }
    )

@app.post("/api/appointments/")
async def create_appointment(
    request: Request,
    db: Session = Depends(get_db)
):
    try:
        # Obtener datos del body JSON
        appointment_data = await request.json()
        
        # Convertir la fecha string a datetime
        appointment_date = datetime.fromisoformat(appointment_data["date"])
        
        # Crear la nueva cita
        new_appointment = Appointment(
            patient_id=int(appointment_data["patient_id"]),
            date=appointment_date,
            service_type=appointment_data["service_type"],
            notes=appointment_data.get("notes"),
            status=AppointmentStatus.SCHEDULED
        )
        
        db.add(new_appointment)
        db.commit()
        db.refresh(new_appointment)
        
        return JSONResponse(
            content={"message": "Cita creada exitosamente", "id": new_appointment.id},
            status_code=201
        )
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=str(e))
    

@app.put("/api/appointments/{appointment_id}/cancel")
async def cancel_appointment(
    appointment_id: int,
    db: Session = Depends(get_db)
):
    try:
        appointment = db.query(Appointment).filter(Appointment.id == appointment_id).first()
        if not appointment:
            raise HTTPException(status_code=404, detail="Cita no encontrada")
        
        appointment.status = AppointmentStatus.CANCELLED
        db.commit()
        
        return JSONResponse(
            content={"message": "Cita cancelada exitosamente"},
            status_code=200
        )
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/leads")
async def leads_page(
    request: Request,
    db: Session = Depends(get_db)
):
    leads = db.query(Lead).order_by(Lead.created_at.desc()).all()
    return templates.TemplateResponse(
        "leads.html",
        {
            "request": request,
            "active": "leads",
            "leads": leads
        }
    )
    
@app.post("/patients/create")
async def create_patient(
    request: Request,
    name: str = Form(...),
    email: Optional[str] = Form(None),
    phone: Optional[str] = Form(None),
    notes: Optional[str] = Form(None),
    db: Session = Depends(get_db)
):
    try:
        new_patient = Patient(
            name=name,
            email=email,
            phone=phone,
            notes=notes
        )
        db.add(new_patient)
        db.commit()
        db.refresh(new_patient)
        return RedirectResponse(url="/patients", status_code=303)
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/leads/create")
async def create_lead(
    request: Request,
    name: str = Form(...),
    email: Optional[str] = Form(None),
    phone: Optional[str] = Form(None),
    source: Optional[str] = Form(None),
    notes: Optional[str] = Form(None),
    db: Session = Depends(get_db)
):
    try:
        new_lead = Lead(
            name=name,
            email=email,
            phone=phone,
            source=source,
            notes=notes,
            status=LeadStatus.NUEVO
        )
        db.add(new_lead)
        db.commit()
        db.refresh(new_lead)
        return RedirectResponse(url="/leads", status_code=303)
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=str(e))

@app.put("/leads/{lead_id}/update-status")
async def update_lead_status(
    lead_id: int,
    status: LeadStatus,
    db: Session = Depends(get_db)
):
    try:
        lead = db.query(Lead).filter(Lead.id == lead_id).first()
        if not lead:
            raise HTTPException(status_code=404, detail="Lead no encontrado")
        
        lead.status = status
        db.commit()
        
        return JSONResponse(content={"message": "Estado actualizado exitosamente"})
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)