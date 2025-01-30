from typing import List
from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session
from app.api.deps import get_current_user
from app.db.session import get_db
from app.db.models.lead import Lead
from app.schemas.lead import LeadCreate, LeadResponse
from datetime import datetime

router = APIRouter()

@router.get("/", response_model=List[LeadResponse])
async def get_leads(
    request: Request,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    leads = db.query(Lead).order_by(Lead.created_at.desc()).all()
    return leads

@router.post("/", response_model=LeadResponse)
async def create_lead(
    lead: LeadCreate,
    request: Request,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    new_lead = Lead(
        name=lead.name,
        email=lead.email,
        phone=lead.phone,
        status=lead.status,
        notes=lead.notes
    )
    
    db.add(new_lead)
    try:
        db.commit()
        db.refresh(new_lead)
        return new_lead
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=str(e))