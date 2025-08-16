from sqlalchemy import BigInteger, Column, String, ForeignKey, Text, DateTime, func
from app.core.database import Base

class SubSektor(Base):
    __tablename__ = "sub_sektor"
    __table_args__ = {"schema": "public"}

    subsektor_id = Column(BigInteger, primary_key=True, index=True, nullable=False)
    nama = Column(String, nullable=False)
    sektor_id = Column(
        BigInteger,
        ForeignKey("public.sektor_perizinan.sektor_id", onupdate="CASCADE", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    custom_column = Column(Text, nullable=False)

    created_at = Column(DateTime, server_default=func.now(), nullable=False)
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now(), nullable=True)
    deleted_at = Column(DateTime, nullable=True)
