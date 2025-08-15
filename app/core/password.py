# app/security/passwords.py
from passlib.context import CryptContext

# STRICT: hanya modern scheme, NO crypt lama
pwd_context = CryptContext(
    schemes=["bcrypt"],        # atau ganti ["argon2"] klo mau
    deprecated="auto"
)

def hash_password(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

def needs_rehash(hashed_password: str) -> bool:
    return pwd_context.needs_update(hashed_password)