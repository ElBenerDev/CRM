from sqlalchemy import Boolean, Column, String, Integer
from app.db.models.base import Base, TimestampedModel

class User(Base, TimestampedModel):
    __tablename__ = "users"

    email = Column(String, unique=True, index=True)
    name = Column(String)
    password = Column(String)
    is_active = Column(Boolean, default=True)
    is_admin = Column(Boolean, default=False)