from typing import List, Optional
import math
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.sidadup.sub_sektor import SubSektor
from app.schemas.sidadup.sub_sektor import (
    SubSektorCreate,
    SubSektorUpdate,
    SubSektorRead,
)

router = APIRouter(prefix="/api/sub-sektor", tags=["sub_sektor"])

@router.post("", response_model=SubSektorRead, status_code=201)
def create_subsektor(payload: SubSektorCreate, db: Session = Depends(get_db)):
    obj = SubSektor(**payload.model_dump(exclude_none=True))
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj

@router.get("", response_model=List[SubSektorRead])
def list_subsektor(
    db: Session = Depends(get_db),
    sektor_id: Optional[int] = Query(None, description="Filter by sektor_id"),
    q: Optional[str] = Query(None, description="Filter by nama (ILIKE)"),
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
):
    query = db.query(SubSektor)
    if sektor_id is not None:
        query = query.filter(SubSektor.sektor_id == sektor_id)
    if q:
        query = query.filter(SubSektor.nama.ilike(f"%{q}%"))
    return query.order_by(SubSektor.subsektor_id).offset(offset).limit(limit).all()

@router.get("/paged")
def list_subsektor_paged(
    db: Session = Depends(get_db),
    sektor_id: Optional[int] = Query(None, description="Filter by sektor_id"),
    search: Optional[str] = Query(None, description="Filter by nama (ILIKE)"),
    q: Optional[str] = Query(None, description="Alias of search (ILIKE)"),
    pageNo: int = Query(0, ge=0),
    pageSize: int = Query(50, ge=1, le=200),
    sortBy: str = Query("id"),
    order: str = Query("ASC"),
):
    term = (search or q or "").strip()
    allowed_sort = {
        "id": "subsektor_id",
        "subsektor_id": "subsektor_id",
        "nama": "nama",
        "sektor_id": "sektor_id",
        "created_at": "created_at",
        "updated_at": "updated_at",
    }
    sort_prop = allowed_sort.get(sortBy.lower(), "subsektor_id")
    direction_desc = order.lower() == "desc"

    query = db.query(SubSektor)
    if sektor_id is not None:
        query = query.filter(SubSektor.sektor_id == sektor_id)
    if term:
        query = query.filter(SubSektor.nama.ilike(f"%{term}%"))

    total = query.count()

    sort_col = getattr(SubSektor, sort_prop)
    if direction_desc:
        sort_col = sort_col.desc()

    rows = (
        query.order_by(sort_col)
        .offset(pageNo * pageSize)
        .limit(pageSize)
        .all()
    )

    items = [SubSektorRead.model_validate(r).model_dump() for r in rows]

    return {
        "items": items,
        "currentPage": pageNo,
        "pageSize": pageSize,
        "totalItems": total,
        "totalPages": math.ceil(total / pageSize) if pageSize else 0,
    }

@router.get("/{subsektor_id}", response_model=SubSektorRead)
def get_subsektor(subsektor_id: int, db: Session = Depends(get_db)):
    obj = db.get(SubSektor, subsektor_id)
    if not obj:
        raise HTTPException(status_code=404, detail="SubSektor not found")
    return obj

@router.put("/{subsektor_id}", response_model=SubSektorRead)
def update_subsektor(
    subsektor_id: int,
    payload: SubSektorUpdate,
    db: Session = Depends(get_db),
):
    obj = db.get(SubSektor, subsektor_id)
    if not obj:
        raise HTTPException(status_code=404, detail="SubSektor not found")
    for k, v in payload.model_dump(exclude_none=True).items():
        setattr(obj, k, v)
    db.commit()
    db.refresh(obj)
    return obj

@router.delete("/{subsektor_id}", status_code=204)
def delete_subsektor(subsektor_id: int, db: Session = Depends(get_db)):
    obj = db.get(SubSektor, subsektor_id)
    if not obj:
        raise HTTPException(status_code=404, detail="SubSektor not found")
    db.delete(obj)
    db.commit()
    return {"ok": True}
