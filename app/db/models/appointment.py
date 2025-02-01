from sqlalchemy import Column, Integer, DateTime, String, ForeignKey, Text, Enum as SQLEnum
from sqlalchemy.orm import Mapped, relationship
from datetime import datetime, timezone
from app.db.base_class import Base
from typing import Optional, TYPE_CHECKING
import enum

if TYPE_CHECKING:
    from .patient import Patient
    from .user import User

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

    id: Mapped[int] = Column(Integer, primary_key=True, index=True)
    patient_id: Mapped[int] = Column(Integer, ForeignKey("patients.id"))
    datetime: Mapped[datetime] = Column(DateTime(timezone=True), nullable=False)
    duration: Mapped[int] = Column(Integer, default=30)
    service_type: Mapped[ServiceType] = Column(SQLEnum(ServiceType), nullable=False)
    status: Mapped[AppointmentStatus] = Column(SQLEnum(AppointmentStatus), default=AppointmentStatus.SCHEDULED)
    notes: Mapped[Optional[str]] = Column(Text, nullable=True)
    created_by: Mapped[int] = Column(Integer, ForeignKey("users.id"))
    created_at: Mapped[datetime] = Column(DateTime(timezone=True), default=datetime.now(timezone.utc))
    updated_at: Mapped[datetime] = Column(DateTime(timezone=True), default=datetime.now(timezone.utc), onupdate=datetime.now(timezone.utc))

    if TYPE_CHECKING:
        patient: Mapped["Patient"]
        creator: Mapped["User"]
    else:
        patient = relationship("Patient", back_populates="appointments")
        creator = relationship("User", backref="created_appointments")