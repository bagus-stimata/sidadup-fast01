from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict

class JenisUsahaBase(BaseModel):
    nama: str
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

class JenisUsahaCreate(JenisUsahaBase):
    pass

class JenisUsahaUpdate(BaseModel):
    nama: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

class JenisUsahaRead(JenisUsahaBase):
    model_config = ConfigDict(from_attributes=True)
    jenis_usaha_id: int
