from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import get_current_user
from app.repository.farea_repo import create_farea, get_all_farea
from app.repository.raw.farea_agg import count_active_area_per_division
from app.schemas.farea import FAreaCreate, FAreaResponse
from app.models.farea import FArea

router = APIRouter(prefix="/api/desgreen", tags=["farea"])

@router.post("/createFArea", response_model=FAreaResponse)
def create_farea_endpoint(
    payload: FAreaCreate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):

    # Contoh validasi role admin:
    if "ROLE_ADMIN" not in current_user["roles"]:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Admin only")

    existing = db.query(FArea).filter_by(id=payload.id).first()
    if existing:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="ID already exists")

    # result = create_farea(db, payload)
    # # Force alias!
    # response = FAreaResponse.model_validate(result)
    # return JSONResponse(content=jsonable_encoder(response.model_dump(by_alias=True)))
    result = create_farea(db, payload)
    return FAreaResponse.model_validate(result)

@router.get("/getAllFArea", response_model=list[FAreaResponse])
def read_all_farea(
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):

    if "ROLE_ADMIN" not in current_user["roles"]:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Admin only")
    division_id = current_user["roles"]
    print(division_id)
    print(current_user)

    return get_all_farea(db)

@router.get("/active-per-division")
def get_farea_agg(db: Session = Depends(get_db)):
    data = count_active_area_per_division(db)
    return {"data": data}