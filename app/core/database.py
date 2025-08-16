from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from app.core.config import settings


# DATABASE_URL = "mysql+pymysql://root:Welcome1#@localhost:3306/des_db"
DATABASE_URL = settings.DATABASE_URL  # Ambil dari settings

engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,   # auto-drop dead connections (portable)
    pool_recycle=3600,    # keep < wait_timeout (MySQL); fine for Postgres too
    future=True,          # SQLAlchemy 2.0 style API
)
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