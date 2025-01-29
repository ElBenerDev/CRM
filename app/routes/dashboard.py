from fastapi import APIRouter, Request, Depends, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import datetime, timezone, timedelta

from app.utils.db import get_db
from app.models.models import User, Patient, Appointment  # Importar los modelos desde models.py
from app.auth.dependencies import get_current_user_id

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")

# Diccionarios para nombres legibles
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

@router.get("/dashboard", response_class=HTMLResponse)
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
                "recent_patients": recent_patients,
                "service_names": service_names,
                "status_names": status_names
            }
        )
    except Exception as e:
        print(f"Error en dashboard: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))