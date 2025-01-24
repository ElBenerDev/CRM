from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from app.api import patients, appointments, leads
from app.utils.db import init_db, get_db
from app.services.crm import CRMService
from config.settings import settings
import uvicorn
from datetime import datetime, timedelta

app = FastAPI(
    title=settings.APP_NAME,
    description="Sistema CRM para gestión dental",
    version=settings.APP_VERSION,
    docs_url="/api/docs",
    redoc_url="/api/redoc",
)

# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configurar archivos estáticos y templates
app.mount("/static", StaticFiles(directory="app/static"), name="static")
templates = Jinja2Templates(directory="app/templates")

# Incluir routers API
app.include_router(
    patients.router,
    prefix=f"{settings.API_PREFIX}/patients",
    tags=["patients"]
)
app.include_router(
    appointments.router,
    prefix=f"{settings.API_PREFIX}/appointments",
    tags=["appointments"]
)
app.include_router(
    leads.router,
    prefix=f"{settings.API_PREFIX}/leads",
    tags=["leads"]
)

@app.on_event("startup")
async def startup_event():
    init_db()

# Rutas de la interfaz web
@app.get("/")
async def dashboard(request: Request):
    db = next(get_db())
    crm_service = CRMService(db)
    
    # Obtener estadísticas
    stats = {
        "total_patients": len(crm_service.get_patients()),
        "appointments_today": len(crm_service.get_appointments(
            start_date=datetime.now().replace(hour=0, minute=0),
            end_date=datetime.now().replace(hour=23, minute=59)
        )),
        "active_leads": len(crm_service.get_leads(status="active")),
        "monthly_revenue": "5,000"  # Ejemplo, ajustar según necesidades
    }
    
    # Obtener próximas citas
    upcoming_appointments = crm_service.get_appointments(
        start_date=datetime.now(),
        end_date=datetime.now() + timedelta(days=7),
        limit=5
    )
    
    return templates.TemplateResponse("dashboard.html", {
        "request": request,
        "stats": stats,
        "upcoming_appointments": upcoming_appointments
    })

@app.get("/patients")
async def patients_view(request: Request):
    db = next(get_db())
    crm_service = CRMService(db)
    patients_list = crm_service.get_patients(limit=10)
    return templates.TemplateResponse("patients.html", {
        "request": request,
        "patients": patients_list
    })

@app.get("/appointments")
async def appointments_view(request: Request):
    db = next(get_db())
    crm_service = CRMService(db)
    appointments_list = crm_service.get_appointments(
        start_date=datetime.now(),
        limit=10
    )
    return templates.TemplateResponse("appointments.html", {
        "request": request,
        "appointments": appointments_list
    })

@app.get("/leads")
async def leads_view(request: Request):
    db = next(get_db())
    crm_service = CRMService(db)
    leads_list = crm_service.get_leads(limit=10)
    return templates.TemplateResponse("leads.html", {
        "request": request,
        "leads": leads_list
    })

# Rutas API existentes
@app.get("/api")
async def root():
    return {
        "name": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "timestamp": datetime.utcnow(),
        "status": "running"
    }

@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat()
    }

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.DEBUG
    )   