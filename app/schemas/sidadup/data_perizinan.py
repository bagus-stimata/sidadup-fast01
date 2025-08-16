from datetime import date
from typing import Optional
from pydantic import BaseModel, ConfigDict


class DataPerizinanBase(BaseModel):
    data_perizinan_id: str
    no_sk: str
    tanggal_sk: date
    masa_berlaku: Optional[date] = None
    custom_data: str
    subsektor_id: int
    wilayah_id: Optional[int] = None
    kecamatan_id: Optional[int] = None
    latlong: Optional[str] = None


class DataPerizinanCreate(DataPerizinanBase):
    pass


class DataPerizinanUpdate(BaseModel):
    no_sk: Optional[str] = None
    tanggal_sk: Optional[date] = None
    masa_berlaku: Optional[date] = None
    custom_data: Optional[str] = None
    subsektor_id: Optional[int] = None
    wilayah_id: Optional[int] = None
    kecamatan_id: Optional[int] = None
    latlong: Optional[str] = None


class DataPerizinanRead(DataPerizinanBase):
    model_config = ConfigDict(from_attributes=True)
