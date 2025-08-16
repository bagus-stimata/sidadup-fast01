from typing import List, Optional
import math
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.sidadup.jenis_usaha import JenisUsaha
from app.schemas.sidadup.jenis_usaha import (
    JenisUsahaCreate,
    JenisUsahaUpdate,
    JenisUsahaRead,
)

router = APIRouter(prefix="/api/jenis-usaha", tags=["jenis_usaha"])

@router.post("", response_model=JenisUsahaRead, status_code=201)
def create_jenis(payload: JenisUsahaCreate, db: Session = Depends(get_db)):
    obj = JenisUsaha(**payload.model_dump(exclude_none=True))
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj

@router.get("", response_model=List[JenisUsahaRead])
def list_jenis(
    db: Session = Depends(get_db),
    q: Optional[str] = Query(None, description="Filter by nama (ILIKE)"),
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
):
    query = db.query(JenisUsaha)
    if q:
        query = query.filter(JenisUsaha.nama.ilike(f"%{q}%"))
    return query.order_by(JenisUsaha.jenis_usaha_id).offset(offset).limit(limit).all()

@router.get("/paged")
def list_jenis_paged(
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
        "id": "jenis_usaha_id",
        "jenis_usaha_id": "jenis_usaha_id",
        "nama": "nama",
        "created_at": "created_at",
        "updated_at": "updated_at",
    }
    sort_prop = allowed_sort.get(sortBy.lower(), "jenis_usaha_id")
    direction_desc = order.lower() == "desc"

    query = db.query(JenisUsaha)
    if term:
        query = query.filter(JenisUsaha.nama.ilike(f"%{term}%"))
    total = query.count()

    sort_col = getattr(JenisUsaha, sort_prop)
    if direction_desc:
        sort_col = sort_col.desc()

    rows = (
        query.order_by(sort_col)
        .offset(pageNo * pageSize)
        .limit(pageSize)
        .all()
    )
    items = [JenisUsahaRead.model_validate(r).model_dump() for r in rows]

    return {
        "items": items,
        "currentPage": pageNo,
        "pageSize": pageSize,
        "totalItems": total,
        "totalPages": math.ceil(total / pageSize) if pageSize else 0,
    }

@router.get("/{jenis_usaha_id}", response_model=JenisUsahaRead)
def get_jenis(jenis_usaha_id: int, db: Session = Depends(get_db)):
    obj = db.get(JenisUsaha, jenis_usaha_id)
    if not obj:
        raise HTTPException(status_code=404, detail="JenisUsaha not found")
    return obj

@router.put("/{jenis_usaha_id}", response_model=JenisUsahaRead)
def update_jenis(
    jenis_usaha_id: int,
    payload: JenisUsahaUpdate,
    db: Session = Depends(get_db),
):
    obj = db.get(JenisUsaha, jenis_usaha_id)
    if not obj:
        raise HTTPException(status_code=404, detail="JenisUsaha not found")
    for k, v in payload.model_dump(exclude_none=True).items():
        setattr(obj, k, v)
    db.commit()
    db.refresh(obj)
    return obj

@router.delete("/{jenis_usaha_id}", status_code=204)
def delete_jenis(jenis_usaha_id: int, db: Session = Depends(get_db)):
    obj = db.get(JenisUsaha, jenis_usaha_id)
    if not obj:
        raise HTTPException(status_code=404, detail="JenisUsaha not found")
    db.delete(obj)
    db.commit()
    return {"ok": True}
