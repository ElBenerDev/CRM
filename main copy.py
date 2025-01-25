from fastapi import FastAPI, Request, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import PlainTextResponse, JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from datetime import datetime, timedelta
import os
import time
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.utils.db import get_db, engine, Base, verify_db_connection
from app.models.models import Patient, Appointment, Lead
from app.schemas.schemas import (
    PatientCreate, PatientResponse,
    AppointmentCreate, AppointmentResponse,
    LeadCreate, LeadResponse,
    AppointmentUpdate
)
from config.settings import settings

# Configuración de rutas
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
STATIC_DIR = os.path.join(BASE_DIR, "app", "static")
TEMPLATES_DIR = os.path.join(BASE_DIR, "app", "templates")

# Verificar y crear directorios si no existen
os.makedirs(os.path.join(STATIC_DIR, "js"), exist_ok=True)
os.makedirs(os.path.join(STATIC_DIR, "css"), exist_ok=True)
os.makedirs(os.path.join(STATIC_DIR, "img"), exist_ok=True)

print(f"📁 Directorio base: {BASE_DIR}")
print(f"📁 Directorio estático: {STATIC_DIR}")
print(f"📁 Directorio templates: {TEMPLATES_DIR}")

# Verificar conexión a la base de datos y crear tablas
def init_db():
    try:
        if not verify_db_connection():
            raise Exception("No se pudo establecer conexión con la base de datos")
        Base.metadata.create_all(bind=engine)
        print("✅ Base de datos inicializada correctamente")
        return True
    except Exception as e:
        print(f"❌ Error al inicializar la base de datos: {str(e)}")
        return False

# Inicializar base de datos
print("🔄 Iniciando configuración de la base de datos...")
if not init_db():
    raise Exception("Error en la inicialización de la base de datos")

# Middleware para logging
class LoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):
        start_time = time.time()
        
        # Log request
        print(f"\n🔄 Request: {request.method} {request.url}")
        if request.method in ["POST", "PUT"]:
            try:
                body = await request.body()
                if body:
                    print(f"📝 Request Body: {body.decode()}")
            except Exception as e:
                print(f"❌ Error reading request body: {str(e)}")

        response = await call_next(request)
        
        # Log response
        process_time = time.time() - start_time
        print(f"✅ Response: Status {response.status_code} in {process_time:.2f}s")
        
        return response

# Crear aplicación FastAPI
app = FastAPI(
    title=settings.APP_NAME,
    description="Sistema CRM para gestión dental",
    version=settings.APP_VERSION,
)

# Configurar middleware
app.add_middleware(LoggingMiddleware)

# Configurar CORS
allowed_origins = os.getenv("ALLOWED_ORIGINS", "*").split(",")
app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Montar archivos estáticos
try:
    app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")
    print("✅ Archivos estáticos montados correctamente")
except Exception as e:
    print(f"❌ Error al montar archivos estáticos: {str(e)}")
    print(f"📁 Verificando contenido de {STATIC_DIR}:")
    for root, dirs, files in os.walk(STATIC_DIR):
        print(f"  📂 {root}")
        for d in dirs:
            print(f"    📁 {d}")
        for f in files:
            print(f"    📄 {f}")

# Configurar templates
templates = Jinja2Templates(directory=TEMPLATES_DIR)

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
    try:
        # Verificar si el template existe
        template_path = os.path.join(TEMPLATES_DIR, "patients.html")
        if not os.path.exists(template_path):
            print(f"❌ Template no encontrado: {template_path}")
            raise HTTPException(status_code=500, detail="Template no encontrado")

        patients = db.query(Patient).order_by(Patient.created_at.desc()).all()
        print(f"✅ Pacientes encontrados: {len(patients)}")
        
        return templates.TemplateResponse(
            "patients.html",
            {
                "request": request,
                "user": {"name": "ElBenerDev", "role": "Admin"},
                "active": "patients",
                "patients": patients,
                "datetime": datetime
            }
        )
    except Exception as e:
        print(f"❌ Error en patients_page: {str(e)}")
        return templates.TemplateResponse(
            "error.html",
            {
                "request": request,
                "error_message": f"Error al cargar la página de pacientes: {str(e)}",
                "user": {"name": "ElBenerDev", "role": "Admin"},
                "active": "patients"
            },
            status_code=500
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
@app.post("/api/patients/", response_model=PatientResponse, status_code=status.HTTP_201_CREATED)
async def create_patient(patient: PatientCreate, db: Session = Depends(get_db)):
    """Crear un nuevo paciente"""
    try:
        # Crear instancia del modelo Patient
        new_patient = Patient(
            name=patient.name,
            email=patient.email,
            phone=patient.phone,
            address=patient.address,
            notes=patient.notes,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        
        # Guardar en la base de datos
        db.add(new_patient)
        db.commit()
        db.refresh(new_patient)
        
        print(f"✅ Paciente creado: {new_patient.name}")
        return new_patient
        
    except Exception as e:
        db.rollback()
        print(f"❌ Error al crear paciente: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al crear el paciente: {str(e)}"
        )

@app.get("/api/patients/", response_model=List[PatientResponse])
async def get_patients(db: Session = Depends(get_db)):
    """Obtener todos los pacientes"""
    try:
        patients = db.query(Patient).order_by(Patient.created_at.desc()).all()
        return patients
    except Exception as e:
        print(f"❌ Error al obtener pacientes: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al obtener pacientes: {str(e)}"
        )

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
    try:
        # Verificar si el paciente existe
        patient = db.query(Patient).filter(Patient.id == appointment.patient_id).first()
        if not patient:
            raise HTTPException(status_code=404, detail="Paciente no encontrado")

        # Convertir la fecha
        appointment_date = datetime.strptime(appointment.date, "%Y-%m-%dT%H:%M")

        # Crear la cita
        new_appointment = Appointment(
            patient_id=appointment.patient_id,
            date=appointment_date,
            service_type=appointment.service_type,
            status="scheduled"
        )
        
        db.add(new_appointment)
        db.commit()
        db.refresh(new_appointment)
        
        return JSONResponse(
            status_code=201,
            content={
                "id": new_appointment.id,
                "patient_id": new_appointment.patient_id,
                "date": new_appointment.date.isoformat(),
                "service_type": new_appointment.service_type,
                "status": new_appointment.status
            }
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail="Formato de fecha inválido")
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))

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

# Manejador de errores 404
@app.exception_handler(404)
async def not_found_error(request: Request, exc: HTTPException):
    if request.url.path.startswith('/static/'):
        print(f"❌ Archivo estático no encontrado: {request.url.path}")
        return PlainTextResponse("File not found", status_code=404)
    return templates.TemplateResponse(
        "error.html",
        {
            "request": request,
            "error_message": "Página no encontrada",
            "user": {"name": "ElBenerDev", "role": "Admin"},
            "active": ""
        },
        status_code=404
    )


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    print(f"❌ Error Global: {str(exc)}")
    return JSONResponse(
        status_code=500,
        content={
            "detail": "Error interno del servidor",
            "error": str(exc)
        }
    )

@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    print(f"❌ HTTP Error: {exc.status_code} - {exc.detail}")
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail}
    )

@app.template_filter()
def format_date(date):
    if date is None:
        return datetime.now().strftime('%d/%m/%Y')
    return date.strftime('%d/%m/%Y')

templates = Jinja2Templates(directory=TEMPLATES_DIR)
templates.env.filters["format_date"] = format_date

if __name__ == "__main__":
    port = int(os.getenv("PORT", 8000))
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=port,
        reload=True,
        workers=4
    )