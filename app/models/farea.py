from sqlalchemy import Column, Integer, String, Boolean, DateTime
from sqlalchemy.orm import declarative_base
from datetime import datetime

Base = declarative_base()

class FArea(Base):
    __tablename__ = "farea"

    id = Column(Integer, primary_key=True, index=True)
    # id = Column(Integer, primary_key=True, index=True, autoincrement=True)

    kode1 = Column(String(20), default="", nullable=False)
    kode2 = Column(String(20), default="", nullable=False)
    description = Column(String(100), default="", nullable=False)
    fdivisionBean = Column(Integer, default=0, nullable=False)
    status_active = Column(Boolean, default=True, nullable=False)
    fregionBean = Column(Integer, default=0, nullable=True)
    created = Column(DateTime, default=datetime.utcnow)
    modified = Column(DateTime, default=datetime.utcnow)
    modified_by = Column(String(30), default="", nullable=True)
