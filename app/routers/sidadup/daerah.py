from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.daerah import Daerah
from app.schemas.daerah import DaerahCreate, DaerahUpdate, DaerahRead

router = APIRouter(prefix="/api/daerah", tags=["daerah"])

@router.post("", response_model=DaerahRead, status_code=201)
def create_daerah(payload: DaerahCreate, db: Session = Depends(get_db)):
    obj = Daerah(**payload.model_dump(exclude_none=True))
    db.add(obj); db.commit(); db.refresh(obj)
    return obj

@router.get("", response_model=List[DaerahRead])
def list_daerah(
    db: Session = Depends(get_db),
    q: str | None = None,
    limit: int = 50,
    offset: int = 0,
):
    query = db.query(Daerah)
    if q:
        query = query.filter(Daerah.nama.ilike(f"%{q}%"))
    return query.order_by(Daerah.daerah_id).offset(offset).limit(limit).all()

@router.get("/{daerah_id}", response_model=DaerahRead)
def get_daerah(daerah_id: int, db: Session = Depends(get_db)):
    obj = db.get(Daerah, daerah_id)
    if not obj:
        raise HTTPException(status_code=404, detail="Daerah not found")
    return obj

@router.put("/{daerah_id}", response_model=DaerahRead)
def update_daerah(daerah_id: int, payload: DaerahUpdate, db: Session = Depends(get_db)):
    obj = db.get(Daerah, daerah_id)
    if not obj:
        raise HTTPException(status_code=404, detail="Daerah not found")
    for k, v in payload.model_dump(exclude_unset=True).items():
        setattr(obj, k, v)
    db.commit()
    db.refresh(obj)
    return obj

@router.delete("/{daerah_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_daerah(daerah_id: int, db: Session = Depends(get_db)):
    obj = db.get(Daerah, daerah_id)
    if not obj:
        raise HTTPException(status_code=404, detail="Daerah not found")
    db.delete(obj)
    db.commit()
    return None