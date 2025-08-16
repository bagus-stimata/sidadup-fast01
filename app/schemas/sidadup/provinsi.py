from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict

class ProvinsiBase(BaseModel):
    nama: str
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

class ProvinsiCreate(ProvinsiBase):
    provinsi_id: int  # karena DDL tidak ada default

class ProvinsiUpdate(BaseModel):
    nama: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

class ProvinsiRead(ProvinsiBase):
    model_config = ConfigDict(from_attributes=True)
    provinsi_id: int