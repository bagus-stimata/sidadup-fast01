from datetime import datetime, timedelta
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer

import jwt  # PyJWT
from jwt import PyJWTError
# from jose import JWTError, jwt

from passlib.context import CryptContext

# Ganti dengan secretmu sendiri!
# SECRET_KEY = "YOUR_SECRET_KEY"
# ALGORITHM = "HS256"
# ACCESS_TOKEN_EXPIRE_MINUTES = 360

# -----------------
# Menggunakan .env untuk konfigurasi
# ------------------
from app.core.config import settings

SECRET_KEY = settings.SECRET_KEY
ALGORITHM = settings.ALGORITHM
ACCESS_TOKEN_EXPIRE_MINUTES = settings.ACCESS_TOKEN_EXPIRE_MINUTES

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


# -------------------------------
# 🔑 PASSWORD UTILS
# -------------------------------
def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)


# -------------------------------
# 🔑 JWT UTILS
# -------------------------------
def create_access_token(data: dict, expires_delta: timedelta | None = None) -> str:
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode = data.copy()
    to_encode.update({"iat": datetime.utcnow().timestamp()})
    to_encode.update({"exp": expire})
    # print(f"{data}")

    # Contoh: JWT TIDAK BISA MUNGKIN KARENA HARUS PAKAI TANDA PETIK
    # to_encode = {
    #     "id": 8,
    #     "username": "bagusdes_",  # Subject (username)
    #     "roles":  ['ROLE_ADMIN', 'ROLE_USER'],  # Roles, default to empty list
    #     "iat": datetime.utcnow().timestamp(),  # Issued at
    #     "exp": expire.timestamp()  # Expiration time in seconds
    # }
    # to_encode = {'sub': 'bagusdes_', 'roles': ['ROLE_ADMIN', 'ROLE_USER']}
    # to_encode.update({"iat": datetime.utcnow().timestamp()})
    # to_encode.update({"exp": expire})
    # to_encode.update({"fdivisionBean": data["fdivisionBean"]})

    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt



# -------------------------------
# 🔑 JWT DEPENDENCY
# -------------------------------
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/token")

def get_current_user(token: str = Depends(oauth2_scheme)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    # except JWTError:
    #     raise HTTPException(
    #         status_code=status.HTTP_401_UNAUTHORIZED,
    #         detail="Could not validate credentials"
    #     )
    except PyJWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials"
        )