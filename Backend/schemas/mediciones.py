# schemas.py
from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional, List

class MedicionOut(BaseModel):
    id: int
    sensors_id: int
    parameter: str
    units: str
    value: float
    datetime: datetime

    class Config:
        from_attributes = True  # (Pydantic v2)

class Paged(BaseModel):
    total: int
    items: List[MedicionOut] = Field(default_factory=list)
    page: int
    per_page: int
