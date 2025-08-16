from typing import List, Optional
import math
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.sidadup.data_perizinan import DataPerizinan
from app.schemas.sidadup.data_perizinan import (
    DataPerizinanCreate,
    DataPerizinanUpdate,
    DataPerizinanRead,
)

router = APIRouter(prefix="/api/data-perizinan", tags=["data_perizinan"])


@router.post("", response_model=DataPerizinanRead, status_code=201)
def create_data_perizinan(payload: DataPerizinanCreate, db: Session = Depends(get_db)):
    obj = DataPerizinan(**payload.model_dump(exclude_none=True))
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.get("", response_model=List[DataPerizinanRead])
def list_data_perizinan(
    db: Session = Depends(get_db),
    subsektor_id: Optional[int] = Query(None, description="Filter by subsektor_id"),
    q: Optional[str] = Query(None, description="Filter by no_sk (ILIKE)"),
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
):
    query = db.query(DataPerizinan)
    if subsektor_id is not None:
        query = query.filter(DataPerizinan.subsektor_id == subsektor_id)
    if q:
        query = query.filter(DataPerizinan.no_sk.ilike(f"%{q}%"))
    return query.order_by(DataPerizinan.data_perizinan_id).offset(offset).limit(limit).all()


@router.get("/paged")
def list_data_perizinan_paged(
    db: Session = Depends(get_db),
    subsektor_id: Optional[int] = Query(None, description="Filter by subsektor_id"),
    search: Optional[str] = Query(None, description="Filter by no_sk (ILIKE)"),
    q: Optional[str] = Query(None, description="Alias of search (ILIKE)"),
    pageNo: int = Query(0, ge=0),
    pageSize: int = Query(50, ge=1, le=200),
    sortBy: str = Query("id"),
    order: str = Query("ASC"),
):
    term = (search or q or "").strip()
    allowed_sort = {
        "id": "data_perizinan_id",
        "data_perizinan_id": "data_perizinan_id",
        "no_sk": "no_sk",
        "tanggal_sk": "tanggal_sk",
    }
    sort_prop = allowed_sort.get(sortBy.lower(), "data_perizinan_id")
    direction_desc = order.lower() == "desc"

    query = db.query(DataPerizinan)
    if subsektor_id is not None:
        query = query.filter(DataPerizinan.subsektor_id == subsektor_id)
    if term:
        query = query.filter(DataPerizinan.no_sk.ilike(f"%{term}%"))

    total = query.count()

    sort_col = getattr(DataPerizinan, sort_prop)
    if direction_desc:
        sort_col = sort_col.desc()

    rows = (
        query.order_by(sort_col)
        .offset(pageNo * pageSize)
        .limit(pageSize)
        .all()
    )
    items = [DataPerizinanRead.model_validate(r).model_dump() for r in rows]

    return {
        "items": items,
        "currentPage": pageNo,
        "pageSize": pageSize,
        "totalItems": total,
        "totalPages": math.ceil(total / pageSize) if pageSize else 0,
    }


@router.get("/{data_perizinan_id}", response_model=DataPerizinanRead)
def get_data_perizinan(data_perizinan_id: str, db: Session = Depends(get_db)):
    obj = db.get(DataPerizinan, data_perizinan_id)
    if not obj:
        raise HTTPException(status_code=404, detail="DataPerizinan not found")
    return obj


@router.put("/{data_perizinan_id}", response_model=DataPerizinanRead)
def update_data_perizinan(
    data_perizinan_id: str,
    payload: DataPerizinanUpdate,
    db: Session = Depends(get_db),
):
    obj = db.get(DataPerizinan, data_perizinan_id)
    if not obj:
        raise HTTPException(status_code=404, detail="DataPerizinan not found")
    for k, v in payload.model_dump(exclude_none=True).items():
        setattr(obj, k, v)
    db.commit()
    db.refresh(obj)
    return obj


@router.delete("/{data_perizinan_id}", status_code=204)
def delete_data_perizinan(data_perizinan_id: str, db: Session = Depends(get_db)):
    obj = db.get(DataPerizinan, data_perizinan_id)
    if not obj:
        raise HTTPException(status_code=404, detail="DataPerizinan not found")
    db.delete(obj)
    db.commit()
    return {"ok": True}
