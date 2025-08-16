from sqlalchemy import BigInteger, Integer, Column, String, ForeignKey, DateTime, func
from app.core.database import Base

class Daerah(Base):
    __tablename__ = "daerah"
    __table_args__ = {"schema": "public"}

    daerah_id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    nama = Column(String(100), nullable=False)
    provinsi_id = Column(
        BigInteger,
        ForeignKey("public.provinsi.provinsi_id", onupdate="CASCADE", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    created_at = Column(DateTime, server_default=func.now(), nullable=True)
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now(), nullable=True)