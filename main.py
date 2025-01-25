from fastapi import FastAPI, Request, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from datetime import datetime, timedelta
from config.settings import settings
import os
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.utils.db import get_db, engine, Base, verify_db_connection
from app.models.models import Patient, Appointment, Lead
from typing import Optional
from pydantic import BaseModel

# Verificar conexión a la base de datos y crear tablas
# Verificar conexión a la base de datos y crear tablas
def init_db():
    try:
        # Primero verificar la conexión
        if not verify_db_connection():
            print("❌ No se pudo verificar la conexión a la base de datos")
            return False
        
        # Si la conexión es exitosa, crear las tablas
        Base.metadata.create_all(bind=engine)
        print("✅ Base de datos inicializada correctamente")
        print("✅ Tablas creadas/verificadas correctamente")
        return True
        
    except Exception as e:
        print(f"❌ Error al inicializar la base de datos: {str(e)}")
        return False

# Inicializar base de datos
print("🔄 Iniciando configuración de la base de datos...")
if not init_db():
    raise Exception("Error en la inicialización de la base de datos")
print("✅ Configuración de base de datos completada")


# Modelos Pydantic
class PatientCreate(BaseModel):
    name: str
    email: Optional[str] = None
    phone: Optional[str] = None


class AppointmentCreate(BaseModel):
    patient_id: int
    date: str
    service_type: str
    status: str = "scheduled"

class LeadCreate(BaseModel):
    name: str
    email: str
    phone: str
    status: str = "nuevo"

class AppointmentUpdate(BaseModel):
    status: str

app = FastAPI(
    title=settings.APP_NAME,
    description="Sistema CRM para gestión dental",
    version=settings.APP_VERSION,
)

# Montar archivos estáticos
app.mount("/static", StaticFiles(directory="app/static"), name="static")

# Configurar templates
templates = Jinja2Templates(directory="app/templates")

# Configurar CORS
allowed_origins = os.getenv("ALLOWED_ORIGINS", "*").split(",")
app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Rutas de páginas
@app.get("/")
async def home(request: Request, db: Session = Depends(get_db)):
    """Ruta principal que muestra el dashboard"""
    # Estadísticas
    total_patients = db.query(func.count(Patient.id)).scalar() or 0
    
    # Citas de hoy
    today_start = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
    today_end = today_start + timedelta(days=1)
    appointments_today = db.query(func.count(Appointment.id))\
        .filter(Appointment.date.between(today_start, today_end))\
        .scalar() or 0
    
    # Citas pendientes y completadas
    pending_appointments = db.query(func.count(Appointment.id))\
        .filter(Appointment.status == 'scheduled')\
        .scalar() or 0
    
    completed_appointments = db.query(func.count(Appointment.id))\
        .filter(Appointment.status == 'completed')\
        .scalar() or 0

    # Próximas citas
    upcoming_appointments = db.query(Appointment)\
        .filter(Appointment.date >= datetime.now())\
        .filter(Appointment.status == 'scheduled')\
        .order_by(Appointment.date)\
        .limit(5)\
        .all()

    # Últimos pacientes
    recent_patients = db.query(Patient)\
        .order_by(Patient.created_at.desc())\
        .limit(5)\
        .all()

    # Leads activos
    active_leads = db.query(func.count(Lead.id))\
        .filter(Lead.status.in_(['nuevo', 'contactado']))\
        .scalar() or 0

    return templates.TemplateResponse(
        "dashboard.html",
        {
            "request": request,
            "user": {"name": "ElBenerDev", "role": "Admin"},
            "active": "dashboard",
            "stats": {
                "total_patients": total_patients,
                "appointments_today": appointments_today,
                "pending_appointments": pending_appointments,
                "completed_appointments": completed_appointments,
                "active_leads": active_leads
            },
            "upcoming_appointments": upcoming_appointments,
            "recent_patients": recent_patients
        }
    )

@app.get("/patients")
async def patients_page(request: Request, db: Session = Depends(get_db)):
    """Ruta para la página de pacientes"""
    patients = db.query(Patient).order_by(Patient.created_at.desc()).all()
    return templates.TemplateResponse(
        "patients.html",
        {
            "request": request,
            "user": {"name": "ElBenerDev", "role": "Admin"},
            "active": "patients",
            "patients": patients
        }
    )

