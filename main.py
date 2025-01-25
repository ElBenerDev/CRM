from fastapi import FastAPI, Request, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import PlainTextResponse, JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from datetime import datetime, timedelta
from typing import List
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
from config.settings import settings  # Solo importar desde config.settings
from fastapi import APIRouter, Depends, HTTPException, status
from typing import Optional
from pydantic import validator
from app.schemas.schemas import AppointmentCreate, AppointmentResponse
from app.models.models import Appointment, Patient

# Crear una única instancia de FastAPI
app = FastAPI(
    title=settings.APP_NAME,
    description="Sistema CRM para gestión dental",
    version=settings.APP_VERSION,
)

# Un solo middleware CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # En producción, especifica los dominios exactos
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],  # Especificar todos los métodos
    allow_headers=["*"],
    expose_headers=["*"],
    max_age=600,  # Tiempo de cache para preflight requests
)


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
    allow_origins=["*"],
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

# Función para formatear fechas
def format_date(date):
    if date is None:
        return datetime.utcnow().strftime('%d/%m/%Y')
    return date.strftime('%d/%m/%Y')

# Configurar templates y filtros
templates = Jinja2Templates(directory=TEMPLATES_DIR)
templates.env.filters["format_date"] = format_date

# Rutas de páginas
@app.get("/")
async def home(request: Request, db: Session = Depends(get_db)):
    """Ruta principal que muestra el dashboard"""
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

@app.get("/patients")
async def patients_page(request: Request, db: Session = Depends(get_db)):
    """Ruta para la página de pacientes"""
    try:
        patients = db.query(Patient).order_by(Patient.created_at.desc()).all()
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
        raise HTTPException(status_code=500, detail="Error al cargar la página de pacientes")

@app.get("/appointments")
async def appointments_page(request: Request, db: Session = Depends(get_db)):
    """Ruta para la página de citas"""
    try:
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
    except Exception as e:
        print(f"❌ Error en appointments_page: {str(e)}")
        raise HTTPException(status_code=500, detail="Error al cargar la página de citas")

@app.get("/leads")
async def leads_page(request: Request, db: Session = Depends(get_db)):
    """Ruta para la página de leads"""
    try:
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
    except Exception as e:
        print(f"❌ Error en leads_page: {str(e)}")
        raise HTTPException(status_code=500, detail="Error al cargar la página de leads")

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
    try:
        new_patient = Patient(**patient.dict())
        new_patient.created_at = datetime.utcnow()  # Asegurar que created_at tenga un valor
        db.add(new_patient)
        db.commit()
        db.refresh(new_patient)
        return new_patient
    except Exception as e:
        db.rollback()
        print(f"❌ Error al crear paciente: {str(e)}")
        raise HTTPException(status_code=500, detail="Error al crear el paciente")

@app.get("/api/patients/", response_model=List[PatientResponse])
async def get_patients(db: Session = Depends(get_db)):
    """Obtiene la lista de todos los pacientes"""
    try:
        patients = db.query(Patient).order_by(Patient.created_at.desc()).all()
        return patients
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error al obtener pacientes: {str(e)}"
        )

@app.delete("/api/patients/{patient_id}")
async def delete_patient(patient_id: int, db: Session = Depends(get_db)):
    try:
        patient = db.query(Patient).filter(Patient.id == patient_id).first()
        if not patient:
            raise HTTPException(status_code=404, detail="Paciente no encontrado")
        db.delete(patient)
        db.commit()
        return {"status": "success", "message": "Paciente eliminado correctamente"}
    except Exception as e:
        db.rollback()
        print(f"❌ Error al eliminar paciente: {str(e)}")
        raise HTTPException(status_code=500, detail="Error al eliminar el paciente")

