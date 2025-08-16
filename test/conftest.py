# test/conftest.py
import os
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from fastapi.testclient import TestClient

from app.main import app
from app.core.database import get_db

# =========================
# DB Test: Pakai Postgres (sesuai request)
# =========================
TEST_DATABASE_URL = os.getenv(
    "TEST_DATABASE_URL",
    "postgresql+psycopg2://desgreen:Welcome1#@127.0.0.1:5432/batukota_perizinan"
)
engine = create_engine(TEST_DATABASE_URL, future=True)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine, future=True)

# =========================
# Mapping: file test -> model-model yang perlu dibuat jika file tsb di-skip
#   (Tambah sendiri sesuai kebutuhan)
# =========================
from app.models.farea import FArea
# contoh tambahan kalau perlu:
# from app.models.user import User

TEST_FILE_MODEL_MAP = {
    "test_farea.py": [FArea],
    # "test_user.py": [User],
}

# Set aktif yang akan di-skip:
# - Default: semua key di TEST_FILE_MODEL_MAP kalau SKIP_EXTRA=1
# - Atau override dinamis pakai CSV env SKIP_FILES="fileA.py,fileB.py"
def _active_skip_set():
    explicit = {x.strip() for x in os.getenv("SKIP_FILES", "").split(",") if x.strip()}
    mapped = set(TEST_FILE_MODEL_MAP.keys())
    if explicit:
        return explicit
    return mapped

# =========================
# Track collected test files so we can ensure tables for ACTIVE tests too
# =========================
COLLECTED_FILES: set[str] = set()

def pytest_collection_modifyitems(config, items):
    for it in items:
        nodeid = getattr(it, 'nodeid', '')
        # nodeid like 'test/test_farea.py::test_xxx'
        fname = nodeid.split('::', 1)[0].split('/')[-1]
        if fname:
            COLLECTED_FILES.add(fname)


# =========================
# Hook: skip file test tertentu
# =========================

# Skip test lama yang sudah digabung E2E
def pytest_ignore_collect(collection_path, config):
    try:
        name = collection_path.name  # pathlib.Path (pytest baru)
    except AttributeError:
        # fallback untuk pytest lama (py.path.local)
        name = getattr(collection_path, 'basename', lambda: str(collection_path))()
    SKIP = {"test_provinsi.py", "test_daerah.py", "test_kecamatan.py"}
    if name in SKIP:
        return True

# =========================
# Ensure tables for test files that are SKIPPED or ACTIVE (collected)
# =========================
@pytest.fixture(scope="session", autouse=True)
def _ensure_tables_for_needed_files():
    """
    Buat tabel untuk file yang:
    - di-skip (jika SKIP_EXTRA=1), dan/atau
    - AKTIF terkoleksi (ada di suite),
    sesuai mapping TEST_FILE_MODEL_MAP. Tujuannya mencegah UndefinedTable
    saat kode lain referensi model tersebut.
    """
    # files yang perlu dibuatkan tabel: union antara yang di-skip (jika diminta) dan yang terkoleksi
    needed = set()
    if os.getenv("SKIP_EXTRA") == "1":
        needed.update(_active_skip_set())
    needed.update(name for name in COLLECTED_FILES if name in TEST_FILE_MODEL_MAP)

    for fname in needed:
        for model in TEST_FILE_MODEL_MAP.get(fname, []):
            try:
                model.__table__.create(bind=engine, checkfirst=True)
            except Exception:
                # silent if already exists or no perms
                pass
    yield

# =========================
# DB session & FastAPI overrides
# =========================
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