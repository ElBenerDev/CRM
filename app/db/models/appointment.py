from sqlalchemy import Column, Integer, DateTime, String, ForeignKey, Text, Enum as SQLEnum
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
from app.db.models.base import Base
import enum

class ServiceType(str, enum.Enum):
    CONSULTA = "CONSULTA"
    LIMPIEZA = "LIMPIEZA"
    TRATAMIENTO = "TRATAMIENTO"

class AppointmentStatus(str, enum.Enum):
    SCHEDULED = "SCHEDULED"
    COMPLETED = "COMPLETED"
    CANCELLED = "CANCELLED"
    PENDING = "PENDING"

class Appointment(Base):
    __tablename__ = "appointments"

    id = Column(Integer, primary_key=True, index=True)
    patient_id = Column(Integer, ForeignKey("patients.id"))
    date = Column(DateTime(timezone=True), nullable=False)
    service_type = Column(SQLEnum(ServiceType), nullable=False)
    status = Column(SQLEnum(AppointmentStatus), default=AppointmentStatus.SCHEDULED)
    notes = Column(Text, nullable=True)  
    created_at = Column(DateTime(timezone=True), default=datetime.now(timezone.utc))
    updated_at = Column(DateTime(timezone=True), default=datetime.now(timezone.utc), onupdate=datetime.now(timezone.utc))

    # Relación
    patient = relationship("Patient", back_populates="appointments")