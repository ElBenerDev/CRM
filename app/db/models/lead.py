from sqlalchemy import Column, Integer, String, DateTime, Text, Enum as SQLEnum
from datetime import datetime, timezone
from app.db.models.base import Base
import enum

class LeadStatus(str, enum.Enum):
    NUEVO = "NUEVO"
    CONTACTADO = "CONTACTADO"
    INTERESADO = "INTERESADO"
    CONVERTIDO = "CONVERTIDO"
    PERDIDO = "PERDIDO"

class Lead(Base):
    __tablename__ = "leads"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    email = Column(String, nullable=True)
    phone = Column(String, nullable=True)
    source = Column(String, nullable=True)  # De dónde viene el lead
    status = Column(SQLEnum(LeadStatus), default=LeadStatus.NUEVO)
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), default=datetime.now(timezone.utc))
    updated_at = Column(DateTime(timezone=True), default=datetime.now(timezone.utc), onupdate=datetime.now(timezone.utc))