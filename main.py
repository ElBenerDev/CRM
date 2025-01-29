# Importaciones de Python estándar
import os
from datetime import datetime, timedelta, timezone
from pathlib import Path
import logging
import traceback
import secrets
from typing import Optional

# Importaciones de FastAPI y Starlette
from fastapi import (
    FastAPI,
    Request,
    Depends,
    HTTPException,
    status,
    Form
)
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse, RedirectResponse
from starlette.middleware import Middleware
from starlette.middleware.sessions import SessionMiddleware
from starlette.middleware.cors import CORSMiddleware
from starlette.exceptions import HTTPException as StarletteHTTPException

# Importaciones de SQLAlchemy
from sqlalchemy import func
from sqlalchemy.orm import Session

# Importaciones de rutas (routers)
from app.auth.router import router as auth_router
from app.routes.dashboard import router as dashboard_router
from app.routes.patients import router as patients_router
from app.routes.appointments import router as appointments_router
from app.routes.leads import router as leads_router
from app.routes.settings import router as settings_router

# Importaciones de configuración y utilidades
from config.settings import settings
from app.utils.db import (
    get_db,
    engine,
    Base,
    verify_db_connection,
    SessionLocal
)
from app.utils.logger import logger
from app.auth.utils import get_password_hash
from app.auth.dependencies import get_current_user_id

# Importaciones de modelos y schemas
from app.models.models import (
    Patient,
    Appointment,
    Lead,
    User
)
from app.schemas.schemas import (
    PatientCreate,
    PatientResponse,
    LeadCreate,
    LeadResponse
)

# Importaciones de middleware
from app.middleware.auth import AuthMiddleware
from app.middleware.debug import DebugMiddleware
from app.middleware.logging import LoggingMiddleware

# Importación de servidor
import uvicorn

# Configuración de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

# Configuración de directorios
BASE_DIR = Path(__file__).resolve().parent
TEMPLATES_DIR = BASE_DIR / "app" / "templates"
STATIC_DIR = BASE_DIR / "app" / "static"

# Asegurar que existan los directorios necesarios
for dir_path in [
    STATIC_DIR / "css",
    STATIC_DIR / "js",
    STATIC_DIR / "img",
    TEMPLATES_DIR
]:
    dir_path.mkdir(parents=True, exist_ok=True)
    
# Funciones auxiliares
async def get_current_user(request: Request, db: Session = Depends(get_db)) -> User:
    try:
        user_id = request.session.get("user_id")
        if not user_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="No autenticado"
            )
        
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Usuario no encontrado"
            )
        return user
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Error de autenticación"
        )

def init_db():
    try:
        if not verify_db_connection():
            raise Exception("No se pudo establecer conexión con la base de datos")
        Base.metadata.create_all(bind=engine)
        logger.info("✅ Base de datos inicializada correctamente")
        return True
    except Exception as e:
        logger.error(f"❌ Error al inicializar la base de datos: {str(e)}")
        return False

def init_admin_user():
    try:
        db = SessionLocal()
        admin = db.query(User).filter(User.email == "admin@admin.com").first()
        
        if not admin:
            print("Creando usuario admin...")
            admin = User(
                email="admin@admin.com",
                password=get_password_hash("admin123"),
                name="Admin",
                is_active=True,
                is_admin=True
            )
            db.add(admin)
            try:
                db.commit()
                print("✅ Usuario admin creado correctamente")
            except Exception as e:
                db.rollback()
                print(f"❌ Error al guardar usuario admin: {str(e)}")
        else:
            print("ℹ️ El usuario admin ya existe")
            if not admin.is_admin:
                admin.is_admin = True
                db.commit()
                print("✅ Permisos de admin actualizados")
    except Exception as e:
        print(f"❌ Error creando usuario admin: {str(e)}")
    finally:
        db.close()

def url_for(request: Request, name: str, **params):
    return request.url_for(name, **params)

# Configuración de la aplicación
app = FastAPI(
    title=settings.APP_NAME,
    description="Sistema CRM para gestión dental",  
    version=settings.APP_VERSION
)

# Configuración de templates
templates = Jinja2Templates(directory=str(TEMPLATES_DIR))
templates.env.globals["url_for"] = url_for

# Middleware configuration
@app.middleware("http")
async def log_requests(request: Request, call_next):
    logger.info("\n" + "="*50)
    logger.info(f"🔄 Nueva solicitud: {request.method} {request.url.path}")
    response = await call_next(request)
    logger.info(f"📤 Respuesta: {response.status_code}")
    return response

