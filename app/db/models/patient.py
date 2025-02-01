from datetime import datetime as dt
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import Mapped, relationship
from typing import List, Optional, TYPE_CHECKING
from app.db.base_class import Base

if TYPE_CHECKING:
    from .appointment import Appointment
    from .user import User

class Patient(Base):
    __tablename__ = "patients"

    id: Mapped[int] = Column(Integer, primary_key=True, index=True)
    name: Mapped[str] = Column(String, nullable=False)
    email: Mapped[Optional[str]] = Column(String, nullable=True)
    phone: Mapped[Optional[str]] = Column(String, nullable=True)
    address: Mapped[Optional[str]] = Column(String, nullable=True)
    created_by: Mapped[int] = Column(Integer, ForeignKey("users.id"))
    created_at: Mapped[dt] = Column(DateTime(timezone=True), default=dt.now)
    updated_at: Mapped[dt] = Column(DateTime(timezone=True), default=dt.now, onupdate=dt.now)

    appointments: Mapped[List["Appointment"]] = relationship(
        "Appointment", back_populates="patient"
    )
    creator: Mapped["User"] = relationship(
        "User", backref="created_patients"
    )