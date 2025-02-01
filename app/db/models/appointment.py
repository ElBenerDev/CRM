from sqlalchemy import Column, Integer, DateTime, String, ForeignKey, Text, Enum as SQLEnum
from sqlalchemy.orm import Mapped, relationship
from datetime import datetime as dt
from typing import Optional, TYPE_CHECKING
from app.db.base_class import Base
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
    datetime: Mapped[dt] = Column(DateTime(timezone=True), nullable=False)
    duration: Mapped[int] = Column(Integer, default=30)
    service_type: Mapped[ServiceType] = Column(SQLEnum(ServiceType), nullable=False)
    status: Mapped[AppointmentStatus] = Column(SQLEnum(AppointmentStatus), default=AppointmentStatus.SCHEDULED)
    notes: Mapped[Optional[str]] = Column(Text, nullable=True)
    created_by: Mapped[int] = Column(Integer, ForeignKey("users.id"))
    created_at: Mapped[dt] = Column(DateTime(timezone=True), default=dt.now)
    updated_at: Mapped[dt] = Column(DateTime(timezone=True), default=dt.now, onupdate=dt.now)

    patient: Mapped["Patient"] = relationship(
        "Patient", back_populates="appointments"
    )
    creator: Mapped["User"] = relationship(
        "User", backref="created_appointments"
    )