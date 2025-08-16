from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.core.database import get_db
from app.models.kecamatan import Kecamatan
from app.schemas.kecamatan import KecamatanCreate, KecamatanUpdate, KecamatanRead

router = APIRouter(prefix="/api/kecamatan", tags=["kecamatan"])

@router.post("", response_model=KecamatanRead, status_code=201)
def create_kecamatan(payload: KecamatanCreate, db: Session = Depends(get_db)):
    obj = Kecamatan(**payload.model_dump(exclude_none=True))
    db.add(obj); db.commit(); db.refresh(obj)
    return obj

@router.get("", response_model=List[KecamatanRead])
def list_kecamatan(db: Session = Depends(get_db), q: str | None = None, limit: int = 50, offset: int = 0):
    query = db.query(Kecamatan)
    if q:
        query = query.filter(Kecamatan.nama.ilike(f"%{q}%"))
    return query.order_by(Kecamatan.kecamatan_id).offset(offset).limit(limit).all()

@router.get("/{kecamatan_id}", response_model=KecamatanRead)
def get_kecamatan(kecamatan_id: int, db: Session = Depends(get_db)):
    obj = db.get(Kecamatan, kecamatan_id)
    if not obj:
        raise HTTPException(status_code=404, detail="Kecamatan not found")
    return obj

@router.put("/{kecamatan_id}", response_model=KecamatanRead)
def update_kecamatan(kecamatan_id: int, payload: KecamatanUpdate, db: Session = Depends(get_db)):
    obj = db.get(Kecamatan, kecamatan_id)
    if not obj:
        raise HTTPException(status_code=404, detail="Kecamatan not found")
    data = payload.model_dump(exclude_unset=True)
    for k, v in data.items():
        setattr(obj, k, v)
    db.add(obj)
    db.flush()
    db.refresh(obj)
    return obj

@router.delete("/{kecamatan_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_kecamatan(kecamatan_id: int, db: Session = Depends(get_db)):
    obj = db.get(Kecamatan, kecamatan_id)
    if not obj:
        raise HTTPException(status_code=404, detail="Kecamatan not found")
    db.delete(obj)
    db.flush()
    return None