from sqlalchemy import Integer, Column, String, ForeignKey, Text, DateTime, func
from app.core.database import Base, PUBLIC_SCHEMA

SCHEMA_PREFIX = f"{PUBLIC_SCHEMA}." if PUBLIC_SCHEMA else ""


class SubSektor(Base):
    __tablename__ = "sub_sektor"
    __table_args__ = {"schema": PUBLIC_SCHEMA}

    subsektor_id = Column(Integer, primary_key=True, index=True, nullable=False, autoincrement=True)
    nama = Column(String, nullable=False)
    sektor_id = Column(
        Integer,
        ForeignKey(f"{SCHEMA_PREFIX}sektor_perizinan.sektor_id", onupdate="CASCADE", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    custom_column = Column(Text, nullable=False)

    # Some testing environments may already have an existing ``sub_sektor`` table
    # without a ``DEFAULT`` value defined for ``created_at``.  When SQLAlchemy
    # issues an INSERT without specifying this column, Postgres will raise a
    # ``NOT NULL`` violation.  We keep the server-side default for new tables
    # but also add a client-side default so SQLAlchemy will explicitly provide
    # ``NOW()`` during INSERT if the database lacks the default.
    created_at = Column(
        DateTime,
        server_default=func.now(),
        default=func.now(),
        nullable=False,
    )
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now(), nullable=True)
    deleted_at = Column(DateTime, nullable=True)
