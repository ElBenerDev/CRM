from sqlalchemy import Column, Integer, DateTime, String, ForeignKey, Text, Enum as SQLEnum
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
from app.db.base_class import Base  # Importar Base desde base_class
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
    datetime = Column(DateTime(timezone=True), nullable=False)
    duration = Column(Integer, default=30)
    service_type = Column(SQLEnum(ServiceType), nullable=False)
    status = Column(SQLEnum(AppointmentStatus), default=AppointmentStatus.SCHEDULED)
    notes = Column(Text, nullable=True)
    created_by = Column(Integer, ForeignKey("users.id"))
    created_at = Column(DateTime(timezone=True), default=datetime.now(timezone.utc))
    updated_at = Column(DateTime(timezone=True), default=datetime.now(timezone.utc), onupdate=datetime.now(timezone.utc))

    # Relaciones
    patient = relationship("Patient", back_populates="appointments")
    creator = relationship("User", backref="created_appointments")