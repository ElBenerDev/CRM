from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, Text, Enum
from app.db.base_class import Base
import enum

class LeadStatus(str, enum.Enum):
    NUEVO = "NUEVO"
    CONTACTADO = "CONTACTADO"
    INTERESADO = "INTERESADO"
    CONVERTIDO = "CONVERTIDO"
    PERDIDO = "PERDIDO"

class Lead(Base):
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    email = Column(String(100))
    phone = Column(String(20))
    status = Column(Enum(LeadStatus), default=LeadStatus.NUEVO)
    source = Column(String(50))
    notes = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)