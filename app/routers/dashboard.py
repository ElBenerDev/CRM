from fastapi import APIRouter, Depends, HTTPException
from app.core.auth import get_current_user
from app.db.models.user import User, SpecialtyType

router = APIRouter()

@router.get("/dashboard")
async def dashboard(current_user: User = Depends(get_current_user)):
    # Base común para todas las especialidades
    dashboard_data = {
        "user": {
            "name": current_user.name,
            "specialty": current_user.specialty.value
        },
        "common_stats": {
            "total_patients": 0,
            "appointments_today": 0
        }
    }
    
    # Contenido específico por especialidad
    if current_user.specialty == SpecialtyType.DENTIST:
        dashboard_data.update({
            "specialty_name": "Dental",
            "procedures": ["Limpieza", "Extracción", "Ortodoncia"],
            "equipment_status": ["Sillón Dental", "Rayos X Dental"]
        })
    
    elif current_user.specialty == SpecialtyType.OPHTHALMOLOGIST:
        dashboard_data.update({
            "specialty_name": "Oftalmología",
            "procedures": ["Examen Visual", "Tonometría", "Fondo de Ojo"],
            "equipment_status": ["Lámpara de Hendidura", "Tonómetro"]
        })
    
    elif current_user.specialty == SpecialtyType.GENERAL_PHYSICIAN:
        dashboard_data.update({
            "specialty_name": "Medicina General",
            "procedures": ["Consulta General", "Chequeo Rutinario"],
            "equipment_status": ["Báscula", "Tensiómetro"]
        })
    
    return dashboard_data