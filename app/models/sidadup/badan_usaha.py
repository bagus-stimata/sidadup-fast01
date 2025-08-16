from sqlalchemy import Integer, Column, String, DateTime, func
from app.core.database import Base, PUBLIC_SCHEMA

class BadanUsaha(Base):
    __tablename__ = "badan_usaha"
    __table_args__ = {"schema": PUBLIC_SCHEMA}

    badan_usaha_id = Column(Integer, primary_key=True, index=True, nullable=False, autoincrement=True)
    nama = Column(String(100), nullable=False)

    created_at = Column(DateTime, server_default=func.now(), nullable=True)
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now(), nullable=True)
