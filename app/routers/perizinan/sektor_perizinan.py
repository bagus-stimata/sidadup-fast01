from typing import List, Optional
import math
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from sqlalchemy import asc, desc

from app.core.database import get_db
from app.models.sektor_perizinan import SektorPerizinan
from app.schemas.perizinan.sektor_perizinan import (
    SektorPerizinanCreate,
    SektorPerizinanUpdate,
    SektorPerizinanRead,
)

router = APIRouter(prefix="/api/sektor-perizinan", tags=["sektor_perizinan"])

@router.post("", response_model=SektorPerizinanRead, status_code=201)
def create_sektor(payload: SektorPerizinanCreate, db: Session = Depends(get_db)):
    obj = SektorPerizinan(**payload.model_dump(exclude_none=True))
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj

@router.get("", response_model=List[SektorPerizinanRead])
def list_sektor(
    db: Session = Depends(get_db),
    q: Optional[str] = Query(None, description="Filter by nama (ILIKE)"),
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
):
    query = db.query(SektorPerizinan)
    if q:
        query = query.filter(SektorPerizinan.nama.ilike(f"%{q}%"))
    return query.order_by(SektorPerizinan.sektor_id).offset(offset).limit(limit).all()

@router.get("/paged")
def list_sektor_paged(
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
        "id": "sektor_id",
        "sektor_id": "sektor_id",
        "nama": "nama",
        "created_at": "created_at",
        "updated_at": "updated_at",
    }
    sort_prop = allowed_sort.get(sortBy.lower(), "sektor_id")
    direction_desc = order.lower() == "desc"

    query = db.query(SektorPerizinan)
    if term:
        query = query.filter(SektorPerizinan.nama.ilike(f"%{term}%"))

    total = query.count()

    sort_col = getattr(SektorPerizinan, sort_prop)
    if direction_desc:
        sort_col = sort_col.desc()

    rows = (
        query.order_by(sort_col)
        .offset(pageNo * pageSize)
        .limit(pageSize)
        .all()
    )

    items = [SektorPerizinanRead.model_validate(r).model_dump() for r in rows]

    return {
        "items": items,
        "currentPage": pageNo,
        "pageSize": pageSize,
        "totalItems": total,
        "totalPages": math.ceil(total / pageSize) if pageSize else 0,
    }

@router.get("/{sektor_id}", response_model=SektorPerizinanRead)
def get_sektor(sektor_id: int, db: Session = Depends(get_db)):
    obj = db.get(SektorPerizinan, sektor_id)
    if not obj:
        raise HTTPException(status_code=404, detail="SektorPerizinan not found")
    return obj

@router.put("/{sektor_id}", response_model=SektorPerizinanRead)
def update_sektor(
    sektor_id: int,
    payload: SektorPerizinanUpdate,
    db: Session = Depends(get_db),
):
    obj = db.get(SektorPerizinan, sektor_id)
    if not obj:
        raise HTTPException(status_code=404, detail="SektorPerizinan not found")
    for k, v in payload.model_dump(exclude_none=True).items():
        setattr(obj, k, v)
    db.commit()
    db.refresh(obj)
    return obj

@router.delete("/{sektor_id}", status_code=204)
def delete_sektor(sektor_id: int, db: Session = Depends(get_db)):
    obj = db.get(SektorPerizinan, sektor_id)
    if not obj:
        raise HTTPException(status_code=404, detail="SektorPerizinan not found")
    db.delete(obj)
    db.commit()
    return {"ok": True}
