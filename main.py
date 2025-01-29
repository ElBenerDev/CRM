from datetime import datetime, timedelta, timezone
import os
from typing import Optional
import logging
from pathlib import Path
import traceback
from starlette.middleware import Middleware
from starlette.middleware.sessions import SessionMiddleware
from starlette.middleware.cors import CORSMiddleware
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
from fastapi.security import OAuth2PasswordBearer
from starlette.exceptions import HTTPException as StarletteHTTPException
from sqlalchemy import func
from sqlalchemy.orm import Session

# Importaciones locales
from app.auth.utils import (
    SECRET_KEY, 
    ALGORITHM, 
    get_current_user, 
    ACCESS_TOKEN_EXPIRE_MINUTES
)
from app.auth.router import router as auth_router
from config.settings import settings
from app.utils.db import get_db, engine, Base, verify_db_connection
from app.utils.logger import logger
from app.models.models import Patient, Appointment, Lead, User
from app.schemas.schemas import PatientCreate, PatientResponse, LeadCreate, LeadResponse
from app.middleware.auth import AuthMiddleware
from app.middleware.debug import DebugMiddleware
from app.middleware.logging import LoggingMiddleware

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
    STATIC_DIR / "css" / "errors",
    STATIC_DIR / "js",
    STATIC_DIR / "img",
    TEMPLATES_DIR / "errors",
]:
    dir_path.mkdir(parents=True, exist_ok=True)
    
async def get_current_user_from_request(request: Request, db: Session) -> Optional[User]:
    try:
        token = request.cookies.get("access_token")
        if not token:
            return None
        if token.startswith("Bearer "):
            token = token.split(" ")[1]
        return await get_current_user(db=db, token=token)
    except:
        return None

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

def url_for(request: Request, name: str, **params):
    return request.url_for(name, **params)

# Configuración de templates
templates = Jinja2Templates(directory=str(TEMPLATES_DIR))
templates.env.globals["url_for"] = url_for


app = FastAPI(
    title=settings.APP_NAME,
    description="Sistema CRM para gestión dental",
    version=settings.APP_VERSION
)

# Primero SessionMiddleware
app.add_middleware(
    SessionMiddleware,
    secret_key="8f96d3a4e5b7c9d1f2g3h4j5k6l7m8n9p0q1r2s3t4u5v6w7x8y9z",
    session_cookie="session",
    max_age=1800,
    same_site="lax",
    https_only=False  # Cambia a True en producción
)

# Después AuthMiddleware
app.add_middleware(AuthMiddleware)

# Luego los demás middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

app.add_middleware(LoggingMiddleware)
app.add_middleware(DebugMiddleware)

# Montar archivos estáticos
app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")

# Incluir routers
app.include_router(auth_router)


@app.middleware("http")
async def log_requests(request: Request, call_next):
    logger.info("\n" + "="*50)
    logger.info(f"🔄 Nueva solicitud: {request.method} {request.url.path}")
    response = await call_next(request)
    logger.info(f"📤 Respuesta: {response.status_code}")
    return response

@app.on_event("startup")
async def startup_event():
    logger.info("🚀 Aplicación iniciada")
    logger.info(f"🌐 Ambiente: {settings.ENVIRONMENT}")
    logger.info(f"🔧 Debug: {settings.DEBUG}")
    init_db()

# Manejadores de excepciones
@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    if exc.status_code == 405:
        return RedirectResponse(url="/auth/login", status_code=303)
    return templates.TemplateResponse(
        "errors/error.html",
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
@app.get("/", response_class=HTMLResponse)
async def home(
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    try:
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

        # Próximas citas
        upcoming_appointments = db.query(Appointment)\
            .join(Patient)\
            .filter(Appointment.date >= datetime.now(timezone.utc))\
            .filter(Appointment.status == 'scheduled')\
            .order_by(Appointment.date)\
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
                "upcoming_appointments": upcoming_appointments
            }
        )
    except Exception as e:
        logger.error(f"Error en home: {str(e)}")
        return RedirectResponse(url="/auth/login", status_code=302)
    
@app.post("/api/patients/", response_model=PatientResponse)
async def create_patient(
    patient: PatientCreate, 
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    try:
        new_patient = Patient(
            name=patient.name,
            email=patient.email,
            phone=patient.phone,
            address=patient.address,
            notes=patient.notes,
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc),
            created_by=current_user.id
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

@app.get("/patients", response_class=HTMLResponse)
async def patients_page(
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    try:
        patients = db.query(Patient).order_by(Patient.created_at.desc()).all()
        logger.info(f"Pacientes encontrados: {len(patients)}")
        
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

@app.get("/leads", response_class=HTMLResponse)
@app.head("/leads")
async def leads_page(
    request: Request, 
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    try:
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
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
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
        return new_lead
        
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))
    
@app.get("/settings", response_class=HTMLResponse)
@app.head("/settings")
async def settings_page(
    request: Request,
    current_user: User = Depends(get_current_user)
):
    try:
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

@app.get("/appointments", response_class=HTMLResponse)
@app.head("/appointments")
async def appointments_page(
    request: Request, 
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if request.method == "HEAD":
        return HTMLResponse(content="")
        
    try:
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
    
@app.get("/auth/logout")
async def logout():
    response = RedirectResponse(url="/auth/login", status_code=302)
    response.delete_cookie(
        key="access_token",
        path="/",
        secure=True,
        httponly=True
    )
    return response

# Configuración de inicio de la aplicación
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=port,
        reload=settings.DEBUG,
        workers=4,
        log_level="info"
    )