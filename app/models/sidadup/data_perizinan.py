from sqlalchemy import BigInteger, Integer, Column, String, Date, Text, ForeignKey
from sqlalchemy.types import UserDefinedType
from app.core.database import Base


class Point(UserDefinedType):
    def get_col_spec(self, **kw):
        return "POINT"


class DataPerizinan(Base):
    __tablename__ = "data_perizinan"
    __table_args__ = {"schema": "public"}

    data_perizinan_id = Column(
        String,
        primary_key=True,
        nullable=False,
        comment="ymdhis_sektorid_subsektorid",
    )
    no_sk = Column(String(100), nullable=False)
    tanggal_sk = Column(Date, nullable=False)
    masa_berlaku = Column(Date, nullable=True, comment="tanggal berlaku sampai")
    custom_data = Column(
        Text,
        nullable=False,
        comment="json value,  key berdasarkan, key di custom_column di subsektor",
    )
    subsektor_id = Column(
        Integer,
        ForeignKey("public.sub_sektor.subsektor_id", onupdate="CASCADE", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    wilayah_id = Column(
        BigInteger,
        ForeignKey("public.wilayah.wilayah_id", onupdate="NO ACTION", ondelete="NO ACTION"),
        nullable=True,
        index=True,
    )
    kecamatan_id = Column(
        BigInteger,
        ForeignKey("public.kecamatan.kecamatan_id", onupdate="NO ACTION", ondelete="NO ACTION"),
        nullable=True,
        index=True,
    )
    latlong = Column(Point, nullable=True)