# Middleware stack (orden importante)
app.add_middleware(
    SessionMiddleware,
    secret_key=settings.SECRET_KEY,  # Usar la clave de settings.py
    session_cookie="session",
    max_age=1800,
    same_site="Lax",  # Corregir a "Lax" con mayúscula
    https_only=settings.ENVIRONMENT == "production"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

app.add_middleware(AuthMiddleware)
app.add_middleware(LoggingMiddleware)
app.add_middleware(DebugMiddleware)

# Montar archivos estáticos
app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")

app.include_router(auth_router, prefix="/auth", tags=["auth"])
app.include_router(dashboard_router, tags=["dashboard"])
app.include_router(patients_router, tags=["patients"])
app.include_router(appointments_router, tags=["appointments"])
app.include_router(leads_router, tags=["leads"])
app.include_router(settings_router, tags=["settings"])

# Eventos de la aplicación
@app.on_event("startup")
async def startup_event():
    logger.info("🚀 Aplicación iniciada")
    logger.info(f"🌐 Ambiente: {settings.ENVIRONMENT}")
    logger.info(f"🔧 Debug: {settings.DEBUG}")
    
    # Inicializar DB
    if not init_db():
        raise Exception("No se pudo inicializar la base de datos")
    
    # Crear usuario admin
    init_admin_user()

# Manejadores de excepciones
@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    if exc.status_code == 401:
        return RedirectResponse(url="/auth/login", status_code=303)
    return templates.TemplateResponse(
        "error.html",
        {
            "request": request,
            "error_message": str(exc.detail),
            "status_code": exc.status_code
        },
        status_code=exc.status_code
    )

@app.exception_handler(StarletteHTTPException)
async def starlette_exception_handler(request: Request, exc: StarletteHTTPException):
    if exc.status_code in [401, 403]:
        return RedirectResponse(url="/auth/login", status_code=302)
    
    if request.url.path.startswith(('/static/',)):
        return HTMLResponse(content="File not found", status_code=404)
    
    return templates.TemplateResponse(
        "errors/error.html",
        {
            "request": request,
            "error_message": str(exc.detail),
            "status_code": exc.status_code
        },
        status_code=exc.status_code
    )

@app.exception_handler(Exception)
async def generic_exception_handler(request: Request, exc: Exception):
    template_name = "errors/error.html"
    status_code = 500
    error_message = str(exc)

    if isinstance(exc, HTTPException):
        status_code = exc.status_code
        error_message = exc.detail

    logger.error(f"Error {status_code}: {error_message}")
    logger.error(traceback.format_exc())

    return templates.TemplateResponse(
        template_name,
        {
            "request": request,
            "status_code": status_code,
            "error_message": error_message
        },
        status_code=status_code
    )
    
@app.get("/")
async def root(request: Request):
    if "user_id" not in request.session:
        return RedirectResponse(url="/auth/login", status_code=303)
    return RedirectResponse(url="/dashboard", status_code=303)

# Ruta del dashboard - contiene toda la lógica
@app.get("/dashboard", response_class=HTMLResponse)
async def dashboard(
    request: Request,
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    try:
        current_user = db.query(User).filter(User.id == user_id).first()
        
        # Estadísticas para el dashboard
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

        # Próximas citas
        upcoming_appointments = db.query(Appointment)\
            .join(Patient)\
            .filter(Appointment.date >= datetime.now(timezone.utc))\
            .filter(Appointment.status == 'scheduled')\
            .order_by(Appointment.date)\
            .limit(5)\
            .all()

        # Últimos pacientes registrados
        recent_patients = db.query(Patient)\
            .order_by(Patient.created_at.desc())\
            .limit(5)\
            .all()

        return templates.TemplateResponse(
            "dashboard.html",
            {
                "request": request,
                "user": {
                    "name": current_user.name,
                    "email": current_user.email,
                    "role": "Admin"
                },
                "active": "dashboard",
                "stats": {
                    "total_patients": total_patients,
                    "appointments_today": appointments_today,
                    "pending_appointments": pending_appointments,
                    "completed_appointments": completed_appointments
                },
                "upcoming_appointments": upcoming_appointments,
                "recent_patients": recent_patients
            }
        )
    except Exception as e:
        logger.error(f"Error en dashboard: {str(e)}")
        return RedirectResponse(url="/auth/login", status_code=303)

# Rutas de pacientes
@app.get("/patients", response_class=HTMLResponse)
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
                    "role": "Admin",
                    "email": current_user.email
                },
                "active": "patients",
                "patients": patients,
                "datetime": datetime
            }
        )
    except Exception as e:
        logger.error(f"Error en patients_page: {str(e)}")
        return RedirectResponse(url="/auth/login", status_code=302)

