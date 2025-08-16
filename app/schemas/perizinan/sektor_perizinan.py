from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict

class SektorPerizinanBase(BaseModel):
    nama: str
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    deleted_at: Optional[datetime] = None

class SektorPerizinanCreate(SektorPerizinanBase):
    pass

class SektorPerizinanUpdate(BaseModel):
    nama: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    deleted_at: Optional[datetime] = None

class SektorPerizinanRead(SektorPerizinanBase):
    model_config = ConfigDict(from_attributes=True)
    sektor_id: int
