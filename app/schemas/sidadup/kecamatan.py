from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict

class KecamatanBase(BaseModel):
    nama: str
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

class KecamatanCreate(KecamatanBase):
    daerah_id: int

class KecamatanUpdate(BaseModel):
    nama: Optional[str] = None
    daerah_id: Optional[int] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

class KecamatanRead(KecamatanBase):
    model_config = ConfigDict(from_attributes=True)
    kecamatan_id: int
    daerah_id: int