from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
from app.utils.db import get_db
from app.services.crm import CRMService
from pydantic import BaseModel
from datetime import datetime
from app.models.models import LeadStatus

router = APIRouter()

class LeadBase(BaseModel):
    patient_id: int
    title: str
    expected_value: float
    source: Optional[str] = None
    notes: Optional[str] = None

class LeadCreate(LeadBase):
    pass

class LeadUpdate(BaseModel):
    title: Optional[str] = None
    status: Optional[LeadStatus] = None
    expected_value: Optional[float] = None
    source: Optional[str] = None
    notes: Optional[str] = None

class LeadResponse(LeadBase):
    id: int
    status: LeadStatus
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True

@router.post("/", response_model=LeadResponse, status_code=status.HTTP_201_CREATED)
def create_lead(lead: LeadCreate, db: Session = Depends(get_db)):
    crm_service = CRMService(db)
    return crm_service.create_lead(lead)

@router.get("/", response_model=List[LeadResponse])
def get_leads(
    skip: int = 0,
    limit: int = 100,
    patient_id: Optional[int] = None,
    status: Optional[LeadStatus] = None,
    min_value: Optional[float] = None,
    max_value: Optional[float] = None,
    db: Session = Depends(get_db)
):
    crm_service = CRMService(db)
    return crm_service.get_leads(
        skip=skip,
        limit=limit,
        patient_id=patient_id,
        status=status,
        min_value=min_value,
        max_value=max_value
    )

@router.get("/{lead_id}", response_model=LeadResponse)
def get_lead(lead_id: int, db: Session = Depends(get_db)):
    crm_service = CRMService(db)
    lead = crm_service.get_lead(lead_id)
    if lead is None:
        raise HTTPException(status_code=404, detail="Lead not found")
    return lead

@router.put("/{lead_id}", response_model=LeadResponse)
def update_lead(
    lead_id: int,
    lead_update: LeadUpdate,
    db: Session = Depends(get_db)
):
    crm_service = CRMService(db)
    updated_lead = crm_service.update_lead(lead_id, lead_update)
    if updated_lead is None:
        raise HTTPException(status_code=404, detail="Lead not found")
    return updated_lead

@router.delete("/{lead_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_lead(lead_id: int, db: Session = Depends(get_db)):
    crm_service = CRMService(db)
    if not crm_service.delete_lead(lead_id):
        raise HTTPException(status_code=404, detail="Lead not found")
    return {"ok": True}