from fastapi import FastAPI, Request, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from datetime import datetime, timedelta
from config.settings import settings
import os
from sqlalchemy.orm import Session
from app.utils.db import get_db
from app.models.models import Patient, Appointment

app = FastAPI(
    title=settings.APP_NAME,
    description="Sistema CRM para gestión dental",
    version=settings.APP_VERSION,
)

# Montar archivos estáticos
app.mount("/static", StaticFiles(directory="app/static"), name="static")

# Configurar templates
templates = Jinja2Templates(directory="app/templates")

# Configurar CORS con origen permitido desde variables de entorno
allowed_origins = os.getenv("ALLOWED_ORIGINS", "*").split(",")
app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def home(request: Request):
    """Ruta principal que muestra el dashboard"""
    # Datos de ejemplo para el dashboard
    mock_stats = {
        "total_patients": 150,
        "appointments_today": 8,
        "active_leads": 25,
        "monthly_revenue": 15000.00
    }

    # Citas próximas de ejemplo
    mock_upcoming_appointments = [
        {
            "patient": {"name": "Juan Pérez"},
            "date": datetime.now() + timedelta(days=1),
            "service_type": "Consulta General",
            "status": "scheduled"
        },
        {
            "patient": {"name": "María García"},
            "date": datetime.now() + timedelta(days=2),
            "service_type": "Limpieza Dental",
            "status": "scheduled"
        }
    ]

    # Leads recientes de ejemplo
    mock_recent_leads = [
        {
            "name": "Carlos Rodríguez",
            "email": "carlos@example.com",
            "phone": "555-0101",
            "status": "new"
        },
        {
            "name": "Ana Martínez",
            "email": "ana@example.com",
            "phone": "555-0102",
            "status": "contacted"
        }
    ]

    return templates.TemplateResponse(
        "dashboard.html",
        {
            "request": request,
            "user": {
                "name": "ElBenerDev",
                "role": "Admin"
            },
            "active": "dashboard",
            "stats": mock_stats,
            "upcoming_appointments": mock_upcoming_appointments,
            "recent_leads": mock_recent_leads,
            "current_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
    )

@app.get("/patients")
async def patients_page(request: Request):
    """Ruta para la página de pacientes"""
    return templates.TemplateResponse(
        "patients.html",
        {
            "request": request,
            "user": {
                "name": "ElBenerDev",
                "role": "Admin"
            },
            "active": "patients",
            "patients": []
        }
    )

@app.get("/appointments")
async def appointments_page(request: Request):
    """Ruta para la página de citas"""
    # Datos de ejemplo para los pacientes
    mock_patients = [
        {"id": 1, "name": "Juan Pérez"},
        {"id": 2, "name": "María García"},
        {"id": 3, "name": "Carlos López"}
    ]

    # Datos de ejemplo para las citas
    mock_appointments = [
        {
            "id": 1,
            "patient": {"id": 1, "name": "Juan Pérez"},
            "date": datetime.now() + timedelta(days=1),
            "service_type": "consulta",
            "status": "scheduled"
        },
        {
            "id": 2,
            "patient": {"id": 2, "name": "María García"},
            "date": datetime.now() + timedelta(days=2),
            "service_type": "limpieza",
            "status": "scheduled"
        }
    ]

    return templates.TemplateResponse(
        "appointments.html",
        {
            "request": request,
            "user": {
                "name": "ElBenerDev",
                "role": "Admin"
            },
            "active": "appointments",
            "appointments": mock_appointments,
            "patients": mock_patients,
            "datetime": datetime  # Añadimos datetime para usar en el template
        }
    )

@app.get("/leads")
async def leads_page(request: Request):
    """Ruta para la página de leads"""
    return templates.TemplateResponse(
        "leads.html",
        {
            "request": request,
            "user": {
                "name": "ElBenerDev",
                "role": "Admin"
            },
            "active": "leads",
            "leads": []
        }
    )

@app.get("/settings")
async def settings_page(request: Request):
    """Ruta para la página de configuración"""
    return templates.TemplateResponse(
        "settings.html",
        {
            "request": request,
            "user": {
                "name": "ElBenerDev",
                "role": "Admin"
            },
            "active": "settings"
        }
    )

@app.get("/health")
async def health_check():
    """Endpoint para verificar el estado del servidor"""
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat()
    }


@app.get("/appointments")
async def appointments_page(request: Request):
    """Ruta para la página de citas"""
    # Ejemplo de datos de pacientes (reemplazar con datos reales de la BD)
    sample_patients = [
        {"id": 1, "name": "Juan Pérez"},
        {"id": 2, "name": "María García"},
        {"id": 3, "name": "Carlos López"}
    ]

    # Ejemplo de citas (reemplazar con datos reales de la BD)
    sample_appointments = [
        {
            "id": 1,
            "patient": {"name": "Juan Pérez"},
            "date": datetime.now() + timedelta(days=1),
            "service_type": "consulta",
            "status": "scheduled"
        },
        {
            "id": 2,
            "patient": {"name": "María García"},
            "date": datetime.now() + timedelta(days=2),
            "service_type": "limpieza",
            "status": "scheduled"
        }
    ]

    return templates.TemplateResponse(
        "appointments.html",
        {
            "request": request,
            "user": {
                "name": "ElBenerDev",
                "role": "Admin"
            },
            "active": "appointments",
            "appointments": sample_appointments,
            "patients": sample_patients
        }
    )

@app.post("/api/webhook")
async def webhook(request: Request):
    data = await request.json()
    print("Datos recibidos:", data)  # Para debug
    return {"status": "success", "data": data}

@app.get("/api/debug/patients")
async def get_patients(db: Session = Depends(get_db)):
    patients = db.query(Patient).all()
    return {"patients": [
        {
            "id": p.id, 
            "name": p.name,
            "appointments": len(p.appointments)
        } for p in patients
    ]}

@app.get("/api/debug/appointments")
async def get_appointments(db: Session = Depends(get_db)):
    appointments = db.query(Appointment).all()
    return {"appointments": [
        {
            "id": a.id,
            "patient_name": a.patient.name,
            "date": a.date.strftime("%Y-%m-%d %H:%M:%S"),
            "status": a.status,
            "service_type": a.service_type
        } for a in appointments
    ]}

if __name__ == "__main__":
    port = int(os.getenv("PORT", 8000))
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=port, reload=True)