from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app.core.security import create_access_token, verify_password
from app.schemas.auth import Token, SignInRequest
from app.repository.user_repo import get_user_by_username
from app.core.database import get_db
from app.core.config import settings

# router = APIRouter()
router = APIRouter(
    prefix="/api/auth",
    tags=["auth"]
)

@router.post("/token", response_model=Token)
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    """
    Endpoint Login pakai OAuth2PasswordRequestForm (form-urlencoded)
    """
    user = get_user_by_username(db, form_data.username)

    if not user or not verify_password(form_data.password, user.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials"
        )

    access_token = create_access_token({
        # "id": user.id,
        "username": user.username,
        "roles": ["ROLE_ADMIN", "ROLE_USER"],  # Bisa ambil dari user.roles kalau ada
    })

    return {
        "access_token": access_token,
        "token_type": "bearer",
        "expires_in": settings.ACCESS_TOKEN_EXPIRE_MINUTES  # Contoh: 1 jam
    }

# curl --location 'http://127.0.0.1:8000/api/auth/token' \
# --header 'Content-Type: application/x-www-form-urlencoded' \
# --data-urlencode 'username=bagusdes_' \
# --data-urlencode 'password=hacker'

@router.post("/signin", response_model=Token)
def signin(payload: SignInRequest, db: Session = Depends(get_db)):
    user = get_user_by_username(db, payload.username)
    if not user or not verify_password(payload.password, user.password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")

    # Contoh: JWT claims minimal
    access_token = create_access_token({
        # "id": user.id,
        "username": user.username,
        "fdivisionBean": user.fdivisionBean,
        "roles": ["ROLE_ADMIN", "ROLE_USER"],  # Bisa ambil dari user.roles kalau ada
    })

    return {
        "access_token": access_token,
        "token_type": "bearer",
        "fdivisionBean": user.fdivisionBean,
        "expires_in": settings.ACCESS_TOKEN_EXPIRE_MINUTES
    }

#  curl --location 'http://127.0.0.1:8000/api/auth/signin' \
# --header 'Content-Type: application/json' \
# --data '{
#   "username": "bagusdes_",
#   "password": "hacker"
# }'

@router.get("/test")
async def say_something():
    print("==== Catat Di Log ====")
    return {"message": f"Hello Aja bisa"}