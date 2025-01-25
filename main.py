from fastapi import FastAPI, Request, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import PlainTextResponse, JSONResponse, HTMLResponse
from starlette.middleware.base import BaseHTTPMiddleware
from datetime import datetime, timedelta
from pydantic import ValidationError
from typing import List, Optional
from datetime import timezone
from typing import List
from datetime import datetime, timezone
from fastapi import FastAPI, Depends, HTTPException, status
from sqlalchemy.orm import Session
import os
import time

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
from fastapi import status
from sqlalchemy.orm import joinedload 

# Middleware de Debug - COLOCAR AQUÍ
class DebugMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        print(f"\n🔍 DEBUG - Request path: {request.url.path}")
        print(f"🔍 DEBUG - Templates dir: {TEMPLATES_DIR}")
        print(f"🔍 DEBUG - Template files: {os.listdir(TEMPLATES_DIR)}")
        
        try:
            response = await call_next(request)
            print(f"🔍 DEBUG - Response status: {response.status_code}")
            return response
        except Exception as e:
            print(f"❌ DEBUG - Error: {str(e)}")
            raise e

# Crear una única instancia de FastAPI
app = FastAPI(
    title=settings.APP_NAME,
    description="Sistema CRM para gestión dental",
    version=settings.APP_VERSION,
)

# Agregar los middlewares en orden
app.add_middleware(DebugMiddleware)  # Primero el Debug
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS", "HEAD", "PATCH"],
    allow_headers=["*"],
    expose_headers=["*"],
    max_age=3600,
)


# Configuración de rutas
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
STATIC_DIR = os.path.join(BASE_DIR, "app", "static")
TEMPLATES_DIR = os.path.join(BASE_DIR, "app", "templates")

# Verificar y crear directorios si no existen
for dir_name in ["js", "css", "img"]:
    os.makedirs(os.path.join(STATIC_DIR, dir_name), exist_ok=True)

print(f"📁 Directorio base: {BASE_DIR}")
print(f"📁 Directorio estático: {STATIC_DIR}")
print(f"📁 Directorio templates: {TEMPLATES_DIR}")

# Middleware para logging mejorado
class LoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        start_time = time.time()
        
        # Log request
        print(f"\n🔄 Request: {request.method} {request.url}")
        
        try:
            response = await call_next(request)
            process_time = time.time() - start_time
            print(f"✅ Response: Status {response.status_code} in {process_time:.2f}s")
            
            # Agregar headers de rendimiento
            response.headers["X-Process-Time"] = f"{process_time:.4f}"
            return response
            
        except Exception as e:
            process_time = time.time() - start_time
            print(f"❌ Error: {str(e)} in {process_time:.2f}s")
            return JSONResponse(
                status_code=500,
                content={
                    "detail": "Internal Server Error",
                    "message": str(e)
                }
            )

# Inicializar base de datos
print("🔄 Iniciando configuración de la base de datos...")
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

if not init_db():
    raise Exception("Error en la inicialización de la base de datos")

# Configurar middleware
app.add_middleware(LoggingMiddleware)

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

# Función para formatear fechas
def format_date(date):
    if date is None:
        return datetime.utcnow().strftime('%d/%m/%Y')
    return date.strftime('%d/%m/%Y')

# Configurar templates y filtros
templates = Jinja2Templates(directory=TEMPLATES_DIR)
templates.env.filters["format_date"] = format_date

# Rutas de páginas con soporte mejorado para HEAD
@app.get("/", response_class=HTMLResponse)
@app.head("/")
async def home(request: Request, db: Session = Depends(get_db)):
    """Ruta principal que muestra el dashboard"""
    try:
        if request.method == "HEAD":
            return HTMLResponse(content="")

        # Definir los diccionarios de nombres
        service_names = {
            'cleaning': 'Limpieza',
            'consultation': 'Consulta',
            'treatment': 'Tratamiento',
            'emergency': 'Emergencia',
            # Agrega más servicios según necesites
        }

        status_names = {
            'scheduled': 'Programada',
            'completed': 'Completada',
            'cancelled': 'Cancelada',
            # Agrega más estados según necesites
        }

        # Estadísticas
        total_patients = db.query(func.count(Patient.id)).scalar() or 0
        
        # Citas de hoy
        today_start = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
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

        # Próximas citas con información del paciente
        upcoming_appointments = db.query(Appointment)\
            .join(Patient)\
            .filter(Appointment.date >= datetime.utcnow())\
            .filter(Appointment.status == 'scheduled')\
            .order_by(Appointment.date)\
            .limit(5)\
            .all()

        # Últimos pacientes con sus citas
        recent_patients = db.query(Patient)\
            .options(joinedload(Patient.appointments))\
            .order_by(Patient.created_at.desc())\
            .limit(5)\
            .all()

        return templates.TemplateResponse(
            "dashboard.html",
            {
                "request": request,
                "user": {"name": "ElBenerDev", "role": "Admin"},
                "stats": {
                    "total_patients": total_patients,
                    "appointments_today": appointments_today,
                    "pending_appointments": pending_appointments,
                    "completed_appointments": completed_appointments,
                },
                "upcoming_appointments": upcoming_appointments,
                "recent_patients": recent_patients,
                "service_names": service_names,
                "status_names": status_names
            }
        )

    except Exception as e:
        print(f"❌ Error en home: {str(e)}")
        return templates.TemplateResponse(
            "error.html",
            {
                "request": request,
                "error_message": f"Error al cargar el dashboard: {str(e)}",
                "user": {"name": "ElBenerDev", "role": "Admin"},
            },
            status_code=500
        )
