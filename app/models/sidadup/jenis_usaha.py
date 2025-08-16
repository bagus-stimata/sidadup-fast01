from sqlalchemy import Integer, Column, String, DateTime, func
from app.core.database import Base

class JenisUsaha(Base):
    __tablename__ = "jenis_usaha"
    __table_args__ = {"schema": "public"}

    jenis_usaha_id = Column(Integer, primary_key=True, index=True, nullable=False, autoincrement=True)
    nama = Column(String(100), nullable=False)

    created_at = Column(DateTime, server_default=func.now(), nullable=True)
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now(), nullable=True)
