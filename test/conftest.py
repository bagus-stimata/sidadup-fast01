# test/conftest.py
import os
import pathlib
import pytest
from sqlalchemy import create_engine, MetaData
from sqlalchemy.orm import sessionmaker
from fastapi.testclient import TestClient

from app.main import app
from app.core.database import get_db  # dependency FastAPI
from app.models.farea import FArea


# Daftar file test yang mau di-skip kalau SKIP_EXTRA=1
SKIP_TEST_FILES = [
    "test_farea.py",
    # "test_user.py",
    "test_something_else.py",
]

# Daftar file test yang mau di-skip kalau SKIP_EXTRA=1
def pytest_ignore_collect(collection_path, config):
    """Optionally skip collecting tests in test_farea.py when SKIP_FAREA=1."""
    try:
        name = collection_path.name  # pathlib.Path on modern pytest
    except AttributeError:
        name = getattr(collection_path, 'basename', lambda: str(collection_path))()
    # if name == "test_farea.py" and os.getenv("SKIP_FAREA") == "1":
    #     return True
  # Skip semua file di list kalau env SKIP_EXTRA=1
    if os.getenv("SKIP_EXTRA") == "1" and name in SKIP_TEST_FILES:
        return True

# 1) Pakai DB khusus test (hindari DB dev/prod). Default ke SQLite in-memory biar tidak error DB missing
# TEST_DATABASE_URL = os.getenv(
#     "TEST_DATABASE_URL",
#     "sqlite+pysqlite:///:memory:"
# )
TEST_DATABASE_URL = os.getenv(
    "TEST_DATABASE_URL",
    "postgresql+psycopg2://desgreen:Welcome1#@127.0.0.1:5432/batukota_perizinan"
)

engine = create_engine(TEST_DATABASE_URL, future=True)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine, future=True)

# 2) Whitelist tabel yang mau dibuat (anggap ini "ignore list" kebalikannya)
WHITELIST_TABLES = [
    FArea.__table__,
]

@pytest.fixture(scope="session", autouse=True)
def _setup_test_schema():
    """
    Buat hanya tabel yang dibutuhkan test (FArea),
    tanpa menyentuh tabel lain seperti 'users'.
    """
    metadata = MetaData()
    for t in WHITELIST_TABLES:
        # Kompat untuk SQLAlchemy <1.4 dan >=1.4
        if hasattr(t, "to_metadata"):
            t.to_metadata(metadata)
        else:
            t.tometadata(metadata)
    metadata.create_all(engine)   # create hanya whitelist
    yield
    metadata.drop_all(engine)     # bersihkan setelah test

@pytest.fixture()
def db():
    """Session per-test."""
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()

# 3) Override dependency FastAPI agar endpoint pakai session test

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