from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
import math
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.sidadup.daerah import Daerah
from app.schemas.sidadup.daerah import DaerahCreate, DaerahUpdate, DaerahRead


router = APIRouter(prefix="/api/daerah", tags=["daerah"])

@router.post("", response_model=DaerahRead, status_code=201)
def create_daerah(payload: DaerahCreate, db: Session = Depends(get_db)):
    obj = Daerah(**payload.model_dump(exclude_none=True))
    db.add(obj); db.commit(); db.refresh(obj)
    return obj

@router.get("", response_model=List[DaerahRead])
def list_daerah(
    db: Session = Depends(get_db),
    q: Optional[str] = Query(None, description="Filter by nama (ILIKE)"),
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
):
    query = db.query(Daerah)
    if q:
        query = query.filter(Daerah.nama.ilike(f"%{q}%"))
    return query.order_by(Daerah.daerah_id).offset(offset).limit(limit).all()

@router.get("/by-provinsi/{provinsi_id}", response_model=List[DaerahRead])
def list_daerah_by_provinsi(
    provinsi_id: int,
    db: Session = Depends(get_db),
    q: Optional[str] = Query(None, description="Filter by nama (ILIKE)"),
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
):
    query = db.query(Daerah).filter(Daerah.provinsi_id == provinsi_id)
    if q:
        query = query.filter(Daerah.nama.ilike(f"%{q}%"))
    return query.order_by(Daerah.daerah_id).offset(offset).limit(limit).all()


# --- PAGED ENDPOINTS ---

@router.get("/by-provinsi/{provinsi_id}/paged")
def list_daerah_by_provinsi_paged(
    provinsi_id: int,
    db: Session = Depends(get_db),
    search: Optional[str] = Query(None, description="Filter by nama (ILIKE)"),
    q: Optional[str] = Query(None, description="Alias of search (ILIKE)"),
    pageNo: int = Query(0, ge=0),
    pageSize: int = Query(50, ge=1, le=200),
    sortBy: str = Query("id"),
    order: str = Query("ASC"),
):
    # Normalisasi param FE
    term = (search or q or "").strip()

    # Mapping sortBy FE -> kolom DB
    allowed_sort = {
        "id": "daerah_id",
        "daerah_id": "daerah_id",
        "nama": "nama",
        "provinsi_id": "provinsi_id",
        "created_at": "created_at",
        "updated_at": "updated_at",
    }
    sort_prop = allowed_sort.get(sortBy.lower(), "daerah_id")
    direction_desc = order.lower() == "desc"

    query = db.query(Daerah).filter(Daerah.provinsi_id == provinsi_id)
    if term:
        query = query.filter(Daerah.nama.ilike(f"%{term}%"))

    total = query.count()

    sort_col = getattr(Daerah, sort_prop)
    if direction_desc:
        sort_col = sort_col.desc()

    rows = (
        query.order_by(sort_col)
        .offset(pageNo * pageSize)
        .limit(pageSize)
        .all()
    )

    # serialize to dicts via schema for JSON
    items = [DaerahRead.model_validate(r).model_dump() for r in rows]

    return {
        "items": items,
        "currentPage": pageNo,
        "pageSize": pageSize,
        "totalItems": total,
        "totalPages": math.ceil(total / pageSize) if pageSize else 0,
    }


@router.get("/paged")
def list_daerah_paged(
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
        "id": "daerah_id",
        "daerah_id": "daerah_id",
        "nama": "nama",
        "provinsi_id": "provinsi_id",
        "created_at": "created_at",
        "updated_at": "updated_at",
    }
    sort_prop = allowed_sort.get(sortBy.lower(), "daerah_id")
    direction_desc = order.lower() == "desc"

    query = db.query(Daerah)
    if term:
        query = query.filter(Daerah.nama.ilike(f"%{term}%"))

    total = query.count()

    sort_col = getattr(Daerah, sort_prop)
    if direction_desc:
        sort_col = sort_col.desc()

    rows = (
        query.order_by(sort_col)
        .offset(pageNo * pageSize)
        .limit(pageSize)
        .all()
    )

    items = [DaerahRead.model_validate(r).model_dump() for r in rows]

    return {
        "items": items,
        "currentPage": pageNo,
        "pageSize": pageSize,
        "totalItems": total,
        "totalPages": math.ceil(total / pageSize) if pageSize else 0,
    }

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

