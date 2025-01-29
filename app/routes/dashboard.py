from fastapi import APIRouter, Request, Depends, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import datetime, timezone, timedelta
import logging

from app.utils.db import get_db
from app.models.models import User, Patient, Appointment

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")
logger = logging.getLogger(__name__)

# Diccionarios para nombres legibles (mantener como está)
service_names = {
    'cleaning': 'Limpieza',
    'extraction': 'Extracción',
    'filling': 'Empaste',
    'root_canal': 'Endodoncia',
    'whitening': 'Blanqueamiento',
    'checkup': 'Revisión'
}

status_names = {
    'scheduled': 'Programada',
    'completed': 'Completada',
    'cancelled': 'Cancelada',
    'pending': 'Pendiente'
}

async def get_current_user(request: Request, db: Session = Depends(get_db)):
    user_id = request.session.get("user_id")
    if not user_id:
        raise HTTPException(status_code=401, detail="No autenticado")
    
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=401, detail="Usuario no encontrado")
    return user

@router.get("/dashboard", response_class=HTMLResponse)
async def dashboard(
    request: Request,
    db: Session = Depends(get_db)
):
    try:
        # Verificar autenticación
        user_id = request.session.get("user_id")
        if not user_id:
            logger.warning("Intento de acceso al dashboard sin autenticación")
            return RedirectResponse(url="/auth/login", status_code=303)

        current_user = db.query(User).filter(User.id == user_id).first()
        if not current_user:
            logger.warning(f"Usuario no encontrado: {user_id}")
            request.session.clear()
            return RedirectResponse(url="/auth/login", status_code=303)

        logger.info(f"Usuario autenticado accediendo al dashboard: {current_user.email}")
        
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

        logger.info("Dashboard cargado exitosamente")
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
                "recent_patients": recent_patients,
                "service_names": service_names,
                "status_names": status_names
            }
        )
    except Exception as e:
        logger.error(f"Error en dashboard: {str(e)}")
        # En caso de error, redirigir al login en lugar de lanzar una excepción
        return RedirectResponse(url="/auth/login", status_code=303)