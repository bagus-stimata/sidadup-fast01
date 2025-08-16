import pytest
from httpx import AsyncClient, ASGITransport
from sqlalchemy import text

from app.main import app
from app.core.database import SessionLocal, engine
from app.models.sidadup.sektor_perizinan import SektorPerizinan

NAME = "SEKTOR-TEST"


def _ensure_tables():
    SektorPerizinan.__table__.create(bind=engine, checkfirst=True)


def _cleanup():
    db = SessionLocal()
    try:
        db.execute(text("DELETE FROM public.sektor_perizinan WHERE nama LIKE :n"), {"n": f"{NAME}%"})
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
async def test_sektor_perizinan_crud():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        resp = await ac.post("/api/sektor-perizinan", json={"nama": NAME})
        assert resp.status_code == 201, resp.text
        sektor_id = resp.json()["sektor_id"]

        resp_list = await ac.get("/api/sektor-perizinan")
        assert any(r["sektor_id"] == sektor_id for r in resp_list.json())

        resp_paged = await ac.get("/api/sektor-perizinan/paged", params={"search": NAME})
        assert resp_paged.status_code == 200
        assert any(r["sektor_id"] == sektor_id for r in resp_paged.json()["items"])

        resp_get = await ac.get(f"/api/sektor-perizinan/{sektor_id}")
        assert resp_get.status_code == 200
        assert resp_get.json()["nama"] == NAME

        new_name = NAME + "-UPDATED"
        resp_upd = await ac.put(f"/api/sektor-perizinan/{sektor_id}", json={"nama": new_name})
        assert resp_upd.status_code == 200
        assert resp_upd.json()["nama"] == new_name

        resp_del = await ac.delete(f"/api/sektor-perizinan/{sektor_id}")
        assert resp_del.status_code == 204

        resp_get2 = await ac.get(f"/api/sektor-perizinan/{sektor_id}")
        assert resp_get2.status_code == 404
