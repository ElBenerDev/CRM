from sqlalchemy import Column, Integer, String, DateTime, Boolean
from sqlalchemy.orm import Mapped, relationship
from datetime import datetime, timezone
from app.db.base_class import Base
from typing import List, Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from .appointment import Appointment
    from .patient import Patient

class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = Column(Integer, primary_key=True, index=True)
    email: Mapped[str] = Column(String, unique=True, index=True, nullable=False)
    hashed_password: Mapped[str] = Column(String, nullable=False)
    full_name: Mapped[str] = Column(String)
    is_active: Mapped[bool] = Column(Boolean, default=True)
    is_superuser: Mapped[bool] = Column(Boolean, default=False)
    created_at: Mapped[datetime] = Column(DateTime(timezone=True), default=datetime.now(timezone.utc))
    updated_at: Mapped[datetime] = Column(DateTime(timezone=True), default=datetime.now(timezone.utc), onupdate=datetime.now(timezone.utc))

    if TYPE_CHECKING:
        created_appointments: Mapped[List["Appointment"]]
        created_patients: Mapped[List["Patient"]]