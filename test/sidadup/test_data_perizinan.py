import pytest
from httpx import AsyncClient, ASGITransport
from sqlalchemy import text

from app.main import app
from app.core.database import SessionLocal, engine
from app.models.sidadup.sektor_perizinan import SektorPerizinan
from app.models.sidadup.sub_sektor import SubSektor
from app.models.sidadup.provinsi import Provinsi
from app.models.sidadup.daerah import Daerah
from app.models.sidadup.kecamatan import Kecamatan
from app.models.sidadup.data_perizinan import DataPerizinan

SEKTOR_NAME = "SEK-DP-TEST"
SUB_NAME = "SUB-DP-TEST"
DP_ID = "DPTEST-1"
NO_SK = "NOSK-1"


def _ensure_tables():
    Provinsi.__table__.create(bind=engine, checkfirst=True)
    Daerah.__table__.create(bind=engine, checkfirst=True)
    Kecamatan.__table__.create(bind=engine, checkfirst=True)
    with engine.begin() as conn:
        conn.execute(text("CREATE TABLE IF NOT EXISTS public.wilayah (wilayah_id BIGINT PRIMARY KEY)"))
    SektorPerizinan.__table__.create(bind=engine, checkfirst=True)
    SubSektor.__table__.create(bind=engine, checkfirst=True)
    DataPerizinan.__table__.create(bind=engine, checkfirst=True)


def _cleanup():
    db = SessionLocal()
    try:
        db.execute(text("DELETE FROM public.data_perizinan WHERE data_perizinan_id = :i"), {"i": DP_ID})
        db.execute(text("DELETE FROM public.sub_sektor WHERE nama LIKE :n"), {"n": f"{SUB_NAME}%"})
        db.execute(text("DELETE FROM public.sektor_perizinan WHERE nama LIKE :n"), {"n": f"{SEKTOR_NAME}%"})
        db.commit()
    finally:
        db.close()


@pytest.fixture(autouse=True, scope="function")
def _reset_db():
    _ensure_tables()
    _cleanup()
    yield
    _cleanup()


@pytest.mark.asyncio
async def test_data_perizinan_crud():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        s_resp = await ac.post("/api/sektor-perizinan", json={"nama": SEKTOR_NAME})
        assert s_resp.status_code == 201, s_resp.text
        sektor_id = s_resp.json()["sektor_id"]

        sub_resp = await ac.post(
            "/api/sub-sektor",
            json={"nama": SUB_NAME, "sektor_id": sektor_id, "custom_column": "CC"},
        )
        assert sub_resp.status_code == 201, sub_resp.text
        subsektor_id = sub_resp.json()["subsektor_id"]

        resp = await ac.post(
            "/api/data-perizinan",
            json={
                "data_perizinan_id": DP_ID,
                "no_sk": NO_SK,
                "tanggal_sk": "2024-01-01",
                "masa_berlaku": "2025-01-01",
                "custom_data": "{}",
                "subsektor_id": subsektor_id,
            },
        )
        assert resp.status_code == 201, resp.text

        resp_list = await ac.get("/api/data-perizinan")
        assert any(r["data_perizinan_id"] == DP_ID for r in resp_list.json())

        resp_get = await ac.get(f"/api/data-perizinan/{DP_ID}")
        assert resp_get.status_code == 200
        assert resp_get.json()["no_sk"] == NO_SK

        new_no_sk = NO_SK + "-UPD"
        resp_upd = await ac.put(
            f"/api/data-perizinan/{DP_ID}", json={"no_sk": new_no_sk}
        )
        assert resp_upd.status_code == 200
        assert resp_upd.json()["no_sk"] == new_no_sk

        resp_del = await ac.delete(f"/api/data-perizinan/{DP_ID}")
        assert resp_del.status_code == 204

        await ac.delete(f"/api/sub-sektor/{subsektor_id}")
        await ac.delete(f"/api/sektor-perizinan/{sektor_id}")

        resp_get2 = await ac.get(f"/api/data-perizinan/{DP_ID}")
        assert resp_get2.status_code == 404
