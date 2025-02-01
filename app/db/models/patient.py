from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import Mapped, relationship
from datetime import datetime, timezone
from app.db.base_class import Base
from typing import List, Optional, TYPE_CHECKING

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
    created_at: Mapped[datetime] = Column(DateTime(timezone=True), default=datetime.now(timezone.utc))
    updated_at: Mapped[datetime] = Column(DateTime(timezone=True), default=datetime.now(timezone.utc), onupdate=datetime.now(timezone.utc))

    if TYPE_CHECKING:
        appointments: Mapped[List["Appointment"]]
        creator: Mapped["User"]
    else:
        appointments = relationship("Appointment", back_populates="patient")
        creator = relationship("User", backref="created_patients")