@app.post("/api/patients/", response_model=PatientResponse)
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
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

# Rutas de citas
@app.get("/appointments", response_class=HTMLResponse)
@app.head("/appointments")
async def appointments_page(request: Request, db: Session = Depends(get_db)):
    if request.method == "HEAD":
        return HTMLResponse(content="")
        
    try:
        user_id = request.session.get("user_id")
        if not user_id:
            return RedirectResponse(url="/auth/login", status_code=302)
            
        current_user = db.query(User).filter(User.id == user_id).first()
        if not current_user:
            return RedirectResponse(url="/auth/login", status_code=302)

        appointments = db.query(Appointment)\
            .order_by(Appointment.date.desc())\
            .all()
        patients = db.query(Patient).order_by(Patient.name).all()

        return templates.TemplateResponse(
            "appointments.html",
            {
                "request": request,
                "user": {
                    "name": current_user.name,
                    "email": current_user.email,
                    "role": "Admin"
                },
                "active": "appointments",
                "appointments": appointments,
                "patients": patients,
                "datetime": datetime
            }
        )
    except Exception as e:
        logger.error(f"Error en appointments_page: {str(e)}")
        return RedirectResponse(url="/auth/login", status_code=302)
    
# Rutas de leads
@app.get("/leads", response_class=HTMLResponse)
@app.head("/leads")
async def leads_page(request: Request, db: Session = Depends(get_db)):
    try:
        user_id = request.session.get("user_id")
        if not user_id:
            return RedirectResponse(url="/auth/login", status_code=302)
            
        current_user = db.query(User).filter(User.id == user_id).first()
        if not current_user:
            return RedirectResponse(url="/auth/login", status_code=302)

        leads = db.query(Lead).order_by(Lead.created_at.desc()).all()
        
        return templates.TemplateResponse(
            "leads.html",
            {
                "request": request,
                "user": {
                    "name": current_user.name,
                    "role": "Admin",
                    "email": current_user.email
                },
                "active": "leads",
                "leads": leads
            }
        )
    except Exception as e:
        logger.error(f"Error en leads_page: {str(e)}")
        return RedirectResponse(url="/auth/login", status_code=302)

@app.post("/api/leads/", response_model=LeadResponse)
async def create_lead(
    lead: LeadCreate, 
    request: Request,
    db: Session = Depends(get_db)
):
    try:
        user_id = request.session.get("user_id")
        if not user_id:
            raise HTTPException(status_code=401, detail="No autenticado")

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
        return new_lead
        
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))
    
# Rutas de configuración y cierre de sesión
@app.get("/settings", response_class=HTMLResponse)
@app.head("/settings")
async def settings_page(request: Request, db: Session = Depends(get_db)):
    try:
        user_id = request.session.get("user_id")
        if not user_id:
            return RedirectResponse(url="/auth/login", status_code=302)
            
        current_user = db.query(User).filter(User.id == user_id).first()
        if not current_user:
            return RedirectResponse(url="/auth/login", status_code=302)

        return templates.TemplateResponse(
            "settings.html",
            {
                "request": request,
                "user": {
                    "name": current_user.name,
                    "email": current_user.email,
                    "role": "Admin"
                },
                "active": "settings"
            }
        )
    except Exception as e:
        logger.error(f"Error en settings_page: {str(e)}")
        return RedirectResponse(url="/auth/login", status_code=302)

@app.get("/auth/logout")
async def logout(request: Request):
    try:
        request.session.clear()
        return RedirectResponse(url="/auth/login", status_code=302)
    except Exception as e:
        logger.error(f"Error en logout: {str(e)}")
        return RedirectResponse(url="/auth/login", status_code=302)



# Configuración de inicio de la aplicación
if __name__ == "__main__":
    try:
        port = int(os.environ.get("PORT", 10000))
        uvicorn.run(
            "main:app",
            host="0.0.0.0",
            port=port,
            reload=settings.DEBUG,
            workers=4,
            log_level="info"
        )
    except Exception as e:
        logger.error(f"Error iniciando la aplicación: {str(e)}")