from datetime import datetime as dt
from sqlalchemy import Column, Integer, String, DateTime, Text
from sqlalchemy.orm import Mapped, relationship
from typing import List, Optional, TYPE_CHECKING
from app.db.base_class import Base

if TYPE_CHECKING:
    from .appointment import Appointment

class Patient(Base):
    __tablename__ = "patients"

    id: Mapped[int] = Column(Integer, primary_key=True, index=True)
    name: Mapped[str] = Column(String, nullable=False)
    email: Mapped[Optional[str]] = Column(String, nullable=True)
    phone: Mapped[Optional[str]] = Column(String, nullable=True)
    notes: Mapped[Optional[str]] = Column(Text, nullable=True)
    created_at: Mapped[Optional[dt]] = Column(DateTime(timezone=True), nullable=True)
    updated_at: Mapped[Optional[dt]] = Column(DateTime(timezone=True), nullable=True)

    appointments: Mapped[List["Appointment"]] = relationship(
        "Appointment", back_populates="patient"
    )