from sqlalchemy import BigInteger, Column
from app.core.database import Base, PUBLIC_SCHEMA


class Wilayah(Base):
    __tablename__ = "wilayah"
    __table_args__ = {"schema": PUBLIC_SCHEMA}

    wilayah_id = Column(BigInteger, primary_key=True, index=True)
