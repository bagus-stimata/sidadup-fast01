from sqlalchemy import Column, Integer, String, Date
from app.core.database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(255), unique=True, index=True, nullable=False)
    email = Column(String(255), unique=True, index=True, nullable=False)
    password = Column(String(255), nullable=False)
    # roles = Column(JSON, nullable=False)  # simpan list ["ROLE_ADMIN", ...]
    fdivisionBean = Column(Integer, nullable=True)
    organizationLevel = Column(String(50), nullable=True)
    phone = Column(Integer, nullable=True)
    countryCode = Column(Integer, nullable=True)
    avatarImage = Column(String(255), nullable=True)
    birthDate = Column(Date, nullable=True)