# API Endpoints para Citas
@app.post("/api/appointments/", response_model=AppointmentResponse, status_code=status.HTTP_201_CREATED)
async def create_appointment(appointment: AppointmentCreate, db: Session = Depends(get_db)):
    """
    Crea una nueva cita médica.
    
    Args:
        appointment: Datos de la cita a crear
        db: Sesión de base de datos
    
    Returns:
        AppointmentResponse: Datos de la cita creada
    
    Raises:
        HTTPException: Si hay errores en la validación o creación
    """
    try:
        # 1. Validar que el paciente existe
        patient = db.query(Patient).filter(Patient.id == appointment.patient_id).first()
        if not patient:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Paciente no encontrado"
            )

        # 2. Validar y convertir la fecha
        try:
            appointment_date = datetime.strptime(appointment.date, "%Y-%m-%dT%H:%M")
            
            # Validar que la fecha no está en el pasado
            if appointment_date < datetime.utcnow():
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="La fecha de la cita no puede estar en el pasado"
                )
            
            # Validar que la fecha no está muy lejos en el futuro (ejemplo: 1 año)
            if appointment_date > datetime.utcnow() + timedelta(days=365):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="La fecha de la cita no puede estar a más de un año en el futuro"
                )
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Formato de fecha inválido. Use el formato: YYYY-MM-DDTHH:MM"
            )

        # 3. Verificar si ya existe una cita en el mismo horario
        existing_appointment = db.query(Appointment).filter(
            Appointment.date == appointment_date,
            Appointment.status == "scheduled"
        ).first()
        
        if existing_appointment:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Ya existe una cita programada para esta fecha y hora"
            )

        # 4. Crear la cita
        new_appointment = Appointment(
            patient_id=appointment.patient_id,
            date=appointment_date,
            service_type=appointment.service_type,
            status="scheduled",
            notes=appointment.notes if hasattr(appointment, 'notes') else None,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        
        db.add(new_appointment)
        db.commit()
        db.refresh(new_appointment)
        
        # 5. Retornar respuesta formateada
        return AppointmentResponse(
            id=new_appointment.id,
            patient_id=new_appointment.patient_id,
            patient_name=patient.name,  # Incluir nombre del paciente
            date=new_appointment.date.isoformat(),
            service_type=new_appointment.service_type,
            status=new_appointment.status,
            notes=new_appointment.notes,
            created_at=new_appointment.created_at,
            updated_at=new_appointment.updated_at
        )

    except HTTPException as he:
        raise he
    except Exception as e:
        db.rollback()
        print(f"❌ Error al crear cita: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al crear la cita: {str(e)}"
        )
    

@app.put("/api/appointments/{appointment_id}/cancel")
async def cancel_appointment(appointment_id: int, db: Session = Depends(get_db)):
    try:
        appointment = db.query(Appointment).filter(Appointment.id == appointment_id).first()
        if not appointment:
            raise HTTPException(status_code=404, detail="Cita no encontrada")
        appointment.status = "cancelled"
        appointment.updated_at = datetime.utcnow()
        db.commit()
        return {
            "status": "success",
            "message": "Cita cancelada correctamente",
            "appointment": {
                "id": appointment.id,
                "status": appointment.status,
                "updated_at": appointment.updated_at.isoformat()
            }
        }
    except Exception as e:
        db.rollback()
        print(f"❌ Error al cancelar cita: {str(e)}")
        raise HTTPException(status_code=500, detail="Error al cancelar la cita")

# API Endpoints para Leads
@app.post("/api/leads/")
async def create_lead(lead: LeadCreate, db: Session = Depends(get_db)):
    try:
        new_lead = Lead(**lead.dict())
        new_lead.created_at = datetime.utcnow()
        new_lead.updated_at = datetime.utcnow()
        db.add(new_lead)
        db.commit()
        db.refresh(new_lead)
        return new_lead
    except Exception as e:
        db.rollback()
        print(f"❌ Error al crear lead: {str(e)}")
        raise HTTPException(status_code=500, detail="Error al crear el lead")

@app.get("/api/leads/{lead_id}")
async def get_lead(lead_id: int, db: Session = Depends(get_db)):
    lead = db.query(Lead).filter(Lead.id == lead_id).first()
    if not lead:
        raise HTTPException(status_code=404, detail="Lead no encontrado")
    return lead

@app.put("/api/leads/{lead_id}")
async def update_lead(lead_id: int, lead_data: LeadCreate, db: Session = Depends(get_db)):
    try:
        lead = db.query(Lead).filter(Lead.id == lead_id).first()
        if not lead:
            raise HTTPException(status_code=404, detail="Lead no encontrado")
        
        for key, value in lead_data.dict().items():
            setattr(lead, key, value)
        
        lead.updated_at = datetime.utcnow()
        db.commit()
        db.refresh(lead)
        return lead
    except Exception as e:
        db.rollback()
        print(f"❌ Error al actualizar lead: {str(e)}")
        raise HTTPException(status_code=500, detail="Error al actualizar el lead")

@app.delete("/api/leads/{lead_id}")
async def delete_lead(lead_id: int, db: Session = Depends(get_db)):
    try:
        lead = db.query(Lead).filter(Lead.id == lead_id).first()
        if not lead:
            raise HTTPException(status_code=404, detail="Lead no encontrado")
        db.delete(lead)
        db.commit()
        return {"status": "success", "message": "Lead eliminado correctamente"}
    except Exception as e:
        db.rollback()
        print(f"❌ Error al eliminar lead: {str(e)}")
        raise HTTPException(status_code=500, detail="Error al eliminar el lead")

# API Endpoint para respaldo del sistema
@app.post("/api/settings/backup")
async def create_backup():
    try:
        # Aquí iría la lógica para crear el respaldo
        current_time = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
        return {
            "status": "success",
            "message": "Respaldo iniciado correctamente",
            "backup_time": current_time
        }
    except Exception as e:
        print(f"❌ Error al crear respaldo: {str(e)}")
        raise HTTPException(status_code=500, detail="Error al crear el respaldo")

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
            "error": str(exc),
            "timestamp": datetime.utcnow().isoformat()
        }
    )

@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    print(f"❌ HTTP Error: {exc.status_code} - {exc.detail}")
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "detail": exc.detail,
            "timestamp": datetime.utcnow().isoformat()
        }
    )




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