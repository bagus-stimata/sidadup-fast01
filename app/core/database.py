from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker, declarative_base
from app.core.config import settings


# DATABASE_URL = "mysql+pymysql://root:Welcome1#@localhost:3306/des_db"
DATABASE_URL = settings.DATABASE_URL  # Ambil dari settings

# Untuk SQLite, perlu connect_args agar bisa diakses lintas thread
connect_args = {"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {}

engine = create_engine(
    DATABASE_URL,
    connect_args=connect_args,
    pool_pre_ping=True,   # auto-drop dead connections (portable)
    pool_recycle=3600,    # keep < wait_timeout (MySQL); fine for Postgres too
    future=True,          # SQLAlchemy 2.0 style API
)

# Mapping schema "public" ke default apabila pakai SQLite
if DATABASE_URL.startswith("sqlite"):
    engine = engine.execution_options(schema_translate_map={"public": None})

    db_path = engine.url.database

    @event.listens_for(engine, "connect")
    def _sqlite_on_connect(dbapi_connection, connection_record):
        # buat schema alias "public" yang menunjuk ke DB utama
        dbapi_connection.execute(f"ATTACH DATABASE '{db_path}' AS public")
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


### Test the database connection: pada Terminal
# python - << 'PY'
# from app.core.database import engine
# print("dialect:", engine.dialect.name)
# PY