# test/conftest.py
import os
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from fastapi.testclient import TestClient

from app.main import app
from app.core.database import get_db

# -------------------------------
# 1) DB test config (Postgres)
# -------------------------------
TEST_DATABASE_URL = os.getenv(
    "TEST_DATABASE_URL",
    "postgresql+psycopg2://desgreen:Welcome1#@127.0.0.1:5432/batukota_perizinan",
)
engine = create_engine(TEST_DATABASE_URL, future=True)
TestingSessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False, future=True)

# -------------------------------
# 2) Mapping: test file -> models
#    HANYA dipakai untuk file yang DI-SKIP
# -------------------------------
TEST_FILE_MODEL_MAP = {
    # contoh lain kalau mau skip tapi tetap butuh tabel
    # "test_farea.py": [FArea],
}

# -------------------------------
# 3) Utility: daftar file yang di-skip
#    - Pakai env SKIP_FILES="fileA.py,fileB.py"
#    - Atau aktifkan default skip lama di DEFAULT_IGNORES
# -------------------------------
DEFAULT_IGNORES = {"test_farea.py"}

def get_skip_files() -> set[str]:
    # SKIP_FILES menang; kalau kosong, pakai default ignores
    csv = os.getenv("SKIP_FILES", "")
    items = {x.strip() for x in csv.split(",") if x.strip()}
    return items if items else set(DEFAULT_IGNORES)

# -------------------------------
# 4) Hook: skip pengumpulan test
# -------------------------------
def pytest_ignore_collect(collection_path, config):
    name = getattr(collection_path, "name", None) or getattr(collection_path, "basename", lambda: "")()
    return name in get_skip_files()

# -------------------------------
# 5) Autouse fixture:
#    Buat tabel HANYA untuk file yang DI-SKIP (sesuai mapping)
# -------------------------------
@pytest.fixture(scope="session", autouse=True)
def ensure_tables_for_skipped_files():
    skipped = get_skip_files()
    for fname in skipped:
        for model in TEST_FILE_MODEL_MAP.get(fname, []):
            try:
                model.__table__.create(bind=engine, checkfirst=True)
            except Exception:
                # sengaja di-senyapkan kalau table sudah ada / tidak punya akses
                pass
    yield

# -------------------------------
# 6) DB session fixture & FastAPI override
# -------------------------------
@pytest.fixture()
def db():
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()

def _override_get_db():
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()

app.dependency_overrides[get_db] = _override_get_db

@pytest.fixture()
def client():
    return TestClient(app)