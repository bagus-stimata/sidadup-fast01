import pytest
from httpx import AsyncClient, ASGITransport
from sqlalchemy import text, select
from datetime import datetime
@pytest.fixture(autouse=True, scope="function")
def _reset_db():
    _ensure_tables()
    _cleanup()
    yield
    _cleanup()
import pytest
from httpx import AsyncClient, ASGITransport
from sqlalchemy import text, select
from datetime import datetime

from app.main import app
from app.core.database import SessionLocal, engine
from app.models.sidadup.provinsi import Provinsi
from app.models.daerah import Daerah
from app.models.sidadup.kecamatan import Kecamatan

# Pakai ID/nama tetap, tapi selalu dibersihkan dulu biar gak duplikat
PROV_ID = 990001
DAERAH_NAME = "DAERAH-TEST-E2E"
KEC_NAME = "KEC-TEST-E2E"


def _ensure_tables():
    # Urutan sesuai FK
    Provinsi.__table__.create(bind=engine, checkfirst=True)
    Daerah.__table__.create(bind=engine, checkfirst=True)
    Kecamatan.__table__.create(bind=engine, checkfirst=True)


def _cleanup():
    db = SessionLocal()
    try:
        # child -> parent
        db.execute(text("DELETE FROM public.kecamatan WHERE nama = :n"), {"n": KEC_NAME})
        db.execute(text("DELETE FROM public.daerah WHERE nama = :n"), {"n": DAERAH_NAME})
        db.execute(text("DELETE FROM public.provinsi WHERE provinsi_id = :id"), {"id": PROV_ID})
        # reset sequence ke max id + 1
        db.execute(text("SELECT setval('daerah_daerah_id_seq', COALESCE((SELECT MAX(daerah_id) FROM public.daerah), 0) + 1, false)"))
        db.execute(text("SELECT setval('kecamatan_kecamatan_id_seq', COALESCE((SELECT MAX(kecamatan_id) FROM public.kecamatan), 0) + 1, false)"))
        db.commit()
    finally:
        db.close()


@pytest.mark.asyncio
async def test_wilayah_end_to_end():

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        # === PROVINSI ===
        p_create = await ac.post(
            "/api/provinsi",
            json={
                "provinsi_id": PROV_ID,
                "nama": "PROV-TEST-E2E",
                "created_at": datetime.utcnow().isoformat(),
                "updated_at": datetime.utcnow().isoformat(),
            },
        )
        assert p_create.status_code == 201

        p_get = await ac.get(f"/api/provinsi/{PROV_ID}")
        assert p_get.status_code == 200
        assert p_get.json()["nama"] == "PROV-TEST-E2E"

        # Cek timestamp di DB untuk provinsi
        db = SessionLocal()
        try:
            prow = db.execute(select(Provinsi).where(Provinsi.provinsi_id == PROV_ID)).scalar_one()
            assert isinstance(prow.created_at, (datetime, type(None)))
            assert isinstance(prow.updated_at, (datetime, type(None)))
        finally:
            db.close()

        # === DAERAH (FK ke PROVINSI) ===
        d_create = await ac.post(
            "/api/daerah",
            json={
                "nama": DAERAH_NAME,
                "provinsi_id": PROV_ID,
                "created_at": datetime.utcnow().isoformat(),
                "updated_at": datetime.utcnow().isoformat(),
            },
        )
        assert d_create.status_code == 201
        daerah_id = d_create.json()["daerah_id"]

        d_get = await ac.get(f"/api/daerah/{daerah_id}")
        assert d_get.status_code == 200
        d_body = d_get.json()
        assert d_body["nama"] == DAERAH_NAME
        assert d_body["provinsi_id"] == PROV_ID

        # === DAERAH BY PROVINSI ===
        d_list_by_prov = await ac.get(f"/api/daerah/by-provinsi/{PROV_ID}")
        assert d_list_by_prov.status_code == 200
        assert any(x["daerah_id"] == daerah_id for x in d_list_by_prov.json())

        # Cek timestamp di DB untuk daerah
        db = SessionLocal()
        try:
            drow = db.execute(select(Daerah).where(Daerah.daerah_id == daerah_id)).scalar_one()
            assert isinstance(drow.created_at, (datetime, type(None)))
            assert isinstance(drow.updated_at, (datetime, type(None)))
        finally:
            db.close()

        # === KECAMATAN (FK ke DAERAH) ===
        k_create = await ac.post(
            "/api/kecamatan",
            json={
                "nama": KEC_NAME,
                "daerah_id": daerah_id,
                "created_at": datetime.utcnow().isoformat(),
                "updated_at": datetime.utcnow().isoformat(),
            },
        )
        assert k_create.status_code == 201
        kec_id = k_create.json()["kecamatan_id"]

        k_get = await ac.get(f"/api/kecamatan/{kec_id}")
        assert k_get.status_code == 200
        assert k_get.json()["nama"] == KEC_NAME

        # list sanity (filter + limit besar agar deterministic)
        k_list = await ac.get("/api/kecamatan", params={"q": KEC_NAME, "limit": 1000})
        assert k_list.status_code == 200
        assert any(x["kecamatan_id"] == kec_id for x in k_list.json())

        # Simpan created_at sebelum update, lalu cek updated_at naik setelah update
        db = SessionLocal()
        try:
            krow_before = db.execute(select(Kecamatan).where(Kecamatan.kecamatan_id == kec_id)).scalar_one()
            before_created = krow_before.created_at
            before_updated = krow_before.updated_at
        finally:
            db.close()

        # update kecamatan
        k_upd = await ac.put(f"/api/kecamatan/{kec_id}", json={"nama": "KEC-EDIT-E2E"})
        assert k_upd.status_code == 200
        assert k_upd.json()["nama"] == "KEC-EDIT-E2E"

        # === KECAMATAN BY DAERAH ===
        k_list_by_daerah = await ac.get(f"/api/kecamatan/by-daerah/{daerah_id}")
        assert k_list_by_daerah.status_code == 200
        assert any(x["kecamatan_id"] == kec_id for x in k_list_by_daerah.json())

        db = SessionLocal()
        try:
            krow_after = db.execute(select(Kecamatan).where(Kecamatan.kecamatan_id == kec_id)).scalar_one()
            # created_at seharusnya tidak lebih besar setelah update
            if before_created and krow_after.created_at:
                assert krow_after.created_at <= before_created
            # updated_at seharusnya bertambah (kalau onupdate aktif)
            if before_updated and krow_after.updated_at:
                assert krow_after.updated_at >= before_updated
        finally:
            db.close()

        # === TEARDOWN via API (child -> parent) ===
        k_del = await ac.delete(f"/api/kecamatan/{kec_id}")
        assert k_del.status_code == 204

        d_del = await ac.delete(f"/api/daerah/{daerah_id}")
        assert d_del.status_code == 204

        p_del = await ac.delete(f"/api/provinsi/{PROV_ID}")
        assert p_del.status_code == 204

        # final checks 404
        assert (await ac.get(f"/api/kecamatan/{kec_id}")).status_code == 404
        assert (await ac.get(f"/api/daerah/{daerah_id}")).status_code == 404
        assert (await ac.get(f"/api/provinsi/{PROV_ID}")).status_code == 404