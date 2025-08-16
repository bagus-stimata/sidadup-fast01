from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict

class BadanUsahaBase(BaseModel):
    nama: str
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

class BadanUsahaCreate(BadanUsahaBase):
    pass

class BadanUsahaUpdate(BaseModel):
    nama: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

class BadanUsahaRead(BadanUsahaBase):
    model_config = ConfigDict(from_attributes=True)
    badan_usaha_id: int
