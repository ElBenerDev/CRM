from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
from app.utils.db import get_db
from app.services.crm import CRMService
from pydantic import BaseModel, field_validator
from datetime import datetime
from app.dependencies import get_crm_service
from app.core.config import settings

router = APIRouter(
    prefix=f"{settings.API_V1_STR}/patients",
    tags=["patients"],
    responses={404: {"description": "Not found"}},
)




class PatientBase(BaseModel):
    name: str
    email: Optional[str] = None  # Cambiado de EmailStr a Optional[str]
    phone: Optional[str] = None  # Hecho opcional
    address: Optional[str] = None
    notes: Optional[str] = None

    @field_validator('email')
    def validate_email(cls, v):
        if v is not None and '@' not in v:
            raise ValueError('Email inválido')
        return v

    @field_validator('phone')
    def validate_phone(cls, v):
        if v is not None:
            cleaned = ''.join(filter(str.isdigit, v))
            if len(cleaned) < 10:
                raise ValueError('El número de teléfono debe tener al menos 10 dígitos')
        return v

    @field_validator('name')
    def validate_name(cls, v):
        if not v or len(v.strip()) < 2:
            raise ValueError('El nombre debe tener al menos 2 caracteres')
        return v.strip()

class PatientCreate(PatientBase):
    pass

class PatientUpdate(PatientBase):
    name: Optional[str] = None  # Permitir actualización parcial

class PatientResponse(BaseModel):
    id: int
    name: str
    email: Optional[str]
    phone: Optional[str]
    address: Optional[str]
    notes: Optional[str]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True  # Actualizado de orm_mode a from_attributes

@router.post("/", response_model=PatientResponse, status_code=status.HTTP_201_CREATED)
async def create_patient(patient: PatientCreate, db: Session = Depends(get_db)):
    """
    Crea un nuevo paciente.
    
    Args:
        patient: Datos del paciente a crear
        db: Sesión de base de datos
    
    Returns:
        PatientResponse: Paciente creado
    
    Raises:
        HTTPException: Si hay un error al crear el paciente
    """
    try:
        crm_service = CRMService(db)
        return crm_service.create_patient(patient)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

@router.get("/", response_model=List[PatientResponse])
async def get_patients(
    skip: int = 0, 
    limit: int = 100, 
    search: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """
    Obtiene la lista de pacientes con opciones de paginación y búsqueda.
    
    Args:
        skip: Número de registros a saltar
        limit: Número máximo de registros a retornar
        search: Término de búsqueda opcional
        db: Sesión de base de datos
    
    Returns:
        List[PatientResponse]: Lista de pacientes
    """
    try:
        crm_service = CRMService(db)
        return crm_service.get_patients(skip=skip, limit=limit, search=search)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error al obtener los pacientes"
        )

@router.get("/{patient_id}", response_model=PatientResponse)
async def get_patient(patient_id: int, db: Session = Depends(get_db)):
    """
    Obtiene un paciente por su ID.
    
    Args:
        patient_id: ID del paciente
        db: Sesión de base de datos
    
    Returns:
        PatientResponse: Datos del paciente
    
    Raises:
        HTTPException: Si el paciente no existe
    """
    crm_service = CRMService(db)
    patient = crm_service.get_patient(patient_id)
    if patient is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Paciente no encontrado"
        )
    return patient

@router.put("/{patient_id}", response_model=PatientResponse)
async def update_patient(
    patient_id: int,
    patient_update: PatientUpdate,
    db: Session = Depends(get_db)
):
    """
    Actualiza los datos de un paciente.
    
    Args:
        patient_id: ID del paciente a actualizar
        patient_update: Datos a actualizar
        db: Sesión de base de datos
    
    Returns:
        PatientResponse: Paciente actualizado
    
    Raises:
        HTTPException: Si el paciente no existe o hay un error en la actualización
    """
    try:
        crm_service = CRMService(db)
        updated_patient = crm_service.update_patient(patient_id, patient_update)
        if updated_patient is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Paciente no encontrado"
            )
        return updated_patient
    except ValueError as ve:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(ve)
        )

@router.delete("/{patient_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_patient(patient_id: int, db: Session = Depends(get_db)):
    """
    Elimina un paciente por su ID.
    
    Args:
        patient_id: ID del paciente a eliminar
        db: Sesión de base de datos
    
    Returns:
        dict: Confirmación de eliminación
    
    Raises:
        HTTPException: Si el paciente no existe
    """
    try:
        crm_service = CRMService(db)
        if not crm_service.delete_patient(patient_id):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Paciente no encontrado"
            )
        return {"ok": True}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error al eliminar el paciente"
        )


@router.post("/", response_model=PatientResponse, status_code=status.HTTP_201_CREATED)
async def create_patient(
    patient: PatientCreate,
    crm_service: CRMService = Depends(get_crm_service)
):
    try:
        return crm_service.create_patient(patient)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )