# app/dependencies.py
from fastapi import Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.utils.db import get_db
from app.services.crm import CRMService

def get_crm_service(db: Session = Depends(get_db)) -> CRMService:
    try:
        return CRMService(db)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error al inicializar el servicio CRM"
        )