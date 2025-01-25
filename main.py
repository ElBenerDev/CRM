from fastapi import FastAPI, Request, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import PlainTextResponse, JSONResponse, HTMLResponse
from starlette.middleware.base import BaseHTTPMiddleware
from datetime import datetime, timedelta
from typing import List, Optional
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
from fastapi import status

# Crear una única instancia de FastAPI
app = FastAPI(
    title=settings.APP_NAME,
    description="Sistema CRM para gestión dental",
    version=settings.APP_VERSION,
)

# Configuración CORS mejorada
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # En producción, especifica los dominios exactos
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
async def home(request: Request, db: Session = Depends(get_db)):
    """Ruta principal que muestra el dashboard"""
    if request.method == "HEAD":
        return HTMLResponse(content="")
    
    try:
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

        # Próximas citas
        upcoming_appointments = db.query(Appointment)\
            .filter(Appointment.date >= datetime.utcnow())\
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
    except Exception as e:
        print(f"❌ Error en home: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="Error al cargar el dashboard"
        )

# Endpoint de verificación de salud del sistema
@app.get("/health")
async def health_check():
    """Endpoint para verificar el estado del sistema"""
    try:
        # Verificar conexión a la base de datos
        if not verify_db_connection():
            raise HTTPException(
                status_code=503,
                detail="Database connection failed"
            )
        
        return {
            "status": "healthy",
            "timestamp": datetime.utcnow().isoformat(),
            "version": settings.APP_VERSION,
            "database": "connected"
        }
    except Exception as e:
        raise HTTPException(
            status_code=503,
            detail=f"System unhealthy: {str(e)}"
        )

# API Endpoints para Pacientes con mejor manejo de errores
@app.post("/api/patients/", response_model=PatientResponse, status_code=status.HTTP_201_CREATED)
async def create_patient(patient: PatientCreate, db: Session = Depends(get_db)):
    """Crear un nuevo paciente"""
    try:
        new_patient = Patient(**patient.dict())
        new_patient.created_at = datetime.utcnow()
        new_patient.updated_at = datetime.utcnow()
        db.add(new_patient)
        db.commit()
        db.refresh(new_patient)
        return new_patient
    except Exception as e:
        db.rollback()
        print(f"❌ Error al crear paciente: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error al crear el paciente: {str(e)}"
        )

# Manejadores de errores mejorados
@app.exception_handler(404)
async def not_found_error(request: Request, exc: HTTPException):
    """Manejador personalizado para errores 404"""
    if request.url.path.startswith('/static/'):
        print(f"❌ Archivo estático no encontrado: {request.url.path}")
        return PlainTextResponse("File not found", status_code=404)
    
    return templates.TemplateResponse(
        "error.html",
        {
            "request": request,
            "error_message": "Página no encontrada",
            "user": {"name": "ElBenerDev", "role": "Admin"},
            "active": "",
            "status_code": 404
        },
        status_code=404
    )

@app.exception_handler(405)
async def method_not_allowed_handler(request: Request, exc: HTTPException):
    """Manejador personalizado para errores 405"""
    print(f"⚠️ Método no permitido: {request.method} {request.url}")
    return JSONResponse(
        status_code=405,
        content={
            "detail": f"Método {request.method} no permitido para esta ruta",
            "allowed_methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS", "HEAD"],
            "timestamp": datetime.utcnow().isoformat()
        }
    )

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Manejador global de excepciones"""
    print(f"❌ Error Global: {str(exc)}")
    return JSONResponse(
        status_code=500,
        content={
            "detail": "Error interno del servidor",
            "error": str(exc),
            "path": str(request.url),
            "method": request.method,
            "timestamp": datetime.utcnow().isoformat()
        }
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