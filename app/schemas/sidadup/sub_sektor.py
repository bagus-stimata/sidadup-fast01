from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict

class SubSektorBase(BaseModel):
    nama: str
    sektor_id: int
    custom_column: str
    created_at: datetime | None = None
    updated_at: datetime | None = None
    deleted_at: datetime | None = None

class SubSektorCreate(SubSektorBase):
    pass

class SubSektorUpdate(BaseModel):
    nama: Optional[str] = None
    sektor_id: Optional[int] = None
    custom_column: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    deleted_at: Optional[datetime] = None

class SubSektorRead(SubSektorBase):
    model_config = ConfigDict(from_attributes=True)
    subsektor_id: int
