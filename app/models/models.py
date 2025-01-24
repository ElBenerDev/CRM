from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
import enum
from datetime import datetime

Base = declarative_base()

class AppointmentStatus(str, enum.Enum):
    SCHEDULED = "scheduled"
    CANCELLED = "cancelled"
    COMPLETED = "completed"
    PENDING = "pending"

class ServiceType(str, enum.Enum):
    CONSULTA = "consulta"
    LIMPIEZA = "limpieza"
    TRATAMIENTO = "tratamiento"

class Patient(Base):
    __tablename__ = "patients"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    email = Column(String, unique=True, index=True, nullable=True)
    phone = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    appointments = relationship("Appointment", back_populates="patient")

class Appointment(Base):
    __tablename__ = "appointments"

    id = Column(Integer, primary_key=True, index=True)
    patient_id = Column(Integer, ForeignKey("patients.id"))
    date = Column(DateTime, index=True)
    service_type = Column(String)
    status = Column(String, default=AppointmentStatus.SCHEDULED)
    created_at = Column(DateTime, default=datetime.utcnow)

    patient = relationship("Patient", back_populates="appointments")