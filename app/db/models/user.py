from sqlalchemy import Column, Integer, String, DateTime, Boolean
from sqlalchemy.orm import Mapped, relationship, RelationshipProperty
from datetime import datetime as dt
from typing import List, Optional, TYPE_CHECKING
from app.db.base_class import Base

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
    created_at: Mapped[dt] = Column(DateTime(timezone=True), default=dt.now)
    updated_at: Mapped[dt] = Column(DateTime(timezone=True), default=dt.now, onupdate=dt.now)

    # Las relaciones inversas se manejarán automáticamente por los backrefs
    # definidos en los otros modelos