from sqlalchemy import BigInteger, Column, String, DateTime, func
from app.core.database import Base

class BadanUsaha(Base):
    __tablename__ = "badan_usaha"
    __table_args__ = {"schema": "public"}

    badan_usaha_id = Column(BigInteger, primary_key=True, index=True, nullable=False)
    nama = Column(String(100), nullable=False)

    created_at = Column(DateTime, server_default=func.now(), nullable=True)
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now(), nullable=True)
