from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, DateTime, Integer
from datetime import datetime, timezone
from app.db.base_class import Base  # noqa
from app.db.models.appointment import Appointment  # noqa
from app.db.models.patient import Patient  # noqa
from app.db.models.lead import Lead  # noqa
from app.db.models.user import User  # noqa
Base = declarative_base()

class TimestampedModel:
    """Mixin que agrega campos de timestamp a los modelos"""
    id = Column(Integer, primary_key=True, index=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))