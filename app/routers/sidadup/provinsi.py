from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.sidadup.provinsi import Provinsi
from app.schemas.sidadup.provinsi import ProvinsiCreate, ProvinsiUpdate, ProvinsiRead

router = APIRouter(prefix="/api/provinsi", tags=["provinsi"])

@router.post("", response_model=ProvinsiRead, status_code=201)
def create_provinsi(payload: ProvinsiCreate, db: Session = Depends(get_db)):
    obj = Provinsi(**payload.model_dump(exclude_none=True))
    db.add(obj); db.commit(); db.refresh(obj)
    return obj

@router.get("", response_model=List[ProvinsiRead])
def list_provinsi(
    db: Session = Depends(get_db),
    q: str | None = None,
    limit: int = 50,
    offset: int = 0,
):
    query = db.query(Provinsi)
    if q:
        query = query.filter(Provinsi.nama.ilike(f"%{q}%"))
    return query.order_by(Provinsi.provinsi_id).offset(offset).limit(limit).all()

@router.get("/{provinsi_id}", response_model=ProvinsiRead)
def get_provinsi(provinsi_id: int, db: Session = Depends(get_db)):
    obj = db.get(Provinsi, provinsi_id)
    if not obj:
        raise HTTPException(status_code=404, detail="Provinsi not found")
    return obj

@router.put("/{provinsi_id}", response_model=ProvinsiRead)
def update_provinsi(provinsi_id: int, payload: ProvinsiUpdate, db: Session = Depends(get_db)):
    obj = db.get(Provinsi, provinsi_id)
    if not obj:
        raise HTTPException(status_code=404, detail="Provinsi not found")
    for k, v in payload.model_dump(exclude_unset=True).items():
        setattr(obj, k, v)
    db.commit()
    db.refresh(obj)
    return obj

@router.delete("/{provinsi_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_provinsi(provinsi_id: int, db: Session = Depends(get_db)):
    obj = db.get(Provinsi, provinsi_id)
    if not obj:
        raise HTTPException(status_code=404, detail="Provinsi not found")
    db.delete(obj)
    db.commit()
    return None