from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict

class DaerahBase(BaseModel):
    nama: str
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

class DaerahCreate(DaerahBase):
    provinsi_id: int

class DaerahUpdate(BaseModel):
    nama: Optional[str] = None
    provinsi_id: Optional[int] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

class DaerahRead(DaerahBase):
    model_config = ConfigDict(from_attributes=True)
    daerah_id: int
    provinsi_id: int