from sqlalchemy import BigInteger, Column
from app.core.database import Base


class Wilayah(Base):
    __tablename__ = "wilayah"
    __table_args__ = {"schema": "public"}

    wilayah_id = Column(BigInteger, primary_key=True, index=True)
