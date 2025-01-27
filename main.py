# Imports estándar de Python
from datetime import datetime, timedelta, timezone
import os
import time
from typing import Optional, Dict, List  # Agregado para type hints

# Imports de FastAPI y Starlette
from fastapi import (
    FastAPI,
    Request,
    Depends,
    HTTPException,
    status,
    Response,
    Cookie,
)
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import (
    PlainTextResponse,
    JSONResponse,
    HTMLResponse,
    RedirectResponse,
)
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from starlette.middleware.base import BaseHTTPMiddleware

# Imports de SQLAlchemy
from sqlalchemy import func, desc, and_, or_
from sqlalchemy.orm import Session, joinedload
from sqlalchemy.exc import SQLAlchemyError

# Imports locales - Configuración y utilidades
from config.settings import settings
from app.utils.db import (
    get_db,
    engine,
    Base,
    verify_db_connection,
    reset_db,
    SessionLocal,
)

# Imports locales - Modelos
from app.models.models import (
    Patient,
    Appointment,
    Lead,
    User,
)

# Imports locales - Schemas
from app.schemas.schemas import (
    PatientCreate,
    PatientResponse,
    AppointmentCreate,
    AppointmentResponse,
    LeadCreate,
    LeadResponse,
    AppointmentUpdate,
    Token,
)

# Imports locales - Autenticación
from app.auth.utils import (
    oauth2_scheme,
    get_current_user,
    get_current_active_user,
    create_access_token,
    verify_token,
)
from app.auth.router import router as auth_router
from app.middleware.auth import AuthMiddleware

# Configuración de plantillas
templates = Jinja2Templates(directory="app/templates")

class AuthMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        # No requerir autenticación para rutas de auth y static
        if request.url.path.startswith("/auth/") or request.url.path.startswith("/static/"):
            return await call_next(request)

        try:
            # Obtener token
            token = await oauth2_scheme(request)
            if not token:
                return RedirectResponse(url="/auth/login", status_code=302)
        except HTTPException:
            return RedirectResponse(url="/auth/login", status_code=302)

        response = await call_next(request)
        return response



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


