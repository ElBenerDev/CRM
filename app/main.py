from datetime import datetime, timezone, timedelta
from pathlib import Path
from typing import Optional

from fastapi import FastAPI, Request, HTTPException, Depends, status
from fastapi.params import Form
from fastapi.responses import JSONResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.encoders import jsonable_encoder
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import JWTError, jwt
from sqlalchemy import func, inspect
from sqlalchemy.orm import Session

# Importaciones de la aplicación
from app.db.session import get_db, engine
from app.db.models.base import Base
from app.db.models.patient import Patient
from app.db.models.appointment import Appointment, ServiceType, AppointmentStatus
from app.db.models.lead import Lead, LeadStatus
from app.db.models.user import User, SpecialtyType
from app.core.security import create_access_token, verify_password, get_password_hash
from app.core.config import settings
from app.api.v1.router import api_router

# OAuth2
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# Crear tablas en la base de datos
def init_db():
    inspector = inspect(engine)
    existing_tables = inspector.get_table_names()
    
    if not existing_tables:
        print("Inicializando base de datos...")
        Base.metadata.create_all(bind=engine)
        print("Base de datos inicializada correctamente.")
    else:
        print("Base de datos ya existente, omitiendo inicialización.")

init_db()

app = FastAPI(title="Medical CRM")
app.include_router(api_router, prefix="/api/v1")

# Montar archivos estáticos
BASE_DIR = Path(__file__).resolve().parent
app.mount("/static", StaticFiles(directory=str(BASE_DIR / "static")), name="static")

# Configurar templates
templates = Jinja2Templates(directory=str(BASE_DIR / "templates"))

def get_static_url(request: Request):
    def _static_url(path: str) -> str:
        return request.url_for("static", path=path)
    return _static_url

async def get_current_user(
    request: Request,
    db: Session = Depends(get_db)
) -> User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    token = request.cookies.get("access_token")
    if not token or not token.startswith("Bearer "):
        return RedirectResponse(url="/login", status_code=303)
    
    token = token.split("Bearer ")[1]
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])
        email: str = payload.get("sub")
        if email is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    
    user = db.query(User).filter(User.email == email).first()
    if user is None:
        raise credentials_exception
    return user

@app.get("/login")
async def login_page(request: Request):
    return templates.TemplateResponse(
        "login.html",
        {
            "request": request,
            "static_url": get_static_url(request)
        }
    )


@app.get("/")
async def root():
    return RedirectResponse(url="/login")

