from sqlalchemy import BigInteger, Integer, Column, String, ForeignKey, DateTime, func
from app.core.database import Base, PUBLIC_SCHEMA

SCHEMA_PREFIX = f"{PUBLIC_SCHEMA}." if PUBLIC_SCHEMA else ""


class Daerah(Base):
    __tablename__ = "daerah"
    __table_args__ = {"schema": PUBLIC_SCHEMA}

    daerah_id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    nama = Column(String(100), nullable=False)
    provinsi_id = Column(
        BigInteger,
        ForeignKey(f"{SCHEMA_PREFIX}provinsi.provinsi_id", onupdate="CASCADE", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    created_at = Column(DateTime, server_default=func.now(), nullable=True)
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now(), nullable=True)