@app.post("/api/patients/", response_model=PatientResponse)
async def create_patient(patient: PatientCreate, db: Session = Depends(get_db)):
    try:
        new_patient = Patient(
            name=patient.name,
            email=patient.email,
            phone=patient.phone,
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc)
        )
        
        db.add(new_patient)
        db.commit()
        db.refresh(new_patient)
        
        return new_patient
        
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )
    
@app.post("/api/patients/", response_model=PatientResponse)
async def create_patient(patient: PatientCreate, db: Session = Depends(get_db)):
    try:
        # Crear nuevo paciente sin especificar ID
        new_patient = Patient(
            name=patient.name,
            email=patient.email,
            phone=patient.phone,
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc)
        )
        
        db.add(new_patient)
        db.commit()
        db.refresh(new_patient)
        
        return new_patient
        
    except Exception as e:
        db.rollback()
        print(f"❌ Error al crear paciente: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
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
            detail=str(e)
        )
@app.get("/appointments", response_class=HTMLResponse)
@app.head("/appointments")
async def appointments_page(request: Request, db: Session = Depends(get_db)):
    """Ruta para la página de citas"""
    if request.method == "HEAD":
        return HTMLResponse(content="")
        
    try:
        print(f"🔍 Intentando cargar appointments_page")
        appointments = db.query(Appointment)\
            .order_by(Appointment.date.desc())\
            .all()
        patients = db.query(Patient).order_by(Patient.name).all()
        print(f"✅ Citas encontradas: {len(appointments)}")

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
    except Exception as e:
        print(f"❌ Error en appointments_page: {str(e)}")
        return templates.TemplateResponse(
            "error.html",
            {
                "request": request,
                "error_message": f"Error al cargar la página de citas: {str(e)}",
                "user": {"name": "ElBenerDev", "role": "Admin"},
                "active": "appointments"
            },
            status_code=500
        )

@app.get("/leads", response_class=HTMLResponse)
@app.head("/leads")
async def leads_page(request: Request, db: Session = Depends(get_db)):
    """Ruta para la página de leads"""
    if request.method == "HEAD":
        return HTMLResponse(content="")
        
    try:
        print(f"🔍 Intentando cargar leads_page")
        leads = db.query(Lead).order_by(Lead.created_at.desc()).all()
        print(f"✅ Leads encontrados: {len(leads)}")
        
        return templates.TemplateResponse(
            "leads.html",
            {
                "request": request,
                "user": {"name": "ElBenerDev", "role": "Admin"},
                "active": "leads",
                "leads": leads
            }
        )
    except Exception as e:
        print(f"❌ Error en leads_page: {str(e)}")
        return templates.TemplateResponse(
            "error.html",
            {
                "request": request,
                "error_message": f"Error al cargar la página de leads: {str(e)}",
                "user": {"name": "ElBenerDev", "role": "Admin"},
                "active": "leads"
            },
            status_code=500
        )

@app.get("/settings", response_class=HTMLResponse)
@app.head("/settings")
async def settings_page(request: Request):
    """Ruta para la página de configuración"""
    if request.method == "HEAD":
        return HTMLResponse(content="")
        
    try:
        return templates.TemplateResponse(
            "settings.html",
            {
                "request": request,
                "user": {"name": "ElBenerDev", "role": "Admin"},
                "active": "settings"
            }
        )
    except Exception as e:
        print(f"❌ Error en settings_page: {str(e)}")
        return templates.TemplateResponse(
            "error.html",
            {
                "request": request,
                "error_message": f"Error al cargar la página de configuración: {str(e)}",
                "user": {"name": "ElBenerDev", "role": "Admin"},
                "active": "settings"
            },
            status_code=500
        )

# Configuración de inicio
if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=port,
        reload=settings.DEBUG,
        workers=4,
        log_level="info"
    )