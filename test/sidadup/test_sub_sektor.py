import pytest
from datetime import datetime
from httpx import AsyncClient, ASGITransport
from sqlalchemy import text

from app.main import app
from app.core.database import SessionLocal, engine
from app.models.sidadup.sektor_perizinan import SektorPerizinan
from app.models.sidadup.sub_sektor import SubSektor

SEKTOR_NAME = "SEKTOR-SS-TEST"
SUB_NAME = "SUBSEKTOR-TEST"


def _ensure_tables():
    SektorPerizinan.__table__.create(bind=engine, checkfirst=True)
    SubSektor.__table__.create(bind=engine, checkfirst=True)


def _cleanup():
    db = SessionLocal()
    try:
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
async def test_sub_sektor_crud():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        s_resp = await ac.post("/api/sektor-perizinan", json={"nama": SEKTOR_NAME})
        assert s_resp.status_code == 201, s_resp.text
        sektor_id = s_resp.json()["sektor_id"]

        resp = await ac.post(
            "/api/sub-sektor",
            json={"nama": SUB_NAME, "sektor_id": sektor_id, "custom_column": "CC"},
        )
        assert resp.status_code == 201, resp.text
        sub_id = resp.json()["subsektor_id"]

        resp_list = await ac.get("/api/sub-sektor", params={"sektor_id": sektor_id})
        assert any(r["subsektor_id"] == sub_id for r in resp_list.json())

        resp_paged = await ac.get(
            "/api/sub-sektor/paged",
            params={"sektor_id": sektor_id, "search": SUB_NAME},
        )
        assert resp_paged.status_code == 200
        assert any(r["subsektor_id"] == sub_id for r in resp_paged.json()["items"])

        resp_get = await ac.get(f"/api/sub-sektor/{sub_id}")
        assert resp_get.status_code == 200
        assert resp_get.json()["nama"] == SUB_NAME

        new_name = SUB_NAME + "-UPDATED"
        resp_upd = await ac.put(f"/api/sub-sektor/{sub_id}", json={"nama": new_name})
        assert resp_upd.status_code == 200
        assert resp_upd.json()["nama"] == new_name

        resp_del = await ac.delete(f"/api/sub-sektor/{sub_id}")
        assert resp_del.status_code == 204

        await ac.delete(f"/api/sektor-perizinan/{sektor_id}")

        resp_get2 = await ac.get(f"/api/sub-sektor/{sub_id}")
        assert resp_get2.status_code == 404
