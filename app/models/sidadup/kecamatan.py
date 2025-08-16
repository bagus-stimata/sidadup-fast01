from sqlalchemy import BigInteger, Column, String, ForeignKey, DateTime, func
from app.core.database import Base

class Kecamatan(Base):
    __tablename__ = "kecamatan"
    __table_args__ = {"schema": "public"}

    kecamatan_id = Column(BigInteger, primary_key=True, index=True)  # DB punya default seq
    nama = Column(String(100), nullable=False)
    daerah_id = Column(
        BigInteger,
        ForeignKey("public.daerah.daerah_id", onupdate="CASCADE", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    created_at = Column(DateTime, server_default=func.now(), nullable=True)
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now(), nullable=True)