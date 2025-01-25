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
# Rutas de páginas con soporte mejorado para HEAD y mejor manejo de errores
@app.get("/", response_class=HTMLResponse)
@app.head("/")  # Agregar soporte explícito para HEAD
async def home(request: Request, db: Session = Depends(get_db)):
    """Ruta principal que muestra el dashboard"""
    if request.method == "HEAD":
        return HTMLResponse(content="")
    
    try:
        # ... resto del código del home ...
        return templates.TemplateResponse("dashboard.html", {...})
    except Exception as e:
        print(f"❌ Error en home: {str(e)}")
        return templates.TemplateResponse(
            "error.html",
            {
                "request": request,
                "error_message": str(e),
                "user": {"name": "ElBenerDev", "role": "Admin"},
                "active": "dashboard"
            },
            status_code=500
        )

@app.get("/patients", response_class=HTMLResponse)
@app.head("/patients")
async def patients_page(request: Request, db: Session = Depends(get_db)):
    """Ruta para la página de pacientes"""
    if request.method == "HEAD":
        return HTMLResponse(content="")
        
    try:
        print(f"🔍 Intentando cargar patients_page")
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