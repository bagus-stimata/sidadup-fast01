from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from httpx import Response
from sqlalchemy.orm import Session
from sqlalchemy import asc, desc

import math

from app.core.database import get_db
from app.models.sidadup.provinsi import Provinsi
from app.schemas.sidadup.provinsi import ProvinsiCreate, ProvinsiUpdate, ProvinsiRead

router = APIRouter(prefix="/api/provinsi", tags=["provinsi"])

@router.post("", response_model=ProvinsiRead, status_code=201)
def create_provinsi(payload: ProvinsiCreate, db: Session = Depends(get_db)):
    obj = Provinsi(**payload.model_dump(exclude_none=True))
    db.add(obj); db.commit(); db.refresh(obj)
    return obj

@router.delete("/{provinsi_id}", status_code=204)
def delete_provinsi(provinsi_id: int, db: Session = Depends(get_db)):
    obj = db.get(Provinsi, provinsi_id)
    if not obj:
        raise HTTPException(status_code=404, detail="Provinsi not found")
    db.delete(obj)
    db.commit()
    return Response(status_code=204)

# === List Provinsi (semua) ===
@router.get("", response_model=list[ProvinsiRead])
def list_provinsi(db: Session = Depends(get_db)):
    return db.query(Provinsi).all()
# === Paged Provinsi ===
@router.get("/paged")
def list_provinsi_paged(
    pageNo: int = Query(0, ge=0),
    pageSize: int = Query(10, gt=0),
    sortBy: str = Query("id"),
    order: str = Query("ASC"),
    search: str = Query(""),
    db: Session = Depends(get_db),
):
    q = db.query(Provinsi)
    if search:
        q = q.filter(Provinsi.nama.ilike(f"%{search}%"))

    total = q.count()
    sort_map = {
        "id": "provinsi_id",
        "provinsi_id": "provinsi_id",
        "nama": "nama",
        "created_at": "created_at",
        "updated_at": "updated_at",
    }
    sort_key = sort_map.get(sortBy.lower(), "provinsi_id")
    sort_col = getattr(Provinsi, sort_key)
    q = q.order_by(desc(sort_col) if order.upper() == "DESC" else asc(sort_col))

    items = q.offset(pageNo * pageSize).limit(pageSize).all()

    return {
        "items": items,
        "currentPage": pageNo,
        "pageSize": pageSize,  # <- ini yang tadinya hilang
        "totalItems": total,
        "totalPages": math.ceil(total / pageSize) if pageSize else 0,
    }

# === Detail by ID (harus paling bawah) ===
@router.get("/{provinsi_id}", response_model=ProvinsiRead)
def get_provinsi(provinsi_id: int, db: Session = Depends(get_db)):
    obj = db.get(Provinsi, provinsi_id)
    if not obj:
        raise HTTPException(status_code=404, detail="Provinsi not found")
    return obj