from sqlalchemy import Integer, Column, String, DateTime, func
from app.core.database import Base

class SektorPerizinan(Base):
    __tablename__ = "sektor_perizinan"
    __table_args__ = {"schema": "public"}

    sektor_id = Column(Integer, primary_key=True, index=True, nullable=False, autoincrement=True)
    nama = Column(String(100), nullable=False)

    created_at = Column(DateTime, server_default=func.now(), nullable=True)
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now(), nullable=True)
    deleted_at = Column(DateTime, nullable=True)
