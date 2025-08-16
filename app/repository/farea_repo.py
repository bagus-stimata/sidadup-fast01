from sqlalchemy.exc import IntegrityError
from fastapi import HTTPException
from sqlalchemy.orm import Session
from app.models.desgreen.farea import FArea
from app.schemas.farea import FAreaCreate

def create_farea(db: Session, farea_in: FAreaCreate):
    # db_farea = FArea(**farea_in.dict())
#    db_farea = FArea(**farea_in.dict(by_alias=True))
    db_farea = FArea(**farea_in.model_dump(by_alias=True))
    db.add(db_farea)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=400, detail="ID already exists")
    db.refresh(db_farea)
    return db_farea

def get_all_farea(db: Session):
    return db.query(FArea).all()

def get_farea(db: Session, farea_id: int):
    return db.query(FArea).filter(FArea.id == farea_id).first()

def delete_farea(db: Session, farea_id: int):
    db.query(FArea).filter(FArea.id == farea_id).delete()
    db.commit()

