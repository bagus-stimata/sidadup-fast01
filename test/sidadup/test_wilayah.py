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
DAERAH_NAME2 = "DAERAH-TEST-E2E-2"
KEC_NAME = "KEC-TEST-E2E"
KEC_NAME2 = "KEC-TEST-E2E-2"


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
        db.execute(text("DELETE FROM public.kecamatan WHERE nama = :n2"), {"n2": KEC_NAME2})
        db.execute(text("DELETE FROM public.daerah WHERE nama = :n"), {"n": DAERAH_NAME})
        db.execute(text("DELETE FROM public.daerah WHERE nama = :n2"), {"n2": DAERAH_NAME2})
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

        # create a second daerah to test paging/sorting on daerah
        d2_create = await ac.post(
            "/api/daerah",
            json={
                "nama": DAERAH_NAME2,
                "provinsi_id": PROV_ID,
                "created_at": datetime.utcnow().isoformat(),
                "updated_at": datetime.utcnow().isoformat(),
            },
        )
        assert d2_create.status_code == 201
        daerah_id2 = d2_create.json()["daerah_id"]


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

        # === DAERAH BY PROVINSI (PAGED) ===
        d_paged = await ac.get(
            f"/api/daerah/by-provinsi/{PROV_ID}/paged",
            params={
                "pageNo": 0,
                "pageSize": 1,
                "sortBy": "id",
                "order": "DESC",
                "search": "",
            },
        )
        assert d_paged.status_code == 200, d_paged.text
        d_body_paged = d_paged.json()
        assert set(d_body_paged.keys()) == {"items", "currentPage", "pageSize", "totalItems", "totalPages"}
        assert d_body_paged["currentPage"] == 0
        assert d_body_paged["pageSize"] == 1
        assert d_body_paged["totalItems"] >= 2
        assert isinstance(d_body_paged["items"], list) and len(d_body_paged["items"]) == 1
        # with DESC on id and pageSize=1, the first item should be the latest created (daerah_id2)
        assert d_body_paged["items"][0]["daerah_id"] == daerah_id2

        # search should filter only matching daerah
        d_paged_search = await ac.get(
            f"/api/daerah/by-provinsi/{PROV_ID}/paged",
            params={
                "pageNo": 0,
                "pageSize": 10,
                "sortBy": "id",
                "order": "ASC",
                "search": DAERAH_NAME,
            },
        )
        assert d_paged_search.status_code == 200
        d_body_paged2 = d_paged_search.json()
        assert any(it["daerah_id"] == daerah_id for it in d_body_paged2["items"]) and all(
            DAERAH_NAME in it["nama"] for it in d_body_paged2["items"]
        )

        # === DAERAH PAGED (GLOBAL) ===
        d_global_paged = await ac.get(
            "/api/daerah/paged",
            params={
                "pageNo": 0,
                "pageSize": 2,
                "sortBy": "id",
                "order": "DESC",
                "search": "DAERAH-TEST-E2E",
            },
        )
        assert d_global_paged.status_code == 200
        d_global_body = d_global_paged.json()
        assert d_global_body["pageSize"] == 2
        assert isinstance(d_global_body["items"], list)
        assert any(it["daerah_id"] in {daerah_id, daerah_id2} for it in d_global_body["items"])

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

        # create a second kecamatan to test paging/sorting
        k2_create = await ac.post(
            "/api/kecamatan",
            json={
                "nama": KEC_NAME2,
                "daerah_id": daerah_id,
                "created_at": datetime.utcnow().isoformat(),
                "updated_at": datetime.utcnow().isoformat(),
            },
        )
        assert k2_create.status_code == 201
        kec_id2 = k2_create.json()["kecamatan_id"]

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

        # === KECAMATAN BY DAERAH (PAGED) ===
        paged = await ac.get(
            f"/api/kecamatan/by-daerah/{daerah_id}/paged",
            params={
                "pageNo": 0,
                "pageSize": 1,
                "sortBy": "id",
                "order": "DESC",
                "search": "",
            },
        )
        assert paged.status_code == 200, paged.text
        body = paged.json()
        assert set(body.keys()) == {"items", "currentPage", "pageSize", "totalItems", "totalPages"}
        assert body["currentPage"] == 0
        assert body["pageSize"] == 1
        assert body["totalItems"] >= 2
        assert isinstance(body["items"], list) and len(body["items"]) == 1
        # with DESC on id and pageSize=1, the first item should be the latest created (kec_id2)
        assert body["items"][0]["kecamatan_id"] == kec_id2

        # with search filter should return only the matching first kecamatan
        paged_search = await ac.get(
            f"/api/kecamatan/by-daerah/{daerah_id}/paged",
            params={
                "pageNo": 0,
                "pageSize": 10,
                "sortBy": "id",
                "order": "ASC",
                "search": KEC_NAME,
            },
        )
        assert paged_search.status_code == 200
        body2 = paged_search.json()
        assert any(it["kecamatan_id"] == kec_id for it in body2["items"]) and all(
            KEC_NAME in it["nama"] for it in body2["items"]
        )

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