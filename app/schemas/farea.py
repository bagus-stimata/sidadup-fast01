
from pydantic import BaseModel, Field, field_validator, ConfigDict
from typing import Optional
from datetime import datetime

class FAreaBase(BaseModel):
    kode1: str
    kode2: str
    description: str
    fdivisionBean: int
    # status_active: bool = Field(default=True, alias="statusActive") #Mapping Tanpa Dimapping malah bisa
    statusActive: bool = True
    @field_validator('statusActive')
    def check_status_active(cls, v):
        print(f"[DEBUG] status_active received: {v}")
        return v

    # class Config:
    #     from_attributes = True
    #     validate_by_name = True
    model_config = ConfigDict(
        from_attributes=True,
        validate_by_name=True
    )

    fregionBean: Optional[int] = 0

class FAreaCreate(FAreaBase):
    id: int
    pass

class FAreaUpdate(FAreaBase):
    id: int
    pass

class FAreaResponse(FAreaBase):
    id: int
    status_active: bool = Field(default=True, alias="statusActive") #Mapping Tanpa Dimapping malah bisa

    created: datetime
    modified: datetime

    # class Config:
    #     # orm_mode = True
    #     from_attributes = True
    #     validate_by_name = True

    model_config = ConfigDict(
        from_attributes=True,
        validate_by_name=True
    )