from typing import List, Optional
import math
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.sidadup.badan_usaha import BadanUsaha
from app.schemas.sidadup.badan_usaha import (
    BadanUsahaCreate,
    BadanUsahaUpdate,
    BadanUsahaRead,
)

router = APIRouter(prefix="/api/badan-usaha", tags=["badan_usaha"])

@router.post("", response_model=BadanUsahaRead, status_code=201)
def create_badan(payload: BadanUsahaCreate, db: Session = Depends(get_db)):
    obj = BadanUsaha(**payload.model_dump(exclude_none=True))
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj

@router.get("", response_model=List[BadanUsahaRead])
def list_badan(
    db: Session = Depends(get_db),
    q: Optional[str] = Query(None, description="Filter by nama (ILIKE)"),
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
):
    query = db.query(BadanUsaha)
    if q:
        query = query.filter(BadanUsaha.nama.ilike(f"%{q}%"))
    return query.order_by(BadanUsaha.badan_usaha_id).offset(offset).limit(limit).all()

@router.get("/paged")
def list_badan_paged(
    db: Session = Depends(get_db),
    search: Optional[str] = Query(None, description="Filter by nama (ILIKE)"),
    q: Optional[str] = Query(None, description="Alias of search (ILIKE)"),
    pageNo: int = Query(0, ge=0),
    pageSize: int = Query(50, ge=1, le=200),
    sortBy: str = Query("id"),
    order: str = Query("ASC"),
):
    term = (search or q or "").strip()
    allowed_sort = {
        "id": "badan_usaha_id",
        "badan_usaha_id": "badan_usaha_id",
        "nama": "nama",
        "created_at": "created_at",
        "updated_at": "updated_at",
    }
    sort_prop = allowed_sort.get(sortBy.lower(), "badan_usaha_id")
    direction_desc = order.lower() == "desc"

    query = db.query(BadanUsaha)
    if term:
        query = query.filter(BadanUsaha.nama.ilike(f"%{term}%"))
    total = query.count()

    sort_col = getattr(BadanUsaha, sort_prop)
    if direction_desc:
        sort_col = sort_col.desc()

    rows = (
        query.order_by(sort_col)
        .offset(pageNo * pageSize)
        .limit(pageSize)
        .all()
    )
    items = [BadanUsahaRead.model_validate(r).model_dump() for r in rows]

    return {
        "items": items,
        "currentPage": pageNo,
        "pageSize": pageSize,
        "totalItems": total,
        "totalPages": math.ceil(total / pageSize) if pageSize else 0,
    }

@router.get("/{badan_usaha_id}", response_model=BadanUsahaRead)
def get_badan(badan_usaha_id: int, db: Session = Depends(get_db)):
    obj = db.get(BadanUsaha, badan_usaha_id)
    if not obj:
        raise HTTPException(status_code=404, detail="BadanUsaha not found")
    return obj

@router.put("/{badan_usaha_id}", response_model=BadanUsahaRead)
def update_badan(
    badan_usaha_id: int,
    payload: BadanUsahaUpdate,
    db: Session = Depends(get_db),
):
    obj = db.get(BadanUsaha, badan_usaha_id)
    if not obj:
        raise HTTPException(status_code=404, detail="BadanUsaha not found")
    for k, v in payload.model_dump(exclude_none=True).items():
        setattr(obj, k, v)
    db.commit()
    db.refresh(obj)
    return obj

@router.delete("/{badan_usaha_id}", status_code=204)
def delete_badan(badan_usaha_id: int, db: Session = Depends(get_db)):
    obj = db.get(BadanUsaha, badan_usaha_id)
    if not obj:
        raise HTTPException(status_code=404, detail="BadanUsaha not found")
    db.delete(obj)
    db.commit()
    return {"ok": True}