@app.get("/dashboard")
async def dashboard(
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # Estadísticas
    total_patients = db.query(func.count(Patient.id)).scalar() or 0
    total_appointments = db.query(func.count(Appointment.id)).scalar() or 0
    total_leads = db.query(func.count(Lead.id)).scalar() or 0
    
    today = datetime.now(timezone.utc)
    appointments_today = db.query(func.count(Appointment.id))\
        .filter(func.date(Appointment.datetime) == today.date())\
        .scalar() or 0

    upcoming_appointments = db.query(Appointment)\
        .join(Patient)\
        .filter(Appointment.datetime >= today)\
        .order_by(Appointment.datetime)\
        .limit(5)\
        .all()

    recent_patients = db.query(Patient)\
        .order_by(Patient.created_at.desc())\
        .limit(5)\
        .all()

    # Datos específicos según la especialidad
    specialty_data = {
        SpecialtyType.DENTAL: {
            "title": "Panel Dental",
            "procedures": ["Limpieza", "Extracción", "Ortodoncia"],
            "equipment": ["Sillón Dental", "Rayos X Dental"]
        },
        SpecialtyType.OPHTHALMOLOGY: {
            "title": "Panel Oftalmológico",
            "procedures": ["Examen Visual", "Tonometría", "Fondo de Ojo"],
            "equipment": ["Lámpara de Hendidura", "Tonómetro"]
        },
        SpecialtyType.GENERAL_MEDICINE: {
            "title": "Panel Medicina General",
            "procedures": ["Consulta General", "Chequeo Rutinario"],
            "equipment": ["Báscula", "Tensiómetro"]
        }
    }

    specialty_info = specialty_data.get(current_user.specialty, {})

    return templates.TemplateResponse(
        "dashboard.html",
        {
            "request": request,
            "static_url": get_static_url(request),
            "active": "dashboard",
            "user": current_user,
            "title": specialty_info.get("title", "Dashboard"),
            "procedures": specialty_info.get("procedures", []),
            "equipment": specialty_info.get("equipment", []),
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

# Mantener el resto de tus endpoints existentes agregando:
# current_user: User = Depends(get_current_user)
# Por ejemplo:

@app.get("/patients")
async def patients_page(
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)  # Agregar esta línea
):
    patients = db.query(Patient).order_by(Patient.created_at.desc()).all()
    return templates.TemplateResponse(
        "patients.html",
        {
            "request": request,
            "static_url": get_static_url(request),
            "active": "patients",
            "patients": patients,
            "user": current_user  # Agregar esta línea
        }
    )

@app.post("/token")
async def login(
    request: Request,
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    try:
        print(f"Intentando login para usuario: {form_data.username}")
        user = db.query(User).filter(User.email == form_data.username).first()
        
        if not user:
            print(f"Usuario no encontrado: {form_data.username}")
            return templates.TemplateResponse(
                "login.html",
                {
                    "request": request,
                    "static_url": get_static_url(request),
                    "error": "Usuario o contraseña incorrectos"
                },
                status_code=400
            )
        
        print(f"Usuario encontrado, verificando contraseña")
        if not verify_password(form_data.password, user.password):
            print(f"Contraseña incorrecta para usuario: {form_data.username}")
            return templates.TemplateResponse(
                "login.html",
                {
                    "request": request,
                    "static_url": get_static_url(request),
                    "error": "Usuario o contraseña incorrectos"
                },
                status_code=400
            )
        
        print(f"Login exitoso para usuario: {form_data.username}")
        access_token = create_access_token(
            subject=user.email,
            expires_delta=timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        )
        response = RedirectResponse(url="/dashboard", status_code=303)
        response.set_cookie(
            key="access_token",
            value=f"Bearer {access_token}",
            httponly=True
        )
        return response
        
    except Exception as e:
        print(f"Error en login: {str(e)}")
        return templates.TemplateResponse(
            "login.html",
            {
                "request": request,
                "static_url": get_static_url(request),
                "error": "Error en el sistema"
            },
            status_code=500
        )


@app.get("/appointments")
async def appointments_page(
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # Obtener todas las citas ordenadas por fecha
    appointments = db.query(Appointment)\
        .join(Patient)\
        .order_by(Appointment.datetime.desc())\
        .all()
    
    # Obtener todos los pacientes para el formulario de nueva cita
    patients = db.query(Patient).order_by(Patient.name).all()
    
    return templates.TemplateResponse(
        "appointments.html",
        {
            "request": request,
            "static_url": get_static_url(request),
            "active": "appointments",
            "appointments": appointments,
            "patients": patients,
            "user": current_user,
            "datetime": datetime
        }
    )
    
@app.get("/leads")
async def leads_page(
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # Obtener todos los leads ordenados por fecha de creación
    leads = db.query(Lead).order_by(Lead.created_at.desc()).all()
    
    return templates.TemplateResponse(
        "leads.html",
        {
            "request": request,
            "static_url": get_static_url(request),
            "active": "leads",
            "leads": leads,
            "user": current_user
        }
    )    

@app.get("/calendar")
async def calendar_page(
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    patients = db.query(Patient).all()
    return templates.TemplateResponse(
        "calendar.html",
        {
            "request": request,
            "static_url": get_static_url(request),
            "active": "calendar",
            "patients": patients,
            "user": current_user
        }
    )


@app.get("/logout")
async def logout():
    response = RedirectResponse(url="/login", status_code=303)
    response.delete_cookie("access_token")
    return response

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)