@app.get("/appointments")
async def appointments_page(request: Request, db: Session = Depends(get_db)):
    """Ruta para la página de citas"""
    appointments = db.query(Appointment)\
        .order_by(Appointment.date.desc())\
        .all()
    patients = db.query(Patient).order_by(Patient.name).all()

    return templates.TemplateResponse(
        "appointments.html",
        {
            "request": request,
            "user": {"name": "ElBenerDev", "role": "Admin"},
            "active": "appointments",
            "appointments": appointments,
            "patients": patients,
            "datetime": datetime
        }
    )

@app.get("/leads")
async def leads_page(request: Request, db: Session = Depends(get_db)):
    """Ruta para la página de leads"""
    leads = db.query(Lead).order_by(Lead.created_at.desc()).all()
    return templates.TemplateResponse(
        "leads.html",
        {
            "request": request,
            "user": {"name": "ElBenerDev", "role": "Admin"},
            "active": "leads",
            "leads": leads
        }
    )

@app.get("/settings")
async def settings_page(request: Request):
    """Ruta para la página de configuración"""
    return templates.TemplateResponse(
        "settings.html",
        {
            "request": request,
            "user": {"name": "ElBenerDev", "role": "Admin"},
            "active": "settings"
        }
    )

# API Endpoints para Pacientes
@app.post("/api/patients/")
async def create_patient(patient: PatientCreate, db: Session = Depends(get_db)):
    new_patient = Patient(**patient.dict())
    db.add(new_patient)
    db.commit()
    db.refresh(new_patient)
    return new_patient

@app.get("/api/patients/{patient_id}")
async def get_patient(patient_id: int, db: Session = Depends(get_db)):
    patient = db.query(Patient).filter(Patient.id == patient_id).first()
    if not patient:
        raise HTTPException(status_code=404, detail="Paciente no encontrado")
    return patient

@app.delete("/api/patients/{patient_id}")
async def delete_patient(patient_id: int, db: Session = Depends(get_db)):
    patient = db.query(Patient).filter(Patient.id == patient_id).first()
    if not patient:
        raise HTTPException(status_code=404, detail="Paciente no encontrado")
    db.delete(patient)
    db.commit()
    return {"status": "success"}

# API Endpoints para Citas
@app.post("/api/appointments/")
async def create_appointment(appointment: AppointmentCreate, db: Session = Depends(get_db)):
    new_appointment = Appointment(
        patient_id=appointment.patient_id,
        date=datetime.strptime(appointment.date, "%Y-%m-%dT%H:%M"),
        service_type=appointment.service_type,
        status=appointment.status
    )
    db.add(new_appointment)
    db.commit()
    db.refresh(new_appointment)
    return new_appointment

@app.put("/api/appointments/{appointment_id}/cancel")
async def cancel_appointment(appointment_id: int, db: Session = Depends(get_db)):
    appointment = db.query(Appointment).filter(Appointment.id == appointment_id).first()
    if not appointment:
        raise HTTPException(status_code=404, detail="Cita no encontrada")
    appointment.status = "cancelled"
    db.commit()
    return {"status": "success"}

# API Endpoints para Leads
@app.post("/api/leads/")
async def create_lead(lead: LeadCreate, db: Session = Depends(get_db)):
    new_lead = Lead(**lead.dict())
    db.add(new_lead)
    db.commit()
    db.refresh(new_lead)
    return new_lead

@app.get("/api/leads/{lead_id}")
async def get_lead(lead_id: int, db: Session = Depends(get_db)):
    lead = db.query(Lead).filter(Lead.id == lead_id).first()
    if not lead:
        raise HTTPException(status_code=404, detail="Lead no encontrado")
    return lead

@app.put("/api/leads/{lead_id}")
async def update_lead(lead_id: int, lead_data: LeadCreate, db: Session = Depends(get_db)):
    lead = db.query(Lead).filter(Lead.id == lead_id).first()
    if not lead:
        raise HTTPException(status_code=404, detail="Lead no encontrado")
    for key, value in lead_data.dict().items():
        setattr(lead, key, value)
    db.commit()
    db.refresh(lead)
    return lead

@app.delete("/api/leads/{lead_id}")
async def delete_lead(lead_id: int, db: Session = Depends(get_db)):
    lead = db.query(Lead).filter(Lead.id == lead_id).first()
    if not lead:
        raise HTTPException(status_code=404, detail="Lead no encontrado")
    db.delete(lead)
    db.commit()
    return {"status": "success"}

# API Endpoint para respaldo del sistema
@app.post("/api/settings/backup")
async def create_backup():
    # Aquí iría la lógica para crear el respaldo
    return {"status": "success", "message": "Respaldo iniciado correctamente"}

if __name__ == "__main__":
    port = int(os.getenv("PORT", 8000))
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=port, reload=True)