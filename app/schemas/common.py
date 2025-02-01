from typing import TypeVar, Optional, Generic
from pydantic import BaseModel
from datetime import datetime

ModelType = TypeVar("ModelType")

class TimestampedSchema(BaseModel):
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True