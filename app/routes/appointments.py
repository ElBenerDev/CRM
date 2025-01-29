from fastapi import APIRouter, Request, Depends, HTTPException, status, Form
from fastapi.responses import HTMLResponse, RedirectResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from datetime import datetime, timezone
from typing import List, Optional
from app.auth.dependencies import get_current_user_id

from app.utils.db import get_db
from app.models.models import Appointment, Patient, User


router = APIRouter()
templates = Jinja2Templates(directory="app/templates")

appointment_status = {
    'scheduled': 'Programada',
    'completed': 'Completada',
    'cancelled': 'Cancelada'
}

service_types = {
    'consultation': 'Consulta',
    'cleaning': 'Limpieza',
    'extraction': 'Extracción',
    'filling': 'Empaste',
    'root_canal': 'Endodoncia',
    'whitening': 'Blanqueamiento'
}

@router.get("/appointments", response_class=HTMLResponse)
async def appointments_page(request: Request, db: Session = Depends(get_db)):
    try:
        user_id = request.session.get("user_id")
        if not user_id:
            return RedirectResponse(url="/auth/login", status_code=302)
            
        current_user = db.query(User).filter(User.id == user_id).first()
        if not current_user:
            return RedirectResponse(url="/auth/login", status_code=302)

        appointments = db.query(Appointment)\
            .join(Patient)\
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
                "status_options": appointment_status,
                "service_types": service_types,
                "datetime": datetime
            }
        )
    except Exception as e:
        print(f"Error en appointments_page: {str(e)}")
        return RedirectResponse(url="/auth/login", status_code=302)

@router.post("/api/appointments/")
async def create_appointment(
    request: Request,
    patient_id: int = Form(...),
    date: str = Form(...),
    time: str = Form(...),
    service_type: str = Form(...),
    notes: Optional[str] = Form(None),
    db: Session = Depends(get_db)
):
    try:
        user_id = request.session.get("user_id")
        if not user_id:
            raise HTTPException(status_code=401, detail="No autenticado")

        # Combinar fecha y hora
        date_time_str = f"{date} {time}"
        appointment_date = datetime.strptime(date_time_str, '%Y-%m-%d %H:%M')

        new_appointment = Appointment(
            patient_id=patient_id,
            date=appointment_date,
            service_type=service_type,
            notes=notes,
            status='scheduled',
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc),
            created_by=user_id
        )
        
        db.add(new_appointment)
        db.commit()
        db.refresh(new_appointment)
        
        return JSONResponse(
            content={"message": "Cita creada exitosamente"},
            status_code=200
        )
    
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))