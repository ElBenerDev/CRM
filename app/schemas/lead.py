from pydantic import BaseModel, EmailStr
from typing import Optional
from app.schemas.base import TimestampedSchema
from app.db.models.lead import LeadStatus

class LeadBase(BaseModel):
    name: str
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    status: LeadStatus = LeadStatus.NUEVO
    notes: Optional[str] = None

class LeadCreate(LeadBase):
    pass

class LeadResponse(LeadBase, TimestampedSchema):
    pass