app.include_router(auth_router)
app.add_middleware(AuthMiddleware)

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
        
        # Usar reset_db para una inicialización limpia
        if not reset_db():
            raise Exception("Error al reinicializar la base de datos")
            
        print("✅ Base de datos inicializada correctamente")
        return True
    except Exception as e:
        print(f"❌ Error al inicializar la base de datos: {str(e)}")
        return False

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
async def home(
    request: Request, 
    db: Session = Depends(get_db)
):
    try:
        # Obtener token de las cookies
        token = request.cookies.get("access_token")
        if not token:
            return RedirectResponse(url="/auth/login", status_code=302)
            
        # Limpiar el prefijo "Bearer " si existe
        if token.startswith("Bearer "):
            token = token.split(" ")[1]
            
        try:
            # Verificar el token y obtener el usuario
            current_user = await get_current_user(db=db, token=token)
            if not current_user:
                return RedirectResponse(url="/auth/login", status_code=302)
        except:
            return RedirectResponse(url="/auth/login", status_code=302)

        # Definir los diccionarios de nombres
        service_names = {
            'cleaning': 'Limpieza',
            'consultation': 'Consulta',
            'treatment': 'Tratamiento',
            'emergency': 'Emergencia',
        }

        status_names = {
            'scheduled': 'Programada',
            'completed': 'Completada',
            'cancelled': 'Cancelada',
        }

        # Estadísticas
        total_patients = db.query(func.count(Patient.id)).scalar() or 0
        
        # Citas de hoy
        today_start = datetime.now(timezone.utc).replace(hour=0, minute=0, second=0, microsecond=0)
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
            .filter(Appointment.date >= datetime.now(timezone.utc))\
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
                "current_user": current_user,
                "user": {
                    "name": current_user.name,
                    "role": "Admin",
                    "email": current_user.email
                },
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

    except HTTPException as he:
        print(f"❌ Error de HTTP en home: {str(he)}")
        return RedirectResponse(url="/auth/login", status_code=302)

    except Exception as e:
        print(f"❌ Error en home: {str(e)}")
        return templates.TemplateResponse(
            "error.html",
            {
                "request": request,
                "error_message": f"Error al cargar el dashboard: {str(e)}",
                "user": {
                    "name": "Usuario",
                    "role": "Admin",
                    "email": ""
                }
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
        
        print(f"✅ Paciente creado: {new_patient.name}")
        return new_patient
        
    except Exception as e:
        db.rollback()
        print(f"❌ Error al crear paciente: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

# Agrega la ruta para la vista de pacientes
@app.get("/patients", response_class=HTMLResponse)
@app.head("/patients")
async def patients_page(
    request: Request, 
    db: Session = Depends(get_db),
    token: str = Depends(oauth2_scheme)
):
    try:
        # Obtener usuario actual
        current_user = get_current_user(db, token)
        if not current_user:
            return RedirectResponse(url="/auth/login", status_code=status.HTTP_302_FOUND)

        patients = db.query(Patient).order_by(Patient.created_at.desc()).all()
        
        return templates.TemplateResponse(
            "patients.html",
            {
                "request": request,
                "current_user": current_user,  # Usar current_user en lugar de user fijo
                "user": {
                    "name": current_user.name,
                    "role": "Admin",
                    "email": current_user.email
                },
                "active": "patients",
                "patients": patients
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
    
@app.post("/api/appointments/", response_model=AppointmentResponse)
async def create_appointment(
    appointment: AppointmentCreate,
    db: Session = Depends(get_db)
):
    try:
        print(f"📝 Recibiendo datos de cita: {appointment.dict()}")
        
        # Verificar que el paciente existe
        patient = db.query(Patient).filter(Patient.id == appointment.patient_id).first()
        if not patient:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"No se encontró el paciente con ID {appointment.patient_id}"
            )

        # Crear la cita
        new_appointment = Appointment(
            patient_id=appointment.patient_id,
            date=datetime.fromisoformat(appointment.date.replace('Z', '+00:00')),
            service_type=appointment.service_type,
            status=appointment.status,
            notes=appointment.notes,
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc)
        )
        
        print(f"📅 Creando cita para paciente {patient.name}")
        db.add(new_appointment)
        db.commit()
        db.refresh(new_appointment)
        
        # Crear respuesta con el nombre del paciente
        response_data = {
            "id": new_appointment.id,
            "patient_id": new_appointment.patient_id,
            "patient_name": patient.name,  # Agregar el nombre del paciente
            "date": new_appointment.date,
            "service_type": new_appointment.service_type,
            "status": new_appointment.status,
            "notes": new_appointment.notes,
            "created_at": new_appointment.created_at,
            "updated_at": new_appointment.updated_at
        }
        
        print(f"✅ Cita creada exitosamente para {patient.name}")
        return response_data
        
    except ValueError as e:
        db.rollback()
        print(f"❌ Error de validación: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(e)
        )
    except HTTPException as e:
        db.rollback()
        print(f"❌ Error HTTP: {str(e.detail)}")
        raise e
    except Exception as e:
        db.rollback()
        print(f"❌ Error inesperado: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@app.post("/api/leads/", response_model=LeadResponse)
async def create_lead(
    lead: LeadCreate,
    db: Session = Depends(get_db)
):
    try:
        new_lead = Lead(
            name=lead.name,
            email=lead.email,
            phone=lead.phone,
            status=lead.status,
            notes=lead.notes,
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc)
        )
        
        db.add(new_lead)
        db.commit()
        db.refresh(new_lead)
        
        print(f"✅ Lead creado: {new_lead.name}")
        return new_lead
        
    except Exception as e:
        db.rollback()
        print(f"❌ Error al crear lead: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
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