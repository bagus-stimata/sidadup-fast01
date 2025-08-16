from httpx import AsyncClient, ASGITransport  # <--- Tambahkan ASGITransport

from app.core.database import SessionLocal
from app.main import app
from app.core.security import create_access_token  # <--- Buat token valid
from app.models.desgreen.farea import FArea
import pytest

@pytest.mark.asyncio
async def test_create_farea():
    valid_token = create_access_token({
        # "id": 1,
        "username": "test_user",
        "fdivisionBean": 18,
        "roles": ["ROLE_ADMIN"]   # Harus ada ROLE_ADMIN
    })
    print("VALID TOKEN:", valid_token)  # DEBUG: Cek token yang dibuat

    async with AsyncClient(
        transport=ASGITransport(app=app),  # <- Pakai ASGITransport
        base_url="http://test"
    ) as ac:
        headers = {"Authorization": f"Bearer {valid_token}"}

        payload = {
            "id": 9999,
            "kode1": "TEST",
            "kode2": "X2",
            "description": "Testing area",
            "fdivisionBean": 1,
            "statusActive": True,
            "fregionBean": 1
        }

        response = await ac.post("/api/desgreen/createFArea", json=payload, headers=headers)

        print("RESP STATUS:", response.status_code)
        print("RESP JSON:", response.json())  # DEBUG: LIHAT detail error

        assert response.status_code == 200

@pytest.mark.asyncio
async def test_create_farea_del(db):
    db = SessionLocal()
    db.query(FArea).filter(FArea.id == 9999).delete()
    db.commit()
    db.close()

    @pytest.mark.asyncio
    async def test_farea_count_endpoint(db):
        # Buat token valid
        token = create_access_token({
            "username": "test_user",
            "roles": ["ROLE_ADMIN"]
        })

        # Buat dummy data dulu
        db = SessionLocal()
        dummy = FArea(
            id=9999,
            kode1="AGG",
            kode2="CNT",
            description="Agregat Test",
            fdivisionBean=1,
            statusActive=True,
            fregionBean=1
        )
        db.add(dummy)
        db.commit()
        db.close()

        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
            headers = {"Authorization": f"Bearer {token}"}
            response = await ac.get("/api/desgreen/farea/count", headers=headers)

            print("RESP JSON:", response.json())
            assert response.status_code == 200
            assert "count" in response.json()
            assert response.json()["count"] >= 1

        # Bersihkan dummy data
        db = SessionLocal()
        db.query(FArea).filter(FArea.id == 9999).delete()
        db.commit()
        db.close()