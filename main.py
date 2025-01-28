# JWT y Autenticación
from jose import JWTError, jwt
from app.auth.utils import SECRET_KEY, ALGORITHM, oauth2_scheme, get_current_user, ACCESS_TOKEN_EXPIRE_MINUTES
from app.auth.router import router as auth_router
import uvicorn
from starlette.exceptions import HTTPException as StarletteHTTPException

# Imports estándar de Python
from datetime import datetime, timedelta, timezone
import os
import time
from typing import Optional, Dict, List

# FastAPI y Starlette
from fastapi import FastAPI, Request, Depends, HTTPException, status, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import PlainTextResponse, JSONResponse, HTMLResponse, RedirectResponse
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from starlette.middleware.base import BaseHTTPMiddleware
from fastapi.exceptions import HTTPException

# SQLAlchemy
from sqlalchemy import func, desc
from sqlalchemy.orm import Session, joinedload

# Configuración y utilidades locales
from config.settings import settings
from app.utils.db import get_db, engine, Base, verify_db_connection, reset_db

# Modelos y Schemas
from app.models.models import Patient, Appointment, Lead, User
from app.schemas.schemas import (
    PatientCreate, PatientResponse,
    AppointmentCreate, AppointmentResponse,
    LeadCreate, LeadResponse,
    AppointmentUpdate
)
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Configuración de directorios
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
STATIC_DIR = os.path.join(BASE_DIR, "app", "static")
TEMPLATES_DIR = os.path.join(BASE_DIR, "app", "templates")

# Middlewares
class AuthMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        excluded_paths = [
            "/auth/login",
            "/auth/token", 
            "/auth/register",
            "/auth/logout",
            "/static"
        ]
        
        if any(request.url.path.startswith(path) for path in excluded_paths):
            return await call_next(request)

        try:
            token = request.cookies.get("access_token")
            if not token:
                return RedirectResponse(url="/auth/login", status_code=302)

            if token.startswith("Bearer "):
                token = token.split(" ")[1]

            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
            email = payload.get("sub")
            
            if not email:
                return RedirectResponse(url="/auth/login", status_code=302)

            response = await call_next(request)
            return response
            
        except Exception as e:
            print(f"❌ Auth Error: {str(e)}")
            return RedirectResponse(url="/auth/login", status_code=302)

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

# Inicialización de FastAPI
app = FastAPI(
    title=settings.APP_NAME,
    description="Sistema CRM para gestión dental",
    version=settings.APP_VERSION,
)

# Configuración de middleware
app.add_middleware(LoggingMiddleware)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.add_middleware(AuthMiddleware)
app.add_middleware(DebugMiddleware)

# Routers
app.include_router(auth_router)

# Configuración de archivos estáticos
for dir_name in ["js", "css", "img"]:
    os.makedirs(os.path.join(STATIC_DIR, dir_name), exist_ok=True)

app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")

# Funciones auxiliares
def format_date(date):
    if date is None:
        return datetime.utcnow().strftime('%d/%m/%Y')
    return date.strftime('%d/%m/%Y')

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

# Templates
templates = Jinja2Templates(directory=TEMPLATES_DIR)
templates.env.filters["format_date"] = format_date

# Rutas principales
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
        print(f"Error: {str(e)}")
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
async def patients_page(request: Request, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
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
        return RedirectResponse(url="/auth/login", status_code=302)

# Additional routes
@app.get("/leads", response_class=HTMLResponse)
@app.head("/leads")
async def leads_page(
    request: Request, 
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Ruta para la página de leads"""
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
        return RedirectResponse(url="/auth/login", status_code=302)

@app.get("/appointments", response_class=HTMLResponse)
@app.head("/appointments") 
async def appointments_page(
    request: Request, 
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Ruta para la página de citas"""
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
        return RedirectResponse(url="/auth/login", status_code=302)
    
    
@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(request: Request, exc: StarletteHTTPException):
    if exc.status_code == 401 or exc.status_code == 403:
        return RedirectResponse(url="/auth/login", status_code=302)
    return templates.TemplateResponse(
        "error.html",
        {
            "request": request,
            "error_message": str(exc.detail),
            "status_code": exc.status_code
        },
        status_code=exc.status_code
    )
    
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


# Inicio de la aplicación
if __name__ == "__main__":
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=port,
        reload=settings.DEBUG,
        workers=4,
        log_level="info"
    )