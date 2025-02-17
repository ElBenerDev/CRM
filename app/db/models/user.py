from datetime import datetime as dt
from sqlalchemy import Column, Integer, String, Boolean, Enum as SQLEnum, DateTime
from sqlalchemy.orm import Mapped
from typing import Optional
from app.db.base_class import Base
import enum

class SpecialtyType(str, enum.Enum):
    DENTAL = "DENTAL"
    OPHTHALMOLOGY = "OPHTHALMOLOGY"
    GENERAL_MEDICINE = "GENERAL_MEDICINE"

class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = Column(Integer, primary_key=True, index=True)
    email: Mapped[str] = Column(String, unique=True, index=True, nullable=False)
    name: Mapped[str] = Column(String, nullable=False)
    password: Mapped[str] = Column(String, nullable=False)
    is_active: Mapped[bool] = Column(Boolean, default=True)
    specialty: Mapped[SpecialtyType] = Column(SQLEnum(SpecialtyType), nullable=False)
    clinic_name: Mapped[Optional[str]] = Column(String, nullable=True)
    professional_license: Mapped[Optional[str]] = Column(String, nullable=True)
    created_at: Mapped[Optional[dt]] = Column(DateTime(timezone=True), nullable=True)
    updated_at: Mapped[Optional[dt]] = Column(DateTime(timezone=True), nullable=True)